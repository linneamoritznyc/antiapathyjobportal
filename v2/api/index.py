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
import pathlib
import io
from PyPDF2 import PdfReader
from docx import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # For client-side auth
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# App-level Gmail OAuth credentials (shared by all users, set in Vercel env vars)
# Each user's access/refresh tokens are stored per-user in Supabase
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")

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


# ============== STORAGE BUCKET INIT ==============

async def ensure_storage_buckets():
    """Create required storage buckets if they don't exist"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return

    buckets = [
        {"id": "profile-photos", "name": "profile-photos", "public": True},
        {"id": "training-letters", "name": "training-letters", "public": True},
        {"id": "cv-files", "name": "cv-files", "public": True},
    ]

    async with httpx.AsyncClient() as client:
        for bucket in buckets:
            try:
                resp = await client.post(
                    f"{SUPABASE_URL}/storage/v1/bucket",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=bucket,
                    timeout=10
                )
                if resp.status_code in [200, 201]:
                    logger.info(f"Created storage bucket: {bucket['id']}")
                elif resp.status_code == 409:
                    logger.debug(f"Storage bucket already exists: {bucket['id']}")
                else:
                    logger.warning(f"Bucket {bucket['id']}: {resp.status_code} - {resp.text[:100]}")
            except Exception as e:
                logger.warning(f"Could not create bucket {bucket['id']}: {e}")


@app.on_event("startup")
async def startup_event():
    await ensure_storage_buckets()


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


class UpdateApplicationRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    cover_letter: Optional[str] = None


class SaveJobRequest(BaseModel):
    job_id: str
    notes: Optional[str] = None


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
    """Extract a real contact email from job ad text, filtering generic/system addresses."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)

    # Substrings that indicate a generic/system address — not a real contact
    exclude_fragments = [
        'noreply', 'no-reply', 'donotreply',
        'arbetsformedlingen', 'arbetsförmedlingen',
        'platsbanken',
        'info@', 'kontakt@', 'post@', 'mail@', 'hej@',
        'support@', 'help@', 'helpdesk@',
        'kundtjanst@', 'kundservice@',
        'jobb@', 'jobb.', 'career@', 'careers@', 'jobbansok',
        'ansok@', 'ansökan@',
        'hr@', 'rekrytering@', 'rekrytera@', 'resurs@',
        'admin@', 'webmaster@', 'abuse@',
        'example.com', 'test@',
    ]

    for email in emails:
        low = email.lower()
        if not any(ex in low for ex in exclude_fragments):
            return low
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
    except Exception:
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

                # Extract more fields from the ad
                app_details = ad.get("applicationDetails", {}) or {}
                conditions = ad.get("conditions", {}) or {}
                employment_type = ad.get("employmentType", "") or conditions.get("employmentType", "")
                duration = ad.get("duration", "") or conditions.get("duration", "")
                working_hours = ad.get("workingHoursType", "") or conditions.get("workingHoursType", "")
                salary_type = conditions.get("salaryType", "")
                salary_description = conditions.get("salaryDescription", "")

                # Always fetch full job detail — more reliable email + extra fields
                number_of_positions = 1
                municipality = ""
                county = ""
                occupation = ""
                try:
                    detail_res = await client.get(
                        f"https://platsbanken-api.arbetsformedlingen.se/jobs/v1/job/{job_id}",
                        headers={"Content-Type": "application/json"},
                        timeout=8
                    )
                    if detail_res.status_code == 200:
                        detail = detail_res.json()
                        full_desc = detail.get("description", "") or ""
                        if len(full_desc) > len(description):
                            description = full_desc

                        d_app = detail.get("applicationDetails", {}) or {}
                        d_cond = detail.get("conditions", {}) or {}
                        d_workplace = detail.get("workplace", {}) or {}

                        # applicationDetails.email is most reliable
                        if d_app.get("email"):
                            app_details_email = d_app["email"].lower()
                        else:
                            app_details_email = None

                        apply_url = d_app.get("url", "") or app_details.get("url", "")
                        contact_name = d_app.get("name") or extract_contact_name(full_desc)
                        contact_phone = d_app.get("phoneNumber", "")

                        if not employment_type:
                            employment_type = d_cond.get("employmentType", "")
                        if not duration:
                            duration = d_cond.get("duration", "")
                        if not working_hours:
                            working_hours = d_cond.get("workingHoursType", "")
                        if not salary_type:
                            salary_type = d_cond.get("salaryType", "")
                        if not salary_description:
                            salary_description = d_cond.get("salaryDescription", "")

                        number_of_positions = detail.get("numberOfVacancies", 1) or 1
                        municipality = d_workplace.get("municipality", "") or ""
                        county = d_workplace.get("region", "") or ""
                        occupation = detail.get("occupation", {}).get("label", "") if isinstance(detail.get("occupation"), dict) else ""
                except Exception as e:
                    logger.debug(f"Detail fetch failed for {job_id}: {e}")
                    app_details_email = None
                    apply_url = app_details.get("url", "")
                    contact_name = extract_contact_name(description)
                    contact_phone = app_details.get("phoneNumber", "")

                # Pick best contact email:
                # Priority: applicationDetails.email → extract from full description
                # Both filtered through extract_email's blocklist
                contact_email = None
                if app_details_email and not any(ex in app_details_email for ex in [
                    'noreply', 'no-reply', 'arbetsformedlingen', 'platsbanken',
                    'donotreply', 'example.com'
                ]):
                    contact_email = app_details_email
                if not contact_email:
                    contact_email = extract_email(description)

                # Strip HTML tags from description
                description = re.sub(r'<[^>]+>', ' ', description)
                description = re.sub(r'\s+', ' ', description).strip()

                job = {
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "municipality": municipality,
                    "county": county,
                    "occupation": occupation,
                    "description": description[:6000],
                    "url": f"https://arbetsformedlingen.se/platsbanken/annonser/{job_id}",
                    "deadline": deadline,
                    "priority": calculate_priority(deadline),
                    "contact_email": contact_email,
                    "contact_name": contact_name,
                    "contact_phone": contact_phone,
                    "employment_type": employment_type,
                    "duration": duration,
                    "working_hours": working_hours,
                    "salary_type": salary_type,
                    "salary_description": salary_description,
                    "number_of_positions": number_of_positions,
                    "apply_url": apply_url,
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

    "industri": """- Siggesta Gård: Städning och praktiskt underhållsarbete
- Max Hamburgare (Apr-Aug 2024): Kök, drive-in, fysiskt arbete i högt tempo
- ICA Maxi (2015, 2017, 2019): Fysiskt butiksarbete, varumottagning, frukt/grönt
- B-körkort och tillgång till bil
- Van vid tidiga morgnar, kvällar och helger""",

    "healthcare": """- Bred servicevana och empatisk kontakt med människor
- Flexibel, pålitlig och van vid ansvar
- B-körkort och flexibel med arbetstider""",

    "contentmoderation": """- Innehållsmoderator, Clubhouse (Jun 2021-Jan 2022): Trust & Safety, granskning, support
- Innehållsanalytiker, Google Ads (Maj 2018-Apr 2019): 100+ annonser/dag, policyhantering
- Global Marketing, Minerva Project (Sep 2019-Apr 2020): Kundkommunikation via Intercom""",

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


async def generate_cover_letter(job: Dict, user_cv_text: Optional[str] = None, user_profile: Optional[Dict] = None, extra_hints: Optional[str] = None) -> str:
    """Generate personalized cover letter using Claude"""

    if not ANTHROPIC_API_KEY:
        return generate_template_letter(job)

    # Get relevant experience
    category = detect_job_category(job.get("title", ""), job.get("description", ""))
    experience = user_cv_text or DEFAULT_EXPERIENCE.get(category, DEFAULT_EXPERIENCE["default"])

    # Append any extra hints the user selected in the UI
    if extra_hints:
        experience += f"\n\nEXTRA ERFARENHETER SOM MÅSTE NÄMNAS I BREVET:\n{extra_hints}"

    # Use profile data from database, fall back to defaults
    p = user_profile or {}
    name = p.get("full_name", "Linnea Moritz")
    phone = p.get("phone", "0761166109")
    email = p.get("email", "linneamoritzCV@gmail.com")
    location = p.get("location", "Sollentuna")
    has_license = p.get("drivers_license", True)
    linkedin = p.get("linkedin", "")

    contact_greeting = f"Hej {job.get('contact_name', '')}!" if job.get('contact_name') else "Hej!"

    # Build extra job details for the prompt
    job_extras = []
    if job.get("employment_type"):
        job_extras.append(f"- Anställningsform: {job['employment_type']}")
    if job.get("working_hours"):
        job_extras.append(f"- Omfattning: {job['working_hours']}")
    if job.get("duration"):
        job_extras.append(f"- Varaktighet: {job['duration']}")
    if job.get("salary_type") or job.get("salary_description"):
        sal = job.get("salary_description") or job.get("salary_type", "")
        job_extras.append(f"- Lön: {sal}")
    extras_text = "\n".join(job_extras) if job_extras else ""

    # Build user info section
    user_info = f"- {name}"
    user_info += f", bor i {location}"
    if has_license:
        user_info += f"\n- Har B-körkort, egen bil, flexibel med arbetstider"
    else:
        user_info += f"\n- Flexibel med arbetstider"
    user_info += f"\n- Telefon: {phone}"
    user_info += f"\n- Svenska (modersmål), Engelska (flytande)"
    if linkedin:
        user_info += f"\n- LinkedIn: {linkedin}"

    prompt = f"""Skriv ett personligt brev på svenska för denna jobbansökan.

JOBBET:
- Titel: {job.get('title')}
- Företag: {job.get('company')}
- Plats: {job.get('location')}
{extras_text}
- Beskrivning: {job.get('description', '')[:2500]}

MIN BAKGRUND (använd som inspiration — plocka bara det som faktiskt är relevant):
{experience}

OM MIG:
{user_info}

INSTRUKTIONER:
1. Börja med: {contact_greeting}
2. Skriv 150-200 ord på naturlig, varm svenska
3. Matcha tonen mot jobbet: fysisk/praktisk tjänst → enkelt och jordnära; kontorsjobb → lite mer formellt
4. Lyft BARA erfarenheter som faktiskt passar jobbet. Om inga erfarenheter matchar direkt, fokusera istället på personliga egenskaper som passar (t.ex. noggrannhet, pålitlighet, initiativförmåga, servicekänsla). Försök ALDRIG koppla irrelevant erfarenhet till jobbet på ett konstruerat sätt.
5. VIKTIGT: Om annonsen nämner specifika krav eller önskemål (t.ex. körkort, bil, fysisk förmåga, kvällar/helger, sommarsäsong, "annan sysselsättning"), bekräfta kortfattat att jag uppfyller/passar dem — utan att överdriva
6. Nämn var jag bor och att jag är flexibel med arbetstider
7. Om "EXTRA ERFARENHETER SOM MÅSTE NÄMNAS I BREVET" finns ovan — nämn dem ALLTID specifikt i brevet, även om de inte är den starkaste matchningen
8. Avsluta med:
   Med vänlig hälsning,
   {name}
   {phone}
   {email}

Skriv ENDAST det färdiga brevet, inget annat."""

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

    # Extract profile data
    profile = master_cv.get('profile', {})
    if isinstance(profile, list) and len(profile) > 0:
        profile = profile[0]

    # Format experiences as text
    experiences = master_cv.get('experiences', [])
    experience_text = ""
    for exp in experiences:
        if isinstance(exp, dict):
            company = exp.get('company', '')
            title = exp.get('title', '')
            location = exp.get('location', '')
            dates = exp.get('dates', '') or f"{exp.get('start_date', '')} - {exp.get('end_date', 'Nuvarande')}"
            description = exp.get('description', '')
            categories = exp.get('categories', [])
            experience_text += f"\n{title} - {company} ({location})\n{dates}\n{description}\nKategorier: {', '.join(categories) if categories else 'Alla'}\n"

    # Format education as text
    education_list = master_cv.get('education', [])
    education_text = ""
    for edu in education_list:
        if isinstance(edu, dict):
            school = edu.get('school', '')
            degree = edu.get('degree', '')
            field = edu.get('field_of_study', '')
            dates = edu.get('dates', '') or f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
            education_text += f"\n{school} - {degree} {field} ({dates})"

    # Format skills as text
    skills_list = master_cv.get('skills', [])
    skills_text = ""
    for skill in skills_list:
        if isinstance(skill, dict):
            skills_text += f"\n- {skill.get('skill_text', '')} ({skill.get('category', 'all')})"
        elif isinstance(skill, str):
            skills_text += f"\n- {skill}"

    prompt = f"""Skriv ett komplett CV på svenska för {vibe['name']}-jobb.

PERSONINFO:
- Namn: {profile.get('full_name', '')}
- E-post: {profile.get('email', '')}
- Telefon: {profile.get('phone', '')}
- Plats: {profile.get('location', '')}
- Språk: {', '.join(profile.get('languages', ['Svenska', 'Engelska'])) if isinstance(profile.get('languages'), list) else 'Svenska, Engelska'}
- Körkort: {'Ja, B-körkort' if profile.get('drivers_license') else 'Nej'}

ALL ERFARENHET (inkludera ALLT):
{experience_text or 'Ingen erfarenhet angiven'}

ALL UTBILDNING:
{education_text or 'Ej angivet'}

ALLA FÄRDIGHETER:
{skills_text or 'Ej angivet'}

DENNA CV-VERSION ÄR FÖR: {vibe['name']}
Fokus: {vibe['focus']}

INSTRUKTIONER:
1. Skriv ett KOMPLETT CV - inkludera ALL erfarenhet, ALL utbildning, ALLA färdigheter
2. Ordna erfarenheterna kronologiskt (senaste först)
3. För {vibe['name']}-versionen: skriv en kort profil (2-3 meningar) som lyfter erfarenhet relevant för denna bransch
4. Bullet points för varje jobb ska vara korta och konkreta
5. Inga emojis
6. Format:
   NAMN
   Plats | Telefon | E-post

   PROFIL
   [2-3 meningar]

   ERFARENHET
   [Titel - Företag (Datum)]
   - Punkt 1
   - Punkt 2

   UTBILDNING
   [Skola - Examen (Datum)]

   FÄRDIGHETER
   [Lista]

KRITISKT - Du MÅSTE inkludera VARJE jobb som listas ovan. Räkna jobben. Om det finns 5 jobb ovan måste det finnas 5 jobb i CV:t. INGA undantag. FILTRERA INTE.

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
    """Match a job to the best CV vibe. Returns vibe_id that maps to a CV PDF."""
    text = f"{job_title} {job_description}".lower()

    # Use whole-word matching via regex to avoid "it" matching inside "arbetstider" etc.
    def word_match(keyword: str, haystack: str) -> bool:
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', haystack))

    vibe_keywords = {
        "restaurant":        ["servitör", "servitris", "restaurang", "kock", "café", "barista", "kök", "matlagning", "dryck", "bar", "bageri", "konditori"],
        "retail":            ["butik", "kassa", "kassaarbete", "försäljare", "säljare", "retail", "handel", "klädbutik", "ica", "coop", "lidl", "hemköp", "lagerarbete i butik"],
        "customerservice":   ["kundtjänst", "kundservice", "kundmottagning", "support", "helpdesk", "telefonsupport", "chatt", "reception", "receptionist"],
        "tech":              ["mjukvara", "programmering", "webbutvecklare", "frontend", "backend", "systemutvecklare", "it-tekniker", "it-support", "devops", "agile", "scrum"],
        "healthcare":        ["vård", "omsorg", "sjuksköterska", "undersköterska", "äldreboende", "hemtjänst", "medicin", "rehab", "personlig assistent", "lss", "psykiatri"],
        "industri":          ["trädgård", "industri", "lager", "städ", "städning", "renhållning", "utomhus", "bygg", "produktion", "truck", "magasin", "underhåll", "rastplats",
                              "skötsel", "fastighet", "mark", "park", "reparation", "maskin", "montör", "svetsare", "godshantering", "bud", "chaufför", "sommarjobb utomhus"],
        "contentmoderation": ["moderator", "content moderation", "trust and safety", "granskning", "recensioner", "online safety"],
        "art":               ["konst", "kultur", "galleri", "utställning", "kreativ", "illustration", "foto", "film", "musik", "teater"],
    }

    scores = {vibe: sum(1 for kw in kws if word_match(kw, text)) for vibe, kws in vibe_keywords.items()}
    best_vibe = max(scores, key=scores.get) if max(scores.values()) > 0 else "customerservice"
    return best_vibe


# Maps vibe_id → actual CV PDF filename in cv_files/
CV_FILE_MAP = {
    "restaurant":        "CV_Linnea_Moritz_Restaurang_Cafe.pdf",
    "retail":            "CV_Linnea_Moritz_Butik_Kassa.pdf",
    "customerservice":   "CV_Linnea_Moritz_Kundtjanst.pdf",
    "tech":              "CV_Linnea_Moritz_Tech_Kontor.pdf",
    "healthcare":        "CV_Linnea_Moritz_Vard_Omsorg.pdf",
    "industri":          "CV_Linnea_Moritz_Industri_Tradgard.pdf",
    "contentmoderation": "CV_Linnea_Moritz_Content_Moderation.pdf",
    "art":               "CV_Linnea_Moritz_Konst_Kultur.pdf",
}
CV_FILES_DIR = pathlib.Path(__file__).parent / "cv_files"


def get_cv_pdf_bytes(vibe_id: str) -> Optional[bytes]:
    """Read the matching CV PDF from disk. Returns None if not found."""
    filename = CV_FILE_MAP.get(vibe_id, CV_FILE_MAP["customerservice"])
    path = CV_FILES_DIR / filename
    try:
        return path.read_bytes()
    except Exception as e:
        logger.error(f"Could not read CV PDF {path}: {e}")
        return None


def get_cv_pdf_filename(vibe_id: str) -> str:
    """Return the CV PDF filename for a given vibe."""
    return CV_FILE_MAP.get(vibe_id, CV_FILE_MAP["customerservice"])


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
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, params=params, timeout=10)
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

    # Only send columns that exist in the jobs table
    db_columns = {"id", "title", "company", "location", "description", "url",
                  "deadline", "priority", "contact_email", "contact_name",
                  "source", "scraped_at", "link_status"}

    saved = 0
    for job in jobs:
        db_job = {k: v for k, v in job.items() if k in db_columns}
        # Store extra fields in description as fallback
        extras = []
        if job.get("employment_type"):
            extras.append(f"Anstallningsform: {job['employment_type']}")
        if job.get("working_hours"):
            extras.append(f"Omfattning: {job['working_hours']}")
        if job.get("duration"):
            extras.append(f"Varaktighet: {job['duration']}")
        if job.get("contact_phone"):
            extras.append(f"Telefon: {job['contact_phone']}")
        if job.get("salary_description"):
            extras.append(f"Lon: {job['salary_description']}")
        if extras and db_job.get("description"):
            db_job["description"] = "\n".join(extras) + "\n\n" + db_job["description"]
        result = await db_request("POST", "jobs", data=db_job)
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
    """Get all applications with job details"""
    # Use Supabase's select to embed job data
    url = f"{SUPABASE_URL}/rest/v1/applications?select=*,jobs(id,title,company,contact_email,url,deadline)&order=created_at.desc"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code == 200:
            apps = response.json()
            # Flatten job details into application
            for app in apps:
                if app.get("jobs"):
                    app["job_title"] = app["jobs"].get("title")
                    app["company"] = app["jobs"].get("company")
                    app["contact_email"] = app["jobs"].get("contact_email")
                    app["job_url"] = app["jobs"].get("url")
                    app["deadline"] = app["jobs"].get("deadline")
                    del app["jobs"]
            return apps
    return []


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
    """Scrape jobs from Platsbanken.
    Searches user's positive keywords PLUS a broad catch-all search,
    so unexpected dream jobs also appear (filtered by negatives in frontend).
    """
    keywords = request.keywords if request and request.keywords else ["servitör", "kundtjänst", "butik"]
    location = request.location if request else "Stockholm"

    all_jobs = []

    # 1. Scrape user's positive keywords (what they specifically want)
    for keyword in keywords[:5]:  # Max 5 keywords
        jobs = await scrape_platsbanken(keyword, location, max_jobs=10)
        all_jobs.extend(jobs)

    # 2. Broad catch-all scrape so unexpected cool jobs also appear
    #    (negative keywords filter them in frontend — we cast a wide net here)
    broad_terms = ["jobb", "anställning"]
    for term in broad_terms:
        broad_jobs = await scrape_platsbanken(term, location, max_jobs=15)
        all_jobs.extend(broad_jobs)

    # Remove duplicates by job ID
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique_jobs.append(job)

    # Sort by deadline (soonest first) before returning
    unique_jobs.sort(key=lambda j: j.get("deadline") or "2099-12-31")

    # Save to database if configured
    saved_count = await save_jobs_to_db(unique_jobs)

    return {
        "success": True,
        "jobs_found": len(unique_jobs),
        "jobs_saved": saved_count,
        "jobs": unique_jobs
    }


@app.get("/api/jobs")
async def list_jobs(request: Request, limit: int = 50):
    """List all jobs, filtered by user's interaction history if logged in"""
    # Get user_id from auth token (optional)
    auth_header = request.headers.get("Authorization", "")
    user_id = None
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
                )
                if user_response.status_code == 200:
                    user_id = user_response.json().get("id")
        except Exception:
            pass

    # Try database first
    jobs = await get_jobs_from_db(limit)

    if not jobs:
        # Fallback: scrape live AND save to DB so apply-with-cv can find them
        jobs = await scrape_platsbanken("jobb", "Stockholm", max_jobs=limit)
        if jobs:
            await save_jobs_to_db(jobs)

    if not jobs:
        return {"success": True, "source": "empty", "jobs": []}

    # If logged in, load user's interaction history and filter/score jobs
    if user_id and jobs:
        interactions = await db_request("GET", "user_job_interactions", params={
            "user_id": f"eq.{user_id}",
            "select": "job_id,action"
        }) or []

        rejected_ids = {i["job_id"] for i in interactions if i["action"] == "rejected"}
        applied_ids = {i["job_id"] for i in interactions if i["action"] == "applied"}
        skipped_ids = {i["job_id"] for i in interactions if i["action"] == "skipped"}

        # Hard-filter rejected and applied jobs out of the feed
        # Skipped jobs are moved to the end (deprioritized)
        active_jobs = [j for j in jobs if j["id"] not in rejected_ids and j["id"] not in applied_ids]
        skipped_jobs = [j for j in active_jobs if j["id"] in skipped_ids]
        fresh_jobs = [j for j in active_jobs if j["id"] not in skipped_ids]
        jobs = fresh_jobs + skipped_jobs  # Fresh first, skipped last

    return {"success": True, "source": "database", "jobs": jobs}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get single job by ID"""
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if jobs and len(jobs) > 0:
        return {"success": True, "job": jobs[0]}
    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs/{job_id}/interaction")
async def log_job_interaction(job_id: str, request: Request):
    """
    Log a user's interaction with a job (viewed, skipped, applied, rejected).
    This powers the smart feed — rejected/applied jobs are hidden, skipped pushed to end.
    Modeled after Meta/TikTok engagement signal collection: every action is an event.
    """
    auth_header = request.headers.get("Authorization", "")
    user_id = None
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
                )
                if user_response.status_code == 200:
                    user_id = user_response.json().get("id")
        except Exception:
            pass

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    body = await request.json()
    action = body.get("action", "").lower()
    valid_actions = {"viewed", "skipped", "applied", "saved", "rejected"}
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Ogiltig action. Välj bland: {', '.join(valid_actions)}")

    context = body.get("context", {})  # Optional metadata (time_spent, etc.)

    # Upsert: one record per (user, job, action) — prevents duplicate signals
    await db_request("POST", "user_job_interactions", data={
        "user_id": user_id,
        "job_id": job_id,
        "action": action,
        "context": context
    })

    return {"success": True, "job_id": job_id, "action": action}


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
async def save_application(request: SaveApplicationRequest, req: Request):
    """Save an application"""
    # Get user_id from auth token
    auth_header = req.headers.get("Authorization", "")
    user_id = "default_user"

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id", "default_user")

    data = {
        "job_id": request.job_id,
        "user_id": user_id,
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


@app.patch("/api/applications/{application_id}")
async def update_application(application_id: str, request: UpdateApplicationRequest):
    """Update an application's status, notes, or cover letter"""
    update_data = {"updated_at": datetime.now().isoformat()}

    if request.status is not None:
        update_data["status"] = request.status
        if request.status == "sent":
            update_data["sent_at"] = datetime.now().isoformat()

    if request.notes is not None:
        update_data["notes"] = request.notes

    if request.cover_letter is not None:
        update_data["cover_letter"] = request.cover_letter

    # Update via Supabase REST API
    url = f"{SUPABASE_URL}/rest/v1/applications?id=eq.{application_id}"
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            json=update_data,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
        )
        if response.status_code in [200, 201]:
            result = response.json()
            if result:
                return {"success": True, "application": result[0]}

    raise HTTPException(status_code=500, detail="Could not update application")


