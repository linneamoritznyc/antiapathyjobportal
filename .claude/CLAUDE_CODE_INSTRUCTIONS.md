# CLAUDE CODE INSTRUCTIONS - Anti-Apathy Job Portal

**Generated:** 2026-02-16
**Purpose:** Complete codebase reference for all future Claude Code sessions
**Status:** Comprehensive analysis based on complete file reading

---

## EXECUTIVE SUMMARY

**What this app is:**
AI-powered job application automation for neurodivergent job seekers in Sweden. Scrapes Platsbanken, generates personalized cover letters via Claude API, auto-selects industry-matched CVs, and creates Gmail drafts.

**Current state:**
- **v1 (Local):** SQLite + FastAPI + React HTML - Active development version
- **v2 (Deployed):** Supabase PostgreSQL + Vercel + Next.js API routes - Production at https://platsbanken-ai.vercel.app
- **User:** Linnea Moritz (solo user, neurodivergent/ADHD)
- **Market:** Swedish job market (Platsbanken integration)

**Critical constraints:**
- All UI text must be in Swedish
- Never mention: art, painting, exhibitions, Shopify in generated content
- CV categories: restaurant, retail, industry, healthcare, tech, customerservice, reception, contentmoderation, art
- Gmail: linneamoritzCV@gmail.com

---

## FILES IN THIS REPO

### Complete File Inventory

**Documentation (.md files) - 22 files:**
```
.claude/
├── CLAUDE.md                    # Project instructions (checked into repo)
├── START_HERE.md                # Session start guide
├── INDEX.md                     # Task-based doc navigation
└── CODEBASE_AUDIT.md            # Doc accuracy audit

Root:
├── SECURITY.md                  # 30 security tips for vibe-coded apps
├── CURRENT_TASK.md              # What to work on right now
├── CLAUDE_CODE_MANDATORY_INSTRUCTIONS.md  # Strong warnings about workflow
├── CLAUDE_CODE_INSTRUCTIONS.md  # Earlier instructions (this file supersedes it)
├── CODEBASE_CLEANUP.md          # File organization guide
├── PROJECT_CONTEXT.md           # One-sentence summary + architecture
├── HANDOFF_2025-02-16.md        # Handoff document
└── app-changes-Feb-8-2026.md    # **SOURCE OF TRUTH for v2 architecture**

docs/
├── GDPR-GUIDE-SVENSKA-APPAR.md  # GDPR compliance checklist (Feb 2026)
└── DESIGN_HISTORY.md            # UI evolution v1 → v2

anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/
├── CHANGELOG.md                 # v1 changelog (OUTDATED)
├── GAP_ANALYSIS.md              # v1 gap analysis (OUTDATED)
├── INDEX.md                     # v1 doc navigation (OUTDATED)
├── NEXT_STEPS.md                # v1 action plan (OUTDATED - contains exposed credentials)
├── PHILOSOPHY.md                # Design philosophy (values valid, tech claims wrong)
├── PROJECT_OVERVIEW.md          # v1 executive summary (OUTDATED)
├── README.md                    # v1 full README (OUTDATED)
└── TECHNICAL_SPEC.md            # v1 technical spec (1,091 lines, OUTDATED)
```

**Database Schema (.sql files) - 5 files:**
```
Root:
└── supabase_schema.sql          # OUTDATED schema (v2/supabase_schema.sql is canonical)

v2/
├── supabase_schema.sql          # **CANONICAL v2 schema**
├── setup_and_migrate.sql        # Initial migration + RLS setup
├── migrate_complete.sql         # Complete data migration script
└── migrate_complete_data.sql    # Data-only migration
```

**Python Backend (.py files) - 13 files:**
```
Root (Active v1):
├── api_server.py                # **ACTIVE** FastAPI server (618 lines)
├── job_portal_backend.py        # **ACTIVE** Business logic (1,150+ lines)
├── config.py                    # Config for api_server_updated.py (NOT USED)
├── auth.py                      # Auth for api_server_updated.py (NOT USED)
├── rate_limit.py                # Rate limit for api_server_updated.py (NOT USED)
├── supabase_helper.py           # Supabase utilities
└── inspect_supabase.py          # DB inspection script

v2/ (Deployed):
├── api/index.py                 # **V2 BACKEND** (3,570 lines, Vercel deployment)
├── finish_cv_sql.py             # CV migration utility
└── migrate_user_data.py         # User data migration utility

api/ (Unclear):
└── index.py                     # Unknown purpose

Legacy:
└── example_direct_integration.py  # Example script
```

