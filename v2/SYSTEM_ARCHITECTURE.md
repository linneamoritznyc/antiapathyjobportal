# System Architecture & Data Modeling
## Anti-Apathy Job Portal v2

*Senast uppdaterad: 2026-02-18 — Baserad på faktisk DB-state och källkod*

---

## Del 1: Grundläggande arkitektur & Modellering

### 1. Vilken databastyp används och vad är motorn?

**Relationell databas — PostgreSQL via Supabase (molnhostad).**

| Lager | Teknologi |
|-------|-----------|
| Databasmotor | PostgreSQL 15 (hanterad av Supabase) |
| Hosting | Supabase Cloud (eu-north-1 / Stockholm-region) |
| Anslutning från backend | HTTP/REST via Supabase REST API (`httpx`) |
| ORM | Ingen — råa HTTP-anrop mot Supabase PostgREST |

Ingen SQLAlchemy, ingen Prisma. All DB-kommunikation sker via Supabase's automatgenererade REST API.

---

### 2. Vilka är de centrala entiteterna i schemat?

Databasen har **29 tabeller** i tre lager:

**Kärn-entiteter (alltid relevanta):**
| Tabell | Syfte | Rader (feb 2026) |
|--------|-------|-----------------|
| `user_profiles` | Personlig info, foto, signatur | 1 |
| `jobs` | Jobb skrapade från Platsbanken | 263 |
| `applications` | Ansökningar med status-spårning | 1 |
| `user_google_credentials` | Gmail OAuth-tokens per användare | 1 |

**CV-data (bygger upp Master CV:t):**
| Tabell | Syfte | Rader |
|--------|-------|-------|
| `user_experiences` | Arbetslivserfarenheter | 27 |
| `user_skills` | Färdigheter per bransch-kategori | 88 |
| `user_awards` | Utmärkelser | 18 |
| `tech_certifications` | Tech-certifikat | 14 |
| `user_volunteer` | Ideellt arbete | 12 |
| `tech_projects` | Tech-projekt | 11 |
| `user_certifications` | Generella certifikat | 10 |
| `user_cv_branscher` | Användarens CV-branscher | 8 |
| `user_education` | Utbildning | 4 |

**Inställningar & preferenser:**
| Tabell | Syfte |
|--------|-------|
| `user_cover_letter_preferences` | AI-stil för personliga brev |
| `user_job_preferences` | Sökfilter (plats, typ, etc.) |
| `user_job_interactions` | Interaktions-logg (viewed/skipped/applied) |

**Genererade CV-varianter (alla tomma, ännu ej använda):**
`user_cvs`, `bransch_cvs`, `master_cv_exports`, `user_cv_versions`, `user_cv_creation_conversations`, `user_cv_uploads`, `user_training_letters`

---

### 3. Hur ser ER-diagrammet (Entity Relationship) ut?

```
user_profiles (1)
    │
    ├──── user_experiences (many) ──── user_experience_tags (many) ──── user_cv_branscher (many)
    │
    ├──── user_education (many)
    ├──── user_skills (many)
    ├──── user_volunteer (many)
    ├──── user_awards (many)
    ├──── user_certifications (many)
    ├──── tech_certifications (many)
    ├──── tech_projects (many)
    │
    ├──── user_cover_letter_preferences (1:1)
    ├──── user_job_preferences (1:1)
    ├──── user_google_credentials (1:1)
    │
    ├──── applications (many) ──── jobs (many, skrapade oberoende)
    │                   └───────── user_cvs (many)
    │
    └──── user_job_interactions (many) ──── jobs
```

**Viktigt:** De flesta relationer är **logiska** (via `user_id` TEXT-fält), inte hårt FK-enforced i databasen. Undantag:
- `user_experience_tags.experience_id` → `user_experiences.id` (FK med CASCADE)
- `applications.job_id` → `jobs.id` (FK)
- `applications.cv_id` → `user_cvs.id` (FK)
- `user_training_letters.user_id` → `auth.users.id` (FK med CASCADE)