@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: str):
    """Delete an application"""
    url = f"{SUPABASE_URL}/rest/v1/applications?id=eq.{application_id}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code in [200, 204]:
            return {"success": True}

    raise HTTPException(status_code=500, detail="Could not delete application")


@app.post("/api/jobs/{job_id}/save")
async def save_job(job_id: str, request: Request):
    """Save/bookmark a job for later"""
    # Get user_id from auth token if available
    auth_header = request.headers.get("Authorization", "")
    user_id = "default_user"

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id", "default_user")

    # Check if application already exists
    existing = await db_request("GET", "applications", params={
        "job_id": f"eq.{job_id}",
        "user_id": f"eq.{user_id}"
    })

    if existing and len(existing) > 0:
        # Update existing to saved
        url = f"{SUPABASE_URL}/rest/v1/applications?id=eq.{existing[0]['id']}"
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                json={"status": "saved", "updated_at": datetime.now().isoformat()},
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                }
            )
            if response.status_code in [200, 201]:
                return {"success": True, "application": response.json()[0]}
    else:
        # Create new saved application
        data = {
            "job_id": job_id,
            "user_id": user_id,
            "status": "saved",
            "created_at": datetime.now().isoformat()
        }
        result = await db_request("POST", "applications", data=data)
        if result:
            return {"success": True, "application": result[0]}

    raise HTTPException(status_code=500, detail="Could not save job")


@app.delete("/api/jobs/{job_id}/save")
async def unsave_job(job_id: str, request: Request):
    """Remove a saved job"""
    auth_header = request.headers.get("Authorization", "")
    user_id = "default_user"

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id", "default_user")

    # Delete saved application
    url = f"{SUPABASE_URL}/rest/v1/applications?job_id=eq.{job_id}&user_id=eq.{user_id}&status=eq.saved"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code in [200, 204]:
            return {"success": True}

    raise HTTPException(status_code=500, detail="Could not unsave job")


@app.get("/api/stats")
async def get_stats():
    """Get statistics"""
    jobs = await get_jobs_from_db(1000)
    apps = await get_applications_from_db()

    # Calculate deadline_today - count jobs with deadline today
    today = datetime.now().strftime('%Y-%m-%d')
    deadline_today = 0
    if jobs:
        for job in jobs:
            deadline = job.get("deadline", "")
            if deadline and deadline.startswith(today):
                deadline_today += 1

    return {
        "success": True,
        "stats": {
            "total_jobs": len(jobs) if jobs else 0,
            "total_applications": len(apps) if apps else 0,
            "drafts": len([a for a in (apps or []) if a.get("status") == "draft"]),
            "sent": len([a for a in (apps or []) if a.get("status") == "sent"]),
            "interviews": len([a for a in (apps or []) if a.get("status") == "interview"]),
            "deadline_today": deadline_today
        }
    }


# ============== CV ENDPOINTS ==============

@app.get("/api/cv/vibes")
async def list_cv_vibes():
    """List all available CV vibes/categories"""
    return {"success": True, "vibes": CV_BRANSCHER}


@app.post("/api/cv/master")
async def save_master_cv(request: Request, master_cv: MasterCV):
    """
    Save complete Master CV with all structured data.
    This is the source of truth - all CV vibes are generated from this.
    """
    # Get user_id from auth token
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

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
async def get_master_cv(request: Request):
    """Get user's complete Master CV as structured data"""
    # Get user_id from auth token
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        return {"success": False, "master_cv": None, "message": "Ej inloggad"}

    # Get profile
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    profile = profiles[0] if profiles else None

    if not profile:
        # Create empty profile for new users
        profile = {"user_id": user_id, "full_name": "", "email": "", "phone": "", "location": ""}

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
        "user_id": user_id,
        "master_cv": {
            "profile": profile,
            "education": education,
            "experiences": experiences,
            "volunteer": volunteer,
            "awards": [a.get("award_text") if isinstance(a, dict) else a for a in awards],
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
async def generate_cv_branscher(request: Request):
    """Generate all CV bransch versions from master CV"""
    # Get user_id from auth token
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # Get user's profile and experiences
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    experiences = await db_request("GET", "user_experiences", params={"user_id": f"eq.{user_id}", "order": "sort_order.asc"})
    education = await db_request("GET", "user_education", params={"user_id": f"eq.{user_id}"})
    skills = await db_request("GET", "user_skills", params={"user_id": f"eq.{user_id}"})

    if not experiences or len(experiences) == 0:
        return {"success": False, "message": "Lägg till erfarenheter i Master CV först!"}

    profile = profiles[0] if profiles else {}

    # Build master CV structure
    master_cv = {
        "profile": profile,
        "experiences": experiences,
        "education": education or [],
        "skills": skills or []
    }

    # Generate all vibes
    generated = await generate_all_cv_vibes(master_cv, user_id)

    return {
        "success": True,
        "message": f"Genererade {len(generated)} CV-versioner!",
        "cvs": generated
    }


@app.get("/api/cv/all")
async def get_user_cvs(request: Request):
    """Get all user's generated CV versions"""
    # Get user_id from auth token
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        return {"success": True, "cvs": [], "message": "Ej inloggad"}

    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "order": "vibe_id.asc"
    })

    return {"success": True, "cvs": cvs or [], "user_id": user_id}


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


# ============== MASTER CV & BRANSCH-CVS ENDPOINTS ==============

@app.get("/api/master-cv")
async def get_full_master_cv(request: Request):
    """Get complete Master CV data including all sections (experiences, education, projects, certifications, awards, volunteer, skills)"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        return {"success": False, "message": "Ej inloggad"}

    # Fetch all data from Supabase
    experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    education = await db_request("GET", "user_education", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    projects = await db_request("GET", "tech_projects", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    certifications = await db_request("GET", "user_certifications", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    tech_certs = await db_request("GET", "tech_certifications", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    awards = await db_request("GET", "user_awards", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    volunteer = await db_request("GET", "user_volunteer", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    skills = await db_request("GET", "user_skills", params={
        "user_id": f"eq.{user_id}"
    }) or []

    return {
        "experiences": experiences,
        "education": education,
        "projects": projects,
        "certifications": certifications + tech_certs,
        "awards": awards,
        "volunteer": volunteer,
        "skills": skills
    }


@app.get("/api/bransch-cvs")
async def get_bransch_cvs(request: Request):
    """Get all Bransch-CVs (industry-specific CV templates)"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        return {"success": False, "bransch_cvs": []}

    # Fetch bransch-CVs from database
    bransch_cvs = await db_request("GET", "bransch_cvs", params={
        "user_id": f"eq.{user_id}", "order": "created_at.desc"
    }) or []

    return {"bransch_cvs": bransch_cvs}


@app.get("/api/master-cv/download-pdf")
async def download_master_cv_pdf(request: Request):
    """Generate and download Master CV as PDF"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # For now, return a simple text response indicating this feature is coming soon
    # In production, this would generate a formatted PDF using a library like ReportLab or WeasyPrint
    raise HTTPException(status_code=501, detail="PDF-generering kommer snart. Använd Bransch-CVs för nu.")


@app.get("/api/bransch-cvs/{cv_id}/download-pdf")
async def download_bransch_cv_pdf(cv_id: str, request: Request):
    """Generate and download a specific Bransch-CV as PDF"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # Fetch the specific Bransch-CV
    cv_result = await db_request("GET", "bransch_cvs", params={
        "id": f"eq.{cv_id}",
        "user_id": f"eq.{user_id}"
    })

    if not cv_result or len(cv_result) == 0:
        raise HTTPException(status_code=404, detail="Bransch-CV hittades inte")

    # For now, return a simple text response indicating this feature is coming soon
    # In production, this would generate a formatted PDF
    raise HTTPException(status_code=501, detail="PDF-generering kommer snart. CV-text finns i bransch-CV databasen.")



