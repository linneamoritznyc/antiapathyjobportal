-- ============================================
-- Anti-Apathy Job Portal - ACTUAL Database Schema
-- Exported from Supabase: Wednesday February 18, 2026
-- This file reflects the REAL database state
-- ============================================

-- ============================================
-- JOBS (scraped from Platsbanken)
-- ============================================
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    url TEXT,
    deadline TIMESTAMPTZ,
    contact_email TEXT
);

-- ============================================
-- USER PROFILES
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    drivers_license BOOLEAN DEFAULT FALSE,
    languages TEXT[] DEFAULT ARRAY['Svenska']::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    photo_url TEXT,
    linkedin TEXT,
    age TEXT,
    earliest_start TEXT,
    education_level TEXT
);

-- ============================================
-- USER EDUCATION
-- ============================================
CREATE TABLE IF NOT EXISTS user_education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    school TEXT NOT NULL,
    degree TEXT,
    field_of_study TEXT,
    location TEXT,
    start_date TEXT,
    end_date TEXT
);

-- ============================================
-- WORK EXPERIENCES (with AI matching tags)
-- ============================================
CREATE TABLE IF NOT EXISTS user_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    categories TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    -- Rich description variants for different CV contexts
    description_long TEXT,
    description_short TEXT,
    description_variants JSONB DEFAULT '{}'::JSONB,
    relevance_scores JSONB DEFAULT '{}'::JSONB,
    key_achievements TEXT[] DEFAULT ARRAY[]::TEXT[],
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_featured BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    -- AI matching tags
    job_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    skill_level TEXT,
    environment_type TEXT,
    key_skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    industry_keywords TEXT[] DEFAULT ARRAY[]::TEXT[]
);

-- ============================================
-- EXPERIENCE TAGS (links experiences to branscher)
-- ============================================
CREATE TABLE IF NOT EXISTS user_experience_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    experience_id UUID REFERENCES user_experiences(id) ON DELETE CASCADE,
    bransch_id TEXT NOT NULL,
    priority INT DEFAULT 5,
    highlight_points TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experience_id, bransch_id)
);

-- ============================================
-- VOLUNTEER WORK
-- ============================================
CREATE TABLE IF NOT EXISTS user_volunteer (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    organization TEXT NOT NULL,
    dates TEXT,
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- AWARDS
-- ============================================
CREATE TABLE IF NOT EXISTS user_awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    award_text TEXT NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- GENERAL CERTIFICATIONS (non-tech)
-- ============================================
CREATE TABLE IF NOT EXISTS user_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    certification_name TEXT NOT NULL,
    issuing_organization TEXT,
    issue_date TEXT,
    expiry_date TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SKILLS (per category)
-- ============================================
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    category TEXT DEFAULT 'all',
    skill_type TEXT DEFAULT 'soft',
    skill_text TEXT NOT NULL
);

-- ============================================
-- USER CV BRANSCHER (user-defined industries)
-- ============================================
CREATE TABLE IF NOT EXISTS user_cv_branscher (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    bransch_id TEXT NOT NULL,
    bransch_name TEXT NOT NULL,
    emoji TEXT,
    focus TEXT,
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, bransch_id)
);

-- ============================================
-- COVER LETTER PREFERENCES
-- ============================================
CREATE TABLE IF NOT EXISTS user_cover_letter_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tone TEXT DEFAULT 'professional',
    max_words INT DEFAULT 200,
    greeting_style TEXT DEFAULT 'Hej!',
    signature_style TEXT DEFAULT 'Med vänlig hälsning',
    always_mention TEXT[] DEFAULT ARRAY[]::TEXT[],
    never_mention TEXT[] DEFAULT ARRAY[]::TEXT[],
    priority_jobs JSONB,
    writing_style TEXT,
    avoid_phrases JSONB DEFAULT '[]'::JSONB,
    length_preference TEXT,
    opening_style TEXT
);

-- ============================================
-- JOB SEARCH PREFERENCES
-- ============================================
CREATE TABLE IF NOT EXISTS user_job_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    search_keywords TEXT[],
    locations TEXT[],
    excluded_companies TEXT[],
    quiz_answers JSONB DEFAULT '{}'::JSONB
);

-- ============================================
-- AI FEEDBACK (not in DB yet but in old schema — check if needed)
-- ============================================
-- NOTE: user_ai_feedback table does NOT exist in the actual database as of Feb 18.
-- Uncomment and run if needed:
--
-- CREATE TABLE IF NOT EXISTS user_ai_feedback (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id TEXT NOT NULL,
--     feedback_type TEXT DEFAULT 'cover_letter',
--     feedback_text TEXT NOT NULL,
--     applies_to_branscher TEXT[] DEFAULT ARRAY[]::TEXT[],
--     excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
--     is_active BOOLEAN DEFAULT TRUE,
--     is_processed BOOLEAN DEFAULT FALSE,
--     created_at TIMESTAMPTZ DEFAULT NOW()
-- );

