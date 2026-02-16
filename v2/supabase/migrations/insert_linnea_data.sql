-- ============================================================================
-- INSERT LINNEA'S DATA INTO EXISTING SCHEMA
-- ============================================================================
-- IMPORTANT: Replace 'YOUR_USER_ID_HERE' with Linnea's actual user_id UUID
-- after creating her account in Supabase Authentication
-- ============================================================================

-- Variable to make it easy to replace (you'll need to do a find/replace)
-- Find: 'YOUR_USER_ID_HERE'
-- Replace with: actual UUID like '123e4567-e89b-12d3-a456-426614174000'

-- ----------------------------------------------------------------------------
-- 1. USER PROFILE
-- ----------------------------------------------------------------------------
INSERT INTO public.user_profiles (user_id, full_name, email, phone, location, drivers_license, languages) VALUES
('YOUR_USER_ID_HERE', 'Linnea Moritz', 'linneamoritzCV@gmail.com', '+46 XX XXX XX XX', 'Stockholm, Sverige', TRUE, ARRAY['Svenska (modersmål)', 'Engelska (flytande)', 'Spanska (god)', 'Franska (grundläggande)']);

-- ----------------------------------------------------------------------------
-- 2. WORK EXPERIENCES (19 positions)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_experiences (user_id, company, title, start_date, end_date, description, categories, sort_order) VALUES
-- Restaurant positions
('YOUR_USER_ID_HERE', 'Morfar Ginko & Pappa Ray', 'Bartender', 'Juni 2022', 'Augusti 2023', 'Mixology, kundservice, kassamanagement i högtrafikerad cocktailbar. Ansvarade för drinkmeny och personalutbildning.', ARRAY['restaurant'], 1),
('YOUR_USER_ID_HERE', 'AG', 'Hovmästare/Bartender', 'November 2022', 'Augusti 2023', 'Blandade drinkar, serverade mat, hanterade bokningar. Deltidsroll parallellt med Morfar Ginko.', ARRAY['restaurant'], 2),
('YOUR_USER_ID_HERE', 'Steakhouse', 'Servitör/Bartender', 'Juni 2021', 'Maj 2022', 'Fine dining service, drinktillverkning, gästrelationer i exklusiv miljö.', ARRAY['restaurant'], 3),
('YOUR_USER_ID_HERE', 'Wayne''s Coffee', 'Restaurangbiträde', 'September 2019', 'Augusti 2020', 'Kaffeservering, kassahantering, kundkontakt i snabbtempomiljö.', ARRAY['restaurant', 'customerservice'], 4),

-- Retail positions
('YOUR_USER_ID_HERE', 'Cervera', 'Butiksbiträde', 'November 2020', 'Maj 2021', 'Försäljning av hushållsprodukter, kundrådgivning, lageradministration.', ARRAY['retail', 'customerservice'], 5),
('YOUR_USER_ID_HERE', 'Lagerhaus', 'Säljare', 'Januari 2020', 'Oktober 2020', 'Heminteriör försäljning, visual merchandising, kundmöten.', ARRAY['retail', 'customerservice'], 6),
('YOUR_USER_ID_HERE', 'Systembolaget', 'Butiksbiträde', 'Juni 2019', 'Augusti 2019', 'Vinrådgivning, lageradministration, kassahantering. Sommarjobb.', ARRAY['retail'], 7),

-- Industry/Production
('YOUR_USER_ID_HERE', 'Frebaco', 'Produktionsassistent', 'September 2023', 'Februari 2024', 'Food production, kvalitetskontroll, förpackning. Arbetade i klimatstyrd produktionsmiljö.', ARRAY['industry'], 8),
('YOUR_USER_ID_HERE', 'PostNord', 'Lagerarbetare', 'December 2021', 'Maj 2022', 'Paketsortering, lageradministration, distribution. Nattskift och helger.', ARRAY['industry'], 9),

-- Healthcare
('YOUR_USER_ID_HERE', 'Tiohundra AB', 'Vårdbiträde', 'Juni 2018', 'Maj 2019', 'Äldreomsorg, personlig assistans, dokumentation i journalsystem.', ARRAY['healthcare'], 10),
('YOUR_USER_ID_HERE', 'Olika arbetsgivare', 'Personlig assistent', 'Januari 2017', 'Maj 2018', 'Stöd till personer med funktionsnedsättning. Flertal uppdragsgivare.', ARRAY['healthcare'], 11),

-- Tech/Digital
('YOUR_USER_ID_HERE', 'Majorel (via Manpower)', 'Content Moderator', 'Mars 2024', 'November 2024', 'Granskning av innehåll för sociala medier enligt community guidelines. Hanterade känsligt material, rapporterade policybrott, arbetade med internationellt team.', ARRAY['contentmoderation', 'tech'], 12),
('YOUR_USER_ID_HERE', 'Freelance', 'Junior Webbutvecklare', 'Januari 2023', 'December 2023', 'Byggde webbsidor med HTML, CSS, JavaScript för småföretag. Portfolio-projekt och kundutvecklingsuppdrag.', ARRAY['tech'], 13),

-- Customer service
('YOUR_USER_ID_HERE', 'Telenor', 'Kundtjänstmedarbetare', 'Juni 2020', 'November 2020', 'Telefonkundservice, problemlösning, CRM-system. Hanterade abonnemangsärenden.', ARRAY['customerservice'], 14),
('YOUR_USER_ID_HERE', 'SJ', 'Kundtjänst', 'Januari 2019', 'Maj 2019', 'Biljettsupport, reseinformation, kundrelationer. Säsongsarbete.', ARRAY['customerservice'], 15),

-- Reception
('YOUR_USER_ID_HERE', 'Comfort Hotel', 'Receptionist', 'September 2018', 'December 2018', 'Check-in/check-out, telefonservice, gästrelationer. Kvällsskift och helger.', ARRAY['reception', 'customerservice'], 16),

-- Art/Culture (historical - archived experience)
('YOUR_USER_ID_HERE', 'Galleri Moment', 'Galleriassistent', 'Juni 2016', 'Juni 2017', 'Vernissage-koordinering, konstnärskontakter, utställningsplanering.', ARRAY['art'], 17),
('YOUR_USER_ID_HERE', 'Konstakademien', 'Curator Assistant', 'Januari 2016', 'Maj 2016', 'Utställningskurering, katalogproduktion. Praktikplats.', ARRAY['art'], 18),

-- Other
('YOUR_USER_ID_HERE', 'Stockholms Stad', 'Projektassistent', 'Juli 2017', 'December 2017', 'Administrativt stöd för samhällsprojekt. Tidsbegränsad projekttjänst.', ARRAY['other'], 19);

-- ----------------------------------------------------------------------------
-- 3. EDUCATION (2 entries)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date) VALUES
('YOUR_USER_ID_HERE', 'Stockholms Universitet', 'Kandidatexamen', 'Konstvetenskap', 'Stockholm', '2013', '2016'),
('YOUR_USER_ID_HERE', 'Södra Latin', 'Gymnasieexamen', 'Estetiska programmet - Konst', 'Stockholm', '2010', '2013');