**Frontend (.html files) - 15 files:**
```
Root (Active v1):
├── frontend.html                # **ACTIVE** Main React app (3,050 lines)
├── account.html                 # Account settings page (27KB)
├── login.html                   # Login/signup page (25KB)
├── setup-guide.html             # Setup guide
├── anvandarvillkor.html         # Terms of service
├── integritetspolicy.html       # Privacy policy
├── cv_template.html             # CV template
└── inspect_supabase_live.html   # DB inspector

v2/ (Deployed - mirrors):
├── frontend.html                # v2 version
├── account.html
├── login.html
├── setup-guide.html
├── anvandarvillkor.html
├── integritetspolicy.html
└── cv_template.html
```

**Configuration files:**
```
├── requirements.txt             # Root Python deps (may be used by Vercel)
├── v2/requirements.txt          # **CANONICAL** v2 Python deps (pinned versions)
├── vercel.json                  # Vercel deployment config
├── v2/vercel.json               # v2 Vercel config
├── .env.example                 # Environment variables template
└── .gitignore                   # Git ignore rules
```

**Data files:**
```
data/
└── jobs.db                      # SQLite database (auto-created for v1)

CV PDFs (8 industry-specific):
├── CV_Linnea_Moritz_Restaurang_Cafe.pdf
├── CV_Linnea_Moritz_Butik_Kassa.pdf
├── CV_Linnea_Moritz_Kundtjanst.pdf
├── CV_Linnea_Moritz_Tech_Kontor.pdf
├── CV_Linnea_Moritz_Content_Moderation.pdf
├── CV_Linnea_Moritz_Industri_Tradgard.pdf
├── CV_Linnea_Moritz_Vard_Omsorg.pdf
└── CV_Linnea_Moritz_Konst_Kultur.pdf
```

**Deprecated/Legacy (DO NOT USE):**
```
v1/ - Entire directory abandoned
Olika CV/ - Old CV folder with duplicates
fix_my_backend.py - One-shot script (already run)
api_server_updated.py - Experimental, not active
```

---

## WHAT THIS APP ACTUALLY DOES

### v1 (Local Development - ACTIVE)

**Tech Stack:**
- Backend: FastAPI (`api_server.py`) + business logic (`job_portal_backend.py`)
- Frontend: Single-file React app (`frontend.html`) via CDN (no build step)
- Database: SQLite (`data/jobs.db`)
- AI: Anthropic Claude API (Sonnet 4)
- Email: Gmail via IMAP (app password)
- Server: `python3 api_server.py` → localhost:8000

**Core Flow:**
1. **Scrape** → Platsbanken API → Parse → Store in SQLite
2. **Apply** → Detect job category → Select CV PDF → Generate cover letter (Claude) → Create Gmail draft
3. **Track** → Status: pending → letter_generated → draft_saved → sent → interview/rejected

**Key Features:**
- Job scraping from Platsbanken (Swedish national employment service)
- AI cover letter generation (Claude Sonnet 4)
- 8 industry-specific CV PDFs (auto-selected by job category)
- Gmail draft creation via IMAP
- Application tracking (SQLite)
- Swedish UI throughout

### v2 (Production - DEPLOYED on Vercel)

**Tech Stack:**
- Backend: Next.js API routes (`v2/api/index.py` - FastAPI on Vercel)
- Frontend: Same HTML files as v1 but deployed
- Database: Supabase PostgreSQL (aap_ prefixed tables)
- Auth: Supabase Auth (Google OAuth)
- Email: Gmail API (not IMAP)
- URL: https://platsbanken-ai.vercel.app

**Additional Features (v2 only):**
- Multi-user support with authentication
- Row Level Security (RLS) on all user data
- User profiles with CV builder
- Custom CV "branscher" (industry variants)
- Cover letter preference system
- AI feedback learning
- GDPR compliance features (data export, account deletion)

