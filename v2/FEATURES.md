# Platsbanken-ai — Funktioner & UX per sida

> Uppdaterad: 24 feb 2026 (v2.5 — kvalifikationskontroll fixad, Q&A-dokumentation, statusmarkeringar för halvbyggda features)

AI-driven jobbportal för neurodivergenta jobbsökare i Sverige. Skrapar Platsbanken, genererar personliga brev via Claude, skapar Gmail-utkast med bransch-CV.

---

## Landing Page (ej inloggad)

Besökare som inte är inloggade ser en marknadsföringssida med tre flikar:

### Hem
- Hero-text: "Jobbsökande utan ångest."
- Kort pitch: Master CV → bransch-versioner → Platsbanken-scraping → AI-brev → Gmail-utkast
- Processtegsvisning: 1. Skapa konto → 2. Fyll i Master CV → 3. Generera bransch-CV → 4. Sök jobb
- CTA-knapp till inloggning

### Varför oss?
- Tre USP:ar med taggar:
  - Designad för neurodivergenta (ADHD, autism)
  - 100% svenska arbetsmarknaden
  - AI som skriver personliga brev
- Jämförelsematris mot andra verktyg

### Priser
- Prisnivåer och planer
- FAQ-sektion
- **⚠️ PLACEHOLDER** — ingen riktig prismodell eller betalningssystem finns. Needs a decision: freemium, subscription, pay-per-use?

**Supabase-koppling:** Ingen — statisk sida.

---

## Inloggning (`/login`)

Separat HTML-fil (`v2/login.html`). Två flikar: **Logga in** / **Skapa konto**.

### Logga in
- E-postfält (obligatoriskt)
- Lösenordsfält med visa/dölj-toggle (minst 6 tecken)
- **"Glömt lösenord?"** — visar formulär för lösenordsåterställning via e-post
- **"Logga in"**-knapp → `POST /api/auth/signin`
- **"Logga in via Google"**-knapp → `GET /api/auth/google` → Google OAuth-flöde → callback

### Skapa konto
- Förnamn + efternamn (valfritt)
- E-post (obligatoriskt)
- Lösenord med styrkemätare (minst 6 tecken)
- GDPR-samtycke checkbox (obligatorisk)
- **"Skapa konto"**-knapp → `POST /api/auth/signup`

### Lösenordsåterställning
- E-postfält
- **"Skicka återställningslänk"**-knapp → `POST /api/auth/reset-password`

**Supabase-koppling:**
- `auth.users` — Supabase Auth hanterar e-post/lösenord + Google OAuth
- Tokens sparas i `localStorage` (auth_token, refresh_token, user)

---

## Huvudapp — Navigation

12 flikar i toppnavigering efter inloggning:

| Flik | Ikon | Namn |
|------|------|------|
| `jobs` | 📧 | Jobb |
| `external` | 🌐 | Extern |
| `cvs` | 📄 | Mina CV |
| `applications` | 📬 | Ansökningar |
| `metrics` | 📊 | Statistik |
| `preferences` | ⚙️ | Preferenser |
| `platser` | 📍 | Platser |
| `letter` | ✍️ | Personligt brev |
| `brevformat` | 📝 | Brevformat |
| `gmail` | 📬 | Gmail |
| `quiz` | ✨ | Quiz |
| `profil` | 👤 | Profil |

---

## 📧 Jobb

Visar jobb som skrapats från Platsbanken och som har **kontakt-e-post** (= kan sökas via Gmail).

### Platsbanken-scraping
- **Triggas manuellt** — användaren klickar "Sök nya jobb"-knappen (`POST /api/scrape`)
- **Triggas automatiskt** efter onboarding-quiz (en gång)
- **Ingen cron/schema** — ingen automatisk scraping i bakgrunden. **Ska byggas ut i framtiden?** Needs a decision: daglig cron, scrape vid login, eller manuellt för alltid?
- **Volym per scrape**: upp till 5 sökord × 15 jobb + 2 breda sökningar × 20 jobb = ~95 jobb, deduplicerade på jobb-ID

### Toppsektion
- **Sökfält** — filtrerar på titel, företag, plats (klientside)
- **Prioritetsfilter** — dropdown: Alla / Akut / Snart / Normal
- **Sortering** — dropdown: deadline / senaste / etc
- **"Visa dolda"** — toggle för att se jobb du redan hoppat över/avvisat

### Jobbkort (12 per sida, grid-layout)
Varje kort visar:
- **Prioritetsbadge** — ⚡ Akut (röd) / ⏰ Snart (amber) / ✓ Normal
- **📌 Spara-knapp** — sparar jobbet i DB (`POST /api/jobs/{id}/save` → `applications`-tabellen med `status=saved`). Inte localStorage — kräver inloggning. Unsave via `DELETE /api/jobs/{id}/save`.
- **Deadline** — datum + färgkodad badge
- **Jobbtitel**, **Företagsnamn**, **Ort**
- **Kontakt-epost** (grön badge)
- **"✨ Ansök"**-knapp — öppnar ansökningsmodalen
- **↗ Extern länk** — öppnar originalannonsen på Platsbanken

### Ansökningsmodal (öppnas vid "✨ Ansök")
1. **Kvalifikationsvarning** — Haiku (billig + snabb modell) gör en snabbkontroll mot dina erfarenheter + utbildning. Om `qualified=false` visas varning med tre val:
   - **"Jag vill söka ändå"** — struntar i varningen, genererar brev som vanligt
   - **"Hoppa över"** — stänger modalen
   - **"Hoppa över + filtrera bort liknande"** — lägger till föreslagna negativa sökord
   - **Varningen är bara rådgivande** — användaren kan ALLTID söka ändå. Om Haiku-API:t misslyckas → `qualified=true` (fail open).
   - **"Credit"** = en Claude API-anrop. Att generera ett brev kostar ~1 Sonnet-anrop. Kvalifikationskontrollen kostar ~1 Haiku-anrop (mycket billigare). Det finns inget credit-saldo i appen — det är en kostnadssignal till appägaren. **Ska byggas ut i framtiden?** Needs a decision: per-user credit-system, flat monthly fee, eller obegränsat?
