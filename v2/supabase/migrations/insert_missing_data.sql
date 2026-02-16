-- ============================================================================
-- INSERT ONLY MISSING DATA FOR LINNEA
-- ============================================================================
-- Based on current counts:
-- - user_awards: 0 → insert 7
-- - user_volunteer: 0 → insert 4
-- - user_cv_branscher: 0 → insert 8
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. AWARDS (0 → 7 entries)
-- Note: user_id is TEXT type in this table
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
-- 2. VOLUNTEER WORK (0 → 4 entries)
-- Note: user_id is TEXT type in this table
-- ----------------------------------------------------------------------------
INSERT INTO public.user_volunteer (user_id, organization, dates, bullets, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Stadsmission', '2019-2020', ARRAY['Serverade mat till hemlösa', 'Organiserade julbord', 'Utdelning av hygienprodukter'], 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Pride Stockholm', 'Sommaren 2018', ARRAY['Event coordinator', 'Logistik och besökshantering', 'Informationsdisk'], 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Kompisbyråan', '2017-2018', ARRAY['Mentor för nyanlända', 'Språkstöd och kulturell orientering', 'Myndighetskontakter'], 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Stockholms Katthem', '2016', ARRAY['Djurvolontär', 'Adoptionsarrangemang', 'Socialisering av katter'], 4);

-- ----------------------------------------------------------------------------
-- 3. CV BRANSCHER (0 → 8 entries)
-- Note: user_id is TEXT type in this table
-- ----------------------------------------------------------------------------
INSERT INTO public.user_cv_branscher (user_id, bransch_id, bransch_name, emoji, focus, keywords, is_active, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'restaurant', 'Restaurang & Bar', '🍽️', 'Bartending, service, fine dining', ARRAY['bartender', 'servitör', 'hovmästare', 'kassa', 'kundservice', 'mixology'], TRUE, 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'retail', 'Butik & Detaljhandel', '🛍️', 'Försäljning, kundrådgivning, visual merchandising', ARRAY['butiksbiträde', 'säljare', 'försäljning', 'kassa', 'lager', 'butik'], TRUE, 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'industry', 'Industri & Lager', '🏭', 'Produktion, lager, distribution', ARRAY['lager', 'produktion', 'truck', 'packning', 'kvalitetskontroll'], TRUE, 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'healthcare', 'Vård & Omsorg', '🏥', 'Äldreomsorg, personlig assistans', ARRAY['vård', 'omsorg', 'vårdbiträde', 'personlig assistent', 'dokumentation'], TRUE, 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'Tech & IT', '💻', 'Webbutveckling, content moderation', ARRAY['webbutveckling', 'html', 'css', 'javascript', 'tech', 'digital'], TRUE, 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'customerservice', 'Kundtjänst', '📞', 'Telefonsupport, CRM, problemlösning', ARRAY['kundtjänst', 'support', 'telefon', 'crm', 'helpdesk'], TRUE, 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'reception', 'Reception & Hotell', '🏨', 'Receptionsarbete, gästservice', ARRAY['reception', 'hotell', 'check-in', 'gästservice', 'bokning'], TRUE, 7),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'contentmoderation', 'Content Moderation', '🛡️', 'Social media moderation, policy enforcement', ARRAY['content moderation', 'social media', 'policy', 'moderation', 'review'], TRUE, 8);

-- Done! Run this to insert the 3 missing data types.
