# Codebase Documentation Audit

**Last updated:** 2026-02-14
**Production URL:** https://platsbanken-ai.vercel.app
**Architecture:** Vercel (Next.js serverless) + Supabase PostgreSQL + Claude API
**Active codebase:** v2/ folder only
**Legacy/deprecated:** v1/ folder (pending deletion after data migration)

---

## EXECUTIVE SUMMARY

The project underwent a major architectural rebuild (documented in `app-changes-Feb-8-2026.md`) from a local Python/SQLite/React-CDN app to a Vercel-deployed Next.js app with Supabase cloud PostgreSQL. The original documentation folder (`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/`) was written in December 2024 for v1 and has NOT been updated to reflect the v2 reality. This means **7 of 15 docs are significantly outdated** and will mislead any AI or developer that reads them without this context.

**Documentation health:**

- Accurate & current: `app-changes-Feb-8-2026.md`, `docs/GDPR-GUIDE-SVENSKA-APPAR.md`, `SECURITY.md`, `docs/DESIGN_HISTORY.md`, `v2/requirements.txt`
- Partially outdated: `PHILOSOPHY.md` (values still apply, tech details wrong), root `requirements.txt`
- Wrong/misleading: `CHANGELOG.md`, `GAP_ANALYSIS.md`, `INDEX.md` (original), `NEXT_STEPS.md`, `PROJECT_OVERVIEW.md`, `README.md`, `TECHNICAL_SPEC.md`, `v1/requirements.txt`

---

## COMPLETE DOC INVENTORY

### 1. SECURITY.md

**Path:** `SECURITY.md`
**Status:** Accurate
**Summary:** 30 security tips for vibe-coded apps, written in Swedish. Covers secrets management, input sanitization, RLS, CORS, rate limiting, DDoS protection, session management, and more. Generic best-practice advice, not project-specific.
**Use when:** Doing security reviews, hardening the app, or setting up new features that handle user data.
**Conflicts:** None -- this is generic advice, not project-specific claims.
**Red flags:** None.

---

### 2. CHANGELOG.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/CHANGELOG.md`
**Status:** Outdated
**Summary:** Changelog for v1.0.0 (Dec 28, 2024). Documents the original MVP: SQLite database, local FastAPI server, React CDN frontend, IMAP Gmail integration, 8 CV personas. Lists planned versions 1.1, 1.5, 2.0 that were never released in this form -- the project was rebuilt instead.
**Use when:** Understanding the original v1 feature set and its history.
**Conflicts:** States "SQLite database" and "local server" as current -- both replaced by Supabase PostgreSQL and Vercel deployment. Plans "SQLite -> PostgreSQL migration" as a future v2.0 change -- this already happened. References `api_server.py` and `frontend.html` which are v1 files.
**Red flags:** Roadmap dates (Jan 2025, Feb 2025, Q1 2025) are all past and irrelevant. The planned architecture changes listed for v2.0 happened via a complete rebuild, not an incremental migration.

---

### 3. GAP_ANALYSIS.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/GAP_ANALYSIS.md`
**Status:** Outdated
**Summary:** Detailed gap analysis of v1 MVP vs desired state. Identifies 9 gaps across 3 priority tiers with effort estimates. Written Dec 28, 2024.
**Use when:** Historical reference only -- understanding what problems v1 had.
**Conflicts:** Entire document describes v1 architecture (SQLite, localhost, IMAP, single-user). Lists "Cloud deployment" as "Not Yet Implemented" with "Low" priority -- the app is now deployed on Vercel. Lists "Multi-user support" as not implemented -- v2 has Supabase Auth. Recommends "fix this week" actions from December 2024.
**Red flags:** Every technical recommendation targets v1 code that no longer exists. The "Critical Gaps" (Gmail button, email extraction, error messages) may or may not apply to v2 -- check v2 code directly.

---