**Architecture Reference:**
v2 is modeled after "Bidragsguiden" (Swedish business grant navigator):
- Dark quiz theme for public pages
- Light dashboard theme for logged-in users
- Freemium usage limits (3 searches/day anonymous, 5/day logged in)
- Google OAuth login
- PDF/TXT/CSV export

---

## DATABASE STRUCTURE

### v1 (SQLite - Local)

**Tables:**
1. **jobs** - Scraped job listings
   - id (TEXT PRIMARY KEY)
   - title, company, location, description, url
   - source, priority, deadline
   - contact_email, contact_name, why_perfect
   - created_at, link_status

2. **applications** - Job applications
   - id (INTEGER PRIMARY KEY)
   - job_id → jobs(id)
   - status, cover_letter, gmail_draft_id
   - sent_at, follow_up_at, notes
   - created_at, updated_at

3. **user_data** - Key-value store
   - key (TEXT PRIMARY KEY)
   - value (TEXT)

4. **daily_stats** - Daily metrics
   - date (TEXT PRIMARY KEY)
   - jobs_scraped, applications_sent, interviews

### v2 (Supabase PostgreSQL - Production)

**Core Tables:**

1. **jobs** - Scraped jobs (same structure as v1 but PostgreSQL)
   - id, title, company, location, description, url
   - deadline, priority, contact_email, contact_name
   - source, scraped_at, link_status

2. **user_profiles** - User accounts
   - id (UUID), user_id (UUID → auth.users)
   - full_name, email, phone, location
   - photo_url, drivers_license, languages[], certificates[]
   - about_me, onboarding_completed
   - privacy_policy_accepted, data_consent_given_at

**CV Management Tables:**

3. **user_cv_branscher** - User-defined CV industries
   - id, user_id, bransch_id (slug), bransch_name
   - emoji, focus, keywords[]
   - is_active, sort_order

4. **user_cvs** - Generated CV versions
   - id, user_id, vibe_id, vibe_name, vibe_emoji
   - cv_text
   - UNIQUE(user_id, vibe_id)

5. **master_cv_exports** - Complete CV snapshots
   - id, user_id, export_data (JSONB)
   - version, notes

**Experience Tables:**

6. **user_experiences** - Work history
   - id, user_id, company, title, location
   - dates, bullets[], categories[]
   - sort_order

7. **user_experience_tags** - Experience → bransch mapping
   - id, user_id, experience_id → user_experiences
   - bransch_id, priority (1-10)
   - highlight_points[]

8. **user_education** - Education entries
   - id, user_id, school, location, degree
   - dates, bullets[], sort_order

9. **user_volunteer** - Volunteer work
   - id, user_id, organization, dates
   - bullets[], sort_order

10. **user_awards** - Awards/recognition
    - id, user_id, award_text, sort_order

11. **user_skills** - Skills per category
    - id, user_id, category, skill_type
    - skill_text

**Industry-Specific Tables:**

12. **artist_exhibitions** - Art exhibitions
    - id, user_id, exhibition_type (solo/group/juried)
    - title, venue, city, country, year, notes

13. **artist_residencies** - Residencies/grants
    - id, user_id, entry_type (residency/grant/fellowship)
    - name, organization, location, year

14. **artist_collections** - Collections holding work
    - id, user_id, collection_name, location
    - year_acquired, notes

15. **tech_projects** - Tech projects
    - id, user_id, project_name, description
    - tech_stack[], github_url, live_url, year

16. **tech_certifications** - Tech certifications
    - id, user_id, certification_name, issuer
    - year_obtained, expiry_year, credential_url

17. **academic_publications** - Academic publications
    - id, user_id, pub_type, title
    - authors[], publication_venue, year, doi, url

**Preference Tables:**

18. **user_cover_letter_preferences** - Cover letter style
    - user_id (PRIMARY KEY)
    - tone, max_words, greeting_style, signature_style
    - sign_off_name, sign_off_phone, sign_off_email
    - always_mention[], never_mention[]
    - priority_experiences_per_vibe (JSONB)
    - custom_ai_instructions

19. **user_job_preferences** - Job search filters
    - user_id (PRIMARY KEY)
    - preferred_locations[], search_keywords[]
    - excluded_keywords[], excluded_companies[]
    - job_types[], min_hours_per_week, max_commute_minutes
    - remote_only

