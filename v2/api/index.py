"""
Anti-Apathy Job Portal v2
En jobbportal som hjälper dig söka jobb via e-post direkt till arbetsgivare.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import logging
import httpx
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI(
    title="Anti-Apathy Job Portal",
    description="Sök jobb utan apati. AI-genererade personliga brev, direkt till din Gmail.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== MODELS ==============

class JobSearchRequest(BaseModel):
    keywords: Optional[List[str]] = None
    location: Optional[str] = "Stockholm"


class GenerateLetterRequest(BaseModel):
    job_id: str
    user_cv_text: Optional[str] = None


class SaveApplicationRequest(BaseModel):
    job_id: str
    cover_letter: str
    status: str = "draft"


# ============== HELPERS ==============

def extract_email(text: str) -> Optional[str]:
    """Extract email from text, filtering out generic ones"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    exclude = ['noreply', 'info@arbetsformedlingen', 'kundtjanst@', 'support@']
    for email in emails:
        if not any(ex in email.lower() for ex in exclude):
            return email.lower()
    return None


def extract_contact_name(text: str) -> Optional[str]:
    """Extract contact person name from Swedish job ads"""
    patterns = [
        r'[Kk]ontakt(?:person)?[:\s]+([A-ZÅÄÖ][a-zåäö]+(?:\s+[A-ZÅÄÖ][a-zåäö]+)?)',
        r'[Ff]rågor till[:\s]+([A-ZÅÄÖ][a-zåäö]+(?:\s+[A-ZÅÄÖ][a-zåäö]+)?)',
        r'[Aa]nsökan till[:\s]+([A-ZÅÄÖ][a-zåäö]+(?:\s+[A-ZÅÄÖ][a-zåäö]+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            if len(name) > 3 and ' ' not in name or len(name.split()) == 2:
                return name
    return None


def calculate_priority(deadline: Optional[str]) -> str:
    """Calculate job priority based on deadline"""
    if not deadline:
        return "normal"
    try:
        deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        days_left = (deadline_date - datetime.now(deadline_date.tzinfo)).days
        if days_left <= 3:
            return "urgent"
        elif days_left <= 7:
            return "soon"
        return "normal"
    except:
        return "normal"


# ============== PLATSBANKEN SCRAPER ==============

async def scrape_platsbanken(keyword: str, location: str = "Stockholm", max_jobs: int = 15) -> List[Dict]:
    """
    Scrape jobs from Platsbanken API.
    Only returns jobs where you can apply via email (not portal).
    """
    jobs = []

    try:
        async with httpx.AsyncClient() as client:
            # Search for jobs
            response = await client.post(
                "https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search",
                headers={"Content-Type": "application/json"},
                json={
                    "filters": [
                        {"type": "freetext", "value": keyword},
                    ],
                    "fromDate": None,
                    "order": "date",
                    "maxRecords": 50,  # Get more to filter down
                    "startIndex": 0,
                    "source": "pb"
                },
                timeout=20
            )

            if response.status_code != 200:
                logger.error(f"Platsbanken API error: {response.status_code}")
                return jobs

            data = response.json()
            ads = data.get("ads", [])

            logger.info(f"Found {len(ads)} ads for '{keyword}'")

            for ad in ads:
                if len(jobs) >= max_jobs:
                    break

                job_id = str(ad.get("id", ""))
                title = ad.get("title", "Okänd tjänst")
                company = ad.get("workplaceName", "Okänt företag")
                job_location = ad.get("workplace", location)
                description = ad.get("description", "") or ""
                deadline = ad.get("lastApplicationDate")

                # Try to get email from description
                contact_email = extract_email(description)

                # Also check application details
                app_details = ad.get("applicationDetails", {}) or {}
                if not contact_email and app_details.get("email"):
                    contact_email = app_details.get("email")

                # Skip jobs without email (portal-only applications)
                if not contact_email:
                    continue

                # Extract contact name
                contact_name = extract_contact_name(description)
                if not contact_name and app_details.get("name"):
                    contact_name = app_details.get("name")

                # Check location match (fuzzy)
                if location.lower() not in job_location.lower() and job_location.lower() not in location.lower():
                    # Allow "Sverige" as fallback
                    if "sverige" not in job_location.lower():
                        continue

                job = {
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "description": description[:3000],
                    "url": f"https://arbetsformedlingen.se/platsbanken/annonser/{job_id}",
                    "deadline": deadline,
                    "priority": calculate_priority(deadline),
                    "contact_email": contact_email,
                    "contact_name": contact_name,
                    "source": "platsbanken",
                    "scraped_at": datetime.now().isoformat()
                }
                jobs.append(job)
                logger.info(f"  ✓ {title} @ {company} - {contact_email}")

            logger.info(f"Returning {len(jobs)} jobs with email application for '{keyword}'")

    except httpx.TimeoutException:
        logger.error(f"Timeout scraping Platsbanken for '{keyword}'")
    except Exception as e:
        logger.error(f"Error scraping Platsbanken: {e}")

    return jobs


# ============== COVER LETTER GENERATION ==============

# Default experience sections (used if no CV provided)
DEFAULT_EXPERIENCE = {
    "restaurant": """- Restaurangbiträde, Max Hamburgare (Apr-Aug 2024): Drive-in, kök, servering, kassa
- Barista/Försäljare, House of Beans (Aug 2024-Feb 2025): Kaffe, te, kundkontakt
- Cafépersonal, Coffeehouse by George (2014-2015): Kassahantering, barista""",

    "retail": """- Försäljare, House of Beans (Aug 2024-Feb 2025): Direktförsäljning, ensam i butik
- Kassapersonal, ICA Maxi (2015, 2017, 2019): Kassa, självscanning, frukt/grönt""",

    "customerservice": """- Innehållsmoderator, Clubhouse (Jun 2021-Jan 2022): Trust & Safety, support
- Innehållsanalytiker, Google Ads (Maj 2018-Apr 2019): 100+ annonser/dag
- Global Marketing, Minerva Project (Sep 2019-Apr 2020): Kundservice via Intercom""",

    "tech": """- Webbutveckling: Fullstack-appar med React, Python/FastAPI, PostgreSQL
- Deployment: Vercel, Supabase, API-integrationer
- Innehållsanalytiker, Google Ads (2018-2019): Teknisk granskning, dataanalys""",

    "default": """- Bred erfarenhet inom service, kundkontakt och administration
- Flexibel, pålitlig och snabb på att lära mig nya system
- B-körkort och flexibel med arbetstider"""
}


def detect_job_category(title: str, description: str) -> str:
    """Detect job category for matching experience"""
    text = f"{title} {description}".lower()

    if any(w in text for w in ["servitör", "servitris", "restaurang", "kock", "café", "barista", "kök"]):
        return "restaurant"
    if any(w in text for w in ["butik", "kassa", "försäljare", "säljare", "retail"]):
        return "retail"
    if any(w in text for w in ["kundtjänst", "customer service", "support", "kundservice"]):
        return "customerservice"
    if any(w in text for w in ["it", "tech", "utvecklare", "developer", "webbutvecklare", "frontend", "backend", "data"]):
        return "tech"
    return "default"


async def generate_cover_letter(job: Dict, user_cv_text: Optional[str] = None) -> str:
    """Generate personalized cover letter using Claude"""

    if not ANTHROPIC_API_KEY:
        return generate_template_letter(job)

    # Get relevant experience
    category = detect_job_category(job.get("title", ""), job.get("description", ""))
    experience = user_cv_text or DEFAULT_EXPERIENCE.get(category, DEFAULT_EXPERIENCE["default"])

    contact_greeting = f"Hej {job.get('contact_name', '')}!" if job.get('contact_name') else "Hej!"

    prompt = f"""Skriv ett personligt brev på svenska för denna jobbansökan.

JOBBET:
- Titel: {job.get('title')}
- Företag: {job.get('company')}
- Plats: {job.get('location')}
- Beskrivning: {job.get('description', '')[:1500]}

MIN ERFARENHET:
{experience}

OM MIG:
- Linnea Moritz, 28 år, bor i Sollentuna
- B-körkort, flexibel med arbetstider
- Telefon: 0761166109
- Svenska (modersmål), Engelska (flytande)

INSTRUKTIONER:
1. Börja med: {contact_greeting}
2. Skriv 150-200 ord på naturlig, varm svenska
3. Lyft fram 2-3 specifika erfarenheter som matchar jobbet
4. Nämn att jag bor i Sollentuna, har B-körkort och är flexibel
5. Avsluta med:
   Med vänlig hälsning,
   Linnea Moritz
   0761166109
   linneamoritzCV@gmail.com

Skriv ENDAST brevet, inget annat."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 600,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"].strip()
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Error generating letter: {e}")

    return generate_template_letter(job)


def generate_template_letter(job: Dict) -> str:
    """Fallback template when API fails"""
    contact_greeting = f"Hej {job.get('contact_name', '')}!" if job.get('contact_name') else "Hej!"

    return f"""{contact_greeting}

Jag söker tjänsten som {job.get('title', 'tjänsten')} hos {job.get('company', 'er')}.

Jag har bred erfarenhet från service och kundkontakt, och trivs i roller där jag får hjälpa människor. Jag bor i Sollentuna, har B-körkort och är flexibel med arbetstider.

Jag ser fram emot att höra från er!

Med vänlig hälsning,
Linnea Moritz
0761166109
linneamoritzCV@gmail.com"""


# ============== SUPABASE DATABASE ==============

async def db_request(method: str, table: str, data: dict = None, params: dict = None) -> Optional[List]:
    """Make request to Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                headers["Prefer"] = "resolution=merge-duplicates,return=representation"
                response = await client.post(url, headers=headers, json=data, timeout=10)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data, params=params, timeout=10)
            else:
                return None

            if response.status_code >= 400:
                logger.error(f"DB error: {response.status_code} - {response.text}")
                return None

            return response.json() if response.text else []

    except Exception as e:
        logger.error(f"DB request error: {e}")
        return None


