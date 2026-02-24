# Features — Anti-Apathy Job Portal

> Uppdaterad: 24 feb 2026

En AI-driven jobbportal för neurodivergenta jobbsökare i Sverige. Automatiserar det mekaniska — du behåller kontrollen.

---

## 1. Master CV med 8 branschanpassade versioner

**Det som gör oss unika:** Du bygger ETT Master CV — sedan genererar AI:n automatiskt 8 olika branschanpassade versioner. Varje version lyfter just de erfarenheter och skills som är relevanta för den branschen.

**Branscher:**
- Restaurang & Cafe
- Butik & Kassa
- Kundtjänst & Support
- Tech & Kontor
- Vård & Omsorg
- Trädgård & Industri
- Content & Moderation
- Konst & Kultur

**Vad Master CV innehåller:**
- Arbetslivserfarenheter med start/slutdatum, beskrivning, bullet points
- Utbildning (gymnasium, högskola, kurser)
- Certifieringar (körkort, kassahantering, första hjälpen, etc.)
- Utmärkelser
- Volontärarbete
- Skills (tekniska, branschspecifika, språk)
- Tech-projekt med GitHub- och live-länkar

**Hur bransch-CVer fungerar:**
AI:n analyserar varje erfarenhet och rankar dess relevans per bransch. I restaurang-CVt lyfts kundkontakt och stresshantering. I tech-CVt lyfts tekniska projekt och struktur. Varje version har rätt ton — restaurang är avslappnat/vänligt, tech är formellt/strukturerat.

**Alla CVer kan laddas ner som PDF.**

---

## 2. AI-chatt som uppdaterar ditt CV direkt i databasen

Du kan prata med AI:n i chattform och den utför ändringarna direkt:

- *"Jag fick ett certifikat i serveringskunskap idag"* → AI lägger till i certifieringar
- *"Jag jobbar inte längre på Ica Maxi, markera det som avslutat"* → AI uppdaterar slutdatum
- *"Ändra min adress till Norsborg"* → AI uppdaterar profilen
- *"Lägg till att jag kan kassaarbete"* → AI lägger till skill

**AI:n har läs- och skrivåtkomst till din Master CV-data i databasen.** Den läser vad du har, föreslår ändringar, och sparar efter ditt godkännande. Ingen formulärklickande — bara skriv vad du vill ändra.

---

## 3. AI-genererade personliga brev per jobb

Klicka "Ansök" på valfritt jobb → AI (Claude) skriver ett personligt brev som är:

- **Jobbanpassat** — refererar specifika krav och detaljer från annonsen
- **CV-matchat** — baserat på rätt bransch-CV (automatiskt vald)
- **Personligt** — väver in dina anekdoter och hobbies när de är relevanta
- **Skrivet i din stil** — använder fraser du gillar, undviker fraser du hatar
- **Grammatik-checkat** — automatisk svensk grammatik-kontroll

Du kan redigera brevet, kopiera det, ladda ner som PDF, eller spara direkt som Gmail-utkast.

---

## 4. Kvalifikationsvarning — sparar API-credits

Innan brevet genereras gör en billig AI-check (Haiku) en snabb analys: är du ens kvalificerad?

Om jobbet kräver doktorsexamen, legitimation, eller 5+ års specifik erfarenhet du saknar → **varning visas INNAN credits används**.

Tre val:
1. **Sök ändå** — generera brevet
2. **Hoppa över** — spara credits
3. **Hoppa över + filtrera bort liknande** — AI föreslår nyckelord att lägga till som negativa sökord

---

## 5. Stil-preferenser — AI:n lär sig hur du skriver

**Träningsbrev:** Ladda upp 1-20 tidigare personliga brev du skrivit → AI analyserar din stil (ton, struktur, öppning, avslutning, favoritfraser).

**Inställningar du kan styra:**
- **Ton:** professionellt vänlig / formell / casual / varm
- **Gillade fraser:** ord du VILL att AI:n använder
- **Undvik-lista:** fraser AI:n ALDRIG ska använda (t.ex. "passionerad", "brinner för")
- **Ämnen att aldrig nämna:** t.ex. "konst", "Shopify"
- **Anekdoter:** personliga berättelser med nyckelord — AI väljer relevanta per jobb
- **Hobbies:** intressen som kan vävas in
- **Fritext-feedback:** "Gör breven kortare", "Nämn mer teamwork" → AI sparar och applicerar

---

## 6. Gmail-integration med ett klick