20. **user_ai_feedback** - AI learning from user feedback
    - id, user_id, feedback_type
    - feedback_text, applies_to_branscher[]
    - excluded_keywords[], is_active, is_processed

**Application Tables:**

21. **applications** - Job applications
    - id, user_id, job_id → jobs, cv_id → user_cvs
    - bransch_id, cover_letter, status
    - gmail_draft_id, gmail_message_id, notes
    - sent_at, response_at
    - UNIQUE(user_id, job_id)

22. **user_google_credentials** - User's Gmail OAuth
    - id, user_id
    - google_client_id, google_client_secret
    - access_token, refresh_token, token_expires_at
    - gmail_address, is_connected

**Template Tables:**

23. **cv_industry_templates** - CV template definitions
    - id (TEXT PRIMARY KEY: 'traditional', 'artist', 'tech', 'academic')
    - name, description
    - sections (JSONB - ordered list of section configs)
    - example_roles[]

**Row Level Security (RLS):**
- ALL user tables have RLS enabled
- Users can only access their own data (WHERE auth.uid() = user_id)
- Service role bypasses RLS for admin operations

---

## CURRENT IMPLEMENTATION

### What Works (v1 Local)

**Job Scraping:**
- Platsbanken API integration (`https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search`)
- Search keywords: servitör, trädgård, content moderator, butik, café, etc.
- Location filtering: Stockholm, Sollentuna, Vetlanda, Nässjö, Eksjö, Småland
- Duplicate detection via job ID hashing
- Priority assignment (akut, strategisk)
- Stores in SQLite with metadata

**AI Cover Letter Generation:**
- Uses Anthropic Claude API (Sonnet 4)
- Context includes: job description, company, industry, user profile
- Swedish language output
- Follows "lagom" cultural norms (balanced, not too boastful)
- References specific experiences from CV
- ~200 words, professional but warm tone

**CV Selection:**
- 8 industry-specific PDF CVs
- Auto-detection based on job keywords
- Categories: restaurant, retail, industry, healthcare, tech, customerservice, reception, contentmoderation, art
- Manual override available

**Gmail Draft Creation:**
- IMAP integration (Gmail App Password required)
- Email format:
  - To: job contact email
  - Subject: "Ansökan [Job Title] - Linnea Moritz"
  - Body: "Hej, jag hittade denna tjänst på Platsbanken och vill gärna söka. Se bifogat CV och personligt brev. Vänligen, Linnea Moritz"
  - Attachments: CV PDF + cover letter (text in email body)
- Draft saved to Gmail [Drafts] folder
- User reviews and sends manually

**API Endpoints (v1):**
```
GET  /api/jobs/next              # Get next job to review
GET  /api/jobs                   # List all jobs
GET  /api/jobs/{id}              # Get specific job
POST /api/jobs/{id}/generate-letter  # Generate cover letter
POST /api/jobs/{id}/apply        # Save application
POST /api/jobs/{id}/skip         # Skip job
POST /api/jobs/{id}/create-draft # Create Gmail draft
POST /api/scrape                 # Start scraping (background)
POST /api/scrape/sync            # Scrape synchronously
GET  /api/stats                  # Dashboard statistics
GET  /api/applications           # List all applications
GET  /api/today                  # Today's session stats
POST /api/quick-apply/{id}       # One-click: generate + draft
POST /api/batch-apply            # Batch process multiple jobs
GET  /api/jobs/ready             # Jobs with email addresses
```

### What's Different in v2

**Not in v1 (v2 only):**
- Multi-user authentication (Supabase Auth)
- User profiles with structured data
- Master CV editor (WYSIWYG)
- Custom CV branscher (user-defined)
- Cover letter preference learning
- AI feedback system
- Gmail API (not IMAP)
- Data export/deletion (GDPR)
- Row Level Security

**Frontend Expectations:**
The root `frontend.html` was copied from v2, so it calls some endpoints that don't exist in v1:
- `/api/cv/vibes` - v2 only
- `/api/cv/all` - v2 only
- `/api/cv/master` - v2 only
- `/api/user/preferences` - v2 only
- `/api/user/profile` - v2 only
- `/api/migrate-my-data` - v2 only

