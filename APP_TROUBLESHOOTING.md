# App Troubleshooting Guide

Quick reference for recurring issues and their fixes. When something breaks, check here first.

---

## White Screen (React crash — nothing renders)

**Symptom**: Page loads but shows nothing — completely blank/white.

**Root cause**: Babel fails to parse JSX, or React crashes during mount. The app uses `@babel/standalone` in the browser to compile JSX, so any syntax error kills the entire page silently.

### Known causes & fixes

| # | Cause | Fix | Commit |
|---|-------|-----|--------|
| 1 | **Extra `</div>` tag** in a component (mismatched open/close) | Count `<div>` vs `</div>` in the component. Remove the extra one. | `fb4e6cd` |
| 2 | **`catch {}` without binding** — Babel version doesn't support ES2019 optional catch | Change `catch {}` → `catch (e) {}` everywhere | `a2083e1` |
| 3 | **React hooks after early return** — `useState()` called after a conditional `return` statement | Move ALL `useState`/`useEffect` calls to the TOP of the component, before any `if (...) return` | `0b5c6bd`, `2818ab8` |
| 4 | **Tailwind CDN broken** — unpinned CDN URL changed/disappeared | Pin Tailwind to specific version: `https://cdn.tailwindcss.com/3.4.16` | `6cf10bf` |

### How to debug

1. Open browser DevTools → **Console** tab (`F12`)
2. Look for red error messages — they usually say exactly what's wrong
3. If no console error, add this temporary overlay to `frontend.html` right after `<script type="text/babel">`:
   ```js
   window.onerror = function(msg, url, line, col, err) {
       document.body.innerHTML = '<pre style="color:red;padding:20px">' + msg + '\nLine: ' + line + '</pre>';
   };
   ```
4. Common error patterns:
   - `"Adjacent JSX elements must be wrapped"` → extra closing tag
   - `"Unexpected token"` → syntax error in JSX
   - `"React hooks must be called in the exact same order"` → hook after conditional return

---

## 403 Forbidden (Vercel blocks all traffic)

**Symptom**: Every page/API call returns 403. Not a code issue — Vercel itself refuses to serve.

### Check these in order

1. **Vercel Deployment Protection** (most common!)
   - Vercel Dashboard → project → **Settings** → **Deployment Protection**
   - If "Vercel Authentication" is **Enabled for Production** → set to **Only Preview Deployments** or **Off**
   - "Standard Protection" should only apply to preview, not production

2. **Failed deployment**
   - Vercel Dashboard → **Deployments** tab
   - Check if latest production deploy shows **Error** (red)
   - If so → click it → read **Build Logs** to find the Python/build error

3. **Domain/DNS issue**
   - Vercel Dashboard → **Settings** → **Domains**
   - Make sure the domain points to the correct project and shows a green checkmark

---

## Cover Letter Generation Stops Working

**Symptom**: "Kunde inte skapa personligt brev" error, or cover letters return empty/template text.

### Check these in order

