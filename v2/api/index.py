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
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # For client-side auth
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Gmail API scopes (for user's own Google Cloud credentials)
GMAIL_SCOPES = "https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.modify"

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
    cv_id: Optional[str] = None
    status: str = "draft"


# ============== AUTH MODELS ==============

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    email: str


class UpdatePasswordRequest(BaseModel):
    new_password: str


# ============== STRUCTURED CV MODELS ==============

class UserProfile(BaseModel):
    """User's personal info"""
    full_name: str
    email: str
    phone: str
    location: str
    photo_url: Optional[str] = None
    drivers_license: bool = False
    languages: List[str] = ["Svenska (Modersmål)", "Engelska (flytande)"]
    certificates: List[str] = []


class EducationEntry(BaseModel):
    """Education entry"""
    school: str
    location: str
    degree: str
    dates: str
    bullets: List[str] = []
    sort_order: int = 0


class ExperienceEntry(BaseModel):
    """Work experience entry with category tags"""
    company: str
    location: str
    title: str
    dates: str
    bullets: List[str] = []
    categories: List[str] = []  # ['restaurant', 'tech', 'retail', etc.]
    sort_order: int = 0


class VolunteerEntry(BaseModel):
    """Volunteer work entry"""
    organization: str
    dates: str
    bullets: List[str] = []
    sort_order: int = 0


class SkillEntry(BaseModel):
    """Skill entry with category"""
    category: str  # 'tech', 'restaurant', 'all'
    skill_type: str  # 'technical', 'certificate', 'language'
    skill_text: str


class MasterCV(BaseModel):
    """Complete Master CV with all data"""
    profile: UserProfile
    education: List[EducationEntry] = []
    experiences: List[ExperienceEntry] = []
    volunteer: List[VolunteerEntry] = []
    awards: List[str] = []
    skills: List[SkillEntry] = []


class GenerateCVBranscherRequest(BaseModel):
    """Request to generate multiple CV versions for different branscher"""
    user_id: Optional[str] = None


# ============== GMAIL API MODELS ==============

class GoogleCredentialsRequest(BaseModel):
    """User's own Google Cloud credentials"""
    google_client_id: str
    google_client_secret: str


class CreateGmailDraftRequest(BaseModel):
    """Request to create a Gmail draft"""
    to_email: str
    subject: str
    body: str
    job_id: Optional[str] = None


# CV Categories/Branscher (will be loaded from database per user)
# This is a fallback for users without custom branscher
CV_BRANSCHER = [
    {"id": "restaurant", "name": "Restaurang & Café", "emoji": "🍽️",
     "focus": "servering, kundkontakt, stresshantering, teamwork, hygien",
     "keywords": ["servitör", "restaurang", "café", "barista", "kök", "mat"]},
    {"id": "retail", "name": "Butik & Kassa", "emoji": "🛒",
     "focus": "försäljning, kassahantering, kundservice, lagerhantering",
     "keywords": ["butik", "kassa", "försäljare", "säljare", "handel"]},
    {"id": "customerservice", "name": "Kundtjänst & Support", "emoji": "💬",
     "focus": "problemlösning, kommunikation, CRM-system, tålamod",
     "keywords": ["kundtjänst", "support", "customer service", "telefon"]},
    {"id": "tech", "name": "Tech & Kontor", "emoji": "💻",
     "focus": "programmering, teknisk kompetens, analytiskt tänkande, dataanalys",
     "keywords": ["it", "tech", "utvecklare", "data", "analyst", "kontor"]},
    {"id": "healthcare", "name": "Vård & Omsorg", "emoji": "🏥",
     "focus": "omvårdnad, empati, medicinhantering, dokumentation",
     "keywords": ["vård", "omsorg", "sjuksköterska", "äldreboende"]},
    {"id": "industry", "name": "Trädgård & Industri", "emoji": "🌱",
     "focus": "fysiskt arbete, utomhusarbete, maskiner, självständighet",
     "keywords": ["trädgård", "industri", "lager", "städ", "bygg"]},
    {"id": "hotel", "name": "Hotell & Reception", "emoji": "🏨",
     "focus": "gästservice, bokningssystem, incheckning, serviceinriktad",
     "keywords": ["hotell", "reception", "gäst", "bokning", "concierge"]},
    {"id": "content", "name": "Content & Moderation", "emoji": "📱",
     "focus": "innehållsgranskning, trust & safety, riktlinjer, datahantering",
     "keywords": ["content", "moderat", "trust", "safety", "granskning"]},
]


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


# ============== CV GENERATION ==============

async def generate_cv_vibe(master_cv: Dict, vibe: Dict) -> str:
    """Generate a CV version optimized for a specific job category"""

    if not ANTHROPIC_API_KEY:
        return f"[CV för {vibe['name']} - API ej konfigurerad]"

    prompt = f"""Skriv ett CV på svenska optimerat för {vibe['name']}-jobb.

PERSONINFO:
- Namn: {master_cv.get('full_name')}
- E-post: {master_cv.get('email')}
- Telefon: {master_cv.get('phone')}
- Plats: {master_cv.get('location')}
- Språk: {', '.join(master_cv.get('languages', ['Svenska']))}
- Körkort: {'Ja, B-körkort' if master_cv.get('drivers_license') else 'Nej'}

ERFARENHET:
{master_cv.get('experience', '')}

UTBILDNING:
{master_cv.get('education', 'Ej angivet')}

FÄRDIGHETER:
{master_cv.get('skills', 'Ej angivet')}

OM MIG:
{master_cv.get('about_me', '')}

FOKUSOMRÅDEN FÖR DENNA CV-VERSION:
{vibe['focus']}

INSTRUKTIONER:
1. Skriv ett professionellt CV på svenska
2. Lyft fram erfarenheter som är relevanta för {vibe['name']}-jobb
3. Fokusera på: {vibe['focus']}
4. Använd konkreta exempel och siffror där möjligt
5. Håll det till 1 sida (ca 300-400 ord)
6. Formatera snyggt med tydliga sektioner:
   - Kontaktinfo (namn, tel, email, plats)
   - Profil (2-3 meningar)
   - Erfarenhet (relevanta jobb)
   - Utbildning
   - Färdigheter

Skriv ENDAST CV-texten, inget annat."""

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
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"].strip()
            else:
                logger.error(f"Claude API error: {response.status_code}")

    except Exception as e:
        logger.error(f"Error generating CV: {e}")

    return f"[Kunde inte generera CV för {vibe['name']}]"


async def generate_all_cv_vibes(master_cv: Dict, user_id: str) -> List[Dict]:
    """Generate all CV versions for a user"""
    generated_cvs = []

    for vibe in CV_BRANSCHER:
        logger.info(f"Generating CV vibe: {vibe['name']}...")
        cv_text = await generate_cv_vibe(master_cv, vibe)

        cv_data = {
            "user_id": user_id,
            "vibe_id": vibe["id"],
            "vibe_name": vibe["name"],
            "vibe_emoji": vibe["emoji"],
            "cv_text": cv_text,
            "created_at": datetime.now().isoformat()
        }

        # Save to database
        saved = await db_request("POST", "user_cvs", data=cv_data)
        if saved:
            generated_cvs.append(saved[0])
        else:
            generated_cvs.append(cv_data)

    return generated_cvs


def match_job_to_cv_vibe(job_title: str, job_description: str) -> str:
    """Match a job to the best CV vibe"""
    text = f"{job_title} {job_description}".lower()

    # Keywords for each vibe
    vibe_keywords = {
        "restaurant": ["servitör", "servitris", "restaurang", "kock", "café", "barista", "kök", "mat", "dryck"],
        "retail": ["butik", "kassa", "försäljare", "säljare", "retail", "lager", "handel"],
        "customerservice": ["kundtjänst", "customer service", "support", "kundservice", "telefon", "chat"],
        "tech": ["it", "tech", "utvecklare", "developer", "webbutvecklare", "frontend", "backend", "data", "programmering"],
        "healthcare": ["vård", "omsorg", "sjuksköterska", "äldreboende", "hemtjänst", "medicin"],
        "garden": ["trädgård", "industri", "lager", "städ", "fysiskt", "utomhus", "bygg"],
    }

    # Count keyword matches
    scores = {}
    for vibe_id, keywords in vibe_keywords.items():
        scores[vibe_id] = sum(1 for kw in keywords if kw in text)

    # Return best match, or "customerservice" as default
    best_vibe = max(scores, key=scores.get) if max(scores.values()) > 0 else "customerservice"
    return best_vibe


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


# ============== CV ENDPOINTS ==============

@app.get("/api/cv/vibes")
async def list_cv_vibes():
    """List all available CV vibes/categories"""
    return {"success": True, "vibes": CV_BRANSCHER}


@app.post("/api/cv/master")
async def save_master_cv(master_cv: MasterCV, user_id: str = "default_user"):
    """
    Save complete Master CV with all structured data.
    This is the source of truth - all CV vibes are generated from this.
    """
    # Save profile
    profile_data = {
        "user_id": user_id,
        "full_name": master_cv.profile.full_name,
        "email": master_cv.profile.email,
        "phone": master_cv.profile.phone,
        "location": master_cv.profile.location,
        "photo_url": master_cv.profile.photo_url,
        "drivers_license": master_cv.profile.drivers_license,
        "languages": master_cv.profile.languages,
        "certificates": master_cv.profile.certificates,
        "updated_at": datetime.now().isoformat()
    }
    await db_request("POST", "user_profiles", data=profile_data)

    # Save education entries
    for i, edu in enumerate(master_cv.education):
        edu_data = {
            "user_id": user_id,
            "school": edu.school,
            "location": edu.location,
            "degree": edu.degree,
            "dates": edu.dates,
            "bullets": edu.bullets,
            "sort_order": i
        }
        await db_request("POST", "user_education", data=edu_data)

    # Save experience entries with category tags
    for i, exp in enumerate(master_cv.experiences):
        exp_data = {
            "user_id": user_id,
            "company": exp.company,
            "location": exp.location,
            "title": exp.title,
            "dates": exp.dates,
            "bullets": exp.bullets,
            "categories": exp.categories,
            "sort_order": i
        }
        await db_request("POST", "user_experiences", data=exp_data)

    # Save volunteer entries
    for i, vol in enumerate(master_cv.volunteer):
        vol_data = {
            "user_id": user_id,
            "organization": vol.organization,
            "dates": vol.dates,
            "bullets": vol.bullets,
            "sort_order": i
        }
        await db_request("POST", "user_volunteer", data=vol_data)

    # Save awards
    for i, award in enumerate(master_cv.awards):
        award_data = {
            "user_id": user_id,
            "award_text": award,
            "sort_order": i
        }
        await db_request("POST", "user_awards", data=award_data)

    # Save skills
    for skill in master_cv.skills:
        skill_data = {
            "user_id": user_id,
            "category": skill.category,
            "skill_type": skill.skill_type,
            "skill_text": skill.skill_text
        }
        await db_request("POST", "user_skills", data=skill_data)

    return {
        "success": True,
        "message": "Master CV sparad!",
        "summary": {
            "education": len(master_cv.education),
            "experiences": len(master_cv.experiences),
            "volunteer": len(master_cv.volunteer),
            "awards": len(master_cv.awards),
            "skills": len(master_cv.skills)
        }
    }


@app.get("/api/cv/master")
async def get_master_cv(user_id: str = "default_user"):
    """Get user's complete Master CV as structured data"""

    # Get profile
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    profile = profiles[0] if profiles else None

    if not profile:
        return {"success": True, "master_cv": None, "message": "Ingen CV uppladdad ännu"}

    # Get all data
    education = await db_request("GET", "user_education", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    volunteer = await db_request("GET", "user_volunteer", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    awards = await db_request("GET", "user_awards", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    skills = await db_request("GET", "user_skills", params={
        "user_id": f"eq.{user_id}"
    }) or []

    return {
        "success": True,
        "master_cv": {
            "profile": profile,
            "education": education,
            "experiences": experiences,
            "volunteer": volunteer,
            "awards": [a.get("award_text") for a in awards],
            "skills": skills
        }
    }


@app.get("/api/cv/export/{vibe_id}")
async def export_cv_for_vibe(vibe_id: str, user_id: str = "default_user"):
    """
    Export CV data filtered for a specific vibe.
    Returns structured data ready for PDF template.
    """
    # Get master CV
    master_cv_response = await get_master_cv(user_id)
    if not master_cv_response.get("master_cv"):
        raise HTTPException(status_code=404, detail="No Master CV found")

    master = master_cv_response["master_cv"]
    profile = master["profile"]

    # Filter experiences by vibe category
    all_experiences = master.get("experiences", [])
    filtered_experiences = [
        exp for exp in all_experiences
        if vibe_id in exp.get("categories", [])
    ]

    # Get skills for this vibe (and 'all' skills)
    all_skills = master.get("skills", [])
    vibe_skills = [s for s in all_skills if s.get("category") in [vibe_id, "all"]]

    # Build technical skills string if tech vibe
    technical_skills = None
    if vibe_id in ["tech", "content"]:
        tech_skill_texts = [s.get("skill_text") for s in vibe_skills if s.get("skill_type") == "technical"]
        if tech_skill_texts:
            technical_skills = ", ".join(tech_skill_texts)

    # Get vibe info
    vibe_info = next((v for v in CV_BRANSCHER if v["id"] == vibe_id), None)

    return {
        "success": True,
        "vibe": vibe_info,
        "cv_data": {
            "full_name": profile.get("full_name"),
            "email": profile.get("email"),
            "phone": profile.get("phone"),
            "location": profile.get("location"),
            "photo_url": profile.get("photo_url"),
            "drivers_license": profile.get("drivers_license"),
            "languages": ", ".join(profile.get("languages", [])),
            "certificates": ", ".join(profile.get("certificates", [])),
            "technical_skills": technical_skills,
            "education": master.get("education", []),
            "experience": filtered_experiences,
            "volunteer": master.get("volunteer", []),
            "awards": master.get("awards", [])
        }
    }


@app.post("/api/cv/suggest-vibe")
async def suggest_new_vibe(job_keywords: List[str], user_id: str = "default_user"):
    """
    Analyze job search keywords and suggest if user should create a new CV vibe.
    Returns suggestion if pattern detected and user doesn't have that vibe.
    """
    # Count keyword matches per vibe
    vibe_scores = {}
    for vibe in CV_BRANSCHER:
        score = 0
        for keyword in job_keywords:
            if any(vk in keyword.lower() for vk in vibe.get("keywords", [])):
                score += 1
        if score > 0:
            vibe_scores[vibe["id"]] = score

    if not vibe_scores:
        return {"success": True, "suggestion": None}

    # Find top vibe
    top_vibe_id = max(vibe_scores, key=vibe_scores.get)
    top_score = vibe_scores[top_vibe_id]

    # Only suggest if significant pattern (3+ matches)
    if top_score < 3:
        return {"success": True, "suggestion": None}

    # Check if user has experiences tagged for this vibe
    experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}",
        "categories": f"cs.{{{top_vibe_id}}}"  # contains
    })

    has_vibe_cv = bool(experiences)

    if has_vibe_cv:
        return {"success": True, "suggestion": None, "message": f"Du har redan ett {top_vibe_id}-CV!"}

    # Get vibe info
    vibe_info = next((v for v in CV_BRANSCHER if v["id"] == top_vibe_id), None)

    return {
        "success": True,
        "suggestion": {
            "vibe_id": top_vibe_id,
            "vibe_name": vibe_info["name"],
            "vibe_emoji": vibe_info["emoji"],
            "match_count": top_score,
            "message": f"Hej! Jag ser att du söker många jobb inom {vibe_info['name'].lower()}. Vill du skapa ett CV anpassat för den branschen?"
        }
    }


@app.post("/api/cv/generate-branscher")
async def generate_cv_branscher(request: GenerateCVBranscherRequest = None):
    """Generate all CV bransch versions from master CV"""
    user_id = request.user_id if request and request.user_id else "default_user"

    # Get master CV
    cvs = await db_request("GET", "master_cvs", params={
        "user_id": f"eq.{user_id}",
        "order": "created_at.desc",
        "limit": "1"
    })

    if not cvs:
        raise HTTPException(status_code=404, detail="Ladda upp din CV först!")

    master_cv = cvs[0]

    # Generate all vibes
    generated = await generate_all_cv_vibes(master_cv, user_id)

    return {
        "success": True,
        "message": f"Genererade {len(generated)} CV-versioner!",
        "cvs": generated
    }


@app.get("/api/cv/all")
async def get_user_cvs(user_id: str = "default_user"):
    """Get all user's generated CV versions"""
    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "order": "vibe_id.asc"
    })

    return {"success": True, "cvs": cvs or []}


