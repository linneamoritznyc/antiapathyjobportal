# Anti Apathy Portal - Major Development Brief

## Architecture Reference: Bidragsguiden

I have an existing project called Bidragsguiden (Swedish business grant navigator) that I want you to use as the architectural reference for rebuilding this project. Here's how it's built:

### Stack
- Next.js 14 (Pages Router) deployed on Vercel
- Supabase for database (PostgreSQL), authentication (Google OAuth), and row-level security
- Anthropic Claude API for AI generation (called server-side from Next.js API routes)
- No local dev -- everything runs on Vercel + Supabase cloud

### How the app works (UX flow)

**Public quiz (no login required):** Users land on the homepage and answer a step-by-step quiz (one question per screen, animated transitions). Based on their answers, an AI analyzes and returns personalized results. Users can use this without creating an account.

**AI follow-up questions:** After results are shown, the AI generates 3 smart follow-up questions that the user can click to refine results. There's also a small text input for custom questions. Each refinement sends the previous results + feedback + the question back to the AI.

**Freemium usage limits:** Anonymous users get 3 searches/day, logged-in users get 5/day. Tracked server-side in a bg_usage table using session ID, user ID, or IP address. The API route checks limits before calling Claude.

**Google OAuth login:** Users can optionally log in with Google to save their data. Uses Supabase Auth with the implicit OAuth flow. A database trigger (handle_new_user) auto-creates a profile row when a new user signs up. There's a dedicated /auth/callback page that handles the OAuth redirect.

**Logged-in dashboard (light professional design):** After login, users see a clean white/light dashboard with:
- Stats overview (counts by status)
- Company profile (from quiz answers)
- Search history with PDF/TXT download per search
- Saved items with status workflow (New → Investigating → Applying → Applied → Granted/Rejected/Archived)
- Per-item checklists, notes, deadlines
- Bulk download: PDF, TXT, CSV export

**GDPR compliance:**
- All user data tables have Row Level Security (RLS) -- users can only read/write their own data
- Profile table linked to auth.users via foreign key
- delete_user_data RPC function that cascades deletion
- Privacy policy page
- User can export all their data (JSON)
- User can delete their account

### Database structure (all tables prefixed with bg_)
- `bg_profiles` -- user profiles (id references auth.users, display_name, email, quiz_answers JSONB)
- `bg_sessions` -- anonymous session tracking
- `bg_searches` / `bg_user_searches` -- search history
- `bg_saved_grants` -- saved items with status workflow, notes, deadlines
- `bg_checklist_items` -- per-item checklists
- `bg_usage` -- daily API usage tracking (freemium)
- `bg_feedback` -- user feedback on results
- `bg_email_signups` -- optional email collection

### Key files
- `pages/index.js` -- public quiz + results page
- `pages/dashboard.js` -- logged-in dashboard
- `pages/login.js` -- login page
- `pages/auth/callback.js` -- OAuth callback handler
- `pages/api/analyze.js` -- server-side API route calling Claude
- `lib/supabase.js` -- Supabase client (implicit flow, detectSessionInUrl)
- `lib/auth.js` -- AuthProvider React context (onAuthStateChange, auto-create profile on login)
- `lib/dashboard.js` -- CRUD functions for saved items, checklists, quiz profile
- `lib/export.js` -- PDF/TXT generation

### Design
- Quiz/public pages: dark theme with gradient background, animated transitions
- Dashboard/logged-in pages: light white theme, clean cards with subtle shadows, sticky top nav bar
- Font: DM Sans + Space Mono
- No emojis anywhere
- Swedish UI throughout with proper åäö characters

---

## What I want you to build: Anti Apathy Portal

Rebuild this project using the exact same architecture as Bidragsguiden above, but for job searching instead of grants. Here's what it does:

### Core concept
An AI-powered job application assistant. Users answer questions about their preferences, upload their resume, and the AI helps them find jobs and generate application materials.

### User account (required features)

When creating an account (Google OAuth via Supabase), users must also provide:
- Full name (first name + last name, stored separately so we can format "Vänligen, Firstname Lastname")
- Email address (the Gmail they want to send applications FROM)
- Uploaded resume/CV (stored securely in their portal, only accessible to them via Supabase RLS)

Use Supabase Storage for resume file uploads (PDF). Each user gets their own folder. RLS policies ensure users can only access their own files.

### Quiz flow (like Bidragsguiden)

Step-by-step quiz asking about:
1. What kind of role are you looking for?
2. What industry/field?
3. Experience level?
4. Location preferences (remote/hybrid/on-site, city)?
5. Salary expectations?
6. What are your key skills?
7. What kind of company culture do you prefer?
8. Any dealbreakers?

Based on answers + their uploaded resume, the AI recommends matching jobs.

### AI features (server-side API route calling Claude)

- **Job recommendations:** Based on quiz answers + resume, suggest relevant jobs
- **"Generera personligt brev":** AI writes a personalized cover letter for a specific job, referencing the user's actual resume and the job description
- **"Generera CV" / "Automatiskt välj CV":** AI generates a tailored CV that emphasizes the skills/experience most relevant to that specific job
- **Follow-up questions:** Like Bidragsguiden, the AI suggests smart follow-up questions to refine job recommendations

### Gmail draft integration

When the user clicks "Spara till utkast" on a generated application:
- It creates a draft email in the user's Gmail (using Gmail API)
- The email is pre-filled with:
  - **To:** The job's contact email address
  - **Subject:** Auto-generated relevant subject line
  - **Body:** "Hej, jag hittade denna tjänst på [source site] och vill gärna söka. Se bifogat CV och personligt brev. Vänligen, [Firstname Lastname]"
  - **Attachments:** The generated CV (PDF) and cover letter (PDF)
- The draft just appears in their Gmail drafts -- they review and send themselves

For Gmail API access, you'll need to add Gmail OAuth scopes (gmail.compose) to the Google OAuth setup. The user already signs in with Google, so you extend the OAuth consent to include Gmail draft creation.

### Dashboard (logged-in portal, light professional design like Bidragsguiden)

- **My profile:** Name, email, uploaded resume (with ability to replace)
- **Job recommendations:** Saved/bookmarked jobs with status workflow (New → Interested → Applied → Interview → Offer/Rejected)
- **Application history:** Generated cover letters and CVs, with download buttons (PDF/TXT)
- **Drafts sent to Gmail:** Log of which drafts were created
- **Search history:** Previous job searches with ability to re-run

### GDPR compliance (same as Bidragsguiden)

- RLS on all tables
- User can export all data
- User can delete account + all data
- Resume files deleted from Supabase Storage on account deletion
- Privacy policy page

### Database tables (prefix with aap_)

- `aap_profiles` -- user profiles (id, first_name, last_name, email, resume_url, preferences JSONB)
- `aap_sessions` -- anonymous session tracking
- `aap_searches` -- search history
- `aap_saved_jobs` -- saved jobs with status workflow
- `aap_applications` -- generated cover letters + CVs per job
- `aap_gmail_drafts` -- log of drafts sent to Gmail
- `aap_usage` -- daily API usage tracking

### User preferences

- NO EMOJIS anywhere
- Swedish UI throughout (åäö characters)
- Freemium model: free users get limited searches/day, logged-in users get more
- Light professional dashboard design (white background, subtle shadows, clean cards)
- Dark themed public quiz page with animated transitions

---

## Implementation Order

Start by setting up the project structure, Supabase tables (as SQL migration files the user runs manually), and the authentication flow. Then build the quiz, then the AI integration, then the dashboard, then the Gmail draft feature.