@app.post("/api/jobs/{job_id}/apply-with-cv")
async def apply_with_cv(request: Request, job_id: str):
    """
    Smart apply: Auto-selects best CV, generates cover letter, returns both.
    This is the main "one-click apply" endpoint.
    """
    # Get user_id from auth token (optional - works without login too)
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
                )
                if user_response.status_code == 200:
                    user_id = user_response.json().get("id")
        except Exception as e:
            logger.warning(f"Auth check failed: {e}")

    # Parse request body (may contain job data as fallback)
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Get job from database; fall back to job data sent from frontend
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if not jobs:
        job_from_body = body.get("job")
        if job_from_body:
            job = job_from_body
            logger.info(f"Job {job_id} not in DB, using data from request body")
        else:
            raise HTTPException(status_code=404, detail="Jobbet hittades inte")
    else:
        job = jobs[0]

    # Match job to best CV vibe
    best_vibe = match_job_to_cv_vibe(job.get("title", ""), job.get("description", ""))
    logger.info(f"Job '{job.get('title')}' matched to CV vibe: {best_vibe}")

    # Try to get matching CV and user profile if logged in
    cv = None
    user_profile = None
    if user_id:
        cvs = await db_request("GET", "user_cvs", params={
            "user_id": f"eq.{user_id}",
            "vibe_id": f"eq.{best_vibe}"
        })
        cv = cvs[0] if cvs else None
        # Fetch user profile for cover letter personalization
        profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        user_profile = profiles[0] if profiles else None

    # Generate cover letter (works with or without CV/profile)
    cv_text_for_letter = cv.get("cv_text") if cv else None
    extra_hints = body.get("extra_hints")
    cover_letter = await generate_cover_letter(job, cv_text_for_letter, user_profile, extra_hints)

    # Try to automatically create a Gmail draft using this user's connected Gmail
    contact_email = job.get("contact_email")
    contact_name = job.get("contact_name")

    # Validate email looks real before using it
    if contact_email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', contact_email):
        logger.warning(f"Scraped email looks invalid, ignoring: {contact_email}")
        contact_email = None

    # Build subject line: "Ansökan: Jobbtitel – Linnea Moritz"
    sender_name = user_profile.get("full_name", "Linnea Moritz") if user_profile else "Linnea Moritz"
    job_title = job.get("title", "Tjänst")
    subject = f"Ansökan: {job_title} – {sender_name}"

    # Append custom email signature if the user has one saved
    email_signature = user_profile.get("email_signature", "") if user_profile else ""
    email_body = cover_letter + ("\n\n" + email_signature if email_signature else "")

    # Create Gmail draft with PDF attachments if user has connected Gmail
    draft_id = None
    if contact_email and user_id:
        attachments = []

        # 1. Cover letter as PDF (professional Swedish business letter design)
        sender_phone = user_profile.get("phone", "0761166109") if user_profile else "0761166109"
        sender_email_addr = user_profile.get("email", "linneamoritzCV@gmail.com") if user_profile else "linneamoritzCV@gmail.com"
        sender_location = user_profile.get("location", "Sollentuna") if user_profile else "Sollentuna"
        try:
            cover_letter_pdf = generate_cover_letter_pdf(
                email_body,
                sender_name=sender_name,
                sender_phone=sender_phone,
                sender_email=sender_email_addr,
                sender_location=sender_location,
                job_title=job_title,
                company=job.get("company", ""),
            )
            attachments.append({
                "filename": f"Personligt_Brev_{sender_name.replace(' ', '_')}.pdf",
                "data": cover_letter_pdf
            })
        except Exception as e:
            logger.error(f"Cover letter PDF generation failed: {e}")

        # 2. Matching CV PDF
        cv_pdf_bytes = get_cv_pdf_bytes(best_vibe)
        if cv_pdf_bytes:
            attachments.append({
                "filename": get_cv_pdf_filename(best_vibe),
                "data": cv_pdf_bytes
            })

        draft_id = await create_gmail_draft_for_user(
            user_id, contact_email, subject, email_body, attachments
        )

    return {
        "success": True,
        "job": {
            "id": job.get("id"),
            "title": job_title,
            "company": job.get("company"),
            "contact_email": contact_email,
            "contact_name": contact_name
        },
        "matched_vibe": best_vibe,
        "cv_filename": get_cv_pdf_filename(best_vibe),
        "cv": cv,
        "cover_letter": cover_letter,
        "draft_created": draft_id is not None,
        "draft_id": draft_id,
        "gmail_link": _create_gmail_link(job, cover_letter, subject)
    }


def _create_gmail_link(job: Dict, letter: str, subject: str = "") -> str:
    """Create Gmail compose link as fallback when no draft was created."""
    import urllib.parse
    to = job.get("contact_email", "")
    if not subject:
        subject = f"Ansökan: {job.get('title', 'Tjänst')}"
    return (
        f"https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={urllib.parse.quote(to)}"
        f"&su={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(letter)}"
    )


@app.post("/api/jobs/{job_id}/save-draft")
async def save_gmail_draft_with_attachments(request: Request, job_id: str):
    """
    Create (or update) a Gmail draft with the edited cover letter + PDF attachments.
    Called from the ApplyModal when the user clicks 'Spara i Gmail med bilagor'.
    Requires Gmail OAuth to be connected.
    """
    auth_header = request.headers.get("Authorization", "")
    user_id = None
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
                )
                if user_response.status_code == 200:
                    user_id = user_response.json().get("id")
        except Exception as e:
            logger.warning(f"Auth check failed: {e}")

    if not user_id:
        raise HTTPException(status_code=401, detail="Inloggning krävs")

    try:
        body = await request.json()
    except Exception:
        body = {}

    cover_letter_text = body.get("cover_letter", "")
    vibe = body.get("vibe", "customerservice")
    job = body.get("job", {})

    if not cover_letter_text:
        raise HTTPException(status_code=400, detail="Brevtext saknas")

    contact_email = job.get("contact_email")
    if not contact_email:
        raise HTTPException(status_code=400, detail="Jobbets e-postadress saknas")

    # Get user profile for sender name
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    user_profile = profiles[0] if profiles else {}
    sender_name = user_profile.get("full_name", "Linnea Moritz")

    job_title = job.get("title", "Tjänst")
    subject = f"Ansökan: {job_title} – {sender_name}"

    # Append custom signature if the user has one saved
    email_signature = user_profile.get("email_signature", "")
    email_body = cover_letter_text + ("\n\n" + email_signature if email_signature else "")

    attachments = []

    # 1. Cover letter as PDF (professional Swedish business letter design)
    sender_phone = user_profile.get("phone", "0761166109")
    sender_email_addr = user_profile.get("email", "linneamoritzCV@gmail.com")
    sender_location = user_profile.get("location", "Sollentuna")
    try:
        cover_letter_pdf = generate_cover_letter_pdf(
            email_body,
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_email=sender_email_addr,
            sender_location=sender_location,
            job_title=job_title,
            company=job.get("company", ""),
        )
        attachments.append({
            "filename": f"Personligt_Brev_{sender_name.replace(' ', '_')}.pdf",
            "data": cover_letter_pdf
        })
    except Exception as e:
        logger.error(f"Cover letter PDF generation failed: {e}")

    # 2. Matching CV PDF
    cv_pdf_bytes = get_cv_pdf_bytes(vibe)
    if cv_pdf_bytes:
        attachments.append({
            "filename": get_cv_pdf_filename(vibe),
            "data": cv_pdf_bytes
        })

    draft_id = await create_gmail_draft_for_user(
        user_id, contact_email, subject, email_body, attachments
    )

    if not draft_id:
        raise HTTPException(status_code=500, detail="Kunde inte skapa Gmail-utkast. Är Gmail kopplat?")

    return {
        "success": True,
        "draft_id": draft_id,
        "cv_filename": get_cv_pdf_filename(vibe),
        "attachments_count": len(attachments)
    }


# ============== FRONTEND ==============

def get_setup_guide_html():
    """Load Gmail setup guide HTML"""
    try:
        guide_path = pathlib.Path(__file__).parent.parent / "setup-guide.html"
        if guide_path.exists():
            return guide_path.read_text(encoding='utf-8')
    except Exception:
        pass
    return "<h1>Setup guide not found</h1>"


def get_login_html():
    """Load login page HTML"""
    try:
        login_path = pathlib.Path(__file__).parent.parent / "login.html"
        if login_path.exists():
            return login_path.read_text(encoding='utf-8')
    except Exception:
        pass
    return "<h1>Login page not found</h1>"


def get_frontend_html():
    """Load frontend HTML from file or use embedded version"""
    try:
        frontend_path = pathlib.Path(__file__).parent.parent / "frontend.html"
        if frontend_path.exists():
            return frontend_path.read_text(encoding='utf-8')
    except Exception:
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

