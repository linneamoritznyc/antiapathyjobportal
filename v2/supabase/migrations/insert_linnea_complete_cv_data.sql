-- ============================================
-- COMPLETE MASTER CV - ALL DATA SOURCES
-- User: Linnea Moritz (da8ed517-3b67-4456-8831-6ed3cb7114ad)
-- Sources: Industry CVs, linneamoritzdev.vercel.app, existing database
-- ============================================
BEGIN;
-- ============================================
-- EDUCATION (4 entries)
-- ============================================
INSERT INTO user_education (user_id, school, location, degree, dates, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Minerva University', 'San Francisco, USA', 'B.S in Social Science, Economics and Business Administration (GPA: 3.6)', 'Aug 2017 - Maj 2021', 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'United World College Red Cross Nordics', 'Flekke, Norge', 'International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)', 'Aug 2015 - Maj 2017', 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'International School of the Stockholm Region', 'Stockholm', 'International Baccalaureate (Year 1)', 'Aug 2014 - Maj 2015', 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Per Brahe Gymnasium', 'Jönköping', 'Pre-IB', 'Aug 2013 - Maj 2014', 4)
ON CONFLICT DO NOTHING;
-- ============================================
-- TECH CERTIFICATIONS (from linneamoritzdev.vercel.app)
-- ============================================
INSERT INTO tech_certifications (user_id, certification_name, issuer, year_obtained, credential_url, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Introduction to Python', 'DataCamp', 2022, 'https://www.datacamp.com/completed/statement-of-accomplishment/course/b48391ada93ca5d05574753a080433a38613cbb1', 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Intermediate SQL Queries', 'DataCamp', 2021, 'https://www.datacamp.com/completed/statement-of-accomplishment/course/39b604029392a524860d0b1b01770fd40daca6ea', 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Joining Data in SQL', 'DataCamp', 2022, 'https://www.datacamp.com/statement-of-accomplishment/course/716134e07e88965583ff3a22ec5b0331fefb5ab3', 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Credit Risk Modeling in Python', 'DataCamp', 2021, 'https://www.datacamp.com/completed/statement-of-accomplishment/course/7a7b44fbb09e0d53fd6a316cb6be3d95b89ad054', 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Portfolio Risk Management in Python', 'DataCamp', 2021, 'https://www.datacamp.com/completed/statement-of-accomplishment/course/300ccf35d18836e5febcfe983ed849e277bc958d', 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Foundations: Data, Data, Everywhere', 'Google via Coursera', NULL, 'https://www.coursera.org/account/accomplishments/certificate/RKCK36NMMFRY', 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Blockchain for Business', 'Udemy', 2021, 'https://www.udemy.com/certificate/UC-d788d078-ea05-49fc-bc2a-e93f455dd0d1/', 7)
ON CONFLICT DO NOTHING;
-- ============================================
-- TECH PROJECTS (from linneamoritzdev.vercel.app)
-- ============================================
INSERT INTO tech_projects (user_id, project_name, description, tech_stack, live_url, year, highlights, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'CBAM-Validator',
 'Reaktivt frågeformulär för svenska företag som importerar varor. Hjälper företag att följa EU:s kolbaserade gränsskatt (CBAM). Multi-steg formulär med villkorlig logik.',
 ARRAY['TypeScript', 'Next.js', 'Reactive Forms']::TEXT[],
 'https://cbam-validator.vercel.app/',
 2026,
 ARRAY['Lansering 25 feb 2026', 'Multi-steg formulär', 'EU-regler CBAM']::TEXT[],
 1),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'NordiqFlow',
 'Flerproduktsplattform för svensk arbetsmarknadsintelligens med verktyg för karriärövergångar, kompetensanalys och kommunal utbildningsdata.',
 ARRAY['Python', 'Next.js', 'React', 'API Integration']::TEXT[],
 'https://nordiqflow.vercel.app/',
 2025,
 ARRAY['SCB arbetsmarknadsdata', 'AI-driven matchning', 'Kommunal analys']::TEXT[],
 2),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Linneas Konstbutik',
 'E-handelsplattform med försäljning av original kubistiska oljemålningar internationellt. Automatisering för Pinterest-marknadsföring och AI-produktrekommendationer.',
 ARRAY['Shopify', 'Pinterest API', 'Anthropic API', 'Automation']::TEXT[],
 'https://linneamoritz.com/',
 2024,
 ARRAY['Internationell e-handel', 'Pinterest automation', 'AI-produktbeskrivningar']::TEXT[],
 3),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Smålands Företagskarta',
 'Interaktiv dashboard som visualiserar företagsdata för alla 13 kommuner i Jönköpings län. Byggd för Science Park, Almi och kommuner.',
 ARRAY['Next.js 14', 'TypeScript', 'Recharts', 'Framer Motion']::TEXT[],
 'https://smalands-foretagskarta.vercel.app/',
 2025,
 ARRAY['Interaktiv SVG-karta', '13 kommuner', 'Kvartalsuppdateringar']::TEXT[],
 4),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'AK Städservice',
 'Komplett företagshemsida för Stockholmsbaserat B2B-städföretag. SEO-optimerad för Google och AI-verktyg.',
 ARRAY['Next.js', 'React', 'Tailwind CSS', 'SEO']::TEXT[],
 'https://akstadservice.vercel.app/',
 2025,
 ARRAY['Byggd på 2 dagar', 'B2B-fokus', 'AI-SEO optimerad']::TEXT[],
 5),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Provence Bike Touring',
 'Ruttplaneringsplattform för självständiga cykelturister i Provence. Interaktiv karta med POI-lager, höjdprofiler och GPX-export.',
 ARRAY['React', 'Mapbox GL JS', 'PostGIS', 'OpenStreetMap']::TEXT[],
 'https://provencebiking.vercel.app/',
 2025,
 ARRAY['Mapbox GL JS', 'PostGIS queries', 'Swipeable mobile UI']::TEXT[],
 6),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 '10K Race Finder — Europe 2026',
 'Verktyg för att hitta och bokmärka 10K-lopp i Europa. 38 kurerade lopp med localStorage favoriter.',
 ARRAY['React 18', 'Vite 5', 'localStorage', 'IntersectionObserver']::TEXT[],
 'https://10krunningeurope.vercel.app/',
 2026,
 ARRAY['38 europeiska lopp', 'localStorage favoriter', 'Multi-country']::TEXT[],
 7),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Bidragsguiden',
 'AI-driven webbapp för att hitta företagsbidrag. Interaktivt quiz som matchar svenska företagare mot relevanta bidrag från Tillväxtverket, Vinnova, EU-fonder.',
 ARRAY['Next.js 14', 'Claude API', 'Supabase', 'Vercel']::TEXT[],
 'https://bidragsguiden.vercel.app/',
 2025,
 ARRAY['Live i produktion', 'Används av svenska företag', 'EU compliance']::TEXT[],
 8),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Backspegeln',
 'Skräck-temat körkortsquiz med pseudo-3D grafik. Svara rätt på svenska körkorsfrågor för att överleva.',
 ARRAY['React 19', 'Vite 6', 'Tone.js', 'Canvas API']::TEXT[],
 'https://backspegeln.vercel.app/',
 2025,
 ARRAY['Interaktivt spel', 'Äkta Trafikverket-frågor', 'Web Audio synthesis']::TEXT[],
 9),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Digitala Produktpass',
 'Quiz-baserat verktyg som hjälper svenska tillverkare generera EU-kompatibla Digitala Produktpass med AI.',
 ARRAY['Next.js 14', 'TypeScript', 'Claude API', 'jsPDF']::TEXT[],
 NULL,
 2025,
 ARRAY['EU ESPR 2024/1781', 'AI-genererade pass', 'PDF + QR-kod']::TEXT[],
 10),
