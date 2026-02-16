-- ============================================
-- MIGRATION PART 1: Structured Data + 4 CVs
-- (Restaurant, Retail, Customer Service, Content Moderation)
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
-- STEP 2: Insert Profile
-- ============================================
INSERT INTO public.user_profiles (
    user_id,
    full_name,
    email,
    phone,
    location,
    drivers_license,
    languages
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Linnea Moritz',
    'linneamoritzcv@gmail.com',
    '0761166109',
    'Sollentuna',
    TRUE,
    ARRAY['Svenska (Modersmål)', 'Engelska (flytande)', 'Tyska (grundläggande)', 'Spanska (grundläggande)', 'Mandarin (HSK nivå 3)']
);

-- ============================================
-- STEP 3: Insert Education
-- ============================================
INSERT INTO public.user_education (user_id, institution, degree, field_of_study, start_date, end_date, description, location, gpa) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'B.S', 'Social Science, Economics and Business Administration', '2017-08-01', '2021-05-31',
'● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.',
'San Francisco, USA', '3.6'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma', 'Engelska och Svenska', '2015-08-01', '2017-05-31',
'● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).',
'Flekke, Norge', '3.85');

-- ============================================
-- STEP 4: Insert Work Experiences
-- ============================================
INSERT INTO public.user_experiences (user_id, company, title, location, start_date, end_date, description, employment_type) VALUES

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'Alumni Ambassador Western Europe', 'Stockholm', '2024-09-01', NULL,
'● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Linnea Moritz (linneamoritz.com)', 'Konstnär och Egenföretagare', 'Stockholm', '2024-01-01', NULL,
'● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.', 'self_employed'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'House of Beans, Hötorgshallen', 'Försäljare/Barista', 'Stockholm', '2024-08-01', '2025-02-28',
'● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.', 'full_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Max Hamburgare', 'Restaurangbiträde', 'Vetlanda', '2024-04-01', '2024-08-31',
'● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.', 'full_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Profilgruppen', 'Anodiseringsoperatör', 'Åseda', '2024-07-01', '2024-08-31',
'● Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering.
● Arbetade på tvåskift (06.00-14.00 och 14.00-23.00), vilket visade flexibilitet.
● Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor.', 'temporary'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kvarngården äldreboende', 'Timvikarie', 'Vetlanda', '2020-05-01', '2020-09-30',
'● Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd.
● Gav omsorg till äldre personer med demens och Alzheimers sjukdom.
● Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.', 'temporary'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och grönt', 'Vetlanda & Värmdö', '2015-06-01', '2019-08-31',
'● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Vetlanda Kommun, Ekenässjöns skola', 'Köksbiträde', 'Vetlanda', '2017-07-01', '2017-08-31',
'● Assisterade vid matlagning och serverade mat till elever och personal.', 'temporary'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Wallby Säteri', 'Gårdsvärd/Receptionist', 'Vetlanda', '2016-06-01', '2016-08-31',
'● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.', 'temporary'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Siggesta Gård', 'Gårdsvärd/Trädgårdsarbetare', 'Värmdö', '2014-06-01', '2015-08-31',
'● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Coffeehouse by George', 'Cafépersonal', 'Nacka', '2014-06-01', '2015-05-31',
'● Kassahantering, kundbemötande, barista, matberedning och servering.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Keeping Tabs', 'Multimedia Technical Specialist', 'New York, USA', '2022-11-01', '2023-06-30',
'● Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay).
● Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj.
● Utvecklade partnerskap med organisationer inom konstindustrin i USA.
● Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.', 'full_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', '30 Campos Eliseos', 'Kubistisk målare', 'New York, USA', '2022-01-01', '2024-12-31',
'● Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens.
● En av endast fem konstnärer utvalda bland 500+ sökande.
● Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.', 'contract'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'Handledare för examensprojekt', 'San Francisco, USA', '2020-09-01', '2021-05-31',
'● Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner.
● Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd.
● Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva Project', 'Marknadsföring/Kundservice - Global Marketing Team', 'Berlin & Buenos Aires', '2019-09-01', '2020-04-30',
'● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.', 'part_time'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'San Francisco, USA', '2017-09-01', '2018-05-31',
'● Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka.
● Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring.
● Organiserade stadsskattjakt där studenter upptäckte San Francisco och utvidgade kontaktnät.
● Koordinerade gästföreläsare och använde mjukvara för eventlogistik och närvarohantering.', 'part_time');

