# Database Setup Guide

## Quick Start: Run These Migrations In Order

### Step 1: Restore Complete User Data
**File:** `v2/supabase/migrations/COMPLETE_REAL_DATA.sql`

This restores all user data:
- ✅ 19 work experiences
- ✅ 2 education entries
- ✅ 37 skills
- ✅ 7 awards
- ✅ 4 volunteer entries
- ✅ 8 CV branscher (categories)
- ✅ Cover letter preferences
- ✅ Job preferences

**Run this first** to restore your complete profile data.

---

### Step 2: Add Modularity System Tables
**File:** `v2/supabase/migrations/add_modularity_tables.sql`

This creates new tables for the modular CV system:
- ✅ `tech_certifications` (DataCamp, Coursera, etc.)
- ✅ `tech_projects` (Portfolio projects with live URLs)
- ✅ `user_certifications` (Work certs: ICA, Trygga mat, etc.)
- ✅ `user_cv_versions` (Version history for conversational CV creation)
- ✅ `user_cv_creation_conversations` (Conversation logs)
- ✅ New columns in `user_cvs` table (is_ai_generated, times_used, etc.)

**Run this second** to add the modular system.

---

### Step 3: Add Tech Profile Data
**File:** `v2/supabase/migrations/insert_linnea_complete_cv_data.sql`

This adds tech-focused data:
- ✅ 4 education entries (expands from 2 to 4)
- ✅ 7 DataCamp/Google/Udemy certifications
- ✅ 11 production tech projects with live URLs
- ✅ 30+ additional tech skills (TypeScript, Next.js, APIs, etc.)
- ✅ 2 additional awards

**Run this third** to complete your tech profile.

---

## After Running All Migrations

Verify your data at:
```
https://platsbanken-ai.vercel.app/api/admin/user/linneamoritzcv@gmail.com
```

You should see:
- **education:** 4
- **experiences:** 19
- **skills:** 50+
- **awards:** 9
- **tech_certifications:** 7
- **tech_projects:** 11
- **cvs:** 8
- **volunteer:** 4

---

## Storage Buckets

The app uses three Supabase Storage buckets:

### 1. `cv-files`
- Stores uploaded CV PDFs
- Path: `{user_id}/{vibe_id}_cv.pdf`
- Public access
- Endpoint: `POST /api/upload/cv/{vibe_id}`

### 2. `profile-photos`
- Stores user profile pictures
- Path: `{user_id}/profile.{jpg|png}`
- Public access
- Endpoint: `POST /api/upload/profile-photo`

### 3. `training-letters`
- Stores example cover letters for tone analysis
- Path: `{user_id}/training_letter.pdf`
- Private access
- Endpoint: `POST /api/upload/training-letter`

---

## Modular CV System

### Base CVs (8 templates)
These are stored in `user_cvs` table with `is_ai_generated = FALSE`:

1. **restaurant** - Restaurang & Café
2. **retail** - Butik & Kassa
3. **customerservice** - Kundtjänst & Support
4. **contentmoderation** - Content Moderation
5. **healthcare** - Vård & Omsorg
6. **tech** - Tech & Kontor
7. **industry** - Industri & Trädgård
8. **art** - Konst & Kultur

### Application CVs (infinite, never saved)
When a user applies to a job:
1. AI analyzes job description
2. Selects appropriate base CV (e.g., "restaurant")
3. Customizes **IN MEMORY** (adds relevant experiences/projects)
4. Creates Gmail draft with customized CV
5. **Never saves** customized version to database

**Cost:** $0 (just text manipulation, no API call needed)

### When to Create New Base CV
Only when:
1. User explicitly requests: *"Create a software developer CV"*
2. AI detects pattern: *User applied to 20 luxury hotels → suggest "Luxury Hospitality CV"*
3. New job category with no existing match

Then use conversational flow (saved in `user_cv_creation_conversations`).

---

## Quick Links

- **Supabase Dashboard:** [https://supabase.com/dashboard](https://supabase.com/dashboard)
- **Vercel Dashboard:** [https://vercel.com/linneamoritznyc/platsbanken-ai](https://vercel.com/linneamoritznyc/platsbanken-ai)
- **Admin API:** [https://platsbanken-ai.vercel.app/api/admin/user/linneamoritzcv@gmail.com](https://platsbanken-ai.vercel.app/api/admin/user/linneamoritzcv@gmail.com)