@app.get("/api/cv/{vibe_id}")
async def get_cv_by_vibe(vibe_id: str, user_id: str = "default_user"):
    """Get a specific CV version"""
    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "vibe_id": f"eq.{vibe_id}"
    })

    if cvs and len(cvs) > 0:
        return {"success": True, "cv": cvs[0]}

    raise HTTPException(status_code=404, detail=f"Ingen CV för {vibe_id}")


@app.patch("/api/cv/{vibe_id}")
async def update_cv(vibe_id: str, cv_text: str, user_id: str = "default_user"):
    """Update a CV version (after user edits)"""
    result = await db_request("PATCH", "user_cvs",
        data={"cv_text": cv_text, "updated_at": datetime.now().isoformat()},
        params={"user_id": f"eq.{user_id}", "vibe_id": f"eq.{vibe_id}"}
    )

    if result:
        return {"success": True, "cv": result[0]}

    raise HTTPException(status_code=500, detail="Kunde inte uppdatera CV")


@app.post("/api/jobs/{job_id}/apply-with-cv")
async def apply_with_cv(job_id: str, user_id: str = "default_user"):
    """
    Smart apply: Auto-selects best CV, generates cover letter, returns both.
    This is the main "one-click apply" endpoint.
    """
    # Get job
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[0]

    # Match job to best CV vibe
    best_vibe = match_job_to_cv_vibe(job.get("title", ""), job.get("description", ""))
    logger.info(f"Job '{job.get('title')}' matched to CV vibe: {best_vibe}")

    # Get the matching CV
    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "vibe_id": f"eq.{best_vibe}"
    })

    cv = cvs[0] if cvs else None

    # Generate cover letter using the CV
    cv_text_for_letter = cv.get("cv_text") if cv else None
    cover_letter = await generate_cover_letter(job, cv_text_for_letter)

    return {
        "success": True,
        "job": {
            "id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "contact_email": job.get("contact_email"),
            "contact_name": job.get("contact_name")
        },
        "matched_vibe": best_vibe,
        "cv": cv,
        "cover_letter": cover_letter,
        "gmail_link": _create_gmail_link(job, cover_letter)
    }


