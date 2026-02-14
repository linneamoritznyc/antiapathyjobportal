# Codebase Cleanup Guide

## System Map

```
Anti-Apathy Job Portal
├── Local v1 (ACTIVE - what you develop on)
│   ├── Backend:  api_server.py + job_portal_backend.py
│   ├── Frontend: frontend.html (React + Tailwind via CDN)
│   ├── Database: data/jobs.db (SQLite)
│   └── Server:   python3 api_server.py → localhost:8000
│
├── Deployed v2 (LIVE on Vercel + Supabase)
│   ├── Backend:  v2/api/index.py (FastAPI, 3570 lines)
│   ├── Frontend: v2/frontend.html + v2/login.html + v2/account.html
│   ├── Database: Supabase (PostgreSQL, cloud)
│   └── Schema:   v2/supabase_schema.sql + v2/setup_and_migrate.sql
│
└── CV PDFs (8 industry-specific, used by both versions)
    ├── CV_Linnea_Moritz_Restaurang_Cafe.pdf
    ├── CV_Linnea_Moritz_Butik_Kassa.pdf
    ├── CV_Linnea_Moritz_Kundtjanst.pdf
    ├── CV_Linnea_Moritz_Tech_Kontor.pdf
    ├── CV_Linnea_Moritz_Content_Moderation.pdf
    ├── CV_Linnea_Moritz_Industri_Tradgard.pdf
    ├── CV_Linnea_Moritz_Vard_Omsorg.pdf
    └── CV_Linnea_Moritz_Konst_Kultur.pdf
```

---

## Active Files (DO edit these)

### Core Backend (local v1)
| File | Purpose | Lines |
|------|---------|-------|
| `api_server.py` | FastAPI server — all REST endpoints | ~600 |
| `job_portal_backend.py` | Business logic — scraping, AI, Gmail, DB | ~1150 |
| `requirements.txt` | Python dependencies | 5 |

### Frontend
| File | Purpose | Size |
|------|---------|------|
| `frontend.html` | Main React app (jobs, CVs, applications, today) | ~3050 lines |
| `login.html` | Login/signup page (Supabase auth) | 25KB |
| `account.html` | User account/settings page | 27KB |

### Data
| File | Purpose |
|------|---------|
| `data/jobs.db` | SQLite database (auto-created) |
| `CV_Linnea_Moritz_*.pdf` (x8) | Industry-specific CVs for attachments |

### Configuration
| File | Purpose |
|------|---------|
| `.env` (create if needed) | API keys, passwords |
| `.gitignore` | Git ignore rules |
| `vercel.json` | Vercel deployment config |

### Deployed v2 (edit carefully — it's live)
| File | Purpose |
|------|---------|
| `v2/api/index.py` | Full backend with auth, Supabase, all features | 3570 lines |
| `v2/supabase_schema.sql` | Database schema (the real one) |
| `v2/setup_and_migrate.sql` | Migration scripts |
| `v2/migrate_user_data.py` | Data migration utility |

---

## Files to IGNORE (legacy / deprecated / one-shot)

### Can be deleted
| File | Why |
|------|-----|
| `fix_my_backend.py` | One-shot regex surgery script. Already run. |
| `api_server_updated.py` | Experimental version with auth. Never used as primary. |
| `v1/` (entire directory) | Abandoned first Vercel attempt. Empty shell. |
| `Olika CV/anti-apathy-portal-final/` | Pre-GitHub copy of original project. |
| `Olika CV/Skarmavbild 2025-12-20 kl. 13.10.27.png` | Random screenshot. |

### Keep but don't edit (reference only)
| File | Why |
|------|-----|
| `app-changes-Feb-8-2026.md` | Architecture brief for v2 rebuild. Reference. |
| `supabase_schema.sql` (root) | Outdated schema. v2 version is canonical. |
| `config.py` | Settings class for `api_server_updated.py`. Not used by active server. |
| `auth.py` | Auth utilities for `api_server_updated.py`. Not used by active server. |
| `rate_limit.py` | Rate limiting for `api_server_updated.py`. Not used by active server. |

### Documentation (reference only)
| Directory | Contents |
|-----------|----------|
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/` | README, philosophy, specs, changelog, next steps |
| `docs/` | Design history, GDPR guide |
| `SECURITY.md` | Security guidelines |

---

## Frontend-Backend Mismatch Warning

The frontend (`frontend.html`) was copied from v2 and expects these endpoints that **only exist in v2/api/index.py**, NOT in `api_server.py`:

| Frontend calls... | Exists in `api_server.py`? | Exists in `v2/api/index.py`? |
|---|---|---|
| `GET /api/jobs` | YES | YES |
| `POST /api/scrape` | YES | YES |
| `GET /api/stats` | YES | YES |
| `GET /api/today` | YES (new) | NO |
| `POST /api/quick-apply/{id}` | YES (new) | NO |
| `POST /api/batch-apply` | YES (new) | NO |
| `GET /api/cv/vibes` | NO | YES |
| `GET /api/cv/all` | NO | YES |
| `POST /api/cv/generate-branscher` | NO | YES |
| `GET /api/cv/master` | NO | YES |
| `POST /api/jobs/{id}/apply-with-cv` | NO | YES |
| `GET /api/user/preferences` | NO | YES |
| `POST /api/user/profile` | NO | YES |
| `POST /api/user/experience` | NO | YES |
| `POST /api/migrate-my-data` | NO | YES |
| `GET /api/applications` | YES (basic) | YES (full) |

This means: **locally, the CV/profile/auth features in the frontend won't work**. They only work when deployed to Vercel where `v2/api/index.py` handles them.

---

## File Size Reality Check

| Category | Files | Total size |
|----------|-------|------------|
| Active Python backend | 2 files | ~63KB |
| Frontend HTML | 3 files | ~230KB |
| v2 backend | 1 file | ~127KB |
| CV PDFs | 8 files | ~800KB |
| Documentation | ~12 .md files | ~100KB |
| Legacy/deletable | ~5 files | ~25KB |

The codebase is not huge — it just feels overwhelming because of the v1/v2 split and files that should have been cleaned up.
