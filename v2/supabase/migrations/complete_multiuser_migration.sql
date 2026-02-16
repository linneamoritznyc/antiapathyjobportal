-- ============================================================================
-- COMPLETE MULTI-USER MIGRATION FOR ANTI-APATHY JOB PORTAL
-- ============================================================================
-- Creates all tables and inserts complete profile data for Linnea Moritz
-- Designed for multi-user from the start with proper foreign keys
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. EXPERIENCES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    category TEXT NOT NULL CHECK (category IN (
        'restaurant', 'retail', 'industry', 'healthcare', 'tech',
        'customerservice', 'reception', 'contentmoderation', 'art', 'other'
    )),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_experiences_user_id ON public.experiences(user_id);
CREATE INDEX idx_experiences_category ON public.experiences(category);

-- Enable RLS
ALTER TABLE public.experiences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own experiences" ON public.experiences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own experiences" ON public.experiences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own experiences" ON public.experiences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own experiences" ON public.experiences
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's complete work experience
-- Note: Replace 'LINNEA_USER_ID' with actual UUID after user creation
INSERT INTO public.experiences (user_id, title, company, location, start_date, end_date, is_current, description, category) VALUES
-- Restaurant experience
('LINNEA_USER_ID', 'Bartender', 'Morfar Ginko & Pappa Ray', 'Stockholm', '2022-06-01', '2023-08-31', FALSE, 'Mixology, kundservice, kassamanagement', 'restaurant'),
('LINNEA_USER_ID', 'Hovmästare/Bartender', 'AG', 'Stockholm', '2022-11-01', '2023-08-31', FALSE, 'Blandade drinkar, serverade mat, hanterade bokningar', 'restaurant'),
('LINNEA_USER_ID', 'Servitör/Bartender', 'Steakhouse', 'Stockholm', '2021-06-01', '2022-05-31', FALSE, 'Fine dining service, drinktillverkning', 'restaurant'),
('LINNEA_USER_ID', 'Restaurangbiträde', 'Wayne''s Coffee', 'Stockholm', '2019-09-01', '2020-08-31', FALSE, 'Kaffeservering, kassahantering, kundkontakt', 'restaurant'),

-- Retail experience
('LINNEA_USER_ID', 'Butiksbiträde', 'Cervera', 'Stockholm', '2020-11-01', '2021-05-31', FALSE, 'Försäljning av hushållsprodukter, kundrådgivning', 'retail'),
('LINNEA_USER_ID', 'Säljare', 'Lagerhaus', 'Stockholm', '2020-01-01', '2020-10-31', FALSE, 'Heminteriör försäljning, visual merchandising', 'retail'),
('LINNEA_USER_ID', 'Butiksbiträde', 'Systembolaget', 'Stockholm', '2019-06-01', '2019-08-31', FALSE, 'Vinrådgivning, lageradministration', 'retail'),

-- Industry/Production experience
('LINNEA_USER_ID', 'Produktionsassistent', 'Frebaco', 'Stockholm', '2023-09-01', '2024-02-28', FALSE, 'Food production, kvalitetskontroll, förpackning', 'industry'),
('LINNEA_USER_ID', 'Lagerarbetare', 'PostNord', 'Stockholm', '2021-12-01', '2022-05-31', FALSE, 'Paketsortering, lageradministration, distribution', 'industry'),

-- Healthcare experience
('LINNEA_USER_ID', 'Vårdbiträde', 'Tiohundra AB', 'Norrtälje', '2018-06-01', '2019-05-31', FALSE, 'Äldreomsorg, personlig assistans, dokumentation', 'healthcare'),
('LINNEA_USER_ID', 'Personlig assistent', 'Olika arbetsgivare', 'Stockholm', '2017-01-01', '2018-05-31', FALSE, 'Stöd till personer med funktionsnedsättning', 'healthcare'),