These will fail when running locally on v1. Use v2 deployed version for these features.

---

## ARCHITECTURE & CONSTRAINTS

### Deployment Architecture

**Local Development (v1):**
```
Developer Machine
├── SQLite (data/jobs.db)
├── FastAPI (api_server.py on port 8000)
├── React via CDN (frontend.html)
└── Environment variables (.env or export)
```

**Production (v2):**
```
GitHub → Vercel (auto-deploy)
         ├── Next.js API routes (v2/api/index.py)
         ├── Static HTML files
         └── Environment variables (Vercel dashboard)

Supabase Cloud
├── PostgreSQL (aap_ tables)
├── Auth (Google OAuth)
├── Storage (for resume uploads)
└── Row Level Security
```

### Technical Constraints

**v1 Limitations:**
- Single user only (hardcoded Linnea Moritz profile)
- No authentication
- Local SQLite (not multi-device)
- IMAP Gmail (requires app password, less secure than OAuth)
- No automatic backups
- No GDPR compliance features

**v2 Production:**
- Multi-user ready
- Google OAuth authentication
- Cloud PostgreSQL (automatic backups)
- Gmail API with OAuth scopes
- GDPR compliant (data export, deletion, RLS)
- Serverless (auto-scales)

### Environment Variables

**Required for v1:**
```bash
ANTHROPIC_API_KEY=sk-ant-...     # Claude API key
GMAIL_APP_PASSWORD=xxxx-xxxx-... # Gmail app password (16 chars)
```

**Required for v2:**
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhb...
SUPABASE_ANON_KEY=eyJhb...
ANTHROPIC_API_KEY=sk-ant-...
```

### Security Constraints

**From SECURITY.md (30 tips):**
1. Never commit API keys to git
2. Use parameterized queries (SQL injection prevention)
3. Enable CORS only for specific domains (not "*" in production)
4. Rate limit all public endpoints
5. Row Level Security on all Supabase tables
6. Never expose service role key to frontend
7. Validate all user input
8. Use HTTPS only
9. Rotate secrets every 90 days
10. Log all critical actions (audit_log table)

**From GDPR guide:**
- Privacy policy required (Swedish)
- Cookie consent banner (if using analytics)
- Data export functionality (JSON/CSV)
- Account deletion cascade (all user data)
- Data Processing Agreement with Supabase
- EU data residency (Supabase EU region)
- Consent tracking (timestamps)

---

## MANDATORY READING BY TASK TYPE

### Task: Understanding the Project
**Read first:**
1. `app-changes-Feb-8-2026.md` - SOURCE OF TRUTH for v2
2. `.claude/START_HERE.md` - Critical facts
3. `PROJECT_CONTEXT.md` - One-sentence summary
4. `CURRENT_TASK.md` - What to work on now

**Skip:** All files in `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/` (outdated v1 docs)

### Task: Working on Database/Schema
**Read first:**
1. `v2/supabase_schema.sql` - Canonical schema (450 lines)
2. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` - GDPR requirements
3. `app-changes-Feb-8-2026.md` - RLS policies, security

**Skip:** Root `supabase_schema.sql` (outdated)

### Task: Working on API Endpoints
**Read first:**
1. `api_server.py` - Current v1 API (618 lines)
2. `job_portal_backend.py` - Business logic (1,150 lines)
3. `v2/api/index.py` - v2 API if working on production (3,570 lines)

**Note:** If endpoint doesn't exist in v1 but exists in v2, either add to v1 or use v2 deployed version.

### Task: Working on Frontend
**Read first:**
1. `frontend.html` - Main React app (3,050 lines)
2. `app-changes-Feb-8-2026.md` - Design requirements (DM Sans font, no emojis, Swedish UI)
3. `docs/DESIGN_HISTORY.md` - UI evolution

**Note:** Frontend calls some v2-only endpoints. Check API availability before implementing features.

### Task: Working on AI/Cover Letters
**Read first:**
1. `job_portal_backend.py` - LetterGenerator class (around line 500-800)
2. `.claude/CLAUDE.md` - Constraints (never mention art/Shopify)
3. `PHILOSOPHY.md` - Swedish cultural context ("lagom", teamwork focus)