def _create_gmail_link(job: Dict, letter: str) -> str:
    """Create Gmail compose link"""
    import urllib.parse
    to = job.get("contact_email", "")
    subject = urllib.parse.quote(f"Ansökan: {job.get('title', 'Tjänst')}")
    body = urllib.parse.quote(letter)
    return f"https://mail.google.com/mail/?view=cm&fs=1&to={to}&su={subject}&body={body}"


# ============== FRONTEND ==============

import pathlib

def get_setup_guide_html():
    """Load Gmail setup guide HTML"""
    try:
        guide_path = pathlib.Path(__file__).parent.parent / "setup-guide.html"
        if guide_path.exists():
            return guide_path.read_text(encoding='utf-8')
    except:
        pass
    return "<h1>Setup guide not found</h1>"


def get_login_html():
    """Load login page HTML"""
    try:
        login_path = pathlib.Path(__file__).parent.parent / "login.html"
        if login_path.exists():
            return login_path.read_text(encoding='utf-8')
    except:
        pass
    return "<h1>Login page not found</h1>"


def get_frontend_html():
    """Load frontend HTML from file or use embedded version"""
    try:
        frontend_path = pathlib.Path(__file__).parent.parent / "frontend.html"
        if frontend_path.exists():
            return frontend_path.read_text(encoding='utf-8')
    except:
        pass

    # Fallback: minimal embedded version
    return '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anti-Apathy Job Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen flex items-center justify-center">
    <div class="text-center p-8">
        <h1 class="text-3xl font-bold text-indigo-600 mb-4">Anti-Apathy Job Portal</h1>
        <p class="text-slate-600 mb-4">API is running!</p>
        <p class="text-sm text-slate-400">Frontend file not found. Check /v2/frontend.html</p>
        <div class="mt-6 space-x-4">
            <a href="/api/health" class="text-indigo-600 hover:underline">Health Check</a>
            <a href="/docs" class="text-indigo-600 hover:underline">API Docs</a>
        </div>
    </div>
