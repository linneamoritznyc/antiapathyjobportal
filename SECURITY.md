# Säkerhetstips för Vibe Coding

30 säkerhetstips för att hålla din AI-byggda app säker.

> Källa: [itsthatlady.dev/blog/vibe-coding-security-tips](https://www.itsthatlady.dev/blog/vibe-coding-security-tips/)

## Del 1: Grunderna

### 1. Håll hemligheter utanför chatten
Klistra aldrig in API-nycklar, lösenord eller databas-URL:er i ChatGPT eller Claude. Använd platshållare som `YOUR_API_KEY` eller be AI:n skriva kod som hämtar hemligheter från miljövariabler.

### 2. Akta dig för "spök-paket"
AI hittar ibland på bibliotek som inte finns. Hackare skapar malware-paket med dessa påhittade namn. Verifiera alltid att paket finns innan du installerar - kolla nedladdningssiffror på npm/PyPI.

### 3. Rulla inte din egen auth
Använd etablerade lösningar som Clerk, Supabase Auth, NextAuth eller Firebase istället för AI-genererad inloggning. Auth är där 90% av dataintrång börjar.

### 4. Låt AI granska sin egen kod
Efter att koden fungerar, be AI:n granska den: "Agera som en Senior Security Engineer. Granska denna kod för sårbarheter som SQL injection eller XSS och skriv om den säkert."

### 5. Sanera all input
AI älskar att ta användarinput och stoppa det direkt i databasen. Be explicit: "Se till att alla databasfrågor använder parameteriserade queries för att förhindra SQL injection."

### 6. Fixa din .gitignore
Be AI:n generera en omfattande .gitignore för din projekttyp innan första commit. Inkludera alla miljöfiler och systemloggar. Botar scannar GitHub efter exponerade nycklar 24/7.

### 7. Använd aktuella paket
AI:ns träningsdata har ett cutoff-datum och kan föreslå gamla versioner med kända säkerhetshål. Kör `npm audit` efter installation.

### 8. Lägg till rate limiting tidigt
Om du bygger ett kontaktformulär eller API-endpoint utan rate limiting kommer botar hitta det. Lägg till rate limiting på alla publika endpoints från dag ett.

### 9. Be AI hacka dig
Klistra in din kod och fråga: "Om du vore en hackare, hur skulle du bryta denna specifika funktion? Berätta om exploiten och fixen."

### 10. Aktivera Row Level Security (RLS)
Som standard låter de flesta databaser vem som helst se allt. Om du använder Supabase, aktivera RLS på alla tabeller från dag ett och sätt upp policies så användare bara kan se sin egen data.

## Del 2: Vanliga misstag

### 11. Lås CORS
AI sätter ofta CORS till `*` (tillåt alla domäner). Konfigurera CORS för att bara tillåta requests från din produktionsdomän.

### 12. Validera redirects
Om din inloggningssida använder `?redirect=/dashboard`, kan angripare ändra till `?redirect=evil.com/phishing`. Validera alla redirect-URL:er mot en allowlist.

### 13. Säkra dina storage buckets
AI gör ofta hela bucketen publik som standard. Sätt storage policies så användare bara kan komma åt filer de laddat upp.

### 14. Städa bort debug-satser
AI älskar att lägga till `console.log(userData)`. Den datan syns i produktions-browsers konsol. Ta bort alla console.log före deploy.

### 15. Verifiera webhooks
Om du accepterar Stripe webhooks kan vem som helst POST:a falsk data till den endpointen. Verifiera alltid webhook-signaturer med leverantörens SDK.

### 16. Kolla permissions server-side
Att gömma en "Radera allt"-knapp i UI:t stoppar ingen från att anropa API:t direkt med curl. Varje skyddad route behöver server-side permission checks.

### 17. Håll dependencies uppdaterade
AI kan scaffolda med paket från flera år sedan. Kör `npm audit fix` efter byggning och kolla periodiskt efter uppdateringar.

### 18. Rate limita lösenordsåterställning
Begränsa till 3 lösenordsåterställnings-requests per e-post per timme.

### 19. Dölj feldetaljer
Returnera generiska felmeddelanden till användare. Logga detaljerade fel bara server-side.

### 20. Sätt sessionsutgång
Sätt JWT expiration till 7 dagar och implementera refresh token rotation.

## Del 3: Produktionsproblem

### 21. Skydda alla dina API:er
Applicera samma auth, rate limits och validering på ALLA endpoints - inte bara webbappen.

### 22. Sätt tak på AI-kostnader
Sätt användningsgränser i ditt OpenAI dashboard OCH rate limita endpointen. Max 50 requests per användare per dag är en bra start.

### 23. Använd riktig e-postinfrastruktur
Använd en verifierad sändningstjänst som Resend eller SendGrid med SPF/DKIM-records konfigurerade.

### 24. Bygg kontoborttagning
Skapa en endpoint som tar bort all användardata från både databas OCH storage. GDPR-brott kan resultera i böter upp till 4% av global omsättning.

### 25. Automatisera backups
Om du är på Supabase, aktivera Point-in-Time Recovery i databasinställningarna.

### 26. Rotera dina hemligheter
Rotera alla API-nycklar var 90:e dag. Använd GitHubs secret scanning för att hitta läckta nycklar.

### 27. Skaffa DDoS-skydd
Använd Cloudflares gratis tier eller Vercels Edge Config för rate limiting på CDN-nivå.

### 28. Begränsa uppladdningsstorlekar
Sätt max filstorlek till 5MB för bilder och validera filtyper server-side.

### 29. Logga kritiska handlingar
Skapa en `audit_log`-tabell. Logga varje användarborttagning, rolländring, betalning och dataexport.

### 30. Separera test och produktion
Använd Stripe testläge-nycklar och en helt separat databas för staging.

---

## Resurser

- 🤖 Agent skill: [ladydev.me/security-skill](https://ladydev.me/security-skill)
- 🔐 VibeSec Skill: [github.com/BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill)