1. **Anthropic API credits depleted**
   - Go to [Anthropic Console](https://console.anthropic.com) → **Billing** / **Usage**
   - If credits are at $0 → **add more credits**
   - This is the #1 cause of cover letter failures!

2. **API key doesn't support the model**
   - The app uses `claude-sonnet-4-5-20250929`. Not all API keys have access.
   - Check Anthropic Console → **API Keys** to verify your key's permissions
   - **Quick fix**: In `v2/api/index.py`, search for the model name and switch to `claude-3-5-sonnet-20241022` (widely available)
   - Past incidents: `e6a3664`, `1a103e0`, `1740bb9`

3. **Vercel function timeout**
   - AI calls can take 10-30 seconds
   - Make sure `v2/vercel.json` has `maxDuration` set (Vercel Pro allows up to 60s):
     ```json
     "functions": { "api/index.py": { "maxDuration": 60 } }
     ```
   - Past fix: `67cd61a`

4. **Haiku fallback**
   - The backend has automatic fallback: if Sonnet fails, it retries with Haiku
   - If both fail, check Anthropic Console — the API key itself may be invalid

---

## "Kunde inte skapa ansökan" (Apply button fails)

**Symptom**: Clicking apply shows an error toast.

### Causes

1. **Timeout** — the apply flow (cover letter + Gmail draft + DB save) can exceed Vercel's default 10s limit
   - Fix: ensure `maxDuration: 60` in vercel.json (see above)

2. **Supabase table/column missing** — new features need DB migrations
   - Check Supabase SQL Editor: `SELECT * FROM information_schema.columns WHERE table_name = 'applications';`
   - Compare with `v2/supabase_schema.sql`

3. **Gmail token expired** — if Gmail draft creation fails
   - User needs to reconnect Gmail in Profile tab

---

## Gmail Drafts Not Created

**Symptom**: Cover letter generates fine, but no draft appears in Gmail.

1. **Gmail not connected** — check Profile tab → Gmail section
2. **OAuth token expired** — disconnect and reconnect Gmail
3. **Missing CV file** — check that the bransch CV exists in `v2/api/cv_files/`
4. **Scopes issue** — the app needs `gmail.compose` scope

---

## Jobs Not Loading / Empty Job Feed

**Symptom**: The jobs tab shows no jobs or a loading spinner forever.

1. **Platsbanken API down** — the scraper calls `platsbanken-api.af.se`. Sometimes it's slow or down.
2. **No municipalities selected** — user needs to set locations in Platser tab
3. **All jobs filtered out** — check if excluded keywords are too aggressive
4. **DB query limit** — the backend fetches max 500 jobs. If none match filters, feed is empty.

---

## Environment Variables Reference

All set in **Vercel Dashboard → Settings → Environment Variables**:

| Variable | Purpose | Where to get it |
|----------|---------|-----------------|
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Full DB access | Supabase Dashboard → Settings → API (service_role key) |
| `SUPABASE_ANON_KEY` | Client-side auth | Supabase Dashboard → Settings → API (anon key) |
| `ANTHROPIC_API_KEY` | Claude AI calls | [Anthropic Console](https://console.anthropic.com) → API Keys |
| `GOOGLE_CLIENT_ID` | Gmail OAuth | Google Cloud Console → Credentials |
| `GOOGLE_CLIENT_SECRET` | Gmail OAuth | Google Cloud Console → Credentials |

**If any of these expire or are rotated**, update them in Vercel AND redeploy.

---

## Quick Diagnostic Checklist

When the app breaks, go through this in order:

- [ ] Can you load the site at all? (If 403 → check Vercel Deployment Protection)
- [ ] Does the page render? (If white screen → check browser Console for JS error)
- [ ] Can you log in? (If not → check Supabase auth settings)
- [ ] Do jobs load? (If not → check Platsbanken API / municipality settings)
- [ ] Do cover letters generate? (If not → check Anthropic credits / API key)
- [ ] Do Gmail drafts work? (If not → reconnect Gmail OAuth)

---

## Past Incident Log

| Date | Issue | Root Cause | Fix |
|------|-------|-----------|-----|
| 2026-02 | Cover letters stopped working | Anthropic API credits ran out | Refilled credits in Anthropic Console |
| 2026-02 | Cover letter API errors | API key didn't support Sonnet 4.5 model | Switched to claude-3-5-sonnet, then back after confirming key works |
| 2026-02 | "Kunde inte skapa ansökan" timeout | Vercel 10s default timeout too short for AI calls | Added `maxDuration: 60` to vercel.json |
| Earlier | White screen (multiple times) | Babel parse errors from mismatched tags, unsupported syntax, hooks violations | Various JSX fixes (see commits above) |
| 2026-02-23 | 403 on entire site | Under investigation — likely Vercel Deployment Protection or failed deploy | Check Vercel dashboard settings |