2. AI genererar personligt brev via `POST /api/jobs/{id}/apply-with-cv`
   - **Status sätts direkt till `sent`** + `sent_at` sätts till nu. Ansökan syns direkt i Ansökningar-fliken.
3. Brevet visas i redigerbar textarea
4. **Erfarenhets-chips** (gröna) — erfarenheter som nämns i brevet. Klicka bort/i och omgenerera
5. **Utbildnings-chips** (gröna) + **Anekdot-chips** (amber) — samma logik
6. **Fritext-ruta** — skriv egen erfarenhet att inkludera
7. **"✨ Omgenerera brev"**-knapp
8. **"Granska svenskan"**-knapp — LanguageTool kollar grammatik/stavning (bara säkra rättningar)
9. **Feedback-ruta** — skriv feedback om brevet → `POST /api/user/ai-feedback/smart` → uppdaterar dina preferenser automatiskt
10. **Knappar**:
    - **"Kopiera"** — kopierar brevet till urklipp
    - **"Ladda ner PDF"** → `POST /api/jobs/{id}/cover-letter-pdf`
    - **"Spara i Gmail med bilagor"** → `POST /api/jobs/{id}/save-draft` — skapar Gmail-utkast med:
      1. Ämne: `Ansökan: [Jobbtitel] – [Ditt namn]`
      2. Brödtext: personligt brev
      3. Bilaga 1: Personligt brev som PDF
      4. Bilaga 2: Rätt bransch-CV som PDF
    - **"Markera skickad"** — sätter `status=sent` + `sent_at`. Redundant om man redan klickat "Ansök" (som redan sätter sent). Finns mest för manuella flöden där man sparar jobb först och ansöker utanför appen.
    - **CV-badge** — visar vilken bransch som matchades. Om inget bransch-CV matchar jobbet faller det tillbaka till **"customerservice"** (kundtjänst) som default. **Needs a decision:** är customerservice rätt fallback för alla användare, eller borde det vara konfigurerbart?

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `jobs` | ✅ | | Hämtar skrapade jobb med e-postkontakt |
| `applications` | ✅ | ✅ | Sparar ansökan (status, brev, bransch_id, gmail_draft_id) |
| `user_job_interactions` | | ✅ | Loggar viewed/skipped/applied/saved/rejected |
| `user_experiences` | ✅ | | Hämtar erfarenheter för brevgenerering |
| `user_education` | ✅ | | Hämtar utbildning för brevgenerering |
| `user_anecdotes` | ✅ | | Hämtar anekdoter/hobbys att väva in |
| `user_profiles` | ✅ | | Namn, ort, telefon, e-post för brev + signatur |
| `user_cover_letter_preferences` | ✅ | ✅ | Ton, stil, avoid/like-fraser, AI-instruktioner |
| `user_ai_feedback` | ✅ | ✅ | Sparar + hämtar feedback om brev (smart endpoint uppdaterar preferences) |
| `user_cvs` / `bransch_cvs` | ✅ | | Hämtar bransch-CV PDF för bilaga |
| `user_google_credentials` | ✅ | | Gmail OAuth-tokens för att skapa utkast |

---

## 🌐 Extern

Visar jobb från Platsbanken som **saknar kontakt-e-post** — användaren ansöker via företagets hemsida.

### Layout
Tvådelad: jobblista till vänster, detaljer till höger.

### Höger panel — tre flikar:
1. **Beskrivning** — full jobbannons, utfällbar
2. **Brev** — generera personligt brev (samma flöde som Jobb-modalen)
3. **Q&A** — ställ frågor om jobbet → `POST /api/jobs/{id}/answer-question`
   - AI:n svarar baserat på **både jobbannonsen OCH ditt CV/profil**: namn, ort, bästa CV-text (från `user_cvs`), ton och avoid-fraser (från `user_cover_letter_preferences`), plus jobbets titel/företag/beskrivning (max 2000 tecken).
   - Svar: 50–150 ord, refererar till specifika delar av annonsen och väver in din erfarenhet.
   - Snabbknappar för vanliga frågor ("Varför vill du jobba hos oss?" etc) + fritext.

### Åtgärdsknappar
- **"Hoppa över"** — loggar `action=skipped` i `user_job_interactions`. Jobbet filtreras bort från feedet (hård filtrering, inte bara nedprioriterat). Kan dock dyka upp igen vid ny scrape om samma jobb-ID skrapas igen.
- **"Avvisa"** — loggar `action=rejected`. Jobbet **permanent dolt** från feedet. Visas bara om du klickar "Visa dolda".

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `jobs` | ✅ | | Hämtar jobb UTAN e-postkontakt |
| `user_job_interactions` | ✅ | ✅ | Filtrerar bort skipped/rejected, loggar interaktioner |
| `applications` | | ✅ | Sparar om man genererar brev |
| Alla brevgenereringstabell (se Jobb ovan) | ✅ | | Samma data för brevgenerering |

---

## 📄 Mina CV

Hantera Master CV + 9 branschanpassade versioner.

### Master CV-sektion
- **"Redigera Master CV"**-knapp — öppnar fullständig redigeringsmodal
- **"Generera alla CV"**-knapp → `POST /api/cv/generate-branscher` — **regenererar ALLA 9 bransch-CV varje gång** (upsert med `on_conflict=user_id,vibe_id`). Kollar inte om CV redan finns — full omskrivning. Kräver att Master CV (erfarenheter/utbildning) finns.
- **"Ladda ner Master CV"** → `GET /api/master-cv/download-pdf`
- Statistik: antal erfarenheter, utbildningar, utmärkelser, projekt, språk

