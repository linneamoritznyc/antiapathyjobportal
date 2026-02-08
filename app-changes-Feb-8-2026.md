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

---

## Security, Scalability, and Compliance Guide

### Authentication options (implement in priority order)

**1. Google OAuth (easiest, already proven in Bidragsguiden)**
Works well, most users have Google accounts.

**2. Email + password (Supabase Auth supports this out of the box)**
Enable in Supabase > Authentication > Providers > Email. Use email confirmation (double opt-in) so users verify their address before accessing the portal. This is important since we'll be creating Gmail drafts from their account.

**3. Magic link (passwordless email)**
User enters email, gets a login link. No password to remember, no password to leak. Supabase supports this natively. Good UX and more secure than passwords.

**4. SMS/WhatsApp login**
Supabase supports SMS via Twilio. Set up a Twilio account, enable Phone provider in Supabase Auth. User enters phone number, gets a 6-digit code via SMS. WhatsApp is possible through Twilio's WhatsApp API but requires Meta business verification -- start with SMS, add WhatsApp later.

**5. BankID (Swedish electronic ID)**
This is the gold standard for Swedish apps handling sensitive data. BankID is NOT built into Supabase, so you need a third-party BankID provider (like Freja eID, Criipto, or BankID's own API). The flow:

- User clicks "Logga in med BankID"
- Opens BankID app on their phone
- Authenticates with fingerprint/PIN
- Your backend verifies the signature with BankID's API
- Creates a Supabase session via supabase.auth.admin.createUser() or custom JWT

BankID costs money (monthly fee + per-authentication fee) and requires a signed agreement with Finansiell ID-Teknik. Worth it for trust, but implement it as a later phase. Start with Google + Email, add BankID when you have paying users.

### GitHub security

The repo MUST be private. Never public. Specifically:

- Set the repo to Private on GitHub (Settings > General > Danger Zone > Change visibility)
- Add a `.gitignore` that excludes: `.env`, `.env.local`, `.env.production`, `node_modules/`, `.next/`, any credential files
- NEVER commit API keys, secrets, or credentials to git. Not even once -- git history is permanent. If you accidentally commit a secret, rotate the key immediately (don't just delete the file, the old key is still in git history)
- Use Vercel Environment Variables for all secrets (ANTHROPIC_API_KEY, SUPABASE_SERVICE_ROLE_KEY, etc.)
- Enable GitHub branch protection on main: require PR reviews, no force pushes
- Enable Dependabot for security updates (GitHub > Settings > Code security and analysis)

### Supabase security hardening

**Row Level Security (RLS) -- non-negotiable:**

```sql
-- Every table MUST have RLS enabled
ALTER TABLE aap_profiles ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "users_own_data" ON aap_profiles
  FOR ALL USING (auth.uid() = id);

-- For file storage (resumes), same principle
CREATE POLICY "users_own_files" ON storage.objects
  FOR ALL USING (auth.uid()::text = (storage.foldername(name))[1]);
```

**Service role key:**

- The `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS. NEVER expose it to the client/browser.
- Only use it in server-side API routes (`pages/api/*.js`), never in `lib/` files imported by React components.
- In Vercel, set it as a server-only environment variable (don't prefix with `NEXT_PUBLIC_`).

**Database triggers:**

- Use `SECURITY DEFINER` on trigger functions so they run with elevated permissions
- Always include `ON CONFLICT DO NOTHING` or `DO UPDATE` to handle race conditions
- Test triggers by creating a test user through the Supabase auth UI

**API rate limiting:**

- Track usage per user per day in an `aap_usage` table (same pattern as Bidragsguiden)
- Check limits server-side in the API route BEFORE calling Claude
- Add IP-based rate limiting as backup for anonymous users
- Consider adding Vercel's Edge Middleware for DDoS protection at the edge

**Supabase Storage for resumes:**

```sql
-- Create a private bucket (not public!)
INSERT INTO storage.buckets (id, name, public) VALUES ('resumes', 'resumes', false);

-- Users can only upload to their own folder
CREATE POLICY "users_upload_own" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'resumes' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can only read their own files
CREATE POLICY "users_read_own" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'resumes' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can delete their own files
CREATE POLICY "users_delete_own" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'resumes' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );
```

File path pattern: `resumes/{user_id}/cv.pdf` -- each user gets their own folder, RLS ensures isolation.

### GDPR and Swedish data law compliance

You are storing personal data (names, emails, resumes, job preferences). Swedish law requires:

**Privacy policy page (`/integritetspolicy`)** that clearly states:

- What data you collect and why
- How long you store it
- That you use AI (Claude API) to process their data -- mention that resume content is sent to Anthropic's API for analysis
- That data is stored in Supabase (mention the hosting region -- EU if possible)
- User's rights: access, correction, deletion, data portability
- Contact information for the data controller (you)

**Consent at signup:**

- Checkbox (not pre-checked) for "Jag har läst och godkänner integritetspolicyn"
- Store `gdpr_consent: true` and `gdpr_consent_at: timestamp` in the profile
- Separate optional checkbox for marketing emails

**Data export (GDPR Article 15 + 20):**

- User can download ALL their data as JSON (profile, searches, saved jobs, applications, resume)
- Button in account settings: "Exportera min data"

**Account deletion (GDPR Article 17 -- right to erasure):**

- User can delete their entire account
- This MUST cascade: profile, saved jobs, applications, search history, resume files from storage, usage records
- Create a Supabase RPC function:

```sql
CREATE OR REPLACE FUNCTION delete_user_data(target_user_id UUID)
RETURNS void AS $$
BEGIN
  DELETE FROM aap_gmail_drafts WHERE user_id = target_user_id;
  DELETE FROM aap_applications WHERE user_id = target_user_id;
  DELETE FROM aap_saved_jobs WHERE user_id = target_user_id;
  DELETE FROM aap_searches WHERE user_id = target_user_id;
  DELETE FROM aap_usage WHERE user_id = target_user_id;
  DELETE FROM aap_profiles WHERE id = target_user_id;
  -- Also delete storage files via Supabase Storage API in the API route
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Data minimization:**

- Only collect what you actually need
- Don't store the full AI conversation history forever -- set an auto-cleanup (e.g., delete searches older than 12 months)
- When sending resume content to Claude API, don't include unnecessary metadata

**Supabase region:**

- If possible, use a Supabase project in the EU region (Frankfurt or Stockholm). This keeps personal data within the EU, which simplifies GDPR compliance.
- When creating a new Supabase project, select "EU West" or "EU North" as the region.

**Anthropic API data handling:**

- Anthropic's API does NOT train on your data by default (API usage is not used for training)
- But mention in your privacy policy that data is processed by a third-party AI provider (Anthropic)
- Consider whether you need a Data Processing Agreement (DPA) with Anthropic -- for production apps handling PII, you should have one

### Scaling for many users

**Database:**

- Add indexes on frequently queried columns (user_id, created_at, status)
- Use LIMIT on all queries (never fetch unbounded data)
- Add the cleanup function for old anonymous sessions and usage data (run weekly via Supabase cron or pg_cron)

**API costs:**

- Claude API calls are the main cost. The freemium model limits this.
- Cache common job recommendations (if 10 users in the same city search for "IT-jobb", you don't need 10 separate API calls)
- Use claude-sonnet-4-20250514 (fast, cheap) instead of Opus for most calls
- Set `max_tokens` in the API call to limit response size

**Vercel:**

- Free tier handles thousands of users fine
- API routes have a 10-second timeout on free tier (60s on Pro) -- keep AI responses within limits
- If you need longer AI processing, consider Vercel Pro ($20/month)

**Gmail API quotas:**

- Gmail API has a daily quota (250 draft creates/day for free, more with Google Workspace)
- Track draft creation in `aap_gmail_drafts` to monitor usage
- Show users a clear message when quota is reached

### Account settings page (`/konto`)

Build an account settings page where users can:

- Update their name and email
- Upload/replace their resume
- Export all data (JSON download)
- Delete account (with confirmation: "All din data raderas permanent, inklusive sparade jobb, CV:n och personliga brev. Detta kan inte ångras.")
- View and revoke Gmail access
- Toggle email notifications
