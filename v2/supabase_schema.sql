-- Anti-Apathy Job Portal v2 - Database Schema
-- Run this in your Supabase SQL Editor

-- Jobs table (scraped from Platsbanken)
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    county TEXT,                     -- Län from Platsbanken (e.g. "Stockholms län", "Jönköpings län")
    description TEXT,                -- Full job description (used by cover letter AI)
    description_summary TEXT,        -- AI-generated 3-4 sentence summary (shown in UI)
    url TEXT,
    deadline TIMESTAMPTZ,
    priority TEXT DEFAULT 'normal',
    contact_email TEXT,
    contact_name TEXT,
    source TEXT DEFAULT 'platsbanken',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    link_status TEXT DEFAULT 'active'
);

-- User profiles (personal info + photo)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT,
    photo_url TEXT,  -- Supabase Storage URL
    drivers_license BOOLEAN DEFAULT FALSE,
    own_car BOOLEAN DEFAULT FALSE,
    own_computer BOOLEAN DEFAULT FALSE,
    location_by_region JSONB DEFAULT '{}'::JSONB,  -- Region→location mapping for cover letters
    languages TEXT[] DEFAULT ARRAY['Svenska (Modersmål)', 'Engelska (flytande)']::TEXT[],
    certificates TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['B-körkort', 'ICA kassahantering', etc.]
    about_me TEXT,  -- Professional bio/summary
    birth_date DATE,  -- For accurate age calculation in cover letters (added 2026-02-18)
    email_signature TEXT DEFAULT '',  -- Custom email signature for Gmail drafts
    -- Legacy columns (exist in live DB, used by quiz flow — stored here + in quiz_answers JSONB)
    linkedin TEXT,
    age TEXT,
    earliest_start TEXT,
    education_level TEXT,
    preferred_locations TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Also on user_job_preferences; legacy duplication
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============== NEW MULTI-USER PREFERENCE TABLES ==============

-- User-defined CV branscher/industries (replaces hard-coded CV_VIBES)
CREATE TABLE IF NOT EXISTS user_cv_branscher (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    bransch_id TEXT NOT NULL,  -- user-defined slug, e.g., "restaurant", "tattoo"
    bransch_name TEXT NOT NULL,  -- display name, e.g., "Restaurang & Café"
    emoji TEXT,  -- e.g., "🍽️"
    focus TEXT,  -- what to emphasize for this bransch
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- job search keywords
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, bransch_id)
);

-- Cover letter preferences per user
CREATE TABLE IF NOT EXISTS user_cover_letter_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Live DB has separate id + user_id
    user_id TEXT NOT NULL UNIQUE,
    tone TEXT DEFAULT 'professional_friendly',  -- 'formal', 'casual', 'warm'
    max_words INT DEFAULT 200,
    greeting_style TEXT DEFAULT 'Hej!',  -- 'Hej [Company]!', 'Till [Company],'
    signature_style TEXT DEFAULT 'Med vänliga hälsningar',
    liked_phrases TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['flexibel med tider', 'körkort'] — phrases user likes to use (not forced)
    never_mention TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['konst', 'Shopify']
    priority_jobs JSONB,  -- priority job types/preferences
    sign_off_name TEXT,
    sign_off_phone TEXT,
    sign_off_email TEXT,
    priority_experiences_per_vibe JSONB,  -- {"restaurant": ["Max Hamburgare"], "tech": ["Clubhouse"]}
    custom_ai_instructions TEXT,  -- Free-form additional rules
    writing_style TEXT,             -- How the letter is structured (from AI analysis)
    avoid_phrases JSONB DEFAULT '[]'::jsonb,  -- Phrases/clichés the user never uses
    length_preference TEXT,         -- Short/long preference description
    opening_style TEXT,             -- How user typically opens letters
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job search preferences per user
-- quiz_answers JSONB stores all preferences (location/kommun IDs, keywords, dealbreakers, etc.)
-- This is the primary source of truth; other columns are legacy/denormalized.
CREATE TABLE IF NOT EXISTS user_job_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,  -- UUID in live DB; FK to auth.users was dropped 2026-02-23
    search_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    locations TEXT,  -- legacy column, kept for backwards compat
    excluded_companies TEXT[] DEFAULT ARRAY[]::TEXT[],
    quiz_answers JSONB DEFAULT '{}'::jsonb,  -- All quiz + preferences data (location, dealbreakers, etc.)
    preferred_locations TEXT[] DEFAULT ARRAY[]::TEXT[],
    excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    job_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    min_hours_per_week INT,
    max_commute_minutes INT,
    remote_only BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI feedback from users (learning their preferences)
