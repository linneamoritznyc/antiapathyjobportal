# Next Steps - Anti-Apathy Job Portal

**Last Updated:** December 28, 2024  
**Current Status:** MVP completed, Gmail integration in testing

---

## 🔥 Immediate Actions (This Week)

### 1. Test Gmail Draft Integration ⏰ HIGH PRIORITY

**What to do:**
```bash
cd ~/Desktop/anti-apathy-portal-final
export GMAIL_APP_PASSWORD="xcwu agnn brcq unng"
python3 api_server.py
```

1. Open `http://localhost:8000`
2. Scrape jobs
3. Generate a cover letter
4. Click "Send to Gmail Draft" button
5. Verify draft appears in Gmail
6. Test editing draft in Gmail
7. Send one test application

**Expected Result:** Draft should appear in Gmail Drafts folder with subject and body correctly formatted.

**If it fails:**
- Check `api_server.py` has updated code with Gmail endpoint
- Verify environment variable is set: `echo $GMAIL_APP_PASSWORD`
- Check logs for error messages
- Verify Gmail App Password is correct (16 characters, no spaces)

---

### 2. Complete Frontend-Backend Gmail Flow

**Missing pieces:**
1. Frontend button for "Send to Gmail Draft" - needs to be added to `frontend.html`
2. Success/error messaging after draft creation
3. Link to Gmail Drafts after successful creation

**Code to add to frontend.html:**

```javascript
async function sendToGmailDraft() {
    const coverLetterText = document.getElementById('coverLetterOutput').textContent;
    const jobTitle = document.getElementById('jobTitle').value;
    const companyName = document.getElementById('companyName').value;
    
    const subject = `Ansökan - ${jobTitle} på ${companyName}`;
    const toEmail = "recruiter@company.com"; // TODO: Extract from job posting
    
    const response = await fetch('http://localhost:8000/api/gmail/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            subject: subject,
            body: coverLetterText,
            to_email: toEmail
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        alert('Gmail-utkast skapat! Öppnar Gmail...');
        window.open(data.drafts_url, '_blank');
    } else {
        alert('Fel: ' + data.detail);
    }
}
```

---

### 3. Set Up Git Workflow (COMPLETED ✓)

**Already done:**
- ✅ Repository created on GitHub: `linneamoritznyc/antiapathyjobportal`
- ✅ Initial commit pushed
- ✅ All files tracked

**Next Git actions:**

```bash
# When you make changes:
git add .
git commit -m "Describe what you changed"
git push

# Example:
git add api_server.py
git commit -m "Added Gmail draft endpoint"
git push
```

---

## 📅 Short-Term Goals (This Month)

### 1. Install and Test Claude Code

**Why:** Enables easier collaboration with Claude for debugging and feature additions.

**Steps:**
```bash
# Install (if Node is ready)
npm install -g @anthropic-ai/claude-code

# Authenticate
claude auth login

# Start using it
cd ~/Desktop/anti-apathy-portal-final
claude
```

**What you can do with Claude Code:**
- Ask it to fix bugs directly in your code
- Request new features and it implements them
- Debug issues without copy-pasting files
- Automatic git commits

---

### 2. Extract Email Addresses from Job Postings

**Current problem:** Manually entering "recruiter@company.com" for each application.

**Solution:** Use AI to extract contact information from job descriptions.

**Implementation:**

```python
def extract_contact_info(job_description: str) -> dict:
    """
    Uses AI to extract email and contact person from job posting.
    """
    prompt = f"""
    Analysera denna jobbannons och hitta kontaktinformation:
    
    {job_description}
    
    Returnera ENDAST JSON:
    {{
        "email": "found email or null",
        "contact_name": "contact person name or null"
    }}
    """
    
    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse JSON from response
    import json
    return json.loads(response.content[0].text)
```

**Add to workflow:**
- Run this when job is first displayed
- Store in database (contact_email column)
- Use in Gmail draft creation

**Estimated time:** 2-3 hours

---

