# Documentation Index

Map of task types to the actual documentation files in this repo.
See `.claude/CODEBASE_AUDIT.md` for detailed analysis of each file's accuracy.

**WARNING:** 7 of 15 docs describe the deprecated v1 architecture (SQLite, localhost, IMAP).
The source of truth for v2 is `app-changes-Feb-8-2026.md`.

---

## Task: Understanding the project

| File | Status | What it contains |
|------|--------|-----------------|
| `app-changes-Feb-8-2026.md` | Current | **SOURCE OF TRUTH** -- v2 rebuild blueprint, full architecture spec |
| `PHILOSOPHY.md` (in project mgmt folder) | Partial | UX values still valid; tech/architecture claims are wrong for v2 |
| `docs/DESIGN_HISTORY.md` | Current | Visual design evolution from v1 to v2 |

## Task: Architecture & technical decisions

| File | Status | What it contains |
|------|--------|-----------------|
| `app-changes-Feb-8-2026.md` | Current | Next.js + Vercel + Supabase + Claude API architecture |
| `TECHNICAL_SPEC.md` (in project mgmt folder) | Outdated | v1 architecture only (SQLite, localhost FastAPI) |

## Task: Security & compliance

| File | Status | What it contains |
|------|--------|-----------------|
| `docs/GDPR-GUIDE-SVENSKA-APPAR.md` | Current | GDPR checklist for Swedish Supabase apps (Feb 2026) |
| `SECURITY.md` | Current | 30 general security tips for vibe-coded apps |
| `app-changes-Feb-8-2026.md` | Current | RLS policies, auth hardening, Supabase security section |

## Task: Planning next work / roadmap

| File | Status | What it contains |
|------|--------|-----------------|
| `docs/GDPR-GUIDE-SVENSKA-APPAR.md` | Current | Implementation status checklist (what's done vs missing) |
| `CHANGELOG.md` (in project mgmt folder) | Outdated | v1 changelog only -- no v2 changelog exists yet |
| `GAP_ANALYSIS.md` (in project mgmt folder) | Outdated | v1 gap analysis -- historical reference only |
| `NEXT_STEPS.md` (in project mgmt folder) | Outdated | v1 action plan -- contains exposed credentials |

## Task: Dependency / environment setup

| File | Status | What it contains |
|------|--------|-----------------|
| `v2/requirements.txt` | Current | v2 Python deps (pinned versions) |
| `requirements.txt` (root) | Partial | May be used by Vercel -- unclear |
| `v1/requirements.txt` | Outdated | v1 deps -- do not use |

---

## Quick reference by question

| Question | Read this |
|----------|-----------|
| "What does this app do?" | `app-changes-Feb-8-2026.md` (core concept section) |
| "How is it built?" | `app-changes-Feb-8-2026.md` (stack + architecture) |
| "What's the database schema?" | `app-changes-Feb-8-2026.md` (aap_ tables section) |
| "Is it GDPR compliant?" | `docs/GDPR-GUIDE-SVENSKA-APPAR.md` |
| "Is it secure?" | `SECURITY.md` + `app-changes-Feb-8-2026.md` security section |
| "Why was it designed this way?" | `PHILOSOPHY.md` (UX values only) + `docs/DESIGN_HISTORY.md` |
| "What Python packages do I need?" | `v2/requirements.txt` |
| "What's outdated?" | `.claude/CODEBASE_AUDIT.md` |