@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check if environment variables are loaded"""
    return {
        "supabase_url_exists": bool(SUPABASE_URL),
        "supabase_url_length": len(SUPABASE_URL) if SUPABASE_URL else 0,
        "supabase_anon_key_exists": bool(SUPABASE_ANON_KEY),
        "supabase_anon_key_length": len(SUPABASE_ANON_KEY) if SUPABASE_ANON_KEY else 0,
        "anthropic_key_exists": bool(ANTHROPIC_API_KEY),
        "all_env_vars": list(os.environ.keys())[:10]  # First 10 env var names
    }

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
                "data": {"full_name": request.full_name} if request.full_name else {},
                "options": {
                    "email_redirect_to": "https://platsbanken-ai.vercel.app/login"
                }
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
        await client.post(
            f"{SUPABASE_URL}/auth/v1/resend",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "type": "signup",
                "email": request.email,
                "options": {
                    "email_redirect_to": "https://platsbanken-ai.vercel.app/login"
                }
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


@app.post("/api/auth/refresh")
async def refresh_auth_token(request: Request):
    """Refresh an expired access token using refresh_token."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token krävs")

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={"refresh_token": refresh_token}
        )

    if res.status_code == 200:
        data = res.json()
        return {
            "success": True,
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "user": {"id": data.get("user", {}).get("id"), "email": data.get("user", {}).get("email")}
        }

    raise HTTPException(status_code=401, detail="Kunde inte förnya session. Logga in igen.")


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
        await client.post(
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


@app.post("/api/migrate-my-data")
async def migrate_user_data(request: Request):
    """Migrate pre-defined CV data for the logged-in user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Try to get refresh_token from request body
    refresh_token = None
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        pass

    # Get user ID - try access token first, then refresh if expired
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )

        if user_response.status_code != 200 and refresh_token:
            # Access token expired - try refreshing
            refresh_response = await client.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
                headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
                json={"refresh_token": refresh_token}
            )
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                token = refresh_data.get("access_token", token)
                # Re-validate with new token
                user_response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
                )

        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session - logga in igen")
        user_id = user_response.json().get("id")

    # Pre-defined data — ALL experiences from Linnea's 8 CV PDFs
    EXPERIENCES = [
        {"user_id": user_id, "company": "Minerva University", "title": "Alumni Ambassador Western Europe", "location": "Stockholm", "dates": "Sep 2024 - Pagaende", "bullets": ["25% tjanst med sjalvstandig planering, cirka 40 timmar i manaden", "Genomfor strategisk marknadsforing genom resor till skolor och massor i Vasteuropa och Norden", "Bygger och underhaller databaser for skolkontakter, moten med SYO:er och studievagledare", "Ansvarar for logistik: bokning av flyg, hotell och transporter for stort geografiskt omrade"], "categories": ["office", "customerservice"], "sort_order": 1},
        {"user_id": user_id, "company": "House of Beans, Hotorgshallen", "title": "Forsaljare/Barista", "location": "Stockholm", "dates": "Aug 2024 - Feb 2025", "bullets": ["Sjalvstandigt butiksansvar med forsaljning av te, kaffe och choklad", "Direktforsaljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar", "Hanterade kassa, kundservice och lagerhantering"], "categories": ["restaurant", "retail"], "sort_order": 2},
        {"user_id": user_id, "company": "Profilgruppen", "title": "Anodiseringsoperator (Feriearbete)", "location": "Aseda", "dates": "Juli 2024 - Aug 2024", "bullets": ["Utforde tungt fysiskt arbete med fokus pa armlyft och materialhantering", "Arbetade pa tvaskift (06.00-14.00 och 14.00-23.00)", "Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor"], "categories": ["industry"], "sort_order": 3},
        {"user_id": user_id, "company": "Max Hamburgare", "title": "Restaurangbitrade", "location": "Vetlanda", "dates": "April 2024 - Aug 2024", "bullets": ["Arbetade i hogt tempo med drive-in, fritos, kok, servering, kassa och stad", "Levererade god kundservice och samarbetade effektivt med teamet under rusningstid"], "categories": ["restaurant"], "sort_order": 4},
        {"user_id": user_id, "company": "Keeping Tabs", "title": "Multimedia Technical Specialist", "location": "New York, USA", "dates": "Nov 2022 - Juni 2023", "bullets": ["Planerade och koordinerade konstsamling for Art Basel Hong Kong (70x30m skarm, Causeway Bay)", "Designade visuell merchandise och rullade ut forsaljnings- och logistikkampanj", "Utvecklade partnerskap med organisationer inom konstindustrin i USA", "Ansvarade for leadgenerering, orderleverans, fakturering och kundnojdhet"], "categories": ["art", "office"], "sort_order": 5},
        {"user_id": user_id, "company": "30 Campos Eliseos", "title": "Kubistisk malare", "location": "New York, USA", "dates": "2022 - 2024", "bullets": ["Scoutad som professionell kubistmalare till prestigefylld konstsamlargrupp grundad i Florens", "En av endast fem konstnarer utvalda bland 500+ sokande", "Deltog i utstallningar i New York, Dubai, Seoul, Madrid och Florens"], "categories": ["art"], "sort_order": 6},
        {"user_id": user_id, "company": "TikTok/ByteDance", "title": "Kvalitetsgranskare - Amerikanska marknaden", "location": "Nashville, USA", "dates": "Maj 2022 - Juni 2022", "bullets": ["Granskade innehallsmoderatörernas arbete for att sakerstalla att de foljer riktlinjer", "Kvalitetssakrade moderering och bidrog till forbattrade processer"], "categories": ["tech", "content"], "sort_order": 7},
        {"user_id": user_id, "company": "YouTube Ads (via Vaco)", "title": "Innehallsmoderator - Svenska marknaden", "location": "San Francisco, USA", "dates": "Feb 2022 - Juni 2022", "bullets": ["Flaggade olamplig reklam och bidrog till att utoka databaser med markerat innehall", "Foljde noggrant alla riktlinjer och samarbetade med det svenska teamet", "Deltog i regelbundna moten for att sakerstalla korrekt granskning av material"], "categories": ["tech", "content"], "sort_order": 8},
        {"user_id": user_id, "company": "Clubhouse (via Vaco)", "title": "Innehallsmoderator - Skandinaviska och amerikanska marknaden", "location": "Walnut Creek, USA", "dates": "Juni 2021 - Jan 2022", "bullets": ["Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media", "Kategorier inkluderade hatiskt tal, sexuell exploatering, valdsbejakande extremism, CSAM och falsk information", "Hade fullt ansvar for att hantera alla arenden inom svenska, norska och danska marknaden", "Identifierade brister i standardiserade arbetsrutiner och drev policyforbttringar", "Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes"], "categories": ["tech", "customerservice", "content"], "sort_order": 9},
        {"user_id": user_id, "company": "Svensk-amerikanska handelskammaren", "title": "Marknadsforing och forsaljningsutveckling", "location": "San Francisco, USA", "dates": "Juni 2021 - Sep 2021", "bullets": ["Byggde upp natverk med 100+ svenska startups, myndigheter och foretag genom konferenser och event", "Okade handelskammarens natverk med 20% genom effektiv e-post- och LinkedIn-marknadsforing", "Assisterade tva svenska konsultkunder med databas av 120 forsaljningsleads i USA", "Organiserade kraftskiva for 80 skandinaver och amerikaner i samarbete med Norska klubben"], "categories": ["office", "customerservice"], "sort_order": 10},
        {"user_id": user_id, "company": "Minerva University", "title": "Handledare for examensprojekt", "location": "San Francisco, USA", "dates": "Sep 2020 - Maj 2021", "bullets": ["Handledde 45 studenter i deras capstone-projekt inom VR, hallbart mode, varumarkesanalys och historiska romaner", "Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stod", "Gav kvalitativ och kvantitativ aterkoppling till over 90 uppgifter och 40 lektioner"], "categories": ["office", "art"], "sort_order": 11},
        {"user_id": user_id, "company": "Kvarngarden aldreboende", "title": "Timvikarie", "location": "Vetlanda", "dates": "Maj 2020 - Sep 2020", "bullets": ["Omvardnad, medicinhantering, maltidsassistans, dokumentation och emotionellt stod", "Gav omsorg till aldre personer med demens och Alzheimers sjukdom", "Foljde noggrant covid-protokoll och arbetade bade morgon- och kvallspass"], "categories": ["healthcare"], "sort_order": 12},
        {"user_id": user_id, "company": "Minerva Project", "title": "Marknadsforing/Kundservice - Global Marketing Team", "location": "Berlin & Buenos Aires", "dates": "Sep 2019 - April 2020", "bullets": ["Samarbetade med globala marknadsforingsteamet for att oka antagningen till Minerva University", "Vagledde och stottade over 2000 sokande elever via Intercom med hogkvalitativ kundservice", "Svarade pa fragor fran elever i over 40 lander genom Intercom och personliga moten", "Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet"], "categories": ["customerservice", "office"], "sort_order": 13},
        {"user_id": user_id, "company": "Google Ads (via Vaco)", "title": "Svensk innehallsanalytiker for gTech", "location": "Sunnyvale, USA / Seoul / Hyderabad", "dates": "Maj 2018 - April 2019", "bullets": ["Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak", "Utforde extraktion och granskning av innehall for over 100 annonser per dag", "Arbetade i USA och pa distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering", "Det svenska teamet uppnadde 100% mal for tjanstenivaavatalet"], "categories": ["tech", "content"], "sort_order": 14},
        {"user_id": user_id, "company": "Minerva Project - Student Experience Team", "title": "Evenemangskoordinator och elevhemsvärd", "location": "San Francisco, USA", "dates": "Sep 2017 - Maj 2018", "bullets": ["Organiserade 60 evenemang for 210 internationella studenter, 2-3 per vecka", "Ansvarade for moten, budgetkontroll, narvaro, schemalggning och marknadsforing", "Organiserade stadsskattjakt dar studenter upptackte San Francisco", "Koordinerade gastforelasare och anvande mjukvara for eventlogistik"], "categories": ["office", "customerservice"], "sort_order": 15},
        {"user_id": user_id, "company": "Wallby Sateri", "title": "Gardsvard/Receptionist", "location": "Vetlanda", "dates": "Juni 2016 - Aug 2016", "bullets": ["Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar", "Assisterade vid cafeet och bidrog till allman service"], "categories": ["reception", "customerservice"], "sort_order": 16},
        {"user_id": user_id, "company": "ICA Maxi Stormarknad", "title": "Kassapersonal, frukt och gront", "location": "Vetlanda & Varmdo", "dates": "2015, 2017, 2019", "bullets": ["Arbetade i kassan, sjalvscanningen, frukt och gront, charken och blomavdelningen", "ICA-certifierad inom kassahantering, Trygga mat och sakerhet i butik"], "categories": ["retail"], "sort_order": 17},
        {"user_id": user_id, "company": "Coffeehouse by George", "title": "Cafepersonal", "location": "Stockholm", "dates": "2014 - 2015", "bullets": ["Kassahantering och barista", "Hog serviceeniva i centralt lage"], "categories": ["restaurant"], "sort_order": 18},
        {"user_id": user_id, "company": "Siggesta Gard", "title": "Gardsvard/Tradgardsarbetare", "location": "Varmdo", "dates": "2014 - 2015", "bullets": ["Kundbemotande pa stor evenemangsanlaggning (minigolf, restauranger, konferenser, hotell)", "Overseende roll med kommunikation mellan avdelningar. Ansvarade for marknad med ~1000 besokare/sondag", "Tradgardsarbete: klippte gras, rensade ogras, planterade, skrapsortering. Korde golfbil"], "categories": ["industry", "reception"], "sort_order": 19},
    ]

    EDUCATION = [
        {"user_id": user_id, "school": "Minerva University", "degree": "B.S in Social Science, Economics and Business Administration", "location": "San Francisco, USA", "dates": "Aug 2017 - Maj 2021", "bullets": ["Varldens mest innovativa universitet enligt WURI", "Antagningsgrad pa 1.8% - mest selektiva universitetet i USA", "Studerade i fem lander: USA, Sydkorea, Indien, Tyskland och Argentina", "Handledde 45 studenter i examensprojekt inom fem amnen och branscher"], "sort_order": 1},
        {"user_id": user_id, "school": "United World College Red Cross Nordic", "degree": "International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)", "location": "Flekke, Norge", "dates": "Aug 2015 - Maj 2017", "bullets": ["Utvald som toppelev fran Sverige bland 120 sokande, fullt stipendium", "Bodde med 200 elever fran 96 olika lander med fokus pa internationell fred och forstaelse", "Roda Korsets diplom: Guldutmarkelse for teamwork, frivilligarbete och ledarskap (100+ timmar)"], "sort_order": 2},
    ]

    PROFILE = {
        "user_id": user_id,
        "full_name": "Linnea Moritz",
        "email": "linneamoritz1@gmail.com",
        "phone": "0761166109",
        "location": "Sollentuna",
        "drivers_license": True,
        "languages": ["Svenska (Modersmal)", "Engelska (Flytande)", "Tyska (grundlaggande)", "Spanska (grundlaggande)", "Mandarin (HSK niva 3)"],
        "certificates": ["B-korkort (automat)", "ICA kassahantering", "Trygga mat", "Roda Korset forsta hjalpen"],
        "about_me": "Serviceinriktad och stresstalig med bred internationell erfarenhet. Minerva University (1.8% antagning). Jobbat i 7 lander. Flytande svenska och engelska.",
    }

    SKILLS = [
        # General
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Kundservice"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Kommunikation"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Teamwork"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Stresshantering"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Svenska (Modersmal)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Engelska (Flytande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Tyska (grundlaggande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Spanska (grundlaggande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Mandarin (HSK niva 3)"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "B-korkort"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "ICA kassahantering"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "Trygga mat"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "Roda Korset forsta hjalpen"},
        # Restaurant
        {"user_id": user_id, "category": "restaurant", "skill_type": "technical", "skill_text": "Kassasystem"},
        {"user_id": user_id, "category": "restaurant", "skill_type": "technical", "skill_text": "Barista"},
        {"user_id": user_id, "category": "restaurant", "skill_type": "technical", "skill_text": "Servering"},
        {"user_id": user_id, "category": "restaurant", "skill_type": "certificate", "skill_text": "Livsmedelshygien"},
        # Tech/Content
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Content Moderation"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Trust & Safety"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Policy Compliance"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Data Analysis"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Python"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "SQL"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Tableau"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Google Analytics"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Google Ads"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Facebook Ads"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Adobe Creative Suite"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Content SEO"},
        {"user_id": user_id, "category": "tech", "skill_type": "technical", "skill_text": "Excel/Google Sheets"},
        # Customer service
        {"user_id": user_id, "category": "customerservice", "skill_type": "technical", "skill_text": "Intercom"},
        {"user_id": user_id, "category": "customerservice", "skill_type": "technical", "skill_text": "Zendesk"},
        {"user_id": user_id, "category": "customerservice", "skill_type": "technical", "skill_text": "CRM-system"},
        {"user_id": user_id, "category": "customerservice", "skill_type": "soft", "skill_text": "Problemlosning"},
        # Retail
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Kassasystem"},
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Lagerhantering"},
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Merforsaljning"},
    ]

    VOLUNTEER = [
        {"user_id": user_id, "organization": "LEAF (Living Environment and Future)", "dates": "2016 - 2017", "bullets": ["Ledde elevgrupp for att utbilda skolan i miljotank. Organiserade presentationer och kampanjer", "Skapade modemagasin for att sponsra hallbart jordbruksprojekt i Ghana. Samlade in 30,000 kr"], "sort_order": 1},
        {"user_id": user_id, "organization": "The Right Solution Project", "dates": "Mars 2013 - April 2015", "bullets": ["Tog initiativ att finansiera NGO for kvinnors utbildning vid 15 ars alder", "Samlade in over 120,000 kr genom evenemang och forsaljning", "Tillhandaholl 400+ vardpaket med hygienprodukter till etiopiska skolor. Tacktes i media tva ganger"], "sort_order": 2},
        {"user_id": user_id, "organization": "India Unlimited Utbytesprogram", "dates": "Nov 2014 - Feb 2015", "bullets": ["Deltog i EU-projekt for att framja fredliga relationer mellan Sverige och Indien", "Koordinerade hygienprojekt och fick kunskap om hallbar utveckling i utvecklingslander"], "sort_order": 3},
        {"user_id": user_id, "organization": "Varmdo Forsamling", "dates": "2012 - 2014", "bullets": ["Ledare for 3 konfirmandgrupper under 2 ar. Ledare pa tre veckors sommarlager pa Angsholmen", "Svenska Kyrkan: Ledarskapskurs steg 1 och 2"], "sort_order": 4},
    ]

    AWARDS = [
        {"user_id": user_id, "award_text": "1:a pris Stockholms Konstsalong 2024 - Jurybedomd utstallning, nominerad Publikens Favorit", "sort_order": 1},
        {"user_id": user_id, "award_text": "1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnarer, fick soloutstallning", "sort_order": 2},
        {"user_id": user_id, "award_text": "1:a pris Murrays Creative Contest 2022 - Detroit-baserad tavling med specialdesign", "sort_order": 3},
        {"user_id": user_id, "award_text": "Global Startup Weekend Stockholm - Vinnare for Terra Finance (Google for Startups & Techstars)", "sort_order": 4},
        {"user_id": user_id, "award_text": "Tredje pris Chinese Bridge - Nationell tavling i kinesiskt sprak, Bergen 2016", "sort_order": 5},
        {"user_id": user_id, "award_text": "Roda Korsets diplom - Guldutmarkelse for teamwork och ledarskap (100+ volontartimmar)", "sort_order": 6},
        {"user_id": user_id, "award_text": "Minerva University Award for Initiative 2018", "sort_order": 7},
    ]

    COVER_LETTER_PREFS = {
        "user_id": user_id,
        "tone": "professional_friendly",
        "max_words": 200,
        "greeting_style": "Hej!",
        "signature_style": "Med vanliga halsningar",
        "sign_off_name": "Linnea Moritz",
        "sign_off_phone": "076-116 61 09",
        "sign_off_email": "linneamoritz1@gmail.com",
        "always_mention": ["flexibel med tider", "korkort", "flytande engelska"],
        "never_mention": ["konst", "malning", "utstallningar", "Shopify", "e-handel", "oljemaalning", "linneamoritz.com"],
        "custom_ai_instructions": "Skriv pa naturlig, flytande svenska. Undvik AI-floskler som 'gedigen', 'brinner for', 'vittnar om'. Beratta varfor jag vill ha just det jobbet.",
    }

    JOB_PREFS = {
        "user_id": user_id,
        "preferred_locations": ["Stockholm", "Sollentuna", "Sundbyberg", "Vetlanda"],
        "search_keywords": ["servitor", "kundtjanst", "content moderator", "butik", "cafe", "reception", "lager"],
        "excluded_keywords": [],
        "excluded_companies": [],
        "job_types": ["heltid", "deltid"],
        "remote_only": False,
    }

    CV_BRANSCHER = [
        {"user_id": user_id, "bransch_id": "restaurant", "bransch_name": "Restaurang & Cafe", "focus": "Service, tempo, kundkontakt", "keywords": ["servitor", "servitris", "restaurang", "cafe", "barista", "kok"], "is_active": True, "sort_order": 1},
        {"user_id": user_id, "bransch_id": "retail", "bransch_name": "Butik & Kassa", "focus": "Forsaljning, kassa, kundservice", "keywords": ["butik", "kassa", "saljare", "ica", "coop"], "is_active": True, "sort_order": 2},
        {"user_id": user_id, "bransch_id": "customerservice", "bransch_name": "Kundtjanst & Support", "focus": "Kommunikation, problemlosning, internationell erfarenhet", "keywords": ["kundtjanst", "support", "kundservice", "helpdesk"], "is_active": True, "sort_order": 3},
        {"user_id": user_id, "bransch_id": "content", "bransch_name": "Content & Moderation", "focus": "Trust & Safety, policy, granskning", "keywords": ["moderator", "content", "review", "granskning", "trust"], "is_active": True, "sort_order": 4},
        {"user_id": user_id, "bransch_id": "tech", "bransch_name": "Tech & Kontor", "focus": "Analytiskt arbete, data, tech-bolag", "keywords": ["tech", "IT", "data", "analyst", "kontor"], "is_active": True, "sort_order": 5},
        {"user_id": user_id, "bransch_id": "industry", "bransch_name": "Industri & Tradgard", "focus": "Fysiskt arbete, skift, materialhantering", "keywords": ["industri", "lager", "produktion", "operator", "tradgard"], "is_active": True, "sort_order": 6},
        {"user_id": user_id, "bransch_id": "healthcare", "bransch_name": "Vard & Omsorg", "focus": "Omvardnad, empati, medicinhantering", "keywords": ["vard", "omsorg", "aldre", "sjukvard"], "is_active": True, "sort_order": 7},
        {"user_id": user_id, "bransch_id": "art", "bransch_name": "Konst & Kultur", "focus": "Konstnarligt arbete, utstallningar, projektledning", "keywords": ["konst", "kultur", "galleri", "museum", "kreativ"], "is_active": True, "sort_order": 8},
    ]

    CV_VERSIONS = [
        {"user_id": user_id, "vibe_id": "restaurant", "vibe_name": "Restaurang & Cafe", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Vetlanda Kommun, Ekenässjöns skola - Vetlanda
Köksbiträde | Juli – Aug 2017
● Assisterade vid matlagning och serverade mat till elever och personal.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Coffeehouse by George - Nacka
Cafépersonal | 2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "retail", "vibe_name": "Butik & Kassa", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

Coffeehouse by George - Nacka
Cafépersonal | 2014 - 2015
● Kassahantering, kundbemötande, barista, matberedning och servering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "customerservice", "vibe_name": "Kundtjanst & Support", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "content", "vibe_name": "Content & Moderation", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 – Juni 2022
● Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer.
● Kvalitetssäkrade moderering och bidrog till förbättrade processer.

YouTube Ads (via Vaco) - San Francisco, USA
Innehållsmoderator - Svenska marknaden | Feb 2022 – Juni 2022
● Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll.
● Följde noggrant alla riktlinjer och samarbetade med det svenska teamet.
● Deltog i regelbundna möten för att säkerställa korrekt granskning av material.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Svensk-amerikanska handelskammaren i San Francisco och Silicon Valley - San Francisco, USA
Marknadsföring och försäljningsutveckling | Juni 2021 – Sep 2021
● Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event.
● Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring.
● Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA.
● Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "tech", "vibe_name": "Tech & Kontor", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 – Juni 2022
● Granskade innehållsmoderatorernas arbete för att säkerställa att de följer riktlinjer.
● Kvalitetssäkrade moderering och bidrog till förbättrade processer.

YouTube Ads (via Vaco) - San Francisco, USA
Innehållsmoderator - Svenska marknaden | Feb 2022 – Juni 2022
● Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll.
● Följde noggrant alla riktlinjer och samarbetade med det svenska teamet.
● Deltog i regelbundna möten för att säkerställa korrekt granskning av material.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehållsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 – Jan 2022
● Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media.
● Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information.
● Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden.
● Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar.
● Ökade produktiviteten med 98% samtidigt som jag uppfyllde alla dagliga kvalitetsmål.

Svensk-amerikanska handelskammaren i San Francisco och Silicon Valley - San Francisco, USA
Marknadsföring och försäljningsutveckling | Juni 2021 – Sep 2021
● Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event.
● Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring.
● Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA.
● Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehållsanalytiker för gTech | Maj 2018 – April 2019
● Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk.
● Utförde extraktion och granskning av innehåll för över 100 annonser per dag.
● Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering.
● Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet; främjade positivt samarbete.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Shopify, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "industry", "vibe_name": "Industri & Tradgard", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

Profilgruppen - Åseda, Sverige
Anodiseringsoperatör (Feriearbete) | Juli 2024 – Aug 2024
● Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering.
● Arbetade på tvåskift (06.00-14.00 och 14.00-23.00), vilket visade flexibilitet och anpassningsförmåga.
● Genomgick 3-timmarsutbildning i handtravers och hanterade material.
● Samarbetade effektivt med dagligen roterande kollegor, vilket visade stark teamkänsla.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Kvarngården äldreboende - Vetlanda
Timvikarie | Maj 2020 – Sep 2020
● Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd.
● Gav omsorg till äldre personer med demens och Alzheimers sjukdom.
● Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen
Tekniska färdigheter: Python, SQL, Tableau, Google Analytics, Excel/Google Sheets

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "healthcare", "vibe_name": "Vard & Omsorg", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbiträde | April 2024 – Aug 2024
● Arbetade i högt tempo med drive-in, fritös, kök, servering, kassa och städ.
● Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

Kvarngården äldreboende - Vetlanda
Timvikarie | Maj 2020 – Sep 2020
● Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd.
● Gav omsorg till äldre personer med demens och Alzheimers sjukdom.
● Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass.

ICA Maxi Stormarknad - Vetlanda & Värmdö
Kassapersonal, frukt och grönt | 2015, 2017, 2019
● Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen.
● ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik.

Wallby Säteri - Vetlanda
Gårdsvärd/Receptionist | Juni 2016 – Aug 2016
● Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
● Assisterade vid caféet och bidrog till allmän service.

Siggesta Gård - Värmdö
Gårdsvärd/Trädgårdsarbetare | 2014 - 2015
● Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell).
● Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag.
● Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
        {"user_id": user_id, "vibe_id": "art", "vibe_name": "Konst & Kultur", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Körkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
● Världens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
● En antagningsgräns på 1.8% gör Minerva till det mest selektiva universitetet i USA.
● Studerade i fem länder under fyra år; USA, Sydkorea, Indien, Tyskland och Argentina.
● Handledde 45 studenter i deras examensprojekt inom fem olika ämnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
● Utvald som en toppelev från Sverige bland 120 sökande och fick fullt stipendium.
● Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse.
● Röda Korsets diplom; Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Linnea Moritz (linneamoritz.com) - Stockholm
Konstnär och Egenföretagare | Jan 2024 – Pågående
● Målar och säljer egna oljemålningar. 39 utställningar i 21 städer, 10 länder och 4 kontinenter.
● Vunnit tre första pris i jurybedömda konstutställningar (bl.a. Stockholms Konstsalong, Greenpoint Gallery Brooklyn).
● Driver all marknadsföring, bokföring, export, kundhantering och sociala medier självständigt.
● Förvaltar Shopify-butik med försäljning av originalkonst och konsttryck internationellt.

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 – Pågående
● 25% tjänst med självständig planering, cirka 40 timmar i månaden.
● Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden.
● Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare.
● Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område.

Keeping Tabs - New York, USA
Multimedia Technical Specialist | Nov 2022 – Juni 2023
● Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay).
● Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj.
● Utvecklade partnerskap med organisationer inom konstindustrin i USA.
● Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet.

30 Campos Eliseos - New York, USA
Kubistisk målare | 2022 – 2024
● Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens.
● En av endast fem konstnärer utvalda bland 500+ sökande.
● Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens.

Minerva University - San Francisco, USA
Handledare för examensprojekt | Sep 2020 – Maj 2021
● Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner.
● Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd.
● Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner.

Minerva Project - Berlin & Buenos Aires
Marknadsföring/Kundservice - Global Marketing Team | Sep 2019 – April 2020
● Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University.
● Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice.
● Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten.
● Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet.

Minerva Project - Student Experience Team - San Francisco, USA
Evenemangskoordinator och elevhemsvärd | Sep 2017 – Maj 2018
● Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka.
● Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring.
● Organiserade stadsskattjakt där studenter upptäckte San Francisco och utvidgade kontaktnät.
● Koordinerade gästföreläsare och använde mjukvara för eventlogistik och närvarohantering.

House of Beans, Hötorgshallen - Stockholm
Försäljare/Barista | Aug 2024 – Feb 2025
● Självständigt butiksansvar med försäljning av te, kaffe och choklad.
● Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
● Hanterade kassa, kundservice och lagerhantering.

SPRÅK & KVALIFIKATIONER
Språk: Svenska (Modersmål), Engelska (flytande), Tyska (grundläggande), Spanska (grundläggande), Mandarin (HSK nivå 3)
Certifikat: B-körkort (automat), ICA kassahantering, Trygga mat, Röda Korset första hjälpen

IDEELLT ENGAGEMANG

LEAF (Living Environment and Future) | 2016 - 2017
● Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer.
● Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr.

The Right Solution Project | Mars 2013 – April 2015
● Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder.
● Samlade in över 120,000 kr genom evenemang, konstutställningar och försäljning.
● Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger.

India Unlimited Utbytesprogram | Nov 2014 - Feb 2015
● Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien.
● Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer.

Värmdö Församling | 2012 - 2014
● Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarläger på Ängsholmen.
● Svenska Kyrkan: Ledarskapskurs steg 1 och 2.

UTMÄRKELSER
● 1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad 'Publikens Favorit'.
● 1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick solouställning.
● 1:a pris Murray's Creative Contest 2022 - Detroit-baserad tävling med specialdesign.
● Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars).
● Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016.
● Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar).
● Minerva University Award for Initiative 2018."""},
    ]

    results = {"profile": False, "experiences": 0, "education": 0, "cvs": 0, "errors": []}

    # Use service role key for DB operations (bypasses RLS)
    db_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or SUPABASE_KEY
    headers = {
        "apikey": db_key,
        "Authorization": f"Bearer {db_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        # 1. Upsert profile (on_conflict=user_id)
        try:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_profiles?on_conflict=user_id",
                headers=headers,
                json=PROFILE
            )
            if res.status_code < 400:
                results["profile"] = True
            else:
                results["errors"].append(f"Profile: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Profile error: {str(e)}")

        # 2. Delete old experiences, then batch insert
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_experiences?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_experiences",
                headers=headers,
                json=EXPERIENCES
            )
            if res.status_code < 400:
                results["experiences"] = len(EXPERIENCES)
            else:
                results["errors"].append(f"Experiences: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Experiences error: {str(e)}")

        # 3. Delete old education, then batch insert
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_education?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_education",
                headers=headers,
                json=EDUCATION
            )
            if res.status_code < 400:
                results["education"] = len(EDUCATION)
            else:
                results["errors"].append(f"Education: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Education error: {str(e)}")

        # 4. Delete old CVs, then batch insert
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_cvs?user_id=eq.{user_id}",
                headers=headers
            )
            for cv in CV_VERSIONS:
                cv["created_at"] = datetime.now().isoformat()
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_cvs",
                headers=headers,
                json=CV_VERSIONS
            )
            if res.status_code < 400:
                results["cvs"] = len(CV_VERSIONS)
            else:
                results["errors"].append(f"CVs: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"CVs error: {str(e)}")

        # 5. Delete old skills, then batch insert
        results["skills"] = 0
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_skills?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_skills",
                headers=headers,
                json=SKILLS
            )
            if res.status_code < 400:
                results["skills"] = len(SKILLS)
            else:
                results["errors"].append(f"Skills: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Skills error: {str(e)}")

        # 6. Delete old volunteer, then batch insert
        results["volunteer"] = 0
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_volunteer?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_volunteer",
                headers=headers,
                json=VOLUNTEER
            )
            if res.status_code < 400:
                results["volunteer"] = len(VOLUNTEER)
            else:
                results["errors"].append(f"Volunteer: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Volunteer error: {str(e)}")

        # 7. Delete old awards, then batch insert
        results["awards"] = 0
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_awards?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_awards",
                headers=headers,
                json=AWARDS
            )
            if res.status_code < 400:
                results["awards"] = len(AWARDS)
            else:
                results["errors"].append(f"Awards: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Awards error: {str(e)}")

        # 8. Upsert cover letter preferences
        results["cover_letter_prefs"] = False
        try:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_cover_letter_preferences?on_conflict=user_id",
                headers=headers,
                json=COVER_LETTER_PREFS
            )
            if res.status_code < 400:
                results["cover_letter_prefs"] = True
            else:
                results["errors"].append(f"Cover letter prefs: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Cover letter prefs error: {str(e)}")

        # 9. Upsert job preferences
        results["job_prefs"] = False
        try:
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_job_preferences?on_conflict=user_id",
                headers=headers,
                json=JOB_PREFS
            )
            if res.status_code < 400:
                results["job_prefs"] = True
            else:
                results["errors"].append(f"Job prefs: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Job prefs error: {str(e)}")

        # 10. Delete old branscher, then batch insert
        results["branscher"] = 0
        try:
            await client.delete(
                f"{SUPABASE_URL}/rest/v1/user_cv_branscher?user_id=eq.{user_id}",
                headers=headers
            )
            res = await client.post(
                f"{SUPABASE_URL}/rest/v1/user_cv_branscher",
                headers=headers,
                json=CV_BRANSCHER
            )
            if res.status_code < 400:
                results["branscher"] = len(CV_BRANSCHER)
            else:
                results["errors"].append(f"Branscher: {res.status_code} {res.text[:200]}")
        except Exception as e:
            results["errors"].append(f"Branscher error: {str(e)}")

    success = (results["profile"] and results["experiences"] > 0 and results["cvs"] > 0
               and results["skills"] > 0 and results["volunteer"] > 0 and results["awards"] > 0)

    # Include refreshed token so frontend can update its stored token
    response_data = {
        "success": success,
        "message": f"Migrerat! Profil: {'OK' if results['profile'] else 'FEL'}, "
                   f"Erfarenheter: {results['experiences']}/19, "
                   f"Utbildning: {results['education']}/2, "
                   f"CV:n: {results['cvs']}/8, "
                   f"Skills: {results['skills']}/{len(SKILLS)}, "
                   f"Volontar: {results['volunteer']}/4, "
                   f"Utmarkelser: {results['awards']}/7, "
                   f"Branscher: {results['branscher']}/8",
        "results": results
    }
    if not success and results["errors"]:
        response_data["errors"] = results["errors"]
    return response_data