### CV-uppladdning med AI-parsning
- Ladda upp befintligt CV (PDF/DOCX/TXT) → `POST /api/cv/enhance-master`
- AI extraherar: erfarenheter, utbildning, skills
- **AI-chatt** efter uppladdning: `POST /api/cv/enhance-chat`

### Master CV Editor (modal)
- **Erfarenheter** — titel, företag, datum, bullets
- **Utbildning** — skola, examen, datum
- **Skills** — kompetenser, typ (teknisk/bransch/språk)
- **Projekt** — namn, beskrivning, GitHub/live-länkar
- **Certifieringar** — körkort, kassahantering, etc
- **Volontärarbete** — organisation, datum, bullets
- **Utmärkelser**

### Bransch-CV-kort (9 kort i grid)
- Emoji + branschnamn
- Fokusområde
- Statusbadge — "✓ CV finns" / "Inte skapat"
- **"📤 Ladda upp CV"** → `POST /api/upload/cv/{bransch_id}`
- **"📄 Visa fil"** — länk till uppladdad PDF
- **"✏️ Redigera"** — öppnar en **fritext-textarea** (monospace-font, `h-64`). Ingen strukturerad editor med bullets/sektioner — bara ren text. Huvudsakliga arbetssättet är att ladda upp PDF eller omgenerera från Master CV, inte redigera inline.

**De 9 branscherna:**

| Bransch | Emoji | Fokus |
|---------|-------|-------|
| Restaurang & Cafe | 🍽️ | Kundkontakt, service, stresshantering |
| Butik & Kassa | 🛍️ | Försäljning, kassaarbete, lager |
| Kundtjänst & Support | 📞 | Kommunikation, problemlösning |
| Tech & Kontor | 💻 | Tekniska projekt, struktur |
| Vård & Omsorg | 🏥 | Omtanke, patientsäkerhet |
| Industri & Trädgård | 🔧 | Fysiskt arbete, maskiner |
| Hotell & Reception | 🏨 | Gästservice, bokning | **⚠️ PDF saknas** — ingen `CV_Linnea_Moritz_Hotell_Reception.pdf` finns i cv_files/. Faller tillbaka till kundtjänst-CV. |
| Content & Moderation | 🛡️ | Digitalt innehåll, riktlinjer |
| Konst & Kultur | 🎨 | Kreativitet, evenemang |

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_profiles` | ✅ | | Namn, ort, foto för CV |
| `user_experiences` | ✅ | ✅ | Arbetslivserfarenheter (CRUD i editor) |
| `user_education` | ✅ | ✅ | Utbildning (CRUD i editor) |
| `user_skills` | ✅ | ✅ | Kompetenser per kategori (CRUD) |
| `user_volunteer` | ✅ | ✅ | Volontärarbete (CRUD) |
| `user_awards` | ✅ | ✅ | Utmärkelser (CRUD) |
| `user_certifications` | ✅ | ✅ | Certifieringar (CRUD) |
| `tech_projects` | ✅ | ✅ | Projekt (för tech-CV) |
| `user_experience_tags` | ✅ | ✅ | Kopplar erfarenheter → branscher med prioritet. **OBS: tabellen finns i DB men har inget UI och inga API-endpoints ännu.** Branschmatchning sker dynamiskt via `experiences.categories`-fältet istället. |
| `user_cvs` | ✅ | ✅ | Genererade bransch-CV texter |
| `bransch_cvs` | ✅ | ✅ | Bransch-CV varianter med PDF-URL |
| `user_cv_branscher` | ✅ | ✅ | Användarens branschdefinitioner |
| `user_cv_uploads` | ✅ | ✅ | Uppladdade CV-filer (max 20) |
| `user_cv_creation_conversations` | ✅ | ✅ | AI-chatt historik per CV |
| `user_cv_versions` | ✅ | ✅ | Versionshistorik per CV. **⚠️ Ska byggas ut i framtiden** — tabellen finns men populeras aldrig och har ingen restore-funktion. CV:n skrivs över direkt vid omgenerering. |
| `master_cv_exports` | | ✅ | Snapshot av hela Master CV som JSON |
| **Storage: `cv-files`** | ✅ | ✅ | PDF-filer för bransch-CVer |
| **Storage: `profile-photos`** | ✅ | | Profilbild på CV |

---

## 📬 Ansökningar

Spåra alla ansökningar och generera aktivitetsrapport för A-kassan.

### Filterflikar
- **Alla (X)** — alla ansökningar
- **📌 Sparade (X)** — bokmärkta jobb
- **✓ Skickade (X)** — inskickade ansökningar
- **🎉 Intervjuer (X)** — intervjustadiet

### Aktivitetsrapport-sektion (LIVE)
- **Stapeldiagram** — sökta jobb per dag (senaste 7 dagarna)
- **Månadsväljare** — välj månad (YYYY-MM)
- **"Ladda ner aktivitetsrapport"**-knapp → `GET /api/aktivitetsrapport?month=YYYY-MM`
  - Genererar PDF med tabell: Datum | Yrkesroll | Arbetsgivare | Omfattning | Ort
  - **⚠️ EJ VERIFIERAD med Arbetsförmedlingen/A-kassan.** Formatet är egendesignat med FPDF — ser rimligt ut men baseras inte på en officiell mall. Användaren ansvarar för att kolla med sin handläggare om det accepteras.
  - Filnamn: `Aktivitetsrapport_MÅNAD_ÅR.pdf`
  - Visar användarens namn, period, totalt antal ansökningar

### Ansökningslista
Varje ansökan visar:
- Jobbtitel + företag
- **Statusbadge** med färgkodning
- **Status-dropdown** — ändra status: 📌 Sparad → 📝 Utkast → ✓ Skickad → 🎉 Intervju → 🎊 Erbjudande / ✗ Avslag. **"Erbjudande" har ingen speciallogik** — det är bara en etikett/badge som alla andra statusar. Skyddad från nedgradering (kan inte gå tillbaka till "Sparad"). Ingen notifikation eller firande triggas.

**Expanderad vy:**
- Plats + deadline (med tidsvarnig: "3 dagar kvar", "Deadline passerad")
- **Anteckningar** — redigera och spara per ansökan. **Manuell sparning** — klicka "Spara"-knappen efter redigering. Ingen auto-save/realtids-sync.
- **Personligt brev** — visa/ladda ner sparat brev
- **"✍️ Skapa ansökan"** — för sparade jobb, öppnar ansökningsmodalen
- **"🔗 Visa annons"** — öppnar original-annonsen
- **"📧 Maila"** — mailto-länk till kontaktpersonen
- **"⬇️ Ladda ner brev"** — ladda ner brevet som textfil
- **"Ta bort"**-knapp

### Ansökningsflöde (apply-with-cv)
```
1. Användare klickar "✨ Ansök" på jobbkort
2. Backend: POST /api/jobs/{id}/apply-with-cv
   a. Duplikatkontroll — om redan sökt → 409 "Du har redan sökt detta jobb"
   b. Väljer bästa bransch-CV (match_job_to_bransch)
   c. Genererar personligt brev via Claude
   d. Sparar application (status='sent') + interaction (action='applied')
   e. Returnerar brev, bransch, CV-info
