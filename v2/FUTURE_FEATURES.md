# Future Features — Anti-Apathy Job Portal

## 1. "Extern webbplats" tab (Separat flik från "Jobb")

**Problem:** Många jobb har inget e-postadress för ansökan — man måste ansöka via deras webbplats/formulär. Appen kan inte skicka Gmail-utkast för dessa, men kan fortfarande hjälpa med personligt brev, CV-val, och formulärsvar.

**Koncept:** En egen flik ("Extern webbplats") där användaren klistrar in en länk till en jobbannons, och appen:

### Steg 1: Klistra in länk
- Användaren klistrar in URL till jobbannons (LinkedIn, företagets hemsida, etc.)
- Appen scraper/hämtar jobbannonsen och visar titel, företag, beskrivning

### Steg 2: AI genererar brev
- Samma AI-motor som "Jobb"-fliken
- Genererar personligt brev baserat på Master CV + stil-preferenser + anekdoter
- Matchar rätt bransch-CV automatiskt

### Steg 3: Spara ner filer
- Ladda ner personligt brev i snyggt PDF-format
- Ladda ner rätt bransch-CV (automatiskt matchat)
- Kopiera brev till urklipp

### Steg 4: Formulärhjälp (stretch goal)
- Användaren kan klistra in frågor från ansökningsformuläret
- AI svarar på varje fråga baserat på användarens profil/CV
- T.ex. "Varför vill du jobba hos oss?" → AI genererar svar
- T.ex. "Beskriv en situation där du löste ett problem" → AI väljer relevant anekdot

### Tekniska detaljer
- Ny flik i frontend navigation: "🌐 Extern" (efter "Jobb")
- Backend endpoint: `POST /api/external-job/analyze` — tar URL, scraper sidan, returnerar jobbdata
- Backend endpoint: `POST /api/external-job/generate-letter` — genererar brev
- Backend endpoint: `POST /api/external-job/answer-questions` — AI svarar på formulärfrågor
- Sparar ansökan i samma `applications`-tabell med `source: 'external'`

---

## 2. Förbättrad geografi-filtrering
- Platsbanken API:et har `region`-filter med NUTS-koder — implementera direkt API-filtrering istället för enbart post-filtering
- Lägg till pendlingsavstånd: "Visa jobb inom X km från min hemort"
- Spara senaste sökområdet

## 3. Batch-apply
- Markera flera jobb och generera brev för alla på en gång
- Visa kö med progress: "3/10 brev klara"
- Granska alla innan de sparas som Gmail-utkast

## 4. Statistik-dashboard förbättringar
- Svarsfrekvens per bransch
- Genomsnittlig tid till intervju
- Vilka sökord ger flest svar

## 5. AI-feedback loop
- Användaren markerar vilka ansökningar som ledde till intervju
- AI lär sig vilka brev-stilar som funkar bäst per bransch
- Automatisk A/B-testning av brev-varianter
