-- Anti-Apathy Job Portal v2 - Database Schema
-- Run this in your Supabase SQL Editor

-- Jobs table (scraped from Platsbanken)
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    description TEXT,
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
    languages TEXT[] DEFAULT ARRAY['Svenska (Modersmål)', 'Engelska (flytande)']::TEXT[],
    certificates TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['B-körkort', 'ICA kassahantering', etc.]
    about_me TEXT,  -- Professional bio/summary
    onboarding_completed BOOLEAN DEFAULT FALSE,
    privacy_policy_accepted BOOLEAN DEFAULT FALSE,
    data_consent_given_at TIMESTAMPTZ,
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
    user_id TEXT PRIMARY KEY,
    tone TEXT DEFAULT 'professional_friendly',  -- 'formal', 'casual', 'warm'
    max_words INT DEFAULT 200,
    greeting_style TEXT DEFAULT 'Hej!',  -- 'Hej [Company]!', 'Till [Company],'
    signature_style TEXT DEFAULT 'Med vänliga hälsningar',
    sign_off_name TEXT,  -- Full name for signature
    sign_off_phone TEXT,
    sign_off_email TEXT,
    always_mention TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['flexibel med tider', 'körkort']
    never_mention TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['konst', 'Shopify']
    priority_experiences_per_vibe JSONB,  -- {"restaurant": ["Max Hamburgare"], "tech": ["Clubhouse"]}
    custom_ai_instructions TEXT,  -- Free-form additional rules
    -- Added 2026-02-17: rich AI style analysis fields (from analyze_writing_tone_rich)
    writing_style TEXT,             -- How the letter is structured
    avoid_phrases JSONB DEFAULT '[]'::jsonb,  -- Phrases/clichés the user never uses
    length_preference TEXT,         -- Short/long preference description
    opening_style TEXT,             -- How user typically opens letters
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job search preferences per user
CREATE TABLE IF NOT EXISTS user_job_preferences (
    user_id TEXT PRIMARY KEY,
    preferred_locations TEXT[] DEFAULT ARRAY['Stockholm']::TEXT[],
    search_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    excluded_companies TEXT[] DEFAULT ARRAY[]::TEXT[],
    job_types TEXT[] DEFAULT ARRAY['heltid', 'deltid']::TEXT[],
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
    dates TEXT,
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

-- User Google Cloud credentials (each user brings their own)
-- This is more secure - users control their own API access
CREATE TABLE IF NOT EXISTS user_google_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,
    google_client_id TEXT NOT NULL,
    google_client_secret TEXT NOT NULL,  -- Stored securely, user provides their own
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    gmail_address TEXT,  -- User's Gmail address after OAuth
    is_connected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
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
    cv_id UUID REFERENCES user_cvs(id),
    bransch_id TEXT,  -- Which bransch CV was used
    cover_letter TEXT,
    status TEXT DEFAULT 'draft',
    gmail_draft_id TEXT,
    gmail_message_id TEXT,  -- After sending
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    response_at TIMESTAMPTZ,
    UNIQUE(user_id, job_id)  -- One application per job per user
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority);
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

-- ============== SUPABASE STORAGE BUCKETS ==============
-- These are created automatically on app startup via the API.
-- If they don't exist, run this in Supabase SQL Editor:
--
-- INSERT INTO storage.buckets (id, name, public) VALUES ('profile-photos', 'profile-photos', true) ON CONFLICT (id) DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('training-letters', 'training-letters', true) ON CONFLICT (id) DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('cv-files', 'cv-files', true) ON CONFLICT (id) DO NOTHING;
--
-- Also add permissive storage policies so service_role can upload:
--
-- CREATE POLICY "Allow public read" ON storage.objects FOR SELECT USING (bucket_id IN ('profile-photos', 'training-letters', 'cv-files'));
-- CREATE POLICY "Allow service upload" ON storage.objects FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow service update" ON storage.objects FOR UPDATE USING (true);
-- CREATE POLICY "Allow service delete" ON storage.objects FOR DELETE USING (true);
--
-- Bucket details:
-- 1. profile-photos    — User profile photos (one per user)
--    Path: {user_id}/profile.{ext}
--    URL:  {SUPABASE_URL}/storage/v1/object/public/profile-photos/{path}
--
-- 2. training-letters  — Personal letters uploaded to train AI style (max 20/user)
--    Path: {user_id}/letter_{timestamp}.{ext}
--    URL:  {SUPABASE_URL}/storage/v1/object/public/training-letters/{path}
--
-- 3. cv-files          — Uploaded CV PDFs (max 20/user)
--    Path: {user_id}/cv_{timestamp}.{ext}
--    URL:  {SUPABASE_URL}/storage/v1/object/public/cv-files/{path}
