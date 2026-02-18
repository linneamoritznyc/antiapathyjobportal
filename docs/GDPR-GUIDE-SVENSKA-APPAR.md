# GDPR-krav för svenska webbappar

> **Sammanställt av:** Claude (Anthropic) den 12 februari 2026
> **Syfte:** Checklista och referensdokument för GDPR-compliance vid utveckling av svenska webbapplikationer med Supabase-stack
> **Licens:** Fritt att använda och anpassa

---

## Innehåll

1. [Rättslig grund för behandling](#1-rättslig-grund-för-behandling)
2. [Registrerades rättigheter](#2-registrerades-rättigheter)
3. [Samtycke vid registrering](#3-samtycke-vid-registrering)
4. [Integritetspolicy](#4-integritetspolicy)
5. [Databehandlingsavtal (DPA)](#5-databehandlingsavtal-dpa)
6. [Register över behandlingar](#6-register-över-behandlingar)
7. [Privacy by Design & Default](#7-privacy-by-design--default)
8. [Datalagring](#8-datalagring)
9. [Säkerhet](#9-säkerhet)
10. [Cookie-samtycke](#10-cookie-samtycke)
11. [Incidentrapportering](#11-incidentrapportering)
12. [Konsekvensbedömning (DPIA)](#12-konsekvensbedömning-dpia)
13. [Implementeringsstatus](#13-implementeringsstatus)
14. [Källor och referenser](#14-källor-och-referenser)

---

## 1. Rättslig grund för behandling

**GDPR Art. 6**

Varje typ av personuppgiftsbehandling kräver en specificerad rättslig grund. Samtycke är bara en av sex möjliga grunder.

| Rättslig grund | Exempel i app-kontext |
|---|---|
| **Avtal** (Art. 6.1b) | Kontodata, betalningsuppgifter — nödvändigt för att fullgöra tjänsten |
| **Samtycke** (Art. 6.1a) | Nyhetsbrev, marknadsföring, icke-nödvändiga cookies |
| **Berättigat intresse** (Art. 6.1f) | Grundläggande analytics, bedrägeribekämpning |
| **Rättslig förpliktelse** (Art. 6.1c) | Bokföringsdata som måste sparas enligt lag |

**Krav:** Dokumentera vilken rättslig grund som gäller för varje datatyp i appen. Blanda inte ihop avtal och samtycke — om data krävs för att leverera tjänsten är det avtal, inte samtycke.

---

## 2. Registrerades rättigheter

**GDPR Art. 15–22**

Användare har följande rättigheter som appen måste stödja:

**Rätt att radera data — Art. 17 ("Right to be forgotten")**
- Användare måste kunna radera sitt konto och ALL sin data
- Ska vara enkelt att hitta (inte gömt bakom flera menyer)
- Ska vara permanent och faktiskt ta bort datan (inte bara markera som raderad)
- Tredjeparter som fått datan ska informeras om raderingen

**Rätt till dataportabilitet — Art. 20**
- Användare ska kunna ladda ner all sin data
- Formatet ska vara maskinläsbart (JSON, CSV)
- Data ska kunna överföras direkt till annan tjänst om tekniskt möjligt

**Rätt till rättelse — Art. 16**
- Användare ska kunna korrigera felaktig persondata
- Implementera redigeringsmöjlighet i profil/inställningar

**Rätt till begränsning av behandling — Art. 18**
- Användare kan begära att behandling pausas (t.ex. vid tvist om datakorrekthet)

**Rätt att göra invändningar — Art. 21**
- Användare kan invända mot behandling baserad på berättigat intresse
- Särskilt relevant vid direktmarknadsföring (absolut rätt att invända)

**Rätt till information — Art. 13–14**
- Informera användare om databehandlingen vid insamlingstillfället

---

## 3. Samtycke vid registrering

**GDPR Art. 7**

- Tydlig information om vad datan används till
- Checkbox för godkännande — får **INTE** vara förkryssad
- Samtycke ska vara fritt, specifikt, informerat och otvetydigt
- Länk till integritetspolicy
- Spara bevis på när och hur samtycke gavs (tidsstämpel, version av policy)
- Lika enkelt att dra tillbaka samtycke som att ge det

---

## 4. Integritetspolicy

**GDPR Art. 13–14**

Integritetspolicyn ska innehålla:

- Vilken data som samlas in och kategorier av personuppgifter
- Rättslig grund för varje behandling
- Syfte med behandlingen
- Hur länge datan sparas (lagringsperiod per datatyp)
- Vem som har tillgång (tredje parter, underbiträden)
- Användarens rättigheter och hur de utövas
- Kontaktinfo till personuppgiftsansvarig
- Rätt att klaga till IMY (Integritetsskyddsmyndigheten)
- Information om eventuella överföringar till tredjeland

---

## 5. Databehandlingsavtal (DPA)

**GDPR Art. 28**

Skriftliga avtal krävs med alla tredjeparter (personuppgiftsbiträden) som behandlar persondata åt dig.

**Vanliga biträden i en Supabase-stack:**

| Tjänst | DPA-status |
|---|---|
| **Supabase** | DPA tillgänglig via [supabase.com/legal/dpa](https://supabase.com/legal/dpa) — signeras via PandaDoc |
| **Vercel** | DPA ingår i Terms of Service |
| **Stripe** | DPA tillgänglig via Stripe Dashboard |
| **Resend/SendGrid** | Kontrollera respektive tjänsts DPA |
| **Analytics-verktyg** | Kontrollera GDPR-compliance (överväg EU-baserade alternativ som Plausible eller Matomo) |

**Krav:** Signera DPA med varje biträde innan lansering. Spara kopiorna.

---

## 6. Register över behandlingar

**GDPR Art. 30**

Intern dokumentation (behöver inte vara synlig för användare men krävs vid granskning av IMY).

Registret ska innehålla:

- Namn och kontaktuppgifter till personuppgiftsansvarig
- Kategorier av registrerade (t.ex. "appanvändare", "kunder")
- Kategorier av personuppgifter (t.ex. "namn", "e-post", "platsdata")
- Syfte med varje behandling
- Rättslig grund
- Kategorier av mottagare (t.ex. "Supabase som biträde")
- Överföringar till tredjeland (om tillämpligt)
- Lagringsperioder
- Beskrivning av tekniska och organisatoriska säkerhetsåtgärder

> **Notera:** Undantag finns för företag med färre än 250 anställda, men bara om behandlingen inte inkluderar känsliga uppgifter, inte sker regelbundet, eller inte innebär risk. I praktiken behöver de flesta appar ett register.

---

## 7. Privacy by Design & Default

**GDPR Art. 25**

- **Dataminimering:** Samla bara in data du faktiskt behöver för appens funktion
- **Privacy by Default:** Standardinställningar ska vara de mest integritetsvänliga
- **Pseudonymisering:** Använd anonymiserad/pseudonymiserad data där möjligt
- Bygg in integritetsskydd från start — inte som eftertanke

---

## 8. Datalagring

**GDPR Art. 44–49**

- Lagra persondata inom EU/EES om möjligt
- Supabase EU-region (t.ex. `eu-west-1`, `eu-central-1`) uppfyller detta krav
- Om data överförs utanför EU: kräver extra skyddsåtgärder (Standard Contractual Clauses, adequacy decisions, eller Binding Corporate Rules)
- Dokumentera var all data lagras och vilka underbiträden som är involverade

---

## 9. Säkerhet

**GDPR Art. 32**

- Kryptering av känslig data (i transit och i vila)
- Säker autentisering (Supabase Auth med RLS uppfyller grundkraven)
- Logga åtkomst till persondata
- Regelbundna säkerhetsgranskningar
- Princip om minsta möjliga behörighet (least privilege)
- Säkerhetskopiering och återställningsplan

---

## 10. Cookie-samtycke

**GDPR + ePrivacy-direktivet**

- Cookie-banner som tydligt förklarar vilka cookies som används och varför
- Möjlighet att **neka** icke-nödvändiga cookies (inte bara "acceptera")
- Spara användarens val
- Inga icke-nödvändiga cookies får sättas innan samtycke ges
- Supabase auth-cookies räknas generellt som "strikt nödvändiga" och kräver inte samtycke, men om du lägger till analytics-cookies eller tredjepartscookies behövs cookie-banner

---

## 11. Incidentrapportering

**GDPR Art. 33–34**

- Personuppgiftsincidenter (dataläckor) måste rapporteras till **Integritetsskyddsmyndigheten (IMY)** inom **72 timmar**
- Om incidenten innebär hög risk för individer ska även de berörda personerna informeras
- Dokumentera alla incidenter (även de som inte rapporteras till IMY)
- Ha en intern plan för incidenthantering redo innan lansering

**Rapporteringsformulär:** [imy.se — Anmäl personuppgiftsincident](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/personuppgiftsincidenter/)

---

## 12. Konsekvensbedömning (DPIA)

**GDPR Art. 35**

En DPIA (Data Protection Impact Assessment) krävs om behandlingen innebär **hög risk** för individer. Exempel på när DPIA behövs:

- Systematisk och omfattande profilering
- Behandling av känsliga uppgifter i stor skala
- Systematisk övervakning av allmänt tillgängliga platser
- **Platsdata i stor skala** (relevant för appar som hanterar GPS-data)

Om din app hanterar platsdata (t.ex. GPS-spårning av fordon eller ruttplanering), genomför en DPIA innan lansering.

---

## 13. Implementeringsstatus

### ✅ Implementerat
- Radera konto (all data raderas permanent)
- EU-lagring (Supabase EU-region)
- Säker auth (Supabase Auth med RLS)

### ⬜ Saknas fortfarande
- [ ] Exportera data-funktion (JSON/CSV-export)
- [ ] Integritetspolicy-sida
- [ ] Cookie-banner (om icke-nödvändiga cookies används)
- [ ] Databehandlingsavtal med tredjeparter (Supabase DPA m.fl.)
- [ ] Register över behandlingar (intern dokumentation)
- [ ] Rätt till rättelse i UI (redigera profil/persondata)
- [ ] Specificera rättslig grund per datatyp
- [ ] DPIA för appar med platsdata
- [ ] Incidenthanteringsplan
- [ ] Bevis på samtycke (tidsstämplar, version av policy)

---

## 14. Källor och referenser

### Svenska myndigheter

- **IMY — Integritetsskyddsmyndigheten (Sveriges dataskyddsmyndighet)**
  - Dataskydd för verksamheter: [imy.se/verksamhet/dataskydd](https://www.imy.se/verksamhet/dataskydd/)
  - GDPR i fulltext (svenska): [imy.se — Dataskyddsförordningen i fulltext](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/introduktion-till-gdpr/dataskyddsforordningen-i-fulltext/)
  - Dataskydd för företag: [imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/foretag](https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/foretag/)
  - De registrerades rättigheter: [imy.se — Rättigheter](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/de-registrerades-rattigheter/)
  - Anmäl personuppgiftsincident: [imy.se — Incidentrapportering](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/personuppgiftsincidenter/)

### EU-resurser

- **EDPB — European Data Protection Board**
  - GDPR-guide för små och medelstora företag: [edpb.europa.eu/sme-data-protection-guide](https://www.edpb.europa.eu/sme-data-protection-guide/home_en)
  - Praktiska resurser för SME:er: [edpb.europa.eu — Practical resources](https://www.edpb.europa.eu/sme-data-protection-guide/practical-resources-for-smes_en)
  - Roller: Personuppgiftsansvarig vs biträde: [edpb.europa.eu — Data controller vs processor](https://www.edpb.europa.eu/sme-data-protection-guide/data-controller-data-processor_en)
- **GDPR.eu** — Praktisk guide till GDPR: [gdpr.eu](https://gdpr.eu/)
  - Cookies och GDPR: [gdpr.eu/cookies](https://gdpr.eu/cookies/)
  - Vad är ett databehandlingsavtal: [gdpr.eu/what-is-data-processing-agreement](https://gdpr.eu/what-is-data-processing-agreement/)

### Teknikspecifika resurser

- **Supabase**
  - DPA (Data Processing Addendum): [supabase.com/legal/dpa](https://supabase.com/legal/dpa)
  - Privacy Policy: [supabase.com/privacy](https://supabase.com/privacy)
  - GDPR-diskussion (community): [github.com/supabase/discussions/2341](https://github.com/orgs/supabase/discussions/2341)

### GDPR-artiklar refererade i detta dokument

| Artikel | Ämne |
|---|---|
| Art. 5 | Grundläggande principer för behandling |
| Art. 6 | Rättslig grund för behandling |
| Art. 7 | Villkor för samtycke |
| Art. 13–14 | Informationsskyldighet |
| Art. 15 | Rätt till tillgång |
| Art. 16 | Rätt till rättelse |
| Art. 17 | Rätt till radering |
| Art. 18 | Rätt till begränsning |
| Art. 20 | Rätt till dataportabilitet |
| Art. 21 | Rätt att göra invändningar |
| Art. 25 | Privacy by Design & Default |
| Art. 28 | Personuppgiftsbiträden (DPA) |
| Art. 30 | Register över behandlingar |
| Art. 32 | Säkerhet vid behandling |
| Art. 33–34 | Incidentrapportering |
| Art. 35 | Konsekvensbedömning (DPIA) |
| Art. 44–49 | Överföring till tredjeland |

---

> **Disclaimer:** Detta dokument är en teknisk checklista, inte juridisk rådgivning. Kontakta en jurist specialiserad på dataskydd för formell compliance-granskning. Dokumentet är sammanställt av Claude (Anthropic) baserat på offentligt tillgänglig information från IMY, EDPB och GDPR-förordningen.