---

### 4. Vilka primärnycklar (Primary Keys) används?

**UUID för nästan allt:**
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

**Undantag:**
| Tabell | PK-typ | Anledning |
|--------|--------|-----------|
| `jobs` | `TEXT` | Platsbanken's eget jobb-ID används direkt |
| `cv_industry_templates` | `TEXT` | Slug-baserade ID:n (`'traditional'`, `'tech'`, etc.) |
| `user_cover_letter_preferences` | `TEXT` (user_id) | 1:1 med användare — user_id är PK |
| `user_job_preferences` | `TEXT` (user_id) | 1:1 med användare — user_id är PK |

**Känd inkonsistens i `user_id`-kolumntypen:**
- De flesta tabeller: `user_id TEXT`
- `user_cv_uploads` och `user_training_letters`: `user_id UUID`

Detta kräver explicit cast vid insert: `p_user_id::UUID` (se `delete_user_data()`-funktionen).

---

### 5. Hur hanteras relationer (Foreign Keys)?

Majoriteten av relationerna är **mjuka** (ingen FK i DB) — `user_id` TEXT-fält som kopplar ihop tabeller utan databas-enforced integritet.

**Hårt enforced FK:s (med CASCADE):**
```sql
-- Raderar tags när erfarenheten raderas
user_experience_tags.experience_id
    REFERENCES user_experiences(id) ON DELETE CASCADE

-- Raderar training letters när auth-användaren raderas
user_training_letters.user_id
    REFERENCES auth.users(id) ON DELETE CASCADE
```

**FK utan CASCADE (manuell rensning krävs):**
```sql
applications.job_id     REFERENCES jobs(id)
applications.cv_id      REFERENCES user_cvs(id)
```

**Varför inte fler FK:s?**
Historisk orsak — tabellerna lades till inkrementellt och `user_id` standardiserades aldrig till en riktig FK mot `auth.users`. GDPR-rensning sköts istället via `delete_user_data()`-funktionen.

---

### 6. Finns det några Enumerated Types (Enums)?

Inga PostgreSQL `ENUM`-typer är skapade. Istället används `TEXT` med `CHECK`-constraints eller konvention:

**CHECK-constraints (hårt enforced):**
```sql
-- user_job_interactions
action TEXT NOT NULL CHECK (action IN ('viewed', 'skipped', 'applied', 'saved', 'rejected'))
```

**Konventions-enums (TEXT, dokumenterat men ej enforced):**
| Kolumn | Tillåtna värden |
|--------|----------------|
| `applications.status` | `'draft'`, `'sent'`, `'skipped'`, `'saved'`, `'interview'`, `'rejected'`, `'offer'` |
| `jobs.priority` | `'normal'`, `'soon'`, `'urgent'` |
| `jobs.link_status` | `'active'`, `'expired'` |
| `user_experiences.skill_level` | `'entry'`, `'mid'`, `'senior'` |
| `user_experiences.environment_type` | `'physical'`, `'office'`, `'remote'`, `'outdoor'`, `'retail'` |
| `artist_exhibitions.exhibition_type` | `'solo'`, `'group'`, `'juried'` |

---

### 7. Hur hanteras tidsstämplar?

**Alla tidsstämplar är `TIMESTAMPTZ`** (med tidszon) i UTC-format, med `DEFAULT NOW()`.

**Standardmönster:**
```sql
created_at  TIMESTAMPTZ DEFAULT NOW()   -- sätts vid INSERT, ändras aldrig
updated_at  TIMESTAMPTZ DEFAULT NOW()   -- uppdateras automatiskt via trigger
```

