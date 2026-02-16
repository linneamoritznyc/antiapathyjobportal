-- ============================================================================
-- FINAL INSERT SCRIPT FOR LINNEA'S COMPLETE PROFILE DATA
-- ============================================================================
-- User ID: da8ed517-3b67-4456-8831-6ed3cb7114ad
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. UPDATE USER PROFILE (in case it's incomplete)
-- ----------------------------------------------------------------------------
UPDATE public.user_profiles
SET
  full_name = 'Linnea Moritz',
  email = 'linneamoritzCV@gmail.com',
  phone = '+46 XX XXX XX XX',
  location = 'Stockholm, Sverige',
  drivers_license = TRUE,
  languages = ARRAY['Svenska (modersmål)', 'Engelska (flytande)', 'Spanska (god)', 'Franska (grundläggande)']
WHERE user_id = 'da8ed517-3b67-4456-8831-6ed3cb7114ad';

-- ----------------------------------------------------------------------------
-- 2. WORK EXPERIENCES (19 positions)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_experiences (user_id, company, title, start_date, end_date, description, categories, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Morfar Ginko & Pappa Ray', 'Bartender', 'Juni 2022', 'Augusti 2023', 'Mixology, kundservice, kassamanagement i högtrafikerad cocktailbar. Ansvarade för drinkmeny och personalutbildning.', ARRAY['restaurant'], 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'AG', 'Hovmästare/Bartender', 'November 2022', 'Augusti 2023', 'Blandade drinkar, serverade mat, hanterade bokningar. Deltidsroll parallellt med Morfar Ginko.', ARRAY['restaurant'], 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Steakhouse', 'Servitör/Bartender', 'Juni 2021', 'Maj 2022', 'Fine dining service, drinktillverkning, gästrelationer i exklusiv miljö.', ARRAY['restaurant'], 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Wayne''s Coffee', 'Restaurangbiträde', 'September 2019', 'Augusti 2020', 'Kaffeservering, kassahantering, kundkontakt i snabbtempomiljö.', ARRAY['restaurant', 'customerservice'], 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Cervera', 'Butiksbiträde', 'November 2020', 'Maj 2021', 'Försäljning av hushållsprodukter, kundrådgivning, lageradministration.', ARRAY['retail', 'customerservice'], 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Lagerhaus', 'Säljare', 'Januari 2020', 'Oktober 2020', 'Heminteriör försäljning, visual merchandising, kundmöten.', ARRAY['retail', 'customerservice'], 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Systembolaget', 'Butiksbiträde', 'Juni 2019', 'Augusti 2019', 'Vinrådgivning, lageradministration, kassahantering. Sommarjobb.', ARRAY['retail'], 7),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Frebaco', 'Produktionsassistent', 'September 2023', 'Februari 2024', 'Food production, kvalitetskontroll, förpackning. Arbetade i klimatstyrd produktionsmiljö.', ARRAY['industry'], 8),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'PostNord', 'Lagerarbetare', 'December 2021', 'Maj 2022', 'Paketsortering, lageradministration, distribution. Nattskift och helger.', ARRAY['industry'], 9),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tiohundra AB', 'Vårdbiträde', 'Juni 2018', 'Maj 2019', 'Äldreomsorg, personlig assistans, dokumentation i journalsystem.', ARRAY['healthcare'], 10),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Olika arbetsgivare', 'Personlig assistent', 'Januari 2017', 'Maj 2018', 'Stöd till personer med funktionsnedsättning. Flertal uppdragsgivare.', ARRAY['healthcare'], 11),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Majorel (via Manpower)', 'Content Moderator', 'Mars 2024', 'November 2024', 'Granskning av innehåll för sociala medier enligt community guidelines. Hanterade känsligt material, rapporterade policybrott, arbetade med internationellt team.', ARRAY['contentmoderation', 'tech'], 12),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Freelance', 'Junior Webbutvecklare', 'Januari 2023', 'December 2023', 'Byggde webbsidor med HTML, CSS, JavaScript för småföretag. Portfolio-projekt och kundutvecklingsuppdrag.', ARRAY['tech'], 13),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Telenor', 'Kundtjänstmedarbetare', 'Juni 2020', 'November 2020', 'Telefonkundservice, problemlösning, CRM-system. Hanterade abonnemangsärenden.', ARRAY['customerservice'], 14),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'SJ', 'Kundtjänst', 'Januari 2019', 'Maj 2019', 'Biljettsupport, reseinformation, kundrelationer. Säsongsarbete.', ARRAY['customerservice'], 15),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Comfort Hotel', 'Receptionist', 'September 2018', 'December 2018', 'Check-in/check-out, telefonservice, gästrelationer. Kvällsskift och helger.', ARRAY['reception', 'customerservice'], 16),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Galleri Moment', 'Galleriassistent', 'Juni 2016', 'Juni 2017', 'Vernissage-koordinering, konstnärskontakter, utställningsplanering.', ARRAY['art'], 17),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Konstakademien', 'Curator Assistant', 'Januari 2016', 'Maj 2016', 'Utställningskurering, katalogproduktion. Praktikplats.', ARRAY['art'], 18),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Stad', 'Projektassistent', 'Juli 2017', 'December 2017', 'Administrativt stöd för samhällsprojekt. Tidsbegränsad projekttjänst.', ARRAY['other'], 19);