3. Frontend: Öppnar ansökningsmodal
4. "Markera skickad" → POST /api/applications (upsert, kontrollerar respons)
5. fetchApplications() → ansökan syns direkt i Ansökningar-fliken
```

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `applications` | ✅ | ✅ | Alla ansökningar — status, notes, cover_letter, sent_at, bransch_id |
| `jobs` | ✅ | | Jobbdata (titel, företag, ort, working_hours) via LEFT JOIN |

**Nyckelkolumner i `applications`:**
- `status` — draft/sent/saved/skipped/interview/rejected/offer
- `sent_at` — TIMESTAMPTZ, sätts vid "Markera skickad" eller auto vid apply-with-cv
- `cover_letter` — sparat brevtext
- `notes` — fria anteckningar per ansökan
- `bransch_id` — vilken bransch-CV som användes
- `gmail_draft_id` — Gmail utkast-ID om det sparades
- `apply_method` — hur man sökte: platsbanken_email, external_website, linkedin, email_direct, in_person, phone, other
- `custom_title` — override jobbtitel (för manuella ansökningar eller redigeringar)
- `custom_company` — override företagsnamn
- `custom_location` — override ort
- `apply_date` — när man faktiskt sökte (user-editable, separat från auto-satt sent_at)
- `UNIQUE(user_id, job_id)` — en ansökan per jobb per användare

---

## 📊 Statistik

Dashboard med 4 sifferkort:

| Kort | Färg | Data |
|------|------|------|
| Jobb hittade | Rosa | Totalt antal skrapade jobb |
| Ansökningar skickade | Grön | Antal med status "skickad" |
| Intervjuer | Amber | Antal med status "intervju" |
| CV-versioner | Lila | Antal genererade bransch-CVer |

**Supabase-koppling:**

| Tabell | Läser | Syfte |
|--------|-------|-------|
| `jobs` | ✅ | Räknar totalt antal jobb |
| `applications` | ✅ | Räknar per status (skickad, intervju, sparad) |
| `user_cvs` | ✅ | Räknar antal bransch-CVer |

---

## ⚙️ Preferenser

Styr vilka jobb som skrapas och visas.

### Positiva sökord (blå chips)
- Förvalda chips från quiz: Servering, Kundtjänst, Butik, Lager, etc
- Inmatningsfält — stödjer kommaseparerade listor ("Hotell, Lärare, Trädgård" → 3 chips)

### Negativa sökord (röda chips)
- Kategorifilter: Hälsa & Vård, Utbildning, Teknik, Juridik, etc
- Sökfilter + inmatningsfält (kommaseparerat)
- **⚠️ Filtrering sker CLIENT-SIDE** — Platsbanken-API:t tar inte emot negativa sökord. Jobben skrapas först, sedan filtreras de bort i frontend via `String.includes()` mot titel + företag + beskrivning. Det betyder att jobb fortfarande laddas ner men aldrig visas.

### Arbetstid (multi-select toggles)
- Heltid / Deltid / Extra/Timanställning

### Dealbreakers (multi-select toggles)
- Nattarbete / Helgarbete / Telefonarbete / Tunga lyft / Utomhusarbete / Ingen
- **⚠️ Enkel keyword-match, ingen NLP.** Frontend gör `String.includes()` mot jobbets titel + beskrivning med hårdkodad mappning: `natt` → "natt", `helg` → "helg", `telefon` → "telefon", `tunga_lyft` → "tunga lyft", `utomhus` → "utomhus". Kan ge false positives (t.ex. "Nattavdelningen" filtreras bort) och false negatives (t.ex. "kvällsarbete" fångas inte).

**"Spara preferenser"**-knapp → `POST /api/user/preferences`

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_job_preferences` | ✅ | ✅ | search_keywords, excluded_keywords, job_types, quiz_answers |

**Nyckelkolumner i `user_job_preferences`:**
- `search_keywords` TEXT[] — positiva sökord (blå chips), påverkar Platsbanken-skrapning
- `excluded_keywords` TEXT[] — negativa sökord (röda chips), filtrerar bort jobb
- `job_types` TEXT[] — heltid/deltid/extra
- `quiz_answers` JSONB — all data från quiz (dealbreakers, lön, anställningsform, etc.)
- `preferred_locations` TEXT[] — valda kommuner (sätts från Platser-sidan)

---

## 📍 Platser

Välj vilka kommuner du vill söka jobb i.

### Snabbval
- **"✓ Hela Sverige"** — toggle
- **"✓ Distans / Remote"** — toggle

### Län-picker
- Sök bland alla 290 kommuner
- Expanderbara län med "Markera alla"
- Checkbox per kommun

