-- ============================================
-- COMPLETE MIGRATION: All Linnea's Data to Supabase
-- Paste this entire file into Supabase SQL Editor and run it
-- ============================================

-- ============================================
-- STEP 1: Delete all old data
-- ============================================
DELETE FROM public.user_experiences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_education WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_skills WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_cvs WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_volunteer WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_awards WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_cover_letter_preferences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_job_preferences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_cv_branscher WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_profiles WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
-- ============================================
-- STEP 2: Insert complete data
-- ============================================

-- Profile
INSERT INTO public.user_profiles (user_id, full_name, email, phone, location, drivers_license, languages)
VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
        'Linnea Moritz',
        'linneamoritz1@gmail.com',
        '0761166109',
        'Sollentuna',
        true,
        ARRAY['Svenska (Modersmål)', 'Engelska (Flytande)', 'Tyska (grundläggande)', 'Spanska (grundläggande)', 'Mandarin (HSK nivå 3)']
    );
    -- Experiences (19 total)
    INSERT INTO public.user_experiences (user_id, company, title, start_date, end_date, description, categories, sort_order)
    VALUES
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'Alumni Ambassador Western Europe', 'Sep 2024', 'Pågående',
         '25% tjänst med självständig planering, cirka 40 timmar i månaden. Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden. Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare. Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.',
         ARRAY['office', 'customerservice'], 1),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'House of Beans, Hötorgshallen', 'Försäljare/Barista', 'Aug 2024', 'Feb 2025',
         'Självständigt butiksansvar med försäljning av te, kaffe och choklad. Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar. Hanterade kassa, kundservice och lagerhantering.',
         ARRAY['restaurant', 'retail'], 2),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Profilgruppen', 'Anodiseringsoperatör (Feriearbete)', 'Juli 2024', 'Aug 2024',
         'Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering. Arbetade på tvåskift (06.00-14.00 och 14.00-23.00). Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor.',
         ARRAY['industry'], 3),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Max Hamburgare', 'Restaurangbiträde', 'April 2024', 'Aug 2024',
         'Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ. Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.',
         ARRAY['restaurant'], 4),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Keeping Tabs', 'Multimedia Technical Specialist', 'Nov 2022', 'Juni 2023',
         'Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay). Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj. Utvecklade partnerskap med organisationer inom konstindustrin i USA. Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.',
         ARRAY['art', 'office'], 5),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', '30 Campos Eliseos', 'Kubistisk målare', '2022', '2024',
         'Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens. En av endast fem konstnärer utvalda bland 500+ sökande. Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.',
         ARRAY['art'], 6),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'TikTok/ByteDance', 'Kvalitetsgranskare - Amerikanska marknaden', 'Maj 2022', 'Juni 2022',
         'Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer. Kvalitetssäkrade moderering och bidrog till förbättrade processer.',
         ARRAY['tech', 'content'], 7),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'YouTube Ads (via Vaco)', 'Innehållsmoderator - Svenska marknaden', 'Feb 2022', 'Juni 2022',
         'Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll. Följde noggrant alla riktlinjer och samarbetade med det svenska teamet. Deltog i regelbundna möten för att säkerställa korrekt granskning av material.',
         ARRAY['tech', 'content'], 8),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Clubhouse (via Vaco)', 'Innehållsmoderator - Skandinaviska och amerikanska marknaden', 'Juni 2021', 'Jan 2022',
         'Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media. Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information. Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden. Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar. Ökade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmål uppfylldes.',
         ARRAY['tech', 'customerservice', 'content'], 9),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Svensk-amerikanska handelskammaren', 'Marknadsföring och försäljningsutveckling', 'Juni 2021', 'Sep 2021',
         'Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event. Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring. Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA. Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.',
         ARRAY['office', 'customerservice'], 10),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'Handledare för examensprojekt', 'Sep 2020', 'Maj 2021',
         'Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner. Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd. Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.',
         ARRAY['office', 'art'], 11),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kvarngården äldreboende', 'Timvikarie', 'Maj 2020', 'Sep 2020',
         'Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd. Gav omsorg till äldre personer med demens och Alzheimers sjukdom. Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.',
         ARRAY['healthcare'], 12),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva Project', 'Marknadsföring/Kundservice - Global Marketing Team', 'Sep 2019', 'April 2020',
         'Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University. Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice. Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten. Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.',
         ARRAY['customerservice', 'office'], 13),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Google Ads (via Vaco)', 'Svensk innehållsanalytiker för gTech', 'Maj 2018', 'April 2019',
         'Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk. Utförde extraktion och granskning av innehåll för över 100 annonser per dag. Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering. Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet.',
         ARRAY['tech', 'content'], 14),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'Sep 2017', 'Maj 2018',
         'Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka. Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring. Organiserade stadsskattjakt där studenter upptäckte San Francisco. Koordinerade gästföreläsare och använde mjukvara för eventlogistik.',
         ARRAY['office', 'customerservice'], 15),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Wallby Säteri', 'Gårdsvärd/Receptionist', 'Juni 2016', 'Aug 2016',
         'Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar. Assisterade vid caféet och bidrog till allmän service.',
         ARRAY['reception', 'customerservice'], 16),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och grönt', '2015', '2019',
         'Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen. ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.',
         ARRAY['retail'], 17),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Coffeehouse by George', 'Cafépersonal', '2014', '2015',
         'Kassahantering och barista. Hög servicenivå i centralt läge.',
         ARRAY['restaurant'], 18),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Siggesta Gård', 'Gårdsvärd/Trädgårdsarbetare', '2014', '2015',
         'Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell). Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag. Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.',
         ARRAY['industry', 'reception'], 19);
    -- Education (2 total)
    INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date)
    VALUES
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'B.S in Social Science, Economics and Business Administration', 'Business, Arts & Humanities', 'San Francisco, USA', 'Aug 2017', 'Maj 2021'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', 'International Baccalaureate', 'Flekke, Norge', 'Aug 2015', 'Maj 2017');
    -- Skills (37 total)
    INSERT INTO public.user_skills (user_id, category, skill_type, skill_text)
    VALUES
        -- General
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'soft', 'Kundservice'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'soft', 'Kommunikation'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'soft', 'Teamwork'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'soft', 'Stresshantering'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Svenska (Modersmål)'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Engelska (Flytande)'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Tyska (grundläggande)'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Spanska (grundläggande)'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Mandarin (HSK nivå 3)'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'certificate', 'B-körkort'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'certificate', 'ICA kassahantering'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'certificate', 'Trygga mat'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'certificate', 'Röda Korset första hjälpen'),
        -- Restaurant
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'technical', 'Kassasystem'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'technical', 'Barista'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'technical', 'Servering'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'certificate', 'Livsmedelshygien'),
        -- Tech/Content
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Content Moderation'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Trust & Safety'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Policy Compliance'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Data Analysis'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Python'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'SQL'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Tableau'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Google Analytics'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Google Ads'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Facebook Ads'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Adobe Creative Suite'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Content SEO'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Excel/Google Sheets'),
        -- Customer service
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'technical', 'Intercom'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'technical', 'Zendesk'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'technical', 'CRM-system'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'soft', 'Problemlösning'),
        -- Retail
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'technical', 'Kassasystem'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'technical', 'Lagerhantering'),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'technical', 'Merförsäljning');
    -- Volunteer (4 total)
    INSERT INTO public.user_volunteer (user_id, organization, dates, bullets, sort_order)
    VALUES
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'LEAF (Living Environment and Future)', '2016 - 2017',
         ARRAY['Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer', 'Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr'], 1),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'The Right Solution Project', 'Mars 2013 - April 2015',
         ARRAY['Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder', 'Samlade in över 120,000 kr genom evenemang och försäljning', 'Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger'], 2),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'India Unlimited Utbytesprogram', 'Nov 2014 - Feb 2015',
         ARRAY['Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien', 'Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer'], 3),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'Värmdö Församling', '2012 - 2014',
         ARRAY['Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen', 'Svenska Kyrkan: Ledarskapskurs steg 1 och 2'], 4);
    -- Awards (7 total)
    INSERT INTO public.user_awards (user_id, award_text, sort_order)
    VALUES
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, '1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad Publikens Favorit', 1),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, '1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning', 2),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, '1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign', 3),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars)', 4),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016', 5),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar)', 6),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'Minerva University Award for Initiative 2018', 7);
    -- Cover letter preferences
    INSERT INTO public.user_cover_letter_preferences (
        user_id, tone, max_words, greeting_style, signature_style,
        always_mention, never_mention
    )
    VALUES (
        'da8ed517-3b67-4456-8831-6ed3cb7114ad',
        'professional',
        200,
        'Hej!',
        'Med vänliga hälsningar',
        ARRAY['flexibel med tider', 'körkort', 'flytande engelska'],
        ARRAY['konst', 'målning', 'utställningar', 'Shopify', 'e-handel', 'oljemålning', 'linneamoritz.com']
    );
    -- Job preferences
    INSERT INTO public.user_job_preferences (
        user_id, search_keywords, locations, excluded_companies
    )
    VALUES (
        'da8ed517-3b67-4456-8831-6ed3cb7114ad',
        ARRAY['servitör', 'kundtjänst', 'content moderator', 'butik', 'café', 'reception', 'lager'],
        ARRAY['Stockholm', 'Sollentuna', 'Sundbyberg', 'Vetlanda'],
        ARRAY[]::text[]
    );
    -- CV Branscher (8 total)
    INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, focus, keywords, is_active, sort_order)
    VALUES
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'restaurant', 'Restaurang & Café', 'Service, tempo, kundkontakt',
         ARRAY['servitör', 'servitris', 'restaurang', 'café', 'barista', 'kök'], true, 1),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'retail', 'Butik & Kassa', 'Försäljning, kassa, kundservice',
         ARRAY['butik', 'kassa', 'säljare', 'ica', 'coop'], true, 2),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'customerservice', 'Kundtjänst & Support', 'Kommunikation, problemlösning, internationell erfarenhet',
         ARRAY['kundtjänst', 'support', 'kundservice', 'helpdesk'], true, 3),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'content', 'Content & Moderation', 'Trust & Safety, policy, granskning',
         ARRAY['moderator', 'content', 'review', 'granskning', 'trust'], true, 4),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'tech', 'Tech & Kontor', 'Analytiskt arbete, data, tech-bolag',
         ARRAY['tech', 'IT', 'data', 'analyst', 'kontor'], true, 5),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'industry', 'Industri & Trädgård', 'Fysiskt arbete, skift, materialhantering',
         ARRAY['industri', 'lager', 'produktion', 'operatör', 'trädgård'], true, 6),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'healthcare', 'Vård & Omsorg', 'Omvårdnad, empati, medicinhantering',
         ARRAY['vård', 'omsorg', 'äldre', 'sjukvård'], true, 7),
        ('da8ed517-3b67-4456-8831-6ed3cb7114ad'::text, 'art', 'Konst & Kultur', 'Konstnärligt arbete, utställningar, projektledning',
         ARRAY['konst', 'kultur', 'galleri', 'museum', 'kreativ'], true, 8);
END $$;
-- ============================================
-- STEP 3: Verification - Show counts
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
