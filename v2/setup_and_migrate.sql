-- ============================================
-- PLATSBANKEN AI - DATABAS SETUP + DATA MIGRATION
-- Kör detta i Supabase SQL Editor
-- ============================================

-- 1. SKAPA TABELLER FÖR JOBBPORTALEN
-- ============================================

-- Användarprofiler
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name text,
    email text,
    phone text,
    location text,
    photo_url text,
    drivers_license boolean DEFAULT false,
    languages text[] DEFAULT ARRAY['Svenska'],
    linkedin_url text,
    summary text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id)
);

-- Jobbpreferenser
CREATE TABLE IF NOT EXISTS public.user_job_preferences (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    job_titles text,
    locations text,
    job_types text[] DEFAULT ARRAY[]::text[],
    experience_level text,
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id)
);

-- Arbetslivserfarenhet
CREATE TABLE IF NOT EXISTS public.user_experiences (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company text NOT NULL,
    title text NOT NULL,
    location text,
    start_date text,
    end_date text,
    description text,
    categories text[] DEFAULT ARRAY[]::text[],
    sort_order integer DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

-- Utbildning
CREATE TABLE IF NOT EXISTS public.user_education (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    school text NOT NULL,
    degree text,
    field_of_study text,
    location text,
    start_date text,
    end_date text,
    sort_order integer DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

-- Färdigheter
CREATE TABLE IF NOT EXISTS public.user_skills (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category text DEFAULT 'all',
    skill_type text DEFAULT 'soft',
    skill_text text NOT NULL,
    skill_name text,
    created_at timestamptz DEFAULT now()
);

-- CV-versioner per bransch
CREATE TABLE IF NOT EXISTS public.user_cvs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    vibe_id text NOT NULL,
    vibe_name text,
    vibe_emoji text,
    cv_text text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id, vibe_id)
);

-- CV-uppladdningar
CREATE TABLE IF NOT EXISTS public.user_cv_uploads (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_text text,
    recommendations jsonb,
    created_at timestamptz DEFAULT now()
);

-- Jobb (scrapade från Platsbanken)
CREATE TABLE IF NOT EXISTS public.jobs (
    id text PRIMARY KEY,
    title text,
    company text,
    location text,
    description text,
    url text,
    deadline timestamptz,
    priority text DEFAULT 'normal',
    contact_email text,
    contact_name text,
    source text DEFAULT 'platsbanken',
    scraped_at timestamptz DEFAULT now()
);

-- Ansökningar
CREATE TABLE IF NOT EXISTS public.applications (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id text REFERENCES public.jobs(id),
    job_title text,
    cover_letter text,
    cv_id uuid REFERENCES public.user_cvs(id),
    status text DEFAULT 'draft',
    gmail_draft_id text,
    created_at timestamptz DEFAULT now()
);

-- Google/Gmail credentials
CREATE TABLE IF NOT EXISTS public.user_google_credentials (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id text,
    client_secret text,
    access_token text,
    refresh_token text,
    token_expires_at timestamptz,
    gmail_address text,
    is_connected boolean DEFAULT false,
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id)
);

-- ============================================
-- 2. AKTIVERA ROW LEVEL SECURITY
-- ============================================

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_job_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_education ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_cv_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_google_credentials ENABLE ROW LEVEL SECURITY;

-- Jobs är publika
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 3. SKAPA RLS POLICIES
-- ============================================

-- User Profiles
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role full access profiles" ON public.user_profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Job Preferences
CREATE POLICY "Users can view own preferences" ON public.user_job_preferences
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own preferences" ON public.user_job_preferences
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own preferences" ON public.user_job_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Service role full access prefs" ON public.user_job_preferences
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Experiences
CREATE POLICY "Users can manage own experiences" ON public.user_experiences
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access exp" ON public.user_experiences
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Education
CREATE POLICY "Users can manage own education" ON public.user_education
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access edu" ON public.user_education
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Skills
CREATE POLICY "Users can manage own skills" ON public.user_skills
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access skills" ON public.user_skills
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- CVs
CREATE POLICY "Users can manage own cvs" ON public.user_cvs
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access cvs" ON public.user_cvs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- CV Uploads
CREATE POLICY "Users can manage own uploads" ON public.user_cv_uploads
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access uploads" ON public.user_cv_uploads
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Applications
CREATE POLICY "Users can manage own applications" ON public.applications
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access apps" ON public.applications
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Google Credentials
CREATE POLICY "Users can manage own google creds" ON public.user_google_credentials
    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Service role full access google" ON public.user_google_credentials
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Jobs - everyone can read
CREATE POLICY "Anyone can view jobs" ON public.jobs
    FOR SELECT USING (true);
CREATE POLICY "Service role can manage jobs" ON public.jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 4. MIGRERA LINNEAS DATA
-- ============================================

