# What I'm Working on RIGHT NOW

## Goal
Get the core job application workflow actually working end-to-end:
**Scrape jobs -> Generate CV -> Generate cover letter -> Create Gmail draft -> Apply**

Nothing fancy. Just the basics, reliably.

---

## Success Criteria

- [ ] Job scraping from Platsbanken works and returns real jobs
- [ ] CV generation works (industry-specific CVs match job categories)
- [ ] Cover letter generation via Claude API produces good Swedish letters
- [ ] Gmail draft creation works (with CV + cover letter PDF attached)
- [ ] User profile data from Supabase (Linnea Moritz) transfers correctly to local profile
- [ ] The full flow works: scrape -> pick job -> generate letter -> create draft

---

## What's Broken / Needs Fixing

### 1. Job Scraping
- Test if Platsbanken API (`platsbanken-api.arbetsformedlingen.se/jobs/v1/search`) still responds
- Check if scraped jobs are actually showing up in the frontend
- Verify location filtering works (Stockholm, Sollentuna, Vetlanda, etc.)

### 2. CV Generation
- 8 PDF CVs exist at root level — verify they get correctly matched to job categories
- The `detect_job_category()` function needs to reliably categorize jobs
- Check that the right CV gets attached when creating Gmail drafts

### 3. Cover Letter Generation
- Requires `ANTHROPIC_API_KEY` env var — verify it's set
- Test that Claude API calls work and return Swedish-language letters
- Letters should reference actual job details (title, company, description)

### 4. Gmail Draft Creation
- Requires `GMAIL_APP_PASSWORD` env var
- Test IMAP connection to Gmail
- Verify drafts show up in Gmail with both CV PDF and cover letter PDF attached

### 5. Supabase -> Local Profile Migration
- User data (Linnea Moritz) exists in Supabase tables
- Need to pull profile, experiences, education, skills into the local system
- The `/api/migrate-my-data` endpoint exists in v2 — check if it works

---

## Technical Requirements

- Backend: `api_server.py` + `job_portal_backend.py` (the active v1 files)
- Frontend: `frontend.html` (React + Tailwind, single file)
- Database: `data/jobs.db` (SQLite)
- Server: `python3 api_server.py` on port 8000

---

## DO NOT

- Do not add new features until the basics work
- Do not refactor or reorganize files right now
- Do not touch `v2/` directory (that's the deployed Vercel version)
- Do not change the CV PDFs
- Do not add authentication to the local v1 server
- Do not remove the hardcoded Linnea Moritz profile from `job_portal_backend.py` — that's intentional for v1