-- ============================================
-- STEP 5: Insert Skills
-- ============================================
INSERT INTO public.user_skills (user_id, skill_name, category) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kundservice', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Teamwork', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kommunikation', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Problemlösning', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Självständighet', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Flexibilitet', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Ledarskap', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Projektledning', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tidsstyrning', 'soft_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kassahantering', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Barista', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Matberedning', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Lagerhantering', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Restaurangarbete', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Omvårdnad', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Medicinhantering', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Evenemangsplanering', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Marknadsföring', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Försäljning', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Python', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'SQL', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tableau', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Google Analytics', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Google Ads', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Facebook Ads', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Adobe Creative Suite', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Intercom', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'CRM-system', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Canva', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Content SEO', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Shopify', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Excel/Google Sheets', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Databaser', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Bokföring', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Trädgårdsarbete', 'technical_skills'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Fysiskt arbete', 'technical_skills');

-- ============================================
-- STEP 6: Insert Awards
-- ============================================
INSERT INTO public.user_awards (user_id, award_name, issuer, date_received, description) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Stockholms Konstsalong 2024', 'Stockholms Konstsalong', '2024-01-01', 'Jurybedömd utställning, nominerad ''Publikens Favorit''.'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Greenpoint Gallery Brooklyn 2023', 'Greenpoint Gallery', '2023-01-01', 'Vann bland 60 konstnärer, fick solouställning.'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Murray''s Creative Contest 2022', 'Murray''s', '2022-01-01', 'Detroit-baserad tävling med specialdesign.'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Global Startup Weekend Stockholm', 'Google for Startups & Techstars', '2020-01-01', 'Vinnare för Terra Finance.'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tredje pris Chinese Bridge', 'Chinese Bridge', '2016-01-01', 'Nationell tävling i kinesiskt språk, Bergen 2016.'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Röda Korsets diplom', 'Röda Korset', '2017-05-01', 'Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University Award for Initiative', 'Minerva University', '2018-05-01', 'Award for Initiative 2018.');

-- ============================================
-- STEP 7: Insert Volunteer Work
-- ============================================
INSERT INTO public.user_volunteer (user_id, organization, role, start_date, end_date, description) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'LEAF (Living Environment and Future)', 'Ledare', '2016-01-01', '2017-12-31',
'● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'The Right Solution Project', 'Grundare och projektledare', '2013-03-01', '2015-04-30',
'● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'India Unlimited Utbytesprogram', 'Deltagare', '2014-11-01', '2015-02-28',
'● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.'),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Värmdö Församling', 'Konfirmandledare', '2012-01-01', '2014-12-31',
'● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.');

-- ============================================
-- STEP 8: Insert Cover Letter Preferences
-- ============================================
INSERT INTO public.user_cover_letter_preferences (
    user_id,
    tone,
    length,
    focus_areas,
    avoid_topics
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'professional',
    'medium',
    ARRAY['kundservice', 'teamwork', 'självständighet', 'problemlösning', 'flexibilitet'],
    ARRAY['konst', 'målning', 'utställningar', 'shopify']
);

-- ============================================
-- STEP 9: Insert Job Preferences
-- ============================================
INSERT INTO public.user_job_preferences (
    user_id,
    preferred_industries,
    preferred_roles,
    preferred_locations,
    min_salary,
    employment_types,
    remote_preference
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    ARRAY['restaurang', 'butik', 'vård', 'kundservice', 'kontor', 'reception'],
    ARRAY['kundservice', 'försäljning', 'barista', 'kassapersonal', 'receptionist', 'omvårdnad'],
    ARRAY['Stockholm', 'Sollentuna', 'Värmdö'],
    25000,
    ARRAY['full_time', 'part_time'],
    'hybrid'
);

-- ============================================
-- STEP 10: Insert CV Branscher Mapping
-- ============================================
INSERT INTO public.user_cv_branscher (user_id, bransch, cv_file_name) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'CV_Linnea_Moritz_Restaurang_Cafe.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'CV_Linnea_Moritz_Butik_Kassa.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'CV_Linnea_Moritz_Kundtjanst.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'contentmoderation', 'CV_Linnea_Moritz_Content_Moderation.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'healthcare', 'CV_Linnea_Moritz_Vard_Omsorg.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'CV_Linnea_Moritz_Tech_Kontor.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'industry', 'CV_Linnea_Moritz_Industri_Tradgard.pdf'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'art', 'CV_Linnea_Moritz_Konst_Kultur.pdf');