-- Tech/Digital experience
('LINNEA_USER_ID', 'Content Moderator', 'Majorel (via Manpower)', 'Stockholm', '2024-03-01', '2024-11-30', FALSE, 'Granskning av innehåll för sociala medier, policyhantering, rapportering', 'contentmoderation'),
('LINNEA_USER_ID', 'Junior Webbutvecklare', 'Freelance', 'Stockholm', '2023-01-01', '2023-12-31', FALSE, 'Byggde webbsidor med HTML, CSS, JavaScript för småföretag', 'tech'),

-- Customer service experience
('LINNEA_USER_ID', 'Kundtjänstmedarbetare', 'Telenor', 'Stockholm', '2020-06-01', '2020-11-30', FALSE, 'Telefonkundservice, problemlösning, CRM-system', 'customerservice'),
('LINNEA_USER_ID', 'Kundtjänst', 'SJ', 'Stockholm', '2019-01-01', '2019-05-31', FALSE, 'Biljettsupport, reseinformation, kundrelationer', 'customerservice'),

-- Reception experience
('LINNEA_USER_ID', 'Receptionist', 'Comfort Hotel', 'Stockholm', '2018-09-01', '2018-12-31', FALSE, 'Check-in/check-out, telefonservice, gästrelationer', 'reception'),

-- Art/Culture (historical - should NOT appear in tech/corporate cover letters)
('LINNEA_USER_ID', 'Galleriassistent', 'Galleri Moment', 'Stockholm', '2016-06-01', '2017-06-30', FALSE, 'Vernissage-koordinering, konstnärskontakter, utställningsplanering', 'art'),
('LINNEA_USER_ID', 'Curator Assistant', 'Konstakademien', 'Stockholm', '2016-01-01', '2016-05-31', FALSE, 'Utställningskurering, katalogproduktion', 'art'),

-- Other
('LINNEA_USER_ID', 'Projektassistent', 'Stockholms Stad', 'Stockholm', '2017-07-01', '2017-12-31', FALSE, 'Administrativt stöd för samhällsprojekt', 'other');

-- ----------------------------------------------------------------------------
-- 2. EDUCATION TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    degree TEXT NOT NULL,
    institution TEXT NOT NULL,
    location TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_education_user_id ON public.education(user_id);

-- Enable RLS
ALTER TABLE public.education ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own education" ON public.education
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own education" ON public.education
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own education" ON public.education
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own education" ON public.education
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's education
INSERT INTO public.education (user_id, degree, institution, location, start_date, end_date, is_current, description) VALUES
('LINNEA_USER_ID', 'Kandidatexamen i Konstvetenskap', 'Stockholms Universitet', 'Stockholm', '2013-09-01', '2016-06-30', FALSE, 'Fokus på modern konst, museologi och kuratorskap'),
('LINNEA_USER_ID', 'Gymnasieexamen', 'Södra Latin', 'Stockholm', '2010-08-01', '2013-06-30', FALSE, 'Estetiska programmet med inriktning konst');

-- ----------------------------------------------------------------------------
-- 3. SKILLS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'technical', 'soft', 'language', 'certification', 'tool', 'other'
    )),
    proficiency_level TEXT CHECK (proficiency_level IN (
        'beginner', 'intermediate', 'advanced', 'expert', NULL
    )),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_skills_user_id ON public.skills(user_id);
CREATE INDEX idx_skills_category ON public.skills(category);

-- Enable RLS
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own skills" ON public.skills
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own skills" ON public.skills
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own skills" ON public.skills
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own skills" ON public.skills
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's complete skill set
INSERT INTO public.skills (user_id, name, category, proficiency_level) VALUES
-- Technical skills
('LINNEA_USER_ID', 'HTML', 'technical', 'intermediate'),
('LINNEA_USER_ID', 'CSS', 'technical', 'intermediate'),
('LINNEA_USER_ID', 'JavaScript', 'technical', 'beginner'),
('LINNEA_USER_ID', 'React', 'technical', 'beginner'),
('LINNEA_USER_ID', 'Python', 'technical', 'beginner'),
('LINNEA_USER_ID', 'Content Moderation', 'technical', 'advanced'),
('LINNEA_USER_ID', 'Social Media Policy Enforcement', 'technical', 'advanced'),
('LINNEA_USER_ID', 'CRM Systems', 'technical', 'intermediate'),
('LINNEA_USER_ID', 'Microsoft Office', 'technical', 'advanced'),
('LINNEA_USER_ID', 'Google Workspace', 'technical', 'advanced'),

