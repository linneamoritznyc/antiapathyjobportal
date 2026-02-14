# READ THIS FIRST -- EVERY SESSION

You have no memory from previous sessions. Before doing ANYTHING:

1. Read `.claude/CODEBASE_AUDIT.md` -- Complete documentation analysis with conflict map
2. Read `.claude/SESSION_STATE.md` -- Where we left off last time (if it exists)
3. Read `.claude/COMMUNICATION_STYLE.md` -- How to communicate with me (if it exists)

Then execute the current task.

**Never skip this. You will waste my time if you don't read these first.**

## Critical facts you must know

- **Production URL:** https://platsbanken-ai.vercel.app
- **Architecture:** Next.js 14 on Vercel + Supabase PostgreSQL + Claude API
- **Active code:** v2/ folder ONLY -- v1/ is deprecated
- **Source of truth:** `app-changes-Feb-8-2026.md` -- this is the rebuild blueprint
- **7 of 15 docs are outdated** -- they describe v1 (SQLite, localhost, IMAP). Do NOT follow them.
- **NO localhost servers exist** -- everything runs on Vercel + Supabase cloud
- **Database:** Supabase PostgreSQL with `aap_` prefixed tables, NOT SQLite
- **Gmail:** Gmail API with OAuth, NOT IMAP with App Passwords
- **Auth:** Supabase Auth with Google OAuth, NOT single-user/no-auth