-- ============================================
-- GENERATED CVs (one per vibe per user)
-- ============================================
CREATE TABLE IF NOT EXISTS user_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    vibe_id TEXT NOT NULL,
    vibe_name TEXT,
    cv_text TEXT,
    pdf_url TEXT,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    created_via_conversation BOOLEAN DEFAULT FALSE,
    conversation_id UUID,
    job_types_matched TEXT[],
    times_used INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CV VERSIONS (version history per CV)
-- ============================================
CREATE TABLE IF NOT EXISTS user_cv_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL,
    version_number INT NOT NULL,
    cv_text TEXT NOT NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- CV CREATION CONVERSATIONS (chat history for AI-built CVs)
-- ============================================
CREATE TABLE IF NOT EXISTS user_cv_creation_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    cv_id UUID,
    messages JSONB NOT NULL DEFAULT '[]'::JSONB,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================
-- BRANSCH CVs (industry-specific CV variants)
-- ============================================
CREATE TABLE IF NOT EXISTS bransch_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    vibe_id TEXT NOT NULL,
    vibe_name TEXT,
    vibe_emoji TEXT,
    cv_text TEXT,
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
);

-- ============================================
-- CV UPLOADS (uploaded PDF CVs, max 20/user)
-- ============================================
CREATE TABLE IF NOT EXISTS user_cv_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cv_text TEXT NOT NULL,
    recommendations JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    filename TEXT,
    file_url TEXT,
    upload_number INT
);

-- ============================================
-- TRAINING LETTERS (for AI style analysis, max 20/user)
-- ============================================
CREATE TABLE IF NOT EXISTS user_training_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename TEXT NOT NULL,
    letter_text TEXT,
    file_url TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- APPLICATIONS (job application tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    job_id TEXT,
    cover_letter TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- MASTER CV EXPORTS (JSON snapshots)
-- ============================================
CREATE TABLE IF NOT EXISTS master_cv_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    export_data JSONB NOT NULL,
    version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- ============================================
-- INDUSTRY-SPECIFIC: Artist Exhibitions
-- ============================================
CREATE TABLE IF NOT EXISTS artist_exhibitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    exhibition_type TEXT NOT NULL,
    title TEXT,
    venue TEXT NOT NULL,
    city TEXT,
    country TEXT,
    year INT,
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDUSTRY-SPECIFIC: Artist Residencies & Grants
-- ============================================
CREATE TABLE IF NOT EXISTS artist_residencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    name TEXT NOT NULL,
    organization TEXT,
    location TEXT,
    year INT,
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDUSTRY-SPECIFIC: Artist Collections
-- ============================================
CREATE TABLE IF NOT EXISTS artist_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    collection_name TEXT NOT NULL,
    location TEXT,
    year_acquired INT,
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDUSTRY-SPECIFIC: Tech Projects
-- ============================================
CREATE TABLE IF NOT EXISTS tech_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    description TEXT,
    tech_stack TEXT[] DEFAULT ARRAY[]::TEXT[],
    github_url TEXT,
    live_url TEXT,
    year INT,
    highlights TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDUSTRY-SPECIFIC: Tech Certifications
-- ============================================
CREATE TABLE IF NOT EXISTS tech_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    certification_name TEXT NOT NULL,
    issuer TEXT,
    year_obtained INT,
    expiry_year INT,
    credential_url TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDUSTRY-SPECIFIC: Academic Publications
-- ============================================
CREATE TABLE IF NOT EXISTS academic_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    pub_type TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT[] DEFAULT ARRAY[]::TEXT[],
    publication_venue TEXT,
    year INT,
    doi TEXT,
    url TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CV INDUSTRY TEMPLATES
-- ============================================
CREATE TABLE IF NOT EXISTS cv_industry_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    sections JSONB NOT NULL,
    example_roles TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default industry templates
INSERT INTO cv_industry_templates (id, name, description, sections, example_roles) VALUES
('traditional', 'Traditionellt CV', 'Standard CV for service, butik, kontor',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "experience", "name": "ARBETSLIVSERFARENHET", "table": "user_experiences"},
   {"id": "skills", "name": "KOMPETENSER", "table": "user_skills"},
   {"id": "volunteer", "name": "IDEELLT ENGAGEMANG", "table": "user_volunteer"},
   {"id": "awards", "name": "UTMÄRKELSER", "table": "user_awards"}]'::JSONB,
 ARRAY['Kassapersonal', 'Kundtjänst', 'Kontorsassistent']),