-- Soft skills
('LINNEA_USER_ID', 'Kundservice', 'soft', 'expert'),
('LINNEA_USER_ID', 'Problemlösning', 'soft', 'advanced'),
('LINNEA_USER_ID', 'Teamwork', 'soft', 'expert'),
('LINNEA_USER_ID', 'Kommunikation', 'soft', 'expert'),
('LINNEA_USER_ID', 'Anpassningsförmåga', 'soft', 'expert'),
('LINNEA_USER_ID', 'Multitasking', 'soft', 'advanced'),
('LINNEA_USER_ID', 'Konflikthantering', 'soft', 'advanced'),
('LINNEA_USER_ID', 'Empati', 'soft', 'expert'),
('LINNEA_USER_ID', 'Attention to Detail', 'soft', 'expert'),
('LINNEA_USER_ID', 'Stress Management', 'soft', 'advanced'),

-- Languages
('LINNEA_USER_ID', 'Svenska', 'language', 'expert'),
('LINNEA_USER_ID', 'Engelska', 'language', 'advanced'),
('LINNEA_USER_ID', 'Spanska', 'language', 'intermediate'),
('LINNEA_USER_ID', 'Franska', 'language', 'beginner'),

-- Certifications
('LINNEA_USER_ID', 'Hygiencompetens', 'certification', NULL),
('LINNEA_USER_ID', 'Alkoholservering', 'certification', NULL),
('LINNEA_USER_ID', 'Första hjälpen', 'certification', NULL),
('LINNEA_USER_ID', 'Truckkort A', 'certification', NULL),

-- Tools
('LINNEA_USER_ID', 'Kassasystem', 'tool', 'expert'),
('LINNEA_USER_ID', 'POS Systems', 'tool', 'advanced'),
('LINNEA_USER_ID', 'Bokningssystem', 'tool', 'advanced'),
('LINNEA_USER_ID', 'Zendesk', 'tool', 'intermediate'),
('LINNEA_USER_ID', 'Slack', 'tool', 'advanced'),
('LINNEA_USER_ID', 'Trello', 'tool', 'intermediate'),
('LINNEA_USER_ID', 'Asana', 'tool', 'intermediate'),

-- Other
('LINNEA_USER_ID', 'Food Safety', 'other', 'advanced'),
('LINNEA_USER_ID', 'Inventory Management', 'other', 'advanced'),
('LINNEA_USER_ID', 'Visual Merchandising', 'other', 'intermediate');

-- ----------------------------------------------------------------------------
-- 4. AWARDS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    issuer TEXT NOT NULL,
    date_received DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_awards_user_id ON public.awards(user_id);

-- Enable RLS
ALTER TABLE public.awards ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own awards" ON public.awards
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own awards" ON public.awards
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own awards" ON public.awards
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own awards" ON public.awards
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's awards
INSERT INTO public.awards (user_id, title, issuer, date_received, description) VALUES
('LINNEA_USER_ID', 'Månadens medarbetare', 'AG Restaurant', '2023-05-15', 'Utnämnd för utmärkt kundservice och teamwork'),
('LINNEA_USER_ID', 'Employee of the Quarter', 'Majorel', '2024-09-01', 'Erkänd för hög noggrannhet i content moderation'),
('LINNEA_USER_ID', 'Bästa försäljare', 'Lagerhaus', '2020-07-01', 'Högst försäljning under sommarmånaderna'),
('LINNEA_USER_ID', 'Teambuilding Award', 'PostNord', '2022-03-01', 'För positivt bidrag till teamklimat'),
('LINNEA_USER_ID', 'Customer Service Excellence', 'Telenor', '2020-10-01', 'Högst kundnöjdhetsbetyg under kvartalet'),
('LINNEA_USER_ID', 'Perfect Attendance', 'Frebaco', '2023-12-01', 'Inga sjukdagar under hela anställningsperioden'),
('LINNEA_USER_ID', 'Innovation Prize', 'Comfort Hotel', '2018-11-01', 'För förbättring av check-in-processen');

