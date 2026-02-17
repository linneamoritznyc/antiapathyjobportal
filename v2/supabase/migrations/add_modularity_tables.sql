-- ============================================================================
-- MODULARITY SYSTEM: Missing Tables and Columns
-- ============================================================================
-- Run this in Supabase SQL Editor AFTER checking which tables already exist
--
-- This adds:
-- 1. user_certifications table (for ICA cert, Trygga mat, work certs)
-- 2. tech_certifications table (for DataCamp, Coursera, Udemy)
-- 3. tech_projects table (for portfolio projects with live URLs)
-- 4. user_cv_versions table (for conversational CV creation)
-- 5. user_cv_creation_conversations table (conversation history)
-- 6. New columns to user_cvs (is_ai_generated, etc.)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. TECH CERTIFICATIONS TABLE (DataCamp, Coursera, Udemy, etc.)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.tech_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    certification_name TEXT NOT NULL,
    issuer TEXT,
    year_obtained INT,
    credential_url TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_tech_certifications_user_id
    ON public.tech_certifications(user_id);

COMMENT ON TABLE public.tech_certifications IS
'Stores technical certifications from online learning platforms like DataCamp, Coursera, Udemy, Google, etc.';

-- ----------------------------------------------------------------------------
-- 2. TECH PROJECTS TABLE (Portfolio projects with live URLs)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.tech_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    description TEXT,
    tech_stack TEXT[],
    live_url TEXT,
    year INT,
    highlights TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_tech_projects_user_id
    ON public.tech_projects(user_id);

CREATE INDEX IF NOT EXISTS idx_tech_projects_year
    ON public.tech_projects(year DESC);

COMMENT ON TABLE public.tech_projects IS
'Stores portfolio tech projects with live URLs, tech stacks, and highlights. Used for tech-focused CVs.';

-- ----------------------------------------------------------------------------
-- 3. WORK CERTIFICATIONS TABLE (ICA, Trygga mat, etc.)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    certification_name TEXT NOT NULL,
    issuing_organization TEXT,
    issue_date TEXT,
    expiry_date TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_certifications_user_id
    ON public.user_certifications(user_id);

COMMENT ON TABLE public.user_certifications IS
'Stores work-related certifications like ICA kassahantering, Trygga mat, B-körkort, etc. Different from tech_certifications.';

-- ----------------------------------------------------------------------------
-- 4. CV VERSIONS TABLE (for conversational creation)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_cv_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL REFERENCES public.user_cvs(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    cv_text TEXT NOT NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_cv_versions_cv_id
    ON public.user_cv_versions(cv_id);

CREATE INDEX IF NOT EXISTS idx_user_cv_versions_created_at
    ON public.user_cv_versions(created_at DESC);

COMMENT ON TABLE public.user_cv_versions IS
'Stores version history when user creates/edits a CV through conversational flow. Each iteration is saved here.';

-- ----------------------------------------------------------------------------
-- 5. CV CREATION CONVERSATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_cv_creation_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    cv_id UUID REFERENCES public.user_cvs(id) ON DELETE SET NULL,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_cv_creation_conversations_user_id
    ON public.user_cv_creation_conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_user_cv_creation_conversations_cv_id
    ON public.user_cv_creation_conversations(cv_id);

CREATE INDEX IF NOT EXISTS idx_user_cv_creation_conversations_started_at
    ON public.user_cv_creation_conversations(started_at DESC);

COMMENT ON TABLE public.user_cv_creation_conversations IS
'Stores the conversation history when user creates a new CV interactively. Messages stored as JSONB array.';

-- ----------------------------------------------------------------------------
-- 6. ADD COLUMNS TO user_cvs TABLE
-- ----------------------------------------------------------------------------
-- These columns help distinguish between:
-- - Base CVs (8 templates, manually created or from migration)
-- - AI-generated CVs (created through conversation)
-- - Application-specific CVs (never saved, only in Gmail)

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS is_ai_generated BOOLEAN DEFAULT FALSE;

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS created_via_conversation BOOLEAN DEFAULT FALSE;

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS conversation_id UUID;

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS job_types_matched TEXT[];

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS times_used INT DEFAULT 0;

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();

ALTER TABLE public.user_cvs
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Add foreign key constraint if conversation_id doesn't have one
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'user_cvs_conversation_id_fkey'
    ) THEN
        ALTER TABLE public.user_cvs
            ADD CONSTRAINT user_cvs_conversation_id_fkey
            FOREIGN KEY (conversation_id)
            REFERENCES public.user_cv_creation_conversations(id)
            ON DELETE SET NULL;
    END IF;
END $$;

-- Add index for job_types_matched (useful for finding CVs by job type)
CREATE INDEX IF NOT EXISTS idx_user_cvs_job_types_matched
    ON public.user_cvs USING GIN (job_types_matched);

-- Add index for times_used (to find most popular CVs)
CREATE INDEX IF NOT EXISTS idx_user_cvs_times_used
    ON public.user_cvs(times_used DESC);

-- Comments
COMMENT ON COLUMN public.user_cvs.is_ai_generated IS
'TRUE if this CV was generated by AI (not manually created). Base CVs from migration = FALSE.';

COMMENT ON COLUMN public.user_cvs.created_via_conversation IS
'TRUE if this CV was created through the conversational flow (user + AI back-and-forth).';

COMMENT ON COLUMN public.user_cvs.conversation_id IS
'Reference to the conversation that created this CV (if created_via_conversation = TRUE).';

COMMENT ON COLUMN public.user_cvs.job_types_matched IS
'Array of job types this CV is good for. E.g., ["restaurant", "cafe", "customer service"]. Used for smart CV selection.';

COMMENT ON COLUMN public.user_cvs.times_used IS
'Counter: how many times this CV has been used in job applications. Helps identify popular CVs.';

-- ----------------------------------------------------------------------------
-- 7. UPDATE FUNCTION (auto-update updated_at timestamp)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'update_user_cvs_updated_at'
    ) THEN
        CREATE TRIGGER update_user_cvs_updated_at
            BEFORE UPDATE ON public.user_cvs
            FOR EACH ROW
            EXECUTE FUNCTION public.update_updated_at_column();
    END IF;
END $$;

-- ----------------------------------------------------------------------------
-- DONE
-- ----------------------------------------------------------------------------
-- Verify by running:
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name LIKE 'user_%';
