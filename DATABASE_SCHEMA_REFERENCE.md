# Database Schema Reference - Anti-Apathy Job Portal v2

**Complete column information for all Supabase tables**

Last updated: 2026-02-16

---

## Core Tables

### `jobs`
Scraped job listings from Platsbanken

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique job identifier |
| title | TEXT | NOT NULL | Job title |
| company | TEXT | | Company name |
| location | TEXT | | Job location/city |
| description | TEXT | | Full job description |
| url | TEXT | | Job posting URL |
| deadline | TIMESTAMPTZ | | Application deadline |
| priority | TEXT | DEFAULT 'normal' | Job priority level |
| contact_email | TEXT | | Recruiter email address |
| contact_name | TEXT | | Contact person name |
| source | TEXT | DEFAULT 'platsbanken' | Job source |
| scraped_at | TIMESTAMPTZ | DEFAULT NOW() | When job was scraped |
| link_status | TEXT | DEFAULT 'active' | Link status |

**Indexes:**
- `idx_jobs_scraped_at` on scraped_at DESC
- `idx_jobs_priority` on priority
- `idx_jobs_contact_email` on contact_email WHERE contact_email IS NOT NULL

---

### `user_profiles`
User profile with personal info and photo

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Profile ID |
| user_id | TEXT | NOT NULL UNIQUE | User identifier (Supabase Auth ID) |
| full_name | TEXT | NOT NULL | Full name |
| email | TEXT | | Email address |
| phone | TEXT | | Phone number |
| location | TEXT | | City/location |
| photo_url | TEXT | | Supabase Storage URL for photo |
| drivers_license | BOOLEAN | DEFAULT FALSE | Has driver's license |
| languages | TEXT[] | DEFAULT ARRAY['Svenska (Modersmål)', 'Engelska (flytande)']::TEXT[] | Languages spoken |
| certificates | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Certificates (e.g., 'B-körkort', 'ICA kassahantering') |
| about_me | TEXT | | Professional bio/summary |
| onboarding_completed | BOOLEAN | DEFAULT FALSE | Onboarding status |
| privacy_policy_accepted | BOOLEAN | DEFAULT FALSE | Privacy policy acceptance |
| data_consent_given_at | TIMESTAMPTZ | | When consent was given |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Profile creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

---

## User Preference Tables

### `user_cv_branscher`
User-defined CV industries/categories (replaces hard-coded CV_VIBES)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Bransch ID |
| user_id | TEXT | NOT NULL | User identifier |
| bransch_id | TEXT | NOT NULL | User-defined slug (e.g., 'restaurant', 'tattoo') |
| bransch_name | TEXT | NOT NULL | Display name (e.g., 'Restaurang & Café') |
| emoji | TEXT | | Emoji for bransch (e.g., '🍽️') |
| focus | TEXT | | What to emphasize for this bransch |
| keywords | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Job search keywords |
| is_active | BOOLEAN | DEFAULT TRUE | Whether bransch is active |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

**Constraints:**
- UNIQUE(user_id, bransch_id)

**Indexes:**
- `idx_user_cv_branscher_user` on user_id

---

### `user_cover_letter_preferences`
Per-user cover letter style and content preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | TEXT | PRIMARY KEY | User identifier |
| tone | TEXT | DEFAULT 'professional_friendly' | Tone style ('formal', 'casual', 'warm') |
| max_words | INT | DEFAULT 200 | Max word count for cover letters |
| greeting_style | TEXT | DEFAULT 'Hej!' | Greeting format |
| signature_style | TEXT | DEFAULT 'Med vänliga hälsningar' | Signature closing |
| sign_off_name | TEXT | | Full name for signature |
| sign_off_phone | TEXT | | Phone number in signature |
| sign_off_email | TEXT | | Email in signature |
| always_mention | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Things to always mention (e.g., 'flexibel med tider', 'körkort') |
| never_mention | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Things to never mention (e.g., 'konst', 'Shopify') |
| priority_experiences_per_vibe | JSONB | | Priority experiences per vibe: {"restaurant": ["Max Hamburgare"], "tech": ["Clubhouse"]} |
| custom_ai_instructions | TEXT | | Free-form additional AI instructions |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

