## Summary

This PR enhances geographic job filtering by adding county (län) level matching, improves CV text handling by stripping stale personal information headers before sending to the AI cover letter generator, adds Swedish language quality checks using LanguageTool, and fixes the AI chat losing conversation context.

## Key Changes

### Language Feedback System
- **LanguageTool integration**: Replaced Claude-based self-review with [LanguageTool](https://languagetool.org/) API for Swedish grammar and spelling checks on generated cover letters
- **Anti-svengelska rules**: Added explicit prompt instructions preventing the AI from mixing English words into Swedish cover letters (e.g., "requirements" → "krav", "passionate" → "engagerad")
- **Anecdote chips in ApplyModal**: Users can now see and select which personal anecdotes/hobbies to weave into the cover letter directly from the apply dialog

### AI Chat Context Fix
- **Full conversation history**: The CV enhance chat (`/api/cv/enhance-chat`) now receives the entire conversation history instead of just the latest message
- **Proper multi-turn messages**: Backend builds a Claude messages array with all previous Q&A (up to 20 messages) so the AI never forgets what was already discussed
- **System prompt upgrade**: Uses a dedicated system prompt with explicit rules: "never repeat questions already answered", "use info the user already provided"
- **Master CV context**: Chat now fetches the user's current master CV data so the AI can reference actual entries when answering questions

### Geographic Filtering Improvements
- **County-level matching**: Added `_build_kommun_to_county()` function that parses `lan-data.js` to build a kommun ID → county name mapping, enabling jobs to be filtered by county as a fallback when municipality matching fails
- **Three-tier matching strategy**:
  1. Exact match on the `municipality` field (most reliable, clean data from Platsbanken)
  2. Substring match on `location` field only when municipality is empty (fallback)
  3. County (län) match as last resort
- **Consistent filtering**: Applied the same three-tier logic in `scrape_platsbanken()`, `list_jobs()`, and frontend job filtering code

### CV Text Improvements
- **Personal info stripping**: Added logic in `generate_cover_letter()` to remove stale personal information headers (name, phone, email, location) from CV text before sending to AI, ensuring the AI uses only current profile data from the "OM MIG" section
- **Location sync on profile updates**: When user's home location changes via `save_profile_from_quiz()`, automatically updates the location field in all user's bransch_cv headers

### Database & API Fixes
- **Upsert conflict resolution**: Added `on_conflict` parameter to `db_request()` for proper upserts on tables where the business key differs from the primary key (e.g., `user_id`). Applied to `user_profiles` and `user_job_preferences`
- **Municipality column**: Extended jobs table schema to include `municipality` field (distinct from `location` and `county`)
- **UTF-8 encoding fixes**: Fixed email draft generation to explicitly use UTF-8 encoding and improved filename sanitization for Unicode characters

### Frontend Enhancements
- **Tinder-style job feed**: Jobs the user has already acted on (applied, skipped, saved) disappear from the feed permanently
- **Unicode-safe filenames**: Updated PDF download filename generation using regex with Unicode property escapes
- **Consistent geography filtering**: Synchronized frontend job filtering logic with backend three-tier strategy

## Implementation Details

- Kommun-to-county mapping is built lazily on first use and cached globally
- County labels are extracted from selected kommun IDs and deduplicated using a Set
- CV header stripping detects personal info lines by pattern matching (phone numbers, emails, pipe-separated headers) and skips them before the first section keyword
- Location updates in bransch_cv headers find and replace the location part in pipe-separated header lines
- LanguageTool API is called as a final post-processing step; results shown inline to the user
- Chat conversation history is capped at 20 messages to stay within token limits

## Test Plan

- [ ] Generate a cover letter and verify no svengelska (English words mixed into Swedish)
- [ ] Check LanguageTool feedback appears after cover letter generation
- [ ] Upload a CV, chat about the changes, verify AI remembers previous messages
- [ ] Search jobs in a small municipality — verify county-level fallback finds regional jobs
- [ ] Update profile location — verify bransch_cv headers update automatically
- [ ] Create Gmail draft — verify UTF-8 characters in filenames work correctly
