-- ============================================================================
-- MIGRATION: File Upload Tables
-- Date: 2026-02-17
-- Why: Several columns and tables referenced in backend code were missing.
--      This migration adds them so file uploads actually work.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. user_cvs — add pdf_url column
--    /api/upload/cv/{vibe_id} writes pdf_url but column didn't exist
-- ----------------------------------------------------------------------------
ALTER TABLE user_cvs
  ADD COLUMN IF NOT EXISTS pdf_url TEXT;


-- ----------------------------------------------------------------------------
-- 2. user_cover_letter_preferences — add rich style columns
--    /api/user/upload-training-letter calls save_letter_style() which writes
--    these columns. They existed in code but not in the table.
-- ----------------------------------------------------------------------------
ALTER TABLE user_cover_letter_preferences
  ADD COLUMN IF NOT EXISTS writing_style        TEXT,
  ADD COLUMN IF NOT EXISTS avoid_phrases        JSONB    DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS length_preference    TEXT,
  ADD COLUMN IF NOT EXISTS opening_style        TEXT;


-- ----------------------------------------------------------------------------
-- 3. user_cv_uploads — enrich with filename + file_url
--    Table existed but was missing fields needed for PDF storage
-- ----------------------------------------------------------------------------
ALTER TABLE user_cv_uploads
  ADD COLUMN IF NOT EXISTS filename     TEXT,
  ADD COLUMN IF NOT EXISTS file_url     TEXT,
  ADD COLUMN IF NOT EXISTS upload_number INTEGER;


-- ----------------------------------------------------------------------------
-- 4. user_training_letters — new table for letter history (max 20 per user)
--    Users can upload multiple training letters; app learns from all of them.
--    /api/user/upload-training-letter should save a row here per upload.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_training_letters (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    filename     TEXT        NOT NULL,
    letter_text  TEXT,
    file_url     TEXT,
    uploaded_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_training_letters_user_id
    ON user_training_letters(user_id, uploaded_at DESC);

ALTER TABLE user_training_letters ENABLE ROW LEVEL SECURITY;

-- NOTE: CREATE POLICY does not support IF NOT EXISTS — use DROP first
DROP POLICY IF EXISTS "Users manage own training letters" ON user_training_letters;
CREATE POLICY "Users manage own training letters"
    ON user_training_letters
    FOR ALL
    USING  (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- ----------------------------------------------------------------------------
-- 5. bransch_cvs — new table (referenced in /api/bransch-cvs but never created)
--    Stores AI-generated and user-uploaded industry-specific CV versions.
--    One row per user+vibe combination.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bransch_cvs (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT        NOT NULL,
    vibe_id     TEXT        NOT NULL,   -- 'restaurant', 'tech', 'retail', etc.
    vibe_name   TEXT,
    vibe_emoji  TEXT,
    cv_text     TEXT,
    pdf_url     TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
);

CREATE INDEX IF NOT EXISTS idx_bransch_cvs_user_id
    ON bransch_cvs(user_id);

ALTER TABLE bransch_cvs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users manage own bransch CVs" ON bransch_cvs;
CREATE POLICY "Users manage own bransch CVs"
    ON bransch_cvs
    FOR ALL
    USING  (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);


-- ----------------------------------------------------------------------------
-- 6. Enforce max-20 limit on training letters via a DB trigger
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION enforce_max_training_letters()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF (SELECT COUNT(*) FROM user_training_letters WHERE user_id = NEW.user_id) >= 20 THEN
        -- Delete oldest letter to make room
        DELETE FROM user_training_letters
        WHERE id = (
            SELECT id FROM user_training_letters
            WHERE user_id = NEW.user_id
            ORDER BY uploaded_at ASC
            LIMIT 1
        );
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_max_training_letters ON user_training_letters;
CREATE TRIGGER trg_max_training_letters
    BEFORE INSERT ON user_training_letters
    FOR EACH ROW EXECUTE FUNCTION enforce_max_training_letters();


-- ----------------------------------------------------------------------------
-- VERIFY: Show columns for all affected tables
-- ----------------------------------------------------------------------------
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN (
    'user_cvs',
    'user_cover_letter_preferences',
    'user_cv_uploads',
    'user_training_letters',
    'bransch_cvs'
)
ORDER BY table_name, ordinal_position;