---

### `user_job_preferences`
Per-user job search filters and preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | TEXT | PRIMARY KEY | User identifier |
| preferred_locations | TEXT[] | DEFAULT ARRAY['Stockholm']::TEXT[] | Preferred job locations |
| search_keywords | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Job search keywords |
| excluded_keywords | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Keywords to exclude |
| excluded_companies | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Companies to exclude |
| job_types | TEXT[] | DEFAULT ARRAY['heltid', 'deltid']::TEXT[] | Job types (full-time, part-time) |
| min_hours_per_week | INT | | Minimum hours per week |
| max_commute_minutes | INT | | Maximum commute time |
| remote_only | BOOLEAN | DEFAULT FALSE | Only remote jobs |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

---

### `user_ai_feedback`
User feedback to AI for learning their preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Feedback ID |
| user_id | TEXT | NOT NULL | User identifier |
| feedback_type | TEXT | DEFAULT 'cover_letter' | Type: 'cover_letter', 'new_bransch_request', 'exclude_jobs', 'general' |
| feedback_text | TEXT | NOT NULL | Feedback text (Swedish or English) |
| applies_to_branscher | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Which branscher this applies to (empty = all) |
| excluded_keywords | TEXT[] | DEFAULT ARRAY[]::TEXT[] | For exclude_jobs: keywords to filter out |
| is_active | BOOLEAN | DEFAULT TRUE | Whether feedback is active |
| is_processed | BOOLEAN | DEFAULT FALSE | Whether AI has processed this |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

**Indexes:**
- `idx_user_ai_feedback_user` on user_id

---

## User Data Tables

### `user_education`
Education entries (same for all CV vibes)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Education ID |
| user_id | TEXT | NOT NULL | User identifier |
| school | TEXT | NOT NULL | School/university name |
| location | TEXT | | School location |
| degree | TEXT | | Degree/program name |
| dates | TEXT | | Date range (e.g., 'Aug 2017 - Maj 2021') |
| bullets | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Bullet points |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `user_experiences`
Work experience entries (tagged with categories)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Experience ID |
| user_id | TEXT | NOT NULL | User identifier |
| company | TEXT | NOT NULL | Company name |
| location | TEXT | | Job location |
| title | TEXT | | Job title |
| dates | TEXT | | Date range |
| bullets | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Bullet points |
| categories | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Categories: ['restaurant', 'retail', 'customerservice', 'tech', etc.] |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `user_experience_tags`
Links experiences to branscher with priority

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Tag ID |
| user_id | TEXT | NOT NULL | User identifier |
| experience_id | UUID | REFERENCES user_experiences(id) ON DELETE CASCADE | Experience reference |
| bransch_id | TEXT | NOT NULL | Which CV bransch this is relevant for |
| priority | INT | DEFAULT 5 | Importance for this bransch (1-10) |
| highlight_points | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Specific bullets to emphasize |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

**Constraints:**
- UNIQUE(experience_id, bransch_id)

**Indexes:**
- `idx_user_experience_tags_user` on user_id
- `idx_user_experience_tags_bransch` on bransch_id

---

### `user_volunteer`
Volunteer work (same for all CV vibes)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Volunteer ID |
| user_id | TEXT | NOT NULL | User identifier |
| organization | TEXT | NOT NULL | Organization name |
| dates | TEXT | | Date range |
| bullets | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Bullet points |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `user_awards`
Awards (same for all CV vibes)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Award ID |
| user_id | TEXT | NOT NULL | User identifier |
| award_text | TEXT | NOT NULL | Full award line (e.g., '1:a pris Stockholms Konstsalong 2024 - ...') |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `user_skills`
Skills per category (different vibes show different skills)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Skill ID |
| user_id | TEXT | NOT NULL | User identifier |
| category | TEXT | NOT NULL | Category: 'tech', 'restaurant', 'all', etc. |
| skill_type | TEXT | NOT NULL | Type: 'technical', 'certificate', 'language', 'soft' |
| skill_text | TEXT | NOT NULL | Skill name/description |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

**Constraints:**
- UNIQUE(user_id, category, skill_text)