-- ----------------------------------------------------------------------------
-- 3. EDUCATION (2 entries)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_education (user_id, school, degree, field_of_study, location, start_date, end_date) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Universitet', 'Kandidatexamen', 'Konstvetenskap', 'Stockholm', '2013', '2016'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Södra Latin', 'Gymnasieexamen', 'Estetiska programmet - Konst', 'Stockholm', '2010', '2013');

-- ----------------------------------------------------------------------------
-- 4. SKILLS
-- ----------------------------------------------------------------------------
INSERT INTO public.user_skills (user_id, category, skill_type, skill_text) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'code', 'HTML, CSS, JavaScript'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'code', 'React (grundläggande)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'code', 'Python (grundläggande)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'software', 'Microsoft Office'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'software', 'Google Workspace'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'software', 'CRM-system'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'software', 'Kassasystem'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'software', 'Bokningssystem'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'specialized', 'Content Moderation'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Tekniska', 'specialized', 'Social Media Policy'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'communication', 'Kundservice'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'communication', 'Kommunikation'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'problem_solving', 'Problemlösning'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'problem_solving', 'Konflikthantering'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'collaboration', 'Teamwork'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'personal', 'Anpassningsförmåga'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'personal', 'Multitasking'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'personal', 'Empati'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'personal', 'Noggrannhet'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Mjuka färdigheter', 'personal', 'Stresshantering'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Certifieringar', 'certification', 'Hygiencompetens'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Certifieringar', 'certification', 'Alkoholservering'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Certifieringar', 'certification', 'Första hjälpen'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Certifieringar', 'certification', 'Truckkort A'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Branschspecifik', 'industry', 'Food Safety'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Branschspecifik', 'industry', 'Inventory Management'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Branschspecifik', 'industry', 'Visual Merchandising'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Branschspecifik', 'industry', 'Mixology');

-- ----------------------------------------------------------------------------
-- 5. AWARDS (user_id is TEXT in this table)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_awards (user_id, award_text, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Månadens medarbetare - AG Restaurant (Maj 2023)', 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Employee of the Quarter - Majorel (Q3 2024)', 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Bästa försäljare - Lagerhaus (Sommaren 2020)', 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Teambuilding Award - PostNord (Mars 2022)', 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Customer Service Excellence - Telenor (Oktober 2020)', 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Perfect Attendance - Frebaco (December 2023)', 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Innovation Prize - Comfort Hotel (November 2018)', 7);

-- ----------------------------------------------------------------------------
-- 6. VOLUNTEER WORK (user_id is TEXT in this table)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_volunteer (user_id, organization, dates, bullets, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Stadsmission', '2019-2020', ARRAY['Serverade mat till hemlösa', 'Organiserade julbord', 'Utdelning av hygienprodukter'], 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Pride Stockholm', 'Sommaren 2018', ARRAY['Event coordinator', 'Logistik och besökshantering', 'Informationsdisk'], 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kompisbyråan', '2017-2018', ARRAY['Mentor för nyanlända', 'Språkstöd och kulturell orientering', 'Myndighetskontakter'], 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Katthem', '2016', ARRAY['Djurvolontär', 'Adoptionsarrangemang', 'Socialisering av katter'], 4);

-- ----------------------------------------------------------------------------
-- 7. CV BRANSCHER (user_id is TEXT in this table)
-- ----------------------------------------------------------------------------
INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, emoji, focus, keywords, is_active, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'Restaurang & Bar', '🍽️', 'Bartending, service', ARRAY['bartender', 'servitör', 'kassa'], TRUE, 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'Butik & Detaljhandel', '🛍️', 'Försäljning', ARRAY['butik', 'säljare', 'kassa'], TRUE, 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'industry', 'Industri & Lager', '🏭', 'Produktion, lager', ARRAY['lager', 'produktion', 'truck'], TRUE, 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'healthcare', 'Vård & Omsorg', '🏥', 'Äldreomsorg', ARRAY['vård', 'omsorg'], TRUE, 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'Tech & IT', '💻', 'Webbutveckling', ARRAY['web', 'tech'], TRUE, 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'Kundtjänst', '📞', 'Support', ARRAY['kundtjänst', 'support'], TRUE, 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'reception', 'Reception', '🏨', 'Receptionsarbete', ARRAY['reception', 'hotell'], TRUE, 7),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'contentmoderation', 'Content Moderation', '🛡️', 'Moderation', ARRAY['moderation', 'policy'], TRUE, 8);

-- ----------------------------------------------------------------------------
-- 8. COVER LETTER PREFERENCES
-- ----------------------------------------------------------------------------
INSERT INTO public.user_cover_letter_preferences (user_id, tone, max_words, greeting_style, signature_style, always_mention, never_mention) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'professional', 300, 'formal', 'full_name',
 ARRAY['anpassningsförmåga', 'problemlösning', 'teamwork'],
 ARRAY['konst', 'galleri', 'utställning', 'målning', 'shopify']);

-- Done!
