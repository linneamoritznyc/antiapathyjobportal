# Future Features — Anti-Apathy Job Portal

---

## KNOWN ISSUES & BUGS (user-reported)

### Bug: "Kunde inte skapa ansökan" popup for no-email jobs
- **Status:** Partially fixed (Feb 19 2026)
- **What happens:** When a job has no `contact_email`, clicking "Skapa ansökan" sometimes shows an error popup instead of still generating the cover letter
- **Root cause:** The `apply-with-cv` endpoint returns `success: true` even without email (it just skips Gmail draft creation). But if the endpoint throws for ANY other reason (e.g., Claude API timeout, job not in DB), the frontend shows this generic error
- **Fix applied:** Better error messages, button says "Skapa brev" for no-email jobs, amber "Extern ansökan" badge
- **Still needed:** More robust error handling in `apply-with-cv` — wrap in try/except, always return partial success if letter was generated

### Issue: Jobs must be saved in Supabase for sorting/filtering to work properly
- **Current behavior:** `/api/scrape` saves jobs to Supabase with upsert (no duplicates). `/api/jobs` loads from DB. User interactions (applied/rejected/skipped) are tracked in `user_job_interactions` table
- **What works:** Applied & rejected jobs are filtered OUT of the feed. Skipped jobs go to end. Email jobs shown before no-email jobs
- **Risk:** If jobs aren't saved to DB (e.g., Supabase is down), the interaction filtering breaks and previously applied-to jobs could reappear
- **Future fix:** Add local cache (localStorage) of applied job IDs as fallback

### Bug: Re-scraping shows already-applied jobs temporarily (FIXED Feb 24 2026)
- **Status:** Fixed
- **Root cause:** Frontend used `fetch` instead of `authFetch` for `POST /api/scrape`, so no auth token was sent. Backend had interaction filtering but couldn't identify the user without the token.
- **Fix:** Changed to `authFetch` so auth token is included → backend filters out applied/rejected/saved jobs from scrape results

### Bug: Sparade jobb var oanvändbara (FIXED Feb 24 2026)
- **Status:** Fixed
- **What happened:** Saved jobs disappeared from the feed (by design) but the "Ansökningar → Sparade" tab had no useful actions — no "Ansök" button, no "Visa annons" link, no deadline info. Saving a job was essentially a dead end.
- **Additional issues fixed:**
  - Saving a job that already had status `sent`/`interview`/`offer` would **overwrite** it to `saved` (destructive!)
  - `/api/stats` endpoint was missing `saved` count
  - Save action wasn't logged in `user_job_interactions` table
- **Fixes applied:**
  - Added "Skapa ansökan" button for saved jobs → opens apply modal
  - Added "Visa annons" link → opens original Platsbanken ad
  - Added deadline info with color coding (red = urgent, amber = soon)
  - Added location display on all application cards
  - Backend now protects `sent`/`interview`/`offer` statuses from being overwritten
  - Added `saved` count to `/api/stats`
  - Added interaction logging when saving jobs

---

## ARCHITECTURE DEBT: Geography/Kommune data

### Current state (BAD)
- `LAN_DATA` is a **hardcoded JavaScript array** in `frontend.html` (~line 2152)
- Only **~60 kommuner** out of Sweden's **290**
- Only **12 län** out of **21** (Norrland completely missing: Norrbotten, Västerbotten, Västernorrland, Jämtland, etc.)
- Custom string IDs (`'sollentuna'`, `'goteborg'`) — NOT official SCB codes
- Location matching is **fuzzy text** (`"stockholm" in "Stockholms stad"`) — fragile, misses edge cases
- No connection to any official data source

### What it SHOULD be
1. **Use Arbetsförmedlingens Taxonomy API** — official source of municipality and region codes
   - API: `https://taxonomy.api.jobtechdev.se/v1/taxonomy/`
   - Has all 290 kommuner, 21 län, with proper codes
   - Same codes that Platsbanken uses internally
2. **Use Platsbanken's `region` filter** in the search API instead of post-filtering
   - The search API supports `{"type": "region", "value": "<region_code>"}` in the filters array
   - This gives exact geographic results from the API — no need for fuzzy text matching