---

## Industry-Specific CV Sections

### `artist_exhibitions`
Artist CV: Exhibitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Exhibition ID |
| user_id | TEXT | NOT NULL | User identifier |
| exhibition_type | TEXT | NOT NULL | Type: 'solo', 'group', 'juried' |
| title | TEXT | | Exhibition title |
| venue | TEXT | NOT NULL | Venue name |
| city | TEXT | | City |
| country | TEXT | | Country |
| year | INT | | Year |
| notes | TEXT | | Additional notes (e.g., 'Vann 1:a pris') |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `artist_residencies`
Artist CV: Residencies & Grants

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Residency ID |
| user_id | TEXT | NOT NULL | User identifier |
| entry_type | TEXT | NOT NULL | Type: 'residency', 'grant', 'fellowship' |
| name | TEXT | NOT NULL | Residency/grant name |
| organization | TEXT | | Organization |
| location | TEXT | | Location |
| year | INT | | Year |
| notes | TEXT | | Additional notes |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `artist_collections`
Artist CV: Collections (where work is held)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Collection ID |
| user_id | TEXT | NOT NULL | User identifier |
| collection_name | TEXT | NOT NULL | Collection name |
| location | TEXT | | Location |
| year_acquired | INT | | Year acquired |
| notes | TEXT | | Additional notes |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `tech_projects`
Tech CV: Projects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Project ID |
| user_id | TEXT | NOT NULL | User identifier |
| project_name | TEXT | NOT NULL | Project name |
| description | TEXT | | Project description |
| tech_stack | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Technologies used (e.g., ['React', 'Python', 'PostgreSQL']) |
| github_url | TEXT | | GitHub URL |
| live_url | TEXT | | Live demo URL |
| year | INT | | Year completed |
| highlights | TEXT[] | DEFAULT ARRAY[]::TEXT[] | Bullet points |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `tech_certifications`
Tech CV: Certifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Certification ID |
| user_id | TEXT | NOT NULL | User identifier |
| certification_name | TEXT | NOT NULL | Certification name |
| issuer | TEXT | | Issuer (e.g., 'AWS', 'Google', 'Microsoft') |
| year_obtained | INT | | Year obtained |
| expiry_year | INT | | Year it expires |
| credential_url | TEXT | | Credential verification URL |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

### `academic_publications`
Academic CV: Publications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Publication ID |
| user_id | TEXT | NOT NULL | User identifier |
| pub_type | TEXT | NOT NULL | Type: 'journal', 'conference', 'book_chapter', 'thesis' |
| title | TEXT | NOT NULL | Publication title |
| authors | TEXT[] | DEFAULT ARRAY[]::TEXT[] | List of author names |
| publication_venue | TEXT | | Journal/conference name |
| year | INT | | Year published |
| doi | TEXT | | DOI identifier |
| url | TEXT | | Publication URL |
| sort_order | INT | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

---

## CV Management Tables

### `cv_industry_templates`
Defines which sections to use for different CV types

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Template ID: 'traditional', 'artist', 'tech', 'academic', 'police' |
| name | TEXT | NOT NULL | Template name |
| description | TEXT | | Template description |
| sections | JSONB | NOT NULL | Ordered list of section configs |
| example_roles | TEXT[] | | Example job roles (e.g., ['Konstnär', 'Gallerist', 'Curator']) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |

**Default Templates:**
- `traditional`: Standard CV for service, retail, office jobs
- `artist`: CV for visual artists with exhibitions and residencies
- `tech`: CV for developers and IT professionals
- `academic`: CV for researchers and academics

---

### `master_cv_exports`
Complete snapshot of all user data as JSON (the "master file")

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Export ID |
| user_id | TEXT | NOT NULL | User identifier |
| export_data | JSONB | NOT NULL | Complete CV data as JSON |
| version | INT | DEFAULT 1 | Version number |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Export time |
| notes | TEXT | | Optional notes about this version |

**Indexes:**
- `idx_master_cv_exports_user` on user_id

---

