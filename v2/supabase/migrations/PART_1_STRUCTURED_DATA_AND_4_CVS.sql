-- ============================================
-- MIGRATION PART 1: Structured Data + 4 CVs
-- (Restaurant, Retail, Customer Service, Content Moderation)
-- ============================================

-- ============================================
-- STEP 1: Delete all old data
-- ============================================
DELETE FROM public.user_experiences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_education WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_skills WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_cvs WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_volunteer WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_awards WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_cover_letter_preferences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_job_preferences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;
DELETE FROM public.user_cv_branscher WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';
DELETE FROM public.user_profiles WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid;

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
    'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
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
INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Minerva University', 'B.S in Social Science, Economics and Business Administration (GPA: 3.6)', NULL, 'San Francisco, USA', 'Aug 2017', 'Maj 2021'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'United World College Red Cross Nordic', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', NULL, 'Flekke, Norge', 'Aug 2015', 'Maj 2017');

-- ============================================
-- STEP 4: Insert Work Experiences
-- ============================================
INSERT INTO public.user_experiences (user_id, company, title, start_date, end_date, description, categories, sort_order) VALUES

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Minerva University', 'Alumni Ambassador Western Europe', 'Sep 2024', 'Pågående',
'25% tjänst med självständig planering, cirka 40 timmar i månaden. Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden. Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare. Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.', ARRAY['tech', 'customerservice', 'reception'], 1),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Linnea Moritz (linneamoritz.com)', 'Konstnär och Egenföretagare', 'Jan 2024', 'Pågående',
'Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter. Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn). Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt. Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.', ARRAY['art'], 2),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'House of Beans, Hötorgshallen', 'Försäljare/Barista', 'Aug 2024', 'Feb 2025',
'Självständigt butiksansvar med försäljning av te, kaffe och choklad. Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar. Hanterade kassa, kundservice och lagerhantering.', ARRAY['restaurant', 'retail', 'customerservice'], 3),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Max Hamburgare', 'Restaurangbiträde', 'April 2024', 'Aug 2024',
'Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ. Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.', ARRAY['restaurant'], 4),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Profilgruppen', 'Anodiseringsoperatör', 'Juli 2024', 'Aug 2024',
'Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering. Arbetade på tvåskift (06.00-14.00 och 14.00-23.00), vilket visade flexibilitet. Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor.', ARRAY['industry'], 5),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Kvarngården äldreboende', 'Timvikarie', 'Maj 2020', 'Sep 2020',
'Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd. Gav omsorg till äldre personer med demens och Alzheimers sjukdom. Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.', ARRAY['healthcare'], 6),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'ICA Maxi Stormarknad', 'Kassapersonal, frukt och grönt', '2015', '2019',
'Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen. ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.', ARRAY['retail'], 7),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Vetlanda Kommun, Ekenässjöns skola', 'Köksbiträde', 'Juli 2017', 'Aug 2017',
'Assisterade vid matlagning och serverade mat till elever och personal.', ARRAY['restaurant', 'healthcare'], 8),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Wallby Säteri', 'Gårdsvärd/Receptionist', 'Juni 2016', 'Aug 2016',
'Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar. Assisterade vid caféet och bidrog till allmän service.', ARRAY['reception', 'restaurant', 'customerservice'], 9),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Siggesta Gård', 'Gårdsvärd/Trädgårdsarbetare', '2014', '2015',
'Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell). Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag. Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.', ARRAY['industry', 'reception', 'customerservice'], 10),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Coffeehouse by George', 'Cafépersonal', '2014', '2015',
'Kassahantering, kundbemötande, barista, matberedning och servering.', ARRAY['restaurant', 'retail'], 11),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Keeping Tabs', 'Multimedia Technical Specialist', 'Nov 2022', 'Juni 2023',
'Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay). Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj. Utvecklade partnerskap med organisationer inom konstindustrin i USA. Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.', ARRAY['art', 'tech', 'customerservice'], 12),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, '30 Campos Eliseos', 'Kubistisk målare', '2022', '2024',
'Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens. En av endast fem konstnärer utvalda bland 500+ sökande. Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.', ARRAY['art'], 13),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Minerva University', 'Handledare för examensprojekt', 'Sep 2020', 'Maj 2021',
'Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner. Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd. Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.', ARRAY['tech', 'customerservice'], 14),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Minerva Project', 'Marknadsföring/Kundservice - Global Marketing Team', 'Sep 2019', 'April 2020',
'Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University. Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice. Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten. Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.', ARRAY['tech', 'customerservice'], 15),

('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'Minerva Project - Student Experience Team', 'Evenemangskoordinator och elevhemsvärd', 'Sep 2017', 'Maj 2018',
'Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka. Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring. Organiserade stadsskattjakt där studenter upptäckte San Francisco och utvidgade kontaktnät. Koordinerade gästföreläsare och använde mjukvara för eventlogistik och närvarohantering.', ARRAY['tech', 'customerservice', 'reception'], 16);