### 4. INDEX.md (original)

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/INDEX.md`
**Status:** Outdated
**Summary:** Navigation index for the documentation folder. Lists 7 docs with reading paths for different roles (new user, developer, product owner, designer). References a folder structure (`docs/`, `roadmap/`) that doesn't match the actual repo layout.
**Use when:** Never -- use `.claude/INDEX.md` or this audit instead.
**Conflicts:** States docs are in `docs/TECHNICAL_SPEC.md`, `docs/PHILOSOPHY.md`, `docs/GAP_ANALYSIS.md`, `roadmap/NEXT_STEPS.md` -- but in the actual repo, all these files are flat inside the `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/` folder, not in subdirectories. References `~/Desktop/anti-apathy-portal-final/` as the code location -- wrong.
**Red flags:** The "Getting Started Checklist" and "Learning Paths" will lead readers through outdated v1 docs.

---

### 5. NEXT_STEPS.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/NEXT_STEPS.md`
**Status:** Outdated
**Summary:** Action plan from Dec 28, 2024. Contains specific bash commands, code snippets, and step-by-step instructions for v1 development. Includes weekly checklist, blocker tracking, and resource planning.
**Use when:** Historical reference only.
**Conflicts:** Every code example references v1 (`api_server.py`, `frontend.html`, `http://localhost:8000`, SQLite). Contains hardcoded paths like `~/Desktop/anti-apathy-portal-final`. Lists "Claude Code Installation Hanging" as a blocker -- no longer relevant. Contains a Gmail App Password in plain text in a code example (security concern, though it may be expired).
**Red flags:** Contains what appears to be a real Gmail App Password (`xcwu agnn brcq unng`) in a code snippet. This should be removed or rotated immediately. Code snippets will break if copy-pasted against v2.

---

### 6. PHILOSOPHY.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/PHILOSOPHY.md`
**Status:** Partially outdated
**Summary:** Design philosophy document covering neurodivergent-first design, human-in-the-loop automation, Swedish cultural context, UX goals, aesthetic choices, and trade-offs. Core values and design mantras.
**Use when:** Understanding the project's mission, design principles, and user experience goals. The values and philosophy are still relevant even though the tech stack changed.
**Conflicts:** States "Local-first architecture, no cloud storage" as a key trade-off and differentiator -- v2 uses Supabase cloud and Vercel. Lists "complete data ownership" and "works offline" as benefits -- no longer true with cloud deployment. "Privacy vs. Convenience" section describes the opposite of current architecture.
**Red flags:** The "Unique Differentiators" section claims "Local-First, Privacy-Respecting" and "No data sent to third parties" -- both wrong for v2 which sends data to Supabase and Anthropic API. The core emotional/UX philosophy is still valid though.

---

### 7. PROJECT_OVERVIEW.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/PROJECT_OVERVIEW.md`
**Status:** Outdated
**Summary:** Executive summary of the v1 MVP. Covers problem statement, features, tech stack, architecture diagram, and quick start guide. Version 1.0.0, Dec 28, 2024.
**Use when:** Understanding the original problem statement and motivation (still valid). Ignore all technical details.
**Conflicts:** Tech stack lists SQLite, BeautifulSoup, Requests, React CDN, IMAP -- all replaced in v2. Architecture diagram shows localhost with SQLite. Quick start guide says `python3 api_server.py` and `http://localhost:8000` -- both wrong for v2. Lists Gemini as a backup AI provider -- v2 is Claude-only.
**Red flags:** "All processing happens locally" is stated as a feature -- false for v2.

---

