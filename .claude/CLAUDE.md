# Claude Code Instructions for Anti-Apathy Job Portal

## What this project is
AI-powered job application portal for neurodivergent job seekers in Sweden. Scrapes Platsbanken, generates cover letters via Claude API, creates Gmail drafts with industry-matched CVs.

---

## ⚠️ CRITICAL: REPO STRUCTURE — TWO APPS EXIST, ONLY ONE IS LIVE

This repo is a mess. There are two `frontend.html`, two `api/index.py`, and two `vercel.json`. You WILL edit the wrong file if you're not careful.

```
antiapathyjobportal/
├── vercel.json              ← ROOT vercel config (NOT deployed — Vercel root dir = v2/)
├── api/index.py             ← ROOT backend (NOT deployed — dead code)
├── frontend.html            ← ROOT frontend (NOT deployed — dead code)
│
└── v2/                      ← ✅ THIS IS THE LIVE APP (Vercel root dir = v2/)
    ├── vercel.json          ← ✅ Active Vercel config
    ├── frontend.html        ← ✅ THE UI — edit this for all frontend changes
    └── api/
        ├── index.py         ← ✅ THE BACKEND — all API endpoints, business logic
        └── cv_files/        ← PDF CVs for Gmail attachments
```

### THE RULE: If you're changing anything — it goes in `v2/`

**Frontend/UI changes → `v2/frontend.html`**
**Backend/API changes → `v2/api/index.py`**
**DB schema reference → `v2/supabase_schema.sql`**

Everything else in the repo root is legacy/dead. Don't touch it.

---

## Deployment pipeline

- **Vercel Pro** plan (maxDuration up to 60s for serverless functions)
- **No local development** — no terminal, no local CLI. Everything is cloud-only (Vercel + Supabase + Claude Code on the web). Never suggest local terminal commands like `git checkout` or `npm run`.
- User manages PRs and merges via **GitHub web UI** (github.com). Claude Code pushes branches; user merges via PR.

```
GitHub (branch: main, root dir: v2/) → Vercel Pro → serves v2/api/index.py
                                                      reads v2/frontend.html
                                                            ↓
                                                        Supabase (cloud DB)
```

How `v2/api/index.py` finds the frontend:
```python
frontend_path = pathlib.Path(__file__).parent.parent / "frontend.html"
# __file__ = v2/api/index.py
# parent   = v2/api/
# parent.parent = v2/
# result   = v2/frontend.html  ✅
```

---

## ⚠️ Vercel dashboard navigation

**READ THIS FILE FIRST**: `.claude/vercel-navigation.md` — full guide to Vercel dashboard navigation, settings locations, and common traps. Always consult it before giving Vercel UI instructions.

---

## Active files (v2 — the live deployed app)

| File | Purpose |
|------|---------|
| `v2/frontend.html` | React + Tailwind single-file UI |
| `v2/api/index.py` | FastAPI backend (Vercel serverless) |
| `v2/api/cv_files/CV_Linnea_Moritz_*.pdf` | 8 industry CVs for Gmail attachments |
| `v2/supabase_schema.sql` | Source-of-truth DB schema (keep updated) |
| `v2/vercel.json` | Vercel config (root dir for project = v2/) |

---

## Dead files — DO NOT TOUCH

| Path | Why it exists | Status |
|------|--------------|--------|
| `api/index.py` | Old v1 backend | Dead — not deployed |
| `frontend.html` | Old v1 frontend | Dead — not deployed |
| `vercel.json` (root) | Old v1 config | Ignored — Vercel uses v2/ as root |
| `v1/` | Abandoned experiments | Ignore completely |
| `api_server.py` | Old local dev server | Dead |
| `job_portal_backend.py` | Old business logic | Dead |
| `api_server_updated.py` | Experiment | Not active |
| `config.py`, `auth.py`, `rate_limit.py` | Only for api_server_updated | Dead |
| `Olika CV/` | Old CV duplicates | Dead |
| `fix_my_backend.py` | One-shot script, already run | Dead |

---

## Key constraints

