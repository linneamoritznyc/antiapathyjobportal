-- ============================================================================
-- COMPLETE SUPABASE DATABASE MIGRATION
--
-- This file:
-- 1. Fixes schema mismatches (user_experiences table)
-- 2. Creates missing tables (user_volunteer, user_awards, user_cv_branscher)
-- 3. Deletes old/incomplete data
-- 4. Inserts all complete data:
--    - 1 Profile
--    - 19 Experiences
--    - 2 Education
--    - 37 Skills
--    - 4 Volunteer
--    - 7 Awards
--    - Cover letter preferences
--    - Job preferences
--    - 8 CV branscher
--
-- Instructions:
-- 1. Go to Supabase Dashboard → SQL Editor
-- 2. Create new query
-- 3. Paste this entire file
-- 4. Click "Run"
-- 5. Done!
-- ============================================================================

-- Get the user_id (assumes only 1 user in auth.users)
DO $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Get the first user from auth.users
    SELECT id INTO v_user_id FROM auth.users LIMIT 1;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'No user found in auth.users. Please create a user first.';
    END IF;

    RAISE NOTICE 'Using user_id: %', v_user_id;

    -- ========================================================================
    -- STEP 1: FIX SCHEMA MISMATCHES
    -- ========================================================================

    -- Fix user_experiences table: add dates and bullets columns if they don't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_experiences' AND column_name = 'dates'
    ) THEN
        ALTER TABLE user_experiences ADD COLUMN dates TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_experiences' AND column_name = 'bullets'
    ) THEN
        ALTER TABLE user_experiences ADD COLUMN bullets JSONB;
    END IF;

    -- Add categories column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_experiences' AND column_name = 'categories'
    ) THEN
        ALTER TABLE user_experiences ADD COLUMN categories TEXT[];
    END IF;

    -- Fix user_education table: add dates and bullets columns if they don't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_education' AND column_name = 'dates'
    ) THEN
        ALTER TABLE user_education ADD COLUMN dates TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_education' AND column_name = 'bullets'
    ) THEN
        ALTER TABLE user_education ADD COLUMN bullets JSONB;
    END IF;

    -- ========================================================================
    -- STEP 2: CREATE MISSING TABLES
    -- ========================================================================

    -- Create user_volunteer table
    CREATE TABLE IF NOT EXISTS user_volunteer (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
        organization TEXT NOT NULL,
        dates TEXT,
        bullets JSONB,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create user_awards table
    CREATE TABLE IF NOT EXISTS user_awards (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
        award_text TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create user_cv_branscher table
    CREATE TABLE IF NOT EXISTS user_cv_branscher (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
        bransch_id TEXT NOT NULL,
        bransch_name TEXT NOT NULL,
        focus TEXT,
        keywords TEXT[],
        is_active BOOLEAN DEFAULT TRUE,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- ========================================================================
    -- STEP 3: DELETE OLD/INCOMPLETE DATA
    -- ========================================================================

    DELETE FROM user_profiles WHERE user_id = v_user_id;
    DELETE FROM user_experiences WHERE user_id = v_user_id;
    DELETE FROM user_education WHERE user_id = v_user_id;
    DELETE FROM user_skills WHERE user_id = v_user_id;
    DELETE FROM user_volunteer WHERE user_id = v_user_id;
    DELETE FROM user_awards WHERE user_id = v_user_id;
    DELETE FROM user_cover_letter_preferences WHERE user_id = v_user_id;
    DELETE FROM user_job_preferences WHERE user_id = v_user_id;
    DELETE FROM user_cv_branscher WHERE user_id = v_user_id;

    -- ========================================================================
    -- STEP 4: INSERT COMPLETE DATA
    -- ========================================================================

    -- Insert Profile
    INSERT INTO user_profiles (
        user_id, full_name, email, phone, location,
        drivers_license, languages, certificates, about_me
    ) VALUES (
        v_user_id,
        'Linnea Moritz',
        'linneamoritz1@gmail.com',
        '0761166109',
        'Sollentuna',
        TRUE,
        ARRAY['Svenska (Modersmal)', 'Engelska (Flytande)', 'Tyska (grundlaggande)', 'Spanska (grundlaggande)', 'Mandarin (HSK niva 3)'],
        ARRAY['B-korkort (automat)', 'ICA kassahantering', 'Trygga mat', 'Roda Korset forsta hjalpen'],
        'Serviceinriktad och stresstalig med bred internationell erfarenhet. Minerva University (1.8% antagning). Jobbat i 7 lander. Flytande svenska och engelska.'
    );

    -- Insert Education (2 entries)
    INSERT INTO user_education (user_id, school, degree, location, dates, bullets, sort_order) VALUES
    (v_user_id, 'Minerva University', 'B.S in Social Science, Economics and Business Administration', 'San Francisco, USA', 'Aug 2017 - Maj 2021', '["Varldens mest innovativa universitet enligt WURI", "Antagningsgrad pa 1.8% - mest selektiva universitetet i USA", "Studerade i fem lander: USA, Sydkorea, Indien, Tyskland och Argentina", "Handledde 45 studenter i examensprojekt inom fem amnen och branscher"]'::jsonb, 1),
    (v_user_id, 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', 'Flekke, Norge', 'Aug 2015 - Maj 2017', '["Utvald som toppelev fran Sverige bland 120 sokande, fullt stipendium", "Bodde med 200 elever fran 96 olika lander med fokus pa internationell fred och forstaelse", "Roda Korsets diplom: Guldutmarkelse for teamwork, frivilligarbete och ledarskap (100+ timmar)"]'::jsonb, 2);

    -- Insert Experiences (19 entries)
    INSERT INTO user_experiences (user_id, company, title, location, dates, bullets, categories, sort_order) VALUES
    (v_user_id, 'Minerva University', 'Alumni Ambassador Western Europe', 'Stockholm', 'Sep 2024 - Pagaende', '["25% tjanst med sjalvstandig planering, cirka 40 timmar i manaden", "Genomfor strategisk marknadsforing genom resor till skolor och massor i Vasteuropa och Norden", "Bygger och underhaller databaser for skolkontakter, moten med SYO:er och studievagledare", "Ansvarar for logistik: bokning av flyg, hotell och transporter for stort geografiskt omrade"]'::jsonb, ARRAY['office', 'customerservice'], 1),
    (v_user_id, 'House of Beans, Hotorgshallen', 'Forsaljare/Barista', 'Stockholm', 'Aug 2024 - Feb 2025', '["Sjalvstandigt butiksansvar med forsaljning av te, kaffe och choklad", "Direktforsaljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar", "Hanterade kassa, kundservice och lagerhantering"]'::jsonb, ARRAY['restaurant', 'retail'], 2),
    (v_user_id, 'Profilgruppen', 'Anodiseringsoperator (Feriearbete)', 'Aseda', 'Juli 2024 - Aug 2024', '["Utforde tungt fysiskt arbete med fokus pa armlyft och materialhantering", "Arbetade pa tvaskift (06.00-14.00 och 14.00-23.00)", "Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor"]'::jsonb, ARRAY['industry'], 3),
    (v_user_id, 'Max Hamburgare', 'Restaurangbitrade', 'Vetlanda', 'April 2024 - Aug 2024', '["Arbetade i hogt tempo med drive-in, fritos, kok, servering, kassa och stad", "Levererade god kundservice och samarbetade effektivt med teamet under rusningstid"]'::jsonb, ARRAY['restaurant'], 4),
    (v_user_id, 'Keeping Tabs', 'Multimedia Technical Specialist', 'New York, USA', 'Nov 2022 - Juni 2023', '["Planerade och koordinerade konstsamling for Art Basel Hong Kong (70x30m skarm, Causeway Bay)", "Designade visuell merchandise och rullade ut forsaljnings- och logistikkampanj", "Utvecklade partnerskap med organisationer inom konstindustrin i USA", "Ansvarade for leadgenerering, orderleverans, fakturering och kundnojdhet"]'::jsonb, ARRAY['art', 'office'], 5),
    (v_user_id, '30 Campos Eliseos', 'Kubistisk malare', 'New York, USA', '2022 - 2024', '["Scoutad som professionell kubistmalare till prestigefylld konstsamlargrupp grundad i Florens", "En av endast fem konstnarer utvalda bland 500+ sokande", "Deltog i utstallningar i New York, Dubai, Seoul, Madrid och Florens"]'::jsonb, ARRAY['art'], 6),
    (v_user_id, 'TikTok/ByteDance', 'Kvalitetsgranskare - Amerikanska marknaden', 'Nashville, USA', 'Maj 2022 - Juni 2022', '["Granskade innehallsmoderatörernas arbete for att sakerstalla att de foljer riktlinjer", "Kvalitetssakrade moderering och bidrog till forbattrade processer"]'::jsonb, ARRAY['tech', 'content'], 7),
    (v_user_id, 'YouTube Ads (via Vaco)', 'Innehallsmoderator - Svenska marknaden', 'San Francisco, USA', 'Feb 2022 - Juni 2022', '["Flaggade olamplig reklam och bidrog till att utoka databaser med markerat innehall", "Foljde noggrant alla riktlinjer och samarbetade med det svenska teamet", "Deltog i regelbundna moten for att sakerstalla korrekt granskning av material"]'::jsonb, ARRAY['tech', 'content'], 8),
    (v_user_id, 'Clubhouse (via Vaco)', 'Innehallsmoderator - Skandinaviska och amerikanska marknaden', 'Walnut Creek, USA', 'Juni 2021 - Jan 2022', '["Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media", "Kategorier inkluderade hatiskt tal, sexuell exploatering, valdsbejakande extremism, CSAM och falsk information", "Hade fullt ansvar for att hantera alla arenden inom svenska, norska och danska marknaden", "Identifierade brister i standardiserade arbetsrutiner och drev policyforbttringar", "Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes"]'::jsonb, ARRAY['tech', 'customerservice', 'content'], 9),
    (v_user_id, 'Svensk-amerikanska handelskammaren', 'Marknadsforing och forsaljningsutveckling', 'San Francisco, USA', 'Juni 2021 - Sep 2021', '["Byggde upp natverk med 100+ svenska startups, myndigheter och foretag genom konferenser och event", "Okade handelskammarens natverk med 20% genom effektiv e-post- och LinkedIn-marknadsforing", "Assisterade tva svenska konsultkunder med databas av 120 forsaljningsleads i USA", "Organiserade kraftskiva for 80 skandinaver och amerikaner i samarbete med Norska klubben"]'::jsonb, ARRAY['office', 'customerservice'], 10),
    (v_user_id, 'Minerva University', 'Handledare for examensprojekt', 'San Francisco, USA', 'Sep 2020 - Maj 2021', '["Handledde 45 studenter i deras capstone-projekt inom VR, hallbart mode, varumarkesanalys och historiska romaner", "Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stod", "Gav kvalitativ och kvantitativ aterkoppling till over 90 uppgifter och 40 lektioner"]'::jsonb, ARRAY['office', 'art'], 11),
    (v_user_id, 'Kvarngarden aldreboende', 'Timvikarie', 'Vetlanda', 'Maj 2020 - Sep 2020', '["Omvardnad, medicinhantering, maltidsassistans, dokumentation och emotionellt stod", "Gav omsorg till aldre personer med demens och Alzheimers sjukdom", "Foljde noggrant covid-protokoll och arbetade bade morgon- och kvallspass"]'::jsonb, ARRAY['healthcare'], 12),
    (v_user_id, 'Minerva Project', 'Marknadsforing/Kundservice - Global Marketing Team', 'Berlin & Buenos Aires', 'Sep 2019 - April 2020', '["Samarbetade med globala marknadsforingsteamet for att oka antagningen till Minerva University", "Vagledde och stottade over 2000 sokande elever via Intercom med hogkvalitativ kundservice", "Svarade pa fragor fran elever i over 40 lander genom Intercom och personliga moten", "Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet"]'::jsonb, ARRAY['customerservice', 'office'], 13),
    (v_user_id, 'Google Ads (via Vaco)', 'Svensk innehallsanalytiker for gTech', 'Sunnyvale, USA / Seoul / Hyderabad', 'Maj 2018 - April 2019', '["Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak", "Utforde extraktion och granskning av innehall for over 100 annonser per dag", "Arbetade i USA och pa distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering", "Det svenska teamet uppnadde 100% mal for tjanstenivaavatalet"]'::jsonb, ARRAY['tech', 'content'], 14),
    (v_user_id, 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'San Francisco, USA', 'Sep 2017 - Maj 2018', '["Organiserade 60 evenemang for 210 internationella studenter, 2-3 per vecka", "Ansvarade for moten, budgetkontroll, narvaro, schemalggning och marknadsforing", "Organiserade stadsskattjakt dar studenter upptackte San Francisco", "Koordinerade gastforelasare och anvande mjukvara for eventlogistik"]'::jsonb, ARRAY['office', 'customerservice'], 15),
    (v_user_id, 'Wallby Sateri', 'Gardsvard/Receptionist', 'Vetlanda', 'Juni 2016 - Aug 2016', '["Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar", "Assisterade vid cafeet och bidrog till allman service"]'::jsonb, ARRAY['reception', 'customerservice'], 16),
    (v_user_id, 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och gront', 'Vetlanda & Varmdo', '2015, 2017, 2019', '["Arbetade i kassan, sjalvscanningen, frukt och gront, charken och blomavdelningen", "ICA-certifierad inom kassahantering, Trygga mat och sakerhet i butik"]'::jsonb, ARRAY['retail'], 17),
    (v_user_id, 'Coffeehouse by George', 'Cafepersonal', 'Stockholm', '2014 - 2015', '["Kassahantering och barista", "Hog serviceeniva i centralt lage"]'::jsonb, ARRAY['restaurant'], 18),
    (v_user_id, 'Siggesta Gard', 'Gardsvard/Tradgardsarbetare', 'Varmdo', '2014 - 2015', '["Kundbemotande pa stor evenemangsanlaggning (minigolf, restauranger, konferenser, hotell)", "Overseende roll med kommunikation mellan avdelningar. Ansvarade for marknad med ~1000 besokare/sondag", "Tradgardsarbete: klippte gras, rensade ogras, planterade, skrapsortering. Korde golfbil"]'::jsonb, ARRAY['industry', 'reception'], 19);

    -- Insert Skills (37 entries)
    INSERT INTO user_skills (user_id, category, skill_type, skill_text) VALUES
    -- General skills (13)
    (v_user_id, 'all', 'soft', 'Kundservice'),
    (v_user_id, 'all', 'soft', 'Kommunikation'),
    (v_user_id, 'all', 'soft', 'Teamwork'),
    (v_user_id, 'all', 'soft', 'Stresshantering'),
    (v_user_id, 'all', 'language', 'Svenska (Modersmal)'),
    (v_user_id, 'all', 'language', 'Engelska (Flytande)'),
    (v_user_id, 'all', 'language', 'Tyska (grundlaggande)'),
    (v_user_id, 'all', 'language', 'Spanska (grundlaggande)'),
    (v_user_id, 'all', 'language', 'Mandarin (HSK niva 3)'),
    (v_user_id, 'all', 'certificate', 'B-korkort'),
    (v_user_id, 'all', 'certificate', 'ICA kassahantering'),
    (v_user_id, 'all', 'certificate', 'Trygga mat'),
    (v_user_id, 'all', 'certificate', 'Roda Korset forsta hjalpen'),
    -- Restaurant skills (4)
    (v_user_id, 'restaurant', 'technical', 'Kassasystem'),
    (v_user_id, 'restaurant', 'technical', 'Barista'),
    (v_user_id, 'restaurant', 'technical', 'Servering'),
    (v_user_id, 'restaurant', 'certificate', 'Livsmedelshygien'),
    -- Tech/Content skills (13)
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
    -- Customer service skills (4)
    (v_user_id, 'customerservice', 'technical', 'Intercom'),
    (v_user_id, 'customerservice', 'technical', 'Zendesk'),
    (v_user_id, 'customerservice', 'technical', 'CRM-system'),
    (v_user_id, 'customerservice', 'soft', 'Problemlosning'),
    -- Retail skills (3)
    (v_user_id, 'retail', 'technical', 'Kassasystem'),
    (v_user_id, 'retail', 'technical', 'Lagerhantering'),
    (v_user_id, 'retail', 'technical', 'Merforsaljning');

    -- Insert Volunteer (4 entries)
    INSERT INTO user_volunteer (user_id, organization, dates, bullets, sort_order) VALUES
    (v_user_id, 'LEAF (Living Environment and Future)', '2016 - 2017', '["Ledde elevgrupp for att utbilda skolan i miljotank. Organiserade presentationer och kampanjer", "Skapade modemagasin for att sponsra hallbart jordbruksprojekt i Ghana. Samlade in 30,000 kr"]'::jsonb, 1),
    (v_user_id, 'The Right Solution Project', 'Mars 2013 - April 2015', '["Tog initiativ att finansiera NGO for kvinnors utbildning vid 15 ars alder", "Samlade in over 120,000 kr genom evenemang och forsaljning", "Tillhandaholl 400+ vardpaket med hygienprodukter till etiopiska skolor. Tacktes i media tva ganger"]'::jsonb, 2),
    (v_user_id, 'India Unlimited Utbytesprogram', 'Nov 2014 - Feb 2015', '["Deltog i EU-projekt for att framja fredliga relationer mellan Sverige och Indien", "Koordinerade hygienprojekt och fick kunskap om hallbar utveckling i utvecklingslander"]'::jsonb, 3),
    (v_user_id, 'Varmdo Forsamling', '2012 - 2014', '["Ledare for 3 konfirmandgrupper under 2 ar. Ledare pa tre veckors sommarlager pa Angsholmen", "Svenska Kyrkan: Ledarskapskurs steg 1 och 2"]'::jsonb, 4);

    -- Insert Awards (7 entries)
    INSERT INTO user_awards (user_id, award_text, sort_order) VALUES
    (v_user_id, '1:a pris Stockholms Konstsalong 2024 - Jurybedomd utstallning, nominerad Publikens Favorit', 1),
    (v_user_id, '1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnarer, fick soloutstallning', 2),
    (v_user_id, '1:a pris Murrays Creative Contest 2022 - Detroit-baserad tavling med specialdesign', 3),
    (v_user_id, 'Global Startup Weekend Stockholm - Vinnare for Terra Finance (Google for Startups & Techstars)', 4),
    (v_user_id, 'Tredje pris Chinese Bridge - Nationell tavling i kinesiskt sprak, Bergen 2016', 5),
    (v_user_id, 'Roda Korsets diplom - Guldutmarkelse for teamwork och ledarskap (100+ volontartimmar)', 6),
    (v_user_id, 'Minerva University Award for Initiative 2018', 7);

    -- Insert Cover Letter Preferences
    INSERT INTO user_cover_letter_preferences (
        user_id, tone, max_words, greeting_style, signature_style,
        sign_off_name, sign_off_phone, sign_off_email,
        always_mention, never_mention, custom_ai_instructions
    ) VALUES (
        v_user_id,
        'professional_friendly',
        200,
        'Hej!',
        'Med vanliga halsningar',
        'Linnea Moritz',
        '076-116 61 09',
        'linneamoritz1@gmail.com',
        ARRAY['flexibel med tider', 'korkort', 'flytande engelska'],
        ARRAY['konst', 'malning', 'utstallningar', 'Shopify', 'e-handel', 'oljemaalning', 'linneamoritz.com'],
        'Skriv pa naturlig, flytande svenska. Undvik AI-floskler som "gedigen", "brinner for", "vittnar om". Beratta varfor jag vill ha just det jobbet.'
    );

    -- Insert Job Preferences
    INSERT INTO user_job_preferences (
        user_id, preferred_locations, search_keywords,
        excluded_keywords, excluded_companies, job_types, remote_only
    ) VALUES (
        v_user_id,
        ARRAY['Stockholm', 'Sollentuna', 'Sundbyberg', 'Vetlanda'],
        ARRAY['servitor', 'kundtjanst', 'content moderator', 'butik', 'cafe', 'reception', 'lager'],
        ARRAY[]::TEXT[],
        ARRAY[]::TEXT[],
        ARRAY['heltid', 'deltid'],
        FALSE
    );

    -- Insert CV Branscher (8 entries)
    INSERT INTO user_cv_branscher (user_id, bransch_id, bransch_name, focus, keywords, is_active, sort_order) VALUES
    (v_user_id, 'restaurant', 'Restaurang & Cafe', 'Service, tempo, kundkontakt', ARRAY['servitor', 'servitris', 'restaurang', 'cafe', 'barista', 'kok'], TRUE, 1),
    (v_user_id, 'retail', 'Butik & Kassa', 'Forsaljning, kassa, kundservice', ARRAY['butik', 'kassa', 'saljare', 'ica', 'coop'], TRUE, 2),
    (v_user_id, 'customerservice', 'Kundtjanst & Support', 'Kommunikation, problemlosning, internationell erfarenhet', ARRAY['kundtjanst', 'support', 'kundservice', 'helpdesk'], TRUE, 3),
    (v_user_id, 'content', 'Content & Moderation', 'Trust & Safety, policy, granskning', ARRAY['moderator', 'content', 'review', 'granskning', 'trust'], TRUE, 4),
    (v_user_id, 'tech', 'Tech & Kontor', 'Analytiskt arbete, data, tech-bolag', ARRAY['tech', 'IT', 'data', 'analyst', 'kontor'], TRUE, 5),
    (v_user_id, 'industry', 'Industri & Tradgard', 'Fysiskt arbete, skift, materialhantering', ARRAY['industri', 'lager', 'produktion', 'operator', 'tradgard'], TRUE, 6),
    (v_user_id, 'healthcare', 'Vard & Omsorg', 'Omvardnad, empati, medicinhantering', ARRAY['vard', 'omsorg', 'aldre', 'sjukvard'], TRUE, 7),
    (v_user_id, 'art', 'Konst & Kultur', 'Konstnarligt arbete, utstallningar, projektledning', ARRAY['konst', 'kultur', 'galleri', 'museum', 'kreativ'], TRUE, 8);

    RAISE NOTICE '✅ Migration complete!';
    RAISE NOTICE '  - Profile: 1';
    RAISE NOTICE '  - Education: 2';
    RAISE NOTICE '  - Experiences: 19';
    RAISE NOTICE '  - Skills: 37';
    RAISE NOTICE '  - Volunteer: 4';
    RAISE NOTICE '  - Awards: 7';
    RAISE NOTICE '  - Cover Letter Prefs: 1';
    RAISE NOTICE '  - Job Prefs: 1';
    RAISE NOTICE '  - CV Branscher: 8';

END $$;