class QuizProfileData(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[str] = None
    drivers_license: Optional[str] = None
    linkedin: Optional[str] = None
    earliest_start: Optional[str] = None
    education_level: Optional[str] = None


class UserPreferences(BaseModel):
    # Quiz fields (maps to Platsbanken data)
    search_terms: Optional[list] = None
    custom_search: Optional[str] = None
    location: Optional[list] = None
    working_hours: Optional[str] = None
    employment_form: Optional[list] = None
    duration: Optional[str] = None
    salary: Optional[str] = None
    dealbreakers: Optional[list] = None
    # Legacy fields (backwards compat)
    role_type: Optional[list] = None
    industry: Optional[list] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    skills: Optional[list] = None
    culture: Optional[list] = None
    job_titles: Optional[str] = None
    locations: Optional[str] = None
    job_types: Optional[list] = None
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None


@app.post("/api/user/profile-from-quiz")
async def save_profile_from_quiz(request: Request, profile: QuizProfileData):
    """Save personal info from onboarding quiz to user_profiles."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        # Still save locally if not logged in - data stored in localStorage
        return {"success": True, "saved_to_db": False, "reason": "not_logged_in"}

    token = auth_header.replace("Bearer ", "")

    # Get user ID
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            return {"success": True, "saved_to_db": False, "reason": "invalid_token"}

        user = user_response.json()
        user_id = user.get("id")
        user_email = user.get("email", "")

    # Build profile data for upsert
    profile_data = {
        "user_id": user_id,
        "email": user_email,
        "updated_at": datetime.now().isoformat()
    }
    if profile.full_name:
        profile_data["full_name"] = profile.full_name
    if profile.phone:
        profile_data["phone"] = profile.phone
    if profile.drivers_license:
        profile_data["drivers_license"] = profile.drivers_license != "no"
    if profile.linkedin:
        profile_data["linkedin"] = profile.linkedin

    # Store extra quiz fields in a JSONB column or as individual fields
    # age, earliest_start, education_level go into quiz_profile JSONB
    quiz_profile = {}
    if profile.age:
        quiz_profile["age"] = profile.age
    if profile.earliest_start:
        quiz_profile["earliest_start"] = profile.earliest_start
    if profile.education_level:
        quiz_profile["education_level"] = profile.education_level
    if profile.drivers_license:
        quiz_profile["drivers_license_type"] = profile.drivers_license

    # Upsert to user_profiles
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_profiles",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=profile_data
        )
        logger.info(f"Profile save: {res.status_code}")

    return {"success": True, "saved_to_db": True}


@app.get("/api/user/preferences")
async def get_user_preferences(request: Request):
    """Get user job preferences and settings."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user ID from token
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

    # Get preferences from database
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/user_job_preferences?user_id=eq.{user_id}&select=*",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {"success": True, "preferences": data[0]}

    return {"success": True, "preferences": None}


@app.post("/api/user/preferences")
async def save_user_preferences(request: Request, prefs: UserPreferences):
    """Save user job preferences and Gmail credentials."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user ID from token
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

    # Upsert preferences - store all quiz answers as JSONB
    prefs_data = {
        "user_id": user_id,
        "job_titles": prefs.custom_search if hasattr(prefs, 'custom_search') and prefs.custom_search else (
            ','.join(prefs.search_terms or prefs.role_type or []) if (prefs.search_terms or prefs.role_type) else (prefs.job_titles or '')
        ),
        "locations": ','.join(prefs.location or []) if prefs.location else (prefs.locations or ''),
        "job_types": prefs.search_terms or prefs.role_type or prefs.job_types or [],
        "experience_level": prefs.experience_level or '',
        "quiz_answers": {
            "search_terms": prefs.search_terms,
            "custom_search": getattr(prefs, 'custom_search', None),
            "location": prefs.location,
            "working_hours": prefs.working_hours,
            "employment_form": prefs.employment_form,
            "duration": prefs.duration,
            "salary": prefs.salary,
            "dealbreakers": prefs.dealbreakers
        },
        "updated_at": "now()"
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/user_job_preferences",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=prefs_data
        )

    # Save Gmail credentials if provided
    if prefs.gmail_client_id and prefs.gmail_client_secret:
        gmail_data = {
            "user_id": user_id,
            "client_id": prefs.gmail_client_id,
            "client_secret": prefs.gmail_client_secret,
            "updated_at": "now()"
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/user_google_credentials",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
                json=gmail_data
            )

    return {"success": True, "message": "Preferenser sparade!"}


class UserProfile(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin_url: str = ""
    summary: str = ""
    skills: str = ""
    experiences: list = []
    education: list = []


@app.post("/api/user/profile")
async def save_user_profile(request: Request, profile: UserProfile):
    """Save user profile and CV data."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user ID from token
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

    # Upsert user profile
    profile_data = {
        "user_id": user_id,
        "full_name": profile.full_name,
        "email": profile.email or user.get("email"),
        "phone": profile.phone,
        "linkedin_url": profile.linkedin_url,
        "summary": profile.summary,
        "updated_at": "now()"
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/user_profiles",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=profile_data
        )

    # Save skills
    if profile.skills:
        skills_list = [s.strip() for s in profile.skills.split(",") if s.strip()]
        for skill in skills_list:
            skill_data = {
                "user_id": user_id,
                "skill_name": skill
            }
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/user_skills",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "resolution=merge-duplicates"
                    },
                    json=skill_data
                )

    # Save experiences
    for exp in profile.experiences:
        exp_data = {
            "user_id": user_id,
            "company": exp.get("company", ""),
            "title": exp.get("title", ""),
            "start_date": exp.get("start_date", ""),
            "end_date": exp.get("end_date", ""),
            "description": exp.get("description", "")
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/user_experiences",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json=exp_data
            )

    # Save education
    for edu in profile.education:
        edu_data = {
            "user_id": user_id,
            "school": edu.get("school", ""),
            "degree": edu.get("degree", ""),
            "field_of_study": edu.get("field", ""),
            "start_date": edu.get("start_date", ""),
            "end_date": edu.get("end_date", "")
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/user_education",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json=edu_data
            )

    return {"success": True, "message": "Profil sparad!"}