-- feedback_type options:
--   'cover_letter' - How to write cover letters (default)
--   'new_bransch_request' - Request to create new CV bransch
--   'exclude_jobs' - Filter out certain jobs ("I don't want to work in Äldrevården")
--   'general' - Other feedback
CREATE TABLE IF NOT EXISTS user_ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    feedback_type TEXT DEFAULT 'cover_letter',
    feedback_text TEXT NOT NULL,  -- Can be Swedish or English
    applies_to_branscher TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['tattoo', 'art'] or empty for all
    excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- For exclude_jobs: keywords to filter out
    is_active BOOLEAN DEFAULT TRUE,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Education entries (same for all CV vibes)
CREATE TABLE IF NOT EXISTS user_education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    school TEXT NOT NULL,
    location TEXT,
    degree TEXT,
    field_of_study TEXT,
    start_date TEXT,
    end_date TEXT,
    dates TEXT,  -- 'Aug 2017 - Maj 2021' (combined display string)
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Work experience entries (tagged with categories + AI matching tags)
CREATE TABLE IF NOT EXISTS user_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    title TEXT,
    dates TEXT,
    start_date TEXT,           -- 'Juli 2024' (for AI sorting/matching)
    end_date TEXT,             -- 'Augusti 2025' or 'Pågående'
    description TEXT,          -- Free-text description of the role
    description_long TEXT,     -- Extended description
    description_short TEXT,    -- One-line summary
    description_variants JSONB,  -- {'formal': '...', 'casual': '...'}
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    categories TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['restaurant', 'retail', 'customerservice', 'tech', etc.]
    relevance_scores JSONB,      -- {'restaurant': 9, 'tech': 3}
    key_achievements TEXT[] DEFAULT ARRAY[]::TEXT[],
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_featured BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMPTZ,
    -- AI matching tags
    job_types TEXT[] DEFAULT ARRAY[]::TEXT[],        -- ['industri', 'fysiskt_arbete', 'kundtjänst']
    skill_level TEXT,                                 -- 'entry', 'mid', 'senior'
    environment_type TEXT,                            -- 'physical', 'office', 'remote', 'outdoor', 'retail'
    key_skills TEXT[] DEFAULT ARRAY[]::TEXT[],        -- ['skiftarbete', 'teamwork', 'kundhantering']
    industry_keywords TEXT[] DEFAULT ARRAY[]::TEXT[], -- ['anodisering', 'metallbearbetning']
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Experience tags: links experiences to branscher with priority
-- (must be after user_experiences for foreign key)
CREATE TABLE IF NOT EXISTS user_experience_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    experience_id UUID REFERENCES user_experiences(id) ON DELETE CASCADE,
    bransch_id TEXT NOT NULL,  -- which CV bransch this experience is relevant for
    priority INT DEFAULT 5,  -- 1-10, how important for this bransch
    highlight_points TEXT[] DEFAULT ARRAY[]::TEXT[],  -- specific bullets to emphasize
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experience_id, bransch_id)
);

-- Volunteer work (same for all CV vibes)
CREATE TABLE IF NOT EXISTS user_volunteer (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    organization TEXT NOT NULL,
    title TEXT,
    dates TEXT,
    description TEXT,
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Awards (same for all CV vibes)
CREATE TABLE IF NOT EXISTS user_awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    award_text TEXT NOT NULL,  -- Full award line like '1:a pris Stockholms Konstsalong 2024 - ...'
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- General certifications (non-tech: körkort, kassahantering, första hjälpen, etc.)
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

-- Skills per category (different vibes show different skills)
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,  -- 'tech', 'restaurant', 'all', etc.
    skill_type TEXT NOT NULL,  -- 'technical', 'certificate', 'language'
    skill_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category, skill_text)
);

-- ============== INDUSTRY-SPECIFIC CV SECTIONS ==============