### 3. Improve Cover Letter Quality

**Current issues:**
- Letters might be too generic
- Not always culturally appropriate for Swedish market
- Length varies too much

**Solutions:**

1. **Add examples to AI prompt:**
```python
prompt = f"""
Här är ett exempel på ett bra personligt brev:

[Insert example of excellent Swedish cover letter]

Nu, skriv ett liknande brev för: {job_description}
"""
```

2. **Enforce stricter length limits:**
```python
# In API prompt
"VIKTIGT: Exakt 250 ord (±10). Räkna ord innan du svarar."
```

3. **Add post-processing:**
```python
def validate_cover_letter(letter: str) -> bool:
    word_count = len(letter.split())
    if word_count < 150 or word_count > 350:
        return False
    if "Med vänliga hälsningar" not in letter:
        return False
    return True
```

**Estimated time:** 3-4 hours

---

## 🎯 Medium-Term Objectives (This Quarter)

### 1. Interview Tracking System

**What:** Track which applications led to interviews, store interview dates, add follow-up reminders.

**Database changes needed:**
```sql
ALTER TABLE applications ADD COLUMN interview_date TIMESTAMP;
ALTER TABLE applications ADD COLUMN interview_notes TEXT;
ALTER TABLE applications ADD COLUMN interview_feedback TEXT;
```

**New endpoints:**
```python
@app.post("/api/applications/{id}/schedule-interview")
async def schedule_interview(id: int, date: datetime):
    # Update database
    # Send calendar invite (future feature)
    pass

@app.get("/api/applications/interviews")
async def get_upcoming_interviews():
    # Return interviews sorted by date
    pass
```

---

### 2. Analytics Dashboard

**Metrics to track:**
- Application success rate (interviews per application)
- Response time from companies
- Best-performing industries
- Cover letter effectiveness (A/B testing)

**Visualization:**
- Chart.js for graphs
- Success rate by industry
- Timeline of applications

---

### 3. Automated Follow-Up System

**Feature:** Automatically create follow-up drafts 1-2 weeks after application if no response.

**Implementation:**
```python
def create_follow_up_draft(application_id: int):
    app = db.get_application(application_id)
    
    follow_up_text = f"""
    Hej,
    
    Jag skickade in en ansökan till er {app.job.title}-tjänst den 
    {app.sent_at.strftime('%Y-%m-%d')}. 
    
    Jag är fortsatt mycket intresserad av rollen och undrar om ni har 
    några uppdateringar gällande rekryteringsprocessen.
    
    Med vänliga hälsningar,
    Linnea Moritz
    """
    
    create_gmail_draft(
        subject=f"Följdfråga - {app.job.title}",
        body=follow_up_text,
        to_email=app.job.contact_email
    )
```

---

## 🚀 Long-Term Vision (This Year)

### 1. Multi-User Deployment

**Requirements:**
- User authentication (email + password)
- Personal CV uploads
- Private databases per user
- Billing/subscription system

**Tech stack changes:**
- PostgreSQL instead of SQLite
- Auth0 or similar for authentication
- AWS/Heroku for hosting
- Stripe for payments

---

### 2. Mobile App

**Platform:** React Native (reuse frontend logic)

**Features:**
- Push notifications for interview invites
- Quick-apply on mobile
- Voice-to-text for cover letter edits
- Location-based job filtering

---

### 3. AI Agent for Full Automation

**Vision:** User just says "apply to 10 customer service jobs" and system:
1. Finds suitable jobs
2. Generates tailored letters
3. Sends applications
4. Tracks responses
5. Schedules interviews
6. Sends follow-ups

**Requires:**
- More sophisticated AI (Claude with tools)
- Calendar integration (Google Calendar API)
- Email sending (not just drafts)
- User approval workflow

---

## 🚧 Current Blockers

### 1. Claude Code Installation Hanging ❗

**Issue:** Installation command from `claude.ai/install.sh` is not responding.

