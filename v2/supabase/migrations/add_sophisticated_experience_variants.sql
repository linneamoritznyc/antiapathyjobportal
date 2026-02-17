-- ============================================================================
-- SOPHISTICATED MODULAR CV SYSTEM: Experience Variants
-- ============================================================================
-- This migration adds support for multiple description versions per experience
-- Enables dynamic CV assembly based on industry relevance and context
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ADD NEW COLUMNS TO user_experiences
-- ----------------------------------------------------------------------------

-- Long description (detailed, for highly relevant industries)
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS description_long TEXT;

-- Short description (condensed, for less relevant industries)
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS description_short TEXT;

-- Industry-specific description variants
-- Format: {"restaurant": "Description focused on restaurant aspects", "tech": "Description focused on tech aspects"}
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS description_variants JSONB DEFAULT '{}'::jsonb;

-- Relevance scores per industry (0-10)
-- Format: {"restaurant": 10, "tech": 3, "retail": 7}
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS relevance_scores JSONB DEFAULT '{}'::jsonb;

-- Key achievements/highlights (bullet points)
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS key_achievements TEXT[] DEFAULT ARRAY[]::TEXT[];

-- Keywords for this experience (for AI matching)
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS keywords TEXT[] DEFAULT ARRAY[]::TEXT[];

-- Metadata
ALTER TABLE public.user_experiences
    ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ DEFAULT NOW();

-- ----------------------------------------------------------------------------
-- 2. ADD COMMENTS
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN public.user_experiences.description IS
'Original description (kept for backward compatibility). Use description_long/short for new entries.';

COMMENT ON COLUMN public.user_experiences.description_long IS
'Detailed description (150-200 words). Used when experience is highly relevant to target industry.';

COMMENT ON COLUMN public.user_experiences.description_short IS
'Condensed description (50-75 words). Used when experience is less relevant but still worth mentioning.';

COMMENT ON COLUMN public.user_experiences.description_variants IS
'Industry-specific description variants. JSON format: {"restaurant": "...", "tech": "...", "retail": "..."}. Allows tailored descriptions for different contexts.';

COMMENT ON COLUMN public.user_experiences.relevance_scores IS
'Relevance score (0-10) for each industry. JSON format: {"restaurant": 10, "tech": 3}. Used for CV assembly logic to decide long vs short description.';

COMMENT ON COLUMN public.user_experiences.key_achievements IS
'Array of 3-5 key achievements/highlights. Can be used as bullet points in CV. Example: ["Ökade försäljningen med 20%", "Ledde team på 5 personer"]';

COMMENT ON COLUMN public.user_experiences.keywords IS
'Keywords/tags for this experience. Used by AI for job matching. Example: ["kundservice", "ledarskap", "försäljning", "Excel"]';

COMMENT ON COLUMN public.user_experiences.is_featured IS
'Flag to mark top/featured experiences. Featured experiences always get prominent placement in CVs.';

-- ----------------------------------------------------------------------------
-- 3. CREATE INDEXES FOR PERFORMANCE
-- ----------------------------------------------------------------------------

-- GIN index for JSONB columns (enables fast querying of JSON fields)
CREATE INDEX IF NOT EXISTS idx_user_experiences_description_variants
    ON public.user_experiences USING GIN (description_variants);

CREATE INDEX IF NOT EXISTS idx_user_experiences_relevance_scores
    ON public.user_experiences USING GIN (relevance_scores);

-- GIN index for array columns
CREATE INDEX IF NOT EXISTS idx_user_experiences_keywords
    ON public.user_experiences USING GIN (keywords);

-- Index for featured experiences
CREATE INDEX IF NOT EXISTS idx_user_experiences_is_featured
    ON public.user_experiences(user_id, is_featured)
    WHERE is_featured = TRUE;

-- ----------------------------------------------------------------------------
-- 4. CREATE HELPER FUNCTIONS
-- ----------------------------------------------------------------------------