async def save_jobs_to_db(jobs: List[Dict]) -> int:
    """Save jobs to database, returns count of saved jobs"""
    if not SUPABASE_URL:
        return 0

    saved = 0
    for job in jobs:
        result = await db_request("POST", "jobs", data=job)
        if result:
            saved += 1
    return saved


async def get_jobs_from_db(limit: int = 50) -> List[Dict]:
    """Get jobs from database"""
    jobs = await db_request("GET", "jobs", params={
        "order": "scraped_at.desc",
        "limit": str(limit)
    })
    return jobs or []


async def get_applications_from_db() -> List[Dict]:
    """Get all applications"""
    apps = await db_request("GET", "applications", params={
        "order": "created_at.desc"
    })
    return apps or []


# ============== API ENDPOINTS ==============

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "supabase": bool(SUPABASE_URL and SUPABASE_KEY),
        "claude": bool(ANTHROPIC_API_KEY)
    }


@app.post("/api/scrape")
async def scrape_jobs(request: JobSearchRequest = None):
    """Scrape jobs from Platsbanken"""
    keywords = request.keywords if request and request.keywords else ["servitör", "kundtjänst", "butik"]
    location = request.location if request else "Stockholm"

    all_jobs = []
    for keyword in keywords[:5]:  # Max 5 keywords
        jobs = await scrape_platsbanken(keyword, location, max_jobs=10)
        all_jobs.extend(jobs)

    # Remove duplicates by job ID
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique_jobs.append(job)

    # Save to database if configured
    saved_count = await save_jobs_to_db(unique_jobs)

    return {
        "success": True,
        "jobs_found": len(unique_jobs),
        "jobs_saved": saved_count,
        "jobs": unique_jobs
    }