('artist', 'Konstnärs-CV', 'CV for bildkonstnärer',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "solo_exhibitions", "name": "SOLOUTSTÄLLNINGAR", "table": "artist_exhibitions", "filter": {"exhibition_type": "solo"}},
   {"id": "group_exhibitions", "name": "GRUPPUTSTÄLLNINGAR", "table": "artist_exhibitions", "filter": {"exhibition_type": "group"}},
   {"id": "residencies", "name": "RESIDENCIES & STIPENDIER", "table": "artist_residencies"},
   {"id": "collections", "name": "SAMLINGAR", "table": "artist_collections"},
   {"id": "awards", "name": "PRISER & UTMÄRKELSER", "table": "user_awards"}]'::JSONB,
 ARRAY['Konstnär', 'Illustratör', 'Fotograf']),

('tech', 'Tech-CV', 'CV for utvecklare och IT',
 '[{"id": "skills", "name": "TEKNISKA FÄRDIGHETER", "table": "user_skills", "filter": {"category": "tech"}},
   {"id": "projects", "name": "PROJEKT", "table": "tech_projects"},
   {"id": "experience", "name": "ARBETSLIVSERFARENHET", "table": "user_experiences"},
   {"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "certifications", "name": "CERTIFIERINGAR", "table": "tech_certifications"}]'::JSONB,
 ARRAY['Webbutvecklare', 'Data Analyst', 'IT-support']),

('academic', 'Akademiskt CV', 'CV for forskare',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "publications", "name": "PUBLIKATIONER", "table": "academic_publications"},
   {"id": "experience", "name": "ANSTÄLLNINGAR", "table": "user_experiences"},
   {"id": "awards", "name": "UTMÄRKELSER & STIPENDIER", "table": "user_awards"}]'::JSONB,
 ARRAY['Forskare', 'Doktorand', 'Universitetslektor'])
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_jobs_deadline ON jobs(deadline DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_contact_email ON jobs(contact_email) WHERE contact_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_master_cv_exports_user ON master_cv_exports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cvs_user ON user_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cv_branscher_user ON user_cv_branscher(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_user ON user_experience_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_bransch ON user_experience_tags(bransch_id);
CREATE INDEX IF NOT EXISTS idx_user_certifications_user ON user_certifications(user_id);

-- ============================================
-- IMPORTANT: user_id TYPE INCONSISTENCY
-- ============================================
-- Some tables use UUID, others use TEXT for user_id:
--
-- UUID: user_profiles, user_education, user_experiences, user_skills,
--       user_cvs, user_cv_uploads, user_training_letters, applications,
--       user_cover_letter_preferences, user_job_preferences
--
-- TEXT: user_volunteer, user_awards, user_certifications, tech_certifications,
--       tech_projects, user_cv_branscher, user_experience_tags, bransch_cvs,
--       master_cv_exports, artist_exhibitions, artist_residencies,
--       artist_collections, academic_publications,
--       user_cv_creation_conversations
--
-- This is a known inconsistency. When inserting data, cast accordingly:
--   UUID tables: 'da8ed517-...'::UUID
--   TEXT tables: 'da8ed517-...'

-- ============================================
-- SUPABASE STORAGE BUCKETS
-- ============================================
-- INSERT INTO storage.buckets (id, name, public) VALUES ('profile-photos', 'profile-photos', true) ON CONFLICT (id) DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('training-letters', 'training-letters', true) ON CONFLICT (id) DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('cv-files', 'cv-files', true) ON CONFLICT (id) DO NOTHING;

COMMENT ON TABLE jobs IS 'Jobs scraped from Platsbanken';
COMMENT ON TABLE user_profiles IS 'User profile with personal info and photo';
COMMENT ON TABLE user_cvs IS 'Generated CV versions for different job categories';
COMMENT ON TABLE applications IS 'Job applications with status tracking';
COMMENT ON TABLE user_cv_branscher IS 'User-defined CV branscher/industries';
COMMENT ON TABLE user_cover_letter_preferences IS 'Per-user cover letter style preferences';
COMMENT ON TABLE user_job_preferences IS 'Per-user job search filters';
COMMENT ON TABLE user_experience_tags IS 'Links experiences to branscher with priority';
COMMENT ON TABLE user_certifications IS 'General certifications (non-tech)';
COMMENT ON TABLE user_training_letters IS 'User-uploaded training letters for AI style analysis';
COMMENT ON TABLE user_cv_uploads IS 'User-uploaded CVs as PDFs';
COMMENT ON TABLE bransch_cvs IS 'Industry-specific CV variants';
COMMENT ON TABLE user_cv_versions IS 'Version history per CV';
COMMENT ON TABLE user_cv_creation_conversations IS 'Chat history for AI-built CVs';