# ============== EXPERIENCE CRUD ==============

class ExperienceData(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    categories: list = []


@app.post("/api/user/experience")
async def create_experience(request: Request, exp: ExperienceData):
    """Create a new work experience."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    exp_data = {
        "user_id": user_id,
        "company": exp.company,
        "title": exp.title,
        "location": exp.location,
        "start_date": exp.start_date,
        "end_date": exp.end_date,
        "description": exp.description,
        "categories": exp.categories
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_experiences",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=exp_data
        )
        if response.status_code in [200, 201]:
            return {"success": True, "experience": response.json()[0] if response.json() else exp_data}

    return {"success": False, "error": "Kunde inte skapa erfarenhet"}


@app.put("/api/user/experience/{exp_id}")
async def update_experience(request: Request, exp_id: str, exp: ExperienceData):
    """Update an existing work experience."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    exp_data = {
        "company": exp.company,
        "title": exp.title,
        "location": exp.location,
        "start_date": exp.start_date,
        "end_date": exp.end_date,
        "description": exp.description,
        "categories": exp.categories
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/user_experiences?id=eq.{exp_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=exp_data
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Erfarenhet uppdaterad"}

    return {"success": False, "error": "Kunde inte uppdatera erfarenhet"}


@app.delete("/api/user/experience/{exp_id}")
async def delete_experience(request: Request, exp_id: str):
    """Delete a work experience."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/user_experiences?id=eq.{exp_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Erfarenhet borttagen"}

    return {"success": False, "error": "Kunde inte ta bort erfarenhet"}


# ============== EDUCATION CRUD ==============

class EducationData(BaseModel):
    school: str = ""
    degree: str = ""
    field_of_study: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""


@app.post("/api/user/education")
async def create_education(request: Request, edu: EducationData):
    """Create a new education entry."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    edu_data = {
        "user_id": user_id,
        "school": edu.school,
        "degree": edu.degree,
        "field_of_study": edu.field_of_study,
        "location": edu.location,
        "start_date": edu.start_date,
        "end_date": edu.end_date
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_education",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=edu_data
        )
        if response.status_code in [200, 201]:
            return {"success": True, "education": response.json()[0] if response.json() else edu_data}

    return {"success": False, "error": "Kunde inte skapa utbildning"}


@app.put("/api/user/education/{edu_id}")
async def update_education(request: Request, edu_id: str, edu: EducationData):
    """Update an existing education entry."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    edu_data = {
        "school": edu.school,
        "degree": edu.degree,
        "field_of_study": edu.field_of_study,
        "location": edu.location,
        "start_date": edu.start_date,
        "end_date": edu.end_date
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/user_education?id=eq.{edu_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=edu_data
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Utbildning uppdaterad"}

    return {"success": False, "error": "Kunde inte uppdatera utbildning"}


# ============== SKILLS CRUD ==============

class SkillData(BaseModel):
    category: str = "all"
    skill_type: str = "technical"
    skill_text: str = ""


@app.post("/api/user/skill")
async def create_skill(request: Request, skill: SkillData):
    """Create a new skill entry."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    skill_data = {
        "user_id": user_id,
        "category": skill.category,
        "skill_type": skill.skill_type,
        "skill_text": skill.skill_text
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_skills",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=skill_data
        )
        if response.status_code in [200, 201]:
            return {"success": True, "skill": response.json()[0] if response.json() else skill_data}

    return {"success": False, "error": "Kunde inte skapa kompetens"}


@app.put("/api/user/skill/{skill_id}")
async def update_skill(request: Request, skill_id: str, skill: SkillData):
    """Update an existing skill entry."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    skill_data = {
        "category": skill.category,
        "skill_type": skill.skill_type,
        "skill_text": skill.skill_text
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/user_skills?id=eq.{skill_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=skill_data
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Kompetens uppdaterad"}

    return {"success": False, "error": "Kunde inte uppdatera kompetens"}


@app.delete("/api/user/skill/{skill_id}")
async def delete_skill(request: Request, skill_id: str):
    """Delete a skill entry."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/user_skills?id=eq.{skill_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Kompetens borttagen"}

    return {"success": False, "error": "Kunde inte ta bort kompetens"}


class LinkedInImport(BaseModel):
    linkedin_url: str


class CVUploadResponse(BaseModel):
    success: bool
    recommendations: list = []
    extracted_text: str = ""
    profile_data: dict = {}


@app.post("/api/cv/upload-and-analyze")
async def upload_and_analyze_cv(request: Request):
    """
    Upload CV (PDF or text) and get AI-powered job recommendations.
    Returns clickable job category suggestions based on work history.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    # Get user ID from token
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

    # Get the uploaded file content
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        # Handle file upload
        form = await request.form()
        file = form.get("file")
        if file:
            file_content = await file.read()
            # Extract text from file (PDF, DOCX, TXT, etc.)
            cv_text = extract_text_from_file(file_content, file.filename)

            if not cv_text:
                raise HTTPException(status_code=400, detail="Kunde inte extrahera text från filen")
    else:
        # Handle JSON with text content
        body = await request.json()
        cv_text = body.get("cv_text", "")

    if not cv_text or len(cv_text) < 50:
        raise HTTPException(status_code=400, detail="CV-text är för kort eller saknas")

    # Use AI to analyze CV and generate recommendations
    recommendations = await analyze_cv_with_ai(cv_text)

    # Extract profile data from CV
    profile_data = await extract_profile_from_cv(cv_text)

    # Save CV text to user profile
    await db_request("POST", "user_cv_uploads", data={
        "user_id": user_id,
        "cv_text": cv_text[:10000],  # Limit size
        "recommendations": recommendations,
        "created_at": datetime.now().isoformat()
    })

    return {
        "success": True,
        "recommendations": recommendations,
        "extracted_text": cv_text[:500] + "..." if len(cv_text) > 500 else cv_text,
        "profile_data": profile_data
    }


async def analyze_cv_with_ai(cv_text: str) -> list:
    """
    Use Claude AI to analyze CV and suggest job categories.
    Returns list of clickable recommendations.
    """
    if not ANTHROPIC_API_KEY:
        # Fallback: simple keyword matching
        return get_fallback_recommendations(cv_text)

    prompt = f"""Analysera detta CV och ge jobbförslag baserat på personens erfarenhet.

CV:
{cv_text[:3000]}

Returnera ENDAST en JSON-array med 3-6 jobbkategorier som passar denna person.
Varje objekt ska ha:
- "id": kort id (t.ex. "restaurant", "retail", "office")
- "title": svensk jobbtitel (t.ex. "Servitör/Servitris")
- "emoji": passande emoji
- "reason": en kort mening på svenska om varför detta passar (baserat på CV:t)
- "keywords": lista med sökord för Platsbanken

Exempel på format:
[
  {{"id": "restaurant", "title": "Restaurang & Café", "emoji": "🍽️", "reason": "Du har erfarenhet från Max Hamburgare och kafé", "keywords": ["servitör", "restaurang", "café", "barista"]}},
  {{"id": "retail", "title": "Butik & Försäljning", "emoji": "🛒", "reason": "Du har jobbat i butik tidigare", "keywords": ["butik", "försäljare", "kassa"]}}
]

Svara ENDAST med JSON-arrayen, inget annat."""

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
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                text = result["content"][0]["text"].strip()
                # Parse JSON from response
                import json
                # Find JSON array in response
                start = text.find('[')
                end = text.rfind(']') + 1
                if start >= 0 and end > start:
                    recommendations = json.loads(text[start:end])
                    return recommendations

    except Exception as e:
        logger.error(f"AI analysis error: {e}")

    return get_fallback_recommendations(cv_text)


def get_fallback_recommendations(cv_text: str) -> list:
    """Fallback keyword-based recommendations when AI is unavailable"""
    text_lower = cv_text.lower()
    recommendations = []

    # Check for different job categories
    categories = [
        {
            "id": "restaurant",
            "title": "Restaurang & Café",
            "emoji": "🍽️",
            "keywords": ["servitör", "servitris", "restaurang", "café", "kafe", "barista", "kök", "kock", "mat", "dryck", "max", "mcdonalds", "espresso"],
            "search_keywords": ["servitör", "restaurang", "café", "barista"]
        },
        {
            "id": "retail",
            "title": "Butik & Försäljning",
            "emoji": "🛒",
            "keywords": ["butik", "kassa", "försäljare", "säljare", "ica", "coop", "handel", "lager"],
            "search_keywords": ["butik", "försäljare", "kassa", "säljare"]
        },
        {
            "id": "customerservice",
            "title": "Kundtjänst",
            "emoji": "💬",
            "keywords": ["kundtjänst", "support", "telefon", "chat", "kundservice", "ärenden", "helpdesk"],
            "search_keywords": ["kundtjänst", "support", "kundservice"]
        },
        {
            "id": "office",
            "title": "Kontor & Admin",
            "emoji": "💼",
            "keywords": ["kontor", "admin", "assistent", "koordinator", "planering", "excel", "word"],
            "search_keywords": ["administratör", "kontorsassistent", "koordinator"]
        },
        {
            "id": "tech",
            "title": "IT & Tech",
            "emoji": "💻",
            "keywords": ["utvecklare", "programmering", "it", "tech", "data", "python", "javascript", "react", "webb"],
            "search_keywords": ["utvecklare", "IT", "webbutvecklare", "data"]
        },
        {
            "id": "healthcare",
            "title": "Vård & Omsorg",
            "emoji": "🏥",
            "keywords": ["vård", "omsorg", "sjukvård", "äldreboende", "hemtjänst", "undersköterska"],
            "search_keywords": ["undersköterska", "vårdbiträde", "omsorg"]
        },
        {
            "id": "warehouse",
            "title": "Lager & Logistik",
            "emoji": "📦",
            "keywords": ["lager", "logistik", "truck", "plock", "packa", "leverans", "transport"],
            "search_keywords": ["lager", "logistik", "truckförare"]
        },
        {
            "id": "cleaning",
            "title": "Städ & Fastighet",
            "emoji": "🧹",
            "keywords": ["städ", "städare", "fastighet", "vaktmästare", "lokalvård"],
            "search_keywords": ["städare", "lokalvårdare", "fastighet"]
        }
    ]

    for cat in categories:
        matches = sum(1 for kw in cat["keywords"] if kw in text_lower)
        if matches >= 1:
            recommendations.append({
                "id": cat["id"],
                "title": cat["title"],
                "emoji": cat["emoji"],
                "reason": f"Matchar {matches} nyckelord i ditt CV",
                "keywords": cat["search_keywords"],
                "match_score": matches
            })

    # Sort by match score and take top 5
    recommendations.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    # If no matches, add general recommendations
    if not recommendations:
        recommendations = [
            {"id": "general", "title": "Allmänt", "emoji": "🔍", "reason": "Öppen för alla typer av jobb", "keywords": ["jobb"]},
            {"id": "customerservice", "title": "Kundtjänst", "emoji": "💬", "reason": "Passar många profiler", "keywords": ["kundtjänst"]},
            {"id": "retail", "title": "Butik", "emoji": "🛒", "reason": "Många lediga tjänster", "keywords": ["butik"]}
        ]

    return recommendations[:6]


async def extract_profile_from_cv(cv_text: str) -> dict:
    """Extract basic profile info from CV text"""
    profile = {}

    # Try to extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', cv_text)
    if email_match:
        profile["email"] = email_match.group()

    # Try to extract phone (Swedish format)
    phone_match = re.search(r'(?:0|\+46)[0-9\s-]{8,12}', cv_text)
    if phone_match:
        profile["phone"] = phone_match.group().strip()

    # Try to extract name (first line often contains name)
    lines = cv_text.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        # If first line looks like a name (2-4 words, capitalized)
        words = first_line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            profile["full_name"] = first_line

    return profile


@app.post("/api/user/import-linkedin")
async def import_from_linkedin(request: Request, data: LinkedInImport):
    """
    Import profile data from LinkedIn URL.
    Note: This is a placeholder - actual LinkedIn scraping requires OAuth or paid API.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # Validate LinkedIn URL
    if "linkedin.com/in/" not in data.linkedin_url:
        return {
            "success": False,
            "message": "Ogiltig LinkedIn-URL. Använd formatet: linkedin.com/in/ditt-namn"
        }

    # For now, return a message that manual import is needed
    # In production, you would use LinkedIn API or a scraping service
    return {
        "success": False,
        "message": "Automatisk LinkedIn-import är inte tillgänglig just nu. Fyll i din profil manuellt eller exportera din LinkedIn-data och ladda upp."
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


# ============== GMAIL OAUTH (App credentials shared, user tokens in Supabase) ==============

@app.get("/api/gmail/auth-url")
async def get_gmail_auth_url(user_id: str = "default_user", redirect_uri: str = None):
    """
    Get Google OAuth URL for user to authorize Gmail access.
    Uses app-level credentials (GMAIL_CLIENT_ID env var).
    """
    if not GMAIL_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Gmail integration not configured. Set GMAIL_CLIENT_ID in env vars.")

    if not redirect_uri:
        base = os.getenv("VERCEL_URL", "http://localhost:8000")
        if base and not base.startswith("http"):
            base = f"https://{base}"
        redirect_uri = f"{base}/api/gmail/callback"

    params = {
        "client_id": GMAIL_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.compose",
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"success": True, "auth_url": auth_url, "redirect_uri": redirect_uri}


@app.get("/api/gmail/callback")
async def gmail_oauth_callback(code: str, state: str = "default_user"):
    """Handle OAuth callback. Exchange code for tokens using app credentials."""
    if not all([GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET]):
        raise HTTPException(status_code=500, detail="Gmail integration not configured.")

    user_id = state
    base = os.getenv("VERCEL_URL", "http://localhost:8000")
    if base and not base.startswith("http"):
        base = f"https://{base}"
    redirect_uri = f"{base}/api/gmail/callback"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GMAIL_CLIENT_ID,
                "client_secret": GMAIL_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(status_code=400, detail="Kunde inte byta kod mot token. Försök igen.")

        tokens = response.json()

        profile_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        gmail_address = profile_response.json().get("email", "")

    expires_at = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))

    # Upsert — create or update
    existing = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    token_data = {
        "user_id": user_id,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "token_expires_at": expires_at.isoformat(),
        "gmail_address": gmail_address,
        "is_connected": True,
        "updated_at": datetime.now().isoformat()
    }
    if existing:
        await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data=token_data)
    else:
        await db_request("POST", "user_google_credentials", data=token_data)

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head><title>Gmail kopplad!</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #f0fdf4;">
        <h1 style="color: #16a34a;">Gmail kopplad!</h1>
        <p>Ditt Gmail-konto ({gmail_address}) är nu kopplat.</p>
        <p>Du kan stänga det här fönstret och gå tillbaka till appen.</p>
        <script>setTimeout(() => window.close(), 2000);</script>
    </body>
    </html>
    """)


@app.get("/api/gmail/status")
async def get_gmail_status(user_id: str = "default_user"):
    """Check if user has Gmail connected"""
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds or not creds[0].get("is_connected"):
        return {"connected": False, "gmail_address": None, "app_configured": bool(GMAIL_CLIENT_ID)}
    cred = creds[0]
    return {
        "connected": True,
        "gmail_address": cred.get("gmail_address"),
        "app_configured": bool(GMAIL_CLIENT_ID)
    }


@app.post("/api/gmail/disconnect")
async def disconnect_gmail(user_id: str = "default_user"):
    """
    Revoke Gmail access and delete all stored tokens for this user.
    GDPR: user has the right to withdraw consent at any time.
    """
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds:
        return {"success": True, "message": "Ingen Gmail-koppling hittades."}

    cred = creds[0]
    access_token = cred.get("access_token")
    refresh_token = cred.get("refresh_token")

    # Revoke token at Google — this invalidates all tokens for this app+user combo
    token_to_revoke = access_token or refresh_token
    if token_to_revoke:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": token_to_revoke},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
                # Google returns 200 on success, 400 if already revoked — both are fine
        except Exception as e:
            logger.warning(f"Could not revoke token at Google: {e}")

    # Delete all stored credentials from Supabase
    await db_request("DELETE", f"user_google_credentials?user_id=eq.{user_id}")

    logger.info(f"Gmail disconnected for user {user_id}")
    return {"success": True, "message": "Gmail frånkopplat. Appen har inte längre åtkomst till din Gmail."}


async def refresh_gmail_token(user_id: str) -> Optional[str]:
    """Get a valid Gmail access token for this user, refreshing if needed."""
    if not all([GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET]):
        return None

    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds or not creds[0].get("is_connected"):
        return None

    cred = creds[0]

    # Return existing token if still valid (with 5-min buffer)
    expires_at = cred.get("token_expires_at")
    if expires_at:
        try:
            exp_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            buffer = timedelta(minutes=5)
            if exp_time.tzinfo:
                from datetime import timezone
                if exp_time > datetime.now(timezone.utc) + buffer:
                    return cred.get("access_token")
            else:
                if exp_time > datetime.now() + buffer:
                    return cred.get("access_token")
        except (ValueError, TypeError):
            pass

    # Refresh using app credentials
    refresh_token = cred.get("refresh_token")
    if not refresh_token:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GMAIL_CLIENT_ID,
                "client_secret": GMAIL_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            },
            timeout=10
        )
        if response.status_code != 200:
            logger.error(f"Token refresh failed for user {user_id}: {response.text}")
            return None

        tokens = response.json()
        expires_at = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
        await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data={
            "access_token": tokens["access_token"],
            "token_expires_at": expires_at.isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        return tokens["access_token"]


def generate_cover_letter_pdf(
    text: str,
    sender_name: str = "Linnea Moritz",
    sender_phone: str = "0761166109",
    sender_email: str = "linneamoritzCV@gmail.com",
    sender_location: str = "Sollentuna",
    job_title: str = "",
    company: str = "",
) -> bytes:
    """
    Generate a professional Swedish business letter PDF.
    Layout: sender info top-right, date + recipient + subject left, body text.
    Matches the v1 design (job_portal_backend.py) ported to ReportLab.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.units import cm
    from io import BytesIO
    from datetime import datetime as dt

    buffer = BytesIO()
    c = rl_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 2.5 * cm
    right_margin = 2.5 * cm
    top_margin = 2.5 * cm
    y = height - top_margin

    # === AVSÄNDARE — top right ===
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - right_margin, y, sender_name)
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawRightString(width - right_margin, y, sender_location)
    y -= 14
    c.drawRightString(width - right_margin, y, sender_phone)
    y -= 14
    c.drawRightString(width - right_margin, y, sender_email)
    y -= 30

    # === DATUM — left ===
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, y, dt.now().strftime("%Y-%m-%d"))
    y -= 30

    # === MOTTAGARE — left ===
    if company:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, company)
        y -= 40

    # === ÄMNESRAD ===
    if job_title:
        c.setFont("Helvetica-Bold", 12)
        subject_label = f"Ans\u00f6kan: {job_title}"
        c.drawString(left_margin, y, subject_label)
        y -= 30

    # === BRÖDTEXT ===
    c.setFont("Helvetica", 11)
    max_width = width - left_margin - right_margin
    line_height = 16

    for paragraph in text.split("\n"):
        if paragraph.strip():
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if c.stringWidth(test_line, "Helvetica", 11) < max_width:
                    line = test_line
                else:
                    c.drawString(left_margin, y, line.strip())
                    y -= line_height
                    line = word + " "
                    if y < 3 * cm:
                        c.showPage()
                        y = height - top_margin
                        c.setFont("Helvetica", 11)
            if line:
                c.drawString(left_margin, y, line.strip())
                y -= line_height
        else:
            y -= 10  # paragraph spacing

        if y < 3 * cm:
            c.showPage()
            y = height - top_margin
            c.setFont("Helvetica", 11)

    c.save()
    buffer.seek(0)
    return buffer.read()