</body>
</html>'''


# ============== AUTH ENDPOINTS ==============

@app.post("/api/auth/signup")
async def sign_up(request: SignUpRequest):
    """
    Create a new user account with email and password.
    Supabase will send a confirmation email automatically.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": request.email,
                "password": request.password,
                "data": {"full_name": request.full_name} if request.full_name else {}
            }
        )

        if response.status_code not in [200, 201]:
            error = response.json()
            raise HTTPException(status_code=400, detail=error.get("msg", "Kunde inte skapa konto"))

        data = response.json()
        return {
            "success": True,
            "message": "Konto skapat! Kolla din e-post för att bekräfta.",
            "user_id": data.get("user", {}).get("id")
        }


class ResendVerificationRequest(BaseModel):
    email: str


@app.post("/api/auth/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """
    Resend email verification link.
    Uses Supabase's resend endpoint.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/resend",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "type": "signup",
                "email": request.email
            }
        )

        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "Om e-postadressen finns skickas en ny verifieringslänk."
        }


@app.post("/api/auth/signin")
async def sign_in(request: SignInRequest):
    """
    Sign in with email and password.
    Returns access token and user info.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": request.email,
                "password": request.password
            }
        )

        if response.status_code != 200:
            error = response.json()
            raise HTTPException(status_code=401, detail=error.get("error_description", "Fel e-post eller lösenord"))

        data = response.json()
        return {
            "success": True,
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "user": {
                "id": data.get("user", {}).get("id"),
                "email": data.get("user", {}).get("email"),
                "full_name": data.get("user", {}).get("user_metadata", {}).get("full_name")
            }
        }


@app.post("/api/auth/signout")
async def sign_out(request: Request):
    """Sign out the current user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"success": True, "message": "Utloggad"}

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/auth/v1/logout",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}"
            }
        )

    return {"success": True, "message": "Utloggad"}


@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Send password reset email.
    Supabase handles the email automatically.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/recover",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={"email": request.email}
        )

        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "Om e-postadressen finns skickas en återställningslänk."
        }


@app.post("/api/auth/update-password")
async def update_password(request: UpdatePasswordRequest, req: Request):
    """
    Update password after reset.
    Requires valid access token from reset link.
    """
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token saknas")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"password": request.new_password}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Kunde inte uppdatera lösenord")

        return {"success": True, "message": "Lösenord uppdaterat!"}


@app.get("/api/auth/user")
async def get_current_user(request: Request):
    """Get current logged in user info."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"authenticated": False}

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}"
            }
        )

        if response.status_code != 200:
            return {"authenticated": False}

        user = response.json()
        return {
            "authenticated": True,
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "full_name": user.get("user_metadata", {}).get("full_name")
            }
        }


@app.delete("/api/auth/delete-account")
async def delete_account(request: Request):
    """
    Delete user account and ALL associated data.
    This is permanent and cannot be undone (GDPR right to be forgotten).
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user info first
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")

        user = user_response.json()
        user_id = user.get("id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Kunde inte hitta användare")

    # Delete all user data from all tables (order matters due to foreign keys)
    tables_to_clear = [
        "applications",
        "user_cvs",
        "user_cv_branscher",
        "user_skills",
        "user_awards",
        "user_volunteer",
        "user_experience_tags",
        "user_experiences",
        "user_education",
        "user_ai_feedback",
        "user_cover_letter_preferences",
        "user_job_preferences",
        "user_google_credentials",
        "user_profiles",
    ]

    deleted_counts = {}
    for table in tables_to_clear:
        try:
            # Use service role key to bypass RLS for deletion
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{SUPABASE_URL}/rest/v1/{table}?user_id=eq.{user_id}",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Prefer": "return=representation"
                    },
                    timeout=10
                )
                if response.status_code < 400:
                    deleted = response.json() if response.text else []
                    deleted_counts[table] = len(deleted) if isinstance(deleted, list) else 0
        except Exception as e:
            logger.warning(f"Could not delete from {table}: {e}")

    # Delete the user from Supabase Auth (requires service role)
    async with httpx.AsyncClient() as client:
        delete_response = await client.delete(
            f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        if delete_response.status_code not in [200, 204]:
            logger.error(f"Failed to delete auth user: {delete_response.text}")
            # Data is already deleted, so we continue

    logger.info(f"Deleted account {user_id}: {deleted_counts}")

    return {
        "success": True,
        "message": "Ditt konto och all din data har raderats permanent.",
        "deleted": deleted_counts
    }


@app.get("/api/auth/export-data")
async def export_user_data(request: Request):
    """
    Export all user data as JSON (GDPR Art. 20 - Right to data portability).
    Returns all personal data in a machine-readable format.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user info
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")

        user = user_response.json()
        user_id = user.get("id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Kunde inte hitta användare")

    # Collect all user data from all tables
    export_data = {
        "export_date": datetime.now().isoformat(),
        "user_id": user_id,
        "email": user.get("email"),
        "created_at": user.get("created_at"),
        "data": {}
    }

    tables_to_export = [
        ("profile", "user_profiles"),
        ("job_preferences", "user_job_preferences"),
        ("cover_letter_preferences", "user_cover_letter_preferences"),
        ("ai_feedback", "user_ai_feedback"),
        ("education", "user_education"),
        ("experiences", "user_experiences"),
        ("volunteer", "user_volunteer"),
        ("awards", "user_awards"),
        ("skills", "user_skills"),
        ("cv_branscher", "user_cv_branscher"),
        ("cvs", "user_cvs"),
        ("applications", "applications"),
    ]

    for key, table in tables_to_export:
        try:
            data = await db_request("GET", table, params={"user_id": f"eq.{user_id}"})
            export_data["data"][key] = data or []
        except Exception as e:
            logger.warning(f"Could not export from {table}: {e}")
            export_data["data"][key] = []

    return {
        "success": True,
        "message": "All din data har exporterats.",
        "export": export_data
    }


# ============== GMAIL API ENDPOINTS (User brings own credentials) ==============

@app.post("/api/gmail/credentials")
async def save_google_credentials(request: GoogleCredentialsRequest, user_id: str = "default_user"):
    """
    Save user's own Google Cloud credentials.
    Users must create their own Google Cloud project and OAuth credentials.
    """
    data = {
        "user_id": user_id,
        "google_client_id": request.google_client_id,
        "google_client_secret": request.google_client_secret,
        "is_connected": False,
        "updated_at": datetime.now().isoformat()
    }

    # Upsert credentials
    existing = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if existing:
        result = await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data=data)
    else:
        result = await db_request("POST", "user_google_credentials", data=data)

    return {"success": True, "message": "Credentials saved. Now connect your Gmail."}


@app.get("/api/gmail/auth-url")
async def get_gmail_auth_url(user_id: str = "default_user", redirect_uri: str = None):
    """
    Get Google OAuth URL for user to authorize Gmail access.
    Uses the user's own Google Cloud credentials.
    """
    # Get user's credentials
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds:
        raise HTTPException(status_code=400, detail="No Google credentials found. Save your credentials first.")

    cred = creds[0]
    client_id = cred.get("google_client_id")

    if not redirect_uri:
        redirect_uri = f"{os.getenv('VERCEL_URL', 'http://localhost:8000')}/api/gmail/callback"

    # Build OAuth URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GMAIL_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id  # Pass user_id through state
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return {"success": True, "auth_url": auth_url, "redirect_uri": redirect_uri}


@app.get("/api/gmail/callback")
async def gmail_oauth_callback(code: str, state: str = "default_user"):
    """
    Handle OAuth callback after user authorizes Gmail access.
    Exchange code for tokens using user's own credentials.
    """
    user_id = state

    # Get user's credentials
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds:
        raise HTTPException(status_code=400, detail="No credentials found")

    cred = creds[0]

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": cred["google_client_id"],
                "client_secret": cred["google_client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{os.getenv('VERCEL_URL', 'http://localhost:8000')}/api/gmail/callback"
            }
        )

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")

        tokens = response.json()

        # Get user's Gmail address
        profile_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        gmail_address = profile_response.json().get("email", "")

    # Save tokens
    expires_at = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
    await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data={
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "token_expires_at": expires_at.isoformat(),
        "gmail_address": gmail_address,
        "is_connected": True,
        "updated_at": datetime.now().isoformat()
    })

    # Return success HTML
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head><title>Gmail Connected!</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px;">
        <h1 style="color: #22c55e;">Gmail Connected!</h1>
        <p>Your Gmail ({gmail_address}) is now connected.</p>
        <p>You can close this window and return to the app.</p>
        <script>setTimeout(() => window.close(), 3000);</script>
    </body>
    </html>
    """)


@app.get("/api/gmail/status")
async def get_gmail_status(user_id: str = "default_user"):
    """Check if user has Gmail connected"""
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds:
        return {"connected": False, "has_credentials": False}

    cred = creds[0]
    return {
        "connected": cred.get("is_connected", False),
        "has_credentials": bool(cred.get("google_client_id")),
        "gmail_address": cred.get("gmail_address")
    }


async def refresh_gmail_token(user_id: str) -> Optional[str]:
    """Refresh Gmail access token if expired"""
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds:
        return None

    cred = creds[0]

    # Check if token is still valid
    expires_at = cred.get("token_expires_at")
    if expires_at:
        try:
            exp_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if exp_time > datetime.now(exp_time.tzinfo):
                return cred.get("access_token")
        except:
            pass

    # Refresh token
    refresh_token = cred.get("refresh_token")
    if not refresh_token:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": cred["google_client_id"],
                "client_secret": cred["google_client_secret"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
        )

        if response.status_code != 200:
            return None

        tokens = response.json()
        expires_at = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))

        await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data={
            "access_token": tokens["access_token"],
            "token_expires_at": expires_at.isoformat(),
            "updated_at": datetime.now().isoformat()
        })

        return tokens["access_token"]


@app.post("/api/gmail/draft")
async def create_gmail_draft(request: CreateGmailDraftRequest, user_id: str = "default_user"):
    """
    Create a draft email in user's Gmail.
    Requires user to have connected their Gmail first.
    """
    # Get valid access token
    access_token = await refresh_gmail_token(user_id)
    if not access_token:
        raise HTTPException(status_code=401, detail="Gmail not connected or token expired. Please reconnect.")

    # Create email message
    message = MIMEMultipart()
    message["to"] = request.to_email
    message["subject"] = request.subject
    message.attach(MIMEText(request.body, "plain"))

    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # Create draft via Gmail API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"message": {"raw": raw_message}}
        )

        if response.status_code != 200:
            logger.error(f"Gmail API error: {response.text}")
            raise HTTPException(status_code=500, detail="Failed to create draft")

        draft = response.json()

    # Save application if job_id provided
    if request.job_id:
        await db_request("POST", "applications", data={
            "user_id": user_id,
            "job_id": request.job_id,
            "cover_letter": request.body,
            "status": "draft",
            "gmail_draft_id": draft.get("id"),
            "created_at": datetime.now().isoformat()
        })

    return {
        "success": True,
        "draft_id": draft.get("id"),
        "message": "Draft created! Check your Gmail drafts folder."
    }


# ============== FRONTEND ==============

@app.get("/setup", response_class=HTMLResponse)
async def setup_page():
    """Gmail setup guide page"""
    return get_setup_guide_html()


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Login/signup page"""
    return get_login_html()


@app.get("/integritetspolicy", response_class=HTMLResponse)
async def privacy_policy_page():
    """Privacy policy page (GDPR)"""
    try:
        policy_path = pathlib.Path(__file__).parent.parent / "integritetspolicy.html"
        if policy_path.exists():
            return policy_path.read_text(encoding='utf-8')
    except:
        pass
    return "<h1>Integritetspolicy kunde inte laddas</h1>"


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend"""
    return get_frontend_html()


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})
