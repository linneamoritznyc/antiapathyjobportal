# Codebase Cleanup Guide
*Senast uppdaterad: 18 februari 2026*

---

## ⚠️ VIKTIGASTE REGELN

Det finns bara **en aktiv app i detta repo**: `v2/`. Den deployας på Vercel.

```
antiapathyjobportal/
│
├── v2/                        ← ✅ LIVE APP — redigera alltid här
│   ├── frontend.html          ← ALL design/UI (React + Tailwind)
│   ├── api/index.py           ← ALL backend/API (FastAPI)
│   ├── api/cv_files/          ← 8 bransch-CVer (PDF)
│   ├── vercel.json            ← Vercel config
│   ├── requirements.txt       ← Python deps
│   └── supabase_schema.sql    ← Source-of-truth DB schema
│
├── .claude/CLAUDE.md          ← LÄSAS AV CLAUDE — projektinstruktioner
├── HANDOFF_2026-02-18.md      ← Aktuellt handoff-dokument
├── ROADMAP.md                 ← Framtidsplaner och prioriteringar
├── CODEBASE_CLEANUP.md        ← DETTA DOKUMENT
└── docs/                      ← GDPR-guide och designhistorik
```

---

## System Map (nuläge feb 2026)

```
GitHub (main branch, root dir: v2/)
    → Vercel (serverless Python)
        → v2/api/index.py  (FastAPI, ~5500 rader)
                ↓
        Supabase (PostgreSQL, cloud)
                ↓
        v2/frontend.html  (React + Tailwind, single-file, ~3000 rader)
```

---

## Active Files — REDIGERA DESSA

### v2/ (live appen)
| Fil | Syfte | Redigera? |
|-----|-------|-----------|
| `v2/frontend.html` | All UI — React + Tailwind, single HTML-fil | ✅ JA |
| `v2/api/index.py` | All backend — FastAPI, endpoints, AI, Gmail, Supabase | ✅ JA |
| `v2/vercel.json` | Vercel config (includeFiles, routes, maxDuration=60s) | Sällan |
| `v2/requirements.txt` | Python-deps (fastapi, httpx, PyPDF2, python-docx, etc.) | Sällan |
| `v2/supabase_schema.sql` | DB-schema source-of-truth — uppdatera när schema ändras | ✅ JA |

### Root-nivå (referensmaterial)
| Fil | Syfte |
|-----|-------|
| `HANDOFF_2026-02-18.md` | Aktuellt handoff — läs detta när ny session startar |
| `ROADMAP.md` | Framtidsplaner och feature-prioriteringar |
| `SECURITY.md` | GDPR och säkerhetsguide |
| `DATABASE_SCHEMA_REFERENCE.md` | Detaljerad DB-referens med alla tabeller |
| `MODULARITY_GUIDE.md` | CV-modularisering och branchstruktur |
| `FEATURE_IDEAS.md` | Löpande idélista |
| `PROJECT_CONTEXT.md` | Projektöversikt och bakgrund |
| `docs/GDPR-GUIDE-SVENSKA-APPAR.md` | GDPR-referens för svenska appar |

---

## CV-bransch-mapping (KRITISK — ändra inte utan att uppdatera alla ställen)

| Kategori-ID | CV-fil | Trigger-ord |
|------------|--------|-------------|
| `restaurant` | `CV_Linnea_Moritz_Restaurang_Cafe.pdf` | restaurang, kock, café, barista, kök |
| `retail` | `CV_Linnea_Moritz_Butik_Kassa.pdf` | butik, kassa, försäljare |
| `customerservice` | `CV_Linnea_Moritz_Kundtjanst.pdf` | kundtjänst, support, kundservice |
| `tech` | `CV_Linnea_Moritz_Tech_Kontor.pdf` | it, tech, utvecklare, developer |
| `healthcare` | `CV_Linnea_Moritz_Vard_Omsorg.pdf` | vård, omsorg, undersköterska |
| `industri` | `CV_Linnea_Moritz_Industri_Tradgard.pdf` | lager, industri, trädgård |
| `contentmoderation` | `CV_Linnea_Moritz_Content_Moderation.pdf` | moderator, content, trust & safety |
| `art` | `CV_Linnea_Moritz_Konst_Kultur.pdf` | konst, kultur, galleri |

**OBS:** Kategorin `art` ska ALDRIG nämna konst/målningar i genererat text.

---

