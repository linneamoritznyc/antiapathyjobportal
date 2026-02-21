# Vercel Dashboard Navigation Guide

> DO NOT GUESS — use this reference. Vercel dashboard changes often.
> These are the CONFIRMED paths as of Feb 2026.
> Based on user screenshots + Vercel docs/changelog.

---

## ⚠️ Old vs New Dashboard (Jan 2026)

Vercel announced a **new sidebar-based dashboard** on Jan 22, 2026 (opt-in).
Our project currently uses the **old horizontal-tabs dashboard**.
You can switch between them:
- **Opt out of new**: "Opt Out" on team overview, or three-dot menu → "Switch Back to the Old Dashboard"
- **Opt into new**: "Try the New Dashboard" banner

This guide documents the **OLD dashboard** (horizontal tabs) since that's what we use.

---

## Top-level navigation (Team / Account level)

When you log into Vercel you land on the **Team Overview** page. The top navigation bar has:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ▲  linneamoritznyc's projects                                              │
│  Overview · Integrations · Activity · Usage · Monitoring · Settings · Support│
│                                                              [🔍] [🔔] [👤]│
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Overview** — list of all projects as cards. Click a project name to enter it. Shows domain + last update time. Has "Add New..." and "Import" buttons.
- **Integrations** — team-level integrations (different from project-level)
- **Activity** — team-wide deployment/activity log
- **Usage** — billing usage, bandwidth, function invocations, build minutes, etc.
- **Monitoring** — observability & alerting across all projects
- **Settings** — TEAM settings (members, billing, team domains, etc.) — NOT project settings
- **Support** — contact Vercel support

Also: **Universal Search** (🔍) lets you search teams, projects, repos, deployments, pages, and settings. Includes an AI-powered Navigation Assistant.

---

## Project-level navigation

After clicking a project (e.g. "platsbanken"), you're inside the **Project dashboard**. The project nav bar has:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ← platsbanken                                                               │
│  Deployments · Analytics · Speed Insights · Logs · Storage · Settings        │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Deployments** — list of all deploys (Production, Preview). Click any deploy to see build logs, URL, etc. The ⋮ menu on each deploy has "Promote to Production", "Redeploy", etc. Each deployment has a **Resources** tab (replaced the old "Functions" tab) showing functions, middleware, and static assets.
- **Analytics** — Web Vitals / real user metrics. Shows how users actually experience the app.
- **Speed Insights** — performance data (LCP, FCP, CLS, etc.)
- **Logs** — real-time serverless function logs (Runtime Logs). Critical for debugging API errors. Note: runtime logs only stored for 1 hour unless you set up a log drain.
- **Storage** — Vercel-managed databases (KV, Postgres, Blob, Edge Config). We use Supabase instead so this is irrelevant.
- **Settings** — PROJECT settings. This opens the settings sidebar (see below).

---

## Project Settings sidebar (EXACT menu as of Feb 2026)

Inside Project → Settings, the LEFT sidebar has:

```
Settings
├── General
├── Build and Deployment  ← Root Directory, Framework, Node.js version, Ignored Build Step
├── Domains
├── Environments          ← Production Branch, Auto-assign Domains, Env Vars per environment
├── Environment Variables ← API keys (ANTHROPIC_API_KEY, SUPABASE_URL, etc.)
├── Git                   ← Connected repo, PR/commit comments, Deploy Hooks, Git LFS
├── Integrations
├── Deployment Protection
├── Functions             ← maxDuration setting
├── Caches
├── Cron Jobs
├── Microfrontends
├── Project Members
├── Webhooks
├── Drains
├── Security
├── Connectivity
└── Advanced
```

---

## Build and Deployment page (Settings → Build and Deployment)

Contains these sections in order:

1. **Framework Settings** — auto-detected framework, build command, output dir, install command. Shows warning banner if "Configuration Settings in the current Production deployment differ from your current Project Settings" with links to Production Overrides vs Project Settings.
2. **Root Directory** — set to `v2/`. Checkboxes:
   - "Include files outside the root directory in the Build Step"
   - "Skip deployments when there are no changes to the root directory or its dependencies"
