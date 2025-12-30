# 🎯 Anti-Apathy Job Portal

> AI-powered job application automation for neurodivergent job seekers in Sweden

[![Status](https://img.shields.io/badge/status-MVP-green)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)]()
[![License](https://img.shields.io/badge/license-TBD-orange)]()

---

## 📖 What It Does

Anti-Apathy Job Portal automates the mechanical parts of job searching while preserving your control over final decisions. It:

1. **Scrapes** job postings from Platsbanken (Sweden's national employment service)
2. **Generates** personalized cover letters using AI (Claude/Gemini)
3. **Selects** the optimal CV from 8 industry-specific personas
4. **Creates** Gmail drafts ready for you to review and send

**Built for neurodivergent profiles:** Reduces decision fatigue, provides structure, and eliminates repetitive tasks.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833)
- API key for [Claude](https://console.anthropic.com/) or [Gemini](https://ai.google.dev/)

### Installation

```bash
# Clone the repository
git clone https://github.com/linneamoritznyc/antiapathyjobportal.git
cd antiapathyjobportal

# Set up environment variables
export GMAIL_APP_PASSWORD="your-16-char-app-password"
export ANTHROPIC_API_KEY="sk-ant-..."  # OR
export GEMINI_API_KEY="your-gemini-key"

# Start the server
python3 api_server.py
```

### Usage

1. Open your browser to `http://localhost:8000`
2. Click **"Scrape Jobs"** to fetch latest Swedish job listings
3. Browse available positions
4. Click **"Generate Letter"** on any job you're interested in
5. Review the AI-generated cover letter (edit if needed)
6. Click **"Send to Gmail Draft"** to create an email draft
7. Go to Gmail, finalize, and send your application

---

## 📁 Project Structure

```
anti-apathy-portal-final/
│
├── api_server.py              # FastAPI backend server
├── job_portal_backend.py      # Core scraping & AI logic
├── fix_my_backend.py          # Debugging utility
├── frontend.html              # React + Tailwind interface
│
├── data/
│   └── jobs.db                # SQLite database (auto-created)
│
├── CV_Linnea_Moritz_*.pdf     # 8 industry-specific CV personas
│   ├── Butik_Kassa.pdf        # Retail & cashier
│   ├── Content_Moderation.pdf # Digital safety
│   ├── Industri_Tradgard.pdf  # Industrial work
│   ├── Konst_Kultur.pdf       # Arts & culture
│   ├── Kundtjanst.pdf         # Customer service
│   ├── Restaurang_Cafe.pdf    # Hospitality
│   ├── Tech_Kontor.pdf        # Technical admin
│   └── Vard_Omsorg.pdf        # Healthcare
│
├── photo.jpg                  # Profile photo
└── __pycache__/               # Python cache (auto-generated)
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GMAIL_APP_PASSWORD` | 16-character app password from Google | ✅ Yes |
| `ANTHROPIC_API_KEY` | Claude API key (starts with `sk-ant-`) | One of these |
| `GEMINI_API_KEY` | Google Gemini API key | One of these |
| `PORT` | Server port (default: 8000) | ❌ Optional |

### Getting Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate password for "Mail" on "Other (Custom name)"
5. Copy the 16-character password (no spaces)

### Getting AI API Keys

**Claude (Anthropic):**
1. Sign up at [console.anthropic.com](https://console.anthropic.com/)
2. Add billing (pay-as-you-go)
3. Create API key in Settings
4. Copy key starting with `sk-ant-`

**Gemini (Google):**
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create API key
3. Copy the key

---

## 🎨 Features

### ✅ Current Features

- **Automated Job Scraping** from Platsbanken
- **AI Cover Letter Generation** (Claude Sonnet 4 or Gemini)
- **8 Industry-Specific CV Personas** (auto-selected)
- **Gmail Draft Creation** (IMAP integration)
- **Job Tracking Database** (SQLite)
- **Application Status Management**
- **Statistics Dashboard**
- **React + Tailwind Frontend**

### 🚧 In Development

- Email address extraction from job postings
- Automated contact enrichment
- Interview tracking
- Follow-up scheduling

### 💡 Future Roadmap

- Cloud deployment
- Multi-user support
- Advanced analytics
- PDF generation
- Mobile app

---

## 🛠️ Dependencies

### Python Backend

```python
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
anthropic>=0.3.0  # For Claude
google-generativeai>=0.2.0  # For Gemini
```

### Frontend

- React (included via CDN)
- Tailwind CSS (included via CDN)
- Babel (included via CDN for JSX)

---

## 🎯 How It Works

### 1. Job Scraping Flow

```
Platsbanken API → BeautifulSoup Parser → Job Metadata Extraction → SQLite Storage
```

**What's Captured:**
- Job title
- Company name
- Job description (full text)
- Application deadline
- Job URL
- Industry category

### 2. Cover Letter Generation

```
Job Description → AI Prompt Engineering → Claude/Gemini API → Personalized Letter
```

**AI Context Includes:**
- Job requirements
- Company information
- Selected CV persona
- Industry-specific language
- Swedish cultural norms

### 3. CV Selection Logic

```python
# Automatic industry detection
if "butik" in job_title or "kassa" in job_description:
    selected_cv = "CV_Linnea_Moritz_Butik_Kassa.pdf"
elif "tech" in job_title or "IT" in job_description:
    selected_cv = "CV_Linnea_Moritz_Tech_Kontor.pdf"
# ... etc for all 8 personas
```

### 4. Gmail Draft Creation

```
Cover Letter → Email Formatting → IMAP Connection → Gmail [Drafts] Folder
```

**Security:** Uses App Passwords (not your main password), all credentials in environment variables.

---

## 🔐 Security & Privacy

- ✅ **No passwords in code** - All credentials via environment variables
- ✅ **Local data storage** - SQLite database on your machine
- ✅ **No cloud dependencies** - Runs entirely on localhost
- ✅ **App Passwords** - Gmail access via secure app-specific passwords
- ✅ **User control** - All applications reviewed before sending

**Data Stored Locally:**
- Job metadata (public information)
- Generated cover letters
- Application tracking (which jobs applied to)

**Data NOT Stored:**
- Your actual Gmail password
- API keys (only in environment)
- Sent emails (only drafts created)

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Check Python version
python3 --version  # Must be 3.9+

# Check if port is available
lsof -i :8000  # Should show nothing

# Verify environment variables
echo $GMAIL_APP_PASSWORD  # Should print your password
echo $ANTHROPIC_API_KEY   # Should print your key
```

### Gmail draft creation fails

**Error:** `GMAIL_APP_PASSWORD environment variable not set`

```bash
# Make sure you exported it in the SAME terminal session
export GMAIL_APP_PASSWORD="your-password-here"

# Restart server in same terminal
python3 api_server.py
```

**Error:** `Gmail authentication failed`

- Verify App Password is correct (16 characters, no spaces)
- Confirm 2-Step Verification is enabled in Google Account
- Try generating a new App Password

### AI generation not working

**Error:** `API key not found`

```bash
# Set the correct API key
export ANTHROPIC_API_KEY="sk-ant-..."  # For Claude
# OR
export GEMINI_API_KEY="your-key"  # For Gemini
```

**Error:** `Rate limit exceeded`

- You've hit API usage limits
- Wait a few minutes or upgrade API plan
- Switch to alternative AI provider

### Frontend shows blank page

1. Make sure server is running (`python3 api_server.py`)
2. Open browser to exactly `http://localhost:8000` (not 127.0.0.1)
3. Check browser console for JavaScript errors (F12)
4. Verify CORS is enabled in `api_server.py`

---

## 📊 API Endpoints

### Job Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/next` | Get next job to review |
| GET | `/api/jobs` | List all jobs (limit 50) |
| GET | `/api/jobs/{id}` | Get specific job details |
| POST | `/api/jobs/{id}/generate-letter` | Generate cover letter |
| POST | `/api/jobs/{id}/skip` | Skip a job |
| POST | `/api/jobs/{id}/apply` | Save application |

### Scraping & Enrichment

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scrape` | Start scraping (async) |
| POST | `/api/scrape/sync` | Scrape and wait for results |
| POST | `/api/enrich-contacts` | Enrich jobs with contact info |

### Gmail Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/gmail/draft` | Create Gmail draft directly |
| POST | `/api/jobs/{id}/create-draft` | Create draft for specific job |

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get application statistics |
| GET | `/api/applications` | List all applications |

---

## 🤝 Contributing

This is a personal project by Linnea Moritz. If you're interested in adapting it for your own use:

1. Fork the repository
2. Customize CV personas with your own PDFs
3. Adjust AI prompts in `job_portal_backend.py`
4. Modify frontend styling in `frontend.html`

**Note:** This project is tailored to Swedish job market (Platsbanken). Adapting to other countries requires changing the scraping source.

---

## 📄 License

License to be determined. Currently a private project.

---

## 🙏 Acknowledgments

**Built by:** Linnea Moritz ([@linneamoritznyc](https://github.com/linneamoritznyc))

**AI Assistance:**
- Claude (Anthropic) - Development partner
- Claude Code - Terminal coding tool

**Inspiration:**
- The neurodivergent community's need for structured, low-friction job search tools
- Personal experience navigating Swedish employment systems

---

## 📞 Support

For issues or questions:
- Open a GitHub issue (when repository is public)
- Check `docs/TROUBLESHOOTING.md` for common solutions
- Review conversation history for implementation details

---

**Ready to start?** Run `python3 api_server.py` and open `http://localhost:8000` 🚀