@app.get("/api/jobs")
async def list_jobs(limit: int = 50):
    """List all jobs"""
    # Try database first
    jobs = await get_jobs_from_db(limit)

    if jobs:
        return {"success": True, "source": "database", "jobs": jobs}

    # Fallback: scrape live
    jobs = await scrape_platsbanken("jobb", "Stockholm", max_jobs=limit)
    return {"success": True, "source": "live", "jobs": jobs}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get single job by ID"""
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if jobs and len(jobs) > 0:
        return {"success": True, "job": jobs[0]}
    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs/{job_id}/letter")
async def create_letter(job_id: str, request: GenerateLetterRequest = None):
    """Generate cover letter for a job"""
    # Get job from database
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[0]
    cv_text = request.user_cv_text if request else None

    letter = await generate_cover_letter(job, cv_text)

    return {
        "success": True,
        "job_id": job_id,
        "job_title": job.get("title"),
        "company": job.get("company"),
        "contact_email": job.get("contact_email"),
        "contact_name": job.get("contact_name"),
        "cover_letter": letter
    }


@app.post("/api/applications")
async def save_application(request: SaveApplicationRequest):
    """Save an application"""
    data = {
        "job_id": request.job_id,
        "cover_letter": request.cover_letter,
        "status": request.status,
        "created_at": datetime.now().isoformat()
    }

    result = await db_request("POST", "applications", data=data)
    if result:
        return {"success": True, "application": result[0]}
    raise HTTPException(status_code=500, detail="Could not save application")


@app.get("/api/applications")
async def list_applications():
    """List all applications"""
    apps = await get_applications_from_db()
    return {"success": True, "applications": apps}


@app.get("/api/stats")
async def get_stats():
    """Get statistics"""
    jobs = await get_jobs_from_db(1000)
    apps = await get_applications_from_db()

    return {
        "success": True,
        "stats": {
            "total_jobs": len(jobs) if jobs else 0,
            "total_applications": len(apps) if apps else 0,
            "drafts": len([a for a in (apps or []) if a.get("status") == "draft"]),
            "sent": len([a for a in (apps or []) if a.get("status") == "sent"]),
            "interviews": len([a for a in (apps or []) if a.get("status") == "interview"])
        }
    }


# ============== FRONTEND ==============

FRONTEND_HTML = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anti-Apathy Job Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * { font-family: system-ui, -apple-system, sans-serif; }
        .gradient { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%); }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;

        // Stats component
        const Stats = ({ stats }) => (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                    { label: "Jobb", value: stats.total_jobs, color: "text-indigo-600" },
                    { label: "Utkast", value: stats.drafts, color: "text-amber-600" },
                    { label: "Skickade", value: stats.sent, color: "text-green-600" },
                    { label: "Intervjuer", value: stats.interviews, color: "text-purple-600" }
                ].map(({ label, value, color }) => (
                    <div key={label} className="bg-white rounded-xl p-4 shadow-sm">
                        <div className={`text-3xl font-bold ${color}`}>{value || 0}</div>
                        <div className="text-slate-500 text-sm">{label}</div>
                    </div>
                ))}
            </div>
        );

        // Job card component
        const JobCard = ({ job, onGenerate, loading }) => {
            const priorityColors = {
                urgent: "bg-red-100 text-red-700",
                soon: "bg-amber-100 text-amber-700",
                normal: "bg-green-100 text-green-700"
            };

            return (
                <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-slate-100">
                    <div className="p-6">
                        <div className="flex items-start justify-between mb-3">
                            <div>
                                <span className={`text-xs px-2 py-1 rounded-full ${priorityColors[job.priority] || priorityColors.normal}`}>
                                    {job.priority === 'urgent' ? '⚡ Akut' : job.priority === 'soon' ? '⏰ Snart' : '✓ Normal'}
                                </span>
                            </div>
                            {job.deadline && (
                                <span className="text-xs text-slate-400">
                                    Deadline: {new Date(job.deadline).toLocaleDateString('sv-SE')}
                                </span>
                            )}
                        </div>

                        <h3 className="text-xl font-semibold text-slate-800 mb-1">{job.title}</h3>
                        <p className="text-indigo-600 font-medium mb-1">{job.company}</p>
                        <p className="text-slate-500 text-sm mb-4">{job.location}</p>

                        <p className="text-slate-600 text-sm mb-4 line-clamp-3">
                            {job.description?.slice(0, 200)}...
                        </p>

                        <div className="bg-slate-50 rounded-lg p-3 mb-4">
                            <p className="text-sm text-slate-600">
                                <span className="font-medium">📧 Ansök till:</span>{' '}
                                <a href={`mailto:${job.contact_email}`} className="text-indigo-600 hover:underline">
                                    {job.contact_email}
                                </a>
                                {job.contact_name && <span className="text-slate-400"> ({job.contact_name})</span>}
                            </p>
                        </div>

                        <div className="flex gap-2">
                            <button
                                onClick={() => onGenerate(job)}
                                disabled={loading}
                                className="flex-1 bg-indigo-600 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
                            >
                                {loading ? 'Genererar...' : '✨ Generera brev'}
                            </button>
                            <a
                                href={job.url}
                                target="_blank"
                                className="px-4 py-2.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition"
                            >
                                Se annons
                            </a>
                        </div>
                    </div>
                </div>
            );
        };

        // Letter modal
        const LetterModal = ({ isOpen, job, letter, onClose, onCopy, onEmail }) => {
            const [editedLetter, setEditedLetter] = useState(letter);

            useEffect(() => setEditedLetter(letter), [letter]);

            if (!isOpen) return null;

            return (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-xl">
                        <div className="gradient text-white p-6">
                            <h3 className="text-xl font-bold">Personligt brev</h3>
                            <p className="opacity-90">{job?.title} @ {job?.company}</p>
                        </div>
                        <div className="p-6">
                            <textarea
                                value={editedLetter}
                                onChange={(e) => setEditedLetter(e.target.value)}
                                className="w-full h-64 p-4 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                            <div className="flex gap-3 mt-4">
                                <button
                                    onClick={() => onEmail(job, editedLetter)}
                                    className="flex-1 bg-green-600 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-green-700 transition"
                                >
                                    📧 Öppna i Gmail
                                </button>
                                <button
                                    onClick={() => onCopy(editedLetter)}
                                    className="px-4 py-2.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition"
                                >
                                    📋 Kopiera
                                </button>
                                <button
                                    onClick={onClose}
                                    className="px-4 py-2.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition"
                                >
                                    Stäng
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        // Main App
        const App = () => {
            const [jobs, setJobs] = useState([]);
            const [stats, setStats] = useState({});
            const [loading, setLoading] = useState(false);
            const [scraping, setScraping] = useState(false);
            const [selectedJob, setSelectedJob] = useState(null);
            const [coverLetter, setCoverLetter] = useState('');
            const [showModal, setShowModal] = useState(false);
            const [keywords, setKeywords] = useState('');
            const [message, setMessage] = useState(null);

            const fetchJobs = async () => {
                const res = await fetch('/api/jobs');
                const data = await res.json();
                if (data.success) setJobs(data.jobs || []);
            };

            const fetchStats = async () => {
                const res = await fetch('/api/stats');
                const data = await res.json();
                if (data.success) setStats(data.stats || {});
            };

            const handleScrape = async () => {
                setScraping(true);
                setMessage(null);
                try {
                    const kw = keywords.trim() ? keywords.split(',').map(k => k.trim()) : null;
                    const res = await fetch('/api/scrape', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ keywords: kw })
                    });
                    const data = await res.json();
                    if (data.success) {
                        setMessage({ type: 'success', text: `Hittade ${data.jobs_found} jobb med e-postansökan!` });
                        fetchJobs();
                        fetchStats();
                    }
                } catch (err) {
                    setMessage({ type: 'error', text: 'Kunde inte hämta jobb' });
                }
                setScraping(false);
            };

            const handleGenerate = async (job) => {
                setLoading(true);
                setSelectedJob(job);
                try {
                    const res = await fetch(`/api/jobs/${job.id}/letter`, { method: 'POST' });
                    const data = await res.json();
                    if (data.success) {
                        setCoverLetter(data.cover_letter);
                        setShowModal(true);
                    }
                } catch (err) {
                    setMessage({ type: 'error', text: 'Kunde inte generera brev' });
                }
                setLoading(false);
            };

            const handleCopy = (text) => {
                navigator.clipboard.writeText(text);
                setMessage({ type: 'success', text: 'Kopierat till urklipp!' });
            };

            const handleEmail = (job, letter) => {
                const subject = encodeURIComponent(`Ansökan: ${job.title}`);
                const body = encodeURIComponent(letter);
                window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${job.contact_email}&su=${subject}&body=${body}`, '_blank');
            };

            useEffect(() => {
                fetchJobs();
                fetchStats();
            }, []);

            return (
                <div className="min-h-screen">
                    <header className="gradient text-white py-8 px-4">
                        <div className="max-w-5xl mx-auto">
                            <h1 className="text-3xl font-bold mb-2">Anti-Apathy Job Portal</h1>
                            <p className="opacity-90">Sök jobb utan apati. En ansökan i taget.</p>
                        </div>
                    </header>

                    <main className="max-w-5xl mx-auto px-4 py-8">
                        {message && (
                            <div className={`mb-6 p-4 rounded-lg ${message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                                {message.text}
                                <button onClick={() => setMessage(null)} className="float-right font-bold">×</button>
                            </div>
                        )}

                        <Stats stats={stats} />

                        <div className="bg-white rounded-xl p-6 shadow-sm mb-8">
                            <h2 className="text-lg font-semibold mb-4">🔍 Sök nya jobb</h2>
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={keywords}
                                    onChange={(e) => setKeywords(e.target.value)}
                                    placeholder="t.ex. servitör, kundtjänst, butik"
                                    className="flex-1 border border-slate-200 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
                                />
                                <button
                                    onClick={handleScrape}
                                    disabled={scraping}
                                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
                                >
                                    {scraping ? 'Söker...' : 'Sök jobb'}
                                </button>
                            </div>
                            <p className="text-sm text-slate-500 mt-2">
                                Visar endast jobb där du kan ansöka via e-post direkt till arbetsgivaren.
                            </p>
                        </div>

                        <h2 className="text-lg font-semibold mb-4">📋 Jobb att söka ({jobs.length})</h2>

                        {jobs.length === 0 ? (
                            <div className="bg-white rounded-xl p-12 text-center shadow-sm">
                                <p className="text-slate-600 mb-4">Inga jobb än. Klicka på "Sök jobb" för att hitta nya!</p>
                            </div>
                        ) : (
                            <div className="grid md:grid-cols-2 gap-4">
                                {jobs.map(job => (
                                    <JobCard
                                        key={job.id}
                                        job={job}
                                        onGenerate={handleGenerate}
                                        loading={loading && selectedJob?.id === job.id}
                                    />
                                ))}
                            </div>
                        )}
                    </main>

                    <LetterModal
                        isOpen={showModal}
                        job={selectedJob}
                        letter={coverLetter}
                        onClose={() => setShowModal(false)}
                        onCopy={handleCopy}
                        onEmail={handleEmail}
                    />
                </div>
            );
        };

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>'''


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend"""
    return FRONTEND_HTML


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})
