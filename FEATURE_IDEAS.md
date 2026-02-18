# Feature Ideas

## Kvalifikationsvarning innan ansökan skapas

**Datum:** 2026-02-18
**Bakgrund:** AI:n genererade ett korrekt brev för en forskningstjänst i mjukröntgen-spektroelektrokemi (kräver doktorsexamen i kemi). Brevet identifierade korrekt att Linnea inte är kvalificerad — men brevet skapades ändå, vilket kostade credits i onödan.

**Viktig distinktion:**
Det är RÄTT att jobbet visades i flödet — titeln ("Almia söker sjuksköterska till säkerhetsklassad verksamhet") ger ingen ledtråd om innehållet. Linnea vill själv kunna bedöma jobbet. Felet är att ansökan skapades automatiskt utan varning.

**Önskat beteende när användaren klickar "Sök jobbet":**

1. Claude analyserar jobbeskrivningen och jämför mot användarens profil/CV
2. Om tydlig diskvalificering hittas (t.ex. kräver doktorsexamen, specifik licens, X år erfarenhet som saknas):
   - Visa en varningsruta **innan** brevet genereras (= innan credits används)
   - Exempel:
     > ⚠️ **OBS — Det här jobbet verkar kräva kvalifikationer du inte har:**
     > "Tjänsten innebär utveckling av avancerad instrumentering för röntgenspektroskopi... kräver doktorsexamen i kemi"
     >
     > **Vill du ändå söka jobbet?** [Ja, skapa brev] [Nej, skippa]
     >
     > **Vill du att jag uppdaterar dina negativa preferenser?** [Ja, lägg till] [Nej tack]

3. Om användaren väljer "Ja, lägg till negativa preferenser":
   - Extrahera nyckelord från diskvalificerande text (t.ex. "doktorsexamen", "spektroelektrokemi", "PhD kemi")
   - Lägg till i användarens negativa keywords i profilen
   - Framtida jobb med dessa keywords filtreras bort eller flaggas

**Teknisk implementation (när det är dags):**
- Steg 1: Enkel pre-check med Claude (billigt, kort prompt) — returnerar `{qualified: bool, reason: string, negative_keywords: []}`
- Steg 2: Om `qualified: false` → visa modal med varning
- Steg 3: Användaren bekräftar → generera brevet som vanligt
- Spara negativa keywords i `user_profiles.negative_keywords` (array/text-kolumn i Supabase)

**Prioritet:** Låg — kärn-flödet måste fungera stabilt först. Men idén är värdefull både för UX och för att spara credits.