-- ----------------------------------------------------------------------------
-- 4. SKILLS (grouped by category)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_skills (user_id, category, skill_type, skill_text) VALUES
-- Technical
('YOUR_USER_ID_HERE', 'Tekniska', 'code', 'HTML, CSS, JavaScript'),
('YOUR_USER_ID_HERE', 'Tekniska', 'code', 'React (grundläggande)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'code', 'Python (grundläggande)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'software', 'Microsoft Office (Word, Excel, PowerPoint)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'software', 'Google Workspace (Docs, Sheets, Drive)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'software', 'CRM-system (Zendesk, Salesforce)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'software', 'Kassasystem och POS'),
('YOUR_USER_ID_HERE', 'Tekniska', 'software', 'Bokningssystem (TheFork, Resy)'),
('YOUR_USER_ID_HERE', 'Tekniska', 'specialized', 'Content Moderation'),
('YOUR_USER_ID_HERE', 'Tekniska', 'specialized', 'Social Media Policy Enforcement'),

-- Soft skills
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'communication', 'Kundservice (expertis)'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'communication', 'Kommunikation'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'problem_solving', 'Problemlösning'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'problem_solving', 'Konflikthantering'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'collaboration', 'Teamwork'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'personal', 'Anpassningsförmåga'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'personal', 'Multitasking'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'personal', 'Empati'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'personal', 'Attention to Detail'),
('YOUR_USER_ID_HERE', 'Mjuka färdigheter', 'personal', 'Stresshantering'),