-- ============================================
-- STEP 5: Insert Skills
-- ============================================
INSERT INTO public.user_skills (user_id, category, skill_type, skill_text) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'language', 'Svenska (Modersmål)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'language', 'Engelska (flytande)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'language', 'Tyska (grundläggande)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'language', 'Spanska (grundläggande)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'language', 'Mandarin (HSK nivå 3)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'certificate', 'B-körkort (automat)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'certificate', 'ICA kassahantering'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'certificate', 'Trygga mat'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'all', 'certificate', 'Röda Korset första hjälpen'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Python'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'SQL'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Tableau'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Google Analytics'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Google Ads'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Facebook Ads'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Adobe Creative Suite'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Intercom'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'CRM-system'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Canva'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Content SEO'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Shopify'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid, 'tech', 'technical', 'Excel/Google Sheets');

-- ============================================
-- STEP 6: Insert Awards
-- ============================================
INSERT INTO public.user_awards (user_id, award_text, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad ''Publikens Favorit''.', 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.', 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Murray''s Creative Contest 2022 - Detroit-baserad tävling med specialdesign.', 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).', 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.', 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).', 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University Award for Initiative 2018.', 7);

-- ============================================
-- STEP 7: Insert Volunteer Work
-- ============================================
INSERT INTO public.user_volunteer (user_id, organization, dates, bullets, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'LEAF (Living Environment and Future)', '2016 - 2017',
ARRAY[
    'Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.',
    'Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.'
], 1),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'The Right Solution Project', 'Mars 2013 – April 2015',
ARRAY[
    'Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.',
    'Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.',
    'Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.'
], 2),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'India Unlimited Utbytesprogram', 'Nov 2014 - Feb 2015',
ARRAY[
    'Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.',
    'Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.'
], 3),

('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Värmdö Församling', '2012 - 2014',
ARRAY[
    'Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.',
    'Svenska Kyrkan: Ledarskapskurs steg 1 och 2.'
], 4);

-- ============================================
-- STEP 8: Insert Cover Letter Preferences
-- ============================================
INSERT INTO public.user_cover_letter_preferences (
    user_id,
    tone,
    max_words,
    greeting_style,
    signature_style,
    always_mention,
    never_mention
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
    'professional_friendly',
    200,
    'Hej!',
    'Med vänliga hälsningar',
    ARRAY['flexibel med tider', 'körkort', 'självständig'],
    ARRAY['konst', 'målning', 'utställningar', 'shopify']
);

-- ============================================
-- STEP 9: Insert Job Preferences
-- ============================================
INSERT INTO public.user_job_preferences (
    user_id,
    search_keywords,
    locations,
    excluded_companies
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
    ARRAY['servitör', 'servitris', 'kundtjänst', 'content moderator', 'barista', 'café', 'receptionist', 'butik', 'kassa', 'trädgård'],
    ARRAY['Stockholm', 'Sollentuna', 'Sundbyberg', 'Solna', 'Vetlanda', 'Nässjö', 'Eksjö', 'Småland', 'Jönköping'],
    ARRAY[]::TEXT[]
);

-- ============================================
-- STEP 10: Insert CV Branscher Mapping
-- ============================================
INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, emoji, keywords, is_active, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'Restaurang & Café', '🍽️', ARRAY['servitör', 'barista', 'kök', 'café']::TEXT[], TRUE, 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'Butik & Kassa', '🛒', ARRAY['kassa', 'butik', 'försäljning']::TEXT[], TRUE, 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'Kundtjänst', '📞', ARRAY['kundtjänst', 'support', 'service']::TEXT[], TRUE, 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'contentmoderation', 'Content Moderation', '🛡️', ARRAY['content moderator', 'trust and safety']::TEXT[], TRUE, 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'healthcare', 'Vård & Omsorg', '🏥', ARRAY['vård', 'omsorg', 'äldreboende']::TEXT[], TRUE, 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'Tech & Kontor', '💻', ARRAY['tech', 'kontor', 'data', 'analyst']::TEXT[], TRUE, 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'industry', 'Industri & Trädgård', '🏭', ARRAY['industri', 'trädgård', 'fysiskt']::TEXT[], TRUE, 7),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'art', 'Konst & Kultur', '🎨', ARRAY['konst', 'kultur', 'utställning']::TEXT[], TRUE, 8);

-- ============================================
-- STEP 11: Insert 4 COMPLETE CVs
-- ============================================

-- CV 1: RESTAURANT/CAFÉ
INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
'restaurant',
'Restaurang & Café',
'🍽️',
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
● Minerva University Award for Initiative 2018.'
);

-- CV 2: RETAIL (BUTIK/KASSA)
INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
'retail',
'Butik & Kassa',
'🛒',
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
● Minerva University Award for Initiative 2018.'
);

-- CV 3: CUSTOMER SERVICE (KUNDTJÄNST)
INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
'customerservice',
'Kundtjänst',
'📞',
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
● Minerva University Award for Initiative 2018.'
);

-- CV 4: CONTENT MODERATION
INSERT INTO public.user_cvs (user_id, vibe_id, vibe_name, vibe_emoji, cv_text) VALUES (
'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid,
'contentmoderation',
'Content Moderation',
'🛡️',
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
● Minerva University Award for Initiative 2018.'
);
