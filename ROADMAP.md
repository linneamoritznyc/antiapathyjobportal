# ROADMAP — Anti-Apathy Job Portal

> Senast uppdaterad: 2026-02-18
>
> Levande dokument — uppdateras löpande när nya idéer dyker upp eller features prioriteras om.

---

## Prioriteringsguide

| Symbol | Betyder |
|--------|---------|
| 🔴 NU | Redo att byggas, planerat, påbörjat |
| 🟡 SNART | Klart idémässigt, väntar på att kärnan är stabil |
| 🔵 FRAMTID | Vision, inte detaljplanerat än |

---

## 🔴 NU — Klart att byggas (redan planerat/begärt)

### 1. Preferenser-flik med negativa sökord

**Vad:** Ersätter Quiz-fliken med en fullständig "Preferenser"-flik där användaren kan filtrera BORT jobbkategorier de inte vill ha.

**Varför:** Platsbanken scrapar psykologjobb, kuratorjobb, ingenjörsjobb — utan ett "minus"-filter visas de ändå i listan trots att Linnea inte är kvalificerad.

**Hur det ska fungera:**
- Chips organiserade i kategorier (Hälsa & Vård, Utbildning, Teknik, Juridik, Övrigt)
- Klicka ett chip → det blir rött och den jobbtypen försvinner ur jobblistan
- Sökfält för att hitta specifika yrken att utesluta
- Frisök: Lägg till valfritt eget ord (t.ex. "kemist")
- Sparas i localStorage, filtreras direkt i frontend

**Tekniskt:** Ingen backend. `v2/frontend.html` only. Befintligt `filteredJobs`-filter utökas.

**Plan:** Detaljerad spec finns i `/root/.claude/plans/lively-watching-whisper.md`

---

### 2. Kvalifikationsvarning innan brev genereras

**Vad:** En pre-check som visas som modal INNAN Claude skriver brevet — om jobbet kräver något Linnea uppenbart saknar (PhD, specifik yrkeslicens, 5+ års erfarenhet).

**Varför:** Claude identifierade korrekt att Linnea inte var kvalificerad för en kemiforskartjänst — men genererade ändå brevet och drog API-krediter. Onödigt och frustrerande.

**Hur det ska fungera:**
1. Klicka "Generera brev" → snabb Claude-förfrågan (billig, ~100 tokens input)
2. Claude returnerar `{ qualified: bool, reason: string, suggested_keywords: [] }`
3. Om `qualified: false` → modal visas: *"Obs: Det här jobbet kräver [X] vilket du inte verkar ha. Vill du fortsätta ändå?"*
4. Användaren väljer: Fortsätt / Hoppa över / Lägg till som negativt sökord

**Tekniskt:** Ny liten funktion i `v2/api/index.py`, anrop från frontend.

**Plan:** Dokumenterad i `FEATURE_IDEAS.md`

---

### 3. user_cv_category_hints-tabell i Supabase

**Vad:** SQL-tabell som låter appen lära sig vilka branscher Linnea föredrar för specifika jobbkategorier.

**Varför:** Idag är branschmatchning hårdkodad i `v2/api/index.py` (`DEFAULT_EXPERIENCE`). Den ska komma från Supabase istället.

**Tekniskt:** SQL redan skriven (18 feb 2026), körs i Supabase SQL Editor.
`v2/api/index.py` uppdateras att läsa från tabellen istället för hårdkodad dict.

---

## 🟡 SNART — Nästa stora features

### 4. Jobblagring i Supabase *(Prioritet: Hög)*

**Vad:** Alla jobb som skrapas från Platsbanken sparas permanent i Supabase per användare — inte bara i minnet.

**Varför:** Idag försvinner jobben när sidan laddas om. Användaren kan inte ta vid där hen slutade, och samma jobb kan dyka upp igen i kön. Det är frustrerande och ineffektivt.

**Hur det ska fungera:**
- Varje skrapat jobb sparas i `jobs`-tabellen i Supabase kopplat till `user_id`
- Jobb som redan setts markeras med `status = 'seen'` och visas inte igen
- Jobb som fått ansökan markeras `status = 'applied'`
- Nästa gång användaren öppnar appen: kön fortsätter från där den slutade
- "Ladda fler jobb"-knappen hämtar nya jobb från Platsbanken OCH sparar dem

**Tekniskt:**
- `v2/api/index.py` — scrape-endpoint skriver till Supabase istället för bara returnera
- `jobs`-tabellen finns redan i Supabase (se `supabase_schema.sql`)
- Frontend hämtar jobb via API, inte från minnet

---

### 5. CV-redigering direkt i appen *(Prioritet: Hög)*

**Vad:** Användaren ska kunna redigera sina CVer inifrån appen — utan att prata med en utvecklare och utan att öppna kod.

**Bakgrund:**
> *"Jag vill göra alla ändringar INNE ifrån APPEN. För så kommer det vara för mina användare i framtiden också — de kanske vill lägga till en bild i sitt CV, ändra ett datum om de hittar en typo, ändra platsen de bor på, ändra en länk till sin portfolio."*

**Exakta features:**

#### 5a. Profilfoto i CV
- Ladda upp foto via appen (en gång)
- Sparas i Supabase Storage
- Visas **uppe i högra hörnet** på ALLA genererade CV-PDFer automatiskt
- Kan bytas ut när som helst → uppdaterar alla PDFer

#### 5b. Master CV-koncept
- En "Master CV"-vy i appen med alla gemensamma fält:
  - Namn, adress, telefon, e-post
  - LinkedIn-länk, portfolio-länk
  - Profilfoto