### 8. README.md (project management folder)

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/README.md`
**Status:** Outdated
**Summary:** Full user-facing README for v1. Includes installation guide, usage instructions, project structure, configuration, API endpoints, troubleshooting, and dependency list.
**Use when:** Never for current development -- this describes v1 entirely. The API endpoint table and troubleshooting may have some overlap with v2 if endpoints were preserved.
**Conflicts:** Entire document is v1-specific. Project structure shows `api_server.py`, `job_portal_backend.py`, `frontend.html`, `data/jobs.db` -- none of these exist in v2. Installation is `python3 api_server.py` on localhost. Dependencies list `beautifulsoup4`, `requests`, `google-generativeai` which aren't in v2.
**Red flags:** States "No cloud dependencies - Runs entirely on localhost" in the Security section. Lists troubleshooting for `localhost:8000` problems.

---

### 9. TECHNICAL_SPEC.md

**Path:** `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/TECHNICAL_SPEC.md`
**Status:** Outdated
**Summary:** Comprehensive technical specification for v1 (1,091 lines). Covers architecture, all component specs, full API docs, database schema, algorithms, design decisions, performance specs, security, error handling, testing strategy, and future deployment plans.
**Use when:** Understanding v1 architecture decisions and their rationale. The design decision rationale (Why FastAPI? Why IMAP over Gmail API?) provides historical context but the choices themselves have changed.
**Conflicts:** Entire architecture is v1 (SQLite, local FastAPI, React CDN, IMAP). Database schema shows SQLite tables -- v2 uses Supabase PostgreSQL with `aap_` prefixed tables. API endpoints reference `localhost:8000`. Code examples throughout reference v1 classes and functions. Future deployment diagram shows nginx/load balancer -- actual deployment is Vercel serverless.
**Red flags:** Contains a hardcoded email address (`linneamoritzcv@gmail.com`) in the IMAP integration code. CORS is set to `allow_origins=["*"]` in the spec -- may or may not carry into v2.

---

### 10. app-changes-Feb-8-2026.md

**Path:** `app-changes-Feb-8-2026.md`
**Status:** Accurate -- THIS IS THE SOURCE OF TRUTH
**Summary:** The master development brief for the v2 rebuild. Uses Bidragsguiden as an architectural reference. Specifies the complete target architecture: Next.js 14 on Vercel, Supabase Auth (Google OAuth), Supabase PostgreSQL with `aap_` prefixed tables, Claude API for AI, Gmail API (not IMAP) for drafts. Includes database schema, GDPR requirements, security hardening guide, scaling plan, and implementation order.
**Use when:** ANY architectural or technical question about v2. This is the blueprint for the current production app.
**Conflicts:** None -- this IS the current truth. Other docs conflict with IT.
**Red flags:** None. This is the most current and authoritative doc in the repo.

---

### 11. DESIGN_HISTORY.md

**Path:** `docs/DESIGN_HISTORY.md`
**Status:** Accurate
**Summary:** Short document (44 lines) tracking the visual design evolution from v1 to v2. Documents the original v1 layout (stat cards, single CTA, simple footer) and the v2 additions (multi-user, tabs, master CV editor, GDPR compliance). References an `original-layout.png` image.
**Use when:** Understanding the UI evolution and design intent.
**Conflicts:** None.
**Red flags:** The referenced image `original-layout.png` may or may not exist in the `docs/` folder.

---

### 12. GDPR-GUIDE-SVENSKA-APPAR.md

**Path:** `docs/GDPR-GUIDE-SVENSKA-APPAR.md`
**Status:** Accurate
**Summary:** Comprehensive GDPR compliance guide for Swedish web apps using Supabase stack. Written Feb 12, 2026. Covers all relevant GDPR articles (5-49), DPA requirements, cookie consent, incident reporting, DPIA, and implementation status checklist. Includes links to IMY, EDPB, and Supabase DPA resources.
**Use when:** Implementing any feature that touches user data, authentication, privacy policy, data export, or account deletion. Check the implementation status checklist for what's done vs what's missing.
**Conflicts:** None.
**Red flags:** The "Implementation Status" section shows many items still pending (data export, privacy policy page, cookie banner, DPA signing, etc.).

---

### 13. requirements.txt (root)

**Path:** `requirements.txt`
**Status:** Partially outdated
**Summary:** Root-level Python dependencies: fastapi, uvicorn, pydantic, httpx, python-multipart. Uses `>=` version constraints.
**Use when:** Setting up the Python environment. May be the active requirements file if the Vercel serverless function uses it.
**Conflicts:** Doesn't include `anthropic` package (which v1/requirements.txt does). May or may not be the one Vercel uses.
**Red flags:** Unclear which requirements.txt is authoritative for v2 deployment.

---

### 14. v1/requirements.txt

**Path:** `v1/requirements.txt`
**Status:** Outdated (v1 legacy)
**Summary:** v1 Python dependencies including python-dotenv, pydantic-settings, and anthropic SDK.
**Use when:** Never -- v1 is deprecated.
**Conflicts:** Targets deprecated v1 codebase.
**Red flags:** v1 is pending deletion.

---

### 15. v2/requirements.txt

**Path:** `v2/requirements.txt`
**Status:** Accurate
**Summary:** v2 Python dependencies with pinned versions: fastapi==0.109.0, httpx==0.26.0, pydantic==2.5.3, uvicorn==0.27.0, python-multipart==0.0.6.
**Use when:** Setting up the v2 Python environment or debugging dependency issues.
**Conflicts:** Does not include `anthropic` SDK -- it may be handled elsewhere (package.json for Next.js API routes, or a separate install).
**Red flags:** Pinned versions may need security updates.

---

## CRITICAL CONFLICTS IDENTIFIED

### Conflict 1: Architecture description (every old doc vs reality)

**Wrong info:** CHANGELOG, GAP_ANALYSIS, INDEX, NEXT_STEPS, PROJECT_OVERVIEW, README, TECHNICAL_SPEC all describe: SQLite database, local FastAPI server on port 8000, React via CDN in a single HTML file, IMAP for Gmail drafts, localhost-only deployment.
**Actual truth:** Next.js 14 on Vercel, Supabase PostgreSQL cloud database, Supabase Auth (Google OAuth), Gmail API (not IMAP) for drafts, deployed at https://platsbanken-ai.vercel.app.
**Source of truth:** `app-changes-Feb-8-2026.md` and actual v2/ code.

### Conflict 2: "Local-first, privacy-respecting" vs cloud deployment

**Wrong info:** PHILOSOPHY.md lists "Local-First, Privacy-Respecting" as a unique differentiator. PROJECT_OVERVIEW says "All processing happens locally." README states "No cloud dependencies."
**Actual truth:** v2 stores all data in Supabase cloud (PostgreSQL). User data including resumes go through Supabase Storage. AI requests go to Anthropic's API. The app is deployed on Vercel's cloud.
**Source of truth:** `app-changes-Feb-8-2026.md` -- explicitly specifies "No local dev -- everything runs on Vercel + Supabase cloud."

### Conflict 3: Database technology

**Wrong info:** TECHNICAL_SPEC shows detailed SQLite schema with `jobs` and `applications` tables. CHANGELOG references SQLite throughout. GAP_ANALYSIS says "SQLite sufficient for single-user."
**Actual truth:** Supabase PostgreSQL with `aap_` prefixed tables: `aap_profiles`, `aap_sessions`, `aap_searches`, `aap_saved_jobs`, `aap_applications`, `aap_gmail_drafts`, `aap_usage`.
**Source of truth:** `app-changes-Feb-8-2026.md` database schema section.

### Conflict 4: Single-user vs multi-user

**Wrong info:** Every old doc describes this as a single-user personal tool. GAP_ANALYSIS lists multi-user as a "nice-to-have" future feature.
**Actual truth:** v2 has Supabase Auth with Google OAuth, per-user data isolation via RLS, and is designed for multiple users with a freemium model.
**Source of truth:** `app-changes-Feb-8-2026.md` user account section.

### Conflict 5: Gmail integration method

**Wrong info:** TECHNICAL_SPEC has detailed IMAP code using `imaplib` with Gmail App Passwords. README lists Gmail App Password as a required environment variable.
**Actual truth:** v2 uses Gmail API with OAuth scopes (gmail.compose), not IMAP. Users authenticate via Google OAuth, and the app extends the consent to include Gmail draft creation.
**Source of truth:** `app-changes-Feb-8-2026.md` Gmail draft integration section.

### Conflict 6: Security concern in NEXT_STEPS.md

**Wrong info:** NEXT_STEPS.md contains what appears to be a real Gmail App Password in a code example: `xcwu agnn brcq unng`.
**Actual truth:** Even if this password has been rotated, credentials should never appear in documentation committed to version control.
**Source of truth:** Security best practice; also stated in SECURITY.md tip #1 and #6.

---

## TASK-BASED NAVIGATION

### When working on: Database/Schema

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- Has the complete v2 Supabase schema with all `aap_` tables and RLS policies
2. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` -- GDPR requirements that affect schema design (data export, deletion, consent tracking)
3. `v2/` source code -- Verify actual schema matches the spec

