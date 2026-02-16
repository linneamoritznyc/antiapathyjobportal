# Supabase Database Schema - Anti-Apathy Job Portal

**Last Updated:** 2026-02-16
**Linnea's User ID:** `da8ed517-3b67-4456-8831-6ed3cb7114ad`

## Current Data Status (as of 2026-02-16)

| Table                         | Row Count | Status      | Notes                          |
|-------------------------------|-----------|-------------|--------------------------------|
| user_profiles                 | 1         | ✅ Complete | Linnea's profile exists        |
| user_experiences              | 15        | ⚠️ Partial  | Has 15/19 positions            |
| user_education                | 1         | ⚠️ Partial  | Has 1/2 education entries      |
| user_skills                   | 18        | ⚠️ Partial  | Has 18/28 skills               |
| user_awards                   | 0         | ❌ Empty    | Needs 7 awards                 |
| user_volunteer                | 0         | ❌ Empty    | Needs 4 volunteer entries      |
| user_cv_branscher             | 0         | ❌ Empty    | Needs 8 CV categories          |
| user_cvs                      | 4         | ⚠️ Partial  | Has 4/8 CV variants            |
| user_cover_letter_preferences | ?         | Unknown     | Needs verification             |

## Schema Structure

### user_profiles
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `full_name` (text)
- `email` (text)
- `phone` (text)
- `location` (text)
- `drivers_license` (boolean)
- `languages` (text[])
- `created_at` (timestamptz)

### user_experiences
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `company` (text, NOT NULL)
- `title` (text, NOT NULL)
- `start_date` (text) ← **TEXT not DATE**
- `end_date` (text)
- `description` (text)
- `categories` (text[])
- `sort_order` (integer)

### user_education
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `school` (text, NOT NULL)
- `degree` (text)
- `field_of_study` (text)
- `location` (text)
- `start_date` (text) ← **TEXT not DATE**
- `end_date` (text)

### user_skills
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `category` (text)
- `skill_type` (text)
- `skill_text` (text, NOT NULL)

### user_awards
- `id` (uuid, PK)
- `user_id` (text, NOT NULL) ← **TEXT TYPE** (inconsistent!)
- `award_text` (text, NOT NULL)
- `sort_order` (integer)
- `created_at` (timestamptz)

### user_volunteer
- `id` (uuid, PK)
- `user_id` (text, NOT NULL) ← **TEXT TYPE** (inconsistent!)
- `organization` (text, NOT NULL)
- `dates` (text)
- `bullets` (text[])
- `sort_order` (integer)
- `created_at` (timestamptz)

### user_cv_branscher
- `id` (uuid, PK)
- `user_id` (text, NOT NULL) ← **TEXT TYPE** (inconsistent!)
- `bransch_id` (text, NOT NULL)
- `bransch_name` (text, NOT NULL)
- `emoji` (text)
- `focus` (text)
- `keywords` (text[])
- `is_active` (boolean)
- `sort_order` (integer)
- `created_at` (timestamptz)

### user_cvs
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `vibe_id` (text, NOT NULL)
- `vibe_name` (text)
- `cv_text` (text)

### user_cover_letter_preferences
- `id` (uuid, PK)
- `user_id` (uuid, NOT NULL) ← **UUID TYPE**
- `tone` (text)
- `max_words` (integer)
- `greeting_style` (text)
- `signature_style` (text)
- `always_mention` (text[])
- `never_mention` (text[])
- `priority_jobs` (jsonb)

### applications
- `id` (uuid, PK)
- `user_id` (uuid) ← **UUID TYPE**
- `job_id` (text)
- `cover_letter` (text)
- `status` (text)
- `created_at` (timestamptz)

## CRITICAL NOTES

### user_id Type Inconsistency
⚠️ **The database has MIXED user_id types:**

**UUID columns:**
- user_profiles
- user_experiences
- user_education
- user_skills
- user_cvs
- user_cover_letter_preferences
- applications

**TEXT columns:**
- user_awards
- user_volunteer
- user_cv_branscher

**For Linnea's data:**
- UUID fields: Use `'da8ed517-3b67-4456-8831-6ed3cb7114ad'::uuid`
- TEXT fields: Use `'da8ed517-3b67-4456-8831-6ed3cb7114ad'` (already text format)

### Date Fields
- All date fields use TEXT, not DATE or TIMESTAMP
- Format: 'Juni 2022', 'Augusti 2023', '2013', '2016', etc.

## Next Actions

1. ✅ Insert missing awards (7 entries)
2. ✅ Insert missing volunteer work (4 entries)
3. ✅ Insert missing CV branscher (8 entries)
4. ⚠️ Check and insert missing experiences (4 missing)
5. ⚠️ Check and insert missing education (1 missing)
6. ⚠️ Check and insert missing skills (10 missing)
7. ⚠️ Check cover letter preferences status
