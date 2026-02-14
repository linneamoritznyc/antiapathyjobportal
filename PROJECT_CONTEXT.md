# Anti-Apathy Job Portal

**In one sentence:** AI-powered job application automation for neurodivergent job seekers in Sweden — scrapes Platsbanken, generates tailored cover letters, and creates Gmail drafts with the right CV attached.

**For who:** Linnea Moritz (solo user, neurodivergent/ADHD), Swedish job market.

**Status:** Active development — MVP working locally, v2 deployed on Vercel with Supabase.

---

## Current Architecture

### What actually runs (local development)
- **Frontend:** Single-file React app (`frontend.html`) — React 18 + Tailwind via CDN, no build step
- **Backend:** FastAPI (`api_server.py`) — Python 3.9+, served by Uvicorn on port 8000
- **Database:** SQLite (`data/jobs.db`) — local file, auto-created
- **AI:** Anthropic Claude API (Sonnet 4) — generates cover letters, email pitches, contact info
- **Email:** Gmail via IMAP (`linneamoritzCV@gmail.com`) — creates drafts with PDF attachments
- **CV System:** 8 industry-specific PDF CVs auto-selected by job category

### What's deployed (Vercel + Supabase)
- **v2 directory** (`v2/`) — Next.js-style API route (`v2/api/index.py`) with Supabase auth, PostgreSQL
- **Frontend copies** — `v2/frontend.html`, `v2/login.html`, `v2/account.html` are deployed versions
- **Supabase tables** — `aap_profiles`, `aap_saved_jobs`, `aap_applications`, etc.

### Key flows
1. **Scrape** → Platsbanken API → parse jobs → store in SQLite → display in frontend
2. **Apply** → Detect job category → pick right CV PDF → generate cover letter via Claude → create Gmail draft with attachments
3. **Quick Apply** → One click: generate letter + create draft (new feature)
4. **Batch Apply** → Select multiple jobs → generate all letters at once (new feature)

---

## Known Issues

### Bugs / Technical Debt
- Gmail app password is hardcoded in `job_portal_backend.py` line 777 — should only come from env var
- `get_next_job()` in `job_portal_backend.py` uses string interpolation in SQL (f-string with location names) — SQL injection risk if locations ever come from user input
- Two versions of the API server exist (`api_server.py` vs `api_server_updated.py`) — unclear which is canonical
- `fix_my_backend.py` is a one-shot script that regex-replaces code in `job_portal_backend.py` — should be deleted after use
- Frontend calls some v2 API endpoints (`/api/cv/vibes`, `/api/cv/all`, `/api/jobs/{id}/apply-with-cv`, `/api/user/*`) that don't exist in the local `api_server.py` — these only work when deployed to Vercel with `v2/api/index.py`
- `config.py`, `auth.py`, `rate_limit.py` are imported by `api_server_updated.py` but NOT by the active `api_server.py`

### Architecture Confusion
- **Root files** = local v1 (SQLite, no auth)
- **v2/ directory** = deployed version (Supabase, auth, more features)
- **v1/ directory** = abandoned early attempt
- Root HTML files (`frontend.html`, `login.html`, etc.) were copied FROM v2 in a deployment fix commit — so root and v2 frontends are nearly identical but the backends are completely different
- The frontend expects Supabase auth (localStorage tokens, `/api/user/*` endpoints) but the local backend doesn't have auth at all

### Missing Features (partially built)
- Email address extraction from job postings (AI-based, planned but not automated)
- Interview tracking system (DB columns exist in v2 schema, no UI)
- Automated follow-ups (planned, not built)
- PDF generation for cover letters (built in backend via reportlab, but needs the package installed)

---

## DO NOT TOUCH

These files/folders are legacy, deprecated, or one-shot utilities:

- `v1/` — Abandoned first Vercel attempt. Not used.
- `fix_my_backend.py` — One-time code surgery script. Already run. Can be deleted.
- `api_server_updated.py` — Experimental version with auth/rate-limiting. Not the active server.
- `Olika CV/` — Old CV folder with duplicates and screenshots. The 8 root-level PDFs are the active CVs.
- `Olika CV/anti-apathy-portal-final/` — Pre-GitHub copy of the original project.
- `supabase_schema.sql` (root) — Outdated schema. `v2/supabase_schema.sql` is the real one.
- `app-changes-Feb-8-2026.md` — One-time architecture brief for rebuilding as v2. Reference only.

---

## Environment Variables Needed

```bash
# Required for AI features
export ANTHROPIC_API_KEY="sk-ant-..."

# Required for Gmail drafts
export GMAIL_APP_PASSWORD="your-16-char-app-password"

# Optional (for v2/Vercel deployment)
export SUPABASE_URL="https://..."
export SUPABASE_ANON_KEY="..."
export SUPABASE_SERVICE_ROLE_KEY="..."
```

## Quick Start (local)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."
export GMAIL_APP_PASSWORD="..."
python3 api_server.py
# Open http://localhost:8000
```