-- Artist CV: Exhibitions
CREATE TABLE IF NOT EXISTS artist_exhibitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    exhibition_type TEXT NOT NULL,  -- 'solo', 'group', 'juried'
    title TEXT,
    venue TEXT NOT NULL,
    city TEXT,
    country TEXT,
    year INT,
    notes TEXT,  -- e.g., "Vann 1:a pris"
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artist CV: Residencies & Grants
CREATE TABLE IF NOT EXISTS artist_residencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    entry_type TEXT NOT NULL,  -- 'residency', 'grant', 'fellowship'
    name TEXT NOT NULL,
    organization TEXT,
    location TEXT,
    year INT,
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artist CV: Collections (where work is held)
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

-- Tech CV: Projects
CREATE TABLE IF NOT EXISTS tech_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    description TEXT,
    tech_stack TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['React', 'Python', 'PostgreSQL']
    github_url TEXT,
    live_url TEXT,
    year INT,
    highlights TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Bullet points
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tech CV: Certifications
CREATE TABLE IF NOT EXISTS tech_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    certification_name TEXT NOT NULL,
    issuer TEXT,  -- 'AWS', 'Google', 'Microsoft'
    year_obtained INT,
    expiry_year INT,
    credential_url TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Academic CV: Publications
CREATE TABLE IF NOT EXISTS academic_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    pub_type TEXT NOT NULL,  -- 'journal', 'conference', 'book_chapter', 'thesis'
    title TEXT NOT NULL,
    authors TEXT[] DEFAULT ARRAY[]::TEXT[],  -- List of author names
    publication_venue TEXT,  -- Journal/conference name
    year INT,
    doi TEXT,
    url TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CV Industry Templates (defines which sections to use)
CREATE TABLE IF NOT EXISTS cv_industry_templates (
    id TEXT PRIMARY KEY,  -- 'traditional', 'artist', 'tech', 'academic', 'police'
    name TEXT NOT NULL,
    description TEXT,
    sections JSONB NOT NULL,  -- Ordered list of section configs
    example_roles TEXT[],  -- ['Konstnär', 'Gallerist', 'Curator']
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default industry templates
INSERT INTO cv_industry_templates (id, name, description, sections, example_roles) VALUES
('traditional', 'Traditionellt CV', 'Standard CV för service, butik, kontor',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "experience", "name": "ARBETSLIVSERFARENHET", "table": "user_experiences"},
   {"id": "skills", "name": "SPRÅK & KVALIFIKATIONER", "table": "user_skills"},
   {"id": "volunteer", "name": "IDEELLT ENGAGEMANG", "table": "user_volunteer"},
   {"id": "awards", "name": "UTMÄRKELSER", "table": "user_awards"}]'::jsonb,
 ARRAY['Servitör', 'Kassapersonal', 'Kundtjänst', 'Kontorsassistent']),

('artist', 'Konstnärs-CV', 'CV för bildkonstnärer med utställningar och residencies',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "solo_exhibitions", "name": "SOLOUTSTÄLLNINGAR", "table": "artist_exhibitions", "filter": {"exhibition_type": "solo"}},
   {"id": "group_exhibitions", "name": "GRUPPUTSTÄLLNINGAR", "table": "artist_exhibitions", "filter": {"exhibition_type": "group"}},
   {"id": "residencies", "name": "RESIDENCIES & STIPENDIER", "table": "artist_residencies"},
   {"id": "collections", "name": "SAMLINGAR", "table": "artist_collections"},
   {"id": "awards", "name": "PRISER & UTMÄRKELSER", "table": "user_awards"}]'::jsonb,
 ARRAY['Konstnär', 'Illustratör', 'Skulptör', 'Fotograf']),

('tech', 'Tech-CV', 'CV för utvecklare och IT-proffs',
 '[{"id": "skills", "name": "TEKNISKA FÄRDIGHETER", "table": "user_skills", "filter": {"category": "tech"}},
   {"id": "projects", "name": "PROJEKT", "table": "tech_projects"},
   {"id": "experience", "name": "ARBETSLIVSERFARENHET", "table": "user_experiences"},
   {"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "certifications", "name": "CERTIFIERINGAR", "table": "tech_certifications"}]'::jsonb,
 ARRAY['Webbutvecklare', 'Data Analyst', 'DevOps', 'IT-support']),

('academic', 'Akademiskt CV', 'CV för forskare och akademiker',
 '[{"id": "education", "name": "UTBILDNING", "table": "user_education"},
   {"id": "publications", "name": "PUBLIKATIONER", "table": "academic_publications"},
   {"id": "experience", "name": "ANSTÄLLNINGAR", "table": "user_experiences"},
   {"id": "awards", "name": "UTMÄRKELSER & STIPENDIER", "table": "user_awards"}]'::jsonb,
 ARRAY['Forskare', 'Doktorand', 'Universitetslektor'])