-- ----------------------------------------------------------------------------
-- 5. VOLUNTEER WORK TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.volunteer_work (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    organization TEXT NOT NULL,
    location TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_volunteer_work_user_id ON public.volunteer_work(user_id);

-- Enable RLS
ALTER TABLE public.volunteer_work ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own volunteer work" ON public.volunteer_work
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own volunteer work" ON public.volunteer_work
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own volunteer work" ON public.volunteer_work
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own volunteer work" ON public.volunteer_work
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's volunteer work
INSERT INTO public.volunteer_work (user_id, role, organization, location, start_date, end_date, is_current, description) VALUES
('LINNEA_USER_ID', 'Frivillig matutdelning', 'Stockholms Stadsmission', 'Stockholm', '2019-01-01', '2020-03-01', FALSE, 'Serverade mat till hemlösa, organiserade evenemang'),
('LINNEA_USER_ID', 'Event Coordinator', 'Pride Stockholm', 'Stockholm', '2018-06-01', '2018-08-31', FALSE, 'Hjälpte till med logistik och besökshantering'),
('LINNEA_USER_ID', 'Mentor', 'Kompisbyråan', 'Stockholm', '2017-09-01', '2018-06-30', FALSE, 'Mentorskap för nyanlända till Sverige'),
('LINNEA_USER_ID', 'Djurvolontär', 'Stockholms Katthem', 'Stockholm', '2016-03-01', '2016-12-31', FALSE, 'Hjälpte till med djurvård och adoptionsarrangemang');

-- ----------------------------------------------------------------------------
-- 6. CVS TABLE (Store 8 CV variants per user)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN (
        'restaurant', 'retail', 'industry', 'healthcare', 'tech',
        'customerservice', 'reception', 'contentmoderation', 'art'
    )),
    file_name TEXT NOT NULL,
    file_path TEXT,
    storage_url TEXT, -- Supabase Storage URL
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category)
);

CREATE INDEX idx_cvs_user_id ON public.cvs(user_id);
CREATE INDEX idx_cvs_category ON public.cvs(category);

-- Enable RLS
ALTER TABLE public.cvs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own CVs" ON public.cvs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own CVs" ON public.cvs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own CVs" ON public.cvs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own CVs" ON public.cvs
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's 8 CV variants (will need to upload PDFs to Supabase Storage)
INSERT INTO public.cvs (user_id, category, file_name, file_path) VALUES
('LINNEA_USER_ID', 'restaurant', 'CV_Linnea_Moritz_Restaurang.pdf', 'CV_Linnea_Moritz_Restaurang.pdf'),
('LINNEA_USER_ID', 'retail', 'CV_Linnea_Moritz_Butik.pdf', 'CV_Linnea_Moritz_Butik.pdf'),
('LINNEA_USER_ID', 'industry', 'CV_Linnea_Moritz_Industri.pdf', 'CV_Linnea_Moritz_Industri.pdf'),
('LINNEA_USER_ID', 'healthcare', 'CV_Linnea_Moritz_Vård.pdf', 'CV_Linnea_Moritz_Vård.pdf'),
('LINNEA_USER_ID', 'tech', 'CV_Linnea_Moritz_Tech.pdf', 'CV_Linnea_Moritz_Tech.pdf'),
('LINNEA_USER_ID', 'customerservice', 'CV_Linnea_Moritz_Kundtjänst.pdf', 'CV_Linnea_Moritz_Kundtjänst.pdf'),
('LINNEA_USER_ID', 'reception', 'CV_Linnea_Moritz_Reception.pdf', 'CV_Linnea_Moritz_Reception.pdf'),
('LINNEA_USER_ID', 'contentmoderation', 'CV_Linnea_Moritz_Contentmoderation.pdf', 'CV_Linnea_Moritz_Contentmoderation.pdf');

