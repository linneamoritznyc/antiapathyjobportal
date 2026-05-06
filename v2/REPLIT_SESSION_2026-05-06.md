# Replit-session — onsdag 6 maj 2026

Sammanfattning av arbetet i Replit kring kl. 13:48–13:51. Skriven i efterhand baserat på Replit-chatten — Linneas krediter tog slut innan ändringarna hann pushas till GitHub.

## Vad Replit försökte fixa

### 1. HuggingFace GPT-SW3 körs aldrig på CV-generering
**Problem**: GPT-SW3 grammatikkollen (`AI-Sweden-Models/gpt-sw3-6.7b-v2-instruct`) var inkopplad på personliga brev men inte på bransch-CV. Claude kunde alltså hitta på böjningar som "Anlaide" → "Anlade" utan att någon svenskmodell granskade resultatet.

**Replit-plan**:
- Generalisera `check_swedish_with_gpt_sw3()` så den tar konfigurerbar `max_new_tokens` (1500 räcker för brev men trunkerar CV).
- Anropa funktionen direkt efter både Claude- och Gemini-svaret i `generate_bransch_cv()`.
- Falla tillbaka tyst om HuggingFace-nyckeln saknas/är expirerad eller modellen är i cold-start.

### 2. Tech-CV lät inte som ett tech-CV
**Problem**: När Linnea genererade tech-CV nedgraderade modellen tekniska erfarenheter och fyllde CV:et med restaurang-/butiksjobb. Tre buggar samverkade:

| Bugg | Effekt | Replit-plan |
|------|--------|----------|
| Okategoriserade jobb (restaurang, butik) räknades som "tech-relevanta" | Allt blandades ihop | Endast jobb som *uttryckligen* är taggade med branschen räknas som primära |
| Alla erfarenheter skickades till Claude med identisk formatering | Claude kunde inte avgöra vad som var viktigt | Taggade jobb → fulla bullets; andra jobb → en-radare under "Övrig erfarenhet" |
| Prompten sade "Inkludera MINST 10 jobb" | Tvingade in irrelevanta jobb i topplistan | Tas bort — primära jobb först, "Övrig erfarenhet" sist i kortform |

**Grammatikregler från start, inte i efterhand**: `SWEDISH_LANGUAGE_RULES` skulle flyttas från slutet av user-meddelandet till Claudes **system prompt** så att de behandlas som hård instruktion, inte påminnelse.

## Vad som faktiskt finns på `claude/fix-google-login-lGYst` just nu

| Ändring | Status i GitHub-branchen |
|---------|--------------------------|
| `check_swedish_with_gpt_sw3()` finns som funktion | ✅ Finns (rad 1445) |
| GPT-SW3 körs på personliga brev | ✅ Finns (rad 2034, 2069) |
| GPT-SW3 körs på bransch-CV | ❌ **Inte pushat** — `generate_bransch_cv` returnerar Claude-texten direkt (rad 2339) |
| `SWEDISH_LANGUAGE_RULES` i system prompt för CV | ❌ **Inte pushat** — fortfarande i user prompt (rad 2310) |
| Primära vs. övriga jobb i CV-prompten | ❌ **Inte pushat** — "Inkludera MINST 10 jobb" finns kvar (rad 2308) |

Senaste commit (`c5eece0`, 11:35) lade bara till skärmdumpar/text-assets — kodändringarna från 13:48-sessionen hann aldrig committas innan kreditbristen.

## Nästa steg
Ändringarna behöver göras om i denna repo. Plan:
1. Lägg till `check_swedish_with_gpt_sw3()`-anrop efter både Claude- och Gemini-grenarna i `generate_bransch_cv()`.
2. Höj `max_new_tokens`-gränsen i grammatikkollen så CV inte trunkeras.
3. Bygg om CV-prompten: dela upp `experiences` i `primary_jobs` (taggade med branschen) och `other_jobs`; rendera primära med fulla bullets och övriga som en-radare i "Övrig erfarenhet".
4. Flytta `SWEDISH_LANGUAGE_RULES` till `system`-fältet i Anthropic-anropet och `systemInstruction` i Gemini-anropet.
5. Ta bort raden "Inkludera MINST 10 jobb" ur prompten.