('da8ed517-3b67-4456-8831-6ed3cb7114ad',
 'Anna Levitova Portfolio',
 'Marknadsföringswebbplats för PR-strateg. Flerspråkigt stöd (EN/DE/RU) med glassmorfism-design.',
 ARRAY['Next.js', 'React', 'TypeScript', 'Tailwind CSS', 'Framer Motion']::TEXT[],
 'https://pinkportfolio.vercel.app/',
 2025,
 ARRAY['Flerspråkig (EN/DE/RU)', 'Glassmorfism', 'Framer Motion animations']::TEXT[],
 11)
ON CONFLICT DO NOTHING;
-- ============================================
-- ADDITIONAL AWARDS (from dev site)
-- ============================================
INSERT INTO user_awards (user_id, award_text, sort_order) VALUES
('da8ed517-3b67-4456-8831-6ed3cb7114ad', '1:a pris Global Startup Weekend Stockholm för Terra Finance (Google for Startups & Techstars)', 8),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'Scoutad som professionell kubistisk målare till 30 Campos Eliseos (5 av 500+ sökande)', 9)
ON CONFLICT DO NOTHING;
-- ============================================
-- ADDITIONAL SKILLS (from dev site)
-- ============================================
INSERT INTO user_skills (user_id, category, skill_type, skill_text) VALUES
-- Programming languages
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'TypeScript'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'JavaScript'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'R'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'HTML/CSS'),
-- Frameworks
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Next.js'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Tailwind CSS'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Node.js'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'NumPy'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Pandas'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Framer Motion'),
-- APIs
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Gmail API'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Claude API'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'OpenAI API'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Google Sheets API'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Mapbox GL JS'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Overpass API'),
-- Platforms
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Vercel'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'GitHub'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'PostgreSQL'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'PostGIS'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Supabase'),
-- Specialties
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Machine Learning'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Web3/Blockchain'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'OAuth'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'GIS & Kartvisualisering'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Canvas API'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'tech', 'technical', 'Tone.js'),
-- Languages
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Norska (professionellt)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Danska (professionellt)'),
('da8ed517-3b67-4456-8831-6ed3cb7114ad', 'all', 'language', 'Franska (grundläggande)')
ON CONFLICT DO NOTHING;
COMMIT;
-- ============================================
-- SUMMARY
-- ============================================
-- This migration adds:
-- - 4 education entries
-- - 7 DataCamp/Google/Udemy tech certifications
-- - 11 production tech projects with live URLs
-- - 2 additional awards
-- - 30+ additional technical skills
--
-- Combined with existing data:
-- - 16 work experiences (already in DB)
-- - 22 base skills (already in DB)
-- - 7 awards (already in DB)
-- - 4 volunteer entries (already in DB)
--
-- TOTAL MASTER CV:
-- - 4 education
-- - 16 experiences
-- - 7 tech certs
-- - 50+ skills
-- - 9 awards
-- - 4 volunteer
-- - 11 tech projects
-- ============================================