-- Certifications
('YOUR_USER_ID_HERE', 'Certifieringar', 'certification', 'Hygiencompetens'),
('YOUR_USER_ID_HERE', 'Certifieringar', 'certification', 'Alkoholservering'),
('YOUR_USER_ID_HERE', 'Certifieringar', 'certification', 'Första hjälpen'),
('YOUR_USER_ID_HERE', 'Certifieringar', 'certification', 'Truckkort A'),

-- Industry-specific
('YOUR_USER_ID_HERE', 'Branschspecifik', 'industry', 'Food Safety & HACCP'),
('YOUR_USER_ID_HERE', 'Branschspecifik', 'industry', 'Inventory Management'),
('YOUR_USER_ID_HERE', 'Branschspecifik', 'industry', 'Visual Merchandising'),
('YOUR_USER_ID_HERE', 'Branschspecifik', 'industry', 'Mixology'),
('YOUR_USER_ID_HERE', 'Branschspecifik', 'industry', 'Vinkunskap');

-- ----------------------------------------------------------------------------
-- 5. AWARDS (7 awards)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_awards (user_id, award_text, sort_order) VALUES
('YOUR_USER_ID_HERE', 'Månadens medarbetare - AG Restaurant (Maj 2023) - Utnämnd för utmärkt kundservice och teamwork', 1),
('YOUR_USER_ID_HERE', 'Employee of the Quarter - Majorel (Q3 2024) - Erkänd för hög noggrannhet i content moderation', 2),
('YOUR_USER_ID_HERE', 'Bästa försäljare - Lagerhaus (Sommaren 2020) - Högst försäljning under sommarmånaderna', 3),
('YOUR_USER_ID_HERE', 'Teambuilding Award - PostNord (Mars 2022) - För positivt bidrag till teamklimat', 4),
('YOUR_USER_ID_HERE', 'Customer Service Excellence - Telenor (Oktober 2020) - Högst kundnöjdhetsbetyg under kvartalet', 5),
('YOUR_USER_ID_HERE', 'Perfect Attendance - Frebaco (December 2023) - Inga sjukdagar under hela anställningsperioden', 6),
('YOUR_USER_ID_HERE', 'Innovation Prize - Comfort Hotel (November 2018) - För förbättring av check-in-processen', 7);

-- ----------------------------------------------------------------------------
-- 6. VOLUNTEER WORK (4 positions)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_volunteer (user_id, organization, dates, bullets, sort_order) VALUES
('YOUR_USER_ID_HERE', 'Stockholms Stadsmission', '2019-2020', ARRAY[
    'Serverade mat till hemlösa och utsatta personer',
    'Organiserade julbord och högtidsevenemang',
    'Deltog i teamet för utdelning av hygienprodukter'
], 1),
('YOUR_USER_ID_HERE', 'Pride Stockholm', 'Sommaren 2018', ARRAY[
    'Event coordinator under Pride-veckan',
    'Hjälpte till med logistik och besökshantering',
    'Informationsdisk och gästrelationer'
], 2),
('YOUR_USER_ID_HERE', 'Kompisbyråan', '2017-2018', ARRAY[
    'Mentor för nyanlända till Sverige',
    'Språkstöd och kulturell orientering',
    'Hjälpte med praktiska göromål och myndighetskontakter'
], 3),
('YOUR_USER_ID_HERE', 'Stockholms Katthem', '2016', ARRAY[
    'Djurvolontär med fokus på kattvård',
    'Hjälpte till med adoptionsarrangemang',
    'Socialiserade katter för återplacering'
], 4);