ON CONFLICT (id) DO NOTHING;

-- MASTER CV EXPORT - Complete snapshot of all user data as JSON
-- This is the "master file" that contains everything
CREATE TABLE IF NOT EXISTS master_cv_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    export_data JSONB NOT NULL,  -- Complete CV data as JSON
    version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT  -- Optional notes about this version
);

-- Function to export complete Master CV as JSON
CREATE OR REPLACE FUNCTION export_master_cv(p_user_id TEXT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'user_id', p_user_id,
        'exported_at', NOW(),
        'profile', (SELECT row_to_json(p.*) FROM user_profiles p WHERE p.user_id = p_user_id),
        'education', (SELECT jsonb_agg(row_to_json(e.*) ORDER BY e.sort_order) FROM user_education e WHERE e.user_id = p_user_id),
        'experiences', (SELECT jsonb_agg(row_to_json(x.*) ORDER BY x.sort_order) FROM user_experiences x WHERE x.user_id = p_user_id),
        'volunteer', (SELECT jsonb_agg(row_to_json(v.*) ORDER BY v.sort_order) FROM user_volunteer v WHERE v.user_id = p_user_id),
        'awards', (SELECT jsonb_agg(row_to_json(a.*) ORDER BY a.sort_order) FROM user_awards a WHERE a.user_id = p_user_id),
        'skills', (SELECT jsonb_agg(row_to_json(s.*)) FROM user_skills s WHERE s.user_id = p_user_id),
        'certifications', (SELECT jsonb_agg(row_to_json(c.*) ORDER BY c.sort_order) FROM user_certifications c WHERE c.user_id = p_user_id),
        'tech_certifications', (SELECT jsonb_agg(row_to_json(tc.*) ORDER BY tc.sort_order) FROM tech_certifications tc WHERE tc.user_id = p_user_id),
        'tech_projects', (SELECT jsonb_agg(row_to_json(tp.*) ORDER BY tp.sort_order) FROM tech_projects tp WHERE tp.user_id = p_user_id)
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to create a Master CV snapshot
CREATE OR REPLACE FUNCTION save_master_cv_snapshot(p_user_id TEXT, p_notes TEXT DEFAULT NULL)
RETURNS UUID AS $$
DECLARE
    new_id UUID;
    cv_data JSONB;
BEGIN
    cv_data := export_master_cv(p_user_id);

    INSERT INTO master_cv_exports (user_id, export_data, notes)
    VALUES (p_user_id, cv_data, p_notes)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- Generated CV versions (different "vibes") — one per industry per user
CREATE TABLE IF NOT EXISTS user_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    vibe_id TEXT NOT NULL,  -- 'restaurant', 'tech', 'retail', etc.
    vibe_name TEXT,
    vibe_emoji TEXT,
    cv_text TEXT NOT NULL,
    pdf_url TEXT,           -- Added 2026-02-17: Supabase Storage URL for uploaded/generated PDF
    -- Extra columns in live DB (not used by backend code, but exist)
    is_ai_generated BOOLEAN,
    created_via_conversation BOOLEAN,
    conversation_id UUID,
    job_types_matched TEXT[],
    times_used INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
);

-- Industry-specific CV variants (read by /api/bransch-cvs, shown in MinaCVPage)
-- Added 2026-02-17: table was referenced in code but never created
CREATE TABLE IF NOT EXISTS bransch_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    vibe_id TEXT NOT NULL,   -- 'restaurant', 'tech', 'retail', etc.
    vibe_name TEXT,
    vibe_emoji TEXT,
    cv_text TEXT,
    pdf_url TEXT,            -- Supabase Storage URL for downloadable PDF
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
);

-- Raw uploaded CV PDFs — max 20 per user (enforced by trigger)
-- Added 2026-02-17: updated from stub (had only cv_text + recommendations)
CREATE TABLE IF NOT EXISTS user_cv_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename TEXT,
    file_url TEXT,           -- Supabase Storage URL (cv-files bucket)
    upload_number INTEGER,   -- 1–20
    cv_text TEXT NOT NULL,
    recommendations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Training letters (personal letters uploaded to train AI style)