**Alternative solutions:**
- ✅ Try npm installation: `npm install -g @anthropic-ai/claude-code`
- ✅ Wait for Node.js to finish installing via Homebrew
- Check if Python version of Claude Code exists

**Impact:** Blocking easier development workflow with Claude.

---

### 2. Gmail Draft Button Not in Frontend ❗

**Issue:** Backend endpoint exists, but frontend button not implemented.

**Required:** Add button to `frontend.html` that calls `/api/gmail/draft`

**Impact:** Can't test full Gmail flow end-to-end.

---

### 3. Email Address Extraction Not Automated

**Issue:** Manually entering email addresses for each draft.

**Temporary workaround:** Use placeholder "recruiter@company.com"

**Proper solution:** Implement AI extraction (see Month 1 goals above)

---

## 💡 Feature Backlog (Ideas)

- [ ] PDF generation of applications for printing
- [ ] Salary negotiation guidance based on market data
- [ ] LinkedIn integration (auto-apply)
- [ ] Cover letter A/B testing
- [ ] Industry-specific tips database
- [ ] Company research automation (Glassdoor, etc.)
- [ ] Interview preparation chatbot
- [ ] Rejection tracking and analysis
- [ ] Success stories from other users
- [ ] Referral request automation

---

## ✅ Decision Points

### Immediate Decisions Needed:

1. **Keep project private or make public?**
   - Private: More control, no external contributions
   - Public: Portfolio piece, community feedback, potential collaborators

2. **Continue with dual AI (Claude + Gemini)?**
   - Keep both: Redundancy, fallback option
   - Pick one: Simpler, cheaper, easier to optimize

3. **Deploy to cloud now or later?**
   - Now: Get user feedback faster
   - Later: Perfect MVP first, then scale

### Recommended Decisions:

1. ✅ **Make public** - It's a great portfolio piece, no secrets in code
2. ✅ **Keep Claude only** - Better quality, you already have subscription
3. ✅ **Deploy later** - Focus on core features first (Month 2-3)

---

## 📋 Weekly Checklist

**Every Monday:**
- [ ] Test scraping (ensure Platsbanken API still works)
- [ ] Check for new jobs added
- [ ] Generate 2-3 sample cover letters
- [ ] Review application statistics

**Every Friday:**
- [ ] Git commit and push all changes
- [ ] Review week's applications and interviews
- [ ] Update roadmap based on learnings
- [ ] Plan next week's features

---

## 🤝 Resources Needed

### Immediately:
- ✅ GitHub account (done)
- ✅ Gmail App Password (done)
- ✅ Claude API access (done)
- ⏳ Node.js (installing)
- ⏳ Claude Code (pending Node)

### This Month:
- [ ] 2-3 hours/week for development
- [ ] Test Gmail account (separate from main)
- [ ] Feedback from 1-2 neurodivergent job seekers

### This Quarter:
- [ ] $20/month Claude Pro (already have)
- [ ] $5-10/month for hosting (when deploying)
- [ ] Design feedback (for UI improvements)

---

## 🎯 Success Criteria

**Week 1:**
- ✅ Gmail integration working end-to-end
- ✅ 5+ test applications sent successfully

**Month 1:**
- ✅ 20+ real applications submitted
- ✅ Email extraction automated
- ✅ Claude Code set up and working

**Quarter 1:**
- ✅ First interview from portal-generated application
- ✅ Analytics dashboard showing insights
- ✅ Follow-up system automated

**Year 1:**
- ✅ Job offer secured via the portal
- ✅ Multi-user version deployed
- ✅ 10+ active users

---

## 📞 When to Ask for Help

**Ask Claude (chat):**
- Strategic planning
- Architecture decisions
- Complex algorithm design
- Research and comparisons

**Ask Claude Code (terminal):**
- Bug fixes in existing code
- Adding new features
- Refactoring code structure
- Git workflow automation

**Ask human developers:**
- UX/UI feedback
- Real-world testing
- Job search domain expertise
- Deployment troubleshooting

---

**Next update:** After completing Week 1 goals (Gmail integration tested)