**Auto-uppdaterade via triggers:**
| Tabell | Trigger | Funktion |
|--------|---------|----------|
| `user_cvs` | `update_user_cvs_updated_at` | `update_updated_at_column()` |
| `user_experiences` | `trigger_update_experience_timestamp` | `update_experience_timestamp()` → uppdaterar `last_updated` |

**Undantag:**
- `user_training_letters` använder `uploaded_at` istället för `created_at`
- `user_cv_creation_conversations` har `started_at` och `completed_at`

---

### 8. Vilka index har skapats för prestanda?

```sql
-- Jobs (mest sökta tabellen)
idx_jobs_scraped_at        ON jobs(scraped_at DESC)          -- sortering i feed
idx_jobs_contact_email     ON jobs(contact_email)            -- filtrera jobb med email

-- Interaktioner (körs vid varje sidinladdning för att filtrera bort sedda jobb)
idx_user_job_interactions_user    ON user_job_interactions(user_id, created_at DESC)
idx_user_job_interactions_job     ON user_job_interactions(job_id)
idx_user_job_interactions_unique  UNIQUE ON (user_id, job_id, action)  -- dedup-skydd

-- CV och ansökningar
idx_master_cv_exports_user   ON master_cv_exports(user_id)
idx_user_cvs_user            ON user_cvs(user_id)
idx_user_cvs_vibe            ON user_cvs(user_id, vibe_id)  -- DB column is still "vibe_id" but the app calls these "branscher"
idx_applications_user        ON applications(user_id)
idx_applications_status      ON applications(status)

-- Multi-user CV-data
idx_user_cv_branscher_user       ON user_cv_branscher(user_id)
idx_user_ai_feedback_user        ON user_ai_feedback(user_id)
idx_user_experience_tags_user    ON user_experience_tags(user_id)
idx_user_experience_tags_bransch ON user_experience_tags(bransch_id)
idx_user_certifications_user     ON user_certifications(user_id)
```

---

## Del 2: Dataflöde & Integration (Supabase → Vercel)

### 1. Hur autentiseras anropen mellan Vercel och Supabase?

Backend (`v2/api/index.py`) kör på Vercel som en **serverless FastAPI-app**. Den autentiserar sig mot Supabase med en **Service Role Key** (admin-nyckel) lagrad som Vercel-miljövariabel:

```python
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
```

Alla Supabase-anrop skickar denna nyckel i HTTP-headers:
```python
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
```

**Service Role Key** kringgår RLS (Row Level Security) — den har full admin-access till hela databasen. Det fungerar nu eftersom det bara finns en användare, men är en säkerhetsrisk om appen skalas till fler.

---

### 2. Används Supabase Client SDK eller direkt REST API?

**Direkt REST API via `httpx`** — ingen Supabase Python SDK installerad.

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{SUPABASE_URL}/rest/v1/jobs",
        headers={"apikey": SUPABASE_KEY, ...},
        params={"select": "*", "order": "scraped_at.desc"}
    )
```

Supabase's PostgREST-API översätter dessa HTTP-anrop till SQL automatiskt. Frontend (React i `frontend.html`) anropar **aldrig** Supabase direkt — allt går via Vercel-backenden.

---

### 3. Hur ser flödet ut vid en skriv-operation?

**Exempel: Användaren klickar "Sök jobb"**

```
[React frontend]
    │  POST /api/scrape-jobs  {"keywords": ["servitör"], "location": "Stockholm"}
    ▼
[Vercel / FastAPI - v2/api/index.py]
    │  1. Anropar Platsbanken API (httpx POST)
    │  2. Filtrerar jobb — bara de med kontakt-email
    │  3. Extraherar email + kontaktnamn via regex
    │  4. Beräknar prioritet (urgent/soon/normal) baserat på deadline
    │  5. Upsert till Supabase:
    │     POST /rest/v1/jobs  (Prefer: resolution=merge-duplicates)
    ▼
[Supabase / PostgreSQL]
    │  INSERT INTO jobs (...) ON CONFLICT (id) DO UPDATE SET ...
    ▼
