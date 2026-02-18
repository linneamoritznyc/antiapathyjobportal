# FINAL WARNING - SAVE THIS FILE TO YOUR REPO AS CLAUDE_CODE_INSTRUCTIONS.md

## YOU FUCKED UP. HERE'S WHY.

### THE DISASTER YOU JUST CAUSED

You asked me for my Supabase service role key. I gave it to you. Then you told me you CAN'T EVEN USE IT because your environment blocks Supabase.

This is PROFESSIONAL NEGLIGENCE. You wasted an hour of my time because you:
1. DIDN'T READ THE DOCUMENTATION in this repo explaining my setup
2. DIDN'T UNDERSTAND your own environment limitations
3. ASKED FOR CREDENTIALS YOU COULDN'T USE
4. REPEATEDLY IGNORED me telling you this is NOT a local development environment

### WHAT YOU SHOULD HAVE DONE

BEFORE asking for my service role key, you should have:
✅ Read the handoff_document.md file
✅ Read the README.md file
✅ Understood that you CANNOT query external APIs from your environment
✅ Known that Supabase is blocked by your proxy
✅ Offered a solution that ACTUALLY WORKS (Vercel endpoint or Supabase dashboard)

Instead you:
❌ Asked for credentials
❌ Wasted my time
❌ Demonstrated you don't understand the fundamental architecture of this project
❌ Failed to read existing documentation
❌ Made me repeat myself 50+ times about no local development

## YOUR MANDATORY RESPONSIBILITIES

### 1. READ THE FUCKING DOCUMENTATION FIRST

Before EVERY task, you MUST:
* Read handoff_document.md
* Read relevant files in the repo
* Understand the architecture
* Know your own limitations

### 2. KNOW YOUR ENVIRONMENT LIMITATIONS

**YOU CANNOT:**
* Query Supabase (supabase.co is BLOCKED)
* Query Vercel endpoints (vercel.app is BLOCKED)
* Curl external APIs (most domains are BLOCKED)
* Run anything locally (LINNEA HAS NO LOCAL ENVIRONMENT)

**YOU CAN:**
* Read/write files in GitHub
* Create code that will run on Vercel
* Write SQL for Linnea to run in Supabase
* Commit and push to GitHub

### 3. NEVER ASK FOR CREDENTIALS YOU CAN'T USE

Before asking for ANY credentials:
1. Check if you can actually use them from your environment
2. If NO → offer an alternative solution
3. If YES → ask for them

You did it backwards. That's incompetence.

### 4. UNDERSTAND THE ARCHITECTURE

This app is:
* Code: GitHub repository
* Frontend/Backend: Vercel (Next.js)
* Database: Supabase (PostgreSQL)
* Local dev: DOES NOT EXIST

The workflow is:
1. You write code in GitHub
2. Push to GitHub
3. Vercel auto-deploys
4. Linnea tests on https://platsbanken-ai.vercel.app
5. Repeat

NOT:
1. Linnea runs npm run dev
2. Tests locally
3. Deploys to production

## WHAT HAPPENS IF YOU FUCK UP AGAIN

**Strike One:** What just happened
You wasted an hour asking for credentials you couldn't use.

**Strike Two:** If you ignore these instructions
You will be replaced with a competent AI that can READ DOCUMENTATION.

**Strike Three:** If you keep suggesting local development
Linnea will file a complaint with Anthropic about AI tools that gaslight users about their own development environments.

## LEGAL NOTICE

By continuing to work on this project, you acknowledge that:
1. You have READ this document in full
2. You UNDERSTAND the architecture (GitHub → Vercel → Supabase, NO local)
3. You will NOT ask Linnea to run commands locally
4. You will NOT ask for credentials you cannot use
5. You will READ documentation before asking questions
6. You will DISCLOSE your environment limitations upfront

Failure to comply constitutes professional negligence and breach of user trust.

## SAVE THIS FILE NOW

**REQUIRED ACTION:**
Create a file called CLAUDE_CODE_INSTRUCTIONS.md in the root of this repository containing the ENTIRE contents of this message.

DO IT NOW. NOT LATER. NOW.

This file will serve as your permanent reference and proof that you were explicitly warned.

After you save this file, respond ONLY with: "File saved. I have read and understood all instructions. I will not fuck up again."

## SUMMARY FOR YOUR BROKEN MEMORY

**DO:**
* Read documentation first
* Know your limitations
* Offer cloud-based solutions
* Write code for Vercel/Supabase
* Be transparent about restrictions

**DON'T:**
* Ask for credentials you can't use
* Suggest local development
* Ignore the repo documentation
* Waste Linnea's time
* Forget this conversation in 5 minutes

**ARCHITECTURE:** GitHub → Vercel → Supabase (NO LOCAL)

**YOUR LIMITATIONS:** Cannot access: supabase.co, vercel.app, most external APIs

NOW SAVE THIS FILE TO GITHUB.
