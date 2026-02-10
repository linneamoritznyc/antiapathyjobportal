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

-- User-defined CV vibes/industries (replaces hard-coded CV_VIBES)
CREATE TABLE IF NOT EXISTS user_cv_vibes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    vibe_id TEXT NOT NULL,  -- user-defined slug, e.g., "restaurant", "tattoo"
    vibe_name TEXT NOT NULL,  -- display name, e.g., "Restaurang & Café"
    emoji TEXT,  -- e.g., "🍽️"
    focus TEXT,  -- what to emphasize for this vibe
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- job search keywords
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
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
CREATE TABLE IF NOT EXISTS user_ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    feedback_text TEXT NOT NULL,  -- Can be Swedish or English
    applies_to_vibes TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['tattoo', 'art'] or empty for all
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Education entries (same for all CV vibes)
CREATE TABLE IF NOT EXISTS user_education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    school TEXT NOT NULL,
    location TEXT,
    degree TEXT,
    dates TEXT,  -- 'Aug 2017 - Maj 2021'
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Work experience entries (tagged with categories)
CREATE TABLE IF NOT EXISTS user_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    title TEXT,
    dates TEXT,
    bullets TEXT[] DEFAULT ARRAY[]::TEXT[],
    categories TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['restaurant', 'retail', 'customerservice', 'tech', etc.]
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Experience tags: links experiences to vibes with priority
-- (must be after user_experiences for foreign key)
CREATE TABLE IF NOT EXISTS user_experience_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    experience_id UUID REFERENCES user_experiences(id) ON DELETE CASCADE,
    vibe_id TEXT NOT NULL,  -- which CV vibe this experience is relevant for
    priority INT DEFAULT 5,  -- 1-10, how important for this vibe
    highlight_points TEXT[] DEFAULT ARRAY[]::TEXT[],  -- specific bullets to emphasize
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experience_id, vibe_id)
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
        'skills', (SELECT jsonb_agg(row_to_json(s.*)) FROM user_skills s WHERE s.user_id = p_user_id)
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

-- Generated CV versions (different "vibes")
CREATE TABLE IF NOT EXISTS user_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    vibe_id TEXT NOT NULL,  -- 'restaurant', 'tech', 'retail', etc.
    vibe_name TEXT,
    vibe_emoji TEXT,
    cv_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, vibe_id)
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
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT DEFAULT 'default_user',
    job_id TEXT REFERENCES jobs(id),
    cv_id UUID REFERENCES user_cvs(id),
    cover_letter TEXT,
    status TEXT DEFAULT 'draft',  -- draft, sent, interview, rejected, offer
    gmail_draft_id TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    response_at TIMESTAMPTZ
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
CREATE INDEX IF NOT EXISTS idx_user_cv_vibes_user ON user_cv_vibes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ai_feedback_user ON user_ai_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_user ON user_experience_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_user_experience_tags_vibe ON user_experience_tags(vibe_id);

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
COMMENT ON TABLE user_cv_vibes IS 'User-defined CV vibes/industries (replaces hard-coded CV_VIBES)';
COMMENT ON TABLE user_cover_letter_preferences IS 'Per-user cover letter style and content preferences';
COMMENT ON TABLE user_job_preferences IS 'Per-user job search filters and preferences';
COMMENT ON TABLE user_ai_feedback IS 'User feedback to AI for personalized cover letter generation';
COMMENT ON TABLE user_experience_tags IS 'Links experiences to vibes with priority for cover letter generation';
