# Claude Code Instructions for Anti-Apathy Job Portal

## What this project is
AI-powered job application portal for neurodivergent job seekers in Sweden. Scrapes Platsbanken, generates cover letters via Claude API, creates Gmail drafts with industry-matched CVs.

## Active files ONLY
- `api_server.py` — FastAPI server (the one you run locally)
- `job_portal_backend.py` — All business logic (scraping, AI, Gmail, DB)
- `frontend.html` — React + Tailwind single-file app
- `data/jobs.db` — SQLite database
- `CV_Linnea_Moritz_*.pdf` (x8) — Industry CVs for email attachments

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
- CV category detection must match: restaurant, retail, industry, healthcare, tech, customerservice, reception, contentmoderation, art
- Gmail drafts go to `linneamoritzCV@gmail.com` with app password from env

## Current priority
Get the basics working reliably: scraping, CV matching, cover letter generation, Gmail drafts.
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

### Architecture reminders:
- GitHub → Vercel → Supabase
- All text in Swedish
- Core flow: job scraping → CV matching → cover letter → Gmail draft
- Get THIS working before adding anything else
