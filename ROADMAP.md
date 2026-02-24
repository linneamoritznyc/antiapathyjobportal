# ROADMAP — Anti-Apathy Job Portal

> Senast uppdaterad: 2026-02-24
>
> Levande dokument — uppdateras löpande när nya idéer dyker upp eller features prioriteras om.

---

## Prioriteringsguide

| Symbol | Betyder |
|--------|---------|
| 🔴 NU | Redo att byggas, planerat, påbörjat |
| 🟡 SNART | Klart idémässigt, väntar på att kärnan är stabil |
| 🔵 FRAMTID | Vision, inte detaljplanerat än |
| ✅ KLART | Implementerat och live |

---

## ✅ KLART — Redan implementerat

### Sparade jobb (Fixed Feb 24 2026)
- Spara jobb → hittas i Ansökningar → Sparade
- "Skapa ansökan"-knapp, "Visa annons"-länk, deadline-info med färgkodning
- Backend skyddar sent/interview/offer-status från att skrivas över
- Interaktionsloggning vid spara

### Preferenser-flik med negativa sökord (UI)
- Chips organiserade i kategorier (Hälsa & Vård, Utbildning, Teknik, Juridik, Övrigt)
- Klicka chip → filtrera bort jobbtyper
- Frisök: Lägg till egna ord
- Sparas i localStorage + Supabase
- **OBS:** Backend filtrerar INTE ännu — negativa sökord sparas men används inte vid scraping. Se 🟡 nedan.

### Master CV & Bransch-CVer
- Master CV-editor med erfarenheter, utbildning, certifikat, utmärkelser, volontär, skills
- 8 bransch-CVer genereras från Master CV
- PDF-nedladdning för alla CVer
- AI-chatt för CV-uppdateringar (enhance-chat)
- CV-uppladdning med AI-parsning

### Gmail-integration
- Koppla Gmail med egna OAuth-credentials
- Skapa utkast med personligt brev + CV som bilagor
- Ansökningsspårning (draft → sent → interview → offer)

### Personligt brev-motor
- AI-genererade brev med stil-preferenser, anekdoter, AI-feedback
- Svensk grammatik-check (GPT-SW3)
- Fallback: Sonnet → Haiku → mall
- Redigerbara stil-preferenser (ton, fraser, undvik-lista)

---

## 🔴 NU — Byggs just nu / nästa att byggas

### 1. Kvalifikationsvarning innan brev genereras
**Vad:** Pre-check INNAN Claude skriver brevet — om jobbet kräver kvalifikationer användaren saknar.

**Varför:** Claude genererade ett brev för en kemiforskartjänst (kräver doktorsexamen) — identifierade korrekt att Linnea inte var kvalificerad men genererade ändå brevet. Onödiga API-credits.

**Hur:**
1. Klicka "Ansök" → billig Claude-förfrågan (~100 tokens)
2. Claude returnerar `{ qualified: bool, reason: string, suggested_keywords: [] }`
3. Om `qualified: false` → modal: "Det här jobbet kräver [X]. Vill du fortsätta?"
4. Användaren väljer: Fortsätt / Hoppa över / Lägg till negativa sökord

**Detaljerad spec:** `FEATURE_IDEAS.md`

---

### 2. Sluta visa redan-ansökta jobb vid re-scrape
**Vad:** När man söker nya jobb ska redan-ansökta/avvisade jobb INTE dyka upp igen.

**Nuvarande problem:** `POST /api/scrape` returnerar färska resultat som ersätter hela jobblistan — inklusive jobb man redan sökt.

**Fix:**
- Backend: filtrera scrape-resultat mot `user_job_interactions` + `applications`
- Frontend: merga scrape-resultat med befintlig lista istället för att ersätta
- Lokal cache av ansökta jobb-IDn i localStorage som fallback

---

## 🟡 SNART — Nästa stora features

### 3. Negativa sökord: backend-filtrering
**Vad:** UI:t för negativa sökord finns redan, men backend använder dem INTE vid scraping.

**Nuvarande status:** Frontend sparar `negative_keywords` till Supabase, men `POST /api/scrape` filtrerar aldrig bort jobb baserat på dem.

**Fix:** I scrape-endpoint: hämta `user_job_preferences.excluded_keywords` och post-filtrera jobb vars titel/beskrivning matchar.

---

### 4. Kodoptimering — Minska filstorlek med ~22%
**Vad:** Båda huvudfilerna har vuxit förbi smärtgränsen. Duplicerad kod överallt.

**Backend (`v2/api/index.py` ~8600 rader):**
- Supabase headers-konstant
- Slå ihop duplicerade GDPR export/delete-endpoints
- Extract `call_claude_api()` wrapper
- Konsolidera filuppladdningslogik
- Flytta/refaktorera hårdkodad CV-migrationsdata

**Frontend (`v2/frontend.html` ~9000 rader):**
- Ta bort död kod
- Button style-konstanter
- `<ModalHeader>` komponent

**Detaljerad spec:** `OPTIMIZATION_PLAN.md`

---

### 5. CV-redigering direkt i appen

**Vad:** Redigera CVer inifrån appen utan att prata med utvecklare.

**Features:**
- 5a. Profilfoto i CV (Supabase Storage → alla PDF-CVer)
- 5b. Master CV gemensamma fält (ändra en gång → uppdatera alla 8)
- 5c. Inline-redigering per CV (per-CV override)

---

### 6. AI-förbättring av erfarenhetsbeskrivningar
Knapp "Förbättra med AI" per erfarenhet → starkare formuleringar, bättre accomplishments.

---

## 🔵 FRAMTID — Visioner & långsiktiga mål

### 7. "Extern webbplats"-flik
Klistra in URL till extern jobbannons → AI genererar brev + matchar CV + hjälper med formulärfrågor.

**Detaljerad spec:** `v2/FUTURE_FEATURES.md`

### 8. Batch-apply
Markera flera jobb → generera brev för alla → granska → spara som Gmail-utkast.

### 9. Geografi-overhaul (Taxonomy API)
Ersätt hårdkodad `LAN_DATA` (~60 kommuner) med Arbetsförmedlingens Taxonomy API (alla 290 kommuner + 21 län). Proper API-level filtrering istället för fuzzy text matching.

**Detaljerad spec:** `v2/FUTURE_FEATURES.md` → Architecture Debt

### 10. Jobbuppföljning & Interview-tracker
Status-pipeline: Ansökt → Intervju → Erbjudande/Avslag. Påminnelse att följa upp efter 2 veckor.

### 11. Multi-user deployment
Öppna appen för fler användare. Stripe-betalplan. Per-user data (redan delvis förberett).

---

## Filosofi

**Kärna:** Automatisera det mekaniska, bevara det meningsfulla.

**Neurodivergent-first:**
> Minimera beslut. Ge struktur. Ett gränssnitt. Transparens.

---

*Se även: `FEATURE_IDEAS.md`, `v2/FUTURE_FEATURES.md`, `.claude/CLAUDE.md`*
