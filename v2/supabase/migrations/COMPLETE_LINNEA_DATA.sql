-- ============================================================================
-- COMPLETE DATA MIGRATION FOR LINNEA MORITZ
-- ============================================================================
-- User ID: da8ed517-3b67-4456-8831-6ed3cb7114ad
--
-- This migration contains ALL profile data:
-- - 1 user profile (UPDATE)
-- - 19 work experiences
-- - 2 education entries
-- - 28 skills
-- - 7 awards
-- - 4 volunteer positions
-- - 8 CV branscher (industry categories)
-- - 1 cover letter preferences entry
--
-- IMPORTANT: This uses INSERT ON CONFLICT DO UPDATE to handle duplicates
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. USER PROFILE
-- ----------------------------------------------------------------------------
-- Update or insert user profile
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
    'linneamoritzCV@gmail.com',
    '+46 XX XXX XX XX',
    'Stockholm, Sverige',
    TRUE,
    ARRAY['Svenska (modersmål)', 'Engelska (flytande)', 'Spanska (god)', 'Franska (grundläggande)']
) ON CONFLICT (user_id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    location = EXCLUDED.location,
    drivers_license = EXCLUDED.drivers_license,
    languages = EXCLUDED.languages;

-- ----------------------------------------------------------------------------
-- 2. WORK EXPERIENCES (19 positions)
-- user_id is UUID type
-- start_date and end_date are TEXT type
-- categories is TEXT[] array
-- ----------------------------------------------------------------------------

-- Delete existing experiences to avoid duplicates, then insert all
DELETE FROM public.user_experiences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_experiences (
    user_id,
    company,
    title,
    start_date,
    end_date,
    description,
    categories,
    sort_order
) VALUES
-- RESTAURANT EXPERIENCE (4 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Morfar Ginko & Pappa Ray',
    'Bartender',
    'Juni 2022',
    'Augusti 2023',
    'Mixology, kundservice, kassamanagement i högtrafikerad cocktailbar. Ansvarade för drinkmeny och personalutbildning. Hanterade stora sällskap och event.',
    ARRAY['restaurant', 'customerservice'],
    1
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'AG',
    'Hovmästare/Bartender',
    'November 2022',
    'Augusti 2023',
    'Blandade drinkar, serverade mat, hanterade bokningar och gästrelationer. Deltidsroll parallellt med Morfar Ginko. Fine dining miljö.',
    ARRAY['restaurant', 'customerservice'],
    2
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Steakhouse',
    'Servitör/Bartender',
    'Juni 2021',
    'Maj 2022',
    'Fine dining service, drinktillverkning, gästrelationer i exklusiv miljö. Vinkunskap och pairing. Hanterade VIP-gäster.',
    ARRAY['restaurant', 'customerservice'],
    3
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Wayne''s Coffee',
    'Restaurangbiträde',
    'September 2019',
    'Augusti 2020',
    'Kaffeservering, kassahantering, kundkontakt i snabbtempomiljö. Barista-arbete, inventering, lokalvård.',
    ARRAY['restaurant', 'customerservice', 'retail'],
    4
),

-- RETAIL EXPERIENCE (3 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Cervera',
    'Butiksbiträde',
    'November 2020',
    'Maj 2021',
    'Försäljning av hushållsprodukter, kundrådgivning, lageradministration. Visual merchandising, kassahantering, kundservice.',
    ARRAY['retail', 'customerservice'],
    5
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Lagerhaus',
    'Säljare',
    'Januari 2020',
    'Oktober 2020',
    'Heminteriör försäljning, visual merchandising, kundmöten. Produktplacering, inventering, aktiv försäljning.',
    ARRAY['retail', 'customerservice'],
    6
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Systembolaget',
    'Butiksbiträde',
    'Juni 2019',
    'Augusti 2019',
    'Vinrådgivning, lageradministration, kassahantering. Sommarjobb med fokus på kundservice och produktkunskap.',
    ARRAY['retail', 'customerservice'],
    7
),

-- INDUSTRY/PRODUCTION EXPERIENCE (2 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Frebaco',
    'Produktionsassistent',
    'September 2023',
    'Februari 2024',
    'Food production, kvalitetskontroll, förpackning. Arbetade i klimatstyrd produktionsmiljö. HACCP-kunskap, hygienrutiner, produktionsmål.',
    ARRAY['industry', 'production'],
    8
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'PostNord',
    'Lagerarbetare',
    'December 2021',
    'Maj 2022',
    'Paketsortering, lageradministration, distribution. Nattskift och helger. Truckkörning, handdator, effektivitetsmål.',
    ARRAY['industry', 'warehouse'],
    9
),

-- HEALTHCARE EXPERIENCE (2 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tiohundra AB',
    'Vårdbiträde',
    'Juni 2018',
    'Maj 2019',
    'Äldreomsorg på demensavdelning, personlig assistans, dokumentation i journalsystem. Omvårdnad, medicinhantering, anhörigkontakt.',
    ARRAY['healthcare', 'care'],
    10
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Olika arbetsgivare',
    'Personlig assistent',
    'Januari 2017',
    'Maj 2018',
    'Stöd till personer med funktionsnedsättning. Flertal uppdragsgivare. Personlig vård, aktivitetsstöd, vardagshjälp, anhörigkontakt.',
    ARRAY['healthcare', 'care'],
    11
),

-- TECH/DIGITAL EXPERIENCE (2 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Majorel (via Manpower)',
    'Content Moderator',
    'Mars 2024',
    'November 2024',
    'Granskning av innehåll för sociala medier enligt community guidelines. Hanterade känsligt material, rapporterade policybrott, arbetade med internationellt team. Högt tempo, noggrannhetskrav.',
    ARRAY['contentmoderation', 'tech', 'digital'],
    12
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Freelance',
    'Junior Webbutvecklare',
    'Januari 2023',
    'December 2023',
    'Byggde webbsidor med HTML, CSS, JavaScript för småföretag. Portfolio-projekt och kundutvecklingsuppdrag. Responsiv design, grundläggande SEO.',
    ARRAY['tech', 'webdev', 'digital'],
    13
),

-- CUSTOMER SERVICE EXPERIENCE (2 positions)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Telenor',
    'Kundtjänstmedarbetare',
    'Juni 2020',
    'November 2020',
    'Telefonkundservice, problemlösning, CRM-system. Hanterade abonnemangsärenden, teknisk support, försäljning. Höga kundnöjdhetsbetyg.',
    ARRAY['customerservice', 'callcenter'],
    14
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'SJ',
    'Kundtjänst',
    'Januari 2019',
    'Maj 2019',
    'Biljettsupport, reseinformation, kundrelationer. Säsongsarbete med fokus på problemlösning och service. Hanterade stressade resenärer.',
    ARRAY['customerservice', 'service'],
    15
),