-- ----------------------------------------------------------------------------
-- 7. CV BRANSCHER (Define which industries Linnea has CVs for)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, emoji, focus, keywords, is_active, sort_order) VALUES
('YOUR_USER_ID_HERE', 'restaurant', 'Restaurang & Bar', '🍽️', 'Bartending, service, fine dining', ARRAY['bartender', 'servitör', 'hovmästare', 'kassa', 'kundservice', 'mixology'], TRUE, 1),
('YOUR_USER_ID_HERE', 'retail', 'Butik & Detaljhandel', '🛍️', 'Försäljning, kundrådgivning, visual merchandising', ARRAY['butiksbiträde', 'säljare', 'försäljning', 'kassa', 'lager', 'butik'], TRUE, 2),
('YOUR_USER_ID_HERE', 'industry', 'Industri & Lager', '🏭', 'Produktion, lager, distribution', ARRAY['lager', 'produktion', 'truck', 'packning', 'kvalitetskontroll'], TRUE, 3),
('YOUR_USER_ID_HERE', 'healthcare', 'Vård & Omsorg', '🏥', 'Äldreomsorg, personlig assistans', ARRAY['vård', 'omsorg', 'vårdbiträde', 'personlig assistent', 'dokumentation'], TRUE, 4),
('YOUR_USER_ID_HERE', 'tech', 'Tech & IT', '💻', 'Webbutveckling, content moderation', ARRAY['webbutveckling', 'html', 'css', 'javascript', 'tech', 'digital'], TRUE, 5),
('YOUR_USER_ID_HERE', 'customerservice', 'Kundtjänst', '📞', 'Telefonsupport, CRM, problemlösning', ARRAY['kundtjänst', 'support', 'telefon', 'crm', 'helpdesk'], TRUE, 6),
('YOUR_USER_ID_HERE', 'reception', 'Reception & Hotell', '🏨', 'Receptionsarbete, gästservice', ARRAY['reception', 'hotell', 'check-in', 'gästservice', 'bokning'], TRUE, 7),
('YOUR_USER_ID_HERE', 'contentmoderation', 'Content Moderation', '🛡️', 'Social media moderation, policy enforcement', ARRAY['content moderation', 'social media', 'policy', 'moderation', 'review'], TRUE, 8);

-- ----------------------------------------------------------------------------
-- 8. USER PREFERENCES (Cover letter settings)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_cover_letter_preferences (user_id, tone, max_words, greeting_style, signature_style, always_mention, never_mention) VALUES
('YOUR_USER_ID_HERE',
 'professional',
 300,
 'formal',
 'full_name',
 ARRAY['anpassningsförmåga', 'problemlösning', 'teamwork'],
 ARRAY['konst', 'galleri', 'utställning', 'målning', 'shopify']
);

-- ----------------------------------------------------------------------------
-- NEXT STEPS:
-- ----------------------------------------------------------------------------
-- 1. Create Linnea's account in Supabase Authentication (Email + Password)
-- 2. Copy her user_id UUID
-- 3. Find and Replace 'YOUR_USER_ID_HERE' with the actual UUID
-- 4. Run this migration in Supabase SQL Editor
-- 5. Upload 8 CV PDFs to Supabase Storage
-- 6. Insert records in user_cvs table with vibe_id matching bransch_id
-- ============================================================================
