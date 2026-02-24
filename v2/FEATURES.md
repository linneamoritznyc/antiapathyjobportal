# Platsbanken-ai — Funktioner & UX per sida

> Uppdaterad: 24 feb 2026

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
- Tillbaka till inloggning-länk

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

Jobb- och Extern-flikarna visar antal hittade jobb. Ansökningar visar antal sparade.

---

## 📧 Jobb

Visar jobb som skrapats från Platsbanken och som har **kontakt-e-post** (= kan sökas via Gmail).

### Toppsektion
- **Sökfält** — filtrerar på titel, företag, plats (klientside)
- **Prioritetsfilter** — dropdown: Alla / Akut / Snart / Normal
- **Sortering** — dropdown: deadline / senaste / etc
- **"Visa dolda"** — toggle för att se jobb du redan hoppat över/avvisat

### Jobbkort (12 per sida, grid-layout)
Varje kort visar:
- **Prioritetsbadge** — ⚡ Akut (röd) / ⏰ Snart (amber) / ✓ Normal
- **📌 Spara-knapp** — bokmärker jobbet → `POST /api/jobs/{id}/save`
- **Deadline** — datum + färgkodad badge (röd = idag, amber = inom 7 dagar)
- **Jobbtitel**
- **Företagsnamn**
- **Ort**
- **Kontakt-epost** (grön badge)
- **"✨ Ansök"**-knapp — öppnar ansökningsmodalen (se nedan)
- **↗ Extern länk** — öppnar originalannonsen på Platsbanken

### Pagination
- 12 jobb per sida
- "Ladda fler"-knapp i botten

### Ansökningsmodal (öppnas vid "✨ Ansök")
1. AI genererar personligt brev via `POST /api/jobs/{id}/apply-with-cv`
2. **Kvalifikationsvarning** — om Haiku bedömer att du inte matchar (t.ex. kräver legitimation) visas varning INNAN credits används. Tre val: Sök ändå / Hoppa över / Filtrera bort liknande
3. Brevet visas i redigerbar textarea
4. **Erfarenhets-chips** — gröna chips för erfarenheter som nämns i brevet. Klicka bort/i och omgenerera
5. **Utbildnings-chips** (grön) + **Anekdot-chips** (amber) — samma logik
6. **Fritext-ruta** — skriv egen erfarenhet att inkludera
7. **"✨ Omgenerera brev"**-knapp — genererar nytt brev med uppdaterade val
8. **"Granska svenskan"**-knapp — LanguageTool kollar grammatik/stavning
9. **Knappar**:
   - **"Kopiera"** — kopierar brevet till urklipp
   - **"Ladda ner PDF"** → `POST /api/jobs/{id}/cover-letter-pdf`
   - **"Spara i Gmail med bilagor"** → `POST /api/jobs/{id}/save-draft` — skapar Gmail-utkast med:
     1. Ämne: `Ansökan: [Jobbtitel] – [Ditt namn]`
     2. Brödtext: personligt brev
     3. Bilaga 1: Personligt brev som PDF
     4. Bilaga 2: Rätt bransch-CV som PDF
   - **CV-badge** — visar vilken bransch som matchades (t.ex. "Restaurang & Cafe")

---

## 🌐 Extern

Visar jobb från Platsbanken som **saknar kontakt-e-post** — användaren ansöker via företagets hemsida, men appen hjälper med brev + CV.

### Layout
Tvådelad: jobblista till vänster, detaljer till höger.

### Höger panel — tre flikar:
1. **Beskrivning** — full jobbannons, utfällbar
2. **Brev** — generera personligt brev (samma flöde som Jobb-modalen). Knappar: Kopiera / Ladda ner PDF / Spara i Gmail
3. **Q&A** — ställ frågor om jobbet (t.ex. "Varför vill du jobba här?")
   - Inmatningsfält + **"Ställ fråga"**-knapp → `POST /api/jobs/{id}/answer-question`
   - AI svarar baserat på din profil + jobbannonsen
   - Kopiera-knapp för svaren

### Åtgärdsknappar
- **"Hoppa över"** — skickar jobbet till slutet
- **"Avvisa"** — döljer jobbet permanent

---

## 📄 Mina CV

Hantera Master CV + 9 branschanpassade versioner.

### Master CV-sektion
- **"Redigera Master CV"**-knapp — öppnar fullständig redigeringsmodal
- **"Generera alla CV"**-knapp → `POST /api/cv/generate-branscher` — AI genererar alla 9 bransch-CVer
- **"Ladda ner Master CV"** → `GET /api/master-cv/download-pdf`
- **Statistik**: antal erfarenheter, utbildningar, utmärkelser, projekt, språk

