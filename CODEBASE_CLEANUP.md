# Codebase Cleanup Guide
*Senast uppdaterad: 18 februari 2026*

---

## ⚠️ VIKTIGASTE REGELN

Det finns **två appar i detta repo**. Vercel deployas ALLTID från `v2/`. Root-nivån är referensmaterial.

```
antiapathyjobportal/
│
├── v2/                        ← ✅ LIVE APP — redigera alltid här
│   ├── frontend.html          ← ALL design/UI
│   ├── api/index.py           ← ALL backend/API
│   ├── api/cv_files/          ← 8 bransch-CVer (PDF)
│   ├── vercel.json            ← Vercel config
│   ├── requirements.txt       ← Python deps
│   └── supabase_schema.sql    ← Source-of-truth DB schema
│
├── api_server.py              ← v1 lokal server (referensmaterial, ALDRIG deployad)
├── job_portal_backend.py      ← v1 business logic (referensmaterial)
├── .claude/CLAUDE.md          ← LÄSAS AV CLAUDE — projektinstruktioner
├── HANDOFF_2026-02-18.md      ← Aktuellt handoff-dokument
└── CODEBASE_CLEANUP.md        ← DETTA DOKUMENT
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

### Root-nivå (referensmaterial — läs, redigera inte)
| Fil | Syfte |
|-----|-------|
| `api_server.py` | v1 lokal server. Innehåller endpoints som inte finns i v2. Referens. |
| `job_portal_backend.py` | v1 business logic. Har Linneas CV-sammanfattning, kategori-logik, scraping. Referens. |
| `auth.py`, `config.py`, `rate_limit.py` | Tillhör api_server_updated.py (experimentell). Referens. |
| `supabase_helper.py` | v1 Supabase-klient. Referens. |
| `HANDOFF_2026-02-18.md` | Aktuellt handoff — läs detta när ny session startar |
| `HANDOFF_2025-02-16.md` | Gammalt handoff — migrationsproblem från feb 2025 |
| `CODEBASE_CLEANUP.md` | Detta dokument |

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

**OBS:** Kategorin `art` ska ALDRIG nämna konst/målningar i generererat text (Linnea vill inte söka konstjobb med det personliga brevet).

---

## Hårdkodat i koden som borde vara i Supabase

Följande finns hårdkodat i `v2/api/index.py` och är Linneas data. Det borde lagras i Supabase:

### 1. DEFAULT_EXPERIENCE (rad ~488)
Per-kategori korta CV-sammanfattningar som används när Supabase-data saknas i cover letter-generering.

**SQL för att lagra detta ordentligt:** Se `v2/supabase/migrations/add_cv_category_hints.sql` (att skapas).

### 2. Profil-fallbacks (rad ~555-560)
```python
phone = p.get("phone", "0761166109")         # Linneas telefon
email = p.get("email", "linneamoritzCV@gmail.com")
location = p.get("location", "Sollentuna")
```
Dessa är fallbacks om user_profiles-tabellen är tom. Bör vara ifyllda i Supabase.

### 3. always_mention / never_mention (rad ~2647-2648)
```python
"always_mention": ["flexibel med tider", "korkort", "flytande engelska"],
"never_mention": ["konst", "malning", "utstallningar", "Shopify", ...]
```
Dessa är migration-defaults. Lagras i `user_cover_letter_prefs` i Supabase efter migration.

---

## SQL-filer i v2/ (förklaring)

| Fil | Status | Innehåll |
|-----|--------|---------|
| `v2/supabase_schema.sql` | ✅ AKTIV (source-of-truth) | Hela DB-schemat |
| `v2/supabase_schema_wed_feb_18.sql` | Snapshot 18 feb 2026 | Faktiskt DB-tillstånd exporterat från Supabase |
| `v2/setup_and_migrate.sql` | Körts | Initial setup + migration |
| `v2/migrate_complete.sql` | Körts | Komplett migrationsskript |
| `v2/migrate_complete_data.sql` | Körts | Migrationsskript med data |
| `v2/master_cv_data.sql` | Referens | Linneas CV-data i SQL-format |
| `v2/MIGRATE_COMPLETE_DATA.sql` | Körts | Komplett data-migration |
| `v2/supabase/migrations/*.sql` | Körts | Alla partiella migrations |

**DB-regel:** Ge SQL direkt i chatten. Uppdatera `v2/supabase_schema.sql`. Skapa ALDRIG nya SQL-filer i repot.

---

## Ändringslogg (18 februari 2026)

### Städning gjord
- ✅ Raderat från root: `frontend.html`, `api/index.py`, `vercel.json`, `requirements.txt` — exakta duplicat av v2/-versioner
- ✅ Raderat: `account.html`, `login.html`, `setup-guide.html`, `anvandarvillkor.html`, `integritetspolicy.html`, `cv_template.html` — duplicat (finns i v2/)
- ✅ Raderat: `CV_Linnea_Moritz_*.pdf` × 8 från root — duplicat (finns i v2/api/cv_files/)
- ✅ Behållit: `api_server.py`, `job_portal_backend.py`, docs — referensmaterial, ej duplicat

### Förbättringar
- ✅ Lagt till `includeFiles` i `v2/vercel.json` — Vercel bundlar nu explicit alla HTML-filer
- ✅ Skapat `HANDOFF_2026-02-18.md` — aktuellt handoff med nuläge
- ✅ Uppdaterat `CODEBASE_CLEANUP.md` (detta dokument)

---

## Vanliga misstag (för Claude)

1. **Redigera root-filer** — de är DÖDA. Allt i v2/.
2. **Bygga API-endpoints för att läsa DB** — be användaren köra SQL i Supabase dashboard.
3. **Skapa SQL-filer i repot** — ge SQL i chatten, uppdatera supabase_schema.sql.
4. **Anta att design-ändringar syns direkt** — behöver merge till main + hard refresh.
5. **Radera context-docs** — HANDOFF, PROJECT_CONTEXT, MODULARITY_GUIDE är INTE dead code.