## Hårdkodat i koden som borde vara i Supabase

Följande finns hårdkodat i `v2/api/index.py` och är Linneas data. Det borde lagras i Supabase:

### 1. DEFAULT_EXPERIENCE (rad ~488)
Per-kategori korta CV-sammanfattningar som används när Supabase-data saknas i cover letter-generering.
**Plan:** Flytta till `user_cv_category_hints`-tabellen i Supabase. SQL skriven 18 feb 2026.

### 2. Profil-fallbacks (rad ~555-560)
```python
phone = p.get("phone", "0761166109")
email = p.get("email", "linneamoritzCV@gmail.com")
location = p.get("location", "Sollentuna")
```
Fallbacks om user_profiles-tabellen är tom. Bör vara ifyllda i Supabase.

### 3. always_mention / never_mention (rad ~2647-2648)
```python
"always_mention": ["flexibel med tider", "korkort", "flytande engelska"],
"never_mention": ["konst", "malning", "utstallningar", "Shopify", ...]
```
Lagras i `user_cover_letter_preferences` i Supabase.

---

## DB-regler

- **Läsa DB:** Be användaren köra SELECT i Supabase SQL Editor och klistra in resultaten. Bygg INTE API-endpoints för detta.
- **Skriva migreringar:** Ge SQL direkt i chatten. Uppdatera sedan `v2/supabase_schema.sql`.
- **Skapa ALDRIG nya SQL-filer i repot.**
- **Direktanslutning till DB:** Blockerad av nätverk. Försök inte.

---

## Ändringslogg

### 18 februari 2026 — Stor städning (denna session)
- ✅ Raderat v1-kod från root: `api_server.py`, `auth.py`, `config.py`, `rate_limit.py`, `job_portal_backend.py`, `supabase_helper.py`, `example_direct_integration.py`, `inspect_supabase.py`, `add_cvs_to_migration.py`, `supabase_schema.sql`
- ✅ Raderat gamla docs: `CLAUDE_CODE_INSTRUCTIONS.md`, `CLAUDE_CODE_MANDATORY_INSTRUCTIONS.md`, `HANDOFF_2025-02-16.md`
- ✅ Raderat hela `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/` — v1-docs från dec 2024
- ✅ Raderat gamla CVer: `Olika CV/` (duplicat — finns i `v2/api/cv_files/`)
- ✅ Raderat SQLite-databas: `data/jobs.db`
- ✅ Raderat alla migrations-SQL: `v2/migrate_*.sql`, `v2/setup_and_migrate.sql`, `v2/master_cv_data.sql`, `v2/MIGRATE_COMPLETE_DATA.sql`, `v2/supabase_schema_wed_feb_18.sql`
- ✅ Raderat `v2/supabase/migrations/` (22 filer — alla körda mot live-DB)
- ✅ Raderat `v2/supabase/*.json` — DB-dataexporter
- ✅ Raderat `v2/*.md` — duplicat-docs (ACTUAL_DB_STATE, APP_SCHEMA, SETUP_DATABASE, SUPABASE_SCHEMA, SUPABASE_STORAGE_SETUP)
- ✅ Raderat `v2/api/cv_assembly.py` — dead code, inte refererad av index.py
- ✅ Uppdaterat `v2/supabase_schema.sql` — lade till `user_cv_versions`, `user_cv_creation_conversations`, user_id-typ-notering
- ✅ Uppdaterat `ROADMAP.md` — städat bort råa anteckningar, tagit bort ej-önskade features

### Tidigare (18 februari 2026)
- ✅ Raderat från root: `frontend.html`, `api/index.py`, `vercel.json`, `requirements.txt`
- ✅ Lagt till `includeFiles` i `v2/vercel.json`
- ✅ Skapat `HANDOFF_2026-02-18.md`

---

## Vanliga misstag (för Claude)

1. **Redigera root-filer** — det finns inga aktiva root-kodfiler kvar. Allt i `v2/`.
2. **Bygga API-endpoints för att läsa DB** — be användaren köra SQL i Supabase dashboard.
3. **Skapa SQL-filer i repot** — ge SQL i chatten, uppdatera `supabase_schema.sql`.
4. **Anta att design-ändringar syns direkt** — behöver merge till main + hard refresh.
5. **Ta bort context-docs** — HANDOFF, ROADMAP, PROJECT_CONTEXT, MODULARITY_GUIDE är INTE dead code.
