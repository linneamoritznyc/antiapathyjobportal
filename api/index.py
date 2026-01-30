"""
Anti-Apathy Job Portal - Vercel Serverless Entry Point
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import json
import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI(
    title="Anti-Apathy Job Portal API",
    description="AI-driven jobbsökningsportal för neurodivergenta profiler",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ENUMS & MODELS ===

class JobPriority(Enum):
    AKUT = "akut"
    STRATEGISK = "strategisk"
    HIDDEN = "hidden"


class ApplicationStatus(Enum):
    NEW = "new"
    LETTER_GENERATED = "letter_generated"
    DRAFT_SAVED = "draft_saved"
    SENT = "sent"
    INTERVIEW = "interview"
    REJECTED = "rejected"


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    priority: str
    deadline: Optional[str]
    contact_email: Optional[str]
    contact_name: Optional[str]
    why_perfect: Optional[str]
    created_at: str
    link_status: str = "active"

    def to_dict(self):
        return asdict(self)


# Pydantic models for requests
class ApplyRequest(BaseModel):
    cover_letter: str
    gmail_draft_id: Optional[str] = None


class CreateDraftRequest(BaseModel):
    cover_letter: str
    to_email: Optional[str] = None


class SkipRequest(BaseModel):
    reason: Optional[str] = None


# === SUPABASE DATABASE FUNCTIONS ===

async def supabase_request(method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
    """Make a request to Supabase REST API"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data, params=params)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unknown method: {method}")

        if response.status_code >= 400:
            logger.error(f"Supabase error: {response.status_code} - {response.text}")
            return None

        if response.text:
            return response.json()
        return {}


async def get_next_job() -> Optional[Dict]:
    """Get next job to review - prioritizes AKUT, then STRATEGISK"""
    allowed_locations = ["Stockholm", "Sollentuna", "Vetlanda", "Nässjö", "Eksjö", "Holsbybrunn", "Småland", "Jönköping"]

    # Get jobs that don't have applications
    jobs = await supabase_request(
        "GET",
        "jobs",
        params={
            "link_status": "eq.active",
            "order": "priority.asc,deadline.asc",
            "limit": "50"
        }
    )

    if not jobs:
        return None

    # Get jobs with applications
    applications = await supabase_request("GET", "applications", params={"select": "job_id"})
    applied_job_ids = {app["job_id"] for app in (applications or [])}

    # Filter jobs
    for job in jobs:
        if job["id"] in applied_job_ids:
            continue

        # Check location
        job_location = job.get("location", "")
        if any(loc.lower() in job_location.lower() for loc in allowed_locations):
            return job

    return None


async def get_job_by_id(job_id: str) -> Optional[Dict]:
    """Get job by ID"""
    jobs = await supabase_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    return jobs[0] if jobs else None


async def save_job(job_data: dict) -> bool:
    """Save or update a job"""
    result = await supabase_request("POST", "jobs", data=job_data)
    return result is not None


