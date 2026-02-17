-- ============================================================================
-- GDPR: Delete all user data (Right to Erasure - Article 17)
-- ============================================================================
-- Run this in Supabase SQL Editor to create the cascade delete function.
-- Called from /api/auth/delete-account endpoint.
-- ============================================================================

CREATE OR REPLACE FUNCTION delete_user_data(target_user_id UUID)
RETURNS void AS $$
BEGIN
    -- Delete applications
    DELETE FROM applications WHERE user_id = target_user_id::text;

    -- Delete saved jobs
    DELETE FROM saved_jobs WHERE user_id = target_user_id::text;

    -- Delete user CVs and versions
    DELETE FROM user_cv_versions WHERE cv_id IN (
        SELECT id FROM user_cvs WHERE user_id = target_user_id::text
    );
    DELETE FROM user_cvs WHERE user_id = target_user_id::text;

    -- Delete user CV uploads
    DELETE FROM user_cv_uploads WHERE user_id = target_user_id;

    -- Delete experiences, education, skills
    DELETE FROM user_experiences WHERE user_id = target_user_id::text;
    DELETE FROM user_education WHERE user_id = target_user_id::text;
    DELETE FROM user_skills WHERE user_id = target_user_id::text;
    DELETE FROM user_certifications WHERE user_id = target_user_id::text;
    DELETE FROM user_awards WHERE user_id = target_user_id::text;
    DELETE FROM user_volunteer WHERE user_id = target_user_id::text;

    -- Delete preferences and feedback
    DELETE FROM user_job_preferences WHERE user_id = target_user_id::text;
    DELETE FROM user_ai_feedback WHERE user_id = target_user_id::text;
    DELETE FROM user_cover_letter_preferences WHERE user_id = target_user_id::text;
    DELETE FROM user_cv_branscher WHERE user_id = target_user_id::text;

    -- Delete Google credentials
    DELETE FROM user_google_credentials WHERE user_id = target_user_id::text;

    -- Delete profile (last, since other tables may reference it)
    DELETE FROM user_profiles WHERE user_id = target_user_id::text;

    -- Note: Storage files (CV PDFs, photos) must be deleted via
    -- Supabase Storage API in the backend route, not here.
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- GDPR: Auto-cleanup old search data (12 months)
-- ============================================================================

-- Optional: Create a scheduled function to clean old data
-- Run this as a Supabase cron job if needed
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete job search results older than 12 months
    DELETE FROM jobs WHERE scraped_at < NOW() - INTERVAL '12 months';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Add quiz_answers column to user_job_preferences if not exists
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_job_preferences' AND column_name = 'quiz_answers'
    ) THEN
        ALTER TABLE user_job_preferences ADD COLUMN quiz_answers JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;