### CV-uppladdning med AI-parsning
- Ladda upp befintligt CV (PDF/DOCX/TXT) → `POST /api/cv/enhance-master`
- AI extraherar: erfarenheter, utbildning, skills → fyller i Master CV automatiskt
- **AI-chatt** efter uppladdning — fråga om förslag, be om ändringar:
  - Skriv t.ex. *"Jag jobbar inte längre på Ica Maxi"* → AI uppdaterar
  - `POST /api/cv/enhance-chat`

### Master CV Editor (modal)
Redigera varje sektion:
- **Erfarenheter** — titel, företag, datum, beskrivning, bullet points. Lägg till / redigera / ta bort
- **Utbildning** — skola, examen, datum. Lägg till / redigera / ta bort
- **Skills** — kompetenser, typ (teknisk/bransch/språk). Lägg till / redigera / ta bort
- **Projekt** — namn, beskrivning, GitHub/live-länkar
- **Certifieringar** — körkort, kassahantering, första hjälpen, etc
- **Volontärarbete** — organisation, datum, bullets
- **Utmärkelser**

### Bransch-CV-kort (9 kort i grid)
Varje kort visar:
- **Emoji + branschnamn** (t.ex. 🍽️ Restaurang & Cafe)
- **Fokusområde** (t.ex. "Kundkontakt, stresshantering, teamwork")
- **Statusbadge** — "✓ CV finns" (grön) eller "Inte skapat"
- **"📤 Ladda upp CV"**-knapp — ladda upp egen PDF → `POST /api/upload/cv/{bransch_id}`
- **"📄 Visa fil"** — länk till uppladdad PDF
- **"✏️ Redigera"** — öppnar texteditor för CV-texten

**De 9 branscherna:**

| Bransch | Emoji | Fokus |
|---------|-------|-------|
| Restaurang & Cafe | 🍽️ | Kundkontakt, service, stresshantering |
| Butik & Kassa | 🛍️ | Försäljning, kassaarbete, lager |
| Kundtjänst & Support | 📞 | Kommunikation, problemlösning |
| Tech & Kontor | 💻 | Tekniska projekt, struktur |
| Vård & Omsorg | 🏥 | Omtanke, patientsäkerhet |
| Industri & Trädgård | 🔧 | Fysiskt arbete, maskiner |
| Hotell & Reception | 🏨 | Gästservice, bokning |
| Content & Moderation | 🛡️ | Digitalt innehåll, riktlinjer |
| Konst & Kultur | 🎨 | Kreativitet, evenemang |

---

## 📬 Ansökningar

Spåra alla ansökningar och generera aktivitetsrapport för A-kassan.

### Filterflikar
- **Alla (X)** — alla ansökningar
- **📌 Sparade (X)** — bokmärkta jobb
- **✓ Skickade (X)** — inskickade ansökningar
- **🎉 Intervjuer (X)** — intervjustadiet

### Aktivitetsrapport-sektion
- **Stapeldiagram** — sökta jobb per dag (senaste 7 dagarna)
- **Månadsväljare** — välj månad (YYYY-MM)
- **"Ladda ner aktivitetsrapport"**-knapp → `GET /api/aktivitetsrapport?month=YYYY-MM`
  - Genererar PDF med tabell: Datum | Yrkesroll | Arbetsgivare | Omfattning | Ort
  - Matchar Arbetsförmedlingens format — redo för A-kassan

### Ansökningslista
Varje ansökan visar:
- Jobbtitel + företag
- **Statusbadge** med färgkodning
- **Status-dropdown** — ändra status:
  - 📌 Sparad → 📝 Utkast → ✓ Skickad → 🎉 Intervju → 🎊 Erbjudande / ✗ Avslag
  - `PATCH /api/applications/{id}`

**Expanderad vy:**
- Plats + deadline
- **Anteckningar** — redigera och spara per ansökan
- **Personligt brev** — visa/ladda ner sparat brev
- **"Ta bort"**-knapp → `DELETE /api/applications/{id}`

---

## 📊 Statistik

Dashboard med 4 sifferkort:

| Kort | Färg | Data |
|------|------|------|
| Jobb hittade | Rosa | Totalt antal skrapade jobb |
| Ansökningar skickade | Grön | Antal med status "skickad" |
| Intervjuer | Amber | Antal med status "intervju" |
| CV-versioner | Lila | Antal genererade bransch-CVer |