**"Spara platser"**-knapp → `POST /api/user/locations`

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_job_preferences` | ✅ | ✅ | `preferred_locations` TEXT[] + `quiz_answers.location` JSONB |

**Hur det hänger ihop med skrapning:**
- Valda kommuner → backend skrapar Platsbanken med dessa kommun-ID:n
- Sparas som kommun-ID:n i `quiz_answers.location` och som namn i `preferred_locations`

---

## ✍️ Personligt brev (stilpreferenser)

Styr hur AI:n skriver dina personliga brev. **All feedback härifrån påverkar ALLA brevgenereringar — både på Jobb-sidan och Extern-sidan.**

### Träningsbrev
- Ladda upp (PDF/DOCX) eller klistra in text → `POST /api/user/training-letters`
- AI analyserar din stil: ton, struktur, favoritfraser (Sonnet, 700 tokens)
- **1 brev räcker** för att starta stilanalys. Fler brev = rikare analys (AI noterar skillnader mellan breven, samlar fler fraser). Max 20 brev.
- **1 brev**: `analyze_writing_tone_rich()` — extraherar ton, meningsstruktur, 3-6 unika fraser, klichéer du undviker, öppningsstil
- **2+ brev**: `analyze_writing_tone_multi()` — analyserar alla brev tillsammans, noterar stilskillnader ("Brev 1: Formellt. Brev 2: Personligt")
- Lista med uppladdade brev + ta bort-knapp

### Fraser jag gillar (blå chips)
- Fraser du VILL att AI:n använder
- Input + "Lägg till" / X för att ta bort
- `PATCH /api/user/letter-style/phrases` (action: add, list: phrases)

### Ämnen att aldrig nämna
- Nyckelord AI:n ska undvika helt (t.ex. "konst", "Shopify")

### Fraser jag inte vill ha (röda chips)
- Fraser AI:n ALDRIG ska använda
- Förvalda AI-klichéer att klicka och blockera: "solid erfarenhet", "brinner för", "gedigen kompetens", "passionerad", "vittnar om", "starkt engagemang", "unik möjlighet", "spännande utmaning"
- `PATCH /api/user/letter-style/phrases` (action: add, list: avoid)

### Egna instruktioner till AI
- Stor textarea för fria instruktioner
- T.ex. ordersättningar: "Mentorerade" → "Handledde", "NGO:er" → "ideella organisationer"
- **"Spara instruktioner"**-knapp → `PATCH /api/user/letter-style`

### AI Feedback
- **Fritext-ruta** — skriv feedback, t.ex. "Gör breven kortare" eller "Säg aldrig rondera"
- **"Skicka feedback"**-knapp → `POST /api/user/ai-feedback/smart`
- AI (Claude) tolkar feedbacken → extraherar avoid/like-fraser → sparar strukturerat
- Feedback sparas i `user_ai_feedback` OCH uppdaterar `user_cover_letter_preferences`
- **`is_active`** — feedback är aktiv tills du manuellt tar bort den (soft-delete via DELETE-endpoint). **Ingen auto-expiry eller åldersbaserad deaktivering.** Senaste 10 aktiva feedback-rader hämtas vid brevgenerering.
- **`applies_to_branscher`** — kan sättas manuellt vid POST. **AI:n (smart feedback) sätter den INTE automatiskt** — defaultar till `[]` (gäller alla branscher). **Ska byggas ut i framtiden?** Needs a decision: ska smart feedback extrahera bransch från texten?
- **Historik** — lista med sparad feedback + ta bort-knapp

### Anekdoter & hobbys
- Lista med sparade anekdoter/hobbys
- Varje post: titel, typ (anekdot/hobby), nyckelord
- **"+ Lägg till anekdot"** → `POST /api/user/anecdotes` (max 30 per användare, godtycklig gräns — inte tokenrelaterad). AI:n väver in **alla relevanta anekdoter/hobbys** per brev (keyword-matchade mot jobbannonsen). Irrelevanta hoppas över.
- **"✎ Redigera"**-knapp per anekdot — inline-redigering av titel, typ, innehåll, nyckelord → `PATCH /api/user/anecdotes/{id}`
- **"✕ Ta bort"**-knapp → `DELETE /api/user/anecdotes/{id}`
- **"TXT"**-knapp — exportera alla anekdoter/hobbys som textfil → `GET /api/user/anecdotes/export?format=txt`
- **"PDF"**-knapp — exportera som formaterad PDF → `GET /api/user/anecdotes/export?format=pdf`
- AI väljer relevanta anekdoter per jobb baserat på nyckelordsmatchning

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_cover_letter_preferences` | ✅ | ✅ | Huvudtabell för brevstil |
| `user_ai_feedback` | ✅ | ✅ | Sparad feedback som AI läser vid varje brevgenerering |
| `user_anecdotes` | ✅ | ✅ | Personliga anekdoter/hobbys (max 30) |
| `user_training_letters` | ✅ | ✅ | Uppladdade träningsbrev |
| **Storage: `training-letters`** | ✅ | ✅ | PDF/DOCX-filer för träningsbrev |

**Nyckelkolumner i `user_cover_letter_preferences`:**
- `liked_phrases` TEXT[] — fraser AI ska gärna använda
- `avoid_phrases` JSONB — fraser AI ALDRIG ska använda (röda chips)
- `never_mention` TEXT[] — ämnen att aldrig nämna
- `custom_ai_instructions` TEXT — fria instruktioner (textarea)
- `tone` TEXT — "professional_friendly" / "formal" / "casual"
- `max_words` INT — maxlängd på brev
- `writing_style` TEXT — AI-analyserad stilbeskrivning från träningsbrev
- `opening_style` TEXT — hur brev öppnas
- `greeting_style` TEXT — "Hej!" / "Hej [Company]!"
- `signature_style` TEXT — "Med vänliga hälsningar"
- `sign_off_name/phone/email` TEXT — signaturuppgifter
- `priority_experiences_per_vibe` JSONB — vilka erfarenheter som prioriteras per bransch

