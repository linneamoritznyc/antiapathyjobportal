# Supabase Schema Reference

**CRITICAL: Use this as the source of truth when writing migrations!**

## Core Tables

### user_profiles
```sql
user_id TEXT PRIMARY KEY
full_name TEXT
email TEXT
phone TEXT
location TEXT
photo_url TEXT
drivers_license BOOLEAN
languages TEXT[]
certificates TEXT[]
about_me TEXT
onboarding_completed BOOLEAN
privacy_policy_accepted BOOLEAN
data_consent_given_at TIMESTAMPTZ
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

### user_education
```sql
id UUID PRIMARY KEY
user_id TEXT
school TEXT              -- NOT "institution"!
location TEXT
degree TEXT
dates TEXT               -- NOT start_date/end_date! Format: 'Aug 2017 - Maj 2021'
bullets TEXT[]           -- NOT "description"!
sort_order INT
created_at TIMESTAMPTZ
```

### user_experiences
```sql
id UUID PRIMARY KEY
user_id TEXT
company TEXT
location TEXT
title TEXT
dates TEXT               -- NOT start_date/end_date!
bullets TEXT[]           -- NOT "description"!
categories TEXT[]        -- ['restaurant', 'retail', 'tech', etc.]
sort_order INT
created_at TIMESTAMPTZ
```

### user_skills
```sql
id UUID PRIMARY KEY
user_id TEXT
category TEXT           -- 'tech', 'restaurant', 'all', etc.
skill_type TEXT         -- 'technical', 'certificate', 'language'
skill_text TEXT         -- NOT "skill_name"!
created_at TIMESTAMPTZ
UNIQUE(user_id, category, skill_text)
```

### user_awards
```sql
id UUID PRIMARY KEY
user_id TEXT
award_text TEXT         -- Full award line, NOT separate columns!
sort_order INT
created_at TIMESTAMPTZ
```

### user_volunteer
```sql
id UUID PRIMARY KEY
user_id TEXT
organization TEXT
dates TEXT              -- NOT start_date/end_date!
bullets TEXT[]
sort_order INT
created_at TIMESTAMPTZ
```

### user_cvs
```sql
id UUID PRIMARY KEY
user_id TEXT
vibe_id TEXT           -- NOT "bransch"! e.g., 'restaurant', 'tech'
vibe_name TEXT
vibe_emoji TEXT
cv_text TEXT           -- NOT "cv_content"!
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
UNIQUE(user_id, vibe_id)
```

### user_cv_branscher
```sql
id UUID PRIMARY KEY
user_id TEXT
bransch_id TEXT        -- user-defined slug
bransch_name TEXT      -- display name
emoji TEXT
focus TEXT
keywords TEXT[]
is_active BOOLEAN
sort_order INT
created_at TIMESTAMPTZ
UNIQUE(user_id, bransch_id)
```

### user_cover_letter_preferences
```sql
user_id TEXT PRIMARY KEY
tone TEXT
max_words INT
greeting_style TEXT
signature_style TEXT
sign_off_name TEXT
sign_off_phone TEXT
sign_off_email TEXT
always_mention TEXT[]
never_mention TEXT[]
priority_experiences_per_vibe JSONB
custom_ai_instructions TEXT
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

### user_job_preferences
```sql
user_id TEXT PRIMARY KEY
preferred_locations TEXT[]
search_keywords TEXT[]
excluded_keywords TEXT[]
excluded_companies TEXT[]
job_types TEXT[]
min_hours_per_week INT
max_commute_minutes INT
remote_only BOOLEAN
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

## Key Differences from Common Patterns

1. **dates** is TEXT, not start_date/end_date
2. **bullets** is TEXT[], not description TEXT
3. **school** not "institution"
4. **award_text** is full text, not separate columns
5. **skill_text** not "skill_name"
6. **vibe_id** not "bransch" in user_cvs
7. **cv_text** not "cv_content"
8. **user_id** is TEXT (not UUID) for all tables

---

**Last updated:** 2026-02-16
