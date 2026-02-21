# Vercel Dashboard Navigation Guide

> DO NOT GUESS — use this reference. Vercel dashboard changes often.
> These are the CONFIRMED paths as of Feb 2026.

---

## Top-level dashboard navigation

When you log into Vercel you land on the **Team Overview** page. The top-level navigation bar has:

```
┌──────────────────────────────────────────────────────────────────┐
│  ▲ [Team name]   Overview · Activity · Integrations · Settings  │
│                                                      [Search]   │
└──────────────────────────────────────────────────────────────────┘
```

- **Overview** — list of all projects. Click a project name to enter that project.
- **Activity** — team-wide deployment log
- **Integrations** — team-level integrations (different from project-level)
- **Settings** — TEAM settings (members, billing, etc.) — NOT project settings

---

## Project-level navigation

After clicking a project (e.g. "platsbanken"), you're inside the **Project dashboard**. The project nav bar has:

```
┌──────────────────────────────────────────────────────────────────┐
│  ← [Project name]   Deployments · Analytics · Speed Insights    │
│                      Logs · Storage · Settings                   │
└──────────────────────────────────────────────────────────────────┘
```

- **Deployments** — list of all deploys (Production, Preview). Click any deploy to see build logs, URL, etc. The ⋮ menu on each deploy has "Promote to Production", "Redeploy", etc.
- **Analytics** — traffic/request analytics (Pro feature)
- **Speed Insights** — Web Vitals performance data
- **Logs** — real-time serverless function logs (Runtime Logs). Critical for debugging API errors.
- **Storage** — Vercel-managed databases (KV, Postgres, Blob, Edge Config). We use Supabase instead.
- **Settings** — PROJECT settings (this is where Build, Domains, Env Vars, etc. live)

---

## Project Settings sidebar (EXACT menu as of Feb 2026)

Inside Project → Settings, the LEFT sidebar has:

```
Settings
├── General
├── Build and Deployment  ← Root Directory, Framework, Node.js version, Ignored Build Step
├── Domains
├── Environments          ← Production Branch lives here (NOT under Git)
├── Environment Variables ← API keys (ANTHROPIC_API_KEY, SUPABASE_URL, etc.)
├── Git                   ← Deploy Hooks, PR/commit comments
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

## ⚠️ Common navigation traps

| What you want | WRONG place | RIGHT place |
|---|---|---|
| Production branch | Settings → Git | Settings → **Environments** → Production → Branch Tracking |
| Root directory | Settings → General | Settings → **Build and Deployment** → Root Directory |
| Team settings | Project → Settings | Top nav → team **Settings** (different page!) |
| Function logs | Settings → Functions | Project nav → **Logs** (top bar, not settings) |
| Deploy list | Settings → anything | Project nav → **Deployments** (top bar) |

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

## Build and Deployment page (Settings → Build and Deployment)

Contains these sections in order:
1. **Framework Settings** — auto-detected framework, build command, output dir, install command. Shows warning if Production Overrides differ from Project Settings.
2. **Root Directory** — set to `v2/`. Has checkboxes for "Include files outside root" and "Skip if no changes"
3. **Ignored Build Step** — controls when to skip builds. Options: Automatic / Only build production / Only build pre-production / Only build if there are changes / Only build if there are changes in a folder / Don't build anything / Run my Bash script / Run my Node script / Custom
4. **Node.js Version** — 24.x, 22.x, or 20.x
5. **On-Demand Concurrent Builds** — Run all builds immediately / Run up to one build per branch / Disable
6. **Build Machine** — Standard (4 vCPU, 8 GB) / Enhanced (8 vCPU, 16 GB) / Turbo (30 vCPU, 60 GB, Default)
7. **Deployment Checks** — checks needed before promoting to production
8. **Rolling Releases** — gradual traffic rollout
9. **Prioritize Production Builds** — enabled by default

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
| Deploy history | Project top nav → **Deployments** (NOT in Settings) |

---

## If deployment isn't updating

1. Check Settings → Environments → Production → Branch Tracking = `main`
2. Check that the merge to `main` actually completed on GitHub
3. Check **Deployments** tab (top nav) — latest `main` deploy should say "Production" not "Preview"
4. If still wrong: click the deploy → ⋮ → "Promote to Production"
5. Check **Logs** (top nav) for serverless function errors if the deploy succeeded but the app is broken