**Ignore:** `TECHNICAL_SPEC.md` (SQLite schema), `GAP_ANALYSIS.md` (v1 database gaps)

### When working on: Auth/Security

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- Supabase Auth setup, RLS policies, service role key handling, authentication options (Google OAuth, email, magic link, BankID)
2. `SECURITY.md` -- General security checklist (RLS, CORS, rate limiting, secrets management)
3. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` -- Consent requirements, data encryption, access logging

**Ignore:** `TECHNICAL_SPEC.md` security section (describes v1 localhost security model)

### When working on: Frontend

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- Design requirements (dark quiz, light dashboard, DM Sans + Space Mono, no emojis, Swedish UI)
2. `docs/DESIGN_HISTORY.md` -- Visual evolution from v1 to v2
3. `PHILOSOPHY.md` -- UX goals (neurodivergent-first, calm technology, reduce cognitive load) -- skip the tech/architecture sections

**Ignore:** `README.md` and `TECHNICAL_SPEC.md` frontend sections (React CDN, single HTML file -- all v1)

### When working on: API

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- API routes are Next.js API routes (`pages/api/*.js`), not FastAPI endpoints
2. `v2/` source code -- Check actual API route implementations
3. `SECURITY.md` -- Rate limiting, input validation, CORS best practices

**Ignore:** `TECHNICAL_SPEC.md` API documentation (describes FastAPI endpoints at localhost:8000), `README.md` API table

### When working on: Deployment

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- "No local dev -- everything runs on Vercel + Supabase cloud"
2. Vercel dashboard and project settings (not documented in repo)

**Ignore:** All old docs that reference localhost, `python3 api_server.py`, port 8000

### When working on: GDPR Compliance

**Must read first:**
1. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` -- Complete GDPR checklist with implementation status
2. `app-changes-Feb-8-2026.md` -- GDPR section (RLS, delete_user_data RPC, data export, privacy policy page, DPA requirements)

**Ignore:** Nothing -- both docs are current and complementary

### When working on: New Features

**Must read first:**
1. `app-changes-Feb-8-2026.md` -- Architecture and design constraints
2. `PHILOSOPHY.md` -- Design principles (skip architecture claims, focus on UX values)
3. `docs/GDPR-GUIDE-SVENSKA-APPAR.md` -- If the feature handles user data

**Ignore:** `GAP_ANALYSIS.md` and `NEXT_STEPS.md` (both describe v1 gaps and plans)

---

## SOURCE OF TRUTH HIERARCHY

When docs conflict, trust in this order:

1. **Actual v2/ code** (what's deployed)
2. **`app-changes-Feb-8-2026.md`** (latest rebuild decisions and target architecture)
3. **`docs/GDPR-GUIDE-SVENSKA-APPAR.md`** (GDPR requirements, Feb 2026)
4. **`SECURITY.md`** (general security best practices)
5. **`docs/DESIGN_HISTORY.md`** (UI evolution reference)
6. **`PHILOSOPHY.md`** (UX values only -- ignore tech claims)
7. **Other docs** (treat as historical v1 artifacts, verify everything against code)

---

## DEPRECATED -- DO NOT USE

These files/references describe v1 architecture and will actively mislead:

- **`v1/` folder** -- entire directory is legacy, pending deletion
- **`v1/requirements.txt`** -- v1 dependencies
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/TECHNICAL_SPEC.md`** -- v1 architecture, SQLite schema, localhost APIs
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/README.md`** -- v1 installation/usage guide
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/NEXT_STEPS.md`** -- v1 action plan with hardcoded credentials
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/GAP_ANALYSIS.md`** -- v1 gap analysis
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/CHANGELOG.md`** -- v1 changelog with obsolete roadmap
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/INDEX.md`** -- navigation to outdated docs
- **`anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/PROJECT_OVERVIEW.md`** -- v1 project overview
- Any reference to `localhost`, `localhost:8000`, or "local server"
- Any reference to `api_server.py`, `job_portal_backend.py`, `frontend.html`, `fix_my_backend.py`
- Any reference to SQLite, `jobs.db`, or `data/` directory
- Any reference to IMAP, `imaplib`, or Gmail App Passwords (v2 uses Gmail API with OAuth)
- Any reference to `~/Desktop/anti-apathy-portal-final/`

---

## GAPS IDENTIFIED

**Missing documentation:**

- No v2-specific README -- the root of the repo has no README.md at all
- No v2 API route documentation (what endpoints exist in `pages/api/`)
- No Supabase setup guide (how to create tables, enable RLS, configure auth)
- No Vercel deployment guide (environment variables needed, build settings)
- No v2 CHANGELOG tracking changes since the rebuild
- No `.env.example` documenting required environment variables for v2
- No documentation of which GDPR checklist items have actually been implemented in v2 code

**Unclear/incomplete:**

- Which `requirements.txt` does Vercel actually use? (root vs v2)
- Is `app-changes-Feb-8-2026.md` fully implemented or partially aspirational?
- What is the actual current state of Gmail API integration in v2?
- Does v2 still use 8 CV personas or has this changed?
- What AI model and prompt structure does v2 actually use?
- The GDPR guide lists many items as "missing" but doesn't track which have been added since Feb 12, 2026

**Should be created:**

- `README.md` at repo root for v2
- `.env.example` listing all required env vars
- `v2/ARCHITECTURE.md` documenting actual v2 architecture as-built
- Updated CHANGELOG for v2 changes