Plus:
- **Sparade jobb** (blå badge)
- **Deadline idag** (röd badge)

---

## ⚙️ Preferenser

Styr vilka jobb som skrapas och visas.

### Positiva sökord (blå chips)
- Förvalda chips från quiz: Servering, Kundtjänst, Butik, Lager, Kontor, IT/Tech, Vård, Hotell, Barn, Skola, Trädgård, Städ
- **Inmatningsfält + "Lägg till"** — stödjer kommaseparerade listor (t.ex. "Hotell, Lärare, Trädgård" → 3 chips)
- X-knapp på varje chip för att ta bort

### Negativa sökord (röda chips)
- Kategorifilter: Hälsa & Vård, Utbildning, Teknik, Juridik, etc
- Sökfilter för att hitta nyckelord
- **Inmatningsfält + "Lägg till"** — stödjer kommaseparerade listor
- X-knapp på varje chip

### Arbetstid (multi-select toggles)
- Heltid
- Deltid
- Extra/Timanställning

### Dealbreakers (multi-select toggles)
- Nattarbete / Helgarbete / Telefonarbete / Tunga lyft / Utomhusarbete / Ingen

**"Spara preferenser"**-knapp → `POST /api/user/preferences`

---

## 📍 Platser

Välj vilka kommuner du vill söka jobb i.

### Snabbval
- **"✓ Hela Sverige"** — toggle, söker överallt
- **"✓ Distans / Remote"** — toggle

### Sökfält
- Sök bland alla 290 kommuner i realtid

### Län-picker (om inte "Hela Sverige" valt)
- Varje län expanderbart
- **"Markera alla"** per län
- Checkbox per kommun
- Visar antal valda: "{n} kommuner valda"

**"Spara platser"**-knapp → `POST /api/user/locations`

---

## ✍️ Personligt brev (stilpreferenser)

Styr hur AI:n skriver dina personliga brev.

### Träningsbrev
- Ladda upp (PDF/DOCX) eller klistra in text från tidigare brev du skrivit
- AI analyserar din stil: ton, struktur, favoritfraser
- Lista med uppladdade brev + ta bort-knapp

### Gillade fraser (blå chips)
- Chips med fraser du VILL att AI:n använder
- Input + "Lägg till" / X för att ta bort
- `PATCH /api/user/letter-style/phrases`

### Undvik-fraser (röda chips)
- Chips med fraser AI:n ALDRIG ska använda (t.ex. "brinner för", "gedigen erfarenhet")
- Samma add/remove-logik

### Ämnen att aldrig nämna
- Nyckelord som AI:n ska undvika helt (t.ex. "konst", "Shopify")

### Anekdoter & hobbys
- Lista med sparade anekdoter/hobbys
- Varje post: titel, typ (anekdot/hobby), nyckelord, ta bort-knapp
- **"+ Lägg till anekdot"** — formulär: titel, typ, innehåll, nyckelord → `POST /api/user/anecdotes`
- AI väljer relevanta anekdoter per jobb baserat på nyckelordsmatchning

### AI Feedback
- **Fritext-ruta** — skriv feedback, t.ex. "Gör breven kortare och mer personliga"
- **"Skicka feedback"**-knapp → `POST /api/user/ai-feedback/smart`
- AI analyserar feedbacken och extraherar: undvik-fraser, gillade fraser, stiländringar
- Feedback sparas i databasen och appliceras automatiskt vid varje brevgenerering
- **Historik** — lista med tidigare feedback + ta bort-knapp

### Egna AI-instruktioner
- Stor textarea för fria instruktioner till AI:n
- **"Spara instruktioner"**-knapp → `PATCH /api/user/letter-style`

---

## 📝 Brevformat

Kontrollera layouten på genererade brev.

### Förhandsgranskning
- Live-preview av brevformat med:
  - Hälsningsfras
  - "[Brevets innehåll — ca X ord]"
  - Avslutningsfras
  - Namn + telefon + e-post

### Formulärfält
- **Hälsning** — t.ex. "Hej!" (kontaktpersons namn läggs till automatiskt)
- **Avslutningsfras** — t.ex. "Med vänliga hälsningar,"
- **Namn i signatur**
- **Telefon**
- **E-post**
- **Maximal ordlängd** — nummer (default 200)

**"Spara"**-knapp → `PATCH /api/user/letter-style`

---

## 📬 Gmail

Koppla ditt Gmail-konto för att skapa utkast direkt från appen.

