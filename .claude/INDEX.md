# Documentation Index

Map of task types to the actual documentation files in this repo.

---

## Task: Understanding the project

| File | What it contains |
|------|-----------------|
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/README.md` | Top-level README - AI-powered job app automation for neurodivergent job seekers in Sweden |
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/PROJECT_OVERVIEW.md` | MVP scope, version, status summary |
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/PHILOSOPHY.md` | Core design principle: "Automate the mechanical, preserve the meaningful" |
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/INDEX.md` | Original documentation index for the project management folder |

## Task: Architecture & technical decisions

| File | What it contains |
|------|-----------------|
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/TECHNICAL_SPEC.md` | Full-stack architecture spec (Python backend + React frontend) |
| `docs/DESIGN_HISTORY.md` | Visual design evolution, original vs current layout |
| `app-changes-Feb-8-2026.md` | Major dev brief - uses Bidragsguiden as architectural reference for rebuild |

## Task: Security & compliance

| File | What it contains |
|------|-----------------|
| `SECURITY.md` | 30 security tips for vibe-coded apps (Swedish) |
| `docs/GDPR-GUIDE-SVENSKA-APPAR.md` | GDPR checklist for Swedish web apps using Supabase stack |

## Task: Planning next work / roadmap

| File | What it contains |
|------|-----------------|
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/NEXT_STEPS.md` | Prioritized next steps, Gmail integration status |
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/GAP_ANALYSIS.md` | Gap analysis of MVP vs production-ready (Dec 2024) |
| `anti apathy job portal DOCUMENTATION AND PROJECT MANAGEMENT/CHANGELOG.md` | All notable changes, Keep a Changelog format |

## Task: Dependency / environment setup

| File | What it contains |
|------|-----------------|
| `requirements.txt` | Root-level Python deps (FastAPI, uvicorn, pydantic, httpx) |
| `v1/requirements.txt` | v1 deps (FastAPI, uvicorn, dotenv, pydantic, pydantic-settings) |
| `v2/requirements.txt` | v2 deps (pinned versions - FastAPI 0.109.0, httpx 0.26.0, etc.) |

---

## Quick reference by question

| Question | Read these |
|----------|-----------|
| "What does this app do?" | `README.md` (in project management folder), `PROJECT_OVERVIEW.md` |
| "How is it built?" | `TECHNICAL_SPEC.md`, `app-changes-Feb-8-2026.md` |
| "What changed recently?" | `CHANGELOG.md`, `app-changes-Feb-8-2026.md` |
| "What should I work on next?" | `NEXT_STEPS.md`, `GAP_ANALYSIS.md` |
| "Is it GDPR compliant?" | `docs/GDPR-GUIDE-SVENSKA-APPAR.md` |
| "Is it secure?" | `SECURITY.md` |
| "Why was it designed this way?" | `PHILOSOPHY.md`, `docs/DESIGN_HISTORY.md` |
| "What Python packages do I need?" | `requirements.txt` (root or version-specific) |