### `user_cvs`
Generated CV versions (different "vibes")

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | CV ID |
| user_id | TEXT | NOT NULL | User identifier |
| vibe_id | TEXT | NOT NULL | Vibe identifier ('restaurant', 'tech', 'retail', etc.) |
| vibe_name | TEXT | | Display name for vibe |
| vibe_emoji | TEXT | | Emoji for vibe |
| cv_text | TEXT | NOT NULL | Generated CV text/content |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

**Constraints:**
- UNIQUE(user_id, vibe_id)

**Indexes:**
- `idx_user_cvs_user` on user_id
- `idx_user_cvs_vibe` on (user_id, vibe_id)

---

## Integration Tables

### `user_google_credentials`
User's Google Cloud credentials (each user brings their own)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Credential ID |
| user_id | TEXT | NOT NULL UNIQUE | User identifier |
| google_client_id | TEXT | NOT NULL | Google OAuth client ID |
| google_client_secret | TEXT | NOT NULL | Google OAuth client secret |
| access_token | TEXT | | OAuth access token |
| refresh_token | TEXT | | OAuth refresh token |
| token_expires_at | TIMESTAMPTZ | | Token expiration time |
| gmail_address | TEXT | | User's Gmail address after OAuth |
| is_connected | BOOLEAN | DEFAULT FALSE | Connection status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

---

## Application Tracking

### `applications`
Job applications with status tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | Application ID |
| user_id | TEXT | DEFAULT 'default_user' | User identifier |
| job_id | TEXT | REFERENCES jobs(id) | Job reference |
| cv_id | UUID | REFERENCES user_cvs(id) | CV used for application |
| bransch_id | TEXT | | Which bransch CV was used |
| cover_letter | TEXT | | Generated cover letter |
| status | TEXT | DEFAULT 'draft' | Status: 'draft', 'sent', 'skipped', 'saved', 'interview', 'rejected', 'offer' |
| gmail_draft_id | TEXT | | Gmail draft identifier |
| gmail_message_id | TEXT | | Gmail message ID after sending |
| notes | TEXT | | Application notes |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |
| sent_at | TIMESTAMPTZ | | When application was sent |
| response_at | TIMESTAMPTZ | | When company responded |

**Constraints:**
- UNIQUE(user_id, job_id) - One application per job per user

**Indexes:**
- `idx_applications_user` on user_id
- `idx_applications_status` on status

**Status Options:**
- `draft` - Saved as Gmail draft, not sent yet
- `sent` - Application sent
- `skipped` - User doesn't want this job (won't show again)
- `saved` - Saved for later (will show again)
- `interview` - Got interview
- `rejected` - Got rejection
- `offer` - Got job offer!

---

## Database Functions

### `export_master_cv(p_user_id TEXT)`
Returns JSONB containing complete CV data for a user

**Returns:**
```json
{
  "user_id": "...",
  "exported_at": "...",
  "profile": {...},
  "education": [...],
  "experiences": [...],
  "volunteer": [...],
  "awards": [...],
  "skills": [...]
}
```

---

### `save_master_cv_snapshot(p_user_id TEXT, p_notes TEXT DEFAULT NULL)`
Creates a versioned snapshot of user's CV data

**Returns:** UUID of the new master_cv_exports record

---

## Linnea's User ID

```
da8ed517-3b67-4456-8831-6ed3cb7114ad
```

Use this user_id for all Linnea's data in the migration files.

---

## Row Level Security (RLS)

Currently disabled. When enabled, use these policies:

```sql
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid()::text = user_id);
```

---

## Table Count Summary

**Total Tables:** 23

- Core: 2 (jobs, user_profiles)
- User Preferences: 4 (cv_branscher, cover_letter_prefs, job_prefs, ai_feedback)
- User Data: 6 (education, experiences, experience_tags, volunteer, awards, skills)
- Industry-Specific: 6 (artist_exhibitions, artist_residencies, artist_collections, tech_projects, tech_certifications, academic_publications)
- CV Management: 3 (cv_industry_templates, master_cv_exports, user_cvs)
- Integration: 1 (user_google_credentials)
- Application Tracking: 1 (applications)

---

**Source Files:**
- Schema: `v2/supabase_schema.sql`
- Migration: `v2/migrate_complete_data.sql`