-- Din user_id
-- 1e9d7392-b0d6-4f35-b69d-090c2fe2c671

-- Profil
INSERT INTO public.user_profiles (user_id, full_name, email, phone, location, photo_url, drivers_license, languages)
VALUES (
    '1e9d7392-b0d6-4f35-b69d-090c2fe2c671',
    'Linnea Moritz',
    'linneamoritz1@gmail.com',
    '0761166109',
    'Sollentuna',
    'https://lh3.googleusercontent.com/a/ACg8ocIjDB6ePOo0bQ5kWIBrfH0RMlePz1nNI9sY0b-goCZ9zZ5VuRZ7=s96-c',
    true,
    ARRAY['Svenska (Modersmål)', 'Engelska (Flytande)']
) ON CONFLICT (user_id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    phone = EXCLUDED.phone,
    location = EXCLUDED.location,
    drivers_license = EXCLUDED.drivers_license,
    updated_at = now();

-- Jobbpreferenser
INSERT INTO public.user_job_preferences (user_id, job_titles, locations, job_types, experience_level)
VALUES (
    '1e9d7392-b0d6-4f35-b69d-090c2fe2c671',
    'servitör, kundtjänst, content moderator, butik, café',
    'Stockholm, Sollentuna, Sundbyberg',
    ARRAY['full_time', 'part_time'],
    'mid'
) ON CONFLICT (user_id) DO UPDATE SET
    job_titles = EXCLUDED.job_titles,
    locations = EXCLUDED.locations,
    job_types = EXCLUDED.job_types,
    updated_at = now();

-- Arbetslivserfarenhet
INSERT INTO public.user_experiences (user_id, company, title, location, start_date, end_date, description, categories, sort_order)
VALUES
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'House of Beans', 'Barista/Försäljare', 'Stockholm', '2024-08', '2025-02', 'Kaffe, te, försäljning, ensam i butik, kundkontakt', ARRAY['restaurant', 'retail'], 1),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'Max Hamburgare', 'Restaurangbiträde', 'Stockholm', '2024-04', '2024-08', 'Drive-in, kök, servering, kassa, teamwork', ARRAY['restaurant'], 2),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'Clubhouse', 'Innehållsmoderator - Trust & Safety', 'Remote', '2021-06', '2022-01', 'Trust & Safety, innehållsgranskning, community support, policy enforcement', ARRAY['tech', 'customerservice', 'content'], 3),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'Minerva Project', 'Global Marketing Coordinator', 'San Francisco / Remote', '2019-09', '2020-04', 'Kundservice via Intercom, marknadsföring, internationell kommunikation', ARRAY['customerservice', 'office'], 4),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'Google Ads (via Cognizant)', 'Innehållsanalytiker', 'Dublin', '2018-05', '2019-04', '100+ annonser/dag, policy compliance, kvalitetsgranskning, dataanalys', ARRAY['tech', 'content'], 5),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'Coffeehouse by George', 'Cafépersonal', 'Stockholm', '2014', '2015', 'Kassahantering, barista, kundservice', ARRAY['restaurant'], 6),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'ICA Maxi', 'Kassapersonal', 'Stockholm', '2015', '2019', 'Kassa, självscanning, frukt/grönt (sommarjobb 2015, 2017, 2019)', ARRAY['retail'], 7);

-- Utbildning
INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date)
VALUES (
    '1e9d7392-b0d6-4f35-b69d-090c2fe2c671',
    'Minerva University',
    'Bachelor''s Degree',
    'Business, Arts & Humanities',
    'San Francisco / Global',
    '2016',
    '2020'
);

-- Färdigheter
INSERT INTO public.user_skills (user_id, category, skill_type, skill_text)
VALUES
    -- Allmänna
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'soft', 'Kundservice'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'soft', 'Kommunikation'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'soft', 'Teamwork'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'soft', 'Stresshantering'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'language', 'Svenska (Modersmål)'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'language', 'Engelska (Flytande)'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'all', 'certificate', 'B-körkort'),
    -- Restaurang
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'restaurant', 'technical', 'Kassasystem'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'restaurant', 'technical', 'Barista'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'restaurant', 'technical', 'Servering'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'restaurant', 'certificate', 'Livsmedelshygien'),
    -- Tech/Content
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'tech', 'technical', 'Content Moderation'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'tech', 'technical', 'Trust & Safety'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'tech', 'technical', 'Policy Compliance'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'tech', 'technical', 'Data Analysis'),
    -- Kundtjänst
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'customerservice', 'technical', 'Intercom'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'customerservice', 'technical', 'Zendesk'),
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'customerservice', 'soft', 'Problemlösning');

-- CV-versioner
INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
VALUES
    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'restaurant', 'Restaurang & Café', '🍽️',
'LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Serviceinriktad och stresstålig person med bred erfarenhet från restaurang och café. Trivs i högt tempo och är van vid att ge gäster en bra upplevelse. B-körkort och flexibel med arbetstider.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Ansvarade för kaffe- och teservering
• Arbetade ofta ensam i butik med fullt ansvar
• Byggde upp kundrelationer och merförsäljning

Restaurangbiträde - Max Hamburgare (Apr - Aug 2024)
• Drive-in, kök och kassahantering
• Effektiv i stressiga miljöer
• Teamwork och snabb inlärning av nya system

Cafépersonal - Coffeehouse by George (2014-2015)
• Kassahantering och barista
• Hög servicenivå i centralt läge

UTBILDNING
Minerva University - Bachelor''s Degree (2016-2020)

SPRÅK & ÖVRIGT
Svenska (modersmål), Engelska (flytande)
B-körkort, Livsmedelshygien'),

    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'customerservice', 'Kundtjänst & Support', '💬',
'LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Kommunikativ och lösningsorienterad med internationell erfarenhet inom kundservice och support. Van vid att hantera ärenden via telefon, mail och chat. Flytande svenska och engelska.

ERFARENHET
Innehållsmoderator, Trust & Safety - Clubhouse (Jun 2021 - Jan 2022)
• Hanterade användarrapporter och support-ärenden
• Tillämpade community guidelines och policy
• Arbetade i ett globalt, remote team

Global Marketing Coordinator - Minerva Project (Sep 2019 - Apr 2020)
• Kundservice via Intercom
• Internationell kommunikation med studenter och partners
• Marknadsföring och eventkoordinering

Innehållsanalytiker - Google Ads (Maj 2018 - Apr 2019)
• Granskade 100+ annonser dagligen
• Policy compliance och kvalitetssäkring
• Datadriven analys och rapportering

UTBILDNING
Minerva University - Bachelor''s Degree, Business & Humanities (2016-2020)

FÄRDIGHETER
Intercom, Zendesk, CRM-system
Problemlösning, Multitasking
Svenska (modersmål), Engelska (flytande)'),

    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'content', 'Content & Moderation', '📱',
'LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Erfaren innehållsgranskare med bakgrund inom Trust & Safety och policy compliance. Analytisk, noggrann och van vid att fatta snabba beslut baserat på riktlinjer. Erfarenhet från tech-bolag som Google och Clubhouse.

ERFARENHET
Innehållsmoderator, Trust & Safety - Clubhouse (Jun 2021 - Jan 2022)
• Trust & Safety för social audio-plattform
• Granskade rapporterat innehåll enligt community guidelines
• Eskalerade komplexa ärenden till senior team
• Remote-arbete i globalt team

Innehållsanalytiker - Google Ads (Maj 2018 - Apr 2019)
• Granskade 100+ annonser dagligen för policy compliance
• Identifierade vilseledande och skadligt innehåll
• Hög accuracy och effektivitet under press
• Bidrog till förbättring av granskningsprocesser

UTBILDNING
Minerva University - Bachelor''s Degree (2016-2020)
Tvärvetenskaplig utbildning i 7 länder

FÄRDIGHETER
Content Moderation, Trust & Safety
Policy Compliance, Riktlinjetolkning
Dataanalys, Kvalitetssäkring
Svenska (modersmål), Engelska (flytande)'),

    ('1e9d7392-b0d6-4f35-b69d-090c2fe2c671', 'retail', 'Butik & Kassa', '🛒',
'LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Serviceinriktad med erfarenhet från både butik och café. Van vid kassahantering, kundkontakt och att arbeta självständigt. Pålitlig och flexibel med arbetstider.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Försäljning av kaffe, te och tillbehör
• Arbetade ofta ensam med fullt butiksansvar
• Kassahantering och lagerhantering
• Byggde kundrelationer och merförsäljning

Kassapersonal - ICA Maxi (Somrar 2015, 2017, 2019)
• Kassahantering och självscanning
• Frukt- och gröntavdelningen
• Kundservice i högt tempo

Cafépersonal - Coffeehouse by George (2014-2015)
• Kassa och kundservice
• Barista i centralt läge

UTBILDNING
Minerva University - Bachelor''s Degree (2016-2020)

FÄRDIGHETER
Kassasystem, Kortterminaler
Lagerhantering, Varupåfyllning
Kundservice, Merförsäljning
Svenska (modersmål), Engelska (flytande)
B-körkort')
ON CONFLICT (user_id, vibe_id) DO UPDATE SET
    cv_text = EXCLUDED.cv_text,
    updated_at = now();

-- ============================================
-- KLART!
-- ============================================
-- Din data är nu migrerad:
-- ✓ Profil med kontaktinfo
-- ✓ Jobbpreferenser
-- ✓ 7 arbetslivserfarenheter
-- ✓ 1 utbildning
-- ✓ 18 färdigheter
-- ✓ 4 CV-versioner (restaurang, kundtjänst, content, butik)