async def save_application(job_id: str, status: str, cover_letter: str = None, gmail_draft_id: str = None) -> int:
    """Save application"""
    data = {
        "job_id": job_id,
        "status": status,
        "cover_letter": cover_letter,
        "gmail_draft_id": gmail_draft_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    result = await supabase_request("POST", "applications", data=data)
    return result[0]["id"] if result else None


async def get_stats() -> Dict[str, int]:
    """Get statistics"""
    jobs = await supabase_request("GET", "jobs", params={"link_status": "eq.active", "select": "id"})
    applications = await supabase_request("GET", "applications", params={"select": "id,status,job_id"})

    total_jobs = len(jobs) if jobs else 0
    total_apps = len(applications) if applications else 0
    sent_apps = len([a for a in (applications or []) if a.get("status") == "sent"])
    interviews = len([a for a in (applications or []) if a.get("status") == "interview"])
    applied_ids = {a["job_id"] for a in (applications or [])}
    pending = total_jobs - len(applied_ids)

    return {
        "total_jobs": total_jobs,
        "pending_jobs": pending,
        "total_applications": total_apps,
        "sent_applications": sent_apps,
        "interviews": interviews,
        "deadline_today": 0  # TODO: implement
    }


# === COVER LETTER GENERATION ===

def detect_job_category(title: str, description: str) -> str:
    """Detect job category"""
    text = f"{title} {description}".lower()

    categories = {
        "contentmoderation": ["content moderation", "moderator", "innehållsmoderator", "trust & safety"],
        "restaurant": ["servitör", "servitris", "restaurang", "kock", "café", "barista"],
        "retail": ["butik", "kassa", "försäljare", "ica", "coop"],
        "industry": ["industri", "lager", "trädgård", "städ"],
        "healthcare": ["vård", "omsorg", "äldreboende", "hemtjänst"],
        "tech": ["it", "tech", "data", "analyst"],
        "customerservice": ["kundtjänst", "customer service", "support"],
    }

    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category
    return "general"


def get_relevant_experience(category: str) -> str:
    """Get relevant experience for category"""
    experiences = {
        "restaurant": """- Restaurangbiträde på Max Hamburgare (Apr-Aug 2024): Drive-in, fritös, kök, servering, kassa, städ
- Försäljare/Barista på House of Beans (Aug 2024-Feb 2025): Sålde te, kaffe, choklad
- Cafépersonal på Coffeehouse by George (2014-2015): Kassahantering, barista""",

        "retail": """- Försäljare på House of Beans (Aug 2024-Feb 2025): Direktförsäljning, ensam i butik
- Kassapersonal på ICA Maxi (2015, 2017, 2019): Kassa, självscanning, frukt/grönt""",

        "customerservice": """- Innehållsmoderator på Clubhouse (Jun 2021-Jan 2022): Trust & Safety, customer support
- Innehållsanalytiker på Google Ads (Maj 2018-Apr 2019): 100+ annonser/dag
- Global Marketing på Minerva Project (Sep 2019-Apr 2020): Kundservice via Intercom""",

        "healthcare": """- Timvikarie på Kvarngården äldreboende (Maj-Sep 2020): Omvårdnad, medicinhantering""",
    }
    return experiences.get(category, experiences["restaurant"])


async def generate_cover_letter(job: Dict) -> str:
    """Generate cover letter using Claude API"""
    if not ANTHROPIC_API_KEY:
        return _template_letter(job)

    category = detect_job_category(job.get("title", ""), job.get("description", ""))
    relevant_exp = get_relevant_experience(category)

    prompt = f"""Skriv ett PERSONLIGT BREV på svenska (ca 150-200 ord).

===MIN RELEVANTA ERFARENHET===
{relevant_exp}

===ÖVRIG INFO OM MIG===
- Linnea Moritz, 28 år, bor i Sollentuna
- B-körkort, flexibel med arbetstider
- Telefon: 0761166109
- Svenska (modersmål), Engelska (flytande)

===JOBBET===
Titel: {job.get('title', 'Okänd')}
Företag: {job.get('company', 'Okänt')}
Plats: {job.get('location', '')}
Beskrivning: {job.get('description', '')[:1500]}

===REGLER===
1. Skriv 150-200 ord på naturlig svenska
2. Lyft fram 2-3 konkreta erfarenheter som matchar jobbet
3. Nämn Sollentuna + B-körkort + flexibel med tider
4. Avsluta: "Med vänlig hälsning, Linnea Moritz" + telefon + "linneamoritzCV@gmail.com"
5. NÄMN ALDRIG konst, målning eller Shopify

Skriv ENDAST brevet."""

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
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["content"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Error generating letter: {e}")

    return _template_letter(job)


def _template_letter(job: Dict) -> str:
    """Fallback template letter"""
    return f"""Hej!

Jag söker tjänsten som {job.get('title', 'tjänsten')} hos {job.get('company', 'er')}.

Jag har bred erfarenhet från service och kundkontakt. Jag bor i Sollentuna, har B-körkort och är flexibel med arbetstider.

Jag ser fram emot att höra från er.

Med vänlig hälsning,
Linnea Moritz
0761166109
linneamoritzCV@gmail.com"""


# === JOB SCRAPING ===

async def scrape_platsbanken(keyword: str) -> List[Dict]:
    """Scrape jobs from Platsbanken API"""
    jobs = []

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search",
                headers={"Content-Type": "application/json"},
                json={
                    "filters": [{"type": "freetext", "value": keyword}],
                    "fromDate": None,
                    "order": "relevance",
                    "maxRecords": 50,
                    "startIndex": 0,
                    "source": "pb"
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                for hit in data.get("ads", []):
                    deadline = hit.get("lastApplicationDate")

                    # Classify priority
                    priority = "strategisk"
                    if deadline:
                        try:
                            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                            days_left = (deadline_date - datetime.now(deadline_date.tzinfo)).days
                            if days_left <= 3:
                                priority = "akut"
                        except:
                            pass

                    job = {
                        "id": str(hit.get("id")),
                        "title": hit.get("title", "Okänd"),
                        "company": hit.get("workplaceName", "Okänt"),
                        "location": hit.get("workplace", "Sverige"),
                        "description": (hit.get("description", "") or "")[:2000],
                        "url": f"https://arbetsformedlingen.se/platsbanken/annonser/{hit.get('id')}",
                        "source": "platsbanken",
                        "priority": priority,
                        "deadline": deadline,
                        "contact_email": None,
                        "contact_name": None,
                        "why_perfect": None,
                        "created_at": datetime.now().isoformat(),
                        "link_status": "active"
                    }
                    jobs.append(job)

    except Exception as e:
        logger.error(f"Error scraping: {e}")

    return jobs


# === API ENDPOINTS ===

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "anti-apathy-portal", "version": "2.0.0"}


@app.get("/api/jobs/next")
async def api_get_next_job():
    """Get next job to review"""
    job = await get_next_job()

    if job:
        return {"success": True, "job": job}

    return {
        "success": True,
        "job": None,
        "message": "Inga fler jobb just nu. Kör scraping för att hämta nya!"
    }


@app.get("/api/jobs")
async def api_get_all_jobs(limit: int = 50):
    """List all jobs"""
    jobs = await supabase_request(
        "GET",
        "jobs",
        params={"order": "created_at.desc", "limit": str(limit)}
    )

    return {
        "success": True,
        "count": len(jobs) if jobs else 0,
        "jobs": jobs or []
    }


@app.get("/api/jobs/{job_id}")
async def api_get_job(job_id: str):
    """Get specific job"""
    job = await get_job_by_id(job_id)

    if job:
        return {"success": True, "job": job}

    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs/{job_id}/generate-letter")
async def api_generate_letter(job_id: str):
    """Generate cover letter for a job"""
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    letter = await generate_cover_letter(job)

    return {
        "success": True,
        "job_id": job_id,
        "cover_letter": letter,
        "company": job.get("company"),
        "title": job.get("title")
    }


@app.post("/api/jobs/{job_id}/apply")
async def api_apply_to_job(job_id: str, request: ApplyRequest):
    """Save application"""
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    app_id = await save_application(
        job_id=job_id,
        status="draft_saved" if request.gmail_draft_id else "letter_generated",
        cover_letter=request.cover_letter,
        gmail_draft_id=request.gmail_draft_id
    )

    return {
        "success": True,
        "application_id": app_id,
        "message": "Ansökan sparad!"
    }


@app.post("/api/jobs/{job_id}/skip")
async def api_skip_job(job_id: str, request: SkipRequest = None):
    """Skip a job"""
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await save_application(job_id, "skipped")

    return {"success": True, "message": "Jobb överhoppat"}


@app.post("/api/scrape/sync")
async def api_scrape_sync():
    """Run scraping synchronously"""
    keywords = ["servitör", "kundtjänst", "café", "barista", "butik"]
    total = 0

    for keyword in keywords:
        jobs = await scrape_platsbanken(keyword)
        for job in jobs:
            if await save_job(job):
                total += 1

    return {
        "success": True,
        "jobs_scraped": total,
        "message": f"Scraping klar! {total} jobb hittade."
    }


@app.get("/api/stats")
async def api_get_stats():
    """Get dashboard statistics"""
    stats = await get_stats()
    return {"success": True, "stats": stats}


@app.get("/api/applications")
async def api_get_applications():
    """List all applications"""
    applications = await supabase_request(
        "GET",
        "applications",
        params={"order": "created_at.desc"}
    )

    return {
        "success": True,
        "count": len(applications) if applications else 0,
        "applications": applications or []
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


# Serve frontend
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect, useCallback } = React;
        const API_URL = '';

        const StatsDashboard = ({ stats }) => (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                    <div className="text-4xl font-bold text-purple-600">{stats.pending_jobs || 0}</div>
                    <div className="text-gray-600 text-sm font-semibold uppercase">Vantande jobb</div>
                </div>
                <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                    <div className="text-4xl font-bold text-green-600">{stats.sent_applications || 0}</div>
                    <div className="text-gray-600 text-sm font-semibold uppercase">Skickade</div>
                </div>
                <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                    <div className="text-4xl font-bold text-blue-600">{stats.interviews || 0}</div>
                    <div className="text-gray-600 text-sm font-semibold uppercase">Intervjuer</div>
                </div>
                <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                    <div className="text-4xl font-bold text-red-600">{stats.deadline_today || 0}</div>
                    <div className="text-gray-600 text-sm font-semibold uppercase">Deadline idag</div>
                </div>
            </div>
        );

        const JobCard = ({ job, onGenerateLetter, onSkip, loading }) => {
            if (!job) return null;
            return (
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
                    <div className="gradient-bg p-6 text-white">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${job.priority === 'akut' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                            {job.priority === 'akut' ? 'AKUT' : 'Strategisk'}
                        </span>
                        <h2 className="text-3xl font-bold mt-4 mb-2">{job.title}</h2>
                        <p className="text-xl opacity-95">{job.company}</p>
                        <p className="opacity-85">{job.location}</p>
                    </div>
                    <div className="p-6">
                        <div className="text-gray-600 mb-6 max-h-40 overflow-y-auto">
                            {job.description?.slice(0, 500)}{job.description?.length > 500 && '...'}
                        </div>
                        {job.url && <a href={job.url} target="_blank" className="text-purple-600 hover:text-purple-800 text-sm mb-4 block">Se annons</a>}
                        <div className="flex gap-3">
                            <button onClick={onGenerateLetter} disabled={loading} className="flex-1 bg-purple-600 text-white py-3 px-6 rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50">
                                {loading ? 'Genererar...' : 'Generera Brev'}
                            </button>
                            <button onClick={onSkip} className="px-6 py-3 border-2 border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50">Skippa</button>
                        </div>
                    </div>
                </div>
            );
        };

        const CoverLetterModal = ({ isOpen, letter, job, onClose, onSave, saving }) => {
            const [editedLetter, setEditedLetter] = useState(letter);
            useEffect(() => { setEditedLetter(letter); }, [letter]);
            if (!isOpen) return null;
            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                        <div className="gradient-bg p-6 text-white">
                            <h3 className="text-2xl font-bold">Personligt Brev</h3>
                            <p className="opacity-90">{job?.title} @ {job?.company}</p>
                        </div>
                        <div className="p-6">
                            <textarea value={editedLetter} onChange={(e) => setEditedLetter(e.target.value)} className="w-full h-48 p-4 border rounded-lg" />
                            <div className="flex gap-3 mt-4">
                                <button onClick={() => onSave(editedLetter)} disabled={saving} className="flex-1 bg-green-600 text-white py-3 px-6 rounded-xl font-medium hover:bg-green-700 disabled:opacity-50">
                                    {saving ? 'Sparar...' : 'Spara'}
                                </button>
                                <button onClick={onClose} className="px-6 py-3 border-2 border-gray-200 rounded-xl">Avbryt</button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        const App = () => {
            const [currentJob, setCurrentJob] = useState(null);
            const [stats, setStats] = useState({});
            const [coverLetter, setCoverLetter] = useState('');
            const [showModal, setShowModal] = useState(false);
            const [loading, setLoading] = useState(false);
            const [saving, setSaving] = useState(false);
            const [scraping, setScraping] = useState(false);
            const [error, setError] = useState(null);
            const [connected, setConnected] = useState(false);

            const fetchStats = useCallback(async () => {
                try {
                    const res = await fetch(`${API_URL}/api/stats`);
                    if (res.ok) { const data = await res.json(); setStats(data.stats); setConnected(true); }
                } catch (err) { setConnected(false); }
            }, []);

            const fetchNextJob = useCallback(async () => {
                try {
                    const res = await fetch(`${API_URL}/api/jobs/next`);
                    if (res.ok) { const data = await res.json(); setCurrentJob(data.job); setConnected(true); }
                } catch (err) { setConnected(false); setError('Kunde inte ansluta.'); }
            }, []);

            const handleGenerateLetter = async () => {
                if (!currentJob) return;
                setLoading(true);
                try {
                    const res = await fetch(`${API_URL}/api/jobs/${currentJob.id}/generate-letter`, { method: 'POST' });
                    if (res.ok) { const data = await res.json(); setCoverLetter(data.cover_letter); setShowModal(true); }
                } catch (err) { setError('Fel vid generering'); }
                setLoading(false);
            };

            const handleSaveApplication = async (letter) => {
                if (!currentJob) return;
                setSaving(true);
                try {
                    const res = await fetch(`${API_URL}/api/jobs/${currentJob.id}/apply`, {
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ cover_letter: letter })
                    });
                    if (res.ok) { setShowModal(false); setCoverLetter(''); fetchNextJob(); fetchStats(); }
                } catch (err) { setError('Kunde inte spara'); }
                setSaving(false);
            };

            const handleSkip = async () => {
                if (!currentJob) return;
                await fetch(`${API_URL}/api/jobs/${currentJob.id}/skip`, { method: 'POST' });
                fetchNextJob(); fetchStats();
            };

            const handleScrape = async () => {
                setScraping(true);
                try {
                    const res = await fetch(`${API_URL}/api/scrape/sync`, { method: 'POST' });
                    if (res.ok) { fetchNextJob(); fetchStats(); }
                } catch (err) { setError('Kunde inte scrapa'); }
                setScraping(false);
            };

            useEffect(() => { fetchStats(); fetchNextJob(); }, [fetchStats, fetchNextJob]);

            return (
                <div className="min-h-screen bg-gray-50">
                    <header className="gradient-bg text-white py-8 px-4">
                        <div className="max-w-4xl mx-auto flex items-center justify-between">
                            <div>
                                <h1 className="text-4xl font-bold">Anti-Apathy Portal</h1>
                                <p className="opacity-90 mt-2">En uppgift i taget. Du klarar detta!</p>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                                <span className="text-sm opacity-80">{connected ? 'Ansluten' : 'Ej ansluten'}</span>
                            </div>
                        </div>
                    </header>
                    <main className="max-w-4xl mx-auto px-4 py-8">
                        {error && <div className="bg-red-100 text-red-700 px-4 py-3 rounded-lg mb-6 flex justify-between"><span>{error}</span><button onClick={() => setError(null)}>X</button></div>}
                        <StatsDashboard stats={stats} />
                        {currentJob ? (
                            <JobCard job={currentJob} onGenerateLetter={handleGenerateLetter} onSkip={handleSkip} loading={loading} />
                        ) : (
                            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                                <h2 className="text-3xl font-bold text-gray-800 mb-3">Inga fler jobb just nu</h2>
                                <button onClick={handleScrape} disabled={scraping} className="bg-purple-600 text-white py-3 px-8 rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50">
                                    {scraping ? 'Scrapar...' : 'Scrapa Nya Jobb'}
                                </button>
                            </div>
                        )}
                        <div className="mt-8 flex justify-center">
                            <button onClick={handleScrape} disabled={scraping} className="text-purple-600 hover:text-purple-800 font-medium">
                                {scraping ? 'Scrapar...' : 'Scrapa fler jobb'}
                            </button>
                        </div>
                    </main>
                    <CoverLetterModal isOpen={showModal} letter={coverLetter} job={currentJob} onClose={() => setShowModal(false)} onSave={handleSaveApplication} saving={saving} />
                </div>
            );
        };
        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>'''


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend"""
    return FRONTEND_HTML