-- Max 20 per user, enforced by trigger. Added 2026-02-17.
CREATE TABLE IF NOT EXISTS user_training_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    letter_text TEXT,
    file_url TEXT,           -- Supabase Storage URL (training-letters bucket)
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job interaction signals — Meta-style event log for smart feed ranking
-- action: 'viewed' | 'skipped' | 'applied' | 'saved' | 'rejected'
-- Skipped jobs move to end of feed; rejected + applied are hidden by default.
-- context JSONB holds optional metadata (time_spent_seconds, etc.)
-- Added 2026-02-18.
CREATE TABLE IF NOT EXISTS user_job_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('viewed', 'skipped', 'applied', 'saved', 'rejected')),
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Fast lookups per user (for feed filtering)
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_user ON user_job_interactions(user_id, created_at DESC);
-- Fast lookups per job (for analytics)
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_job ON user_job_interactions(job_id);
-- One record per (user, job, action) — prevents duplicate signals
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_job_interactions_unique ON user_job_interactions(user_id, job_id, action);

-- User Google Cloud credentials (each user brings their own)
-- This is more secure - users control their own API access
CREATE TABLE IF NOT EXISTS user_google_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,
    client_id TEXT,                      -- Google OAuth client ID
    client_secret TEXT,                  -- Google OAuth client secret
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    gmail_address TEXT,  -- User's Gmail address after OAuth
    is_connected BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Applications (tracking what user has applied to)
-- status options:
--   'draft' - Saved as Gmail draft, not sent yet
--   'sent' - Application sent
--   'skipped' - User doesn't want this job (won't show again)
--   'saved' - Saved for later (will show again)
--   'interview' - Got interview
--   'rejected' - Got rejection
--   'offer' - Got job offer!
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT DEFAULT 'default_user',
    job_id TEXT REFERENCES jobs(id),
    cv_id UUID,
    bransch_id TEXT,  -- Which bransch CV was used
    cover_letter TEXT,
    status TEXT DEFAULT 'draft',
    gmail_draft_id TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    UNIQUE(user_id, job_id)  -- One application per job per user
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_contact_email ON jobs(contact_email) WHERE contact_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_master_cv_exports_user ON master_cv_exports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cvs_user ON user_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cvs_vibe ON user_cvs(user_id, vibe_id);
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Indexes for new multi-user tables
CREATE INDEX IF NOT EXISTS idx_user_cv_branscher_user ON user_cv_branscher(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ai_feedback_user ON user_ai_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_user ON user_experience_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_bransch ON user_experience_tags(bransch_id);
CREATE INDEX IF NOT EXISTS idx_user_certifications_user ON user_certifications(user_id);

-- Row Level Security (enable when you add auth)
-- ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_cvs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (uncomment when you have auth)
-- CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid()::text = user_id);
-- CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid()::text = user_id);

COMMENT ON TABLE jobs IS 'Jobs scraped from Platsbanken (only email-application jobs)';
COMMENT ON TABLE user_profiles IS 'User profile with personal info and photo';
COMMENT ON TABLE user_cvs IS 'Generated CV versions for different job categories';
COMMENT ON TABLE applications IS 'Job applications with status tracking';
COMMENT ON TABLE user_cv_branscher IS 'User-defined CV branscher/industries (replaces hard-coded CV_VIBES)';
COMMENT ON TABLE user_cover_letter_preferences IS 'Per-user cover letter style and content preferences';
COMMENT ON TABLE user_job_preferences IS 'Per-user job search filters and preferences';
COMMENT ON TABLE user_ai_feedback IS 'User feedback to AI for personalized cover letter generation';
COMMENT ON TABLE user_experience_tags IS 'Links experiences to branscher with priority for cover letter generation';
COMMENT ON TABLE user_certifications IS 'General certifications (körkort, kassahantering, första hjälpen, etc.)';
COMMENT ON TABLE user_training_letters IS 'User-uploaded training letters for AI style analysis (max 20 per user)';
COMMENT ON TABLE user_cv_uploads IS 'User-uploaded CVs as PDFs (max 20 per user)';
COMMENT ON TABLE bransch_cvs IS 'Industry-specific CV variants shown in MinaCVPage';

