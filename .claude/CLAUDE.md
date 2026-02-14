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