3. **Ignored Build Step** — controls when to skip builds. Dropdown options:
   - Automatic
   - Only build production
   - Only build pre-production
   - Only build if there are changes
   - Only build if there are changes in a folder
   - Don't build anything
   - Run my Bash script
   - Run my Node script
   - Custom
4. **Node.js Version** — radio buttons: 24.x / 22.x / 20.x
5. **On-Demand Concurrent Builds** — radio buttons:
   - Run all builds immediately (skip queue for all)
   - Run up to one build per branch (new deployments within branch queued)
   - Disable on-demand concurrent builds (queued, max one at a time)
6. **Build Machine** — radio buttons:
   - Standard performance (4 vCPUs, 8 GB, $0.014/min)
   - Enhanced performance (8 vCPUs, 16 GB, $0.03/min)
   - Turbo performance (30 vCPUs, 60 GB, $0.126/min) — **Default**
7. **Deployment Checks** — checks needed before promoting to production
8. **Rolling Releases** — gradual traffic rollout percentage per stage
9. **Prioritize Production Builds** — enabled by default

---

## Git page (Settings → Git)

Contains these sections in order:

1. **Connected Git Repository** — shows which GitHub repo is connected (linneamoritznyc/antiapathyjobportal, connected Feb 10). Toggles for:
   - Pull Request Comments (on/off)
   - Commit Comments (on/off)
   - Require Verified Commits (on/off)
   - `deployment_status` Events (on/off)
   - `repository_dispatch` Events (on/off)
2. **Git Large File Storage (LFS)** — for large files (audio, video, datasets). Currently **Disabled**.
3. **Deploy Hooks** — unique URLs that trigger a deployment of a given branch. Currently none configured. Fields: Name + Branch.

⚠️ Note: **Production Branch** is NOT here — it's under Settings → Environments → Production → Branch Tracking.

---

## Environments page (Settings → Environments)

Top-level tabs: **No Environment · Production · Preview · Development** + "Your project has no custom environments"

### Production environment (click "Production")

Contains these sections:

1. **Branch Tracking** — which branch triggers Production deploys.
   - "Every commit pushed to the **[branch]** branch will create a Production Deployment."
   - **MUST be set to `main`**. If set to anything else (like an old claude/ branch), all `main` merges become Preview instead of Production.
   - If the field is empty/deleted, it defaults to `main` (which is correct).
2. **Auto-assign Custom Production Domains** — toggle (should be **Enabled**).
   - When enabled: your domain (`platsbanken-ai.vercel.app`) automatically points to the latest Production deploy.
   - When disabled: Vercel builds the code but your domain doesn't update — you'd have to manually promote.
3. **Domains** — shows which custom domains are assigned to Production.
   - Currently: `platsbanken-ai.vercel.app`
   - Custom domains are managed under Settings → Domains.