3. **Store the taxonomy as a JSON file** or fetch from API on app load
4. **Map kommune codes to Platsbanken region codes** for proper API-level filtering

### Migration path
1. Fetch all kommuner + län from Taxonomy API → save as `v2/api/taxonomy_data.json`
2. Replace hardcoded `LAN_DATA` with data loaded from this file
3. Update Platsbanken scraper to use `region` filter type with proper codes
4. Remove fuzzy text matching (keep as fallback only)

---

## FUTURE FEATURES

### 1. "Extern webbplats" tab (Separat flik från "Jobb")

**Problem:** Många jobb har ingen e-postadress för ansökan — man måste ansöka via deras webbplats/formulär. Appen kan inte skicka Gmail-utkast för dessa, men kan fortfarande hjälpa med personligt brev, CV-val, och formulärsvar.

**Koncept:** En egen flik ("Extern webbplats") där användaren klistrar in en länk till en jobbannons, och appen:

#### Steg 1: Klistra in länk
- Användaren klistrar in URL till jobbannons (LinkedIn, företagets hemsida, etc.)
- Appen scraper/hämtar jobbannonsen och visar titel, företag, beskrivning

#### Steg 2: AI genererar brev
- Samma AI-motor som "Jobb"-fliken
- Genererar personligt brev baserat på Master CV + stil-preferenser + anekdoter
- Matchar rätt bransch-CV automatiskt

#### Steg 3: Spara ner filer
- Ladda ner personligt brev i snyggt PDF-format
- Ladda ner rätt bransch-CV (automatiskt matchat)
- Kopiera brev till urklipp

#### Steg 4: Formulärhjälp (stretch goal)
- Användaren kan klistra in frågor från ansökningsformuläret (t.ex. "Varför vill du jobba hos oss?")
- AI svarar på varje fråga baserat på användarens profil/CV/anekdoter
- T.ex. "Beskriv en situation där du löste ett problem" → AI väljer relevant anekdot

#### Tekniska detaljer
- Ny flik i frontend navigation: "🌐 Extern" (efter "Jobb")
- Backend endpoint: `POST /api/external-job/analyze` — tar URL, scraper sidan, returnerar jobbdata
- Backend endpoint: `POST /api/external-job/generate-letter` — genererar brev
- Backend endpoint: `POST /api/external-job/answer-questions` — AI svarar på formulärfrågor
- Sparar ansökan i samma `applications`-tabell med `source: 'external'`

---

### 2. Proper geografi-filtrering (replace current hack)
- Use Arbetsförmedlingens Taxonomy API for all 290 kommuner + 21 län
- Use Platsbanken's `region` filter for API-level geographic filtering
- Add pendlingsavstånd: "Visa jobb inom X km från min hemort"
- Spara senaste sökområdet
- All 290 kommuner available in dropdown, searchable

### 3. Batch-apply
- Markera flera jobb och generera brev för alla på en gång
- Visa kö med progress: "3/10 brev klara"
- Granska alla innan de sparas som Gmail-utkast

### 4. Statistik-dashboard förbättringar
- Svarsfrekvens per bransch
- Genomsnittlig tid till intervju
- Vilka sökord ger flest svar

### 5. AI-feedback loop
- Användaren markerar vilka ansökningar som ledde till intervju
- AI lär sig vilka brev-stilar som funkar bäst per bransch
- Automatisk A/B-testning av brev-varianter

### 6. Master CV editing & upload
- Redigera befintliga erfarenheter i Master CV direkt i appen (titel, företag, beskrivning, datum)
- Ladda upp fler CV:er (PDF) och koppla till branschkategorier
- Ta bort/ändra ordning på erfarenheter
- Redigera personuppgifter (namn, telefon, e-post, adress) i Master CV
- Möjlighet att importera erfarenheter från uppladdad PDF (AI-parsning)

### 7. Don't re-scrape applied jobs
- When scraping, check `user_job_interactions` table and exclude applied/rejected jobs from results
- Or: frontend merges scrape results with existing state instead of replacing
- Local cache of applied job IDs in localStorage as Supabase fallback