-- RECEPTION EXPERIENCE (1 position)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Comfort Hotel',
    'Receptionist',
    'September 2018',
    'December 2018',
    'Check-in/check-out, telefonservice, gästrelationer. Kvällsskift och helger. Bokningssystem, fakturering, problemlösning.',
    ARRAY['reception', 'customerservice', 'hospitality'],
    16
),

-- ART/CULTURE EXPERIENCE (2 positions - historical)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Galleri Moment',
    'Galleriassistent',
    'Juni 2016',
    'Juni 2017',
    'Vernissage-koordinering, konstnärskontakter, utställningsplanering. Försäljning av konstverk, kundrelationer, marknadsföring.',
    ARRAY['art', 'culture', 'gallery'],
    17
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Konstakademien',
    'Curator Assistant',
    'Januari 2016',
    'Maj 2016',
    'Utställningskurering, katalogproduktion. Praktikplats under universitetet. Research, textproduktion, konsthistorisk analys.',
    ARRAY['art', 'culture', 'curation'],
    18
),

-- OTHER EXPERIENCE (1 position)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Stockholms Stad',
    'Projektassistent',
    'Juli 2017',
    'December 2017',
    'Administrativt stöd för samhällsprojekt. Tidsbegränsad projekttjänst. Koordinering, dokumentation, mötesanteckningar.',
    ARRAY['admin', 'project'],
    19
);

-- ----------------------------------------------------------------------------
-- 3. EDUCATION (2 entries)
-- user_id is UUID type
-- start_date and end_date are TEXT type
-- ----------------------------------------------------------------------------

-- Delete existing education to avoid duplicates, then insert all
DELETE FROM public.user_education WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_education (
    user_id,
    school,
    degree,
    field_of_study,
    location,
    start_date,
    end_date
) VALUES
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Stockholms Universitet',
    'Kandidatexamen',
    'Konstvetenskap',
    'Stockholm',
    '2013',
    '2016'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Södra Latin',
    'Gymnasieexamen',
    'Estetiska programmet - Konst',
    'Stockholm',
    '2010',
    '2013'
);

-- ----------------------------------------------------------------------------
-- 4. SKILLS (28 skills across categories)
-- user_id is UUID type
-- ----------------------------------------------------------------------------