**Nyckelkolumner i `user_ai_feedback`:**
- `feedback_text` TEXT — sammanfattning av feedback
- `feedback_type` TEXT — "cover_letter" / "new_bransch_request" / "exclude_jobs" / "general"
- `is_active` BOOLEAN — aktiv feedback läses vid varje brevgenerering
- `applies_to_branscher` TEXT[] — om feedbacken bara gäller vissa branscher

**Dataflöde vid brevgenerering:**
```
generate_cover_letter() hämtar:
  1. user_cover_letter_preferences → ton, fraser, avoid, instruktioner
  2. user_ai_feedback (is_active=true, limit 10) → senaste feedback
  3. user_anecdotes → relevanta anekdoter baserat på nyckelord
  → Allt matas in i Claude-prompten som kontext
```

**Feedback-flöde (synk mellan sidor):**
```
Jobb-sidan feedback → POST /api/user/ai-feedback/smart → Claude tolkar →
  1. Sparar i user_ai_feedback (feedback_text)
  2. Uppdaterar user_cover_letter_preferences (avoid_phrases, liked_phrases)
  → Ändringen syns DIREKT i Personligt brev-sidan (röda/blå chips)
  → Och används vid nästa brevgenerering
```

---

## 📝 Brevformat

Kontrollera layouten på genererade brev.

### Förhandsgranskning
- Live-preview av brevformat med hälsning, innehåll, avslutning, signatur

### Formulärfält
- **Hälsning** — t.ex. "Hej!"
- **Avslutningsfras** — t.ex. "Med vänliga hälsningar,"
- **Namn i signatur**
- **Telefon**
- **E-post**
- **Maximal ordlängd** — nummer (default 200)

**"Spara"**-knapp → `PATCH /api/user/letter-style`

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_cover_letter_preferences` | ✅ | ✅ | greeting_style, signature_style, max_words, sign_off_* |

---

## 📬 Gmail

Koppla ditt Gmail-konto för att skapa utkast direkt från appen.

### Ej kopplad
- 3 samtyckes-checkboxar (alla obligatoriska)
- **"Anslut Gmail"**-knapp → `GET /api/gmail/auth-url` → Google OAuth-popup

### Kopplad (grön banner)
- ✓ "Gmail kopplad" + din Gmail-adress
- Vad appen KAN/INTE kan göra
- **"Koppla bort Gmail"**-knapp → `POST /api/gmail/disconnect`

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_google_credentials` | ✅ | ✅ | OAuth client_id/secret, access/refresh_token, gmail_address, is_connected |

**Gmail-flöde vid "Spara i Gmail med bilagor":**
```
1. refresh_gmail_token() — hämtar access_token, auto-refreshar om <5 min kvar
2. Om refresh misslyckas → detaljerat felmeddelande (inte tyst fel):
   - "Gmail är inte kopplat" / "refresh token saknas" / "token kunde inte förnyas"
3. Skapa Gmail draft via Gmail API med:
   - Ämne: "Ansökan: [Jobbtitel] – [Namn]"
   - Body: personligt brev
   - Bilaga 1: Personligt_Brev_[Förnamn]_[Efternamn].pdf (genereras on-the-fly)
   - Bilaga 2: CV_[Förnamn]_[Efternamn]_[Bransch].pdf (BARA från lokal disk v2/api/cv_files/)
     ⚠️ Om PDF saknas på disk → bilagan hoppas över TYST (inget fel, utkastet skapas utan CV).
     Ingen fallback till Supabase Storage.
4. Om Gmail API returnerar 401 → "Token har gått ut. Koppla bort och koppla om Gmail."
5. Spara gmail_draft_id i applications-tabellen
```

---

## ✨ Quiz (onboarding)

Steg-för-steg-guide för nya användare.

### Frågor (15+ steg)

**Personuppgifter:**
1. Namn
2. Telefonnummer
3. Var bor du?
4. Ålder (16-19 / 20-25 / 26-35 / 36-50 / 50+)
5. Körkort? (Manuell / Automat / Nej)
6. Egen bil?
7. Egen dator?
8. Tidigaste startdatum?
9. Utbildningsnivå?
10. LinkedIn-profil?
11. Portfolio/webbsida?

**Jobbpreferenser:**
12. Vad söker du? (multi-select chips)
13. Fritextsökning (kommaseparerade sökord)
14. Arbetstid
15. Anställningsform
16. Längd
17. Lön
18. Dealbreakers