-- CV version history per CV — added from actual DB state (Feb 18 2026)
CREATE TABLE IF NOT EXISTS user_cv_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL,
    version_number INT NOT NULL,
    cv_text TEXT NOT NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat history for AI-built CVs — added from actual DB state (Feb 18 2026)
CREATE TABLE IF NOT EXISTS user_cv_creation_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    cv_id UUID,
    messages JSONB NOT NULL DEFAULT '[]'::JSONB,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============== KNOWN user_id TYPE INCONSISTENCY ==============
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
-- When inserting data, cast accordingly:
--   UUID tables: 'da8ed517-...'::UUID
--   TEXT tables: 'da8ed517-...' (no cast)
--
-- Linneas auth.users id: da8ed517-3b67-4456-8831-6ed3cb7114ad (linneamoritzCV@gmail.com)
-- OLD user_id (pre-auth, migrated 2026-02-23): 1e9d7392-b0d6-4f35-b69d-090c2fe2c671

-- ============== SUPABASE STORAGE BUCKETS ==============
-- All 3 buckets are PUBLIC with 4 RLS policies each (SELECT/INSERT/UPDATE/DELETE).
-- Confirmed existing in Supabase dashboard 2026-02-18.
--
-- 1. profile-photos
--    Visibility: Public
--    Allowed MIME types: image/jpeg, image/png, image/jpg, image/webp
--    Max file size: 10 MB
--    Path pattern: {user_id}/profile.{ext}
--    Public URL: {SUPABASE_URL}/storage/v1/object/public/profile-photos/{path}
--    Policies (4): Allow public read, Allow authenticated upload, Allow owner update, Allow owner delete
--
-- 2. training-letters
--    Visibility: Public
--    Allowed MIME types: application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/msword, text/plain
--    Max file size: 50 MB
--    Path pattern: {user_id}/letter_{timestamp}.{ext}
--    Public URL: {SUPABASE_URL}/storage/v1/object/public/training-letters/{path}
--    Policies (4): Allow public read, Allow authenticated upload, Allow owner update, Allow owner delete
--
-- 3. cv-files
--    Visibility: Public
--    Allowed MIME types: application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/msword, text/plain, application/rtf, application/vnd.oasis.opendocument.text
--    Max file size: 50 MB
--    Path pattern: {user_id}/{vibe_id}_cv.{ext}
--    Public URL: {SUPABASE_URL}/storage/v1/object/public/cv-files/{path}
--    Policies (4): Allow public read, Allow authenticated upload, Allow owner update, Allow owner delete

-- ============== TRIGGER FUNCTIONS ==============
-- Confirmed live in DB via information_schema.routines (Feb 2026)

-- Sets updated_at = NOW() on every UPDATE (used by: user_cvs)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Sets last_updated = NOW() on every UPDATE (used by: user_experiences)
CREATE OR REPLACE FUNCTION update_experience_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============== TRIGGERS ==============
-- Confirmed live in DB via information_schema.triggers (Feb 2026)

-- Auto-updates user_cvs.updated_at on every row update
CREATE TRIGGER update_user_cvs_updated_at
    BEFORE UPDATE ON user_cvs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-updates user_experiences.last_updated on every row update
CREATE TRIGGER trigger_update_experience_timestamp
    BEFORE UPDATE ON user_experiences
    FOR EACH ROW EXECUTE FUNCTION update_experience_timestamp();

-- ============== UTILITY FUNCTIONS ==============
-- Confirmed live in DB via information_schema.routines (Feb 2026)
-- Bodies below are inferred from names + return types — actual Supabase bodies may differ slightly.

-- Returns the best description text for an experience given a target bransch.
-- Priority: description_variants->bransch > description_short > description
CREATE OR REPLACE FUNCTION get_best_description(p_experience_id UUID, p_bransch TEXT)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    SELECT COALESCE(
        (description_variants ->> p_bransch),
        description_short,
        description
    )
    INTO result
    FROM user_experiences
    WHERE id = p_experience_id;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Returns experiences for a user relevant to a given bransch, ordered by relevance score.