### Ej kopplad
- Beskrivning av vad Gmail-koppling gör
- **3 samtyckes-checkboxar** (alla obligatoriska):
  1. Appen skapar utkast (skickar aldrig automatiskt)
  2. Appen skickar aldrig automatiskt
  3. Jag kan koppla bort när som helst
- **"Anslut Gmail"**-knapp → `GET /api/gmail/auth-url` → Google OAuth-popup

### Kopplad (grön banner)
- ✓ "Gmail kopplad" + din Gmail-adress
- **Vad appen KAN göra:**
  - ✓ Skapa utkast med personligt brev + CV-bilagor
  - ✓ Bifoga PDF-filer
- **Vad appen INTE kan göra:**
  - ✗ Skicka e-post
  - ✗ Läsa befintliga mejl
  - ✗ Radera något
- **"Koppla bort Gmail"**-knapp → `POST /api/gmail/disconnect`

---

## ✨ Quiz (onboarding)

Steg-för-steg-guide för nya användare. Återvändande användare ser en sammanfattningsvy med inline-redigering.

### Frågor (15+ steg)

**Personuppgifter:**
1. Vad heter du? (namn)
2. Telefonnummer
3. Var bor du?
4. Ålder (16-19 / 20-25 / 26-35 / 36-50 / 50+)
5. Körkort? (Manuell / Automat / Nej)
6. Egen bil? (Ja / Nej)
7. Egen dator? (Stationär / Laptop / Både / Nej)
8. Tidigaste startdatum? (Omgående / 2 veckor / 1 månad / 2-3 månader / Senare)
9. Utbildningsnivå? (Grundskola / Gymnasiet / Yrkesskola / Högskola / Universitet)
10. LinkedIn-profil? (valfritt)
11. Portfolio/webbsida? (valfritt)

**Jobbpreferenser:**
12. Vad söker du? (multi-select chips)
13. Fritextsökning (kommaseparerade sökord)
14. Arbetstid (Heltid / Deltid / Extra)
15. Anställningsform (Tillsvidare / Tidsbegränsad / Behovs / Sommar)
16. Längd (Tillsvidare / 6+ mån / 3-6 mån / Kortare)
17. Lön (Månadslön / Provision)
18. Dealbreakers (multi-select)

### Dataflöde
- Sparas lokalt i `localStorage` som `job_preferences`
- Vid slutförande: `POST /api/user/profile-from-quiz` + `POST /api/user/preferences`
- Triggar automatisk scrape av jobb efter slutförd quiz

---

## 👤 Profil

Personuppgifter och kontoinställningar.

### Personuppgifter
- **Namn** — textfält → `PATCH /api/profile`
- **Telefon** — textfält → `PATCH /api/profile`
- **E-post** — skrivskyddat (från auth)
- **Ort** — textfält → `PATCH /api/profile`

### Födelsedatum
- **Datumväljare** (YYYY-MM-DD)
- Beräknad ålder visas automatiskt
- **"Spara födelsedatum"**-knapp → `PATCH /api/profile/birth-date`

### Profilbild
- Uppladdningsknapp → `POST /api/upload/profile-photo`
- Visar nuvarande bild om den finns
- Accepterar: JPG, PNG

### E-postsignatur
- Stor textarea
- **"Spara signatur"**-knapp → `PATCH /api/profile/signature`

### Platsbaser (per region)
- Regionala adresser — om jobbet är i Stockholm, använd Stockholmsadress i brevet
- Varje bas: Län, Ort, highlights
- Redigera per region
- **"Spara baser"**-knapp

### GDPR
- **Exportera all data** — ladda ner all din data som JSON
- **Radera konto** — permanent radering av konto + all data

---

## Teknisk arkitektur

| Komponent | Teknik |
|-----------|--------|
| Frontend | React + Tailwind CSS (single-page, CDN) |
| Backend | FastAPI (Python, Vercel serverless, 60s timeout) |
| Databas | Supabase PostgreSQL + Storage |
| AI Brev | Claude Sonnet (fallback: Haiku → mall) |
| AI CV-chatt | Claude Haiku (läser + skriver Master CV i DB) |
| Grammatik | LanguageTool API |
| Jobbkälla | Platsbanken API (Arbetsförmedlingen) |
| E-post | Gmail API (användarens egna OAuth) |
| Deploy | Vercel Pro |

---

*Allt UI-text på svenska. Designat för neurodivergenta jobbsökare — minimera beslut, ge struktur, ett gränssnitt.*