Koppla ditt Gmail → klicka "Spara i Gmail med bilagor" → utkast skapas automatiskt med:

1. **Ämne:** Ansökan: [Jobbtitel] – [Ditt namn]
2. **Brödtext:** Personligt brev
3. **Bilaga 1:** Personligt brev som PDF
4. **Bilaga 2:** Rätt bransch-CV som PDF

Du granskar utkastet i Gmail och skickar manuellt. Inga olyckor.

---

## 7. Smart jobbsökning med filtrering

**Scraping från Platsbanken**
Appen söker direkt i Arbetsförmedlingens API med dina sökord + valda kommuner.

**E-post vs extern ansökan**
- **Jobb-flik:** Jobb med direkt e-post → kan skicka via Gmail
- **Extern-flik:** Jobb utan e-post → ansöker via företagets hemsida, appen hjälper med brev + CV

**Negativa sökord**
Filtrera bort jobbtyper du inte vill se. Chips i kategorier (Hälsa & Vård, Utbildning, Teknik, Juridik) + fritext.

**Smart feed**
Jobb du redan sökt, avvisat eller sparat visas inte igen. Tinder-stil: en gång hanterat, borta ur kön.

---

## 8. Sparade jobb med fulla actions

Spara jobb du vill söka senare. I Ansökningar → Sparade får du:
- **Skapa ansökan** — öppnar full ansökningsmodal med AI-brev
- **Visa annons** — öppnar originalannonsen
- **Deadline-info** med färgkodning (rött = akut, amber = snart)
- Plats och datum

---

## 9. Ansökningsspårning + aktivitetsrapport

Varje ansökan har status: **Sparad → Utkast → Skickad → Intervju → Erbjudande / Avslag**

- Ändra status med dropdown
- Lägg till anteckningar per ansökan
- Se sökta jobb per dag (stapeldiagram)

**Aktivitetsrapport (PDF):** Ladda ner månatlig rapport som PDF med alla skickade ansökningar — datum, yrkesroll, arbetsgivare, omfattning, ort. Matchar Arbetsförmedlingens format. Redo för A-kassan. Data hämtas från `applications`-tabellen i Supabase (status = 'sent'), samkört med `jobs`-tabellen för jobbdetaljer.

**Backend:** `GET /api/aktivitetsrapport?month=2026-02` → genererar PDF med fpdf2.
**Data:** `applications.sent_at` + `jobs.title/company/location/working_hours` från Supabase.

---

## 10. CV-uppladdning med AI-parsning

Ladda upp ett befintligt CV (PDF, DOCX, TXT) → AI:n:
1. Extraherar text
2. Identifierar erfarenheter, utbildning, skills
3. Fyller i ditt Master CV automatiskt
4. Ger rekommendationer på förbättringar

---

## 11. Profil & onboarding

**Quiz för nya användare:** Namn, telefon, plats, körkort, bil, dator, utbildning, tillgänglighet, sökord, dealbreakers. Sparas lokalt + i databasen.

**Profilsida:** Redigera personuppgifter, födelsedatum (för ålder i brev), e-postsignatur, LinkedIn, portfolio-URL.

**Platsval:** Välj kommuner du vill söka jobb i. Region-baserade adressval — om jobbet är i Stockholm, använd Stockholmsadress i brevet.

---

## 12. Statistik

- Totalt antal jobb i databasen
- Antal ansökningar per status (sparade, utkast, skickade, intervjuer)
- Jobb med deadline idag
- Sökta jobb per dag (senaste 7 dagarna)

---

## 13. Autentisering & GDPR

**Inloggning:** E-post + lösenord ELLER Google OAuth.

**GDPR:**
- Exportera all din data som JSON
- Radera konto + all data permanent

---

## Teknisk arkitektur

| Komponent | Teknik |
|-----------|--------|
| Frontend | React + Tailwind CSS (single-page app) |
| Backend | FastAPI (Python, Vercel serverless, 60s timeout) |
| Databas | Supabase PostgreSQL + Storage |
| AI Brev | Claude Sonnet 4.5 (fallback: Haiku → mall) |
| AI CV-chatt | Claude Haiku (läser + skriver Master CV i DB) |
| Grammatik | GPT-SW3 via HuggingFace |
| Jobbkälla | Platsbanken API (Arbetsförmedlingen) |
| E-post | Gmail API (användarens egna OAuth) |
| Deploy | Vercel Pro |

---

*Allt UI-text på svenska. Designat för neurodivergenta jobbsökare — minimera beslut, ge struktur, ett gränssnitt.*