-- Used by cover letter generator to select which jobs to include.
CREATE OR REPLACE FUNCTION get_experiences_for_industry(p_user_id TEXT, p_bransch TEXT)
RETURNS TABLE (
    id              UUID,
    company         TEXT,
    title           TEXT,
    dates           TEXT,
    description     TEXT,
    bullets         TEXT[],
    relevance_score INT,
    sort_order      INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.company,
        e.title,
        e.dates,
        get_best_description(e.id, p_bransch),
        e.bullets,
        COALESCE((e.relevance_scores ->> p_bransch)::INT, 0),
        e.sort_order
    FROM user_experiences e
    WHERE e.user_id = p_user_id
      AND (p_bransch = ANY(e.categories) OR e.categories = ARRAY[]::TEXT[])
    ORDER BY COALESCE((e.relevance_scores ->> p_bransch)::INT, 0) DESC, e.sort_order;
END;
$$ LANGUAGE plpgsql;

-- GDPR / account deletion: removes all data for a user across every table.
-- NOTE: user_id is TEXT in most tables but UUID in user_cv_uploads + user_training_letters.
-- Call with: SELECT delete_user_data('1e9d7392-b0d6-4f35-b69d-090c2fe2c671');
CREATE OR REPLACE FUNCTION delete_user_data(p_user_id TEXT)
RETURNS VOID AS $$
BEGIN
    -- Interaction / application data
    DELETE FROM user_job_interactions     WHERE user_id = p_user_id;
    DELETE FROM applications              WHERE user_id = p_user_id;

    -- CV content
    DELETE FROM user_experience_tags      WHERE user_id = p_user_id;
    DELETE FROM user_experiences          WHERE user_id = p_user_id;
    DELETE FROM user_education            WHERE user_id = p_user_id;
    DELETE FROM user_volunteer            WHERE user_id = p_user_id;
    DELETE FROM user_awards               WHERE user_id = p_user_id;
    DELETE FROM user_certifications       WHERE user_id = p_user_id;
    DELETE FROM user_skills               WHERE user_id = p_user_id;
    DELETE FROM tech_projects             WHERE user_id = p_user_id;
    DELETE FROM tech_certifications       WHERE user_id = p_user_id;
    DELETE FROM artist_exhibitions        WHERE user_id = p_user_id;
    DELETE FROM artist_residencies        WHERE user_id = p_user_id;
    DELETE FROM artist_collections        WHERE user_id = p_user_id;
    DELETE FROM academic_publications     WHERE user_id = p_user_id;

    -- Generated CVs + exports
    DELETE FROM user_cvs                  WHERE user_id = p_user_id;
    DELETE FROM bransch_cvs               WHERE user_id = p_user_id;
    DELETE FROM master_cv_exports         WHERE user_id = p_user_id;
    DELETE FROM user_cv_branscher         WHERE user_id = p_user_id;
    DELETE FROM user_cv_creation_conversations WHERE user_id = p_user_id;
    DELETE FROM user_cv_versions          WHERE cv_id IN (
        SELECT id FROM user_cv_creation_conversations WHERE user_id = p_user_id
    );  -- cascade-safe: cv_id has no FK, delete manually

    -- UUID-typed user_id columns (cast needed)
    DELETE FROM user_anecdotes            WHERE user_id = p_user_id::UUID;
    DELETE FROM user_cv_uploads           WHERE user_id = p_user_id::UUID;
    DELETE FROM user_training_letters     WHERE user_id = p_user_id::UUID;

    -- Preferences + credentials
    DELETE FROM user_cover_letter_preferences WHERE user_id = p_user_id;
    DELETE FROM user_job_preferences          WHERE user_id = p_user_id;
    DELETE FROM user_google_credentials       WHERE user_id = p_user_id;
    DELETE FROM user_ai_feedback              WHERE user_id = p_user_id;

    -- Profile last (other tables may reference user_id but no FK enforced)
    DELETE FROM user_profiles             WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Personal anecdotes & hobbies for cover letter personalization
-- AI picks relevant anecdotes based on job description keyword matching.
-- Example anecdote: "Jag var konfirmationsledare i Värmdö Församling 2012-2014"
-- Example hobby: "Gymma", "Matlagning"
-- Keywords help AI match: ["kyrka", "församling", "ideellt"] → matches church jobs
-- Added 2026-02-18.
CREATE TABLE IF NOT EXISTS user_anecdotes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,              -- Short label, e.g. "Svenska Kyrkan" or "Gymma"
    type TEXT NOT NULL CHECK (type IN ('anecdote', 'hobby')),
    content TEXT NOT NULL,            -- Full text: story or hobby description
    keywords TEXT[] DEFAULT '{}',     -- Matching keywords for job relevance
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE user_anecdotes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own anecdotes"
    ON user_anecdotes FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Max 30 anecdotes per user
CREATE OR REPLACE FUNCTION check_anecdote_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM user_anecdotes WHERE user_id = NEW.user_id) >= 30 THEN
        RAISE EXCEPTION 'Max 30 anekdoter per användare';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_anecdote_limit
    BEFORE INSERT ON user_anecdotes
    FOR EACH ROW EXECUTE FUNCTION check_anecdote_limit();