-- Function: Get best description for an experience given target industry
CREATE OR REPLACE FUNCTION get_best_description(
    exp_id UUID,
    target_industry TEXT,
    prefer_long BOOLEAN DEFAULT TRUE
) RETURNS TEXT AS $$
DECLARE
    exp RECORD;
    relevance_score INT;
    variant_desc TEXT;
BEGIN
    -- Get experience record
    SELECT * INTO exp FROM user_experiences WHERE id = exp_id;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    -- Get relevance score for target industry
    relevance_score := COALESCE((exp.relevance_scores->>target_industry)::INT, 0);

    -- Check if there's an industry-specific variant
    variant_desc := exp.description_variants->>target_industry;
    IF variant_desc IS NOT NULL THEN
        RETURN variant_desc;
    END IF;

    -- Use relevance score to decide long vs short
    IF relevance_score >= 7 THEN
        -- Highly relevant: use long description
        RETURN COALESCE(exp.description_long, exp.description, exp.description_short);
    ELSIF relevance_score >= 4 THEN
        -- Moderately relevant: use short description if available
        IF prefer_long THEN
            RETURN COALESCE(exp.description_long, exp.description, exp.description_short);
        ELSE
            RETURN COALESCE(exp.description_short, exp.description, exp.description_long);
        END IF;
    ELSE
        -- Low relevance: always use short or omit
        RETURN COALESCE(exp.description_short, exp.description);
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_best_description IS
'Returns the most appropriate description for an experience based on target industry and relevance. Checks for industry-specific variants first, then uses relevance score to decide between long/short descriptions.';

-- Function: Get experiences for industry (sorted by relevance)
CREATE OR REPLACE FUNCTION get_experiences_for_industry(
    p_user_id UUID,
    p_industry TEXT,
    p_limit INT DEFAULT NULL
) RETURNS TABLE (
    id UUID,
    company TEXT,
    title TEXT,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    relevance_score INT,
    is_featured BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.company,
        e.title,
        e.start_date,
        e.end_date,
        get_best_description(e.id, p_industry, TRUE) as description,
        COALESCE((e.relevance_scores->>p_industry)::INT, 0) as relevance_score,
        e.is_featured
    FROM user_experiences e
    WHERE e.user_id = p_user_id
    ORDER BY
        e.is_featured DESC,
        COALESCE((e.relevance_scores->>p_industry)::INT, 0) DESC,
        e.sort_order ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_experiences_for_industry IS
'Returns experiences for a user sorted by relevance to target industry. Featured experiences come first, then sorted by relevance score. Returns appropriate description variant for each.';

-- ----------------------------------------------------------------------------
-- 5. CREATE UPDATE TRIGGER
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_experience_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_experience_timestamp ON public.user_experiences;
CREATE TRIGGER trigger_update_experience_timestamp
    BEFORE UPDATE ON public.user_experiences
    FOR EACH ROW
    EXECUTE FUNCTION update_experience_timestamp();

-- ----------------------------------------------------------------------------
-- 6. MIGRATION HELPER: Copy existing description to description_long
-- ----------------------------------------------------------------------------

-- For existing experiences without description_long, copy from description
UPDATE public.user_experiences
SET description_long = description
WHERE description_long IS NULL AND description IS NOT NULL;

-- ----------------------------------------------------------------------------
-- DONE
-- ============================================================================
--
-- NEXT STEPS:
-- 1. Run this migration
-- 2. Populate description_short for each experience (condensed versions)
-- 3. Add relevance_scores for each experience
-- 4. Optionally add industry-specific variants for key experiences
-- 5. Use get_experiences_for_industry() function in API to assemble CVs
--
-- EXAMPLE USAGE:
--
-- -- Get restaurant experiences for user
-- SELECT * FROM get_experiences_for_industry(
--     'da8ed517-3b67-4456-8831-6ed3cb7114ad'::UUID,
--     'restaurant',
--     10
-- );
--
-- -- Get best description for an experience
-- SELECT get_best_description(
--     'some-experience-id'::UUID,
--     'restaurant',
--     TRUE
-- );
--
-- ============================================================================