- Redigera ett fält → popup visas: **"Vill du uppdatera alla 8 CVer med denna ändring?"**
- JA → bulk-update i Supabase, alla PDFer regenereras
- NEJ → ändringen gäller bara det CV du redigerar just nu

**Designprincip: 80/20-modellen**
> 80% av ändringar är gemensamma (adress, telefon, foto) → ska kunna göras en gång.
> 20% är unika per CV (specifika formuleringar för den branschen) → ska kunna avvika.

#### 5c. Inline-redigering per CV
- I "Mina CV"-fliken: klicka på ett fält för att redigera det
- Ändra datum, formulering, platsnamn direkt i UI
- Per-CV override som INTE triggar cascade-frågan

**Tekniskt:**
- `v2/frontend.html` — CV-editor komponent
- `v2/api/index.py` — ny endpoint: `POST /api/cvs/{cv_id}/update`, `POST /api/cvs/bulk-update`
- Supabase: `user_cvs`-tabellen utökas med `overrides`-kolumn (JSON)
- PDF-regenerering: anrop till befintlig PDF-generation-logik per CV

---

### 6. Export av Master CV som PDF och text

**Vad:** Från Master CV-vyn kan användaren ladda ner sitt CV i två format.

**Varför:**
> *"Så att användaren enkelt kan skriva ut och spara, eller ladda upp till ChatGPT eller Gemini för karriärsråd om vilka jobb som hade passat en sådan här profil."*

**Knappar:**
- **"Ladda ner PDF"** — genererar en väldesignad PDF med rätt layout
- **"Kopiera som text"** — kopierar till clipboard i plain text, redo att klistra in

**Tekniskt:**
- PDF: befintlig `reportlab`-logik i `v2/api/index.py`
- Text: enkel serialisering av CV-strukturen till läsbar text

---

### 7. AI-förbättring av erfarenhetsbeskrivningar

**Vad:** Knapp på varje arbetslivserfarenhet: *"Förbättra med AI"*

**Varför:**
> *"Förbättra själva beskrivningen av texten så att det låter att jag verkligen var en bra anställd. Lite bättre accomplishments, lite mer output, lite mer nice vibe."*

**Hur det ska fungera:**
1. Klicka "Förbättra" bredvid en erfarenhet
2. Claude genererar en starkare version (mer output-fokuserad, bättre "sazz")
3. Linnea ser: nuvarande text | förbättrad text — sida vid sida
4. Väljer: Behåll originalet / Använd förbättrad / Redigera manuellt
5. Sparas i Supabase

**Tekniskt:** Ny endpoint `POST /api/experiences/{id}/improve`, frontend diff-vy.

---

### 8. AI-chatt för att uppdatera Master CV

**Vad:** En enkel chattyta i "Mina CV"-fliken där användaren kan prata med AI för att uppdatera sitt CV naturligt.

**Varför:** Det ska vara lika enkelt att uppdatera sitt CV som att skicka ett meddelande. Ingen formulär, inget klickande runt i fält.

**Exempel på vad man kan skriva:**
- *"Jag fick ett certifikat i serveringskunskap idag, kan du lägga till det?"*
- *"Jag jobbar inte längre på Ica Maxi, markera det som avslutat"*
- *"Ändra min adress till Norsdborg istället för Sollentuna"*
- *"Lägg till att jag är van vid kassaarbete i min Butik-CV"*

**Hur det ska fungera:**
1. Användaren skriver ett meddelande i chatten
2. Claude tolkar vad som ska ändras och föreslår en konkret uppdatering
3. Användaren ser förslaget: *"Jag förstår att du vill lägga till X. Ska jag uppdatera Master CV? Vill du också uppdatera alla bransch-CVer?"*
4. JA → sparat i Supabase
5. NEJ / Redigera → användaren justerar manuellt

**Designprincip:** Supervised AI — användaren godkänner alltid innan något sparas.

**Tekniskt:**
- Frontend: enkel chattkomponent i "Mina CV"-fliken
- Backend: `POST /api/master-cv/chat` — skickar meddelande + aktuellt CV-innehåll till Claude
- Claude returnerar strukturerat förslag `{ field, old_value, new_value, affects_all_cvs }`

---

## 🔵 FRAMTID — Visioner & Långsiktiga mål

### 7. Jobbuppföljning & Interview-tracker *(neutral — kan byggas senare)*

**Vad:** Håll koll på var i processen varje ansökan är.

**Funktioner:**
- Datum för ansökan, automatiskt loggat
- Status: Ansökt → Kallad till intervju → Tackad nej / Erbjudande
- Påminnelse att följa upp efter 2 veckor om inget svar

---

### 8. Multi-user deployment

**Vad:** Öppna appen för fler användare — inte bara Linnea.

**Funktioner:**
- Användare laddar upp sina egna CVer och foto
- Betalplan (Stripe)
- Separata Supabase-rader per användare (redan delvis förberett)

---

## Filosofi

**Kärna:** Automatisera det mekaniska, bevara det meningsfulla.

**80/20-regeln (omdefinierad):**
> Istället för 80% jobba + 20% förbättra:
> **80% workflow-optimering, 20% implementation.**
> Tänk igenom systemet. Bygg rätt saker rätt.

**Neurodivergent-first:**
> Minimera beslut. Ge struktur. Ett gränssnitt. Transparens.

---

*Se även: `FEATURE_IDEAS.md`, `HANDOFF_2026-02-18.md`, `.claude/CLAUDE.md`*
