-- ============================================================================
-- COMPLETE DATA MIGRATION FOR LINNEA MORITZ
-- user_id (UUID): da8ed517-3b67-4456-8831-6ed3cb7114ad
-- user_id (TEXT): 'da8ed517-3b67-4456-8831-6ed3cb7114ad'
--
-- This migrates ALL data from v2/api/index.py to Supabase
-- Run in Supabase SQL Editor
-- ============================================================================

DO $$
DECLARE
    v_user_uuid UUID := 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
    v_user_text TEXT := 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
BEGIN
    RAISE NOTICE 'Starting migration for user: %', v_user_uuid;

    -- ========================================================================
    -- STEP 1: DELETE EXISTING DATA (for clean migration)
    -- ========================================================================

    -- UUID tables
    DELETE FROM user_experiences WHERE user_id = v_user_uuid;
    DELETE FROM user_education WHERE user_id = v_user_uuid;
    DELETE FROM user_skills WHERE user_id = v_user_uuid;
    DELETE FROM user_cvs WHERE user_id = v_user_uuid;

    -- TEXT tables
    DELETE FROM user_awards WHERE user_id = v_user_text;
    DELETE FROM user_volunteer WHERE user_id = v_user_text;
    DELETE FROM user_cv_branscher WHERE user_id = v_user_text;

    RAISE NOTICE '✓ Deleted old data';

    -- ========================================================================
    -- STEP 2: INSERT EXPERIENCES (19 total)
    -- ========================================================================

    INSERT INTO user_experiences (user_id, company, title, location, start_date, end_date, description, categories, sort_order)
    VALUES
        (v_user_uuid, 'Minerva University', 'Alumni Ambassador Western Europe', 'Stockholm', 'Sep 2024', NULL, '25% tjänst med självständig planering, cirka 40 timmar i månaden. Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden. Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare. Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.', ARRAY['office', 'customerservice'], 1),
        (v_user_uuid, 'House of Beans, Hötorgshallen', 'Försäljare/Barista', 'Stockholm', 'Aug 2024', 'Feb 2025', 'Självständigt butiksansvar med försäljning av te, kaffe och choklad. Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar. Hanterade kassa, kundservice och lagerhantering.', ARRAY['restaurant', 'retail'], 2),
        (v_user_uuid, 'Profilgruppen', 'Anodiseringsoperatör (Feriearbete)', 'Åseda', 'Juli 2024', 'Aug 2024', 'Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering. Arbetade på tvåskift (06.00-14.00 och 14.00-23.00). Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor.', ARRAY['industry'], 3),
        (v_user_uuid, 'Max Hamburgare', 'Restaurangbiträde', 'Vetlanda', 'April 2024', 'Aug 2024', 'Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ. Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.', ARRAY['restaurant'], 4),
        (v_user_uuid, 'Keeping Tabs', 'Multimedia Technical Specialist', 'New York, USA', 'Nov 2022', 'Juni 2023', 'Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay). Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj. Utvecklade partnerskap med organisationer inom konstindustrin i USA. Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.', ARRAY['art', 'office'], 5),
        (v_user_uuid, '30 Campos Eliseos', 'Kubistisk målare', 'New York, USA', '2022', '2024', 'Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens. En av endast fem konstnärer utvalda bland 500+ sökande. Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.', ARRAY['art'], 6),
        (v_user_uuid, 'TikTok/ByteDance', 'Kvalitetsgranskare - Amerikanska marknaden', 'Nashville, USA', 'Maj 2022', 'Juni 2022', 'Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer. Kvalitetssäkrade moderering och bidrog till förbättrade processer.', ARRAY['tech', 'content'], 7),
        (v_user_uuid, 'YouTube Ads (via Vaco)', 'Innehållsmoderator - Svenska marknaden', 'San Francisco, USA', 'Feb 2022', 'Juni 2022', 'Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll. Följde noggrant alla riktlinjer och samarbetade med det svenska teamet. Deltog i regelbundna möten för att säkerställa korrekt granskning av material.', ARRAY['tech', 'content'], 8),
        (v_user_uuid, 'Clubhouse (via Vaco)', 'Innehållsmoderator - Skandinaviska och amerikanska marknaden', 'Walnut Creek, USA', 'Juni 2021', 'Jan 2022', 'Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media. Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information. Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden. Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar. Ökade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmål uppfylldes.', ARRAY['tech', 'customerservice', 'content'], 9),
        (v_user_uuid, 'Svensk-amerikanska handelskammaren', 'Marknadsföring och försäljningsutveckling', 'San Francisco, USA', 'Juni 2021', 'Sep 2021', 'Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event. Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring. Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA. Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.', ARRAY['office', 'customerservice'], 10),
        (v_user_uuid, 'Minerva University', 'Handledare för examensprojekt', 'San Francisco, USA', 'Sep 2020', 'Maj 2021', 'Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner. Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd. Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.', ARRAY['office', 'art'], 11),
        (v_user_uuid, 'Kvarngården äldreboende', 'Timvikarie', 'Vetlanda', 'Maj 2020', 'Sep 2020', 'Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd. Gav omsorg till äldre personer med demens och Alzheimers sjukdom. Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.', ARRAY['healthcare'], 12),
        (v_user_uuid, 'Minerva Project', 'Marknadsföring/Kundservice - Global Marketing Team', 'Berlin & Buenos Aires', 'Sep 2019', 'April 2020', 'Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University. Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice. Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten. Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.', ARRAY['customerservice', 'office'], 13),
        (v_user_uuid, 'Google Ads (via Vaco)', 'Svensk innehållsanalytiker för gTech', 'Sunnyvale, USA / Seoul / Hyderabad', 'Maj 2018', 'April 2019', 'Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk. Utförde extraktion och granskning av innehåll för över 100 annonser per dag. Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering. Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet.', ARRAY['tech', 'content'], 14),
        (v_user_uuid, 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'San Francisco, USA', 'Sep 2017', 'Maj 2018', 'Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka. Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring. Organiserade stadsskattjakt där studenter upptäckte San Francisco. Koordinerade gästföreläsare och använde mjukvara för eventlogistik.', ARRAY['office', 'customerservice'], 15),
        (v_user_uuid, 'Wallby Säteri', 'Gårdsvärd/Receptionist', 'Vetlanda', 'Juni 2016', 'Aug 2016', 'Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar. Assisterade vid caféet och bidrog till allmän service.', ARRAY['reception', 'customerservice'], 16),
        (v_user_uuid, 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och grönt', 'Vetlanda & Värmdö', '2015, 2017, 2019', NULL, 'Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen. ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.', ARRAY['retail'], 17),
        (v_user_uuid, 'Coffeehouse by George', 'Cafépersonal', 'Stockholm', '2014', '2015', 'Kassahantering och barista. Hög servicenivå i centralt läge.', ARRAY['restaurant'], 18),
        (v_user_uuid, 'Siggesta Gård', 'Gårdsvärd/Trädgårdsarbetare', 'Värmdö', '2014', '2015', 'Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell). Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag. Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.', ARRAY['industry', 'reception'], 19);

    RAISE NOTICE '✓ Inserted 19 experiences';

    -- ========================================================================
    -- STEP 3: INSERT EDUCATION (2 total)
    -- ========================================================================

    INSERT INTO user_education (user_id, school, degree, field_of_study, location, start_date, end_date, sort_order)
    VALUES
        (v_user_uuid, 'Minerva University', 'B.S in Social Science, Economics and Business Administration', NULL, 'San Francisco, USA', 'Aug 2017', 'Maj 2021', 1),
        (v_user_uuid, 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', NULL, 'Flekke, Norge', 'Aug 2015', 'Maj 2017', 2);

    RAISE NOTICE '✓ Inserted 2 education entries';

    -- ========================================================================
    -- STEP 4: INSERT SKILLS (37 total)
    -- ========================================================================

    INSERT INTO user_skills (user_id, category, skill_type, skill_text)
    VALUES
        -- General (13)
        (v_user_uuid, 'all', 'soft', 'Kundservice'),
        (v_user_uuid, 'all', 'soft', 'Kommunikation'),
        (v_user_uuid, 'all', 'soft', 'Teamwork'),
        (v_user_uuid, 'all', 'soft', 'Stresshantering'),
        (v_user_uuid, 'all', 'language', 'Svenska (Modersmål)'),
        (v_user_uuid, 'all', 'language', 'Engelska (Flytande)'),
        (v_user_uuid, 'all', 'language', 'Tyska (grundläggande)'),
        (v_user_uuid, 'all', 'language', 'Spanska (grundläggande)'),
        (v_user_uuid, 'all', 'language', 'Mandarin (HSK nivå 3)'),
        (v_user_uuid, 'all', 'certificate', 'B-körkort'),
        (v_user_uuid, 'all', 'certificate', 'ICA kassahantering'),
        (v_user_uuid, 'all', 'certificate', 'Trygga mat'),
        (v_user_uuid, 'all', 'certificate', 'Röda Korset första hjälpen'),
        -- Restaurant (4)
        (v_user_uuid, 'restaurant', 'technical', 'Kassasystem'),
        (v_user_uuid, 'restaurant', 'technical', 'Barista'),
        (v_user_uuid, 'restaurant', 'technical', 'Servering'),
        (v_user_uuid, 'restaurant', 'certificate', 'Livsmedelshygien'),
        -- Tech/Content (13)
        (v_user_uuid, 'tech', 'technical', 'Content Moderation'),
        (v_user_uuid, 'tech', 'technical', 'Trust & Safety'),
        (v_user_uuid, 'tech', 'technical', 'Policy Compliance'),
        (v_user_uuid, 'tech', 'technical', 'Data Analysis'),
        (v_user_uuid, 'tech', 'technical', 'Python'),
        (v_user_uuid, 'tech', 'technical', 'SQL'),
        (v_user_uuid, 'tech', 'technical', 'Tableau'),
        (v_user_uuid, 'tech', 'technical', 'Google Analytics'),
        (v_user_uuid, 'tech', 'technical', 'Google Ads'),
        (v_user_uuid, 'tech', 'technical', 'Facebook Ads'),
        (v_user_uuid, 'tech', 'technical', 'Adobe Creative Suite'),
        (v_user_uuid, 'tech', 'technical', 'Content SEO'),
        (v_user_uuid, 'tech', 'technical', 'Excel/Google Sheets'),
        -- Customer service (4)
        (v_user_uuid, 'customerservice', 'technical', 'Intercom'),
        (v_user_uuid, 'customerservice', 'technical', 'Zendesk'),
        (v_user_uuid, 'customerservice', 'technical', 'CRM-system'),
        (v_user_uuid, 'customerservice', 'soft', 'Problemlösning'),
        -- Retail (3)
        (v_user_uuid, 'retail', 'technical', 'Kassasystem'),
        (v_user_uuid, 'retail', 'technical', 'Lagerhantering'),
        (v_user_uuid, 'retail', 'technical', 'Merförsäljning');

    RAISE NOTICE '✓ Inserted 37 skills';

    -- ========================================================================
    -- STEP 5: INSERT AWARDS (7 total) - user_id is TEXT
    -- ========================================================================

    INSERT INTO user_awards (user_id, award_text, sort_order)
    VALUES
        (v_user_text, '1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad Publikens Favorit', 1),
        (v_user_text, '1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick soloutställning', 2),
        (v_user_text, '1:a pris Murrays Creative Contest 2022 - Detroit-baserad tävling med specialdesign', 3),
        (v_user_text, 'Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars)', 4),
        (v_user_text, 'Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016', 5),
        (v_user_text, 'Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar)', 6),
        (v_user_text, 'Minerva University Award for Initiative 2018', 7);

    RAISE NOTICE '✓ Inserted 7 awards';

    -- ========================================================================
    -- STEP 6: INSERT VOLUNTEER (4 total) - user_id is TEXT
    -- ========================================================================

    INSERT INTO user_volunteer (user_id, organization, dates, bullets, sort_order)
    VALUES
        (v_user_text, 'LEAF (Living Environment and Future)', '2016 - 2017', ARRAY['Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer', 'Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr'], 1),
        (v_user_text, 'The Right Solution Project', 'Mars 2013 - April 2015', ARRAY['Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder', 'Samlade in över 120,000 kr genom evenemang och försäljning', 'Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger'], 2),
        (v_user_text, 'India Unlimited Utbytesprogram', 'Nov 2014 - Feb 2015', ARRAY['Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien', 'Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer'], 3),
        (v_user_text, 'Värmdö Församling', '2012 - 2014', ARRAY['Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen', 'Svenska Kyrkan: Ledarskapskurs steg 1 och 2'], 4);

    RAISE NOTICE '✓ Inserted 4 volunteer entries';

    -- ========================================================================
    -- STEP 7: INSERT CV BRANSCHER (8 total) - user_id is TEXT
    -- ========================================================================

    INSERT INTO user_cv_branscher (user_id, bransch_id, bransch_name, focus, keywords, is_active, sort_order)
    VALUES
        (v_user_text, 'restaurant', 'Restaurang & Cafe', 'Service, tempo, kundkontakt', ARRAY['servitör', 'servitris', 'restaurang', 'cafe', 'barista', 'kök'], TRUE, 1),
        (v_user_text, 'retail', 'Butik & Kassa', 'Försäljning, kassa, kundservice', ARRAY['butik', 'kassa', 'säljare', 'ica', 'coop'], TRUE, 2),
        (v_user_text, 'customerservice', 'Kundtjänst & Support', 'Kommunikation, problemlösning, internationell erfarenhet', ARRAY['kundtjänst', 'support', 'kundservice', 'helpdesk'], TRUE, 3),
        (v_user_text, 'content', 'Content & Moderation', 'Trust & Safety, policy, granskning', ARRAY['moderator', 'content', 'review', 'granskning', 'trust'], TRUE, 4),
        (v_user_text, 'tech', 'Tech & Kontor', 'Analytiskt arbete, data, tech-bolag', ARRAY['tech', 'IT', 'data', 'analyst', 'kontor'], TRUE, 5),
        (v_user_text, 'industry', 'Industri & Trädgård', 'Fysiskt arbete, skift, materialhantering', ARRAY['industri', 'lager', 'produktion', 'operatör', 'trädgård'], TRUE, 6),
        (v_user_text, 'healthcare', 'Vård & Omsorg', 'Omvårdnad, empati, medicinhantering', ARRAY['vård', 'omsorg', 'äldre', 'sjukvård'], TRUE, 7),
        (v_user_text, 'art', 'Konst & Kultur', 'Konstnärligt arbete, utställningar, projektledning', ARRAY['konst', 'kultur', 'galleri', 'museum', 'kreativ'], TRUE, 8);

    RAISE NOTICE '✓ Inserted 8 CV branscher';

    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ MIGRATION COMPLETE!';
    RAISE NOTICE '  - Experiences: 19';
    RAISE NOTICE '  - Education: 2';
    RAISE NOTICE '  - Skills: 37';
    RAISE NOTICE '  - Awards: 7';
    RAISE NOTICE '  - Volunteer: 4';
    RAISE NOTICE '  - CV Branscher: 8';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'NOTE: CVs (8 full texts) are NOT included in this migration.';
    RAISE NOTICE 'They are too large. Run separate CV migration if needed.';

END $$;