CREATE INDEX IF NOT EXISTS idx_user_anecdotes_user ON user_anecdotes(user_id);

COMMENT ON TABLE user_anecdotes IS 'Personal anecdotes and hobbies for AI cover letter personalization (max 30 per user)';

-- ============== LIVE STATUS (Feb 18 2026) ==============
-- user_anecdotes: LIVE (created Feb 18 2026)
-- user_profiles.birth_date: LIVE (added Feb 18 2026)
--
-- ============== TABLES STATUS ==============
-- user_ai_feedback — LIVE (created 2026-02-22)
--
-- ============== MIGRATIONS APPLIED ==============
-- 2026-02-19: user_job_preferences.quiz_answers JSONB — LIVE
--   Single source of truth for kommun IDs, search keywords, dealbreakers, etc.
-- 2026-02-21: jobs.description_summary TEXT — LIVE
--   AI-generated short summary for UI display. Full text stays in description for cover letters.
--   Migration: ALTER TABLE jobs ADD COLUMN IF NOT EXISTS description_summary TEXT;
-- 2026-02-22: user_ai_feedback — LIVE
--   Created table for AI feedback on cover letters.
-- 2026-02-22: user_cover_letter_preferences.always_mention → liked_phrases
--   Renamed column: "always_mention" was misleading (implies forced). Now "liked_phrases".
--   Migration: ALTER TABLE user_cover_letter_preferences RENAME COLUMN always_mention TO liked_phrases;
-- 2026-02-22: Added 5 missing columns to user_cover_letter_preferences — LIVE
--   sign_off_name, sign_off_phone, sign_off_email, priority_experiences_per_vibe, custom_ai_instructions
-- 2026-02-22: user_job_preferences.preferred_locations TEXT[] — LIVE
--   Stores user's selected kommun/län names from PlatserPage.
--   Migration: ALTER TABLE user_job_preferences ADD COLUMN IF NOT EXISTS preferred_locations TEXT[] DEFAULT ARRAY[]::TEXT[];
-- 2026-02-22: FULL AUDIT — synced schema with live DB. All changes below are LIVE.
--   applications: added cv_id, bransch_id, gmail_draft_id, notes, updated_at, sent_at
--     Removed aspirational columns: gmail_message_id, response_at (not in live, not used by code)
--   user_cover_letter_preferences: added id UUID, created_at, updated_at
--   user_cvs: added vibe_emoji, is_ai_generated, created_via_conversation, conversation_id, job_types_matched, times_used
--   user_experiences: added dates, bullets, created_at
--   user_education: added created_at
--   user_profiles: added certificates, about_me, updated_at; documented legacy cols (linkedin, age, earliest_start, education_level, preferred_locations)
--     Removed aspirational columns: onboarding_completed, privacy_policy_accepted, data_consent_given_at (never created in live DB)
--   user_skills: added created_at
-- 2026-02-23: Dropped FK user_job_preferences_user_id_fkey (pointed to auth.users, blocked inserts)
--   user_job_preferences.user_id is UUID in live DB (schema said TEXT — fixed)
-- 2026-02-23: Migrated ALL user data from old user_id 1e9d7392-... to real auth.users id da8ed517-...
--   Updated 21 tables. Old ID was pre-auth seed data; real ID comes from Supabase Auth.
-- 2026-02-23: Disabled RLS on user_job_preferences
--   RLS policy "Users own job prefs" required auth.uid() = user_id, but backend uses service role key
--   (auth.uid() is null), so all writes were silently blocked. Disabled to match other tables.
--   Migration: ALTER TABLE user_job_preferences DISABLE ROW LEVEL SECURITY;
