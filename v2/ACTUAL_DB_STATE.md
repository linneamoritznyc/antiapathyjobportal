# Actual Supabase Database State (as of 2026-02-16)

## CRITICAL: Mixed user_id Types

**UUID tables:** user_profiles, user_experiences, user_education, user_skills, user_cvs
**TEXT tables:** user_awards, user_volunteer, user_cv_branscher, artist_*, tech_*, academic_publications

## Table Row Counts

| Table | Rows | user_id Type |
|-------|------|--------------|
| user_profiles | 1 | UUID |
| user_experiences | 15 | UUID |
| user_education | 1 | UUID |
| user_skills | 18 | UUID |
| user_cvs | 4 | UUID |
| user_awards | 0 | TEXT |
| user_volunteer | 0 | TEXT |
| user_cv_branscher | 0 | TEXT |
| tech_certifications | 7 | TEXT |
| tech_projects | 0 | TEXT |
| artist_exhibitions | 0 | TEXT |
| artist_residencies | 0 | TEXT |
| artist_collections | 0 | TEXT |
| academic_publications | 0 | TEXT |

## Full Schema

### user_profiles (user_id: UUID)
- id: uuid (PK)
- user_id: uuid (NOT NULL)
- full_name: text
- email: text
- phone: text
- location: text
- drivers_license: boolean
- languages: ARRAY
- created_at: timestamptz

### user_experiences (user_id: UUID)
- id: uuid (PK)
- user_id: uuid (NOT NULL)
- company: text (NOT NULL)
- title: text (NOT NULL)
- start_date: text
- end_date: text
- description: text
- categories: ARRAY
- sort_order: integer

### user_education (user_id: UUID)
- id: uuid (PK)
- user_id: uuid (NOT NULL)
- school: text (NOT NULL)
- degree: text
- field_of_study: text
- location: text
- start_date: text
- end_date: text

### user_skills (user_id: UUID)
- id: uuid (PK)
- user_id: uuid (NOT NULL)
- category: text
- skill_type: text
- skill_text: text (NOT NULL)

### user_cvs (user_id: UUID)
- id: uuid (PK)
- user_id: uuid (NOT NULL)
- vibe_id: text (NOT NULL)
- vibe_name: text
- cv_text: text

### user_awards (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- award_text: text (NOT NULL)
- sort_order: integer
- created_at: timestamptz

### user_volunteer (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- organization: text (NOT NULL)
- dates: text
- bullets: ARRAY
- sort_order: integer
- created_at: timestamptz

### user_cv_branscher (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- bransch_id: text (NOT NULL)
- bransch_name: text (NOT NULL)
- emoji: text
- focus: text
- keywords: ARRAY
- is_active: boolean
- sort_order: integer
- created_at: timestamptz

### tech_certifications (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- certification_name: text (NOT NULL)
- issuer: text
- year_obtained: integer
- expiry_year: integer
- credential_url: text
- sort_order: integer
- created_at: timestamptz

### tech_projects (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- project_name: text (NOT NULL)
- description: text
- tech_stack: ARRAY
- github_url: text
- live_url: text
- year: integer
- highlights: ARRAY
- sort_order: integer
- created_at: timestamptz

### artist_exhibitions (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- exhibition_type: text (NOT NULL)
- title: text
- venue: text (NOT NULL)
- city: text
- country: text
- year: integer
- notes: text
- sort_order: integer
- created_at: timestamptz

### artist_residencies (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- entry_type: text (NOT NULL)
- name: text (NOT NULL)
- organization: text
- location: text
- year: integer
- notes: text
- sort_order: integer
- created_at: timestamptz

### artist_collections (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- collection_name: text (NOT NULL)
- location: text
- year_acquired: integer
- notes: text
- sort_order: integer
- created_at: timestamptz

### academic_publications (user_id: TEXT)
- id: uuid (PK)
- user_id: text (NOT NULL)
- pub_type: text (NOT NULL)
- title: text (NOT NULL)
- authors: ARRAY
- publication_venue: text
- year: integer
- doi: text
- url: text
- sort_order: integer
- created_at: timestamptz

## Missing Data

- 4 more experiences (have 15, need 19)
- 1 more education (have 1, need 2)
- 19 more skills (have 18, need 37)
- 4 more CVs (have 4, need 8)
- 7 awards (have 0)
- 4 volunteer (have 0)
- 8 CV branscher (have 0)
