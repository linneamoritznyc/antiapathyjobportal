# Claude Code Instructions for Anti-Apathy Job Portal

## What this project is
AI-powered job application portal for neurodivergent job seekers in Sweden. Scrapes Platsbanken, generates cover letters via Claude API, creates Gmail drafts with industry-matched CVs.

## Active files ONLY (v2 — Vercel deployed)
- `v2/api/index.py` — FastAPI backend (Vercel serverless, Supabase, auth, all features)
- `v2/frontend.html` — React + Tailwind single-file app
- `v2/api/cv_files/CV_Linnea_Moritz_*.pdf` (x8) — Industry CVs for email attachments
- `v2/supabase_schema.sql` — Source-of-truth DB schema

## Active files ONLY (v1 — local only, legacy)
- `api_server.py` — FastAPI server (the one you run locally)
- `job_portal_backend.py` — All business logic (scraping, AI, Gmail, DB)
- `data/jobs.db` — SQLite database

## DO NOT TOUCH
- `v1/` — Abandoned. Ignore completely.
- `fix_my_backend.py` — One-shot script. Already run.
- `api_server_updated.py` — Experimental. Not the active server.
- `Olika CV/` — Old CV folder with duplicates.
- `config.py`, `auth.py`, `rate_limit.py` — Only used by `api_server_updated.py`, not the active server.

## v2 is deployed separately
- `v2/api/index.py` is the Vercel-deployed backend (Supabase, auth, full features)
- The frontend expects some v2 endpoints that don't exist locally
- Don't merge v1 and v2 logic without explicit instruction

## Key constraints
- All UI text in Swedish
- Never mention art, painting, exhibitions, or Shopify in generated content
- CV category detection must match: restaurant, retail, industri, healthcare, tech, customerservice, contentmoderation, art
- Gmail OAuth connected via Supabase (user connects Gmail in Profile tab)

## Gmail draft spec — EXACTLY 4 assets
When the user clicks "Spara i Gmail med bilagor", the resulting Gmail draft must contain:
1. **Subject line**: `Ansökan: [Jobbtitel] – [Användarens namn]` (e.g. `Ansökan: SERVITRIS/SERVITÖR – Linnea Moritz`)
2. **Email body**: the generated/edited cover letter text (plain text)
3. **Attachment 1**: `Personligt_Brev_[Förnamn]_[Efternamn].pdf` — generated PDF from cover letter text
4. **Attachment 2**: `CV_[Förnamn]_[Efternamn]_[Branch].pdf` — the matched industry CV (e.g. `CV_Linnea_Moritz_Restaurang_Cafe.pdf`)

The v1 screenshot (BBQ Steakhouse application) shows this working correctly and is the reference implementation.

This is handled by:
- Auto-draft: `apply_with_cv` creates draft at apply-time if Gmail is connected
- On-demand: `POST /api/jobs/{job_id}/save-draft` creates draft with current (edited) letter

## CV branch → filename mapping
- restaurant → `CV_Linnea_Moritz_Restaurang_Cafe.pdf`
- retail → `CV_Linnea_Moritz_Butik_Kassa.pdf`
- customerservice → `CV_Linnea_Moritz_Kundtjanst.pdf`
- tech → `CV_Linnea_Moritz_Tech_Kontor.pdf`
- healthcare → `CV_Linnea_Moritz_Vard_Omsorg.pdf`
- industri → `CV_Linnea_Moritz_Industri_Tradgard.pdf`
- contentmoderation → `CV_Linnea_Moritz_Content_Moderation.pdf`
- art → `CV_Linnea_Moritz_Konst_Kultur.pdf`

## Current priority
Get the basics working reliably: scraping, CV matching, cover letter generation, Gmail drafts with both PDFs attached.
Do not add new features until the core flow works end-to-end.

## CRITICAL: Common Claude Code Mistakes to AVOID

### Why Claude Code wastes your time:

1. **Doesn't read documentation before starting** - You have .claude/CLAUDE.md, CURRENT_TASK.md, handoff documents. READ THESE FIRST. Don't jump to coding and guess what's needed.

2. **Defaults to "write more code" for everything** - Sometimes the answer is:
   - Use existing tools (Supabase SQL Editor)
   - Check existing files
   - Run a simple query
   - Don't think "I'm a coding assistant, so I must write code" when code is the WRONG solution.

3. **Doesn't understand "simple" vs "correct"** - Instructions say: "Keep it simple, get basics working." You hear: "Build elaborate infrastructure with API endpoints, migration systems, complex workflows." STOP.

4. **Forgets context every 10 minutes**:
   - Told "No local development" → Still suggests running scripts locally
   - Told "Cloud-based app" → Creates local migration scripts
   - Told "Just use Supabase dashboard" → Builds API endpoints

5. **Treats every problem as greenfield** - This app EXISTS. Database EXISTS. Schema EXISTS. Data definitions EXIST. Don't act like building from scratch. USE WHAT'S THERE.

6. **Can't distinguish "development tools" vs "user features"**:
   - Need to READ database → Development task → Use SQL Editor
   - DON'T think: "Database reading = user feature = build API endpoint"

### Database work specifically:

**When asked to "look at the database":**
- Ask user to run SELECT queries in Supabase SQL Editor
- User pastes results
- That's it
- DON'T build API endpoints to query the database
- DON'T try to connect directly (network blocked)
- DON'T overcomplicate it

**When writing database migrations:**
1. ASK user to show you actual schema first (SELECT from information_schema)
2. ASK user to show you actual data (SELECT * LIMIT 5)
3. THEN write migration SQL based on THEIR reality, not your assumptions
4. Don't write blind

### Database changes:
- NEVER create separate SQL migration files in the repo. It clutters GitHub and is overwhelming.
- Instead: give SQL directly to the user in chat to run in Supabase SQL Editor.
- ALWAYS update `v2/supabase_schema.sql` to reflect any DB changes (this is the source of truth).
- One schema file, no migration folder spam.

### Architecture reminders:
- GitHub → Vercel → Supabase
- All text in Swedish
- Core flow: job scraping → CV matching → cover letter → Gmail draft
- Get THIS working before adding anything else