-- Delete existing skills to avoid duplicates, then insert all
DELETE FROM public.user_skills WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_skills (
    user_id,
    category,
    skill_type,
    skill_text
) VALUES
-- TECHNICAL SKILLS (10 skills)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'code',
    'HTML, CSS, JavaScript'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'code',
    'React (grundläggande)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'code',
    'Python (grundläggande)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'software',
    'Microsoft Office (Word, Excel, PowerPoint)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'software',
    'Google Workspace (Docs, Sheets, Drive)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'software',
    'CRM-system (Zendesk, Salesforce grundläggande)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'software',
    'Kassasystem och POS-terminaler'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'software',
    'Bokningssystem (TheFork, Resy, hotellsystem)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'specialized',
    'Content Moderation & Community Guidelines'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Tekniska',
    'specialized',
    'Social Media Policy Enforcement'
),

-- SOFT SKILLS (10 skills)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'communication',
    'Kundservice (expertis)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'communication',
    'Kommunikation (muntlig och skriftlig)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'problem_solving',
    'Problemlösning'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'problem_solving',
    'Konflikthantering'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'collaboration',
    'Teamwork och samarbete'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'personal',
    'Anpassningsförmåga'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'personal',
    'Multitasking'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'personal',
    'Empati och lyhördhet'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'personal',
    'Noggrannhet och attention to detail'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Mjuka färdigheter',
    'personal',
    'Stresshantering'
),

-- CERTIFICATIONS (4 skills)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Certifieringar',
    'certification',
    'Hygiencompetens (Livsmedelshantering)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Certifieringar',
    'certification',
    'Alkoholservering'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Certifieringar',
    'certification',
    'Första hjälpen (HLR)'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Certifieringar',
    'certification',
    'Truckkort A och B'
),

-- INDUSTRY-SPECIFIC SKILLS (4 skills)
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Branschspecifik',
    'industry',
    'Food Safety & HACCP-kunskap'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Branschspecifik',
    'industry',
    'Inventory Management & Lagerhantering'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Branschspecifik',
    'industry',
    'Visual Merchandising'
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Branschspecifik',
    'industry',
    'Mixology & Bartending'
);

-- ----------------------------------------------------------------------------
-- 5. AWARDS (7 awards)
-- NOTE: user_id is TEXT type in this table (not UUID!)
-- ----------------------------------------------------------------------------

-- Delete existing awards to avoid duplicates, then insert all
DELETE FROM public.user_awards WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_awards (
    user_id,
    award_text,
    sort_order
) VALUES
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Månadens medarbetare - AG Restaurant (Maj 2023) - Utnämnd för utmärkt kundservice och teamwork',
    1
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Employee of the Quarter - Majorel (Q3 2024) - Erkänd för hög noggrannhet i content moderation och teamsamarbete',
    2
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Bästa försäljare - Lagerhaus (Sommaren 2020) - Högst försäljning under sommarmånaderna',
    3
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Teambuilding Award - PostNord (Mars 2022) - För positivt bidrag till teamklimat och arbetsmiljö',
    4
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Customer Service Excellence - Telenor (Oktober 2020) - Högst kundnöjdhetsbetyg under kvartalet',
    5
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Perfect Attendance - Frebaco (December 2023) - Inga sjukdagar under hela anställningsperioden',
    6
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Innovation Prize - Comfort Hotel (November 2018) - För förbättring av check-in-processen och gästupplevelse',
    7
);

-- ----------------------------------------------------------------------------
-- 6. VOLUNTEER WORK (4 positions)
-- NOTE: user_id is TEXT type in this table (not UUID!)
-- ----------------------------------------------------------------------------

-- Delete existing volunteer work to avoid duplicates, then insert all
DELETE FROM public.user_volunteer WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_volunteer (
    user_id,
    organization,
    dates,
    bullets,
    sort_order
) VALUES
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Stockholms Stadsmission',
    '2019-2020',
    ARRAY[
        'Serverade mat till hemlösa och utsatta personer varje vecka',
        'Organiserade julbord och högtidsevenemang för 100+ personer',
        'Deltog i teamet för utdelning av hygienprodukter och kläder',
        'Skapade trygg och välkomnande miljö för besökare'
    ],
    1
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Pride Stockholm',
    'Sommaren 2018',
    ARRAY[
        'Event coordinator under Pride-veckan',
        'Hjälpte till med logistik och besökshantering för stora evenemang',
        'Informationsdisk och gästrelationer',
        'Representerade organisationen med värme och professionalism'
    ],
    2
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Kompisbyråan',
    '2017-2018',
    ARRAY[
        'Mentor för nyanlända till Sverige',
        'Språkstöd och kulturell orientering',
        'Hjälpte med praktiska göromål och myndighetskontakter',
        'Byggde långsiktig, stödjande relation'
    ],
    3
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'Stockholms Katthem',
    '2016',
    ARRAY[
        'Djurvolontär med fokus på kattvård',
        'Hjälpte till med adoptionsarrangemang och visningar',
        'Socialiserade katter för återplacering',
        'Matning, rengöring, och grundläggande djurvård'
    ],
    4
);