- All UI text in Swedish
- Never mention art, painting, exhibitions, or Shopify in generated content
- CV category detection must match: `restaurant`, `retail`, `industri`, `healthcare`, `tech`, `customerservice`, `contentmoderation`, `art`
- Gmail OAuth connected via Supabase (user connects Gmail in Profile tab)

---

## CV branch → filename mapping

| Category | Filename |
|----------|---------|
| restaurant | `CV_Linnea_Moritz_Restaurang_Cafe.pdf` |
| retail | `CV_Linnea_Moritz_Butik_Kassa.pdf` |
| customerservice | `CV_Linnea_Moritz_Kundtjanst.pdf` |
| tech | `CV_Linnea_Moritz_Tech_Kontor.pdf` |
| healthcare | `CV_Linnea_Moritz_Vard_Omsorg.pdf` |
| industri | `CV_Linnea_Moritz_Industri_Tradgard.pdf` |
| contentmoderation | `CV_Linnea_Moritz_Content_Moderation.pdf` |
| art | `CV_Linnea_Moritz_Konst_Kultur.pdf` |

---

## Anecdotes & hobbies for cover letters

Users can add personal anecdotes (stories) and hobbies that AI weaves into cover letters when relevant.

- **Table**: `user_anecdotes` (max 30 per user)
- **Types**: `anecdote` (longer personal story) or `hobby` (short hobby description)
- **Keywords**: matched against job descriptions so AI picks relevant ones
- **Backend**: `GET/POST/DELETE /api/user/anecdotes`
- **UI**: In LetterPreferencesPage (Personligt Brev tab in Profile)
- **Cover letter integration**: `generate_cover_letter()` fetches anecdotes + style prefs when user_id is available

## Editable style preferences

Users can manually add/remove phrases from their "like" and "avoid" lists.
- **Backend**: `PATCH /api/user/letter-style/phrases` (action: add/remove, list: phrases/avoid)
- **UI**: Chips with X to remove + input to add new ones
- **Cover letter integration**: `avoid_phrases` and `always_mention` from `user_cover_letter_preferences` are fed into the prompt

---

## Gmail draft spec — EXACTLY 4 assets

When "Spara i Gmail med bilagor" is clicked:
1. **Subject**: `Ansökan: [Jobbtitel] – [Användarens namn]`
2. **Body**: generated cover letter (plain text)
3. **Attachment 1**: `Personligt_Brev_[Förnamn]_[Efternamn].pdf`
4. **Attachment 2**: `CV_[Förnamn]_[Efternamn]_[Branch].pdf`

Handled by:
- Auto-draft: `apply_with_cv` creates draft at apply-time if Gmail is connected
- On-demand: `POST /api/jobs/{job_id}/save-draft`

---

## Database rules

- **Reading DB**: Ask user to run SELECT in Supabase SQL Editor and paste results. Don't build API endpoints for this.
- **Writing migrations**: Ask user to show actual schema first. Don't write blind.
- **Migration files**: Give SQL directly in chat — never create SQL files in the repo. Update `v2/supabase_schema.sql` to reflect changes.
- **Direct DB connection**: Blocked by network. Don't try.

---

## Architecture

```
GitHub → Vercel (v2/ as root dir) → FastAPI (v2/api/index.py)
                                          ↓
                              Supabase (auth, jobs, CVs, Gmail tokens)
```

Core flow: job scraping → CV matching → cover letter generation → Gmail draft with 2 PDFs

**Current priority**: Get this core flow working reliably. No new features until it's solid end-to-end.

---

## Common mistakes to AVOID

1. **Editing root `frontend.html` or root `api/index.py`** — these are dead. Always edit in `v2/`.
2. **Building API endpoints to read the DB** — just ask user to run SQL in Supabase dashboard.
3. **Creating SQL migration files in the repo** — give SQL in chat, update `v2/supabase_schema.sql`.
4. **Suggesting local terminal commands** — this is a cloud-only app. No local dev, no terminal. Never tell user to run local commands like `git checkout`, `npm install`, etc.
5. **Over-engineering** — keep it simple. Get basics working first.
