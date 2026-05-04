# Anti-Apathy Job Portal

AI-powered job application automation for neurodivergent job seekers in Sweden. Scrapes Platsbanken, generates tailored cover letters using Claude AI, and creates Gmail drafts with the right CV attached.

## Architecture

- **Backend/Frontend:** Single FastAPI app (`v2/api/index.py`) that serves both the REST API and HTML pages
- **Frontend:** Single-file React 18 + Tailwind CSS via CDN (`v2/frontend.html`, `v2/login.html`, `v2/account.html`)
- **Database:** Supabase (PostgreSQL) — 29 tables for jobs, user profiles, CVs, applications
- **AI:** Anthropic Claude API — generates Swedish cover letters with strict grammar/style rules
- **Email:** Gmail API — creates draft emails with PDF CV attachments
- **CV System:** 8 industry-specific PDF CVs in `v2/api/cv_files/`

## Running the App

```bash
python start.py
```

Runs on port 5000 (0.0.0.0). The FastAPI app serves the frontend HTML at `/` and all API routes under `/api/`.

## Key Files

- `start.py` — Startup script (uvicorn on port 5000)
- `v2/api/index.py` — Main FastAPI app (11,000+ lines) with all routes
- `v2/frontend.html` — Main React frontend (607KB single file)
- `v2/login.html` — Login page with Supabase auth
- `v2/account.html` — Account management page
- `v2/requirements.txt` — Python dependencies

## Environment Variables

```bash
# Required for AI cover letter generation
ANTHROPIC_API_KEY=sk-ant-...

# Required for Supabase database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# Required for Gmail draft creation
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password

# Optional
GEMINI_API_KEY=...
HUGGINGFACE_API_KEY=...
```

## Key Routes

- `GET /` — Serves the main frontend app
- `GET /login` — Login page
- `GET /account` — Account page
- `POST /api/scrape` — Scrape jobs from Platsbanken
- `POST /api/jobs/{id}/letter` — Generate cover letter
- `POST /api/jobs/{id}/apply-with-cv` — Full application flow
- `GET /api/cv/all` — List all CVs
- `GET /api/aktivitetsrapport` — Activity report
- `GET /api/health` — Health check

## Notes

- The app uses Supabase for auth — users need a Supabase account configured
- Without Supabase env vars, the app still loads but auth/data features won't work
- The `v1/` directory is abandoned — ignore it
- Root-level `api_server.py` files are the old local SQLite version — not used