async def create_gmail_draft_for_user(
    user_id: str,
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[Dict]] = None  # [{"filename": "...", "data": bytes}]
) -> Optional[str]:
    """Create a Gmail draft with optional PDF attachments. Returns draft ID or None."""
    access_token = await refresh_gmail_token(user_id)
    if not access_token:
        return None
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        msg = MIMEMultipart()
        msg["to"] = to_email
        msg["subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        for att in (attachments or []):
            part = MIMEBase("application", "octet-stream")
            part.set_payload(att["data"])
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=att["filename"])
            msg.attach(part)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={"message": {"raw": raw}},
                timeout=20
            )
            if resp.status_code in [200, 201]:
                return resp.json().get("id")
            logger.error(f"Draft creation failed: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"Gmail draft error: {e}")
    return None


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
    except Exception:
        pass
    return "<h1>Integritetspolicy kunde inte laddas</h1>"


# ============== AI FEEDBACK ==============

class AIFeedback(BaseModel):
    feedback_text: str
    feedback_type: str = "cover_letter"  # cover_letter, new_vibe_request, exclude_jobs, general
    applies_to_vibes: Optional[List[str]] = None


@app.post("/api/user/ai-feedback")
async def save_ai_feedback(request: Request, feedback: AIFeedback):
    """Save user feedback for AI cover letter generation."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    feedback_data = {
        "user_id": user_id,
        "feedback_text": feedback.feedback_text,
        "feedback_type": feedback.feedback_type,
        "applies_to_vibes": feedback.applies_to_vibes,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_ai_feedback",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=feedback_data
        )

        if response.status_code >= 400:
            logger.error(f"Failed to save feedback: {response.text}")
            return {"success": False, "message": "Kunde inte spara feedback"}

    return {"success": True, "message": "Feedback sparad!"}


@app.get("/api/user/ai-feedback")
async def get_ai_feedback(request: Request):
    """Get all AI feedback for user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/user_ai_feedback?user_id=eq.{user_id}&is_active=eq.true&order=created_at.desc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        if response.status_code >= 400:
            return {"success": False, "feedback": []}

        return {"success": True, "feedback": response.json()}


# ============== GDPR ==============

@app.get("/api/user/export-data")
async def export_user_data_gdpr(request: Request):
    """Export all user data as JSON (GDPR Article 20)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user = user_response.json()
        user_id = user.get("id")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    export_data = {
        "user": {"id": user_id, "email": user.get("email")},
        "exported_at": datetime.now().isoformat()
    }

    async with httpx.AsyncClient() as client:
        # Profile
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_profiles?user_id=eq.{user_id}", headers=headers)
        export_data["profile"] = res.json() if res.status_code < 400 else []

        # Experiences
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_experiences?user_id=eq.{user_id}", headers=headers)
        export_data["experiences"] = res.json() if res.status_code < 400 else []

        # Education
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_education?user_id=eq.{user_id}", headers=headers)
        export_data["education"] = res.json() if res.status_code < 400 else []

        # Skills
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_skills?user_id=eq.{user_id}", headers=headers)
        export_data["skills"] = res.json() if res.status_code < 400 else []

        # CVs
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_cvs?user_id=eq.{user_id}", headers=headers)
        export_data["cvs"] = res.json() if res.status_code < 400 else []

        # Job preferences
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_job_preferences?user_id=eq.{user_id}", headers=headers)
        export_data["job_preferences"] = res.json() if res.status_code < 400 else []

        # Applications
        res = await client.get(f"{SUPABASE_URL}/rest/v1/applications?user_id=eq.{user_id}", headers=headers)
        export_data["applications"] = res.json() if res.status_code < 400 else []

        # AI Feedback
        res = await client.get(f"{SUPABASE_URL}/rest/v1/user_ai_feedback?user_id=eq.{user_id}", headers=headers)
        export_data["ai_feedback"] = res.json() if res.status_code < 400 else []

    return {"success": True, "data": export_data}


@app.delete("/api/user/delete-account")
async def delete_user_account(request: Request):
    """Delete all user data and account (GDPR Article 17)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig session")
        user_id = user_response.json().get("id")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    deleted = []

    async with httpx.AsyncClient() as client:
        # Delete all user data from tables
        tables = [
            "user_ai_feedback",
            "applications",
            "user_cvs",
            "user_skills",
            "user_education",
            "user_experiences",
            "user_job_preferences",
            "user_gmail_credentials",
            "user_profiles"
        ]

        for table in tables:
            res = await client.delete(
                f"{SUPABASE_URL}/rest/v1/{table}?user_id=eq.{user_id}",
                headers=headers
            )
            if res.status_code < 400:
                deleted.append(table)

    return {
        "success": True,
        "message": "Ditt konto och all data har raderats.",
        "deleted_from": deleted
    }


@app.get("/account", response_class=HTMLResponse)
async def account_page():
    """Account settings page"""
    try:
        account_path = pathlib.Path(__file__).parent.parent / "account.html"
        if account_path.exists():
            return account_path.read_text(encoding='utf-8')
    except Exception:
        pass
    return "<h1>Kontosidan kunde inte laddas</h1>"


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend"""
    return get_frontend_html()


# ============== ADMIN ENDPOINTS (for debugging Supabase data) ==============

@app.get("/api/admin/schema")
async def admin_schema():
    """Check which tables exist in Supabase and their row counts."""
    tables = [
        "user_profiles", "user_experiences", "user_education", "user_skills",
        "user_cvs", "user_cv_branscher", "user_cover_letter_preferences",
        "user_job_preferences", "user_ai_feedback", "user_volunteer",
        "user_awards", "user_experience_tags", "user_google_credentials",
        "applications", "jobs", "master_cv_exports", "cv_industry_templates",
        "artist_exhibitions", "artist_residencies", "artist_collections",
        "tech_projects", "tech_certifications", "academic_publications"
    ]
    result = {}
    for table in tables:
        rows = await db_request("GET", table, params={"select": "count", "limit": "0"})
        if rows is not None:
            # Try to get actual count
            all_rows = await db_request("GET", table, params={"select": "*"})
            result[table] = {"exists": True, "row_count": len(all_rows) if all_rows else 0}
        else:
            result[table] = {"exists": False, "row_count": 0}
    return {"tables": result, "supabase_connected": bool(SUPABASE_URL and SUPABASE_KEY)}


@app.get("/api/admin/user/{email}")
async def admin_user_data(email: str):
    """Get ALL data for a user by email. Shows exactly what's in Supabase."""
    # Find user profile by email
    profiles = await db_request("GET", "user_profiles", params={"email": f"eq.{email}"})
    if not profiles:
        return {"error": f"No profile found for {email}", "profiles_table_check": await db_request("GET", "user_profiles", params={"select": "*"})}

    profile = profiles[0]
    user_id = profile.get("user_id")

    # Fetch ALL related data
    experiences = await db_request("GET", "user_experiences", params={"user_id": f"eq.{user_id}", "order": "sort_order"}) or []
    education = await db_request("GET", "user_education", params={"user_id": f"eq.{user_id}", "order": "sort_order"}) or []
    skills = await db_request("GET", "user_skills", params={"user_id": f"eq.{user_id}"}) or []
    cvs = await db_request("GET", "user_cvs", params={"user_id": f"eq.{user_id}"}) or []
    branscher = await db_request("GET", "user_cv_branscher", params={"user_id": f"eq.{user_id}"}) or []
    cover_prefs = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"}) or []
    job_prefs = await db_request("GET", "user_job_preferences", params={"user_id": f"eq.{user_id}"}) or []
    volunteer = await db_request("GET", "user_volunteer", params={"user_id": f"eq.{user_id}"}) or []
    awards = await db_request("GET", "user_awards", params={"user_id": f"eq.{user_id}"}) or []
    applications = await db_request("GET", "applications", params={"user_id": f"eq.{user_id}"}) or []
    ai_feedback = await db_request("GET", "user_ai_feedback", params={"user_id": f"eq.{user_id}"}) or []

    return {
        "user_id": user_id,
        "email": email,
        "profile": profile,
        "data_counts": {
            "experiences": len(experiences),
            "education": len(education),
            "skills": len(skills),
            "cvs": len(cvs),
            "cv_vibes": [cv.get("vibe_id") for cv in cvs],
            "branscher": len(branscher),
            "cover_letter_prefs": len(cover_prefs),
            "job_prefs": len(job_prefs),
            "volunteer": len(volunteer),
            "awards": len(awards),
            "applications": len(applications),
            "ai_feedback": len(ai_feedback),
        },
        "experiences": experiences,
        "education": education,
        "skills": skills,
        "cvs": [{"vibe_id": cv.get("vibe_id"), "vibe_name": cv.get("vibe_name"), "text_length": len(cv.get("cv_text", ""))} for cv in cvs],
        "branscher": branscher,
        "cover_letter_prefs": cover_prefs,
        "job_prefs": job_prefs,
        "volunteer": volunteer,
        "awards": awards,
    }


@app.get("/api/admin/migration-status")
async def admin_migration_status():
    """Quick check: is Linnea's data migrated? Returns what's missing."""
    profiles = await db_request("GET", "user_profiles", params={"email": "eq.linneamoritz1@gmail.com"})
    if not profiles:
        return {
            "migrated": False,
            "status": "NO PROFILE FOUND",
            "action_needed": "Run POST /api/migrate-my-data (with auth) or run v2/migrate_user_data.py"
        }

    user_id = profiles[0].get("user_id")
    experiences = await db_request("GET", "user_experiences", params={"user_id": f"eq.{user_id}", "select": "company"}) or []
    education = await db_request("GET", "user_education", params={"user_id": f"eq.{user_id}", "select": "school"}) or []
    skills = await db_request("GET", "user_skills", params={"user_id": f"eq.{user_id}", "select": "skill_text"}) or []
    cvs = await db_request("GET", "user_cvs", params={"user_id": f"eq.{user_id}", "select": "vibe_id"}) or []
    volunteer = await db_request("GET", "user_volunteer", params={"user_id": f"eq.{user_id}", "select": "organization"}) or []
    awards = await db_request("GET", "user_awards", params={"user_id": f"eq.{user_id}", "select": "award_text"}) or []

    expected_cvs = {"restaurant", "retail", "customerservice", "content", "tech", "industry", "healthcare", "art"}
    actual_cvs = {cv.get("vibe_id") for cv in cvs}
    missing_cvs = expected_cvs - actual_cvs

    expected_companies = {
        "Minerva University", "House of Beans", "Max Hamburgare", "Clubhouse",
        "Google Ads (via Vaco)", "Minerva Project", "ICA Maxi", "Coffeehouse by George",
        "TikTok/ByteDance", "YouTube Ads (via Vaco)", "Profilgruppen",
        "Kvarngarden aldreboende", "Wallby Sateri", "Siggesta Gard",
        "Svensk-amerikanska handelskammaren", "Keeping Tabs", "30 Campos Eliseos",
        "Minerva Project - Student Experience Team"
    }
    actual_companies = {exp.get("company") for exp in experiences}

    return {
        "migrated": True,
        "user_id": user_id,
        "profile": "OK",
        "experiences": {"count": len(experiences), "companies": sorted(actual_companies)},
        "education": {"count": len(education), "schools": [e.get("school") for e in education]},
        "skills": {"count": len(skills)},
        "cvs": {
            "count": len(cvs),
            "vibes": sorted(actual_cvs),
            "missing": sorted(missing_cvs) if missing_cvs else "ALL 8 PRESENT"
        },
        "volunteer": {"count": len(volunteer)},
        "awards": {"count": len(awards)},
        "completeness": {
            "has_all_8_cvs": len(missing_cvs) == 0,
            "has_all_experiences": len(experiences) >= 18,
            "has_uwc_education": any("United World College" in e.get("school", "") for e in education),
            "has_skills": len(skills) >= 16,
            "has_volunteer": len(volunteer) >= 4,
            "has_awards": len(awards) >= 7,
        }
    }


# ============== TEXT EXTRACTION HELPERS ==============

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from file based on extension"""
    filename_lower = filename.lower()

    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename_lower.endswith('.txt'):
        try:
            return file_content.decode('utf-8')
        except:
            return file_content.decode('latin-1', errors='ignore')
    elif filename_lower.endswith('.rtf'):
        # RTF is complex - for now just try to decode as text
        # TODO: Add proper RTF parser
        try:
            return file_content.decode('utf-8', errors='ignore')
        except:
            return ""
    else:
        logger.warning(f"No text extraction for file type: {filename}")
        return ""


# ============== FILE UPLOAD ENDPOINTS ==============

@app.post("/api/upload/cv/{vibe_id}")
async def upload_cv(vibe_id: str, request: Request):
    """Upload CV in various formats (PDF, DOCX, DOC, TXT, RTF, ODT)"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    token = auth_header.replace("Bearer ", "")

    # Verify user via Supabase auth
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = user_response.json().get("id")

    # Get file from request
    form = await request.form()
    file = form.get("file")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Determine file extension and content type
    filename = file.filename.lower()
    ext = "pdf"  # default
    content_type = "application/pdf"

    if filename.endswith(".pdf"):
        ext, content_type = "pdf", "application/pdf"
    elif filename.endswith(".docx"):
        ext, content_type = "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".doc"):
        ext, content_type = "doc", "application/msword"
    elif filename.endswith(".txt"):
        ext, content_type = "txt", "text/plain"
    elif filename.endswith(".rtf"):
        ext, content_type = "rtf", "application/rtf"
    elif filename.endswith(".odt"):
        ext, content_type = "odt", "application/vnd.oasis.opendocument.text"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, DOCX, DOC, TXT, RTF, or ODT")

    # Read file content
    file_content = await file.read()

    # Upload to Supabase Storage
    file_path = f"{user_id}/{vibe_id}_cv.{ext}"

    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/cv-files/{file_path}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            content=file_content,
            timeout=30
        )

        if upload_response.status_code not in [200, 201]:
            logger.error(f"Storage upload failed: {upload_response.status_code} - {upload_response.text}")
            raise HTTPException(status_code=500, detail="Failed to upload file")

    # Get public URL
    pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/cv-files/{file_path}"

    # Extract text from file
    cv_text = extract_text_from_file(file_content, file.filename)

    if not cv_text:
        logger.warning(f"Could not extract text from {file.filename}")

    # Update user_cvs table with pdf_url and cv_text
    update_result = await db_request(
        "PATCH",
        "user_cvs",
        params={"user_id": f"eq.{user_id}", "vibe_id": f"eq.{vibe_id}"},
        data={
            "pdf_url": pdf_url,
            "cv_text": cv_text[:50000] if cv_text else None  # Limit text size
        }
    )

    if not update_result or len(update_result) == 0:
        # If no existing record, create one
        vibe_names = {
            "restaurant": "Restaurang & Café",
            "retail": "Butik & Kassa",
            "customerservice": "Kundtjänst & Support",
            "tech": "Tech & Kontor",
            "healthcare": "Vård & Omsorg",
            "industry": "Trädgård & Industri",
            "reception": "Hotell & Reception",
            "contentmoderation": "Content & Moderation"
        }

        await db_request(
            "POST",
            "user_cvs",
            data={
                "user_id": user_id,
                "vibe_id": vibe_id,
                "vibe_name": vibe_names.get(vibe_id, vibe_id),
                "pdf_url": pdf_url,
                "cv_text": cv_text[:50000] if cv_text else None
            }
        )

    return {
        "success": True,
        "pdf_url": pdf_url,
        "vibe_id": vibe_id
    }


