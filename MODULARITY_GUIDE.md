# MODULARITY GUIDE FOR CLAUDE CODE

## THE CORE CONCEPT

**DON'T** generate a new CV for every job.

**DO:** Generate 8-12 BASE CVs once → Customize on-the-fly for each job → Never save the customizations.

---

## BASE CVs vs APPLICATION CVs

### BASE CVs (8-12 total, SAVED in database)

* Restaurant & Café
* Butik & Kassa
* Tech & Kontor
* Vård & Omsorg
* Content Moderation
* Kundtjänst
* Industri & Trädgård
* Konst & Kultur
* [Future: Software Developer, Luxury Hospitality, etc.]

**These are TEMPLATES stored in `user_cvs` table with `is_ai_generated = false`**

### APPLICATION CVs (Infinite, NEVER SAVED)

* Exists only in Gmail drafts
* Customized from base CV based on job description
* Cost: **$0** (just text manipulation)

---

## THE WORKFLOW

When user applies to job:

```
1. AI analyzes job description
   - Type: "restaurant"
   - Special keywords: ["art", "luxury", "english"]

2. Load BASE CV
   - SELECT * FROM user_cvs WHERE vibe_id = 'restaurant'

3. Get ALL modular pieces from database
   - user_experiences (16 rows)
   - user_education (2 rows)
   - user_certifications (5 rows)
   - user_awards (7 rows)
   - user_volunteer (4 rows)

4. AI selects which pieces to include
   IF job mentions "art":
     - Include: art awards
     - Include: international experience
   ELSE:
     - Pure service CV

5. Generate custom CV IN MEMORY
   custom_cv_text = build_from_pieces(selected_pieces)

6. Create Gmail draft
   - Attach: custom_cv_text (as PDF)
   - ❌ DON'T save custom_cv_text to database

7. Cost: $0 (no API call, just text assembly)
```

---

## WHEN TO CREATE NEW BASE CV

### Scenario 1: New job category

```
User: "I found a software developer job"
AI: "You don't have a Software Developer CV. Create one?"
User: "Yes"
AI: [Conversational creation] → Save as CV #9

Cost: $0.10 (one-time)
```

### Scenario 2: User explicitly requests

```
User: "Create CV for police academy"
AI: [Generates] → Save as CV #10

Cost: $0.10 (one-time)
```

### Scenario 3: AI detects pattern

```
AI notices: 20 luxury hotel applications
AI: "Create dedicated Luxury Hospitality CV?"
User: "Yes"
AI: [Generates] → Save as CV #11

Cost: $0.10 (one-time)
```

---

## DATABASE STRUCTURE

### Modular pieces (LEGO blocks):

- `user_experiences` - Work history
- `user_education` - Schools
- `user_certifications` - B-körkort, ICA, etc.
- `user_awards` - Prizes
- `user_volunteer` - Volunteer work

### Base CVs (Templates):

- `user_cvs`
  - `is_ai_generated`: false (for base 8)
  - `times_used`: counter
  - `cv_text`: full CV text

### Version history:

- `user_cv_versions`
  - `version_number`: 1, 2, 3
  - `change_description`: "Made longer", "Removed äldreboende"

---

## COST COMPARISON

### Bad approach (generate per job):
* 500 applications × $0.10 = **$50/month**

### Good approach (modular):
* 8 base CVs × $0.10 = **$0.80 one-time**
* 500 customizations × $0 = **$0**
* **Total: $0.80**

**Savings: 98%**

---

## CONVERSATIONAL CV CREATION

```
AI: "Create Software CV?"
User: "Yes"

AI: [Generates v1] "Includes Minerva, Google, Startup Weekend. Thoughts?"
User: "Make it longer"

AI: [Generates v2 with MORE pieces] "Added Keeping Tabs, art website. Better?"
User: "Remove Kvarngården äldreboende"

AI: [Generates v3 WITHOUT that piece] "Removed! Ready?"
User: "Perfect"

AI: Saves v3 as CV #9, stores versions 1-3
```

---

## CRITICAL RULES

1. **Base CVs = 8-12 reusable templates**
2. **Application CVs = temporary customizations**
3. **NEVER save per-job CVs to database**
4. **Cost optimization = core feature**
5. **User can have max ~12 base CVs before it gets messy**

---

## IMPLEMENTATION CHECKLIST

* [ ] Query modular pieces from database
* [ ] Assemble CV from pieces (not from blob)
* [ ] Customize based on job keywords
* [ ] Create Gmail draft with custom CV
* [ ] ❌ **DON'T INSERT INTO user_cvs**
* [ ] Only save if user creates NEW base CV
* [ ] Track `times_used` counter
* [ ] Store version history for base CVs

---

## WHY THIS MATTERS

### Traditional Approach Problems:
- Database bloat (500 nearly-identical CVs)
- Expensive ($50/month in API costs)
- Slow (regenerate every time)
- Hard to maintain (which version is current?)

### Modular Approach Benefits:
- ✅ Clean database (only 8-12 base CVs)
- ✅ Cheap ($0.80 one-time cost)
- ✅ Fast (instant customization)
- ✅ Easy updates (update base CV → all future applications benefit)

---

## EXAMPLE: Applying to 3 Jobs

**Job 1:** Barista at regular café
- Load: Restaurant Base CV
- Customize: Remove art mentions, emphasize speed
- Result: Standard service CV

**Job 2:** Server at art gallery café
- Load: Restaurant Base CV
- Customize: Include art awards, exhibitions
- Result: Art-aware service CV

**Job 3:** Coffee shop in luxury hotel
- Load: Restaurant Base CV
- Customize: Emphasize international experience, languages
- Result: Luxury hospitality CV

**Database saves:** 0 (all customizations in memory)
**API calls:** 0 (text manipulation only)
**Cost:** $0

---

## UPDATING BASE CVs

When user gets new experience:

```
User: "I got certified in First Aid, January 2026"

AI: "I'll add this to your certifications. Which base CVs should include it?"
1. Healthcare (definitely)
2. Restaurant (food safety relevant)
3. Retail (customer safety relevant)

User: "All three"

AI: Updates 3 base CVs → regenerates each one
Cost: $0.30 (3 CVs × $0.10)

Future benefit: All future healthcare/restaurant/retail applications automatically include it
```

---

**Remember:** The goal is to make applying to 100 jobs/day affordable and sustainable. Modular CVs are the key.