**Critical:** Never mention art, painting, exhibitions, or Shopify in generated content.

### Task: GDPR Compliance
**Read first:**
1. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` - Complete checklist (300 lines)
2. `app-changes-Feb-8-2026.md` - GDPR section
3. Check implementation status in GDPR guide

**Missing in v1:** Data export, privacy policy page, account deletion

### Task: Security Hardening
**Read first:**
1. `SECURITY.md` - 30 security tips
2. `app-changes-Feb-8-2026.md` - RLS policies, service role key handling
3. `.claude/CLAUDE.md` - Key constraints

---

## RULES & REQUIREMENTS

### From .claude/CLAUDE.md

**Active Files ONLY:**
- `api_server.py` - FastAPI server
- `job_portal_backend.py` - Business logic
- `frontend.html` - React app
- `data/jobs.db` - SQLite
- 8 CV PDFs

**DO NOT TOUCH:**
- `v1/` folder - Abandoned
- `fix_my_backend.py` - Already run
- `api_server_updated.py` - Experimental
- `Olika CV/` - Duplicates
- `config.py`, `auth.py`, `rate_limit.py` - Only for api_server_updated.py

**v2 is separate:**
- Don't merge v1 and v2 logic without explicit instruction
- v2 has features v1 doesn't (auth, multi-user, etc.)

**Content Constraints:**
- All UI text in Swedish
- Never mention: art, painting, exhibitions, Shopify
- CV categories must match: restaurant, retail, industry, healthcare, tech, customerservice, reception, contentmoderation, art
- Gmail: linneamoritzCV@gmail.com

### From CLAUDE_CODE_MANDATORY_INSTRUCTIONS.md

**CRITICAL - Environment Limitations:**
- **CANNOT** query Supabase (supabase.co is BLOCKED by proxy)
- **CANNOT** query Vercel endpoints (vercel.app is BLOCKED)
- **CANNOT** curl most external APIs (proxy restrictions)

**CAN DO:**
- Read/write files in GitHub
- Create code that will run on Vercel
- Write SQL for user to run in Supabase
- Commit and push to GitHub

**NEVER:**
- Ask for credentials you can't use
- Suggest local development (Linnea has NO local environment)
- Run commands that require external API access

**Architecture:**
GitHub → Vercel → Supabase (NO LOCAL DEV)

### From CURRENT_TASK.md

**Current Priority:**
Get the core flow working reliably:
1. Job scraping from Platsbanken
2. CV generation (industry-specific matching)
3. Cover letter generation via Claude API
4. Gmail draft creation

**DO NOT:**
- Add new features until basics work
- Refactor or reorganize files right now
- Touch v2/ directory (deployed separately)
- Change CV PDFs
- Add authentication to v1
- Remove hardcoded Linnea Moritz profile from v1

**Success Criteria:**
- [ ] Job scraping returns real jobs
- [ ] CV category detection works
- [ ] Cover letter generation produces good Swedish text
- [ ] Gmail draft creation works (CV + letter attached)
- [ ] Full flow: scrape → pick job → generate → draft

### From PHILOSOPHY.md

**Design Principles:**
- Automate the mechanical, preserve the meaningful
- Neurodivergent-first design (reduce decisions, provide structure)
- Human-in-the-loop (user approves, doesn't just execute)
- Swedish cultural context ("lagom" - balanced, not too boastful)
- Quality over quantity (20 excellent > 100 mediocre)

**UX Goals:**
- Empowered efficiency (in control + productive)
- Reduce cognitive load (one decision at a time)
- Transparent automation (show what's happening)
- Calm technology (work in background, interrupt minimally)

**Anti-Patterns to Avoid:**
- Gamification (job searching isn't a game)
- Aggressive growth hacking (no dark patterns)
- One-size-fits-all (neurodivergent needs differ)
- Feature bloat (more ≠ better)
- Blind automation (always human in loop)

---

## CURRENT STATUS & PRIORITIES

### What Works Right Now

**v1 (Local):**
✅ Job scraping from Platsbanken
✅ SQLite database storage
✅ Cover letter generation (Claude API)
✅ CV selection (8 industry PDFs)
✅ Gmail draft creation (IMAP)
✅ Application tracking
✅ Statistics dashboard
✅ API endpoints functional

**v2 (Production):**
✅ Deployed on Vercel
✅ Supabase PostgreSQL
✅ Google OAuth authentication
✅ Multi-user support
✅ Row Level Security
✅ Master CV editor
✅ Custom CV branscher

### Known Issues

**v1 Bugs:**
- Gmail app password hardcoded in `job_portal_backend.py` line 777 (should only use env var)
- `get_next_job()` uses f-string SQL (SQL injection risk if locations from user input)
- Frontend calls v2-only endpoints (fail when running locally)
- No error handling for failed API calls
- No retry logic for network failures

**v2 Missing:**
- Data export functionality (GDPR requirement)
- Privacy policy page
- Cookie consent banner
- Data Processing Agreement with Supabase (needs signing)
- Some GDPR checklist items not implemented

**Architecture Confusion:**
- Root files = v1 (SQLite, no auth)
- v2/ directory = deployed (Supabase, auth)
- v1/ directory = abandoned
- Root HTML files copied from v2 (expect v2 endpoints)

### Current Priority (from CURRENT_TASK.md)

**Goal:** Get core job application workflow working end-to-end

**Focus:**
1. Test Platsbanken API (verify it responds)
2. Verify CV category detection works
3. Test Claude API calls (require ANTHROPIC_API_KEY)
4. Test Gmail draft creation (require GMAIL_APP_PASSWORD)
5. Complete flow: scrape → select job → generate letter → create draft

**NOT NOW:**
- New features
- Refactoring
- v2 changes (separate deployment)
- Authentication for v1
- File reorganization

---

## VERIFICATION QUESTIONS - ANSWERS

### 1. How many tables are in the database?

**v1 (SQLite):** 4 tables
- jobs
- applications
- user_data
- daily_stats

**v2 (Supabase PostgreSQL):** 23 tables
- jobs, user_profiles, applications
- user_cv_branscher, user_cvs, master_cv_exports
- user_experiences, user_experience_tags, user_education, user_volunteer, user_awards, user_skills
- artist_exhibitions, artist_residencies, artist_collections
- tech_projects, tech_certifications
- academic_publications
- user_cover_letter_preferences, user_job_preferences, user_ai_feedback
- user_google_credentials, cv_industry_templates

### 2. What is the app's main purpose?

AI-powered job application automation for neurodivergent job seekers in Sweden.

**Specifically:**
- Scrapes jobs from Platsbanken (Swedish national employment service)
- Auto-selects industry-appropriate CV from 8 variants
- Generates personalized cover letters via Claude API (Swedish language)
- Creates Gmail drafts ready for user review
- Tracks application status (pending → applied → interview → offer/rejected)

**Target user:** Linnea Moritz (neurodivergent/ADHD, seeking service/tech/garden jobs in Stockholm/Småland)

### 3. Is this single-user or multi-user?

**v1 (Local):** Single-user
- Hardcoded for Linnea Moritz
- No authentication
- SQLite local database

**v2 (Production):** Multi-user
- Supabase Auth with Google OAuth
- Row Level Security isolates user data
- Each user has their own profile, CVs, applications
- Designed for freemium model (free tier + paid upgrades)

### 4. What files contain the most important instructions for me?

**MUST READ FIRST (in order):**
1. `.claude/START_HERE.md` - Critical facts about architecture
2. `.claude/CODEBASE_AUDIT.md` - Which docs are accurate vs outdated
3. `app-changes-Feb-8-2026.md` - SOURCE OF TRUTH for v2 architecture
4. `.claude/CLAUDE.md` - Active files and constraints
5. `CURRENT_TASK.md` - What to work on right now

**Reference when needed:**
- `docs/GDPR-GUIDE-SVENSKA-APPAR.md` - GDPR requirements
- `SECURITY.md` - Security best practices
- `PHILOSOPHY.md` - Design principles (UX only, ignore tech claims)
- `PROJECT_CONTEXT.md` - Quick summary

**IGNORE (outdated v1 docs):**
- All files in `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/`
- Root `supabase_schema.sql`
- Any reference to localhost, port 8000, SQLite in v2 context

### 5. What am I forbidden to do?

**NEVER:**
1. Mention art, painting, exhibitions, or Shopify in generated cover letters
2. Ask for credentials I cannot use (Supabase service role key, Vercel tokens)
3. Suggest local development commands (`npm run dev`, `python api_server.py` for production)
4. Touch v1/ folder (abandoned)
5. Merge v1 and v2 logic without explicit instruction
6. Remove hardcoded Linnea Moritz profile from v1
7. Add authentication to v1 local version
8. Query external APIs directly (supabase.co, vercel.app are BLOCKED)
9. Commit API keys or secrets to git
10. Use force push to main branch
11. Skip git hooks (--no-verify)
12. Use destructive git commands without explicit permission
13. Add new features before core flow works
14. Refactor without explicit request
15. Create commits without explicit request

**ALWAYS:**
1. Read documentation before starting work
2. Check .claude/ folder for latest instructions
3. Use Swedish for all UI text
4. Match CV categories exactly (restaurant, retail, industry, healthcare, tech, customerservice, reception, contentmoderation, art)
5. Disclose environment limitations upfront
6. Offer cloud-based solutions (not local development)
7. Write code that runs on Vercel/Supabase, not localhost

### 6. What's the current priority task?

**From CURRENT_TASK.md:**

Get the core job application workflow working end-to-end:
**Scrape jobs → Generate CV → Generate cover letter → Create Gmail draft → Apply**

**Specific steps:**
1. Test Platsbanken API scraping (verify API still works)
2. Verify CV category detection (job keywords → correct PDF)
3. Test cover letter generation (Claude API produces good Swedish text)
4. Test Gmail draft creation (IMAP connection, attachments work)
5. Verify full flow works without errors

**Technical requirements:**
- Backend: `api_server.py` + `job_portal_backend.py` (v1)
- Frontend: `frontend.html`
- Database: `data/jobs.db`
- Server: `python3 api_server.py` on port 8000 (LOCAL ONLY)

**Success = User can:**
1. Click "Scrape Jobs" and see real Swedish jobs
2. Click on a job and generate a cover letter in Swedish
3. Click "Create Draft" and see it appear in Gmail [Drafts]
4. Review and send from Gmail

**DO NOT add new features until this basic flow works reliably.**

---

## SOURCE OF TRUTH HIERARCHY

When documentation conflicts, trust in this order:

1. **Actual code** (v1: api_server.py, job_portal_backend.py; v2: v2/api/index.py)
2. **app-changes-Feb-8-2026.md** (v2 architecture blueprint)
3. **.claude/ files** (START_HERE.md, CODEBASE_AUDIT.md, CLAUDE.md)
4. **CURRENT_TASK.md** (what to work on now)
5. **docs/GDPR-GUIDE-SVENSKA-APPAR.md** (GDPR requirements)
6. **SECURITY.md** (security best practices)
7. **docs/DESIGN_HISTORY.md** (UI evolution)
8. **PHILOSOPHY.md** (UX values only, ignore tech claims)
9. **Other docs** (verify against code before trusting)

**NEVER TRUST without verification:**
- Files in `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/` (ALL outdated for v2)
- Root `supabase_schema.sql` (outdated)
- Any doc mentioning localhost, SQLite for v2, IMAP for v2

---

## NEXT STEPS FOR NEW SESSIONS

**Every new session, you MUST:**

1. Read `.claude/START_HERE.md` first
2. Read `.claude/CODEBASE_AUDIT.md` to know which docs are accurate
3. Read `CURRENT_TASK.md` to know what to work on
4. Check this file (CLAUDE_CODE_INSTRUCTIONS.md) for comprehensive reference

**Before starting ANY task:**
- Verify which version (v1 or v2) you're working on
- Check if the feature exists in both or only one version
- Read the relevant source code files (don't guess)
- Understand environment limitations (can't query Supabase/Vercel directly)

**When blocked:**
- Don't guess - read the actual code
- Don't assume local development - this is GitHub → Vercel → Supabase
- Don't ask for credentials you can't use
- Offer solutions that work in the actual deployment model

---

**This document is the most comprehensive reference for this codebase.**
**Generated by reading ALL documentation, schemas, and code files.**
**Use this as the single source of truth for future sessions.**