@app.post("/api/upload/profile-photo")
async def upload_profile_photo(request: Request):
    """Upload profile photo"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    token = auth_header.replace("Bearer ", "")

    # Verify user via Supabase auth
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = user_response.json().get("id")

    # Get file from request
    form = await request.form()
    file = form.get("file")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read file content
    file_content = await file.read()

    # Determine file extension
    filename = file.filename.lower()
    ext = "jpg"
    content_type = "image/jpeg"

    if filename.endswith(".png"):
        ext = "png"
        content_type = "image/png"
    elif filename.endswith(".jpeg") or filename.endswith(".jpg"):
        ext = "jpg"
        content_type = "image/jpeg"

    # Upload to Supabase Storage (upsert to handle re-uploads)
    file_path = f"{user_id}/profile.{ext}"

    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/profile-photos/{file_path}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            content=file_content,
            timeout=30
        )

        if upload_response.status_code not in [200, 201]:
            logger.error(f"Storage upload failed: {upload_response.status_code} - {upload_response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {upload_response.text[:200]}")

    # Get public URL
    photo_url = f"{SUPABASE_URL}/storage/v1/object/public/profile-photos/{file_path}"

    # Upsert user_profiles table (create row if not exists)
    # First try PATCH
    update_response = await db_request(
        "PATCH",
        "user_profiles",
        params={"user_id": f"eq.{user_id}"},
        data={"photo_url": photo_url}
    )

    # If PATCH returned empty (no row existed), create one
    # full_name defaults to "" to satisfy NOT NULL constraint
    if not update_response or len(update_response) == 0:
        await db_request(
            "POST",
            "user_profiles",
            data={"user_id": user_id, "photo_url": photo_url, "full_name": ""}
        )

    return {
        "success": True,
        "photo_url": photo_url
    }


@app.get("/api/profile")
async def get_profile(request: Request):
    """Get user profile data (photo URL, training letter status)"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig token")
        user_data = user_response.json()
        user_id = user_data.get("id")
        user_email = user_data.get("email")

    # Get profile from user_profiles
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    profile = profiles[0] if profiles else {}

    # Check if any training letters exist
    letters = await db_request("GET", "user_training_letters", params={
        "user_id": f"eq.{user_id}", "select": "id"
    }) or []

    # Check uploaded CVs
    cv_uploads = await db_request("GET", "user_cv_uploads", params={
        "user_id": f"eq.{user_id}", "select": "id"
    }) or []

    return {
        "profile_photo_url": profile.get("photo_url"),
        "full_name": profile.get("full_name", ""),
        "email": user_email or profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "location": profile.get("location", ""),
        "email_signature": profile.get("email_signature", ""),
        "training_letter_analyzed": len(letters) > 0,
        "training_letter_count": len(letters),
        "cv_uploaded": len(cv_uploads) > 0,
        "cv_count": len(cv_uploads)
    }


@app.patch("/api/profile/signature")
async def update_email_signature(request: Request):
    """Save the user's custom email signature."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ej inloggad")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Ogiltig token")
        user_id = user_response.json().get("id")

    body = await request.json()
    signature = body.get("signature", "")

    result = await db_request(
        "PATCH",
        f"user_profiles?user_id=eq.{user_id}",
        data={"email_signature": signature, "updated_at": datetime.now().isoformat()}
    )
    if not result:
        # No row yet — create one
        await db_request("POST", "user_profiles", data={
            "user_id": user_id,
            "full_name": "",
            "email_signature": signature
        })

    return {"success": True}


@app.post("/api/upload/training-letter")
async def upload_training_letter(request: Request):
    """Upload training letter PDF and analyze tone/style"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    token = auth_header.replace("Bearer ", "")

    # Verify user via Supabase auth
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = user_response.json().get("id")

    # Get file from request
    form = await request.form()
    file = form.get("file")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read file content
    file_content = await file.read()

    # Extract text from file
    letter_text = extract_text_from_file(file_content, file.filename)

    if not letter_text:
        logger.warning(f"Could not extract text from training letter: {file.filename}")
        letter_text = "[Kunde inte extrahera text från filen]"

    # Upload to Supabase Storage
    import time
    timestamp = int(time.time())

    # Determine file extension and content type
    filename_lower = file.filename.lower()
    file_ext = filename_lower.split('.')[-1] if '.' in filename_lower else 'pdf'

    content_type_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        'odt': 'application/vnd.oasis.opendocument.text'
    }
    content_type = content_type_map.get(file_ext, 'application/pdf')

    file_path = f"{user_id}/training_letter_{timestamp}.{file_ext}"

    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/training-letters/{file_path}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            content=file_content,
            timeout=30
        )

        if upload_response.status_code not in [200, 201]:
            logger.error(f"Storage upload failed: {upload_response.status_code} - {upload_response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to upload letter: {upload_response.text[:200]}")

    # Analyze tone/style with Claude if we have text
    tone_analysis = None
    if letter_text and not letter_text.startswith("[PDF-fil"):
        tone_analysis = await analyze_writing_tone(letter_text)

    # Get or create user preferences
    prefs_data = await db_request(
        "GET",
        "user_cover_letter_preferences",
        params={"user_id": f"eq.{user_id}"}
    )

    existing_prefs = prefs_data[0] if prefs_data and len(prefs_data) > 0 else None

    # Update preferences with tone analysis
    if tone_analysis:
        if existing_prefs:
            # Update existing
            await db_request(
                "PATCH",
                "user_cover_letter_preferences",
                params={"user_id": f"eq.{user_id}"},
                data={
                    "tone": tone_analysis.get("tone"),
                    "always_mention": tone_analysis.get("favorite_phrases", [])
                }
            )
        else:
            # Create new
            await db_request(
                "POST",
                "user_cover_letter_preferences",
                data={
                    "user_id": user_id,
                    "tone": tone_analysis.get("tone"),
                    "always_mention": tone_analysis.get("favorite_phrases", [])
                }
            )

    return {
        "success": True,
        "file_path": file_path,
        "tone_analysis": tone_analysis
    }


@app.get("/api/user/letter-style")
async def get_letter_style(request: Request):
    """Get the user's analyzed cover letter style summary"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        return {"style_summary": None}

    prefs = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})

    if not prefs or len(prefs) == 0:
        return {"style_summary": None}

    p = prefs[0]
    # Map DB fields to rich style_summary format for the frontend
    style_summary = {
        "tone": p.get("tone"),
        "structure": p.get("writing_style"),
        "phrases": p.get("always_mention") if isinstance(p.get("always_mention"), list) else [],
        "avoid": p.get("avoid_phrases") if isinstance(p.get("avoid_phrases"), list) else [],
        "length_preference": p.get("length_preference"),
        "opening_style": p.get("opening_style")
    }
    return {"style_summary": style_summary}


@app.get("/api/user/training-letters")
async def get_user_training_letters(request: Request):
    """Get all training letters uploaded by the user"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    letters = await db_request("GET", "user_training_letters",
        params={"user_id": f"eq.{user_id}", "order": "uploaded_at.desc"})

    return {"success": True, "letters": letters or []}


@app.delete("/api/user/training-letters/{letter_id}")
async def delete_user_training_letter(letter_id: str, request: Request):
    """Delete a training letter"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # Verify the letter belongs to this user before deleting
    letter = await db_request("GET", "user_training_letters",
        params={"id": f"eq.{letter_id}", "user_id": f"eq.{user_id}"})

    if not letter or len(letter) == 0:
        raise HTTPException(status_code=404, detail="Brev hittades inte")

    # Delete from storage if file_url exists
    file_url = letter[0].get("file_url", "")
    if file_url and "training-letters/" in file_url:
        storage_path = file_url.split("training-letters/")[-1]
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{SUPABASE_URL}/storage/v1/object/training-letters/{storage_path}",
                headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=10
            )

    await db_request("DELETE", "user_training_letters",
        params={"id": f"eq.{letter_id}", "user_id": f"eq.{user_id}"})

    return {"success": True}


@app.post("/api/user/upload-training-letter")
async def upload_user_training_letter(request: Request):
    """Upload a training letter file, save to storage + DB, and analyze writing style"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    # Check max 20 letters per user
    existing_letters = await db_request("GET", "user_training_letters",
        params={"user_id": f"eq.{user_id}", "select": "id"})
    if existing_letters and len(existing_letters) >= 20:
        raise HTTPException(status_code=400, detail="Max 20 brev. Ta bort ett för att ladda upp fler.")

    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(status_code=400, detail="Ingen fil bifogad")

    file_content = await file.read()
    letter_text = extract_text_from_file(file_content, file.filename)

    if not letter_text:
        letter_text = "[Kunde inte extrahera text från filen]"

    # Upload to Supabase Storage (training-letters bucket, PUBLIC)
    import time
    timestamp = int(time.time())
    filename_lower = file.filename.lower()
    file_ext = filename_lower.split('.')[-1] if '.' in filename_lower else 'pdf'
    content_type_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        'odt': 'application/vnd.oasis.opendocument.text'
    }
    content_type = content_type_map.get(file_ext, 'application/pdf')
    storage_path = f"{user_id}/letter_{timestamp}.{file_ext}"
    file_url = None

    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/training-letters/{storage_path}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            content=file_content,
            timeout=30
        )
        if upload_response.status_code in [200, 201]:
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/training-letters/{storage_path}"

    # Save to user_training_letters table
    await db_request("POST", "user_training_letters", data={
        "user_id": user_id,
        "filename": file.filename,
        "letter_text": letter_text,
        "file_url": file_url
    })

    # Analyze tone and update style preferences
    tone_analysis = await analyze_writing_tone_rich(letter_text)
    await save_letter_style(user_id, tone_analysis)

    return {"success": True, "tone_analysis": tone_analysis, "file_url": file_url}


@app.post("/api/user/analyze-letter-text")
async def analyze_pasted_letter_text(request: Request):
    """Analyze pasted cover letter text to extract writing style"""
    auth_header = request.headers.get("Authorization", "")
    user_id = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Ej inloggad")

    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Ingen text angiven")

    tone_analysis = await analyze_writing_tone_rich(text)
    await save_letter_style(user_id, tone_analysis)

    return {"success": True, "tone_analysis": tone_analysis}


async def save_letter_style(user_id: str, analysis: dict):
    """Save or update letter style analysis in DB"""
    existing = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})
    data = {
        "tone": analysis.get("tone"),
        "writing_style": analysis.get("structure"),
        "always_mention": analysis.get("phrases", []),
        "avoid_phrases": analysis.get("avoid", []),
        "length_preference": analysis.get("length_preference"),
        "opening_style": analysis.get("opening_style")
    }
    if existing and len(existing) > 0:
        await db_request("PATCH", "user_cover_letter_preferences",
            params={"user_id": f"eq.{user_id}"}, data=data)
    else:
        await db_request("POST", "user_cover_letter_preferences",
            data={"user_id": user_id, **data})


async def analyze_writing_tone_rich(text: str) -> dict:
    """Analyze writing tone and style using Claude API — returns rich structured summary"""
    if not ANTHROPIC_API_KEY:
        return {}

    prompt = f"""Du analyserar ett personligt brev på svenska och skapar en strukturerad sammanfattning av skrivarens stil.

Brev:
{text[:3000]}

Returnera ett JSON-objekt med dessa exakta nycklar:
- "tone": En mening om tonen, t.ex. "Varm och personlig, men professionell"
- "structure": En mening om hur brevet är uppbyggt, t.ex. "Börjar med varför företaget, sedan erfarenhet, avslutar med konkret nästa steg"
- "phrases": Lista med 3-6 fraser eller uttryck som personen faktiskt använder
- "avoid": Lista med ord eller fraser som personen INTE använder (t.ex. klichéer som de aktivt undviker)
- "length_preference": En mening om brevets längd och takt, t.ex. "Kortfattat, max 3 stycken, ingen onödig utfyllnad"
- "opening_style": En mening om hur personen brukar inleda, t.ex. "Börjar alltid med vad som drog dem till just det företaget"

Svara ENDAST med JSON."""

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
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 700,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                raw = result["content"][0]["text"].strip()
                import json as json_lib
                start = raw.find('{')
                end = raw.rfind('}') + 1
                if start >= 0 and end > start:
                    return json_lib.loads(raw[start:end])
    except Exception as e:
        logger.error(f"Rich tone analysis error: {e}")

    return {}


async def analyze_writing_tone(text: str) -> dict:
    """Analyze writing tone and style using Claude API"""
    if not ANTHROPIC_API_KEY:
        return {"tone": "neutral", "favorite_phrases": []}

    prompt = f"""Analysera tonen och stilen i detta personliga brev på svenska.

Brev:
{text}

Returnera ett JSON-objekt med:
- "tone": en kort beskrivning av tonen (t.ex. "professionell men personlig", "entusiastisk och energisk")
- "writing_style": beskrivning av meningsstruktur och ordval
- "favorite_phrases": lista med 3-5 fraser eller uttryck som personen använder

Svara ENDAST med JSON, inget annat."""

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
                result = response.json()
                text_response = result["content"][0]["text"].strip()

                # Parse JSON from response
                import json
                start = text_response.find('{')
                end = text_response.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(text_response[start:end])

    except Exception as e:
        logger.error(f"Tone analysis error: {e}")

    return {"tone": "neutral", "favorite_phrases": []}


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})