-- ============================================
-- STEP 11: Insert 4 COMPLETE CVs
-- ============================================

-- CV 1: RESTAURANT/CAFÉ
INSERT INTO public.user_cvs (user_id, cv_name, cv_content, bransch, created_at) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad',
'CV_Restaurang_Cafe',
'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University                                                                San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6)          Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic                                            Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University                                                               Stockholm
Alumni Ambassador Western Europe                                                 Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com)                                                 Stockholm
Konstnär och Egenföretagare                                                      Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen                                                    Stockholm
Försäljare/Barista                                                               Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare                                                                   Vetlanda
Restaurangbiträde                                                                April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad                                                             Vetlanda & Värmdö
Kassapersonal, frukt och grönt                                                   2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Vetlanda Kommun, Ekenässjöns skola                                               Vetlanda
Köksbiträde                                                                      Juli – Aug 2017
● Assisterade vid matlagning och serverade mat till elever och personal.

Wallby Säteri                                                                    Vetlanda
Gårdsvärd/Receptionist                                                           Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Coffeehouse by George                                                            Nacka
Cafépersonal                                                                     2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER

Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future)                                             2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project                                                       Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram                                                   Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling                                                                2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER

● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.',
'restaurant',
NOW()
);

-- CV 2: RETAIL (BUTIK/KASSA)
INSERT INTO public.user_cvs (user_id, cv_name, cv_content, bransch, created_at) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad',
'CV_Butik_Kassa',
'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University                                                                San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6)          Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic                                            Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University                                                               Stockholm
Alumni Ambassador Western Europe                                                 Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com)                                                 Stockholm
Konstnär och Egenföretagare                                                      Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen                                                    Stockholm
Försäljare/Barista                                                               Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare                                                                   Vetlanda
Restaurangbiträde                                                                April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad                                                             Vetlanda & Värmdö
Kassapersonal, frukt och grönt                                                   2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Vetlanda Kommun, Ekenässjöns skola                                               Vetlanda
Köksbiträde                                                                      Juli – Aug 2017
● Assisterade vid matlagning och serverade mat till elever och personal.

Wallby Säteri                                                                    Vetlanda
Gårdsvärd/Receptionist                                                           Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Coffeehouse by George                                                            Nacka
Cafépersonal                                                                     2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER

Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future)                                             2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project                                                       Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram                                                   Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling                                                                2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER

● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.',
'retail',
NOW()
);

-- CV 3: CUSTOMER SERVICE (KUNDTJÄNST)
INSERT INTO public.user_cvs (user_id, cv_name, cv_content, bransch, created_at) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad',
'CV_Kundtjanst',
'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University                                                                San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6)          Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic                                            Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University                                                               Stockholm
Alumni Ambassador Western Europe                                                 Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com)                                                 Stockholm
Konstnär och Egenföretagare                                                      Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen                                                    Stockholm
Försäljare/Barista                                                               Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare                                                                   Vetlanda
Restaurangbiträde                                                                April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Minerva Project                                                                  Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team                              Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

ICA Maxi Stormarknad                                                             Vetlanda & Värmdö
Kassapersonal, frukt och grönt                                                   2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri                                                                    Vetlanda
Gårdsvärd/Receptionist                                                           Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård                                                                    Värmdö
Gårdsvärd/Trädgårdsarbetare                                                      2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER

Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future)                                             2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project                                                       Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram                                                   Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling                                                                2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER

● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.',
'customerservice',
NOW()
);

-- CV 4: CONTENT MODERATION
INSERT INTO public.user_cvs (user_id, cv_name, cv_content, bransch, created_at) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad',
'CV_Content_Moderation',
'Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University                                                                San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6)          Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World''s Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic                                            Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University                                                               Stockholm
Alumni Ambassador Western Europe                                                 Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com)                                                 Stockholm
Konstnär och Egenföretagare                                                      Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen                                                    Stockholm
Försäljare/Barista                                                               Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare                                                                   Vetlanda
Restaurangbiträde                                                                April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Minerva Project                                                                  Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team                              Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

ICA Maxi Stormarknad                                                             Vetlanda & Värmdö
Kassapersonal, frukt och grönt                                                   2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri                                                                    Vetlanda
Gårdsvärd/Receptionist                                                           Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård                                                                    Värmdö
Gårdsvärd/Trädgårdsarbetare                                                      2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER

Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future)                                             2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project                                                       Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram                                                   Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling                                                                2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER

● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018.',
'contentmoderation',
NOW()
);