[FastAPI svarar]
    │  {"scraped": 12, "new": 8, "updated": 4}
    ▼
[React uppdaterar UI]
```

---

### 4. Används Edge Functions eller Serverless Functions?

**Serverless Functions på Vercel** — hela backenden är en enda FastAPI-app (`v2/api/index.py`) som Vercel kör som en serverless funktion.

| Aspekt | Detalj |
|--------|--------|
| Runtime | Python 3.11 serverless (Vercel) |
| Cold start | ~1–3 sekunder vid första anrop |
| Timeout | Vercels standard: 10 sekunder (pro: 60s) |
| Supabase Edge Functions | **Används inte** — all logik i Python-backenden |
| Databas-triggers | Två stycken (för `updated_at`-uppdateringar) |

---

### 5. Hur hanteras databaskopplingar?

**Ingen connection pooling** — varje HTTP-anrop från backenden öppnar ett nytt `httpx.AsyncClient()`-objekt och stänger det efteråt (via `async with`-blocket).

```python
async with httpx.AsyncClient() as client:
    response = await client.get(...)
# Stängs automatiskt här
```

Det fungerar för nuvarande last (1 användare). Supabase hanterar connection pooling på sin sida via PgBouncer, men det är transparent för applikationen. Om appen skalas till hundratals samtidiga användare bör man byta till Supabase Python SDK som hanterar pooling bättre.

---

### 6. Finns det Real-time-prenumerationer?

**Nej** — inga WebSocket-prenumerationer används.

Frontend pollar backenden via vanliga HTTP-anrop (REST). Det finns inga `supabase.channel()` eller `on('postgres_changes', ...)` i koden. Jobbflödet uppdateras när användaren manuellt klickar "Ladda om" eller navigerar mellan flikar.

---

## Del 3: Logik & Endpoints

### 1. Vilka Stored Procedures / RPC (Remote Procedure Calls) används?

Fem SQL-funktioner finns i databasen (bekräftade via `information_schema.routines`):

| Funktion | Signatur | Anropas från |
|----------|---------|--------------|
| `export_master_cv` | `(p_user_id TEXT) → JSONB` | `save_master_cv_snapshot()` internt |
| `save_master_cv_snapshot` | `(p_user_id TEXT, p_notes TEXT) → UUID` | Planerad API-endpoint |
| `get_best_description` | `(experience_id UUID, bransch TEXT) → TEXT` | `get_experiences_for_industry()` internt |
| `get_experiences_for_industry` | `(user_id TEXT, bransch TEXT) → TABLE` | Planerad användning i cover letter-logik |
| `delete_user_data` | `(p_user_id TEXT) → VOID` | GDPR-borttagning |

Anrop från Python sker via Supabase RPC-endpoint:
```python
POST /rest/v1/rpc/delete_user_data
{"p_user_id": "1e9d7392-..."}
```

---

### 2. Används Database Triggers?

**Ja, två triggers:**

| Trigger | Tabell | Händelse | Funktion |
|---------|--------|----------|----------|
| `update_user_cvs_updated_at` | `user_cvs` | BEFORE UPDATE | `update_updated_at_column()` |
| `trigger_update_experience_timestamp` | `user_experiences` | BEFORE UPDATE | `update_experience_timestamp()` |

Båda är BEFORE-triggers som sätter tidsstämpeln innan raden skrivs till disk. Inga AFTER-triggers eller statement-level triggers finns.

---

### 3. Hur ser API-lagret ut?

Supabase PostgREST mappar automatiskt varje tabell till en REST-endpoint:

```
GET    /rest/v1/jobs?select=*&order=scraped_at.desc
POST   /rest/v1/jobs           (INSERT)
PATCH  /rest/v1/jobs?id=eq.123 (UPDATE)
DELETE /rest/v1/jobs?id=eq.123 (DELETE)
POST   /rest/v1/rpc/delete_user_data  (RPC)
```

FastAPI-backenden fungerar som ett mellanled som:
1. Tar emot anrop från React-frontend
2. Gör affärslogik (AI-anrop, email-parsing, bransch-matching)
3. Anropar Supabase REST API
4. Returnerar formaterat svar till frontend

**Viktiga FastAPI-endpoints:**

| Endpoint | Metod | Syfte |
|----------|-------|-------|
| `/api/scrape-jobs` | POST | Skrapar Platsbanken, sparar till DB |
| `/api/jobs` | GET | Hämtar jobb med filter |
| `/api/jobs/{id}/generate-letter` | POST | Genererar personligt brev via Claude API |
| `/api/jobs/{id}/save-draft` | POST | Skapar Gmail-utkast med CV-bilaga |
| `/api/profile` | GET/PUT | Hämtar/sparar användarprofil |
| `/api/gmail/auth` | GET | Startar Gmail OAuth-flöde |
| `/api/gmail/callback` | GET | Hanterar OAuth-callback |

---

## Del 4: Säkerhet & Underhåll

### 1. Hur fungerar Row Level Security (RLS)?

**RLS är inte aktiverat** på någon tabell i nuläget.

```sql
-- Dessa rader finns i schemat men är utkommenterade:
-- ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can view own profile" ON user_profiles
--     FOR SELECT USING (auth.uid()::text = user_id);
```

Eftersom det bara finns **en användare** och backenden använder **Service Role Key** (som kringgår RLS ändå) är detta inget akut problem. Om appen öppnas för fler användare måste RLS aktiveras för att förhindra att användare ser varandras data.

**Nuvarande säkerhetsmodell:**
- Backenden på Vercel är den enda som pratar med Supabase
- Frontend → Backend (Vercel) → Supabase
- Ingen direkt frontend-till-Supabase-kommunikation

---

### 2. Hur hanteras databasmigrationer?

**Manuell process** — inga migrationsverktyg (Flyway, Alembic, etc.) används:

1. Schema-ändringar skrivs som SQL direkt i chat
2. Användaren kör SQL i **Supabase SQL Editor** (dashboard)
3. `v2/supabase_schema.sql` uppdateras för att reflektera nuläget
4. Ändringen committas till GitHub

`v2/supabase_schema.sql` är **dokumentation + källkod** — ett "om du skulle bygga om från scratch"-skript, inte en migrationshistorik. Det innehåller `CREATE TABLE IF NOT EXISTS` och `CREATE OR REPLACE FUNCTION` så det är idempotent (säkert att köra om).

**Vad schemat innehåller (feb 2026):**
- 29 tabeller
- 4 index-grupper (15+ index)
- 3 Supabase Storage buckets (dokumenterade)
- 5 SQL-funktioner (inkl. GDPR delete)
- 2 triggers
- Känd inkonsistens: `user_ai_feedback` finns i schema men ej i live-DB

---

### 3. Vilken backup-strategi finns?

**Supabase automatiska backups:**
- Supabase gör dagliga automatiska snapshots (Point-in-Time Recovery på Pro-plan)
- Retention: 7 dagar på Free, 30 dagar på Pro

**Applikationsnivå:**
- `master_cv_exports`-tabellen är designad för manuella CV-snapshots via `save_master_cv_snapshot()` — men tabellen är tom (0 rader), funktionen anropas inte ännu
- Ingen automatisk export-rutin finns implementerad

**GitHub som backup för schema:**
- `v2/supabase_schema.sql` versionshanteras i Git
- Om databasen raderas kan schemat återspelas manuellt, men **data återställs inte** från schemat — bara strukturen

**Rekommendation:** Implementera ett cron-jobb (t.ex. via Vercel Cron eller GitHub Actions) som anropar `save_master_cv_snapshot()` dagligen och exporterar till Supabase Storage.
