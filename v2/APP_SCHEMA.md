# Anti-Apathy Job Portal v2 — App Schema

Quick reference for Claude Code. Read this before touching anything.

---

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Single-file React (no build step) — `v2/frontend.html` |
| Backend | FastAPI — `v2/api/index.py`, deployed on Vercel |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (JWT tokens in `localStorage` as `auth_token`) |
| Storage | Supabase Storage (profile photos, CV PDFs, training letters) |
| AI | Anthropic Claude API (cover letters, CV generation) |
| Email | Gmail OAuth (creates drafts, does NOT auto-send) |

---

## File Map

```
v2/
├── frontend.html          ← MAIN frontend (React + Tailwind, single file)
├── api/
│   └── index.py           ← MAIN backend (FastAPI, all endpoints)
├── supabase_schema.sql    ← Source of truth for DB schema
├── APP_SCHEMA.md          ← This file
└── api/cv_files/          ← 8 industry PDF CVs (attached to Gmail drafts)
```

**Do not touch:** `v1/`, `fix_my_backend.py`, `api_server_updated.py`, `Olika CV/`

---

## Frontend Pages (tabs in NavTabs)

| Tab ID | Label | Component | What it does |
|--------|-------|-----------|--------------|
| `jobs` | Jobb | `JobsPage` | Search + browse scraped jobs, apply |
| `cvs` | Mina CV | `MinaCVPage` | View Master CV data + bransch CVs |
| `applications` | Ansökningar | `ApplicationsPage` | Track all applications |
| `metrics` | Statistik | inline | Stats dashboard |
| `preferences` | Preferenser | `PreferencesPage` | Job search filters |
| `letter` | Personligt brev | `LetterPreferencesPage` | Cover letter style settings |
| `quiz` | Quiz | `QuizPage` | Onboarding quiz |
| `profil` | Profil | `ProfilPage` | Profile photo + CV uploads |

**Auth flow:** `login.html` → Supabase auth → `frontend.html` (token in localStorage)

---

## Backend API Endpoints

### Jobs
| Method | Path | What it does |
|--------|------|-------------|
| POST | `/api/scrape` | Scrape Platsbanken, save to DB |
| GET | `/api/jobs` | List jobs from DB |
| POST | `/api/jobs/{id}/letter` | Generate cover letter via Claude |
| POST | `/api/jobs/{id}/apply-with-cv` | Generate letter + create Gmail draft |
| POST | `/api/jobs/{id}/save` | Save job for later |

### CV
| Method | Path | What it does |
|--------|------|-------------|
| GET | `/api/master-cv` | Get all CV data (experiences, education, skills, etc.) |
| POST | `/api/cv/master` | Save Master CV from quiz |
| GET | `/api/cv/all` | Get user's generated CV vibes |
| GET | `/api/bransch-cvs` | Get industry-specific CVs |
| POST | `/api/cv/generate-branscher` | Generate CV text for all industries via Claude |
| GET | `/api/master-cv/download-pdf` | Download Master CV as PDF |

### Auth / Profile
| Method | Path | What it does |
|--------|------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/profile` | Get profile + photo URL + cv_count |
| POST | `/api/upload/profile-photo` | Upload profile photo to Supabase Storage |

### Applications
| Method | Path | What it does |
|--------|------|-------------|
| GET | `/api/applications` | List all applications |
| PATCH | `/api/applications/{id}` | Update status |
| DELETE | `/api/applications/{id}` | Delete application |

---

## Database Tables (key ones)

| Table | Purpose |
|-------|---------|
| `jobs` | Scraped jobs from Platsbanken |
| `applications` | Job applications with status tracking |
| `user_profiles` | Personal info, photo URL |
| `user_experiences` | Work history (27 entries for Linnea) — has AI tags |
| `user_education` | Education history (4 entries) |
| `user_skills` | Skills by category + type |
| `user_awards` | Awards/prizes |
| `user_certifications` | General certs (körkort, ICA, etc.) |
| `tech_certifications` | Tech certs with credential URLs |
| `tech_projects` | Portfolio projects (11 entries) |
| `user_volunteer` | Volunteer work (8 entries) |
| `user_cv_branscher` | User-defined industry CV categories |
| `bransch_cvs` | Generated CV text per industry |
| `user_cover_letter_preferences` | Cover letter tone/style settings |
| `user_job_preferences` | Job search filters |
| `user_cv_uploads` | Uploaded CV PDFs (max 20) |
| `user_training_letters` | Training letters for AI style analysis |

**Current user:** Linnea Moritz — `da8ed517-3b67-4456-8831-6ed3cb7114ad`

---

## Key Field Names (common source of bugs)

| Table | Field | NOT |
|-------|-------|-----|
| `user_awards` | `award_text` | ~~award_name~~ |
| `user_volunteer` | `organization` | ~~organization_name~~ |
| `user_skills` | `skill_text` | ~~skill_name~~ |
| `user_certifications` | `issuing_organization` | ~~organization~~ |
| `tech_certifications` | `issuer` | ~~organization~~ |
| `user_education` | `dates` (combined string) | use `dates` not `start_date`+`end_date` (those may be null) |
| `user_experiences` | `categories` (TEXT[]) | array, not string |
| `tech_projects` | `tech_stack` (TEXT[]) | array — join before display |

---

## Core App Flow

```
1. Scrape Platsbanken → jobs saved to DB
2. User browses jobs in JobsPage
3. Click "Ansök" → Claude generates cover letter
4. Match job to best industry CV (detect_job_category)
5. Create Gmail draft with cover letter + CV PDF attached
6. User reviews draft in Gmail, sends manually
```

---

## Industry CV Categories

`restaurant` | `retail` | `industry` | `healthcare` | `tech` | `customerservice` | `reception` | `contentmoderation` | `art`

Each maps to a PDF in `v2/api/cv_files/`.

---

## Supabase Storage Buckets

| Bucket | Path pattern | Used for |
|--------|-------------|---------|
| `profile-photos` | `{user_id}/profile.{ext}` | Profile photo |
| `cv-files` | `{user_id}/cv_{timestamp}.{ext}` | Uploaded CV PDFs |
| `training-letters` | `{user_id}/letter_{timestamp}.{ext}` | AI style training letters |

---

## Rules (from CLAUDE.md)

- All UI text in **Swedish**
- Never mention art, painting, exhibitions, or Shopify in generated content
- Gmail drafts go to `linneamoritzcv@gmail.com`
- Never push to `v2/` without explicit instruction
- DB changes: give SQL to run in Supabase SQL Editor, update `supabase_schema.sql`
- Don't create migration files in the repo