-- ----------------------------------------------------------------------------
-- 7. CV BRANSCHER (8 industry categories)
-- NOTE: user_id is TEXT type in this table (not UUID!)
-- ----------------------------------------------------------------------------

-- Delete existing CV branscher to avoid duplicates, then insert all
DELETE FROM public.user_cv_branscher WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_cv_branscher (
    user_id,
    bransch_id,
    bransch_name,
    emoji,
    focus,
    keywords,
    is_active,
    sort_order
) VALUES
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'restaurant',
    'Restaurang & Bar',
    '🍽️',
    'Bartending, service, fine dining, kundrelationer',
    ARRAY['bartender', 'servitör', 'hovmästare', 'kassa', 'kundservice', 'mixology', 'cocktails', 'vinkunskap', 'restaurang', 'bar'],
    TRUE,
    1
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'retail',
    'Butik & Detaljhandel',
    '🛍️',
    'Försäljning, kundrådgivning, visual merchandising, kassahantering',
    ARRAY['butiksbiträde', 'säljare', 'försäljning', 'kassa', 'lager', 'butik', 'retail', 'kundservice', 'merchandising', 'inventering'],
    TRUE,
    2
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'industry',
    'Industri & Lager',
    '🏭',
    'Produktion, lagerarbete, distribution, kvalitetskontroll',
    ARRAY['lager', 'produktion', 'truck', 'packning', 'kvalitetskontroll', 'industri', 'warehouse', 'logistik', 'distribution', 'förpackning'],
    TRUE,
    3
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'healthcare',
    'Vård & Omsorg',
    '🏥',
    'Äldreomsorg, personlig assistans, omvårdnad, dokumentation',
    ARRAY['vård', 'omsorg', 'vårdbiträde', 'personlig assistent', 'dokumentation', 'äldreomsorg', 'demens', 'omvårdnad', 'medicin', 'healthcare'],
    TRUE,
    4
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'tech',
    'Tech & IT',
    '💻',
    'Webbutveckling, content moderation, digital kompetens',
    ARRAY['webbutveckling', 'html', 'css', 'javascript', 'tech', 'digital', 'it', 'kod', 'programmering', 'react'],
    TRUE,
    5
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'customerservice',
    'Kundtjänst',
    '📞',
    'Telefonsupport, CRM-system, problemlösning, kundrelationer',
    ARRAY['kundtjänst', 'support', 'telefon', 'crm', 'helpdesk', 'kundservice', 'callcenter', 'problemlösning', 'service'],
    TRUE,
    6
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'reception',
    'Reception & Hotell',
    '🏨',
    'Receptionsarbete, gästservice, bokningssystem, hotellbranschen',
    ARRAY['reception', 'hotell', 'check-in', 'gästservice', 'bokning', 'hospitality', 'bokningssystem', 'telefon', 'gäst'],
    TRUE,
    7
),
(
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'contentmoderation',
    'Content Moderation',
    '🛡️',
    'Social media moderation, policy enforcement, community guidelines',
    ARRAY['content moderation', 'social media', 'policy', 'moderation', 'review', 'community guidelines', 'content review', 'moderator', 'digital safety'],
    TRUE,
    8
);

-- ----------------------------------------------------------------------------
-- 8. COVER LETTER PREFERENCES
-- user_id is UUID type
-- ----------------------------------------------------------------------------

-- Delete existing preferences to avoid duplicates, then insert
DELETE FROM public.user_cover_letter_preferences WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

INSERT INTO public.user_cover_letter_preferences (
    user_id,
    tone,
    max_words,
    greeting_style,
    signature_style,
    always_mention,
    never_mention
) VALUES (
    'da8ed517-3b67-4456-8831-6ed3cb7114ad',
    'professional',
    300,
    'formal',
    'full_name',
    ARRAY['anpassningsförmåga', 'problemlösning', 'teamwork', 'kundservice'],
    ARRAY['konst', 'galleri', 'utställning', 'målning', 'shopify', 'konstvetenskap', 'curator']
);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Summary of inserted data:
-- ✅ 1 user profile (updated)
-- ✅ 19 work experiences
-- ✅ 2 education entries
-- ✅ 28 skills
-- ✅ 7 awards
-- ✅ 4 volunteer positions
-- ✅ 8 CV branscher
-- ✅ 1 cover letter preferences entry
--
-- Total rows: 70 data points
-- ============================================================================