### Dataflöde
```
Quiz svar sparas i localStorage som job_preferences
  ↓ vid slutförande ↓
POST /api/user/profile-from-quiz → user_profiles (namn, telefon, ort, körkort, etc.)
POST /api/user/preferences → user_job_preferences (sökord, dealbreakers, quiz_answers JSONB)
  ↓
Automatisk scrape av jobb triggas
```

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_profiles` | | ✅ | Skapas/uppdateras med personuppgifter från quiz |
| `user_job_preferences` | | ✅ | Alla jobbpreferenser sparas — search_keywords, quiz_answers JSONB |

---

## 👤 Profil

Personuppgifter och kontoinställningar.

### Personuppgifter
- **Namn** → `PATCH /api/profile`
- **Telefon** → `PATCH /api/profile`
- **E-post** — skrivskyddat
- **Ort** → `PATCH /api/profile`

### Födelsedatum
- Datumväljare → `PATCH /api/profile/birth-date`
- Beräknad ålder visas

### Profilbild
- Uppladdning → `POST /api/upload/profile-photo`

### E-postsignatur
- Textarea → `PATCH /api/profile/signature`

### Platsbaser (per region)
- Regionala adresser — om jobbet är i Stockholm, använd Stockholmsadress i brevet

### GDPR
- **Exportera all data** — JSON
- **Radera konto** — `SELECT delete_user_data('user_id')` (raderar ALLT i 21 tabeller)

**Supabase-koppling:**

| Tabell | Läser | Skriver | Syfte |
|--------|-------|---------|-------|
| `user_profiles` | ✅ | ✅ | full_name, phone, location, photo_url, birth_date, email_signature, location_by_region |
| **Storage: `profile-photos`** | ✅ | ✅ | Profilbild (JPG/PNG, max 10MB) |

---

## Teknisk arkitektur

| Komponent | Teknik |
|-----------|--------|
| Frontend | React + Tailwind CSS (single-page, CDN) |
| Backend | FastAPI (Python, Vercel serverless, 60s timeout) |
| Databas | Supabase PostgreSQL + Storage (3 buckets) |
| AI Brev | Claude Sonnet (fallback: Haiku → mall) |
| AI CV-chatt | Claude Haiku |
| AI Feedback-tolkning | Claude (smart endpoint) |
| Grammatik | LanguageTool API (bara säkra rättningar) |
| Svenska grammatik | GPT-SW3 via HuggingFace (post-generation check) |
| Jobbkälla | Platsbanken API (Arbetsförmedlingen) |
| E-post | Gmail API (användarens egna OAuth) |
| Deploy | Vercel Pro |

---

## Komplett databasöversikt

### Huvudtabeller (21 st)

| Tabell | Syfte | Sidor som använder |
|--------|-------|-------------------|
| `jobs` | Skrapade jobb från Platsbanken | Jobb, Extern, Ansökningar, Statistik |
| `applications` | Ansökningar med status-tracking | Jobb, Extern, Ansökningar, Statistik |
| `user_profiles` | Personuppgifter + foto | Alla sidor (brev, CV, profil) |
| `user_experiences` | Arbetslivserfarenheter | Mina CV, Jobb (brevgenerering) |
| `user_education` | Utbildning | Mina CV, Jobb (brevgenerering) |
| `user_skills` | Kompetenser per kategori | Mina CV |
| `user_volunteer` | Volontärarbete | Mina CV |
| `user_awards` | Utmärkelser | Mina CV |
| `user_certifications` | Certifieringar | Mina CV |
| `user_cvs` | Genererade bransch-CV texter | Mina CV, Jobb (bilaga) |
| `bransch_cvs` | Bransch-CV varianter med PDF | Mina CV, Jobb (bilaga) |
| `user_cv_branscher` | Branschdefinitioner per user | Mina CV |
| `user_experience_tags` | Erfarenhet→bransch koppling — **⚠️ Ska byggas ut i framtiden** (tabell finns, inget UI/API) | Mina CV |
| `user_cover_letter_preferences` | Brevstil och preferenser | Personligt brev, Brevformat, Jobb, Extern |
| `user_ai_feedback` | AI-feedback från användaren | Personligt brev, Jobb |
| `user_anecdotes` | Anekdoter/hobbys | Personligt brev, Jobb (brevgenerering) |
| `user_job_preferences` | Sökord, platser, dealbreakers | Preferenser, Platser, Quiz |
| `user_google_credentials` | Gmail OAuth-tokens | Gmail, Jobb (utkast) |
| `user_training_letters` | Uppladdade träningsbrev | Personligt brev |
| `user_cv_uploads` | Uppladdade CV-filer | Mina CV |
| `user_job_interactions` | Visad/hoppat/avslagen/sparad | Jobb, Extern |

### Specialtabeller

| Tabell | Syfte |
|--------|-------|
| `master_cv_exports` | Snapshot av Master CV som JSON |
| `user_cv_versions` | Versionshistorik per CV — **⚠️ Ska byggas ut i framtiden** (tabell finns, aldrig populerad) |
| `user_cv_creation_conversations` | AI-chatt historik |
| `cv_industry_templates` | Mallar: traditional, artist, tech, academic — **⚠️ Ska byggas ut i framtiden** (4 mallar seedade, appen hårdkodar "traditional") |
| `tech_projects` | Projekt (tech-CV) |
| `tech_certifications` | Certifieringar (tech-CV) — **⚠️ Ska byggas ut i framtiden** (separat från generella certifieringar, inget UI) |
| `artist_exhibitions` | Utställningar (konstnärs-CV) — **⚠️ Ska byggas ut i framtiden** (tabell finns, inget UI) |
| `artist_residencies` | Residencies (konstnärs-CV) — **⚠️ Ska byggas ut i framtiden** (tabell finns, inget UI) |
| `artist_collections` | Samlingar (konstnärs-CV) — **⚠️ Ska byggas ut i framtiden** (tabell finns, inget UI) |
| `academic_publications` | Publikationer (akademiskt CV) — **⚠️ Ska byggas ut i framtiden** (tabell finns, inget UI) |

### Storage-buckets (3 st)

| Bucket | MIME-typer | Max storlek | Syfte |
|--------|-----------|-------------|-------|
| `profile-photos` | image/jpeg, png, webp | 10 MB | Profilbilder |
| `training-letters` | pdf, docx, doc, txt | 50 MB | Träningsbrev |
| `cv-files` | pdf, docx, doc, txt, rtf, odt | 50 MB | Bransch-CV PDF:er |

---

*Allt UI-text på svenska. Designat för neurodivergenta jobbsökare — minimera beslut, ge struktur, ett gränssnitt.*

---

## Changelog

### v2.1 — 24 feb 2026

**Bugfixar:**
- **Sparade jobb filtreras från flödet** — `/api/jobs` filtrerar nu status `saved` (inte bara sent/draft)
- **Sparade jobb försvinner inte efter scrape** — `/api/scrape` gömmer bara jobb med terminal status, inte saved
- **Duplikatkontroll vid ansökan** — `apply-with-cv` returnerar 409 om du redan sökt ett jobb
- **Frontend hanterar 409** — visar tydligt "Du har redan sökt detta jobb" istället för generiskt fel
- **Markera skickad fixad** — `saveApplication()` kontrollerar nu respons-status, visar felmeddelande vid misslyckande
- **apply-with-cv verifierar DB-write** — loggar varning om ansökan inte sparades, returnerar `application_saved` flagga
- **fetchApplications() direkt efter apply** — ansökningar syns omedelbart i Ansökningar-fliken
- **Auth-krav på endpoints** — `POST /api/applications`, `POST/DELETE /api/jobs/{id}/save` kräver inloggning (inte "default_user")
- **GET /api/applications** — returnerar tom lista om ej inloggad (inte alla användares data)
- **save_job upsert** — använder `on_conflict` för att undvika dubbletter vid race conditions

**Nya features:**
- **Redigera anekdoter** — inline-redigering av titel, typ, innehåll, nyckelord (✎ ikon)
- **Exportera anekdoter** — TXT och PDF-knappar i anekdotsektionen
- **PATCH /api/user/anecdotes/{id}** — ny endpoint för att uppdatera anekdoter
- **GET /api/user/anecdotes/export** — ny endpoint för TXT/PDF-export
- **Max 30-gräns** — backend kontrollerar limit innan POST (utöver DB-trigger)

### v2.2 — 24 feb 2026

**Bugfixar:**
- **Markera skickad: sent_at saknades** — `POST /api/applications` satte aldrig `sent_at` vid status='sent'. Nu sätts det automatiskt. Påverkade Aktivitetsrapport och tidsvisning.
- **Markera skickad: ingen feedback** — Knappen hade ingen loading- eller success-state. Nu visar den "Sparar..." under sparande och "✓ Markerad som skickad" vid lyckat resultat.
- **Chip-highlighting för löst** — Erfarenhets-chips (gröna) och anekdot-chips (orange) matchades på vilken 3-bokstavsord som helst. Nu krävs: 5+ tecken, svenska stoppord filtreras bort, signatur exkluderas, och anekdoter kräver 2+ nyckelordsmatchningar.
- **"Ronder" i prompt** — Hårdkodad "gå ronder" i SWEDISH_LANGUAGE_RULES överskred användarens avoid_phrases. Ersatt med "gå runda".
- **Användarpreferenser övertrumfar allt** — Prompten instruerar nu explicit att "Fraser jag INTE vill ha" ALLTID övertrumfar alla andra regler, även hårdkodade "korrekta" fraser.

**Förbättringar:**
- **Jobb sorterade efter deadline** — Inom varje bucket (e-post/utan e-post, nya/hoppade) sorteras jobb nu med närmast deadline först.

### v2.3 — 24 feb 2026

**Kritiska bugfixar:**
- **Ansökningar visades inte (0 överallt)** — Tre samverkande buggar fixade:
  1. `GET /api/applications` returnerade `200 OK` med tom lista när token var utgången (istället för 401). Frontend trodde det fanns 0 ansökningar.
  2. `get_applications_from_db` hade noll error-logging och ingen fallback — om PostgREST-frågan misslyckades (t.ex. schema-cache stale efter nya kolumner) returnerades tyst `[]`.
  3. `authFetch` hade ingen auto-refresh — utgångna tokens orsakade tysta misslyckanden överallt.
- **apply-with-cv sparade inte ansökan** — `user_id` var valfritt. Om token gått ut blev `user_id = None`, brevgenereringen fungerade men ansökan sparades aldrig i DB. Nu krävs auth (401 om inte inloggad).
- **"Kunde inte spara jobbet"** — `save_job` INSERT saknade `on_conflict=user_id,job_id`, race conditions kunde orsaka duplicate key violation.
- **Utbildnings-chips false positive** — "International School of the Stockholm Region" markerades grön för att "Stockholm" förekom i brevet. Nu krävs 2+ signifikanta ord (samma logik som erfarenhets-chips).

**Förbättringar:**
- **authFetch auto-refresh** — Vid 401 refreshas token automatiskt via `POST /api/auth/refresh` och requesten körs om. Shared promise förhindrar parallella refresh-anrop.
- **GET /api/applications returnerar 401** — Triggar authFetch auto-refresh istället för att tyst returnera tom lista.
- **get_applications_from_db fallback** — Om PostgREST embedded query (`select=*,jobs(...)`) misslyckas, körs en enklare query utan join + batch-fetch av jobb separat. Error loggas alltid.
- **Nya kolumner i applications** — `apply_method`, `custom_title`, `custom_company`, `custom_location`, `apply_date` (tillagda i DB + schema).

### v2.4 — 24 feb 2026

**Bugfixar:**
- **Försvarsmakten slapp igenom "Militär"-filter** — Negativa sökord kollade bara titel + beskrivning, inte företagsnamn. Nu kollas titel + företag + beskrivning på både Jobb- och Extern-sidan.
- **Aktivitetsrapport kraschade** — Ingen auth-kontroll (user_id=None → frågade alla ansökningar), plus Unicode-tecken i jobbtitlar/företagsnamn orsakade Latin-1 encoding-fel i PDF. Nu krävs auth + `_safe_pdf_text()` sanerar all text.
- **Master CV PDF kraschade** — Samma Unicode-problem: em-dash, typografiska citattecken, m.m. från DB-data kraschade fpdf2. `safe_text()` delegerar nu till `_safe_pdf_text()` som ersätter/filtrerar non-Latin-1 tecken.
- **Projekt/certifieringar saknades i Master CV PDF** — `project_name` och `certification_name` matchar nu DB-kolumnnamn (inte bara generiska `name`/`title`).

### v2.5 — 24 feb 2026

**Bugfixar:**
- **Kvalifikationskontroll använde hårdkodad "Gymnasium"** — `qualification-check` endpointen skickade alltid `Utbildning: Gymnasium` till Haiku oavsett användarens faktiska utbildning. Nu hämtas riktig utbildning från `user_education`.
- **Kvalifikationskontroll missade erfarenheter** — Bara 8 erfarenheter hämtades (limit=8). Om vårderfarenhet låg som nr 9+ sågs den aldrig. Limit borttagen — alla erfarenheter skickas nu.
- **Falskt "saknar kvalifikationer"-varning** — Kombination av hårdkodad utbildning + trunkerade erfarenheter gjorde att Haiku felaktigt sa att användaren saknade relevant erfarenhet (t.ex. äldrevård).