-- ----------------------------------------------------------------------------
-- 7. COVER LETTERS TABLE (Store all generated cover letters)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.cover_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT, -- Platsbanken job ID
    job_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    content TEXT NOT NULL, -- Full cover letter text
    category TEXT NOT NULL, -- Which CV category was used
    language TEXT DEFAULT 'swedish' CHECK (language IN ('swedish', 'english')),
    tone TEXT DEFAULT 'professional' CHECK (tone IN ('professional', 'casual', 'formal')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cover_letters_user_id ON public.cover_letters(user_id);
CREATE INDEX idx_cover_letters_job_id ON public.cover_letters(job_id);
CREATE INDEX idx_cover_letters_status ON public.cover_letters(status);

-- Enable RLS
ALTER TABLE public.cover_letters ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own cover letters" ON public.cover_letters
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cover letters" ON public.cover_letters
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cover letters" ON public.cover_letters
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own cover letters" ON public.cover_letters
    FOR DELETE USING (auth.uid() = user_id);

-- ----------------------------------------------------------------------------
-- 8. USER PREFERENCES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_preferences (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    language TEXT DEFAULT 'swedish' CHECK (language IN ('swedish', 'english')),
    tone TEXT DEFAULT 'professional' CHECK (tone IN ('professional', 'casual', 'formal')),
    email_notifications BOOLEAN DEFAULT TRUE,
    auto_generate_cover_letters BOOLEAN DEFAULT FALSE,
    preferred_categories TEXT[], -- Array of preferred job categories
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own preferences" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own preferences" ON public.user_preferences
    FOR DELETE USING (auth.uid() = user_id);

-- Insert Linnea's default preferences
INSERT INTO public.user_preferences (user_id, language, tone, preferred_categories) VALUES
('LINNEA_USER_ID', 'swedish', 'professional', ARRAY['tech', 'customerservice', 'contentmoderation', 'retail', 'restaurant']);

-- ----------------------------------------------------------------------------
-- 9. APPLICATIONS TABLE (Track job applications)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT, -- Platsbanken job ID
    job_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    job_url TEXT,
    cover_letter_id UUID REFERENCES public.cover_letters(id) ON DELETE SET NULL,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'interview', 'rejected', 'accepted', 'archived')),
    applied_date TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_applications_user_id ON public.applications(user_id);
CREATE INDEX idx_applications_status ON public.applications(status);
CREATE INDEX idx_applications_applied_date ON public.applications(applied_date);

-- Enable RLS
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own applications" ON public.applications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own applications" ON public.applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications" ON public.applications
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own applications" ON public.applications
    FOR DELETE USING (auth.uid() = user_id);

-- ----------------------------------------------------------------------------
-- 10. FUNCTIONS & TRIGGERS
-- ----------------------------------------------------------------------------

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_experiences_updated_at BEFORE UPDATE ON public.experiences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_updated_at BEFORE UPDATE ON public.education
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON public.skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_awards_updated_at BEFORE UPDATE ON public.awards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_volunteer_work_updated_at BEFORE UPDATE ON public.volunteer_work
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cvs_updated_at BEFORE UPDATE ON public.cvs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cover_letters_updated_at BEFORE UPDATE ON public.cover_letters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON public.applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- NEXT STEPS:
-- ============================================================================
-- 1. Create Linnea's user account in Supabase Authentication
-- 2. Get her user_id UUID
-- 3. Run this migration: UPDATE all 'LINNEA_USER_ID' placeholders with actual UUID
-- 4. Upload 8 PDF CVs to Supabase Storage
-- 5. Update cvs table with storage_url values
-- ============================================================================
