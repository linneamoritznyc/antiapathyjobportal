-- ============================================
-- COMPLETE MIGRATION: All Linnea's Data to Supabase
-- Paste this entire file into Supabase SQL Editor and run it
-- ============================================

DO $$
DECLARE
    v_user_id uuid;
BEGIN
    -- Get the user_id (there's only 1 user in Supabase)
    SELECT id INTO v_user_id FROM auth.users LIMIT 1;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'No user found in auth.users';
    END IF;

    RAISE NOTICE 'Using user_id: %', v_user_id;

    -- ============================================
    -- STEP 1: Create missing tables
    -- ============================================

    -- user_volunteer table
    CREATE TABLE IF NOT EXISTS public.user_volunteer (
        id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
        organization text NOT NULL,
        dates text,
        description text,
        sort_order integer DEFAULT 0,
        created_at timestamptz DEFAULT now()
    );

    -- user_awards table
    CREATE TABLE IF NOT EXISTS public.user_awards (
        id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
        award_text text NOT NULL,
        sort_order integer DEFAULT 0,
        created_at timestamptz DEFAULT now()
    );

    -- user_cv_branscher table
    CREATE TABLE IF NOT EXISTS public.user_cv_branscher (
        id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
        bransch_id text NOT NULL,
        bransch_name text,
        focus text,
        keywords text[] DEFAULT ARRAY[]::text[],
        is_active boolean DEFAULT true,
        sort_order integer DEFAULT 0,
        created_at timestamptz DEFAULT now(),
        UNIQUE(user_id, bransch_id)
    );

    -- Enable RLS on new tables
    ALTER TABLE public.user_volunteer ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.user_awards ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.user_cv_branscher ENABLE ROW LEVEL SECURITY;

    -- RLS policies for user_volunteer
    DROP POLICY IF EXISTS "Users can manage own volunteer" ON public.user_volunteer;
    CREATE POLICY "Users can manage own volunteer" ON public.user_volunteer
        FOR ALL USING (auth.uid() = user_id);
    DROP POLICY IF EXISTS "Service role full access volunteer" ON public.user_volunteer;
    CREATE POLICY "Service role full access volunteer" ON public.user_volunteer
        FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

    -- RLS policies for user_awards
    DROP POLICY IF EXISTS "Users can manage own awards" ON public.user_awards;
    CREATE POLICY "Users can manage own awards" ON public.user_awards
        FOR ALL USING (auth.uid() = user_id);
    DROP POLICY IF EXISTS "Service role full access awards" ON public.user_awards;
    CREATE POLICY "Service role full access awards" ON public.user_awards
        FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

    -- RLS policies for user_cv_branscher
    DROP POLICY IF EXISTS "Users can manage own branscher" ON public.user_cv_branscher;
    CREATE POLICY "Users can manage own branscher" ON public.user_cv_branscher
        FOR ALL USING (auth.uid() = user_id);
    DROP POLICY IF EXISTS "Service role full access branscher" ON public.user_cv_branscher;
    CREATE POLICY "Service role full access branscher" ON public.user_cv_branscher
        FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

    -- Add missing columns to existing tables
    ALTER TABLE public.user_cover_letter_preferences
        ADD COLUMN IF NOT EXISTS sign_off_name text,
        ADD COLUMN IF NOT EXISTS sign_off_phone text,
        ADD COLUMN IF NOT EXISTS sign_off_email text;

    ALTER TABLE public.user_job_preferences
        ADD COLUMN IF NOT EXISTS preferred_locations text[] DEFAULT ARRAY[]::text[],
        ADD COLUMN IF NOT EXISTS search_keywords text[] DEFAULT ARRAY[]::text[],
        ADD COLUMN IF NOT EXISTS remote_only boolean DEFAULT false,
        ADD COLUMN IF NOT EXISTS excluded_keywords text[] DEFAULT ARRAY[]::text[],
        ADD COLUMN IF NOT EXISTS excluded_companies text[] DEFAULT ARRAY[]::text[];

    -- ============================================
    -- STEP 2: Delete all old data
    -- ============================================

    DELETE FROM public.user_experiences WHERE user_id = v_user_id;
    DELETE FROM public.user_education WHERE user_id = v_user_id;
    DELETE FROM public.user_skills WHERE user_id = v_user_id;
    DELETE FROM public.user_cvs WHERE user_id = v_user_id;
    DELETE FROM public.user_volunteer WHERE user_id = v_user_id;
    DELETE FROM public.user_awards WHERE user_id = v_user_id;
    DELETE FROM public.user_cover_letter_preferences WHERE user_id = v_user_id;
    DELETE FROM public.user_job_preferences WHERE user_id = v_user_id;
    DELETE FROM public.user_cv_branscher WHERE user_id = v_user_id;
    DELETE FROM public.user_profiles WHERE user_id = v_user_id;

    RAISE NOTICE 'Deleted old data';

    -- ============================================
    -- STEP 3: Insert complete data
    -- ============================================

    -- Profile
    INSERT INTO public.user_profiles (user_id, full_name, email, phone, location, drivers_license, languages)
    VALUES (
        v_user_id,
        'Linnea Moritz',
        'linneamoritz1@gmail.com',
        '0761166109',
        'Sollentuna',
        true,
        ARRAY['Svenska (Modersmål)', 'Engelska (Flytande)', 'Tyska (grundläggande)', 'Spanska (grundläggande)', 'Mandarin (HSK nivå 3)']
    );

    -- Experiences (19 total)
    INSERT INTO public.user_experiences (user_id, company, title, location, start_date, end_date, description, categories, sort_order)
    VALUES
        (v_user_id, 'Minerva University', 'Alumni Ambassador Western Europe', 'Stockholm', 'Sep 2024', 'Pågående',
         '25% tjänst med självständig planering, cirka 40 timmar i månaden
Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden
Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare
Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område',
         ARRAY['office', 'customerservice'], 1),

        (v_user_id, 'House of Beans, Hötorgshallen', 'Försäljare/Barista', 'Stockholm', 'Aug 2024', 'Feb 2025',
         'Självständigt butiksansvar med försäljning av te, kaffe och choklad
Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar
Hanterade kassa, kundservice och lagerhantering',
         ARRAY['restaurant', 'retail'], 2),

        (v_user_id, 'Profilgruppen', 'Anodiseringsoperatör (Feriearbete)', 'Åseda', 'Juli 2024', 'Aug 2024',
         'Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering
Arbetade på tvåskift (06.00-14.00 och 14.00-23.00)
Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor',
         ARRAY['industry'], 3),

        (v_user_id, 'Max Hamburgare', 'Restaurangbiträde', 'Vetlanda', 'April 2024', 'Aug 2024',
         'Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ
Levererade god kundservice och samarbetade effektivt med teamet under rusningstid',
         ARRAY['restaurant'], 4),

        (v_user_id, 'Keeping Tabs', 'Multimedia Technical Specialist', 'New York, USA', 'Nov 2022', 'Juni 2023',
         'Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay)
Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj
Utvecklade partnerskap med organisationer inom konstindustrin i USA
Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet',
         ARRAY['art', 'office'], 5),

        (v_user_id, '30 Campos Eliseos', 'Kubistisk målare', 'New York, USA', '2022', '2024',
         'Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens
En av endast fem konstnärer utvalda bland 500+ sökande
Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens',
         ARRAY['art'], 6),

        (v_user_id, 'TikTok/ByteDance', 'Kvalitetsgranskare - Amerikanska marknaden', 'Nashville, USA', 'Maj 2022', 'Juni 2022',
         'Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer
Kvalitetssäkrade moderering och bidrog till förbättrade processer',
         ARRAY['tech', 'content'], 7),

        (v_user_id, 'YouTube Ads (via Vaco)', 'Innehållsmoderator - Svenska marknaden', 'San Francisco, USA', 'Feb 2022', 'Juni 2022',
         'Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll
Följde noggrant alla riktlinjer och samarbetade med det svenska teamet
Deltog i regelbundna möten för att säkerställa korrekt granskning av material',
         ARRAY['tech', 'content'], 8),

        (v_user_id, 'Clubhouse (via Vaco)', 'Innehållsmoderator - Skandinaviska och amerikanska marknaden', 'Walnut Creek, USA', 'Juni 2021', 'Jan 2022',
         'Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media
Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information
Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden
Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar
Ökade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmål uppfylldes',
         ARRAY['tech', 'customerservice', 'content'], 9),

        (v_user_id, 'Svensk-amerikanska handelskammaren', 'Marknadsföring och försäljningsutveckling', 'San Francisco, USA', 'Juni 2021', 'Sep 2021',
         'Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event
Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring
Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA
Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben',
         ARRAY['office', 'customerservice'], 10),

        (v_user_id, 'Minerva University', 'Handledare för examensprojekt', 'San Francisco, USA', 'Sep 2020', 'Maj 2021',
         'Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner
Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd
Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner',
         ARRAY['office', 'art'], 11),

        (v_user_id, 'Kvarngården äldreboende', 'Timvikarie', 'Vetlanda', 'Maj 2020', 'Sep 2020',
         'Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd
Gav omsorg till äldre personer med demens och Alzheimers sjukdom
Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass',
         ARRAY['healthcare'], 12),

        (v_user_id, 'Minerva Project', 'Marknadsföring/Kundservice - Global Marketing Team', 'Berlin & Buenos Aires', 'Sep 2019', 'April 2020',
         'Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University
Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice
Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten
Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet',
         ARRAY['customerservice', 'office'], 13),

        (v_user_id, 'Google Ads (via Vaco)', 'Svensk innehållsanalytiker för gTech', 'Sunnyvale, USA / Seoul / Hyderabad', 'Maj 2018', 'April 2019',
         'Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk
Utförde extraktion och granskning av innehåll för över 100 annonser per dag
Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering
Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet',
         ARRAY['tech', 'content'], 14),

        (v_user_id, 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'San Francisco, USA', 'Sep 2017', 'Maj 2018',
         'Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka
Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring
Organiserade stadsskattjakt där studenter upptäckte San Francisco
Koordinerade gästföreläsare och använde mjukvara för eventlogistik',
         ARRAY['office', 'customerservice'], 15),

        (v_user_id, 'Wallby Säteri', 'Gårdsvärd/Receptionist', 'Vetlanda', 'Juni 2016', 'Aug 2016',
         'Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar
Assisterade vid caféet och bidrog till allmän service',
         ARRAY['reception', 'customerservice'], 16),

        (v_user_id, 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och grönt', 'Vetlanda & Värmdö', '2015', '2019',
         'Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen
ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik',
         ARRAY['retail'], 17),

        (v_user_id, 'Coffeehouse by George', 'Cafépersonal', 'Stockholm', '2014', '2015',
         'Kassahantering och barista
Hög servicenivå i centralt läge',
         ARRAY['restaurant'], 18),

        (v_user_id, 'Siggesta Gård', 'Gårdsvärd/Trädgårdsarbetare', 'Värmdö', '2014', '2015',
         'Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell)
Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag
Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil',
         ARRAY['industry', 'reception'], 19);

    RAISE NOTICE 'Inserted 19 experiences';

    -- Education (2 total)
    INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date, sort_order)
    VALUES
        (v_user_id, 'Minerva University', 'B.S in Social Science, Economics and Business Administration', 'Business, Arts & Humanities', 'San Francisco, USA', 'Aug 2017', 'Maj 2021', 1),
        (v_user_id, 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', 'International Baccalaureate', 'Flekke, Norge', 'Aug 2015', 'Maj 2017', 2);

    RAISE NOTICE 'Inserted 2 education records';

    -- Skills (37 total)
    INSERT INTO public.user_skills (user_id, category, skill_type, skill_text)
    VALUES
        -- General
        (v_user_id, 'all', 'soft', 'Kundservice'),
        (v_user_id, 'all', 'soft', 'Kommunikation'),
        (v_user_id, 'all', 'soft', 'Teamwork'),
        (v_user_id, 'all', 'soft', 'Stresshantering'),
        (v_user_id, 'all', 'language', 'Svenska (Modersmål)'),
        (v_user_id, 'all', 'language', 'Engelska (Flytande)'),
        (v_user_id, 'all', 'language', 'Tyska (grundläggande)'),
        (v_user_id, 'all', 'language', 'Spanska (grundläggande)'),
        (v_user_id, 'all', 'language', 'Mandarin (HSK nivå 3)'),
        (v_user_id, 'all', 'certificate', 'B-körkort'),
        (v_user_id, 'all', 'certificate', 'ICA kassahantering'),
        (v_user_id, 'all', 'certificate', 'Trygga mat'),
        (v_user_id, 'all', 'certificate', 'Röda Korset första hjälpen'),
        -- Restaurant
        (v_user_id, 'restaurant', 'technical', 'Kassasystem'),
        (v_user_id, 'restaurant', 'technical', 'Barista'),
        (v_user_id, 'restaurant', 'technical', 'Servering'),
        (v_user_id, 'restaurant', 'certificate', 'Livsmedelshygien'),
        -- Tech/Content
        (v_user_id, 'tech', 'technical', 'Content Moderation'),
        (v_user_id, 'tech', 'technical', 'Trust & Safety'),
        (v_user_id, 'tech', 'technical', 'Policy Compliance'),
        (v_user_id, 'tech', 'technical', 'Data Analysis'),
        (v_user_id, 'tech', 'technical', 'Python'),
        (v_user_id, 'tech', 'technical', 'SQL'),
        (v_user_id, 'tech', 'technical', 'Tableau'),
        (v_user_id, 'tech', 'technical', 'Google Analytics'),
        (v_user_id, 'tech', 'technical', 'Google Ads'),
        (v_user_id, 'tech', 'technical', 'Facebook Ads'),
        (v_user_id, 'tech', 'technical', 'Adobe Creative Suite'),
        (v_user_id, 'tech', 'technical', 'Content SEO'),
        (v_user_id, 'tech', 'technical', 'Excel/Google Sheets'),
        -- Customer service
        (v_user_id, 'customerservice', 'technical', 'Intercom'),
        (v_user_id, 'customerservice', 'technical', 'Zendesk'),
        (v_user_id, 'customerservice', 'technical', 'CRM-system'),
        (v_user_id, 'customerservice', 'soft', 'Problemlösning'),
        -- Retail
        (v_user_id, 'retail', 'technical', 'Kassasystem'),
        (v_user_id, 'retail', 'technical', 'Lagerhantering'),
        (v_user_id, 'retail', 'technical', 'Merförsäljning');

    RAISE NOTICE 'Inserted 37 skills';

    -- Volunteer (4 total)
    INSERT INTO public.user_volunteer (user_id, organization, dates, description, sort_order)
    VALUES
        (v_user_id, 'LEAF (Living Environment and Future)', '2016 - 2017',
         'Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer
Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr', 1),
        (v_user_id, 'The Right Solution Project', 'Mars 2013 - April 2015',
         'Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder
Samlade in över 120,000 kr genom evenemang och försäljning
Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger', 2),
        (v_user_id, 'India Unlimited Utbytesprogram', 'Nov 2014 - Feb 2015',
         'Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien
Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer', 3),
        (v_user_id, 'Värmdö Församling', '2012 - 2014',
         'Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen
Svenska Kyrkan: Ledarskapskurs steg 1 och 2', 4);

    RAISE NOTICE 'Inserted 4 volunteer records';

    -- Awards (7 total)
    INSERT INTO public.user_awards (user_id, award_text, sort_order)
    VALUES
        (v_user_id, '1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad Publikens Favorit', 1),
        (v_user_id, '1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning', 2),
        (v_user_id, '1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign', 3),
        (v_user_id, 'Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars)', 4),
        (v_user_id, 'Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016', 5),
        (v_user_id, 'Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar)', 6),
        (v_user_id, 'Minerva University Award for Initiative 2018', 7);

    RAISE NOTICE 'Inserted 7 awards';

    -- Cover letter preferences
    INSERT INTO public.user_cover_letter_preferences (
        user_id, tone, max_words, greeting_style, signature_style,
        sign_off_name, sign_off_phone, sign_off_email,
        always_mention, never_mention
    )
    VALUES (
        v_user_id,
        'professional',
        200,
        'Hej!',
        'Med vänliga hälsningar',
        'Linnea Moritz',
        '076-116 61 09',
        'linneamoritz1@gmail.com',
        ARRAY['flexibel med tider', 'körkort', 'flytande engelska'],
        ARRAY['konst', 'målning', 'utställningar', 'Shopify', 'e-handel', 'oljemålning', 'linneamoritz.com']
    );

    RAISE NOTICE 'Inserted cover letter preferences';

    -- Job preferences
    INSERT INTO public.user_job_preferences (
        user_id, job_titles, locations, job_types,
        preferred_locations, search_keywords, remote_only
    )
    VALUES (
        v_user_id,
        'servitör, kundtjänst, content moderator, butik, café, reception, lager',
        'Stockholm, Sollentuna, Sundbyberg, Vetlanda',
        ARRAY['heltid', 'deltid'],
        ARRAY['Stockholm', 'Sollentuna', 'Sundbyberg', 'Vetlanda'],
        ARRAY['servitör', 'kundtjänst', 'content moderator', 'butik', 'café', 'reception', 'lager'],
        false
    );

    RAISE NOTICE 'Inserted job preferences';

    -- CV Branscher (8 total)
    INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, focus, keywords, is_active, sort_order)
    VALUES
        (v_user_id, 'restaurant', 'Restaurang & Café', 'Service, tempo, kundkontakt',
         ARRAY['servitör', 'servitris', 'restaurang', 'café', 'barista', 'kök'], true, 1),
        (v_user_id, 'retail', 'Butik & Kassa', 'Försäljning, kassa, kundservice',
         ARRAY['butik', 'kassa', 'säljare', 'ica', 'coop'], true, 2),
        (v_user_id, 'customerservice', 'Kundtjänst & Support', 'Kommunikation, problemlösning, internationell erfarenhet',
         ARRAY['kundtjänst', 'support', 'kundservice', 'helpdesk'], true, 3),
        (v_user_id, 'content', 'Content & Moderation', 'Trust & Safety, policy, granskning',
         ARRAY['moderator', 'content', 'review', 'granskning', 'trust'], true, 4),
        (v_user_id, 'tech', 'Tech & Kontor', 'Analytiskt arbete, data, tech-bolag',
         ARRAY['tech', 'IT', 'data', 'analyst', 'kontor'], true, 5),
        (v_user_id, 'industry', 'Industri & Trädgård', 'Fysiskt arbete, skift, materialhantering',
         ARRAY['industri', 'lager', 'produktion', 'operatör', 'trädgård'], true, 6),
        (v_user_id, 'healthcare', 'Vård & Omsorg', 'Omvårdnad, empati, medicinhantering',
         ARRAY['vård', 'omsorg', 'äldre', 'sjukvård'], true, 7),
        (v_user_id, 'art', 'Konst & Kultur', 'Konstnärligt arbete, utställningar, projektledning',
         ARRAY['konst', 'kultur', 'galleri', 'museum', 'kreativ'], true, 8);

    RAISE NOTICE 'Inserted 8 CV branscher';

END $$;

-- ============================================
-- STEP 4: Verification - Show counts
-- ============================================

SELECT
    'user_profiles' as table_name,
    COUNT(*)::int as count
FROM public.user_profiles
UNION ALL
SELECT
    'user_experiences',
    COUNT(*)::int
FROM public.user_experiences
UNION ALL
SELECT
    'user_education',
    COUNT(*)::int
FROM public.user_education
UNION ALL
SELECT
    'user_skills',
    COUNT(*)::int
FROM public.user_skills
UNION ALL
SELECT
    'user_volunteer',
    COUNT(*)::int
FROM public.user_volunteer
UNION ALL
SELECT
    'user_awards',
    COUNT(*)::int
FROM public.user_awards
UNION ALL
SELECT
    'user_cover_letter_preferences',
    COUNT(*)::int
FROM public.user_cover_letter_preferences
UNION ALL
SELECT
    'user_job_preferences',
    COUNT(*)::int
FROM public.user_job_preferences
UNION ALL
SELECT
    'user_cv_branscher',
    COUNT(*)::int
FROM public.user_cv_branscher
ORDER BY table_name;

-- Expected output:
-- user_awards: 7
-- user_cover_letter_preferences: 1
-- user_cv_branscher: 8
-- user_education: 2
-- user_experiences: 19
-- user_job_preferences: 1
-- user_profiles: 1
-- user_skills: 37
-- user_volunteer: 4

    -- CV texts (8 full versions from PDFs)
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES
        (v_user_id, 'restaurant', 'Restaurang & Café', '🍽️', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Coffeehouse by George - Nacka
Cafépersonal | 2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');

    RAISE NOTICE 'Inserted restaurant CV';


    -- Retail CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'retail', 'Butik & Kassa', '🛒', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

Coffeehouse by George - Nacka
Cafépersonal | 2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted retail CV';


    -- Kundtjanst & Support CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'customerservice', 'Kundtjanst & Support', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted customerservice CV';

    -- Content & Moderation CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'content', 'Content & Moderation', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 – Juni 2022
● Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer.
● Kvalitetssäkrade moderering och bidrog till förbättrade processer.

YouTube Ads (via Vaco) - San Francisco, USA
Innehållsmoderator - Svenska marknaden | Feb 2022 – Juni 2022
● Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll.
● Följde noggrant alla riktlinjer och samarbetade med det svenska teamet.
● Deltog i regelbundna möten för att säkerställa korrekt granskning av material.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Svensk-amerikanska handelskammaren i San Francisco och Silicon Valley - San Francisco, USA
Marknadsföring och försäljningsutveckling | Juni 2021 – Sep 2021
● Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event.
● Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring.
● Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA.
● Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted content CV';

    -- Tech & Kontor CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'tech', 'Tech & Kontor', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 – Juni 2022
● Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer.
● Kvalitetssäkrade moderering och bidrog till förbättrade processer.

YouTube Ads (via Vaco) - San Francisco, USA
Innehållsmoderator - Svenska marknaden | Feb 2022 – Juni 2022
● Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll.
● Följde noggrant alla riktlinjer och samarbetade med det svenska teamet.
● Deltog i regelbundna möten för att säkerställa korrekt granskning av material.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Svensk-amerikanska handelskammaren i San Francisco och Silicon Valley - San Francisco, USA
Marknadsföring och försäljningsutveckling | Juni 2021 – Sep 2021
● Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event.
● Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring.
● Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA.
● Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted tech CV';

    -- Industri & Tradgard CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'industry', 'Industri & Tradgard', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

Profilgruppen - Åseda, Sverige
Anodiseringsoperatör (Feriearbete) | Juli 2024 – Aug 2024
● Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering.
● Arbetade på tvåskift (06.00-14.00 och 14.00-23.00), vilket visade flexibilitet och anpassningsförmåga.
● Genomgick 3-timmarsutbildning i handtravers och hanterade material.
● Samarbetade effektivt med dagligen roterande kollegor, vilket visade stark teamkänsla.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Kvarngården äldreboende - Vetlanda
Timvikarie | Maj 2020 – Sep 2020
● Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd.
● Gav omsorg till äldre personer med demens och Alzheimers sjukdom.
● Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted industry CV';

    -- Vard & Omsorg CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'healthcare', 'Vard & Omsorg', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Kvarngården äldreboende - Vetlanda
Timvikarie | Maj 2020 – Sep 2020
● Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd.
● Gav omsorg till äldre personer med demens och Alzheimers sjukdom.
● Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted healthcare CV';

    -- Konst & Kultur CV
    INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text)
    VALUES (v_user_id, 'art', 'Konst & Kultur', '', 'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Keeping Tabs - New York, USA
Multimedia Technical Specialist | Nov 2022 – Juni 2023
● Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay).
● Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj.
● Utvecklade partnerskap med organisationer inom konstindustrin i USA.
● Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.

30 Campos Eliseos - New York, USA
Kubistisk målare | 2022 – 2024
● Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens.
● En av endast fem konstnärer utvalda bland 500+ sökande.
● Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.

Minerva University - San Francisco, USA
Handledare för examensprojekt | Sep 2020 – Maj 2021
● Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner.
● Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd.
● Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

Minerva Project - Student Experience Team - San Francisco, USA
Evenemangskoordinator och elevhemsvärd | Sep 2017 – Maj 2018
● Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka.
● Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring.
● Organiserade stadsskattjakt där studenter upptäckte San Francisco och utvidgade kontaktnät.
● Koordinerade gästföreläsare och använde mjukvara för eventlogistik och närvarohantering.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.');
    RAISE NOTICE 'Inserted art CV';

END $$;

-- ============================================
-- STEP 4: Verification - Show counts
-- ============================================

SELECT
    'user_profiles' as table_name,
    COUNT(*)::int as count
FROM public.user_profiles
UNION ALL
SELECT
    'user_experiences',
    COUNT(*)::int
FROM public.user_experiences
UNION ALL
SELECT
    'user_education',
    COUNT(*)::int
FROM public.user_education
UNION ALL
SELECT
    'user_skills',
    COUNT(*)::int
FROM public.user_skills
UNION ALL
SELECT
    'user_volunteer',
    COUNT(*)::int
FROM public.user_volunteer
UNION ALL
SELECT
    'user_awards',
    COUNT(*)::int
FROM public.user_awards
UNION ALL
SELECT
    'user_cover_letter_preferences',
    COUNT(*)::int
FROM public.user_cover_letter_preferences
UNION ALL
SELECT
    'user_job_preferences',
    COUNT(*)::int
FROM public.user_job_preferences
UNION ALL
SELECT
    'user_cv_branscher',
    COUNT(*)::int
FROM public.user_cv_branscher
UNION ALL
SELECT
    'user_cvs',
    COUNT(*)::int
FROM public.user_cvs
ORDER BY table_name;

-- Expected output:
-- user_awards: 7
-- user_cover_letter_preferences: 1
-- user_cv_branscher: 8
-- user_cvs: 8
-- user_education: 2
-- user_experiences: 19
-- user_job_preferences: 1
-- user_profiles: 1
-- user_skills: 37
-- user_volunteer: 4