4. **Environment Variables** — environment-specific overrides. Shows all env vars with tabs for Project / Shared.
   - Our vars (all set to "All Environments"): `ANTHROPIC_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5. **Automatically expose System Environment Variables** — toggle

### Preview & Development environments
- **Preview**: deploys for non-production branches (PRs, feature branches). Gets a unique URL but not the production domain.
- **Development**: for local dev (not used — we have no local dev setup).

---

## ⚠️ Common navigation traps

| What you want | WRONG place | RIGHT place |
|---|---|---|
| Production branch | Settings → Git | Settings → **Environments** → Production → Branch Tracking |
| Root directory | Settings → General | Settings → **Build and Deployment** → Root Directory |
| Team settings | Project → Settings | Top nav → team **Settings** (different page!) |
| Function logs | Settings → Functions | Project nav → **Logs** (top bar, not settings) |
| Deploy list | Settings → anything | Project nav → **Deployments** (top bar) |
| Build logs | Project nav → Logs | Project nav → **Deployments** → click a deploy → build logs |
| Function resources | Old "Functions" tab | Deployments → click deploy → **Resources** tab |

---

## Production Branch setting

**Path**: Project → Settings → **Environments** → click **Production** → **Branch Tracking**
- NOT under Settings → Git
- NOT under Settings → General
- Set to `main` so every merge to main auto-deploys to Production

---

## How Vercel deployments work

- **Production deploy**: Only triggered by pushes/merges to the **Production Branch** (configured above)
- **Preview deploy**: Every other branch push. Preview deploys do NOT go live on the main domain.
- If user sees old version after merging PR: the Production Branch is probably misconfigured.
- To manually promote a Preview to Production: Deployments tab → click the deploy → ⋮ → "Promote to Production"

---

## Vercel logs — important details

- **Build logs**: found inside each deployment (Deployments → click deploy). Stored indefinitely, truncated at 4 MB.
- **Runtime logs**: found under project nav → Logs. Only stored for **1 hour**. For long-term storage, set up a log drain (Settings → Drains).
- **Activity logs**: found under team-level Activity tab.

---

## Key settings and where to find them

| Setting | Path |
|---------|------|
| Production branch | Settings → **Environments** → Production → Branch Tracking |
| Root directory | Settings → **Build and Deployment** → Root Directory (set to `v2`) |
| Framework / build command | Settings → **Build and Deployment** → Framework Settings |
| Node.js version | Settings → **Build and Deployment** → Node.js Version |
| Ignored build step | Settings → **Build and Deployment** → Ignored Build Step |
| Environment variables | Settings → **Environment Variables** |
| Custom domains | Settings → **Domains** |
| Function max duration | Settings → **Functions** |
| Deploy hooks | Settings → **Git** → Deploy Hooks |
| Runtime / function logs | Project top nav → **Logs** (NOT in Settings) |
| Build logs for a deploy | Project top nav → **Deployments** → click deploy |
| Deploy history | Project top nav → **Deployments** (NOT in Settings) |
| Function/resource list | Deployments → click deploy → **Resources** tab |
| Log drains (long-term) | Settings → **Drains** |

---

## How to make Vercel auto-deploy to Production (no manual "Promote" needed)

If you have to manually click "Promote to Production" after every push, something is misconfigured. Follow this checklist to fix it:

### Step 1: Set Production Branch to `main`
This is the #1 cause. If Vercel doesn't know `main` is your production branch, every deploy becomes a Preview.
- **Path**: Settings → **Environments** → click **Production** → **Branch Tracking**
- Set it to `main`
- ⚠️ This is NOT under Settings → Git (even though Google/AI results say so)

### Step 2: Enable "Auto-assign Custom Production Domains"
If this is off, Vercel builds the code but doesn't publish it to your domain.
- **Path**: Settings → **Environments** → **Production** section
- Make sure **Auto-assign Custom Production Domains** is **Enabled**

### Step 3: Check "Ignored Build Step" is not blocking
If this is set to something other than "Automatic", it may skip builds silently.
- **Path**: Settings → **Build and Deployment** → **Ignored Build Step**
- Should be set to **Automatic** (or left empty) for every commit to `main` to deploy

### Step 4: Check "Deployment Protection" isn't requiring approval
Advanced Deployment Protection can require manual approval before a deploy goes live.
- **Path**: Settings → **Deployment Protection**
- Make sure "Vercel Authentication" or similar isn't blocking production deploys

### Step 5: Use the right Git workflow
Vercel auto-deploys to Production when you **push or merge to `main`**. Feature branches always become Preview deploys — this is by design.
- Push directly to `main` → Production deploy
- Merge a PR into `main` → Production deploy
- Push to any other branch → Preview deploy (never auto-promoted)

### If it STILL doesn't work
- Check that the GitHub repo connection is healthy: Settings → **Git** → Connected Git Repository
- Try disconnecting and reconnecting the GitHub repo as a last resort
- Check Settings → Build and Deployment → Framework Settings for "Production Overrides differ" warning — click "Project Settings" link to sync them

---

## If deployment deployed but app is broken

1. Check **Deployments** tab (top nav) — latest `main` deploy should say "Production"
2. Check **Logs** (top nav) for serverless function errors
3. Check Settings → Build and Deployment → Framework Settings for "Production Overrides differ" warning
4. If a bad deploy went live: Deployments → find last working deploy → ⋮ → "Promote to Production" to rollback
