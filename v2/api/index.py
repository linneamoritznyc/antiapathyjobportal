"""
Anti-Apathy Job Portal v2
En jobbportal som hjälper dig söka jobb via e-post direkt till arbetsgivare.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Any, Optional, List, Dict
import os
import logging
import httpx
import re
import time
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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ── Swedish Language Rules (Svenska Skrivregler) ──────────────────────────
# Used in all AI text generation: cover letters, CVs, application answers
SWEDISH_LANGUAGE_RULES = """
SVENSKA SKRIVREGLER — OBLIGATORISKT (all text MÅSTE följa dessa regler):

── GRAMMATIK ──

DE/DEM: DE = subjekt (vi), DEM = objekt (oss). Skriv ALDRIG "dom" i formell text.
  RÄTT: De söker tjänsten. Jag skickade till dem.

EN/ETT: -are/-ing/-het/-tion/-else → "en". -ande/-ende/-ium/-ment/-um → "ett".
  RÄTT: en erfarenhet, en förmåga, en ansökan, ett uppdrag, ett ansvar, ett resultat.
  FEL: "ett erfarenhet", "en ansvar", "ett förmåga" — vanliga AI-fel.

BISATSORDFÖLJD: I bisatser placeras satsadverbialet (inte, alltid, ofta, aldrig, redan, bara) FÖRE verbet.
  RÄTT: ...eftersom jag INTE har arbetat med detta.
  FEL:  ...eftersom jag har INTE arbetat med detta.
  RÄTT: ...trots att jag ALLTID har strävat efter att utvecklas.
  FEL:  ...trots att jag har ALLTID strävat...

VAR/VART: VAR = befintlighet. VART = rörelse/riktning.
  RÄTT: Var arbetar du? Vart är projektet på väg?

JÄMFÖRELSER: Subjektspronomen efter "än".
  RÄTT: Hon har mer erfarenhet än jag. FEL: ...än mig.

ADJEKTIV/ADVERB: Adjektiv böjs efter substantiv, adverb böjs INTE.
  RÄTT: ett tydligt ledarskap (adj). Hon kommunicerar tydligt (adv).

PREPOSITIONER (svenska ≠ engelska):
  ansvarig FÖR (inte "på"), intresserad AV (inte "för"), erfarenhet AV att (inte "från att"),
  fokuserad PÅ (inte "mot"), bidra TILL (inte "för"), engagerad I (inte "med"),
  arbeta MED (inte "på"), ta ansvar FÖR (inte "på"), söker tjänsten SOM (inte "för").

── STAVNING OCH FORM ──

SAMMANSATTA ORD IHOP: projektledare, kundansvar, arbetsuppgifter, marknadsföring,
  kommunikationsförmåga, beslutsfattande, verksamhetsutveckling, kvalitetsarbete.
  FEL: "projekt ledare", "kund ansvar", "problem lösning". Bindestreck vid siffror/förkortningar: IT-kompetens, 50-årskalas.

APOSTROF: Aldrig vid genitiv. RÄTT: Annas erfarenhet, bolagets strategi. FEL: Anna's erfarenhet.

STOR/LITEN BOKSTAV: Liten: månader, dagar, titlar (vd, chef, projektledare).
  Stor: företag, organisationer, egennamn. Aldrig stor mitt i mening för betoning.

PLURAL: videor (inte "videos"), scheman, processer, kompetenser.

FÖRKORTNINGAR I LÖPTEXT: Skriv ut. "till exempel" inte "t.ex.", "det vill säga" inte "d.v.s."

DATUM/TAL: "11 oktober 2025". Tal 1–12 med bokstäver. Decimaler med komma: 3,5. Stora tal med mellanslag: 1 200 000.

── ORDVAL — INGEN SVENGELSKA ──

meeting→möte, deadline→tidsgräns, feedback→återkoppling, track record→dokumenterade resultat,
leverage→dra nytta av, key account→nyckelkund, update→uppdatering, skills→kompetenser,
mindset→tankesätt, achievements→meriter, stakeholder→intressent, onboarding→introduktion,
output→resultat, challenge→utmaning, hands-on→praktisk, high-level→övergripande,
scope→omfattning, impact→påverkan, rollout→lansering, setup→upplägg, know-how→kunnande,
mentored/mentorerade→handledde, NGO→ideell organisation, NGO:er→ideella organisationer,
NGO-partnerskap→samarbeten med ideella organisationer, policy→regel/riktlinje,
policyförbättringar→regelförbättringar, policyriktlinjer→riktlinjer,
teamarbete→lagarbete, team→lag/grupp (i sammansättningar), nätverksevenemang→nätverksträff,
validated/validerade→bekräftade (t.ex. "bekräftade konceptets bärkraft"),
servicenivå→tjänstenivå, servicenivåmål→tjänstenivåmål.

Accepterade lånord (OK att använda): proaktiv, strategi, digital, analys, process, projekt,
kompetens, effektiv, relevant, professionell, innovation, kommunikation, koordinera, implementera.

── TON OCH STIL ──

MENINGSBYGGNAD: Subjekt + verb tidigt. Det viktigaste först. Aktiv form.
  RÄTT: Jag ansvarade för budgeten. FEL: Budgeten ansvarades för av mig.
  Undvik substantiveringar: "Vi genomförde" inte "Genomförandet av".

FÖRBJUDNA AI-KLICHÉER: "passionerad", "brinner för", "gedigen erfarenhet", "unik bakgrund",
  "spännande roll", "dynamisk miljö", "starkt driv", "bidra till er resa", "genuint intresserad",
  "värdefull tillgång", "driven och ambitiös", "positiv mindset".

FÖRBJUDNA FORMELLA/STELA UTTRYCK (använd det vardagliga alternativet):
  "rondera lokaler"→"gå ronder", "rondera"→"gå rond/runda",
  "tillse att"→"se till att", "ombesörja"→"ordna/fixa/se till",
  "beivra"→"ta itu med", "emotse"→"ser fram emot", "delge"→"berätta för",
  "föranstalta"→"ordna", "förhöra sig"→"fråga/kolla",
  "inneha"→"har", "tillgodose"→"uppfylla/möta",
  "vidta åtgärder"→"ta tag i/göra något åt", "genomlysa"→"granska/gå igenom",
  "tillvarata"→"ta vara på", "tillhandahålla"→"erbjuda/ge",
  "säkerställa"→"se till att" (i vardagliga sammanhang),
  "beakta"→"tänka på/ha i åtanke", "ansvara för att upprätthålla"→"sköta/hålla koll på".
  REGEL: Om ett ord inte skulle sägas i ett normalt samtal — byt ut det.

NATURLIGA FORMULERINGAR:
  CV: "Ledde ett team på åtta personer", "Ökade försäljningen med 30 procent"
  Brev: "Det som lockar mig med tjänsten är [specifikt]", "Jag har i tre år arbetat med [specifikt]"
  Mail: "Bifogat hittar du", "Hör gärna av dig om du har frågor", "Tack på förhand"

HÄLSNINGAR: "Hej [namn]," (naturligt). Undvik "Bäste/Bästa" (ålderdomligt).
  Avslut: "Med vänliga hälsningar" / "Vänligen" / "Med vänlig hälsning".
"""

# Gmail API scopes
GMAIL_SCOPES = "https://www.googleapis.com/auth/gmail.compose"

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
    municipality_ids: Optional[List[str]] = None  # Taxonomy concept IDs from JobTech API


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


# ============== AUTH & SHARED HELPERS ==============

async def get_user_id_from_request(request: Request, required: bool = False) -> Optional[str]:
    """Extract user_id from Authorization Bearer token.
    If required=True, raises 401 if not authenticated."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        if required:
            raise HTTPException(status_code=401, detail="Ej inloggad")
        return None
    token = auth_header.replace("Bearer ", "")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                return resp.json().get("id")
    except Exception:
        pass
    if required:
        raise HTTPException(status_code=401, detail="Ej inloggad")
    return None


def get_supabase_headers(prefer: str = "return=representation") -> dict:
    """Get standard Supabase headers for REST API calls."""
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer
    }


async def call_claude_api(prompt: str, model: str = "claude-haiku-4-5-20251001", max_tokens: int = 600, timeout: int = 25) -> Optional[str]:
    """Call Claude API and return the response text, or None on failure."""
    if not ANTHROPIC_API_KEY:
        return None
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
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json()["content"][0]["text"].strip()
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
    return None


CONTENT_TYPE_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".txt": "text/plain",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


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


# ============== MUNICIPALITY LABEL LOOKUP (for scraper post-filtering) ==============

_muni_label_cache: Dict[str, str] = {}
_muni_cache_fetched_at: float = 0

# Kommun ID → county (län) name mapping, built from lan-data.js
_kommun_to_county: Dict[str, str] = {}

def _build_kommun_to_county() -> Dict[str, str]:
    """Parse lan-data.js to build a kommun_id → county_name mapping."""
    global _kommun_to_county
    if _kommun_to_county:
        return _kommun_to_county
    try:
        lan_data_path = pathlib.Path(__file__).parent.parent / "lan-data.js"
        js_text = lan_data_path.read_text(encoding='utf-8')
        # Extract the array content from "const LAN_DATA = [...]"
        start = js_text.index('[')
        end = js_text.rindex(']') + 1
        # Convert JS object syntax to valid JSON (add quotes to keys)
        import re as _re
        json_text = js_text[start:end]
        json_text = _re.sub(r'(\w+):', r'"\1":', json_text)  # {id: → {"id":
        json_text = json_text.replace("'", '"')  # single quotes → double quotes
        import json as _json
        data = _json.loads(json_text)
        mapping = {}
        for lan in data:
            county_name = lan.get("label", "")
            for kommun in lan.get("kommuner", []):
                mapping[kommun["id"]] = county_name
        _kommun_to_county = mapping
        logger.info(f"Built kommun→county mapping: {len(mapping)} entries")
    except Exception as e:
        logger.error(f"Failed to build kommun→county mapping: {e}")
    return _kommun_to_county


def _get_county_labels_for_kommun_ids(kommun_ids: List[str]) -> List[str]:
    """Given a list of kommun IDs, return the unique county (län) names they belong to."""
    mapping = _build_kommun_to_county()
    counties = set()
    for kid in kommun_ids:
        county = mapping.get(kid)
        if county:
            counties.add(county.lower())
    return list(counties)

async def fetch_municipality_labels() -> Dict[str, str]:
    """Fetch municipality ID → label mapping from JobTech Taxonomy API.
    Used by the scraper to post-filter jobs by municipality name.
    Source: https://taxonomy.api.jobtechdev.se/v1/taxonomy/specific/concepts/municipality
    (returns only Swedish municipalities — 290 kommuner)"""
    global _muni_label_cache, _muni_cache_fetched_at
    now = time.time()
    if _muni_label_cache and (now - _muni_cache_fetched_at) < 86400:
        return _muni_label_cache

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "https://taxonomy.api.jobtechdev.se/v1/taxonomy/specific/concepts/municipality",
                timeout=10
            )
            if res.status_code != 200:
                logger.error(f"Municipality taxonomy API error: {res.status_code}")
                return _muni_label_cache
            data = res.json()
            _muni_label_cache = {
                m["taxonomy/id"]: m["taxonomy/preferred-label"]
                for m in data
                if m.get("taxonomy/id") and m.get("taxonomy/preferred-label")
            }
            _muni_cache_fetched_at = now
            logger.info(f"Municipality labels loaded: {len(_muni_label_cache)} municipalities")
            return _muni_label_cache
    except Exception as e:
        logger.error(f"Failed to fetch municipality labels: {e}")
        return _muni_label_cache


def _job_in_municipalities(job: Dict, municipality_labels_lower: List[str],
                           county_labels_lower: List[str] = None) -> bool:
    """Post-filter: check if job location matches any selected municipality or county.
    Uses EXACT match on municipality field (most reliable), falls back to
    substring on location only when municipality is empty, and county as last resort."""
    if not municipality_labels_lower:
        return True
    job_muni = (job.get("municipality") or "").lower().strip()
    job_loc = (job.get("location") or "").lower()
    job_county = (job.get("county") or "").lower()
    # 1. Exact match on municipality field (clean data from Platsbanken)
    if job_muni:
        for label in municipality_labels_lower:
            if label == job_muni:
                return True
        # Municipality exists but doesn't match any selected kommun → skip location fallback
        # (municipality is the authoritative field when present)
    else:
        # 2. Fallback: substring match on location ONLY when municipality field is empty
        if job_loc:
            for label in municipality_labels_lower:
                if label in job_loc:
                    return True
    # 3. County (län) match as last resort
    if county_labels_lower and job_county:
        for county in county_labels_lower:
            if county in job_county:
                return True
    return False


# ============== JOB DESCRIPTION SUMMARIZER ==============

async def summarize_job_descriptions(jobs: List[Dict]) -> List[Dict]:
    """
    Batch-summarize job descriptions using AI.
    Takes full descriptions and produces short, scannable summaries.
    Processes all jobs in one API call for efficiency.
    """
    if not jobs:
        return jobs

    # Build batch prompt with all job descriptions
    job_entries = []
    for i, job in enumerate(jobs):
        full_desc = job.get("full_description", job.get("description", ""))
        if len(full_desc) > 2000:
            full_desc = full_desc[:2000]
        job_entries.append(f"[JOB {i}] {job.get('title', '')} — {job.get('company', '')}\n{full_desc}")

    batch_text = "\n---\n".join(job_entries)

    prompt = f"""Sammanfatta varje jobbannons till MAX 3-4 korta meningar på svenska.
Inkludera BARA det viktigaste:
- Vad jobbet går ut på (1 mening)
- Viktigaste kravet/erfarenheten (1 mening)
- Anställningsform/tider om det nämns (1 kort mening)

Svara med exakt samma format: [JOB 0] sammanfattning, [JOB 1] sammanfattning, osv.
Inga rubriker, inga bullet points, bara löpande text per jobb.

{batch_text}"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 300 * len(jobs),
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            if response.status_code == 200:
                result = response.json()
                summary_text = result["content"][0]["text"]

                # Parse summaries back to individual jobs
                for i, job in enumerate(jobs):
                    marker = f"[JOB {i}]"
                    next_marker = f"[JOB {i+1}]"
                    start = summary_text.find(marker)
                    if start == -1:
                        continue
                    start += len(marker)
                    end = summary_text.find(next_marker) if i < len(jobs) - 1 else len(summary_text)
                    if end == -1:
                        end = len(summary_text)
                    summary = summary_text[start:end].strip()
                    if summary:
                        job["description"] = summary
                logger.info(f"Summarized {len(jobs)} job descriptions")
            else:
                logger.warning(f"Summary API returned {response.status_code}, keeping truncated descriptions")
    except Exception as e:
        logger.warning(f"Job summary failed, keeping truncated descriptions: {e}")

    return jobs


# ============== PLATSBANKEN SCRAPER ==============


async def scrape_platsbanken(keyword: str, max_jobs: int = 15, municipality_ids: List[str] = None) -> List[Dict]:
    """
    Scrape jobs from Platsbanken API.
    When municipality_ids is set, adds geographic filters to the search request
    and post-filters by municipality name as a safety net.
    """
    jobs = []
    max_records = 50

    # Look up municipality labels + county names for post-filtering
    municipality_labels_lower = []
    county_labels_lower = []
    if municipality_ids:
        label_lookup = await fetch_municipality_labels()
        municipality_labels_lower = [
            label_lookup[mid].lower() for mid in municipality_ids if mid in label_lookup
        ]
        county_labels_lower = _get_county_labels_for_kommun_ids(municipality_ids)
        if municipality_labels_lower:
            logger.info(f"Geography filter active: {municipality_labels_lower}, counties: {county_labels_lower}")

    try:
        async with httpx.AsyncClient() as client:
            # Build search filters
            filters = [{"type": "freetext", "value": keyword}]

            # Add geographic filters (municipality concept IDs from taxonomy)
            if municipality_ids:
                for mid in municipality_ids:
                    filters.append({"type": "municipality", "value": mid})

            response = await client.post(
                "https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search",
                headers={"Content-Type": "application/json"},
                json={
                    "filters": filters,
                    "fromDate": None,
                    "order": "date",
                    "maxRecords": max_records,
                    "startIndex": 0,
                    "source": "pb"
                },
                timeout=20
            )

            # If geo filters caused an error, retry without them
            if response.status_code != 200 and municipality_ids:
                logger.warning(f"Platsbanken rejected geo filters (status {response.status_code}), retrying without")
                response = await client.post(
                    "https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search",
                    headers={"Content-Type": "application/json"},
                    json={
                        "filters": [{"type": "freetext", "value": keyword}],
                        "fromDate": None,
                        "order": "date",
                        "maxRecords": 100,  # Fetch more since we'll post-filter
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
                job_location = ad.get("workplace", "")
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

                # Keep full description for AI cover letter generation
                full_description = description

                # Truncate display description to ~500 chars (short intro only)
                # Users can click "Se originalannons" for full text
                if len(description) > 500:
                    truncated = description[:500]
                    last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                    if last_period > 150:
                        description = description[:last_period + 1]
                    else:
                        description = truncated.rsplit(' ', 1)[0] + '...'

                job = {
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "municipality": municipality,
                    "county": county,
                    "occupation": occupation,
                    "description": description,
                    "full_description": full_description[:6000],
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

    # Post-filter by municipality + county name as safety net
    if municipality_labels_lower and jobs:
        before = len(jobs)
        jobs = [j for j in jobs if _job_in_municipalities(j, municipality_labels_lower, county_labels_lower)]
        logger.info(f"Geography post-filter: {before} → {len(jobs)} jobs")

    # AI-summarize descriptions for display (keeps full_description for cover letters)
    if jobs:
        jobs = await summarize_job_descriptions(jobs)

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


async def check_swedish_with_gpt_sw3(text: str) -> str:
    """
    Post-generation Swedish grammar check using GPT-SW3 via HuggingFace Inference API.
    Returns corrected text, or original text if the check fails/is unavailable.
    """
    if not HUGGINGFACE_API_KEY or not text:
        return text

    try:
        prompt = f"""<|endoftext|><s>
User:
Du är en svensk korrekturläsare. Rätta BARA grammatiska fel i texten nedan.
Behåll exakt samma innehåll, ton och längd. Ändra BARA:
- de/dem-fel
- en/ett-fel
- bisatsordföljd (satsadverbial före verb i bisats)
- särskrivningar (sammansatta ord ska vara ihop)
- felaktiga prepositioner
- svengelska (byt till svenska ord)
Om texten redan är korrekt, returnera den oförändrad.

TEXT:
{text}

RÄTTAD TEXT:
<s>
Bot:
"""
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/AI-Sweden-Models/gpt-sw3-6.7b-v2-instruct",
                headers={
                    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 1500,
                        "temperature": 0.1,
                        "do_sample": True,
                        "return_full_text": False
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    corrected = result[0].get("generated_text", "").strip()
                    # Only use the correction if it's roughly the same length (not truncated/garbage)
                    if corrected and len(corrected) > len(text) * 0.5:
                        logger.info("GPT-SW3 grammar check applied successfully")
                        return corrected
                    else:
                        logger.warning(f"GPT-SW3 returned unexpected output length: {len(corrected)} vs {len(text)}")
            elif response.status_code == 503:
                logger.info("GPT-SW3 model is loading (cold start), skipping grammar check")
            else:
                logger.warning(f"GPT-SW3 API returned {response.status_code}: {response.text[:200]}")

    except Exception as e:
        logger.warning(f"GPT-SW3 grammar check failed (non-blocking): {e}")

    return text


async def generate_cover_letter(job: Dict, user_cv_text: Optional[str] = None, user_profile: Optional[Dict] = None, extra_hints: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """Generate personalized cover letter using Claude"""

    if not ANTHROPIC_API_KEY:
        return generate_template_letter(job)

    # If job only has short summary, fetch full description from DB for better cover letter
    if not job.get("full_description") and job.get("id") and SUPABASE_URL:
        try:
            db_job = await db_request("GET", "jobs", params={"id": f"eq.{job['id']}", "select": "description"})
            if db_job and db_job[0].get("description"):
                job["full_description"] = db_job[0]["description"]
        except Exception:
            pass

    # Get relevant experience — prefer user's master CV, then bransch-CV text, then defaults
    category = detect_job_category(job.get("title", ""), job.get("full_description", job.get("description", "")))
    experience = user_cv_text

    # If no bransch-CV text, try to fetch master CV experiences for richer content
    if not experience and user_id:
        try:
            master_exps = await db_request("GET", "master_cv_experiences", params={
                "user_id": f"eq.{user_id}",
                "order": "start_date.desc",
                "limit": "10"
            })
            if master_exps:
                exp_lines = []
                for exp in master_exps:
                    line = f"- {exp.get('title', '')}"
                    if exp.get('company'):
                        line += f", {exp['company']}"
                    dates = ""
                    if exp.get('start_date'):
                        dates = exp['start_date'][:7]
                    if exp.get('end_date'):
                        dates += f" – {exp['end_date'][:7]}"
                    elif exp.get('is_current'):
                        dates += " – pågående"
                    if dates:
                        line += f" ({dates})"
                    if exp.get('description'):
                        line += f": {exp['description'][:200]}"
                    exp_lines.append(line)
                if exp_lines:
                    experience = "\n".join(exp_lines)
                    logger.info(f"Using {len(exp_lines)} master CV experiences for cover letter")
        except Exception as e:
            logger.warning(f"Could not fetch master CV experiences: {e}")

    if not experience:
        experience = DEFAULT_EXPERIENCE.get(category, DEFAULT_EXPERIENCE["default"])

    # Strip personal info header from CV text (name, location, phone, email)
    # so the AI only sees this info from the OM MIG section (which has the correct,
    # up-to-date values from the user's profile — not stale data baked into CV text).
    if experience and user_cv_text:
        lines = experience.split("\n")
        cleaned = []
        in_header = True
        for line in lines:
            stripped = line.strip()
            if in_header:
                # Skip blank lines and personal info lines at the top
                if not stripped:
                    continue
                # Detect personal info lines: contain phone pattern, email, or pipe-separated header
                is_personal = (
                    re.search(r'\d{3,4}[\s-]?\d{2,3}[\s-]?\d{2,4}', stripped) or  # phone
                    re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', stripped) or  # email
                    ("|" in stripped and len(stripped.split("|")) >= 3)  # pipe-separated header
                )
                # Also skip if it's just a name (short line, no section keywords)
                is_just_name = len(stripped.split()) <= 3 and not any(
                    kw in stripped.upper() for kw in ["UTBILDNING", "ERFARENHET", "KOMPETENS", "PROFIL", "SAMMANFATTNING"]
                )
                if is_personal or is_just_name:
                    continue
                in_header = False
            cleaned.append(line)
        if cleaned:
            experience = "\n".join(cleaned)

    # Append any extra hints the user selected in the UI
    if extra_hints:
        experience += f"\n\nEXTRA ERFARENHETER SOM MÅSTE NÄMNAS I BREVET:\n{extra_hints}"

    # Use profile data from database, fall back to defaults
    p = user_profile or {}
    name = p.get("full_name", "Linnea Moritz")
    phone = p.get("phone", "0761166109")
    email = p.get("email", "linneamoritzCV@gmail.com")
    has_license = p.get("drivers_license", True)
    linkedin = p.get("linkedin", "")
    own_car = p.get("own_car", False)

    # Region-based location: pick "bor i X" based on the job's county
    location = p.get("location", "")
    region_highlights = []
    location_by_region = p.get("location_by_region") or {}
    if location_by_region:
        job_county = (job.get("county") or "").strip().lower()
        matched_region = None
        if job_county:
            for region_key, region_data in location_by_region.items():
                if region_key == "default":
                    continue
                if isinstance(region_data, dict) and job_county.startswith(region_key.lower()):
                    matched_region = region_data
                    break
        # Fall back to default region
        if not matched_region and location_by_region.get("default"):
            default_key = location_by_region["default"]
            matched_region = location_by_region.get(default_key)
        if matched_region and isinstance(matched_region, dict):
            location = matched_region.get("ort", location)
            region_highlights = matched_region.get("highlights", [])

    # Defaults — may be overridden by user prefs below
    contact_greeting = f"Hej {job.get('contact_name', '')}!" if job.get('contact_name') else "Hej!"
    signature_style = "Med vänlig hälsning,"

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

    # Calculate real age from birth_date
    real_age = None
    birth_date_str = p.get("birth_date")
    if birth_date_str:
        try:
            from datetime import date
            birth = date.fromisoformat(str(birth_date_str)[:10])
            today = date.today()
            real_age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except Exception:
            pass

    # Build user info section
    user_info = f"- {name}"
    if real_age:
        user_info += f", {real_age} år"
    if location:
        user_info += f", bor i {location}"
    # Körkort/bil: always mention if job description asks, otherwise only if region highlights include it
    job_desc_lower = (job.get("full_description") or job.get("description") or "").lower()
    job_mentions_license = any(w in job_desc_lower for w in ["körkort", "b-körkort", "körkortskrav"])
    job_mentions_car = "egen bil" in job_desc_lower
    show_license = job_mentions_license or "körkort" in [h.lower() for h in region_highlights]
    show_car = job_mentions_car or "egen bil" in [h.lower() for h in region_highlights]
    if has_license and own_car and (show_license or show_car):
        user_info += f"\n- Har B-körkort och egen bil"
    elif has_license and show_license:
        user_info += f"\n- Har B-körkort"
    user_info += f"\n- Flexibel med arbetstider"
    user_info += f"\n- Telefon: {phone}"
    user_info += f"\n- Svenska (modersmål), Engelska (flytande)"
    if linkedin:
        user_info += f"\n- LinkedIn: {linkedin}"
    # Add any other region-specific highlights
    for h in region_highlights:
        if h.lower() not in ("körkort", "egen bil"):
            user_info += f"\n- {h}"

    # Fetch style preferences, anecdotes, and AI feedback if user is logged in
    style_section = ""
    anecdotes_section = ""
    feedback_section = ""
    if user_id:
        try:
            import asyncio as _asyncio
            prefs_result, anecdotes_result, feedback_result = await _asyncio.gather(
                db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"}),
                db_request("GET", "user_anecdotes", params={"user_id": f"eq.{user_id}"}),
                db_request("GET", "user_ai_feedback", params={"user_id": f"eq.{user_id}", "is_active": "eq.true", "order": "created_at.desc", "limit": "10"})
            )

            # Build style instructions from preferences
            if prefs_result and len(prefs_result) > 0:
                sp = prefs_result[0]
                style_parts = []
                if sp.get("tone"):
                    style_parts.append(f"- Min ton: {sp['tone']}")
                if sp.get("writing_style"):
                    style_parts.append(f"- Min brevstruktur: {sp['writing_style']}")
                if sp.get("opening_style"):
                    style_parts.append(f"- Hur jag brukar börja: {sp['opening_style']}")
                if sp.get("length_preference"):
                    style_parts.append(f"- Längd: {sp['length_preference']}")

                phrases = sp.get("liked_phrases", []) or []
                if isinstance(phrases, list) and phrases:
                    style_parts.append(f"- Fraser jag gillar att använda: {', '.join(phrases)}")

                avoid = sp.get("avoid_phrases", []) or []
                if isinstance(avoid, list) and avoid:
                    style_parts.append(f"- Fraser jag INTE vill ha (undvik dessa!): {', '.join(avoid)}")

                never = sp.get("never_mention", []) or []
                if isinstance(never, list) and never:
                    style_parts.append(f"- Ämnen att ALDRIG nämna: {', '.join(never)}")

                custom_instr = sp.get("custom_ai_instructions", "") or ""
                if custom_instr.strip():
                    style_parts.append(f"- Mina egna instruktioner: {custom_instr.strip()}")

                # Override greeting/signature/sign-off from user prefs
                if sp.get("greeting_style"):
                    user_greeting_style = sp["greeting_style"]
                    if job.get("contact_name"):
                        # Replace [Company] or just use greeting + name
                        contact_greeting = f"{user_greeting_style.replace('[Company]', '').strip()} {job['contact_name']}!".strip()
                    else:
                        contact_greeting = user_greeting_style
                if sp.get("signature_style"):
                    signature_style = sp["signature_style"]
                if sp.get("sign_off_name"):
                    name = sp["sign_off_name"]
                if sp.get("sign_off_phone"):
                    phone = sp["sign_off_phone"]
                if sp.get("sign_off_email"):
                    email = sp["sign_off_email"]

                # never_mention list
                never = sp.get("never_mention", []) or []
                if isinstance(never, list) and never:
                    style_parts.append(f"- Ämnen att ALDRIG nämna: {', '.join(never)}")

                if style_parts:
                    style_section = "\n\nMIN SKRIVSTIL (skriv brevet i min stil):\n" + "\n".join(style_parts)

            # Build anecdotes section — include all, let AI pick relevant ones
            if anecdotes_result and len(anecdotes_result) > 0:
                anecdote_parts = []
                for a in anecdotes_result:
                    kw = a.get("keywords", []) or []
                    kw_text = f" (relevant för: {', '.join(kw)})" if kw else ""
                    if a.get("type") == "hobby":
                        anecdote_parts.append(f"- Hobby: {a['title']} — {a['content']}{kw_text}")
                    else:
                        anecdote_parts.append(f"- Anekdot: {a['title']} — {a['content']}{kw_text}")

                if anecdote_parts:
                    anecdotes_section = "\n\nMINA PERSONLIGA ANEKDOTER & HOBBYS (använd BARA om de passar jobbet):\n" + "\n".join(anecdote_parts)

            # Build feedback section from previous user feedback
            if feedback_result and len(feedback_result) > 0:
                feedback_parts = [f"- {fb['feedback_text']}" for fb in feedback_result if fb.get("feedback_text")]
                if feedback_parts:
                    feedback_section = "\n\nTIDIGARE FEEDBACK FRÅN MIG (följ detta STRIKT):\n" + "\n".join(feedback_parts)

        except Exception as e:
            logger.error(f"Error fetching style/anecdotes/feedback: {e}")

    prompt = f"""Skriv ett riktigt bra personligt brev på svenska för denna jobbansökan. Brevet ska vara så bra att arbetsgivaren vill boka en intervju direkt.

JOBBET:
- Titel: {job.get('title')}
- Företag: {job.get('company')}
- Plats: {job.get('location')}
{extras_text}
- Beskrivning: {job.get('full_description', job.get('description', ''))[:3000]}

MIN BAKGRUND (använd som inspiration — plocka bara det som faktiskt är relevant):
{experience}

OM MIG:
{user_info}{style_section}{anecdotes_section}{feedback_section}

INSTRUKTIONER:
1. Börja med: {contact_greeting}
2. Skriv ett FULLSTÄNDIGT personligt brev på naturlig, varm svenska. Brevet ska ha minst 3-4 stycken med riktig substans — INTE bara några generiska meningar. Visa att du har läst annonsen och berätta varför du passar.
3. KRITISKT: Läs jobbeskrivningen NOGA och referera till SPECIFIKA saker från annonsen. Nämn företagsnamnet, tjänstetiteln, och 2-3 konkreta saker från annonsen som visar att du faktiskt har LÄST den. Skriv ALDRIG ett generiskt brev som kunde skickas till vilket jobb som helst.
4. Matcha tonen mot jobbet: fysisk/praktisk tjänst → enkelt och jordnära; kontorsjobb → lite mer formellt
5. Lyft erfarenheter som passar jobbet. Om inga erfarenheter matchar direkt, fokusera istället på personliga egenskaper som passar (t.ex. noggrannhet, pålitlighet, initiativförmåga, servicekänsla). Försök ALDRIG koppla irrelevant erfarenhet till jobbet på ett konstruerat sätt.
6. VIKTIGT: Om annonsen nämner specifika krav eller önskemål (t.ex. körkort, bil, fysisk förmåga, kvällar/helger, sommarsäsong, "annan sysselsättning"), bekräfta kortfattat att jag uppfyller/passar dem — utan att överdriva
7. Nämn var jag bor (EXAKT den ort som anges under "OM MIG" ovan — ignorera eventuell ort/adress i CV-texten) och att jag är flexibel med arbetstider
8. KRITISKT: Om "EXTRA ERFARENHETER SOM MÅSTE NÄMNAS I BREVET" finns ovan — du MÅSTE nämna VARJE ENSKILD erfarenhet som listas där i brevet. Hoppa inte över en enda. Nämn alla, även om de inte matchar jobbet perfekt — hitta en naturlig koppling för var och en. Det är helt ok att nämna 2 erfarenheter tillsammans i samma mening eller stycke om de belyser liknande styrkor
9. Om "MIN SKRIVSTIL" finns ovan — följ den stilen. Undvik ALLA fraser listade under "Fraser jag INTE vill ha". Använd gärna fraser från "Fraser jag gillar".
10. Om "MINA PERSONLIGA ANEKDOTER & HOBBYS" finns ovan — väv in EN relevant anekdot eller hobby om den passar jobbet. Tvinga inte in irrelevanta anekdoter.
11. VIKTIGT om ålder: Om du nämner ålder, använd EXAKT den ålder som står under "OM MIG" ovan. Ignorera eventuell ålder som nämns i bakgrund/erfarenheter — den kan vara gammal.
12. Avsluta med:
   {signature_style}
   {name}
   {phone}
   {email}

{SWEDISH_LANGUAGE_RULES}

EXTRA REGLER FÖR PERSONLIGT BREV:
- Börja INTE varje mening med "Jag". Blanda meningslängder. Texten ska ha flyt.
- INGEN over-explaining: "Jag är noggrann" räcker — behöver INTE tillägga "och det betyder mycket för mig"
- ALDRIG defensiv: Skriv ALDRIG "Jag inser att er annons efterfrågar..." — kort och rakt istället.
- KORREKTA vardagliga fraser: "Jobba i kassan" (INTE "på kassavagn"). "Stå i butik" (INTE "arbeta i butiksmiljö"). "Gå ronder" (INTE "rondera lokaler"). "Sköta om" (INTE "ombesörja").
- Säg: "trygg i min roll", "van vid att jobba självständigt", "bekväm med kundkontakt".
- PROPORTIONER: 80% på vad du KAN. Max 20% på saker du inte gjort.
- Skriv som en RIKTIG person — inte en AI som försöker imponera.
- TESTFRÅGA: Skulle en 25-åring säga det här högt? Om inte → skriv om.

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
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=55
            )

            if response.status_code == 200:
                result = response.json()
                letter_text = result["content"][0]["text"].strip()
                # Run GPT-SW3 Swedish grammar check (non-blocking — returns original on failure)
                letter_text = await check_swedish_with_gpt_sw3(letter_text)
                return letter_text
            else:
                error_body = response.text[:300]
                logger.error(f"Claude API error: {response.status_code} - {error_body}")
                # Try fallback to haiku if sonnet fails
                try:
                    fallback_resp = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": "claude-haiku-4-5-20251001",
                            "max_tokens": 1500,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=55
                    )
                    if fallback_resp.status_code == 200:
                        result = fallback_resp.json()
                        letter_text = result["content"][0]["text"].strip()
                        letter_text = await check_swedish_with_gpt_sw3(letter_text)
                        return letter_text
                except Exception as fallback_err:
                    logger.error(f"Haiku fallback also failed: {fallback_err}")
                # Both failed — show template with error details
                error_note = f"[AI-brevet kunde inte genereras (API-fel {response.status_code}: {error_body[:100]}). Nedan är en mall — redigera den!]\n\n"
                return error_note + generate_template_letter(job)

    except httpx.TimeoutException:
        logger.error("Claude API timeout generating cover letter")
        return "[AI-brevet tog för lång tid. Nedan är en mall — redigera den!]\n\n" + generate_template_letter(job)
    except Exception as e:
        logger.error(f"Error generating letter: {e}")
        return f"[Fel vid brevgenerering: {str(e)[:100]}. Nedan är en mall — redigera den!]\n\n" + generate_template_letter(job)


def generate_template_letter(job: Dict) -> str:
    """Fallback template when API fails — uses job details to be less generic"""
    contact_greeting = f"Hej {job.get('contact_name', '')}!" if job.get('contact_name') else "Hej!"
    title = job.get('title', 'tjänsten')
    company = job.get('company', 'er')
    location = job.get('location', '')

    # Extract a useful snippet from the job description
    desc = job.get('full_description', job.get('description', ''))
    desc_hint = ""
    if desc and len(desc) > 50:
        # Take first sentence or 150 chars as context
        first_sentence = desc.split('.')[0][:150]
        desc_hint = f"\n\nJag läste i annonsen att ni söker någon för {first_sentence.lower().strip()}. Det låter som en roll jag skulle passa bra för."

    location_text = f" i {location}" if location else ""

    return f"""{contact_greeting}

Jag söker tjänsten som {title} hos {company}{location_text}.
{desc_hint}
Jag har bred erfarenhet från service, kundkontakt och praktiskt arbete, och trivs i roller där jag får ta ansvar. Jag är flexibel med arbetstider och kan börja snabbt.

Jag berättar gärna mer om mig i ett samtal!

Med vänlig hälsning,
Linnea Moritz
0761166109
linneamoritzCV@gmail.com"""


# ============== CV GENERATION ==============

async def generate_bransch_cv(master_cv: Dict, bransch: Dict) -> str:
    """Generate a CV version optimized for a specific job category"""

    if not ANTHROPIC_API_KEY:
        return f"[CV för {bransch['name']} - API ej konfigurerad]"

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

    prompt = f"""Skriv ett komplett CV på svenska för {bransch['name']}-jobb.

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

DENNA CV-VERSION ÄR FÖR: {bransch['name']}
Fokus: {bransch['focus']}

INSTRUKTIONER:
1. Skriv ett KOMPLETT CV - inkludera ALL erfarenhet, ALL utbildning, ALLA färdigheter
2. Ordna erfarenheterna kronologiskt (senaste först)
3. För {bransch['name']}-versionen: skriv en kort profil (2-3 meningar) som lyfter erfarenhet relevant för denna bransch
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

{SWEDISH_LANGUAGE_RULES}

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
                    "model": "claude-sonnet-4-5-20250929",
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

    return f"[Kunde inte generera CV för {bransch['name']}]"


async def generate_all_bransch_cvs(master_cv: Dict, user_id: str) -> List[Dict]:
    """Generate all bransch-CV versions for a user"""
    generated_cvs = []

    for bransch in CV_BRANSCHER:
        logger.info(f"Generating bransch-CV: {bransch['name']}...")
        cv_text = await generate_bransch_cv(master_cv, bransch)

        cv_data = {
            "user_id": user_id,
            "vibe_id": bransch["id"],
            "vibe_name": bransch["name"],
            "vibe_emoji": bransch["emoji"],
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


def match_job_to_bransch(job_title: str, job_description: str) -> str:
    """Match a job to the best bransch. Returns bransch_id that maps to a CV PDF."""
    text = f"{job_title} {job_description}".lower()

    # Use whole-word matching via regex to avoid "it" matching inside "arbetstider" etc.
    def word_match(keyword: str, haystack: str) -> bool:
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', haystack))

    bransch_keywords = {
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

    scores = {bransch: sum(1 for kw in kws if word_match(kw, text)) for bransch, kws in bransch_keywords.items()}
    best_bransch = max(scores, key=scores.get) if max(scores.values()) > 0 else "customerservice"
    return best_bransch


# Maps bransch_id → actual CV PDF filename in cv_files/
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


def get_cv_pdf_bytes(bransch_id: str) -> Optional[bytes]:
    """Read the matching CV PDF from disk. Returns None if not found."""
    filename = CV_FILE_MAP.get(bransch_id, CV_FILE_MAP["customerservice"])
    path = CV_FILES_DIR / filename
    try:
        return path.read_bytes()
    except Exception as e:
        logger.error(f"Could not read CV PDF {path}: {e}")
        return None


def get_cv_pdf_filename(bransch_id: str) -> str:
    """Return the CV PDF filename for a given bransch."""
    return CV_FILE_MAP.get(bransch_id, CV_FILE_MAP["customerservice"])


# ============== SUPABASE DATABASE ==============

async def db_request(method: str, table: str, data: dict = None, params: dict = None, on_conflict: str = None) -> Optional[List]:
    """Make request to Supabase.
    For upserts (POST) on tables where the primary key is a UUID (not the business key),
    pass on_conflict='user_id' (or whichever column is the UNIQUE business key) so
    PostgREST resolves conflicts on the right column instead of the UUID primary key."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if on_conflict:
        url += f"?on_conflict={on_conflict}"
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
    db_columns = {"id", "title", "company", "location", "municipality", "county", "description", "description_summary",
                  "url", "deadline", "priority", "contact_email", "contact_name",
                  "source", "scraped_at", "link_status"}

    saved = 0
    for job in jobs:
        db_job = {k: v for k, v in job.items() if k in db_columns}
        # description = full text (for cover letters), description_summary = short AI summary (for UI)
        if job.get("full_description"):
            db_job["description"] = job["full_description"]
            db_job["description_summary"] = job.get("description", "")
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


async def get_jobs_from_db(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Get jobs from database. Returns description_summary + full_description for UI."""
    jobs = await db_request("GET", "jobs", params={
        "order": "scraped_at.desc",
        "limit": str(limit),
        "offset": str(offset)
    })
    if jobs:
        for job in jobs:
            # Always expose full_description for cover letters and "Visa hela annonsen"
            job["full_description"] = job.get("description", "")
            # If we have an AI summary, put it in description for the UI
            if job.get("description_summary"):
                job["description"] = job["description_summary"]
    return jobs or []


async def get_applications_from_db(user_id: str = None) -> List[Dict]:
    """Get applications with job details, optionally filtered by user_id"""
    # Use Supabase's select to embed job data
    url = f"{SUPABASE_URL}/rest/v1/applications?select=*,jobs(id,title,company,contact_email,url,deadline,location,working_hours)&order=created_at.desc"
    if user_id:
        url += f"&user_id=eq.{user_id}"
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
                    app["location"] = app["jobs"].get("location")
                    app["working_hours"] = app["jobs"].get("working_hours")
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
async def scrape_jobs(request: JobSearchRequest = None, req: Request = None):
    """Scrape jobs from Platsbanken.
    Searches user's positive keywords PLUS a broad catch-all search.
    When municipality_ids are provided, geographic filters are applied at the API level.
    """
    keywords = request.keywords if request and request.keywords else ["servitör", "kundtjänst", "butik"]
    municipality_ids = request.municipality_ids if request and request.municipality_ids else None

    if municipality_ids:
        logger.info(f"Scraping with {len(municipality_ids)} municipality filters")

    all_jobs = []

    # 1. Scrape user's positive keywords
    per_keyword_limit = 15
    for keyword in keywords[:5]:
        jobs = await scrape_platsbanken(keyword, max_jobs=per_keyword_limit, municipality_ids=municipality_ids)
        all_jobs.extend(jobs)

    # 2. Broad catch-all scrape so unexpected cool jobs also appear
    broad_limit = 20
    broad_terms = ["jobb", "anställning"]
    for term in broad_terms:
        broad_jobs = await scrape_platsbanken(term, max_jobs=broad_limit, municipality_ids=municipality_ids)
        all_jobs.extend(broad_jobs)

    # Remove duplicates by job ID
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique_jobs.append(job)

    # Sort: email jobs first (direct apply), then external-application jobs at the end
    # Within each group, sort by deadline (soonest first)
    def has_email(j):
        email = j.get("contact_email")
        return bool(email and "@" in str(email))

    unique_jobs.sort(key=lambda j: j.get("deadline") or "2099-12-31")
    with_email = [j for j in unique_jobs if has_email(j)]
    without_email = [j for j in unique_jobs if not has_email(j)]
    unique_jobs = with_email + without_email

    # Save to database if configured
    saved_count = await save_jobs_to_db(unique_jobs)

    # Filter out jobs the user already acted on (applied, rejected, saved)
    # so they don't reappear in fresh scrape results — Tinder-style: once acted on, it's gone.
    user_id = await get_user_id_from_request(req) if req else None
    if user_id and unique_jobs:
        try:
            import asyncio as _asyncio
            interactions, applications = await _asyncio.gather(
                db_request("GET", "user_job_interactions", params={
                    "user_id": f"eq.{user_id}",
                    "action": "in.(applied,rejected)",
                    "select": "job_id"
                }),
                db_request("GET", "applications", params={
                    "user_id": f"eq.{user_id}",
                    "select": "job_id"
                })
            )
            hidden_ids = set()
            if interactions:
                hidden_ids |= {i["job_id"] for i in interactions}
            if applications:
                hidden_ids |= {a["job_id"] for a in applications}
            if hidden_ids:
                before = len(unique_jobs)
                unique_jobs = [j for j in unique_jobs if j["id"] not in hidden_ids]
                logger.info(f"Scrape interaction filter: {before} → {len(unique_jobs)} jobs for user {user_id[:8]}")
        except Exception as e:
            logger.warning(f"Could not filter scrape results by interactions: {e}")

    return {
        "success": True,
        "jobs_found": len(unique_jobs),
        "jobs_saved": saved_count,
        "jobs": unique_jobs
    }


@app.get("/api/jobs")
async def list_jobs(request: Request, limit: int = 50, offset: int = 0):
    """List all jobs, filtered by user's location prefs and interaction history if logged in"""
    user_id = await get_user_id_from_request(request)

    # When logged in, fetch a bigger batch from DB since filtering
    # (rejected/applied/skipped/location) will remove many jobs from the result.
    # Fetch up to 500 from DB so the user sees enough after filtering.
    db_limit = 500 if user_id else limit
    jobs = await get_jobs_from_db(db_limit, offset)

    if not jobs:
        # Fallback: scrape live AND save to DB so apply-with-cv can find them
        jobs = await scrape_platsbanken("jobb", max_jobs=limit)
        if jobs:
            await save_jobs_to_db(jobs)

    if not jobs:
        return {"success": True, "source": "empty", "jobs": []}

    # If logged in, load user's interaction history and filter/score jobs
    if user_id and jobs:
        import asyncio as _asyncio
        interactions_task = db_request("GET", "user_job_interactions", params={
            "user_id": f"eq.{user_id}",
            "select": "job_id,action"
        })
        # Also check applications table — belt-and-suspenders so applied jobs
        # are hidden even if the interaction log silently failed
        applications_task = db_request("GET", "applications", params={
            "user_id": f"eq.{user_id}",
            "status": "in.(sent,draft)",
            "select": "job_id"
        })
        # Fetch user's preferred locations for server-side geo filtering
        prefs_task = db_request("GET", "user_job_preferences", params={
            "user_id": f"eq.{user_id}",
            "select": "preferred_locations"
        })
        interactions, applied_applications, user_prefs = await _asyncio.gather(
            interactions_task, applications_task, prefs_task
        )
        interactions = interactions or []
        applied_applications = applied_applications or []

        # --- SERVER-SIDE LOCATION FILTER ---
        # Convert user's preferred kommun IDs to labels + county names, then filter jobs
        preferred_locs = []
        if user_prefs and len(user_prefs) > 0:
            preferred_locs = user_prefs[0].get("preferred_locations") or []
        if preferred_locs and "anywhere" not in preferred_locs:
            loc_ids = [lid for lid in preferred_locs if lid not in ("remote", "anywhere")]
            if loc_ids:
                label_lookup = await fetch_municipality_labels()
                municipality_labels_lower = [
                    label_lookup[mid].lower() for mid in loc_ids if mid in label_lookup
                ]
                county_labels_lower = _get_county_labels_for_kommun_ids(loc_ids)
                if municipality_labels_lower:
                    before = len(jobs)
                    jobs = [j for j in jobs if _job_in_municipalities(j, municipality_labels_lower, county_labels_lower)]
                    logger.info(f"Server geo filter: {before} → {len(jobs)} jobs for user {user_id[:8]}")

        rejected_ids = {i["job_id"] for i in interactions if i["action"] == "rejected"}
        applied_ids = {i["job_id"] for i in interactions if i["action"] == "applied"}
        # Merge in job IDs from applications table (sent/draft = user already acted on these)
        applied_ids |= {a["job_id"] for a in applied_applications}
        skipped_ids = {i["job_id"] for i in interactions if i["action"] == "skipped"}

        # Hard-filter rejected and applied jobs out of the feed
        # Skipped jobs are moved to the end (deprioritized)
        active_jobs = [j for j in jobs if j["id"] not in rejected_ids and j["id"] not in applied_ids]
        skipped_jobs = [j for j in active_jobs if j["id"] in skipped_ids]
        fresh_jobs = [j for j in active_jobs if j["id"] not in skipped_ids]

        # Within each group, prioritize jobs with contact_email (direct apply) first
        def has_email(j):
            email = j.get("contact_email")
            return bool(email and "@" in str(email))

        fresh_with_email = [j for j in fresh_jobs if has_email(j)]
        fresh_without_email = [j for j in fresh_jobs if not has_email(j)]
        skipped_with_email = [j for j in skipped_jobs if has_email(j)]
        skipped_without_email = [j for j in skipped_jobs if not has_email(j)]

        jobs = fresh_with_email + fresh_without_email + skipped_with_email + skipped_without_email

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
    user_id = await get_user_id_from_request(request, required=True)

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
    }, on_conflict="user_id,job_id,action")

    return {"success": True, "job_id": job_id, "action": action}


@app.post("/api/jobs/{job_id}/letter")
async def create_letter(job_id: str, request: GenerateLetterRequest = None, req: Request = None):
    """Generate cover letter for a job"""
    user_id = await get_user_id_from_request(req) if req else None

    # Get job from database
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[0]
    cv_text = request.user_cv_text if request else None

    # Fetch user profile from DB so cover letter uses correct name/location/etc
    user_profile = None
    if user_id:
        profiles_result = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        user_profile = profiles_result[0] if profiles_result else None

    letter = await generate_cover_letter(job, cv_text, user_profile, user_id=user_id)

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
    user_id = await get_user_id_from_request(req) or "default_user"

    data = {
        "job_id": request.job_id,
        "user_id": user_id,
        "cover_letter": request.cover_letter,
        "status": request.status,
        "created_at": datetime.now().isoformat()
    }

    result = await db_request("POST", "applications", data=data, on_conflict="user_id,job_id")
    if result:
        return {"success": True, "application": result[0]}
    raise HTTPException(status_code=500, detail="Could not save application")


@app.get("/api/applications")
async def list_applications(request: Request):
    """List applications for the logged-in user"""
    user_id = await get_user_id_from_request(request)
    apps = await get_applications_from_db(user_id=user_id)
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


@app.get("/api/aktivitetsrapport")
async def generate_aktivitetsrapport(request: Request, month: str = None):
    """Generate a monthly Aktivitetsrapport PDF for A-kassan/Arbetsförmedlingen.
    ?month=2026-02 format. Defaults to current month."""
    from fpdf import FPDF
    from fastapi.responses import Response as RawResponse

    user_id = await get_user_id_from_request(request)

    # Determine month
    if not month:
        month = datetime.now().strftime("%Y-%m")
    try:
        year, mon = month.split("-")
        year = int(year)
        mon = int(mon)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Ogiltigt månadsformat. Använd YYYY-MM.")

    month_names = [
        "januari", "februari", "mars", "april", "maj", "juni",
        "juli", "augusti", "september", "oktober", "november", "december"
    ]
    month_label = month_names[mon - 1]

    # Get user profile
    sender_name = "Namn"
    if user_id:
        profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        if profiles:
            sender_name = profiles[0].get("full_name", sender_name)

    # Get sent applications for this month
    apps = await get_applications_from_db(user_id=user_id)
    month_apps = []
    for a in apps:
        if a.get("status") != "sent":
            continue
        d = (a.get("sent_at") or a.get("created_at") or "")[:7]
        if d == month:
            month_apps.append(a)

    # Sort by date
    month_apps.sort(key=lambda a: a.get("sent_at") or a.get("created_at") or "")

    # Build PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, f"Aktivitetsrapport {month_label} {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Subtitle
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Sokta jobb / Jobb med annons", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, sender_name, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Period: {month_label} {year}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Table header
    col_widths = [25, 50, 45, 30, 40]
    headers = ["Datum", "Yrkesroll", "Arbetsgivare", "Omfattning", "Ort"]

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(30, 30, 30)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, fill=True)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    for a in month_apps:
        sent_date = (a.get("sent_at") or a.get("created_at") or "")[:10]
        try:
            dt = datetime.fromisoformat(sent_date)
            datum = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            datum = sent_date

        yrkesroll = (a.get("job_title") or "")[:30]
        arbetsgivare = (a.get("company") or "")[:25]
        omfattning = a.get("working_hours") or "Heltid"
        ort = (a.get("location") or "")[:22]

        pdf.cell(col_widths[0], 7, datum, border=1)
        pdf.cell(col_widths[1], 7, yrkesroll, border=1)
        pdf.cell(col_widths[2], 7, arbetsgivare, border=1)
        pdf.cell(col_widths[3], 7, omfattning, border=1)
        pdf.cell(col_widths[4], 7, ort, border=1)
        pdf.ln()

    # Summary
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, f"Totalt: {len(month_apps)} ansokningar", new_x="LMARGIN", new_y="NEXT")

    # Footer
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Genererad {datetime.now().strftime('%Y-%m-%d')} via Platsbanken AI", new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    filename = f"Aktivitetsrapport_{month_label.upper()}{year}.pdf"

    return RawResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/jobs/{job_id}/save")
async def save_job(job_id: str, request: Request):
    """Save/bookmark a job for later"""
    user_id = await get_user_id_from_request(request) or "default_user"

    # Helper: log interaction (non-blocking)
    async def log_save_interaction():
        try:
            await db_request("POST", "user_job_interactions", data={
                "user_id": user_id,
                "job_id": job_id,
                "action": "saved",
                "created_at": datetime.now().isoformat()
            })
        except Exception:
            pass

    # Check if application already exists
    existing = await db_request("GET", "applications", params={
        "job_id": f"eq.{job_id}",
        "user_id": f"eq.{user_id}"
    })

    if existing and len(existing) > 0:
        current_status = existing[0].get("status", "")
        # Don't downgrade important statuses — sent/interview/offer should not revert to saved
        protected_statuses = ["sent", "interview", "offer"]
        if current_status in protected_statuses:
            return {"success": True, "application": existing[0], "note": f"Already has status '{current_status}', not changed to saved"}

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
                await log_save_interaction()
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
            await log_save_interaction()
            return {"success": True, "application": result[0]}

    raise HTTPException(status_code=500, detail="Could not save job")


@app.delete("/api/jobs/{job_id}/save")
async def unsave_job(job_id: str, request: Request):
    """Remove a saved job"""
    user_id = await get_user_id_from_request(request) or "default_user"

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
async def get_stats(request: Request):
    """Get statistics for the logged-in user"""
    user_id = await get_user_id_from_request(request)
    jobs = await get_jobs_from_db(1000)
    apps = await get_applications_from_db(user_id=user_id)

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
            "saved": len([a for a in (apps or []) if a.get("status") == "saved"]),
            "drafts": len([a for a in (apps or []) if a.get("status") == "draft"]),
            "sent": len([a for a in (apps or []) if a.get("status") == "sent"]),
            "interviews": len([a for a in (apps or []) if a.get("status") == "interview"]),
            "deadline_today": deadline_today
        }
    }


# ============== CV ENDPOINTS ==============

@app.get("/api/cv/branscher")
async def list_cv_branscher():
    """List all available CV branscher/categories"""
    return {"success": True, "branscher": CV_BRANSCHER}


@app.post("/api/cv/master")
async def save_master_cv(request: Request, master_cv: MasterCV):
    """
    Save complete Master CV with all structured data.
    This is the source of truth - all bransch-CVs are generated from this.
    """
    user_id = await get_user_id_from_request(request, required=True)

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
    await db_request("POST", "user_profiles", data=profile_data, on_conflict="user_id")

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
    user_id = await get_user_id_from_request(request)
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


@app.get("/api/cv/export/{bransch_id}")
async def export_cv_for_bransch(bransch_id: str, user_id: str = "default_user"):
    """
    Export CV data filtered for a specific bransch.
    Returns structured data ready for PDF template.
    """
    # Get master CV
    master_cv_response = await get_master_cv(user_id)
    if not master_cv_response.get("master_cv"):
        raise HTTPException(status_code=404, detail="No Master CV found")

    master = master_cv_response["master_cv"]
    profile = master["profile"]

    # Filter experiences by bransch category
    all_experiences = master.get("experiences", [])
    filtered_experiences = [
        exp for exp in all_experiences
        if bransch_id in exp.get("categories", [])
    ]

    # Get skills for this bransch (and 'all' skills)
    all_skills = master.get("skills", [])
    bransch_skills = [s for s in all_skills if s.get("category") in [bransch_id, "all"]]

    # Build technical skills string if tech bransch
    technical_skills = None
    if bransch_id in ["tech", "content"]:
        tech_skill_texts = [s.get("skill_text") for s in bransch_skills if s.get("skill_type") == "technical"]
        if tech_skill_texts:
            technical_skills = ", ".join(tech_skill_texts)

    # Get bransch info
    bransch_info = next((v for v in CV_BRANSCHER if v["id"] == bransch_id), None)

    return {
        "success": True,
        "bransch": bransch_info,
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


@app.post("/api/cv/suggest-bransch")
async def suggest_new_bransch(job_keywords: List[str], user_id: str = "default_user"):
    """
    Analyze job search keywords and suggest if user should create a new bransch-CV.
    Returns suggestion if pattern detected and user doesn't have that bransch.
    """
    # Count keyword matches per bransch
    bransch_scores = {}
    for bransch in CV_BRANSCHER:
        score = 0
        for keyword in job_keywords:
            if any(vk in keyword.lower() for vk in bransch.get("keywords", [])):
                score += 1
        if score > 0:
            bransch_scores[bransch["id"]] = score

    if not bransch_scores:
        return {"success": True, "suggestion": None}

    # Find top bransch
    top_bransch_id = max(bransch_scores, key=bransch_scores.get)
    top_score = bransch_scores[top_bransch_id]

    # Only suggest if significant pattern (3+ matches)
    if top_score < 3:
        return {"success": True, "suggestion": None}

    # Check if user has experiences tagged for this bransch
    experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}",
        "categories": f"cs.{{{top_bransch_id}}}"  # contains
    })

    has_bransch_cv = bool(experiences)

    if has_bransch_cv:
        return {"success": True, "suggestion": None, "message": f"Du har redan ett {top_bransch_id}-CV!"}

    # Get bransch info
    bransch_info = next((v for v in CV_BRANSCHER if v["id"] == top_bransch_id), None)

    return {
        "success": True,
        "suggestion": {
            "bransch_id": top_bransch_id,
            "bransch_name": bransch_info["name"],
            "bransch_emoji": bransch_info["emoji"],
            "match_count": top_score,
            "message": f"Hej! Jag ser att du söker många jobb inom {bransch_info['name'].lower()}. Vill du skapa ett CV anpassat för den branschen?"
        }
    }


@app.post("/api/cv/generate-branscher")
async def generate_cv_branscher(request: Request):
    """Generate all CV bransch versions from master CV"""
    user_id = await get_user_id_from_request(request, required=True)

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

    # Generate all bransch-CVs
    generated = await generate_all_bransch_cvs(master_cv, user_id)

    return {
        "success": True,
        "message": f"Genererade {len(generated)} CV-versioner!",
        "cvs": generated
    }


@app.get("/api/cv/all")
async def get_user_cvs(request: Request):
    """Get all user's generated CV versions"""
    user_id = await get_user_id_from_request(request)
    if not user_id:
        return {"success": True, "cvs": [], "message": "Ej inloggad"}

    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "order": "vibe_id.asc"
    })

    return {"success": True, "cvs": cvs or [], "user_id": user_id}


@app.get("/api/cv/{bransch_id}")
async def get_cv_by_bransch(bransch_id: str, user_id: str = "default_user"):
    """Get a specific CV version"""
    cvs = await db_request("GET", "user_cvs", params={
        "user_id": f"eq.{user_id}",
        "vibe_id": f"eq.{bransch_id}"
    })

    if cvs and len(cvs) > 0:
        return {"success": True, "cv": cvs[0]}

    raise HTTPException(status_code=404, detail=f"Ingen CV for {bransch_id}")


@app.patch("/api/cv/{bransch_id}")
async def update_cv(bransch_id: str, cv_text: str, user_id: str = "default_user"):
    """Update a CV version (after user edits)"""
    result = await db_request("PATCH", "user_cvs",
        data={"cv_text": cv_text, "updated_at": datetime.now().isoformat()},
        params={"user_id": f"eq.{user_id}", "vibe_id": f"eq.{bransch_id}"}
    )

    if result:
        return {"success": True, "cv": result[0]}

    raise HTTPException(status_code=500, detail="Kunde inte uppdatera CV")


# ============== MASTER CV & BRANSCH-CVS ENDPOINTS ==============

@app.get("/api/master-cv")
async def get_full_master_cv(request: Request):
    """Get complete Master CV data including all sections (experiences, education, projects, certifications, awards, volunteer, skills)"""
    user_id = await get_user_id_from_request(request)
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
    user_id = await get_user_id_from_request(request)
    if not user_id:
        return {"success": False, "bransch_cvs": []}

    # Fetch bransch-CVs from database
    bransch_cvs = await db_request("GET", "bransch_cvs", params={
        "user_id": f"eq.{user_id}", "order": "created_at.desc"
    }) or []

    return {"bransch_cvs": bransch_cvs}


def _build_master_cv_pdf(profile: Dict, experiences: list, education: list, volunteer: list, awards: list, skills: list, projects: list = None, certifications: list = None) -> bytes:
    """Build a Master CV PDF using fpdf2 and return raw bytes."""
    from fpdf import FPDF

    class CVPDF(FPDF):
        def header(self):
            pass
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"Sida {self.page_no()}/{{nb}}", align="C")

    pdf = CVPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # -- Header: Name --
    name = profile.get("full_name") or "Namn saknas"
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, name, new_x="LMARGIN", new_y="NEXT")

    # -- Contact line --
    contact_parts = []
    if profile.get("email"):
        contact_parts.append(profile["email"])
    if profile.get("phone"):
        contact_parts.append(profile["phone"])
    if profile.get("location"):
        contact_parts.append(profile["location"])
    if contact_parts:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, "  |  ".join(contact_parts), new_x="LMARGIN", new_y="NEXT")

    # Links line (LinkedIn, portfolio)
    links = []
    if profile.get("linkedin"):
        links.append(profile["linkedin"])
    if profile.get("portfolio_url"):
        links.append(profile["portfolio_url"])
    if links:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 130, 200)
        pdf.cell(0, 5, "  |  ".join(links), new_x="LMARGIN", new_y="NEXT")

    # Drivers license & languages
    extras = []
    if profile.get("drivers_license"):
        extras.append("Korkort: Ja")
    langs = profile.get("languages") or []
    if langs:
        extras.append("Sprak: " + ", ".join(langs))
    if extras:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "  |  ".join(extras), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)

    # Divider line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    def section_heading(title: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(60, 130, 200)
        pdf.line(10, pdf.get_y(), 70, pdf.get_y())
        pdf.ln(3)

    def safe_text(text):
        """Clean text for PDF output."""
        if not text:
            return ""
        return str(text)

    # -- Experiences --
    if experiences:
        section_heading("Erfarenhet")
        for exp in experiences:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            title = safe_text(exp.get("title", ""))
            company = safe_text(exp.get("company", ""))
            pdf.cell(0, 6, f"{title} — {company}", new_x="LMARGIN", new_y="NEXT")

            meta_parts = []
            if exp.get("location"):
                meta_parts.append(safe_text(exp["location"]))
            if exp.get("dates"):
                meta_parts.append(safe_text(exp["dates"]))
            if meta_parts:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "  |  ".join(meta_parts), new_x="LMARGIN", new_y="NEXT")

            bullets = exp.get("bullets") or []
            if bullets:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                for b in bullets:
                    bt = safe_text(b).strip()
                    if bt:
                        pdf.cell(5)
                        pdf.multi_cell(0, 4.5, f"• {bt}")
            pdf.ln(3)

    # -- Education --
    if education:
        section_heading("Utbildning")
        for edu in education:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            degree = safe_text(edu.get("degree", ""))
            school = safe_text(edu.get("school", ""))
            pdf.cell(0, 6, f"{degree} — {school}", new_x="LMARGIN", new_y="NEXT")

            meta_parts = []
            if edu.get("location"):
                meta_parts.append(safe_text(edu["location"]))
            if edu.get("dates"):
                meta_parts.append(safe_text(edu["dates"]))
            if meta_parts:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "  |  ".join(meta_parts), new_x="LMARGIN", new_y="NEXT")

            bullets = edu.get("bullets") or []
            if bullets:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                for b in bullets:
                    bt = safe_text(b).strip()
                    if bt:
                        pdf.cell(5)
                        pdf.multi_cell(0, 4.5, f"• {bt}")
            pdf.ln(3)

    # -- Projects --
    if projects:
        section_heading("Projekt")
        for proj in projects:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            pname = safe_text(proj.get("name") or proj.get("title", ""))
            pdf.cell(0, 6, pname, new_x="LMARGIN", new_y="NEXT")
            desc = safe_text(proj.get("description", ""))
            if desc:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(0, 4.5, desc)
            pdf.ln(2)

    # -- Volunteer --
    if volunteer:
        section_heading("Ideellt arbete")
        for vol in volunteer:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            org = safe_text(vol.get("organization", ""))
            dates = safe_text(vol.get("dates", ""))
            pdf.cell(0, 6, f"{org}" + (f" ({dates})" if dates else ""), new_x="LMARGIN", new_y="NEXT")

            bullets = vol.get("bullets") or []
            if bullets:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                for b in bullets:
                    bt = safe_text(b).strip()
                    if bt:
                        pdf.cell(5)
                        pdf.multi_cell(0, 4.5, f"• {bt}")
            pdf.ln(2)

    # -- Certifications --
    if certifications:
        section_heading("Certifieringar")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for cert in certifications:
            cname = safe_text(cert.get("name") or cert.get("cert_name") or cert.get("title", ""))
            if cname:
                pdf.cell(5)
                pdf.cell(0, 5, f"• {cname}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # -- Awards --
    if awards:
        section_heading("Utmarkelser")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for a in awards:
            award_text = safe_text(a.get("award_text") if isinstance(a, dict) else a)
            if award_text:
                pdf.cell(5)
                pdf.cell(0, 5, f"• {award_text}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # -- Skills --
    if skills:
        section_heading("Kompetenser")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        skill_texts = [safe_text(s.get("skill_text", "")) for s in skills if s.get("skill_text")]
        if skill_texts:
            pdf.multi_cell(0, 5, "  •  ".join(skill_texts))
        pdf.ln(2)

    return pdf.output()


@app.get("/api/master-cv/download-pdf")
async def download_master_cv_pdf(request: Request):
    """Generate and download Master CV as PDF"""
    from fastapi.responses import Response
    user_id = await get_user_id_from_request(request, required=True)

    # Fetch profile
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    profile = profiles[0] if profiles else {"full_name": "", "email": "", "phone": "", "location": ""}

    # Fetch all sections
    experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    education = await db_request("GET", "user_education", params={
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
    projects = await db_request("GET", "tech_projects", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    certifications = await db_request("GET", "user_certifications", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    pdf_bytes = _build_master_cv_pdf(profile, experiences, education, volunteer, awards, skills, projects, certifications)

    # Build filename from user's name
    name = (profile.get("full_name") or "CV").replace(" ", "_")
    filename = f"Master_CV_{name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/bransch-cvs/{cv_id}/download-pdf")
async def download_bransch_cv_pdf(cv_id: str, request: Request):
    """Generate and download a specific Bransch-CV as PDF"""
    from fastapi.responses import Response
    from fpdf import FPDF
    user_id = await get_user_id_from_request(request, required=True)

    # Fetch the specific Bransch-CV
    cv_result = await db_request("GET", "bransch_cvs", params={
        "id": f"eq.{cv_id}",
        "user_id": f"eq.{user_id}"
    })

    if not cv_result or len(cv_result) == 0:
        raise HTTPException(status_code=404, detail="Bransch-CV hittades inte")

    cv = cv_result[0]
    cv_text = cv.get("cv_text", "")
    category = cv.get("category", "CV")

    # Fetch profile for header
    profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
    profile = profiles[0] if profiles else {}
    name = profile.get("full_name") or "Namn"

    # Build PDF from CV text
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT")

    # Contact line
    contact_parts = []
    if profile.get("email"):
        contact_parts.append(profile["email"])
    if profile.get("phone"):
        contact_parts.append(profile["phone"])
    if profile.get("location"):
        contact_parts.append(profile["location"])
    if contact_parts:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, "  |  ".join(contact_parts), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(60, 130, 200)
    pdf.cell(0, 6, f"CV — {category}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # CV body text
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    for line in cv_text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
        elif line.startswith("##") or line.startswith("**") or line.isupper():
            # Section heading
            clean = line.replace("##", "").replace("**", "").strip()
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(0, 7, clean, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
        elif line.startswith("- ") or line.startswith("• "):
            bullet_text = line.lstrip("-• ").strip()
            pdf.cell(5)
            pdf.multi_cell(0, 5, f"• {bullet_text}")
        else:
            pdf.multi_cell(0, 5, line)

    pdf_bytes = pdf.output()
    safe_name = name.replace(" ", "_")
    safe_cat = category.replace(" ", "_").replace("&", "")
    filename = f"CV_{safe_name}_{safe_cat}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )



@app.post("/api/jobs/{job_id}/qualification-check")
async def qualification_check(job_id: str, request: Request):
    """
    Quick pre-check: Does the user seem qualified for this job?
    Uses Haiku (cheap + fast) to analyze job requirements vs user profile.
    Returns { qualified: bool, reason: string, suggested_keywords: [] }
    Called BEFORE generating cover letter to save API credits.
    """
    user_id = await get_user_id_from_request(request)

    # Get job
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    if not jobs:
        try:
            body = await request.json()
            job = body.get("job")
        except Exception:
            job = None
        if not job:
            raise HTTPException(status_code=404, detail="Jobbet hittades inte")
    else:
        job = jobs[0]

    # Get user profile + CV summary
    user_profile = None
    cv_summary = ""
    if user_id:
        profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        user_profile = profiles[0] if profiles else None

        # Get master CV experiences for a quick summary
        experiences = await db_request("GET", "user_experiences", params={
            "user_id": f"eq.{user_id}",
            "select": "title,company,categories",
            "order": "sort_order.asc",
            "limit": "8"
        })
        if experiences:
            cv_summary = ", ".join([f"{e.get('title', '')} ({e.get('company', '')})" for e in experiences])

    job_title = job.get("title", "")
    job_desc = job.get("description", "")[:2000]  # Keep prompt small
    profile_info = ""
    if user_profile:
        profile_info = f"""
Användarens profil:
- Namn: {user_profile.get('full_name', 'Okänt')}
- Utbildning: Gymnasium
- Körkort: {'Ja' if user_profile.get('drivers_license') else 'Nej'}
- Erfarenhet: {cv_summary or 'Kundtjänst, butik, restaurang, café'}
"""

    prompt = f"""Analysera om denna jobbsökare verkar kvalificerad för jobbet nedan.
Svara BARA med JSON (ingen markdown, inga kodblock):
{{"qualified": true/false, "reason": "kort förklaring på svenska", "suggested_keywords": ["ord att filtrera bort"]}}

REGLER:
- qualified=false BARA om jobbet har TYDLIGA formella krav som saknas (doktorsexamen, legitimation, certifiering, 5+ års specifik erfarenhet)
- Om jobbet är brett/generellt (butik, kundtjänst, servitör, lager, etc) → qualified=true
- Om osäkert → qualified=true (hellre söka för mycket än för lite)
- suggested_keywords: bara om qualified=false — föreslå 1-3 sökord som kan filtrera bort liknande jobb

JOBB:
Titel: {job_title}
Beskrivning: {job_desc}

{profile_info}"""

    result = await call_claude_api(prompt, model="claude-haiku-4-5-20251001", max_tokens=200, timeout=10)

    if not result:
        # If API fails, don't block the user — assume qualified
        return {"success": True, "qualified": True, "reason": "", "suggested_keywords": []}

    # Parse JSON response
    try:
        import json
        # Strip markdown code blocks if present
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        return {
            "success": True,
            "qualified": parsed.get("qualified", True),
            "reason": parsed.get("reason", ""),
            "suggested_keywords": parsed.get("suggested_keywords", [])
        }
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Could not parse qualification check response: {e}, raw: {result[:200]}")
        return {"success": True, "qualified": True, "reason": "", "suggested_keywords": []}


@app.post("/api/jobs/{job_id}/apply-with-cv")
async def apply_with_cv(request: Request, job_id: str):
    """
    Smart apply: Auto-selects best CV, generates cover letter, returns both.
    This is the main "one-click apply" endpoint.
    """
    # Get user_id from auth token (optional - works without login too)
    user_id = await get_user_id_from_request(request)

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

    # Match job to best bransch
    best_bransch = match_job_to_bransch(job.get("title", ""), job.get("description", ""))
    logger.info(f"Job '{job.get('title')}' matched to bransch: {best_bransch}")

    # Fetch CV and user profile in parallel to save time
    cv = None
    user_profile = None
    if user_id:
        import asyncio as _asyncio
        cvs_result, profiles_result = await _asyncio.gather(
            db_request("GET", "user_cvs", params={"user_id": f"eq.{user_id}", "vibe_id": f"eq.{best_bransch}"}),
            db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        )
        cv = cvs_result[0] if cvs_result else None
        user_profile = profiles_result[0] if profiles_result else None

    # Generate cover letter (works with or without CV/profile)
    cv_text_for_letter = cv.get("cv_text") if cv else None
    extra_hints = body.get("extra_hints")
    cover_letter = await generate_cover_letter(job, cv_text_for_letter, user_profile, extra_hints, user_id=user_id)

    # Log 'applied' interaction server-side so job is hidden from feed
    # AND auto-save application so it appears in Ansökningar + Aktivitetsrapport
    if user_id:
        await db_request("POST", "user_job_interactions", data={
            "user_id": user_id,
            "job_id": job_id,
            "action": "applied",
            "context": {"source": "apply_with_cv"}
        })
        await db_request("POST", "applications", data={
            "job_id": job_id,
            "user_id": user_id,
            "cover_letter": cover_letter,
            "status": "sent",
            "created_at": datetime.now().isoformat(),
            "sent_at": datetime.now().isoformat()
        }, on_conflict="user_id,job_id")

    # No auto-draft: Gmail draft is only created when user clicks "Spara i Gmail med bilagor"
    # (handled by POST /api/jobs/{job_id}/save-draft)
    contact_email = job.get("contact_email")
    contact_name = job.get("contact_name")
    job_title = job.get("title", "Tjänst")
    sender_name = user_profile.get("full_name", "Linnea Moritz") if user_profile else "Linnea Moritz"
    subject = f"Ansökan: {job_title} – {sender_name}"

    return {
        "success": True,
        "job": {
            "id": job.get("id"),
            "title": job_title,
            "company": job.get("company"),
            "contact_email": contact_email,
            "contact_name": contact_name
        },
        "matched_bransch": best_bransch,
        "cv_filename": get_cv_pdf_filename(best_bransch),
        "cv": cv,
        "cover_letter": cover_letter,
        "draft_created": False,
        "draft_id": None,
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


@app.post("/api/review-swedish")
async def review_swedish(request: Request):
    """
    Final-step Swedish language review using LanguageTool.
    Only applies HIGH-CONFIDENCE fixes (spelling, grammar, compounding).
    Skips style suggestions and uncertain replacements that could make text worse.
    Returns details of each change so the user can see what happened.
    """
    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Ingen text att granska")

    # Categories we trust enough to auto-apply
    SAFE_CATEGORIES = {
        "TYPOS", "SPELLING", "COMPOUNDING", "GRAMMAR",
        "PUNCTUATION", "CASING", "CONFUSED_WORDS",
    }
    # Categories we skip — style suggestions often make text worse
    SKIP_CATEGORIES = {
        "STYLE", "REDUNDANCY", "TYPOGRAPHY", "MISC",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.languagetool.org/v2/check",
                data={
                    "text": text,
                    "language": "sv",
                    "enabledOnly": "false",
                },
                timeout=15
            )

            if response.status_code != 200:
                logger.warning(f"LanguageTool returned {response.status_code}")
                return {"success": True, "reviewed_text": text, "fixes": 0, "changes": []}

            result = response.json()
            matches = result.get("matches", [])

            if not matches:
                return {"success": True, "reviewed_text": text, "fixes": 0, "changes": []}

            # Filter matches — only apply safe, high-confidence fixes
            fixed_text = text
            applied = 0
            skipped = 0
            changes = []

            for match in sorted(matches, key=lambda m: m["offset"], reverse=True):
                replacements = match.get("replacements", [])
                if not replacements:
                    continue

                rule = match.get("rule", {})
                category = rule.get("category", {}).get("id", "UNKNOWN")
                issue_type = rule.get("issueType", "")
                original = text[match["offset"]:match["offset"] + match["length"]]
                best_fix = replacements[0]["value"]

                # Skip if the replacement is drastically different (likely wrong)
                if len(best_fix) > len(original) * 3 or len(best_fix) < len(original) * 0.3:
                    skipped += 1
                    logger.info(f"LT skip (size mismatch): '{original}' → '{best_fix}' [{category}]")
                    continue

                # Skip style/misc suggestions — they often make text worse
                if category in SKIP_CATEGORIES or issue_type == "style":
                    skipped += 1
                    logger.info(f"LT skip (style): '{original}' → '{best_fix}' [{category}]")
                    continue

                # Skip if category is unknown and we're not confident
                if category not in SAFE_CATEGORIES and category != "UNKNOWN":
                    skipped += 1
                    logger.info(f"LT skip (unknown cat): '{original}' → '{best_fix}' [{category}]")
                    continue

                # Apply the fix
                offset = match["offset"]
                length = match["length"]
                fixed_text = fixed_text[:offset] + best_fix + fixed_text[offset + length:]
                applied += 1
                changes.append({
                    "original": original,
                    "replacement": best_fix,
                    "category": category,
                    "message": match.get("message", ""),
                })
                logger.info(f"LT applied: '{original}' → '{best_fix}' [{category}]")

            return {
                "success": True,
                "reviewed_text": fixed_text,
                "fixes": applied,
                "skipped": skipped,
                "total_issues": len(matches),
                "changes": changes,
            }
    except Exception as e:
        logger.error(f"Swedish review error: {e}")
        return {"success": True, "reviewed_text": text, "fixes": 0, "changes": []}


@app.post("/api/jobs/{job_id}/cover-letter-pdf")
async def download_cover_letter_pdf(request: Request, job_id: str):
    """Generate and return a formatted cover letter PDF for download."""
    from fastapi.responses import Response as RawResponse

    user_id = await get_user_id_from_request(request)

    try:
        body = await request.json()
    except Exception:
        body = {}

    cover_letter_text = body.get("cover_letter", "")
    if not cover_letter_text:
        raise HTTPException(status_code=400, detail="Inget brev att ladda ner")

    # Get job info for subject line
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    job = jobs[0] if jobs else body.get("job", {})
    job_title = job.get("title", body.get("job_title", "Tjänst"))
    company = job.get("company", body.get("company", ""))

    # Get user profile for sender info
    sender_name = "Jobbsökare"
    sender_phone = ""
    sender_email_addr = ""
    sender_location = ""
    if user_id:
        profiles = await db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"})
        if profiles:
            p = profiles[0]
            sender_name = p.get("full_name", sender_name)
            sender_phone = p.get("phone", "")
            sender_email_addr = p.get("email", "")
            sender_location = p.get("location", "")

    pdf_bytes = generate_cover_letter_pdf(
        cover_letter_text,
        sender_name=sender_name,
        sender_phone=sender_phone,
        sender_email=sender_email_addr,
        sender_location=sender_location,
        job_title=job_title,
        company=company,
    )

    company_clean = re.sub(r'[^\w\s-]', '', company).strip().replace(' ', '_')
    if company_clean:
        filename = f"Personligt_Brev_{company_clean}_{sender_name.replace(' ', '_')}.pdf"
    else:
        filename = f"Personligt_Brev_{sender_name.replace(' ', '_')}.pdf"
    return RawResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/jobs/{job_id}/answer-question")
async def answer_application_question(request: Request, job_id: str):
    """
    Answer a free-form application question using AI + user profile + job context.
    Used for external applications that have text fields like 'Varför vill du jobba här?'
    """
    user_id = await get_user_id_from_request(request)

    try:
        body = await request.json()
    except Exception:
        body = {}

    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Ingen fråga angiven")

    # Get job info
    jobs = await db_request("GET", "jobs", params={"id": f"eq.{job_id}"})
    job = jobs[0] if jobs else body.get("job", {})

    # Get user profile + CV for context
    user_profile = None
    cv_text = None
    style_prefs = None
    if user_id:
        import asyncio as _asyncio
        profiles_r, cvs_r, prefs_r = await _asyncio.gather(
            db_request("GET", "user_profiles", params={"user_id": f"eq.{user_id}"}),
            db_request("GET", "user_cvs", params={"user_id": f"eq.{user_id}", "limit": "1"}),
            db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})
        )
        user_profile = profiles_r[0] if profiles_r else None
        cv_text = cvs_r[0].get("cv_text") if cvs_r else None
        style_prefs = prefs_r[0] if prefs_r else None

    p = user_profile or {}
    name = p.get("full_name", "Jobbsökare")
    location = p.get("location", "")

    # Build style instructions
    style_hint = ""
    if style_prefs:
        if style_prefs.get("tone"):
            style_hint += f"\nAnvändarens ton: {style_prefs['tone']}"
        avoid = style_prefs.get("avoid_phrases") or []
        if avoid:
            style_hint += f"\nUndvik dessa fraser: {', '.join(avoid)}"

    prompt = f"""Svara på en ansökningsfråga på svenska. Svaret ska vara personligt, ärligt och relevant.

FRÅGAN SOM ARBETSGIVAREN STÄLLER:
"{question}"

JOBBET:
- Titel: {job.get('title', 'Okänd')}
- Företag: {job.get('company', 'Okänt')}
- Plats: {job.get('location', '')}
- Beskrivning: {job.get('description', '')[:2000]}

OM SÖKANDEN:
- Namn: {name}
- Bor: {location}
{f'- CV-sammanfattning: {cv_text[:1000]}' if cv_text else ''}
{style_hint}

INSTRUKTIONER:
1. Svara direkt på frågan — inga onödiga inledningar
2. 50-150 ord, kärnfullt och personligt
3. Referera till specifika delar av jobbeskrivningen som visar varför sökanden passar
4. Naturlig, varm svenska — inte krystad eller generisk
5. ALDRIG nämn konst, målning, utställningar eller Shopify
6. Svaret ska kunna klistras in direkt i ett webbformulär

{SWEDISH_LANGUAGE_RULES}"""

    if not ANTHROPIC_API_KEY:
        return {"success": True, "answer": f"Jag är intresserad av tjänsten som {job.get('title', 'denna roll')} och tror att min bakgrund passar bra."}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            data = res.json()
            answer = data.get("content", [{}])[0].get("text", "").strip()
            return {"success": True, "answer": answer}
    except Exception as e:
        logger.error(f"Answer question error: {e}")
        raise HTTPException(status_code=500, detail="Kunde inte generera svar")


@app.post("/api/jobs/{job_id}/save-draft")
async def save_gmail_draft_with_attachments(request: Request, job_id: str):
    """
    Create (or update) a Gmail draft with the edited cover letter + PDF attachments.
    Called from the ApplyModal when the user clicks 'Spara i Gmail med bilagor'.
    Requires Gmail OAuth to be connected.
    """
    user_id = await get_user_id_from_request(request, required=True)

    try:
        body = await request.json()
    except Exception:
        body = {}

    cover_letter_text = body.get("cover_letter", "")
    bransch = body.get("bransch", "customerservice")
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

    # Short email body — cover letter goes in PDF attachment only
    email_signature = user_profile.get("email_signature", "")
    company_name = job.get("company", "")
    job_url = job.get("url", "")
    greeting = f"Hej {company_name}!" if company_name else "Hej!"
    job_ref = f"{job_title} - <a href=\"{job_url}\">{job_url}</a>" if job_url else job_title
    email_body = f"{greeting}<br><br>Jag såg er annons på Platsbanken för {job_ref}<br>"
    email_body += f"Jag kan börja omgående och är flexibel med tider. Vänligen se bifogat personligt brev och CV för min ansökan."
    email_body += f"<br><br>Vänliga hälsningar,<br>{sender_name}"
    if email_signature:
        email_body += f"<br><br>{email_signature}"

    attachments = []

    # 1. Cover letter as PDF (professional Swedish business letter design)
    sender_phone = user_profile.get("phone", "0761166109")
    sender_email_addr = user_profile.get("email", "linneamoritzCV@gmail.com")
    sender_location = user_profile.get("location", "")
    try:
        cover_letter_pdf = generate_cover_letter_pdf(
            cover_letter_text,
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_email=sender_email_addr,
            sender_location=sender_location,
            job_title=job_title,
            company=job.get("company", ""),
        )
        company_clean = re.sub(r'[^\w\s-]', '', job.get("company", "")).strip().replace(' ', '_')
        if company_clean:
            cl_filename = f"Personligt_Brev_{company_clean}_{sender_name.replace(' ', '_')}.pdf"
        else:
            cl_filename = f"Personligt_Brev_{sender_name.replace(' ', '_')}.pdf"
        attachments.append({
            "filename": cl_filename,
            "data": cover_letter_pdf
        })
    except Exception as e:
        logger.error(f"Cover letter PDF generation failed: {e}")

    # 2. Matching CV PDF
    cv_pdf_bytes = get_cv_pdf_bytes(bransch)
    if cv_pdf_bytes:
        attachments.append({
            "filename": get_cv_pdf_filename(bransch),
            "data": cv_pdf_bytes
        })

    draft_id, draft_error = await create_gmail_draft_for_user(
        user_id, contact_email, subject, email_body, attachments
    )

    if not draft_id:
        raise HTTPException(status_code=500, detail=draft_error or "Kunde inte skapa Gmail-utkast. Är Gmail kopplat?")

    return {
        "success": True,
        "draft_id": draft_id,
        "cv_filename": get_cv_pdf_filename(bransch),
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

@app.get("/api/auth/google")
async def google_auth():
    """Redirect user to Google Sign-In via Supabase OAuth."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    redirect_to = "https://platsbanken-ai.vercel.app/login"
    url = (
        f"{SUPABASE_URL}/auth/v1/authorize?provider=google"
        f"&redirect_to={redirect_to}"
        f"&query_params=prompt%3Dselect_account"
    )
    return RedirectResponse(url)


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
        {"user_id": user_id, "company": "Minerva University", "title": "Alumni Ambassador Western Europe", "location": "Stockholm", "dates": "Sep 2024 - Pågående", "bullets": ["25% tjänst med självständig planering, cirka 40 timmar i månaden", "Genomför strategisk marknadsföring genom resor till skolor och mässor i Västeuropa och Norden", "Bygger och underhåller databaser för skolkontakter, möten med SYO:er och studievägledare", "Ansvarar för logistik: bokning av flyg, hotell och transporter för stort geografiskt område"], "categories": ["office", "customerservice"], "sort_order": 1},
        {"user_id": user_id, "company": "House of Beans, Hötorgshallen", "title": "Försäljare/Barista", "location": "Stockholm", "dates": "Aug 2024 - Feb 2025", "bullets": ["Självständigt butiksansvar med försäljning av te, kaffe och choklad", "Direktförsäljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar", "Hanterade kassa, kundservice och lagerhantering"], "categories": ["restaurant", "retail"], "sort_order": 2},
        {"user_id": user_id, "company": "Profilgruppen", "title": "Anodiseringsoperatör (Feriearbete)", "location": "Åseda", "dates": "Juli 2024 - Aug 2024", "bullets": ["Utförde tungt fysiskt arbete med fokus på armlyft och materialhantering", "Arbetade på tvåskift (06.00-14.00 och 14.00-23.00)", "Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor"], "categories": ["industry"], "sort_order": 3},
        {"user_id": user_id, "company": "Max Hamburgare", "title": "Restaurangbiträde", "location": "Vetlanda", "dates": "April 2024 - Aug 2024", "bullets": ["Arbetade i högt tempo med drive-in, fritos, kök, servering, kassa och städ", "Levererade god kundservice och samarbetade effektivt med teamet under rusningstid"], "categories": ["restaurant"], "sort_order": 4},
        {"user_id": user_id, "company": "Keeping Tabs", "title": "Multimedia Technical Specialist", "location": "New York, USA", "dates": "Nov 2022 - Juni 2023", "bullets": ["Planerade och koordinerade konstsamling för Art Basel Hong Kong (70x30m skärm, Causeway Bay)", "Designade visuell merchandise och rullade ut försäljnings- och logistikkampanj", "Utvecklade partnerskap med organisationer inom konstindustrin i USA", "Ansvarade för leadgenerering, orderleverans, fakturering och kundnöjdhet"], "categories": ["art", "office"], "sort_order": 5},
        {"user_id": user_id, "company": "30 Campos Eliseos", "title": "Kubistisk målare", "location": "New York, USA", "dates": "2022 - 2024", "bullets": ["Scoutad som professionell kubistmålare till prestigefylld konstsamlargrupp grundad i Florens", "En av endast fem konstnärer utvalda bland 500+ sökande", "Deltog i utställningar i New York, Dubai, Seoul, Madrid och Florens"], "categories": ["art"], "sort_order": 6},
        {"user_id": user_id, "company": "TikTok/ByteDance", "title": "Kvalitetsgranskare - Amerikanska marknaden", "location": "Nashville, USA", "dates": "Maj 2022 - Juni 2022", "bullets": ["Granskade innehållsmoderatörernas arbete för att säkerställa att de följer riktlinjer", "Kvalitetssäkrade moderering och bidrog till förbättrade processer"], "categories": ["tech", "content"], "sort_order": 7},
        {"user_id": user_id, "company": "YouTube Ads (via Vaco)", "title": "Innehållsmoderator - Svenska marknaden", "location": "San Francisco, USA", "dates": "Feb 2022 - Juni 2022", "bullets": ["Flaggade olämplig reklam och bidrog till att utöka databaser med markerat innehåll", "Följde noggrant alla riktlinjer och samarbetade med det svenska teamet", "Deltog i regelbundna möten för att säkerställa korrekt granskning av material"], "categories": ["tech", "content"], "sort_order": 8},
        {"user_id": user_id, "company": "Clubhouse (via Vaco)", "title": "Innehållsmoderator - Skandinaviska och amerikanska marknaden", "location": "Walnut Creek, USA", "dates": "Juni 2021 - Jan 2022", "bullets": ["Granskade Trust & Safety-ärenden inom samtliga 16 kategorier för ljudbaserad social media", "Kategorier inkluderade hatiskt tal, sexuell exploatering, våldsbejakande extremism, CSAM och falsk information", "Hade fullt ansvar för att hantera alla ärenden inom svenska, norska och danska marknaden", "Identifierade brister i standardiserade arbetsrutiner och drev policyförbättringar", "Ökade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmål uppfylldes"], "categories": ["tech", "customerservice", "content"], "sort_order": 9},
        {"user_id": user_id, "company": "Svensk-amerikanska handelskammaren", "title": "Marknadsföring och försäljningsutveckling", "location": "San Francisco, USA", "dates": "Juni 2021 - Sep 2021", "bullets": ["Byggde upp nätverk med 100+ svenska startups, myndigheter och företag genom konferenser och event", "Ökade handelskammarens nätverk med 20% genom effektiv e-post- och LinkedIn-marknadsföring", "Assisterade två svenska konsultkunder med databas av 120 försäljningsleads i USA", "Organiserade kräftskiva för 80 skandinaver och amerikaner i samarbete med Norska klubben"], "categories": ["office", "customerservice"], "sort_order": 10},
        {"user_id": user_id, "company": "Minerva University", "title": "Handledare för examensprojekt", "location": "San Francisco, USA", "dates": "Sep 2020 - Maj 2021", "bullets": ["Handledde 45 studenter i deras capstone-projekt inom VR, hållbart mode, varumärkesanalys och historiska romaner", "Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stöd", "Gav kvalitativ och kvantitativ återkoppling till över 90 uppgifter och 40 lektioner"], "categories": ["office", "art"], "sort_order": 11},
        {"user_id": user_id, "company": "Kvarngården äldreboende", "title": "Timvikarie", "location": "Vetlanda", "dates": "Maj 2020 - Sep 2020", "bullets": ["Omvårdnad, medicinhantering, måltidsassistans, dokumentation och emotionellt stöd", "Gav omsorg till äldre personer med demens och Alzheimers sjukdom", "Följde noggrant covid-protokoll och arbetade både morgon- och kvällspass"], "categories": ["healthcare"], "sort_order": 12},
        {"user_id": user_id, "company": "Minerva Project", "title": "Marknadsföring/Kundservice - Global Marketing Team", "location": "Berlin & Buenos Aires", "dates": "Sep 2019 - April 2020", "bullets": ["Samarbetade med globala marknadsföringsteamet för att öka antagningen till Minerva University", "Vägledde och stöttade över 2000 sökande elever via Intercom med högkvalitativ kundservice", "Svarade på frågor från elever i över 40 länder genom Intercom och personliga möten", "Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet"], "categories": ["customerservice", "office"], "sort_order": 13},
        {"user_id": user_id, "company": "Google Ads (via Vaco)", "title": "Svensk innehållsanalytiker för gTech", "location": "Sunnyvale, USA / Seoul / Hyderabad", "dates": "Maj 2018 - April 2019", "bullets": ["Förbättrade och granskade svensk annonsering med expertkunskap inom svensk kultur och språk", "Utförde extraktion och granskning av innehåll för över 100 annonser per dag", "Arbetade i USA och på distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering", "Det svenska teamet uppnådde 100% mål för tjänstenivåavtalet"], "categories": ["tech", "content"], "sort_order": 14},
        {"user_id": user_id, "company": "Minerva Project - Student Experience Team", "title": "Evenemangskoordinator och elevhemsvärd", "location": "San Francisco, USA", "dates": "Sep 2017 - Maj 2018", "bullets": ["Organiserade 60 evenemang för 210 internationella studenter, 2-3 per vecka", "Ansvarade för möten, budgetkontroll, närvaro, schemaläggning och marknadsföring", "Organiserade stadsskattjakt där studenter upptäckte San Francisco", "Koordinerade gästföreläsare och använde mjukvara för eventlogistik"], "categories": ["office", "customerservice"], "sort_order": 15},
        {"user_id": user_id, "company": "Wallby Säteri", "title": "Gårdsvärd/Receptionist", "location": "Vetlanda", "dates": "Juni 2016 - Aug 2016", "bullets": ["Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar", "Assisterade vid cafeet och bidrog till allmän service"], "categories": ["reception", "customerservice"], "sort_order": 16},
        {"user_id": user_id, "company": "ICA Maxi Stormarknad", "title": "Kassapersonal, frukt och grönt", "location": "Vetlanda & Värmdö", "dates": "2015, 2017, 2019", "bullets": ["Arbetade i kassan, självscanningen, frukt och grönt, charken och blomavdelningen", "ICA-certifierad inom kassahantering, Trygga mat och säkerhet i butik"], "categories": ["retail"], "sort_order": 17},
        {"user_id": user_id, "company": "Coffeehouse by George", "title": "Cafépersonal", "location": "Stockholm", "dates": "2014 - 2015", "bullets": ["Kassahantering och barista", "Hög servicenivå i centralt läge"], "categories": ["restaurant"], "sort_order": 18},
        {"user_id": user_id, "company": "Siggesta Gård", "title": "Gårdsvärd/Trädgårdsarbetare", "location": "Värmdö", "dates": "2014 - 2015", "bullets": ["Kundbemötande på stor evenemangsanläggning (minigolf, restauranger, konferenser, hotell)", "Överseende roll med kommunikation mellan avdelningar. Ansvarade för marknad med ~1000 besökare/söndag", "Trädgårdsarbete: klippte gräs, rensade ogräs, planterade, skräpsortering. Körde golfbil"], "categories": ["industry", "reception"], "sort_order": 19},
    ]

    EDUCATION = [
        {"user_id": user_id, "school": "Minerva University", "degree": "B.S in Social Science, Economics and Business Administration", "location": "San Francisco, USA", "dates": "Aug 2017 - Maj 2021", "bullets": ["Världens mest innovativa universitet enligt WURI", "Antagningsgrad på 1.8% - mest selektiva universitetet i USA", "Studerade i fem länder: USA, Sydkorea, Indien, Tyskland och Argentina", "Handledde 45 studenter i examensprojekt inom fem ämnen och branscher"], "sort_order": 1},
        {"user_id": user_id, "school": "United World College Red Cross Nordic", "degree": "International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)", "location": "Flekke, Norge", "dates": "Aug 2015 - Maj 2017", "bullets": ["Utvald som toppelev från Sverige bland 120 sökande, fullt stipendium", "Bodde med 200 elever från 96 olika länder med fokus på internationell fred och förståelse", "Röda Korsets diplom: Guldutmärkelse för teamwork, frivilligarbete och ledarskap (100+ timmar)"], "sort_order": 2},
    ]

    PROFILE = {
        "user_id": user_id,
        "full_name": "Linnea Moritz",
        "email": "linneamoritz1@gmail.com",
        "phone": "0761166109",
        "location": "",
        "drivers_license": True,
        "languages": ["Svenska (Modersmål)", "Engelska (Flytande)", "Tyska (grundläggande)", "Spanska (grundläggande)", "Mandarin (HSK nivå 3)"],
        "certificates": ["B-körkort (automat)", "ICA kassahantering", "Trygga mat", "Röda Korset första hjälpen"],
        "about_me": "Serviceinriktad och stresstålig med bred internationell erfarenhet. Minerva University (1.8% antagning). Jobbat i 7 länder. Flytande svenska och engelska.",
    }

    SKILLS = [
        # General
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Kundservice"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Kommunikation"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Teamwork"},
        {"user_id": user_id, "category": "all", "skill_type": "soft", "skill_text": "Stresshantering"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Svenska (Modersmål)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Engelska (Flytande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Tyska (grundläggande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Spanska (grundläggande)"},
        {"user_id": user_id, "category": "all", "skill_type": "language", "skill_text": "Mandarin (HSK nivå 3)"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "B-körkort"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "ICA kassahantering"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "Trygga mat"},
        {"user_id": user_id, "category": "all", "skill_type": "certificate", "skill_text": "Röda Korset första hjälpen"},
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
        {"user_id": user_id, "category": "customerservice", "skill_type": "soft", "skill_text": "Problemlösning"},
        # Retail
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Kassasystem"},
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Lagerhantering"},
        {"user_id": user_id, "category": "retail", "skill_type": "technical", "skill_text": "Merförsäljning"},
    ]

    VOLUNTEER = [
        {"user_id": user_id, "organization": "LEAF (Living Environment and Future)", "dates": "2016 - 2017", "bullets": ["Ledde elevgrupp för att utbilda skolan i miljötänk. Organiserade presentationer och kampanjer", "Skapade modemagasin för att sponsra hållbart jordbruksprojekt i Ghana. Samlade in 30,000 kr"], "sort_order": 1},
        {"user_id": user_id, "organization": "The Right Solution Project", "dates": "Mars 2013 - April 2015", "bullets": ["Tog initiativ att finansiera NGO för kvinnors utbildning vid 15 års ålder", "Samlade in över 120,000 kr genom evenemang och försäljning", "Tillhandahöll 400+ vårdpaket med hygienprodukter till etiopiska skolor. Täcktes i media två gånger"], "sort_order": 2},
        {"user_id": user_id, "organization": "India Unlimited Utbytesprogram", "dates": "Nov 2014 - Feb 2015", "bullets": ["Deltog i EU-projekt för att främja fredliga relationer mellan Sverige och Indien", "Koordinerade hygienprojekt och fick kunskap om hållbar utveckling i utvecklingsländer"], "sort_order": 3},
        {"user_id": user_id, "organization": "Värmdö Församling", "dates": "2012 - 2014", "bullets": ["Ledare för 3 konfirmandgrupper under 2 år. Ledare på tre veckors sommarlager på Ängsholmen", "Svenska Kyrkan: Ledarskapskurs steg 1 och 2"], "sort_order": 4},
    ]

    AWARDS = [
        {"user_id": user_id, "award_text": "1:a pris Stockholms Konstsalong 2024 - Jurybedömd utställning, nominerad Publikens Favorit", "sort_order": 1},
        {"user_id": user_id, "award_text": "1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnärer, fick soloutställning", "sort_order": 2},
        {"user_id": user_id, "award_text": "1:a pris Murrays Creative Contest 2022 - Detroit-baserad tävling med specialdesign", "sort_order": 3},
        {"user_id": user_id, "award_text": "Global Startup Weekend Stockholm - Vinnare för Terra Finance (Google for Startups & Techstars)", "sort_order": 4},
        {"user_id": user_id, "award_text": "Tredje pris Chinese Bridge - Nationell tävling i kinesiskt språk, Bergen 2016", "sort_order": 5},
        {"user_id": user_id, "award_text": "Röda Korsets diplom - Guldutmärkelse för teamwork och ledarskap (100+ volontärtimmar)", "sort_order": 6},
        {"user_id": user_id, "award_text": "Minerva University Award for Initiative 2018", "sort_order": 7},
    ]

    COVER_LETTER_PREFS = {
        "user_id": user_id,
        "tone": "professional_friendly",
        "max_words": 200,
        "greeting_style": "Hej!",
        "signature_style": "Med vänliga hälsningar",
        "sign_off_name": "Linnea Moritz",
        "sign_off_phone": "076-116 61 09",
        "sign_off_email": "linneamoritz1@gmail.com",
        "liked_phrases": ["flexibel med tider", "körkort", "flytande engelska"],
        "never_mention": ["konst", "målning", "utställningar", "Shopify", "e-handel", "oljemålning", "linneamoritz.com"],
        "custom_ai_instructions": "Skriv på naturlig, flytande svenska. Undvik AI-floskler som 'gedigen', 'brinner för', 'vittnar om'. Berätta varför jag vill ha just det jobbet.",
    }

    JOB_PREFS = {
        "user_id": user_id,
        "preferred_locations": ["Stockholm", "Sollentuna", "Sundbyberg", "Vetlanda"],
        "search_keywords": ["servitör", "kundtjänst", "content moderator", "butik", "café", "reception", "lager"],
        "excluded_keywords": [],
        "excluded_companies": [],
        "job_types": ["heltid", "deltid"],
        "remote_only": False,
    }

    CV_BRANSCHER = [
        {"user_id": user_id, "bransch_id": "restaurant", "bransch_name": "Restaurang & Café", "focus": "Service, tempo, kundkontakt", "keywords": ["servitör", "servitris", "restaurang", "café", "barista", "kök"], "is_active": True, "sort_order": 1},
        {"user_id": user_id, "bransch_id": "retail", "bransch_name": "Butik & Kassa", "focus": "Försäljning, kassa, kundservice", "keywords": ["butik", "kassa", "säljare", "ica", "coop"], "is_active": True, "sort_order": 2},
        {"user_id": user_id, "bransch_id": "customerservice", "bransch_name": "Kundtjänst & Support", "focus": "Kommunikation, problemlösning, internationell erfarenhet", "keywords": ["kundtjänst", "support", "kundservice", "helpdesk"], "is_active": True, "sort_order": 3},
        {"user_id": user_id, "bransch_id": "content", "bransch_name": "Content & Moderation", "focus": "Trust & Safety, policy, granskning", "keywords": ["moderator", "content", "review", "granskning", "trust"], "is_active": True, "sort_order": 4},
        {"user_id": user_id, "bransch_id": "tech", "bransch_name": "Tech & Kontor", "focus": "Analytiskt arbete, data, tech-bolag", "keywords": ["tech", "IT", "data", "analyst", "kontor"], "is_active": True, "sort_order": 5},
        {"user_id": user_id, "bransch_id": "industry", "bransch_name": "Industri & Trädgård", "focus": "Fysiskt arbete, skift, materialhantering", "keywords": ["industri", "lager", "produktion", "operatör", "trädgård"], "is_active": True, "sort_order": 6},
        {"user_id": user_id, "bransch_id": "healthcare", "bransch_name": "Vård & Omsorg", "focus": "Omvårdnad, empati, medicinhantering", "keywords": ["vård", "omsorg", "äldre", "sjukvård"], "is_active": True, "sort_order": 7},
        {"user_id": user_id, "bransch_id": "art", "bransch_name": "Konst & Kultur", "focus": "Konstnärligt arbete, utställningar, projektledning", "keywords": ["konst", "kultur", "galleri", "museum", "kreativ"], "is_active": True, "sort_order": 8},
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
    home_location: Optional[str] = None
    age: Optional[str] = None
    drivers_license: Optional[str] = None
    own_car: Optional[str] = None
    own_computer: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio_url: Optional[str] = None
    earliest_start: Optional[str] = None
    education_level: Optional[str] = None


class UserPreferences(BaseModel):
    model_config = {"extra": "ignore"}  # Silently drop unknown fields from frontend
    # Quiz fields (maps to Platsbanken data)
    search_terms: Optional[list] = None
    custom_search: Optional[str] = None
    negative_keywords: Optional[list] = None  # Excluded job keywords
    working_hours: Optional[Any] = None  # str or list from quiz vs PreferencesPage
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

    # Build profile data for upsert — only columns that exist in user_profiles table
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
    if profile.home_location:
        profile_data["location"] = profile.home_location
    if profile.own_car:
        profile_data["own_car"] = profile.own_car == "yes"
    if profile.own_computer:
        profile_data["own_computer"] = profile.own_computer != "no"
    if profile.portfolio_url:
        profile_data["portfolio_url"] = profile.portfolio_url
    # Note: linkedin is NOT a column in user_profiles — stored in quiz_answers instead

    # Upsert to user_profiles — on_conflict=user_id is REQUIRED because
    # the primary key is `id UUID` (auto-generated), not `user_id`.
    # Without it, PostgREST resolves conflicts on `id`, finds none, and
    # the INSERT fails on the user_id UNIQUE constraint → updates never persist.
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_profiles?on_conflict=user_id",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=profile_data
        )
        logger.info(f"Profile save: {res.status_code} - {res.text[:200] if res.status_code >= 400 else 'OK'}")

    # When location changes, update the header line in all user's bransch_cvs
    # so the CV text stays in sync with the profile.
    if profile.home_location and res.status_code < 400:
        try:
            cvs = await db_request("GET", "bransch_cvs", params={
                "user_id": f"eq.{user_id}", "select": "id,cv_text"
            })
            if cvs:
                new_loc = profile.home_location.strip()
                for cv in cvs:
                    cv_text = cv.get("cv_text", "")
                    if not cv_text:
                        continue
                    lines = cv_text.split("\n")
                    updated = False
                    for i, line in enumerate(lines[:5]):  # Header is in first 5 lines
                        parts = line.split("|")
                        if len(parts) >= 3:
                            # Pipe-separated header: "X | Location | Phone | Email"
                            # Replace the location part (typically index 1)
                            parts[1] = f" {new_loc} "
                            lines[i] = "|".join(parts)
                            updated = True
                            break
                    if updated:
                        await db_request("PATCH", f"bransch_cvs?id=eq.{cv['id']}",
                            data={"cv_text": "\n".join(lines)})
                logger.info(f"Updated {len(cvs)} bransch_cv headers with location '{new_loc}'")
        except Exception as e:
            logger.warning(f"Failed to update bransch_cv headers: {e}")

    # Save all personal quiz fields into user_job_preferences.quiz_answers
    # This ensures age, education, earliest_start, own_car, linkedin persist in Supabase
    quiz_personal = {}
    if profile.full_name:
        quiz_personal["full_name"] = profile.full_name
    if profile.phone:
        quiz_personal["phone"] = profile.phone
    if profile.home_location:
        quiz_personal["home_location"] = profile.home_location
    if profile.age:
        quiz_personal["age"] = profile.age
    if profile.earliest_start:
        quiz_personal["earliest_start"] = profile.earliest_start
    if profile.education_level:
        quiz_personal["education_level"] = profile.education_level
    if profile.drivers_license:
        quiz_personal["drivers_license"] = profile.drivers_license
    if profile.own_car:
        quiz_personal["own_car"] = profile.own_car
    if profile.own_computer:
        quiz_personal["own_computer"] = profile.own_computer
    if profile.linkedin:
        quiz_personal["linkedin"] = profile.linkedin
    if profile.portfolio_url:
        quiz_personal["portfolio_url"] = profile.portfolio_url

    if quiz_personal:
        # Merge into existing quiz_answers (don't overwrite job preference fields)
        try:
            existing = await db_request("GET", "user_job_preferences", params={"user_id": f"eq.{user_id}"})
            existing_qa = existing[0].get("quiz_answers", {}) if existing else {}
            merged_qa = {**existing_qa, **quiz_personal}

            prefs_data = {
                "user_id": user_id,
                "quiz_answers": merged_qa,
                "updated_at": datetime.now().isoformat()
            }
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/user_job_preferences?on_conflict=user_id",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "resolution=merge-duplicates"
                    },
                    json=prefs_data
                )
        except Exception as e:
            logger.warning(f"Failed to save quiz personal data to preferences: {e}")

    return {"success": True, "saved_to_db": True}


@app.get("/api/user/preferences")
async def get_user_preferences(request: Request):
    """Get user job preferences and settings."""
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

    # Fetch existing quiz_answers so we MERGE instead of overwrite
    existing_qa = {}
    try:
        existing = await db_request("GET", "user_job_preferences",
            params={"user_id": f"eq.{user_id}", "select": "quiz_answers"})
        if existing and len(existing) > 0:
            existing_qa = existing[0].get("quiz_answers") or {}
    except Exception:
        pass

    # Build new values — only override fields that were actually sent (not None)
    # NOTE: location is NOT here — it's managed by PlatserPage, not the quiz
    incoming = {
        "search_terms": prefs.search_terms,
        "custom_search": getattr(prefs, 'custom_search', None),
        "negative_keywords": prefs.negative_keywords,
        "working_hours": prefs.working_hours,
        "employment_form": prefs.employment_form,
        "duration": prefs.duration,
        "salary": prefs.salary,
        "dealbreakers": prefs.dealbreakers
    }

    # Merge: keep existing values for any field the frontend didn't send
    quiz_answers = {**existing_qa}
    for key, value in incoming.items():
        if value is not None:
            quiz_answers[key] = value

    # Build search keywords from merged data
    search_kw = []
    cs = quiz_answers.get("custom_search")
    st = quiz_answers.get("search_terms")
    if cs:
        search_kw = [k.strip() for k in cs.split(',') if k.strip()]
    elif st:
        search_kw = st

    # Upsert — maps to actual DB columns in user_job_preferences
    # NOTE: preferred_locations is NOT set here — only PlatserPage manages locations
    prefs_data = {
        "user_id": user_id,
        "search_keywords": search_kw,
        "excluded_keywords": quiz_answers.get("negative_keywords") or [],
        "job_types": prefs.job_types or quiz_answers.get("search_terms") or [],
        "quiz_answers": quiz_answers,  # JSONB — merged, never loses data
        "updated_at": datetime.now().isoformat()
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_job_preferences?on_conflict=user_id",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=prefs_data
        )
        if resp.status_code >= 400:
            logger.error(f"Failed to save preferences: {resp.status_code} {resp.text}")
            raise HTTPException(status_code=500, detail=f"Kunde inte spara preferenser: {resp.text[:200]}")

    # Save Gmail credentials if provided
    if prefs.gmail_client_id and prefs.gmail_client_secret:
        gmail_data = {
            "user_id": user_id,
            "client_id": prefs.gmail_client_id,
            "client_secret": prefs.gmail_client_secret,
            "updated_at": datetime.now().isoformat()
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


@app.post("/api/user/locations")
async def save_user_locations(request: Request):
    """Save preferred work locations (from PlatserPage)."""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    locations = body.get("locations", [])

    # Use same upsert pattern as save_user_preferences (POST + merge-duplicates)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/user_job_preferences?on_conflict=user_id",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json={
                "user_id": user_id,
                "preferred_locations": locations,
                "updated_at": datetime.now().isoformat()
            },
            timeout=10
        )
        logger.info(f"Upsert locations: status={resp.status_code} body={resp.text[:200]}")
        if resp.status_code >= 400:
            logger.error(f"Failed to save locations: {resp.text}")
            raise HTTPException(status_code=500, detail=f"Kunde inte spara platser: {resp.text[:300]}")

    return {"success": True, "message": "Platser sparade!"}


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
        "updated_at": datetime.now().isoformat()
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/user_profiles?on_conflict=user_id",
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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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


@app.delete("/api/user/education/{edu_id}")
async def delete_education(request: Request, edu_id: str):
    """Delete an education entry."""
    user_id = await get_user_id_from_request(request, required=True)

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/user_education?id=eq.{edu_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code in [200, 204]:
            return {"success": True, "message": "Utbildning borttagen"}

    return {"success": False, "error": "Kunde inte ta bort utbildning"}


# ============== SKILLS CRUD ==============

class SkillData(BaseModel):
    category: str = "all"
    skill_type: str = "technical"
    skill_text: str = ""


@app.post("/api/user/skill")
async def create_skill(request: Request, skill: SkillData):
    """Create a new skill entry."""
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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


# --- Volunteer CRUD ---

class VolunteerData(BaseModel):
    organization: str
    title: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None

@app.post("/api/user/volunteer")
async def create_volunteer(request: Request, vol: VolunteerData):
    """Create a new volunteer entry."""
    user_id = await get_user_id_from_request(request, required=True)
    result = await db_request("POST", "user_volunteer", data={
        "user_id": user_id,
        "organization": vol.organization,
        "title": vol.title,
        "dates": vol.dates,
        "description": vol.description
    })
    if result:
        return {"success": True, "volunteer": result[0]}
    return {"success": False, "error": "Kunde inte skapa volontärerfarenhet"}

@app.put("/api/user/volunteer/{vol_id}")
async def update_volunteer(request: Request, vol_id: str, vol: VolunteerData):
    """Update an existing volunteer entry."""
    user_id = await get_user_id_from_request(request, required=True)
    result = await db_request("PATCH", "user_volunteer", data={
        "organization": vol.organization,
        "title": vol.title,
        "dates": vol.dates,
        "description": vol.description
    }, params={"id": f"eq.{vol_id}", "user_id": f"eq.{user_id}"})
    if result:
        return {"success": True, "volunteer": result[0]}
    return {"success": False, "error": "Kunde inte uppdatera"}

@app.delete("/api/user/volunteer/{vol_id}")
async def delete_volunteer(request: Request, vol_id: str):
    """Delete a volunteer entry."""
    user_id = await get_user_id_from_request(request, required=True)
    result = await db_request("DELETE", "user_volunteer", params={
        "id": f"eq.{vol_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "message": "Volontärerfarenhet borttagen"}


# --- Award & Certification DELETE ---

@app.post("/api/user/award")
async def create_award(request: Request):
    """Create a new award entry with optional description."""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    award_text = (body.get("award_text") or "").strip()
    if not award_text:
        raise HTTPException(status_code=400, detail="award_text krävs")
    description = (body.get("description") or "").strip() or None
    # Get next sort_order
    existing = await db_request("GET", "user_awards", params={
        "user_id": f"eq.{user_id}", "select": "sort_order", "order": "sort_order.desc", "limit": "1"
    }) or []
    next_order = (existing[0]["sort_order"] + 1) if existing else 0
    data = {
        "user_id": user_id,
        "award_text": award_text,
        "description": description,
        "sort_order": next_order
    }
    result = await db_request("POST", "user_awards", data=data)
    return {"success": True, "message": "Pris tillagt", "award": result[0] if result else data}

@app.put("/api/user/award/{award_id}")
async def update_award(request: Request, award_id: str):
    """Update an award's text and/or description."""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    update = {}
    if "award_text" in body:
        award_text = (body["award_text"] or "").strip()
        if award_text:
            update["award_text"] = award_text
    if "description" in body:
        update["description"] = (body["description"] or "").strip() or None
    if not update:
        raise HTTPException(status_code=400, detail="Inget att uppdatera")
    await db_request("PATCH", "user_awards", data=update, params={
        "id": f"eq.{award_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "message": "Pris uppdaterat"}

@app.delete("/api/user/award/{award_id}")
async def delete_award(request: Request, award_id: str):
    """Delete an award entry."""
    user_id = await get_user_id_from_request(request, required=True)
    await db_request("DELETE", "user_awards", params={
        "id": f"eq.{award_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "message": "Pris borttaget"}

@app.put("/api/user/certification/{cert_id}")
async def update_certification(request: Request, cert_id: str):
    """Update a certification entry."""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    update_data = {}
    for field in ["certification_name", "issuing_organization", "issue_date", "expiry_date", "description"]:
        if field in body:
            update_data[field] = body[field]
    if not update_data:
        raise HTTPException(status_code=400, detail="Inget att uppdatera")
    result = await db_request("PATCH", "user_certifications", data=update_data, params={
        "id": f"eq.{cert_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "certification": result[0] if result else None}


@app.delete("/api/user/certification/{cert_id}")
async def delete_certification(request: Request, cert_id: str):
    """Delete a certification entry."""
    user_id = await get_user_id_from_request(request, required=True)
    await db_request("DELETE", "user_certifications", params={
        "id": f"eq.{cert_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "message": "Certifiering borttagen"}

@app.delete("/api/user/project/{project_id}")
async def delete_project(request: Request, project_id: str):
    """Delete a tech project entry."""
    user_id = await get_user_id_from_request(request, required=True)
    await db_request("DELETE", "tech_projects", params={
        "id": f"eq.{project_id}", "user_id": f"eq.{user_id}"
    })
    return {"success": True, "message": "Projekt borttaget"}


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
    user_id = await get_user_id_from_request(request, required=True)

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


@app.post("/api/cv/enhance-master")
async def enhance_master_cv_from_upload(request: Request):
    """
    Upload a CV file to ENHANCE the existing Master CV.
    AI reads the new CV and adds/improves entries without deleting existing ones.
    """
    user_id = await get_user_id_from_request(request, required=True)

    content_type = request.headers.get("content-type", "")
    cv_text = ""

    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if file:
            file_content = await file.read()
            cv_text = extract_text_from_file(file_content, file.filename)
            if not cv_text:
                raise HTTPException(status_code=400, detail="Kunde inte extrahera text från filen")
    else:
        body = await request.json()
        cv_text = body.get("cv_text", "")

    if not cv_text or len(cv_text) < 50:
        raise HTTPException(status_code=400, detail="CV-text är för kort eller saknas")

    # Fetch existing Master CV data
    existing_experiences = await db_request("GET", "user_experiences", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    existing_education = await db_request("GET", "user_education", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    existing_volunteer = await db_request("GET", "user_volunteer", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    existing_projects = await db_request("GET", "tech_projects", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []
    existing_skills = await db_request("GET", "user_skills", params={
        "user_id": f"eq.{user_id}"
    }) or []
    existing_certifications = await db_request("GET", "user_certifications", params={
        "user_id": f"eq.{user_id}", "order": "sort_order.asc"
    }) or []

    # Build context of what already exists
    existing_summary = "BEFINTLIGA ERFARENHETER I MASTER CV:\n"
    for exp in existing_experiences:
        existing_summary += f"- ID:{exp.get('id')} | {exp.get('company')} | {exp.get('title')} | {exp.get('start_date')}-{exp.get('end_date','')} | Beskrivning: {(exp.get('description') or '')[:100]}\n"
    existing_summary += "\nBEFINTLIG UTBILDNING:\n"
    for edu in existing_education:
        existing_summary += f"- ID:{edu.get('id')} | {edu.get('school')} | {edu.get('degree')} | {edu.get('start_date')}-{edu.get('end_date','')}\n"
    existing_summary += "\nBEFINTLIGT VOLONTÄRARBETE:\n"
    for vol in existing_volunteer:
        existing_summary += f"- ID:{vol.get('id')} | {vol.get('organization')} | {vol.get('dates','')} | {(vol.get('description') or '')[:80]}\n"
    if not existing_volunteer:
        existing_summary += "- (inga poster)\n"
    existing_summary += "\nBEFINTLIGA PROJEKT:\n"
    for proj in existing_projects:
        existing_summary += f"- ID:{proj.get('id')} | {proj.get('name') or proj.get('title','')} | {(proj.get('description') or '')[:80]}\n"
    if not existing_projects:
        existing_summary += "- (inga poster)\n"
    existing_summary += "\nBEFINTLIGA KOMPETENSER:\n"
    skill_texts = [s.get('skill_text','') for s in existing_skills]
    existing_summary += ", ".join(skill_texts) if skill_texts else "(inga)"
    existing_summary += "\n\nBEFINTLIGA CERTIFIERINGAR:\n"
    for cert in existing_certifications:
        existing_summary += f"- ID:{cert.get('id')} | {cert.get('name') or cert.get('cert_name','')}\n"
    if not existing_certifications:
        existing_summary += "- (inga poster)\n"

    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="AI ej konfigurerad")

    # Ask Claude to compare and find improvements
    prompt = f"""Jag har ett Master CV med befintliga poster. Jag har precis laddat upp ett nytt CV-dokument.

UPPGIFT: Analysera ALLA sektioner i det nya dokumentet och jämför med mina befintliga poster. Det nya CVt kan innehålla:
- Arbetslivserfarenheter (jobb, praktik, anställningar)
- Utbildningar (skola, kurser, program)
- Volontärarbete / ideellt arbete
- Projekt (tech-projekt, sidoprojekt, portföljprojekt)
- Kompetenser / skills (tekniska, språk, certifikat)
- Certifieringar

FÖR VARJE SEKTION:
1. Hitta NYA poster som INTE redan finns → skapa dem
2. Hitta befintliga poster som kan FÖRBÄTTRAS med mer detaljer → uppdatera dem
3. RADERA ALDRIG något. Lägg bara till och förbättra.

{existing_summary}

NYTT CV-DOKUMENT:
{cv_text[:5000]}

Svara i EXAKT detta JSON-format (inga kommentarer, bara ren JSON):
{{
    "new_experiences": [
        {{"company": "...", "title": "...", "location": "...", "start_date": "...", "end_date": "...", "description": "...", "categories": ["..."]}}
    ],
    "updated_experiences": [
        {{"id": "befintligt-uuid", "description": "ny förbättrad beskrivning", "categories": ["uppdaterade", "kategorier"]}}
    ],
    "new_education": [
        {{"school": "...", "degree": "...", "field_of_study": "...", "location": "...", "start_date": "...", "end_date": ""}}
    ],
    "updated_education": [
        {{"id": "befintligt-uuid", "degree": "förbättrad examen text", "field_of_study": "inriktning"}}
    ],
    "new_volunteer": [
        {{"organization": "...", "dates": "...", "description": "..."}}
    ],
    "new_projects": [
        {{"name": "...", "description": "...", "tech_stack": "...", "url": ""}}
    ],
    "new_skills": [
        {{"skill_text": "...", "skill_type": "technical|language|certificate", "category": "all"}}
    ],
    "new_certifications": [
        {{"name": "...", "issuer": "...", "date": ""}}
    ],
    "summary": "Kort sammanfattning av vad som ändrades"
}}

VIKTIGT:
- Analysera HELA dokumentet — missa inte volontärarbete, projekt, kompetenser eller certifieringar
- Bara inkludera poster som verkligen behöver skapas eller uppdateras
- Om inget behöver ändras i en sektion, returnera tom array för den
- Kategorier för erfarenheter: restaurant, retail, tech, healthcare, customerservice, contentmoderation, industri, art, marketing, education, reception
- skill_type: "technical" (programmeringsspråk, verktyg), "language" (svenska, engelska), "certificate" (körkort, etc.)
- Datum i format "Aug 2024" eller "2024"
- Beskrivningar på svenska, korta och informativa
- Dubblera INTE kompetenser som redan finns i listan"""

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
                    "max_tokens": 3000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=55
            )

            if response.status_code != 200:
                logger.error(f"Claude API error in enhance: {response.status_code}")
                raise HTTPException(status_code=500, detail=f"AI-fel: {response.status_code}")

            result = response.json()
            ai_text = result["content"][0]["text"].strip()

            # Parse JSON from AI response (handle markdown code blocks)
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0].strip()

            import json as json_module
            changes = json_module.loads(ai_text)

    except json_module.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {ai_text[:500]}")
        raise HTTPException(status_code=500, detail="AI returnerade ogiltigt format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhance: {e}")
        raise HTTPException(status_code=500, detail=f"Fel: {str(e)[:200]}")

    # Apply changes to database
    added = 0
    updated = 0

    # Create new experiences
    for exp in changes.get("new_experiences", []):
        try:
            await db_request("POST", "user_experiences", data={
                "user_id": user_id,
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", ""),
                "description": exp.get("description", ""),
                "categories": exp.get("categories", []),
                "sort_order": len(existing_experiences) + added
            })
            added += 1
        except Exception as e:
            logger.warning(f"Failed to add experience: {e}")

    # Update existing experiences (only non-empty fields)
    for exp in changes.get("updated_experiences", []):
        exp_id = exp.get("id")
        if not exp_id:
            continue
        update_data = {}
        for field in ["description", "categories", "title", "location", "start_date", "end_date"]:
            if exp.get(field):
                update_data[field] = exp[field]
        if update_data:
            try:
                async with httpx.AsyncClient() as client:
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/user_experiences?id=eq.{exp_id}&user_id=eq.{user_id}",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
                        },
                        json=update_data
                    )
                updated += 1
            except Exception as e:
                logger.warning(f"Failed to update experience {exp_id}: {e}")

    # Create new education
    for edu in changes.get("new_education", []):
        try:
            await db_request("POST", "user_education", data={
                "user_id": user_id,
                "school": edu.get("school", ""),
                "degree": edu.get("degree", ""),
                "field_of_study": edu.get("field_of_study", ""),
                "location": edu.get("location", ""),
                "start_date": edu.get("start_date", ""),
                "end_date": edu.get("end_date", ""),
                "sort_order": len(existing_education) + added
            })
            added += 1
        except Exception as e:
            logger.warning(f"Failed to add education: {e}")

    # Update existing education
    for edu in changes.get("updated_education", []):
        edu_id = edu.get("id")
        if not edu_id:
            continue
        update_data = {}
        for field in ["degree", "field_of_study", "school", "location", "start_date", "end_date"]:
            if edu.get(field):
                update_data[field] = edu[field]
        if update_data:
            try:
                async with httpx.AsyncClient() as client:
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/user_education?id=eq.{edu_id}&user_id=eq.{user_id}",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
                        },
                        json=update_data
                    )
                updated += 1
            except Exception as e:
                logger.warning(f"Failed to update education {edu_id}: {e}")

    # Create new volunteer entries
    for vol in changes.get("new_volunteer", []):
        try:
            bullets = []
            desc = vol.get("description", "")
            if desc:
                bullets = [s.strip() for s in desc.split(".") if s.strip()]
            await db_request("POST", "user_volunteer", data={
                "user_id": user_id,
                "organization": vol.get("organization", ""),
                "dates": vol.get("dates", ""),
                "bullets": bullets,
                "sort_order": len(existing_volunteer) + added
            })
            added += 1
        except Exception as e:
            logger.warning(f"Failed to add volunteer: {e}")

    # Create new projects
    for proj in changes.get("new_projects", []):
        try:
            await db_request("POST", "tech_projects", data={
                "user_id": user_id,
                "name": proj.get("name", ""),
                "description": proj.get("description", ""),
                "tech_stack": proj.get("tech_stack", ""),
                "url": proj.get("url", ""),
                "sort_order": len(existing_projects) + added
            })
            added += 1
        except Exception as e:
            logger.warning(f"Failed to add project: {e}")

    # Create new skills (skip duplicates)
    existing_skill_texts = {s.get("skill_text", "").lower() for s in existing_skills}
    for skill in changes.get("new_skills", []):
        try:
            skill_text = skill.get("skill_text", "").strip()
            if skill_text and skill_text.lower() not in existing_skill_texts:
                await db_request("POST", "user_skills", data={
                    "user_id": user_id,
                    "skill_text": skill_text,
                    "skill_type": skill.get("skill_type", "technical"),
                    "category": skill.get("category", "all")
                })
                existing_skill_texts.add(skill_text.lower())
                added += 1
        except Exception as e:
            logger.warning(f"Failed to add skill: {e}")

    # Create new certifications
    for cert in changes.get("new_certifications", []):
        try:
            cert_name = cert.get("name", "").strip()
            if cert_name:
                await db_request("POST", "user_certifications", data={
                    "user_id": user_id,
                    "name": cert_name,
                    "issuer": cert.get("issuer", ""),
                    "date": cert.get("date", ""),
                    "sort_order": len(existing_certifications) + added
                })
                added += 1
        except Exception as e:
            logger.warning(f"Failed to add certification: {e}")

    return {
        "success": True,
        "added": added,
        "updated": updated,
        "summary": changes.get("summary", f"{added} nya poster, {updated} förbättrade"),
        "changes": changes
    }


@app.post("/api/cv/enhance-chat")
async def enhance_chat(request: Request):
    """Chat about the last CV enhancement — AI can actually read AND write Master CV data.
    Returns both a text response and executes any requested DB changes."""
    import json as json_module
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    question = body.get("question", "").strip()
    changes_context = body.get("changes_context", "")
    conversation_history = body.get("conversation_history", [])

    if not question:
        raise HTTPException(status_code=400, detail="Ingen fråga angiven")
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="AI ej konfigurerad")

    # Fetch ALL Master CV data so AI has full picture
    master_cv_sections = {}
    try:
        experiences = await db_request("GET", "user_experiences", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []
        education = await db_request("GET", "user_education", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []
        volunteer = await db_request("GET", "user_volunteer", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []
        projects = await db_request("GET", "tech_projects", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []
        skills = await db_request("GET", "user_skills", params={
            "user_id": f"eq.{user_id}"
        }) or []
        awards = await db_request("GET", "user_awards", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []
        certifications = await db_request("GET", "user_certifications", params={
            "user_id": f"eq.{user_id}", "order": "sort_order.asc"
        }) or []

        # Build readable summary with IDs so AI can reference specific entries
        lines = []
        lines.append("=== ERFARENHETER ===")
        for exp in experiences:
            lines.append(f"[ID:{exp.get('id')}] {exp.get('title','')} @ {exp.get('company','')} | {exp.get('location','')} | {exp.get('start_date','')}-{exp.get('end_date','')} | Kategorier: {exp.get('categories',[])} | Beskrivning: {exp.get('description','')}")
        if not experiences:
            lines.append("(inga)")

        lines.append("\n=== UTBILDNING ===")
        for edu in education:
            lines.append(f"[ID:{edu.get('id')}] {edu.get('degree','')} @ {edu.get('school','')} | {edu.get('location','')} | {edu.get('start_date','')}-{edu.get('end_date','')} | Inriktning: {edu.get('field_of_study','')}")
        if not education:
            lines.append("(inga)")

        lines.append("\n=== PROJEKT ===")
        for proj in projects:
            lines.append(f"[ID:{proj.get('id')}] {proj.get('name', proj.get('title',''))} | {proj.get('description','')} | Tech: {proj.get('tech_stack','')}")
        if not projects:
            lines.append("(inga)")

        lines.append("\n=== VOLONTÄRARBETE ===")
        for vol in volunteer:
            lines.append(f"[ID:{vol.get('id')}] {vol.get('organization','')} | {vol.get('dates','')} | {vol.get('bullets',[])}")
        if not volunteer:
            lines.append("(inga)")

        lines.append("\n=== KOMPETENSER ===")
        for s in skills:
            lines.append(f"[ID:{s.get('id')}] {s.get('skill_text','')} ({s.get('skill_type','')}, {s.get('category','')})")
        if not skills:
            lines.append("(inga)")

        lines.append("\n=== UTMÄRKELSER ===")
        for a in awards:
            lines.append(f"[ID:{a.get('id')}] {a.get('award_text','')}")
        if not awards:
            lines.append("(inga)")

        lines.append("\n=== CERTIFIERINGAR ===")
        for c in certifications:
            lines.append(f"[ID:{c.get('id')}] {c.get('name', c.get('cert_name',''))}")
        if not certifications:
            lines.append("(inga)")

        master_cv_data = "\n".join(lines)
    except Exception as e:
        logger.warning(f"Could not fetch master CV for chat: {e}")
        master_cv_data = "(kunde inte hämta data)"

    system_prompt = f"""Du är en assistent som hjälper en jobbsökare redigera sitt Master CV. Svara ALLTID på svenska.

ANVÄNDARENS KOMPLETTA MASTER CV (allt som finns i databasen):
{master_cv_data}

SENASTE ÄNDRINGAR (från CV-uppladdning):
{changes_context}

DU KAN GÖRA ÄNDRINGAR. När användaren ber dig uppdatera, lägga till, ta bort eller ändra något i Master CV:t, svara med BÅDE:
1. En kort bekräftelse till användaren (vad du ändrade)
2. Ett JSON-block med databasoperationer som backend ska utföra

FORMAT FÖR ÄNDRINGAR — lägg JSON-blocket i slutet av ditt svar, inuti ```actions``` taggar:

```actions
[
  {{"action": "update", "table": "user_experiences", "id": "uuid-här", "data": {{"description": "ny text", "categories": ["tech", "customerservice"]}}}},
  {{"action": "update", "table": "tech_projects", "id": "uuid-här", "data": {{"name": "nytt namn", "description": "ny beskrivning"}}}},
  {{"action": "create", "table": "user_volunteer", "data": {{"organization": "...", "dates": "...", "bullets": ["..."]}}}},
  {{"action": "create", "table": "user_skills", "data": {{"skill_text": "Python", "skill_type": "technical", "category": "tech"}}}},
  {{"action": "delete", "table": "user_skills", "id": "uuid-här"}}
]
```

TABELLER DU KAN ÄNDRA:
- user_experiences: company, title, location, start_date, end_date, description, categories (array)
- user_education: school, degree, field_of_study, location, start_date, end_date
- tech_projects: name, description, tech_stack, url
- user_volunteer: organization, dates, bullets (array)
- user_skills: skill_text, skill_type (technical/language/certificate), category
- user_awards: award_text
- user_certifications: name, issuer, date

REGLER:
- Om användaren ber dig ändra något — GÖR DET DIREKT. Inkludera actions-blocket i ditt svar.
- Fråga ALDRIG om saker som redan framgår av konversationen eller det uppladdade CVt
- Om användaren säger "läs CVt jag laddade upp" — informationen finns redan i SENASTE ÄNDRINGAR ovan
- Var kort och konkret — ingen inställsam AI-ton, inga emojis
- Skriv naturlig svenska"""

    # Build Claude messages from conversation history
    messages = []
    for msg in conversation_history[-20:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("text", "")})

    if not messages or messages[-1]["role"] != "user":
        messages.append({"role": "user", "content": question})

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
                    "max_tokens": 2000,
                    "system": system_prompt,
                    "messages": messages
                },
                timeout=45
            )
            if response.status_code != 200:
                logger.error(f"Enhance chat Claude error: {response.status_code} - {response.text[:200]}")
                raise HTTPException(status_code=500, detail="AI-fel")
            result = response.json()
            answer = result["content"][0]["text"].strip()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhance chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

    # Parse and execute any DB actions from the AI response
    actions_executed = 0
    actions_failed = 0
    allowed_tables = {"user_experiences", "user_education", "tech_projects", "user_volunteer", "user_skills", "user_awards", "user_certifications"}

    if "```actions" in answer:
        try:
            actions_json = answer.split("```actions")[1].split("```")[0].strip()
            actions = json_module.loads(actions_json)

            for act in actions:
                table = act.get("table", "")
                action_type = act.get("action", "")
                entry_id = act.get("id", "")
                data = act.get("data", {})

                if table not in allowed_tables:
                    logger.warning(f"Chat tried to modify disallowed table: {table}")
                    actions_failed += 1
                    continue

                try:
                    if action_type == "update" and entry_id:
                        await db_request("PATCH", f"{table}?id=eq.{entry_id}&user_id=eq.{user_id}", data=data)
                        actions_executed += 1
                    elif action_type == "create":
                        data["user_id"] = user_id
                        await db_request("POST", table, data=data)
                        actions_executed += 1
                    elif action_type == "delete" and entry_id:
                        await db_request("DELETE", f"{table}?id=eq.{entry_id}&user_id=eq.{user_id}")
                        actions_executed += 1
                    else:
                        logger.warning(f"Unknown action: {action_type}")
                        actions_failed += 1
                except Exception as e:
                    logger.warning(f"Failed to execute action {action_type} on {table}: {e}")
                    actions_failed += 1

        except (json_module.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse actions from AI response: {e}")

        # Remove the actions block from the visible answer
        answer = answer.split("```actions")[0].strip()
        if answer.endswith("```"):
            answer = answer[:-3].strip()

    return {
        "success": True,
        "answer": answer,
        "actions_executed": actions_executed,
        "actions_failed": actions_failed
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
                    "model": "claude-sonnet-4-5-20250929",
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
    await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

    # Collect all user data from all tables
    export_data = {
        "export_date": datetime.now().isoformat(),
        "user_id": user_id,
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


# ============== GMAIL OAUTH (Per-user credentials from Supabase) ==============

async def get_user_gmail_credentials(user_id: str) -> Optional[dict]:
    """Fetch Gmail OAuth credentials. Falls back to app-level env vars if user has no per-user creds."""
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if creds and creds[0].get("client_id") and creds[0].get("client_secret"):
        return creds[0]
    # Fall back to app-level credentials from environment variables
    app_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    app_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    if app_client_id and app_client_secret:
        return {"user_id": user_id, "client_id": app_client_id, "client_secret": app_client_secret}
    return None


@app.post("/api/gmail/credentials")
async def save_gmail_credentials(request: Request):
    """Save Google OAuth client_id and client_secret for this user."""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()
    client_id = body.get("client_id", "").strip()
    client_secret = body.get("client_secret", "").strip()
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Både Client ID och Client Secret krävs.")

    existing = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    data = {
        "user_id": user_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "updated_at": datetime.now().isoformat()
    }
    if existing:
        await db_request("PATCH", f"user_google_credentials?user_id=eq.{user_id}", data=data)
    else:
        await db_request("POST", "user_google_credentials", data=data)

    return {"success": True, "message": "Credentials sparade. Du kan nu koppla din Gmail."}


@app.get("/api/gmail/auth-url")
async def get_gmail_auth_url(request: Request, redirect_uri: str = None):
    """
    Get Google OAuth URL for user to authorize Gmail access.
    Uses per-user credentials from user_google_credentials table.
    """
    user_id = await get_user_id_from_request(request, required=True)

    user_creds = await get_user_gmail_credentials(user_id)
    if not user_creds:
        raise HTTPException(status_code=400, detail="Gmail-kopplingen är inte konfigurerad. Kontakta support.")

    redirect_uri = "https://platsbanken-ai.vercel.app/api/gmail/callback"

    params = {
        "client_id": user_creds["client_id"],
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
    """Handle OAuth callback. Exchange code for tokens using per-user credentials from DB."""
    user_id = state

    user_creds = await get_user_gmail_credentials(user_id)
    if not user_creds:
        raise HTTPException(status_code=400, detail="Gmail-kopplingen är inte konfigurerad.")

    redirect_uri = "https://platsbanken-ai.vercel.app/api/gmail/callback"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": user_creds["client_id"],
                "client_secret": user_creds["client_secret"],
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
async def get_gmail_status(request: Request):
    """Check if user has Gmail connected"""
    user_id = await get_user_id_from_request(request)
    if not user_id:
        return {"connected": False, "gmail_address": None, "app_configured": False}
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})

    # Auto-migrate: if no creds under real user_id, check for legacy "default_user" creds
    if (not creds or not creds[0].get("is_connected")) and user_id != "default_user":
        legacy = await db_request("GET", "user_google_credentials", params={"user_id": "eq.default_user"})
        if legacy and legacy[0].get("is_connected"):
            # Move legacy creds to real user_id
            await db_request("PATCH", "user_google_credentials?user_id=eq.default_user", data={"user_id": user_id})
            logger.info(f"Migrated Gmail credentials from default_user to {user_id}")
            creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})

    # Check for app-level credentials as fallback
    app_configured = bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))

    if not creds:
        return {"connected": False, "gmail_address": None, "app_configured": app_configured}

    cred = creds[0]
    has_oauth_creds = bool(cred.get("client_id") and cred.get("client_secret")) or app_configured

    if not cred.get("is_connected"):
        return {"connected": False, "gmail_address": None, "app_configured": has_oauth_creds}

    return {
        "connected": True,
        "gmail_address": cred.get("gmail_address"),
        "app_configured": has_oauth_creds
    }


@app.post("/api/gmail/disconnect")
async def disconnect_gmail(request: Request):
    """
    Revoke Gmail access and delete all stored tokens for this user.
    GDPR: user has the right to withdraw consent at any time.
    """
    user_id = await get_user_id_from_request(request, required=True)
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
    creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
    if not creds or not creds[0].get("is_connected"):
        return None

    cred = creds[0]

    # Need OAuth credentials for token refresh — try per-user, then app-level
    client_id = cred.get("client_id") or os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = cred.get("client_secret") or os.getenv("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None

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

    # Refresh using per-user credentials from DB
    refresh_token = cred.get("refresh_token")
    if not refresh_token:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
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
    sender_location: str = "",
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
) -> tuple:
    """Create a Gmail draft with optional PDF attachments. Returns (draft_id, error_msg) tuple."""
    access_token = await refresh_gmail_token(user_id)
    if not access_token:
        # Figure out WHY token is missing for a useful error
        creds = await db_request("GET", "user_google_credentials", params={"user_id": f"eq.{user_id}"})
        if not creds:
            return (None, "Gmail är inte kopplat. Gå till Profil → Gmail och koppla ditt konto.")
        cred = creds[0]
        if not cred.get("client_id") or not cred.get("client_secret"):
            return (None, "Gmail-kopplingen är inte konfigurerad. Försök igen senare.")
        if not cred.get("is_connected"):
            return (None, "Gmail-kopplingen är inaktiverad. Gå till Profil → Gmail och koppla om.")
        if not cred.get("refresh_token"):
            return (None, "Gmail refresh token saknas. Koppla bort och koppla om Gmail i Profil.")
        return (None, "Gmail-token kunde inte förnyas. Koppla bort och koppla om Gmail i Profil.")
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        msg = MIMEMultipart()
        msg["to"] = to_email
        msg["subject"] = subject
        # If body contains HTML tags, send as HTML; otherwise plain text
        content_type = "html" if "<br>" in body or "<i>" in body else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

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
                return (resp.json().get("id"), None)
            logger.error(f"Draft creation failed: {resp.status_code} {resp.text}")
            if resp.status_code == 401:
                return (None, "Gmail-token har gått ut. Koppla bort och koppla om Gmail i Profil.")
            if resp.status_code == 403:
                return (None, "Gmail-behörighet nekad. Koppla bort och koppla om Gmail med rätt behörigheter.")
            return (None, f"Gmail API-fel ({resp.status_code}). Försök igen eller koppla om Gmail.")
    except Exception as e:
        logger.error(f"Gmail draft error: {e}")
        return (None, f"Tekniskt fel vid skapande av utkast: {str(e)[:100]}")


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
    message.attach(MIMEText(request.body, "plain", "utf-8"))

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
        }, on_conflict="user_id,job_id")

    return {
        "success": True,
        "draft_id": draft.get("id"),
        "message": "Draft created! Check your Gmail drafts folder."
    }


# ============== STATIC JS FILES ==============

@app.get("/static/{filename}")
async def serve_static_js(filename: str):
    """Serve extracted JS files (lan-data.js, linkedin-parser.js)"""
    from fastapi.responses import Response
    allowed = {"lan-data.js", "linkedin-parser.js"}
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Not found")
    file_path = pathlib.Path(__file__).parent.parent / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found")
    content = file_path.read_text(encoding='utf-8')
    return Response(content=content, media_type="application/javascript",
                    headers={"Cache-Control": "public, max-age=86400"})


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
    feedback_type: str = "cover_letter"  # cover_letter, new_bransch_request, exclude_jobs, general
    applies_to_branscher: Optional[List[str]] = None


@app.post("/api/user/ai-feedback")
async def save_ai_feedback(request: Request, feedback: AIFeedback):
    """Save user feedback for AI cover letter generation."""
    user_id = await get_user_id_from_request(request, required=True)

    feedback_data = {
        "user_id": user_id,
        "feedback_text": feedback.feedback_text,
        "feedback_type": feedback.feedback_type,
        "applies_to_branscher": feedback.applies_to_branscher or [],
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
    user_id = await get_user_id_from_request(request, required=True)

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


@app.delete("/api/user/ai-feedback/{feedback_id}")
async def delete_ai_feedback(request: Request, feedback_id: str):
    """Soft-delete a single AI feedback entry."""
    user_id = await get_user_id_from_request(request, required=True)

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/user_ai_feedback?id=eq.{feedback_id}&user_id=eq.{user_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={"is_active": False}
        )
        if response.status_code >= 400:
            return {"success": False, "message": "Kunde inte ta bort feedback"}

    return {"success": True}


class SmartFeedbackInput(BaseModel):
    text: str


@app.post("/api/user/ai-feedback/smart")
async def save_smart_feedback(request: Request, body: SmartFeedbackInput):
    """User writes free-form text. AI understands it and saves as structured feedback."""
    user_id = await get_user_id_from_request(request, required=True)

    if not body.text.strip():
        return {"success": False, "message": "Tom text"}

    # Use Claude to understand what the user wants and create a clean summary
    prompt = f"""Du hjälper en jobbsökare som ger feedback om hur AI ska skriva deras personliga brev (cover letters).

Användaren skrev:
"{body.text}"

Analysera vad användaren menar. Det kan vara:
- Ord eller fraser de INTE vill se (t.ex. "solid butikserfarenhet" låter konstigt)
- Ton eller stil de vill ha (t.ex. mer avslappnat, kortare meningar)
- Grammatikfel de vill undvika
- Saker de VILL att AI nämner
- Generella tankar om hur brevet ska låta

Svara EXAKT i detta JSON-format (inget annat):
{{
  "summary": "Kort sammanfattning på svenska av vad användaren vill (1-2 meningar)",
  "avoid_phrases": ["fras1", "fras2"],
  "like_phrases": ["fras1"],
  "feedback_type": "cover_letter"
}}

Regler:
- "summary" ska vara tydlig och kort, på svenska
- "avoid_phrases" = specifika ord/fraser användaren inte vill ha (kan vara tom lista)
- "like_phrases" = specifika ord/fraser användaren vill ha (kan vara tom lista)
- Om användaren bara ger en generell tanke, lägg den i summary och lämna listorna tomma
- Svara BARA med JSON, ingen annan text"""

    ai_response = await call_claude_api(prompt, max_tokens=400, timeout=15)

    if not ai_response:
        # Fallback: save raw text as feedback
        feedback_data = {
            "user_id": user_id,
            "feedback_text": body.text.strip(),
            "feedback_type": "cover_letter",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        await db_request("POST", "user_ai_feedback", data=feedback_data)
        return {"success": True, "summary": body.text.strip(), "avoid_phrases": [], "like_phrases": []}

    # Parse AI response
    import json as _json
    try:
        # Strip markdown code fences if present
        clean = ai_response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            clean = clean.rsplit("```", 1)[0]
        parsed = _json.loads(clean.strip())
    except Exception:
        parsed = {"summary": body.text.strip(), "avoid_phrases": [], "like_phrases": []}

    summary = parsed.get("summary", body.text.strip())
    avoid_phrases = parsed.get("avoid_phrases", [])
    like_phrases = parsed.get("like_phrases", [])

    # Save the structured feedback to user_ai_feedback
    feedback_data = {
        "user_id": user_id,
        "feedback_text": summary,
        "feedback_type": "cover_letter",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    await db_request("POST", "user_ai_feedback", data=feedback_data)

    # Also update avoid_phrases and like_phrases in user_cover_letter_preferences
    if avoid_phrases or like_phrases:
        try:
            existing = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})
            current_avoid = []
            current_phrases = []
            if existing:
                current_avoid = existing[0].get("avoid_phrases") or []
                current_phrases = existing[0].get("liked_phrases") or []

            new_avoid = list(set(current_avoid + avoid_phrases))
            new_phrases = list(set(current_phrases + like_phrases))

            pref_data = {
                "user_id": user_id,
                "avoid_phrases": new_avoid,
                "liked_phrases": new_phrases,
                "updated_at": datetime.now().isoformat()
            }
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/user_cover_letter_preferences",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "resolution=merge-duplicates"
                    },
                    json=pref_data
                )
        except Exception as e:
            logger.warning(f"Failed to update letter prefs from feedback: {e}")

    return {
        "success": True,
        "summary": summary,
        "avoid_phrases": avoid_phrases,
        "like_phrases": like_phrases
    }


# ============== GDPR (aliases for /api/auth/ endpoints above) ==============

@app.get("/api/user/export-data")
async def export_user_data_gdpr(request: Request):
    """GDPR Article 20 — delegates to /api/auth/export-data."""
    return await export_user_data(request)


@app.delete("/api/user/delete-account")
async def delete_user_account(request: Request):
    """GDPR Article 17 — delegates to /api/auth/delete-account."""
    return await delete_account(request)


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
    html = get_frontend_html()
    return HTMLResponse(content=html, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


# ============== DEBUG: Frontend delivery check ==============

@app.get("/api/debug/frontend-check")
async def debug_frontend_check():
    """Diagnose which frontend.html is being served and whether it contains recent code."""
    import hashlib
    info = {}
    try:
        frontend_path = pathlib.Path(__file__).parent.parent / "frontend.html"
        info["path"] = str(frontend_path)
        info["exists"] = frontend_path.exists()
        if frontend_path.exists():
            content = frontend_path.read_text(encoding='utf-8')
            info["size_bytes"] = len(content.encode('utf-8'))
            info["line_count"] = content.count('\n')
            info["md5"] = hashlib.md5(content.encode('utf-8')).hexdigest()
            info["has_platser_tab"] = "id: 'platser'" in content
            info["has_extern_tab"] = "id: 'external'" in content
            info["has_PlatserPage"] = "const PlatserPage" in content
            info["has_version_marker"] = "FRONTEND_VERSION" in content
            # First 200 chars
            info["first_200_chars"] = content[:200]
        else:
            info["note"] = "frontend.html NOT FOUND at expected path"
    except Exception as e:
        info["error"] = str(e)

    info["__file__"] = str(pathlib.Path(__file__))
    info["cwd"] = str(pathlib.Path.cwd())
    return info


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
            "cv_branscher": [cv.get("vibe_id") for cv in cvs],
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
            "branscher": sorted(actual_cvs),
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

@app.post("/api/upload/cv/{bransch_id}")
async def upload_cv(bransch_id: str, request: Request):
    """Upload CV in various formats (PDF, DOCX, DOC, TXT, RTF, ODT)"""
    user_id = await get_user_id_from_request(request, required=True)

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
    file_path = f"{user_id}/{bransch_id}_cv.{ext}"

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
        params={"user_id": f"eq.{user_id}", "vibe_id": f"eq.{bransch_id}"},
        data={
            "pdf_url": pdf_url,
            "cv_text": cv_text[:50000] if cv_text else None  # Limit text size
        }
    )

    if not update_result or len(update_result) == 0:
        # If no existing record, create one
        bransch_names = {
            "restaurant": "Restaurang & Cafe",
            "retail": "Butik & Kassa",
            "customerservice": "Kundtjanst & Support",
            "tech": "Tech & Kontor",
            "healthcare": "Vard & Omsorg",
            "industry": "Tradgard & Industri",
            "reception": "Hotell & Reception",
            "contentmoderation": "Content & Moderation"
        }

        await db_request(
            "POST",
            "user_cvs",
            data={
                "user_id": user_id,
                "vibe_id": bransch_id,
                "vibe_name": bransch_names.get(bransch_id, bransch_id),
                "pdf_url": pdf_url,
                "cv_text": cv_text[:50000] if cv_text else None
            }
        )

    return {
        "success": True,
        "pdf_url": pdf_url,
        "bransch_id": bransch_id
    }


@app.post("/api/upload/profile-photo")
async def upload_profile_photo(request: Request):
    """Upload profile photo"""
    user_id = await get_user_id_from_request(request, required=True)

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
        "location_by_region": profile.get("location_by_region") or {},
        "email_signature": profile.get("email_signature", ""),
        "birth_date": profile.get("birth_date"),
        "training_letter_analyzed": len(letters) > 0,
        "training_letter_count": len(letters),
        "cv_uploaded": len(cv_uploads) > 0,
        "cv_count": len(cv_uploads)
    }


@app.patch("/api/profile/details")
async def update_profile_details(request: Request):
    """Update user profile fields (name, phone, email, location)."""
    user_id = await get_user_id_from_request(request, required=True)

    body = await request.json()
    allowed_fields = {"full_name", "phone", "email", "location", "drivers_license", "location_by_region"}
    update_data = {k: v for k, v in body.items() if k in allowed_fields}
    if not update_data:
        raise HTTPException(status_code=400, detail="Inga giltiga fält att uppdatera")

    update_data["updated_at"] = datetime.now().isoformat()

    result = await db_request(
        "PATCH",
        f"user_profiles?user_id=eq.{user_id}",
        data=update_data
    )
    if not result:
        # No row yet — create one
        update_data["user_id"] = user_id
        await db_request("POST", "user_profiles", data=update_data)

    return {"success": True}


@app.patch("/api/profile/signature")
async def update_email_signature(request: Request):
    """Save the user's custom email signature."""
    user_id = await get_user_id_from_request(request, required=True)

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


@app.patch("/api/profile/birth-date")
async def update_birth_date(request: Request):
    """Save the user's birth date for accurate age calculation."""
    user_id = await get_user_id_from_request(request, required=True)

    body = await request.json()
    birth_date = body.get("birth_date")

    if not birth_date:
        raise HTTPException(status_code=400, detail="Födelsedatum krävs")

    result = await db_request(
        "PATCH",
        f"user_profiles?user_id=eq.{user_id}",
        data={"birth_date": birth_date, "updated_at": datetime.now().isoformat()}
    )
    if not result:
        await db_request("POST", "user_profiles", data={
            "user_id": user_id,
            "full_name": "",
            "birth_date": birth_date
        })

    return {"success": True}


@app.post("/api/upload/training-letter")
async def upload_training_letter(request: Request):
    """Upload training letter PDF and analyze tone/style"""
    user_id = await get_user_id_from_request(request, required=True)

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
                    "liked_phrases": tone_analysis.get("favorite_phrases", [])
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
                    "liked_phrases": tone_analysis.get("favorite_phrases", [])
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
    user_id = await get_user_id_from_request(request)
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
        "phrases": p.get("liked_phrases") if isinstance(p.get("liked_phrases"), list) else [],
        "avoid": p.get("avoid_phrases") if isinstance(p.get("avoid_phrases"), list) else [],
        "never_mention": p.get("never_mention") if isinstance(p.get("never_mention"), list) else [],
        "length_preference": p.get("length_preference"),
        "opening_style": p.get("opening_style"),
        "custom_ai_instructions": p.get("custom_ai_instructions") or "",
        "greeting_style": p.get("greeting_style") or "Hej!",
        "signature_style": p.get("signature_style") or "Med vänliga hälsningar",
        "sign_off_name": p.get("sign_off_name") or "",
        "sign_off_phone": p.get("sign_off_phone") or "",
        "sign_off_email": p.get("sign_off_email") or "",
        "max_words": p.get("max_words") or 200
    }
    return {"style_summary": style_summary}


@app.get("/api/user/training-letters")
async def get_user_training_letters(request: Request):
    """Get all training letters uploaded by the user"""
    user_id = await get_user_id_from_request(request, required=True)

    letters = await db_request("GET", "user_training_letters",
        params={"user_id": f"eq.{user_id}", "order": "uploaded_at.desc"})

    return {"success": True, "letters": letters or []}


@app.delete("/api/user/training-letters/{letter_id}")
async def delete_user_training_letter(letter_id: str, request: Request):
    """Delete a training letter"""
    user_id = await get_user_id_from_request(request, required=True)

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
    user_id = await get_user_id_from_request(request, required=True)

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

    # Analyze tone and extract anecdotes in parallel
    import asyncio as _asyncio
    tone_analysis, _ = await _asyncio.gather(
        analyze_writing_tone_rich(letter_text),
        extract_anecdotes_from_letter(user_id, letter_text)
    )
    await save_letter_style(user_id, tone_analysis)

    return {"success": True, "tone_analysis": tone_analysis, "file_url": file_url}


@app.post("/api/user/analyze-letter-text")
async def analyze_pasted_letter_text(request: Request):
    """Analyze pasted cover letter text to extract writing style.
    Also saves text to user_training_letters so it's included in future aggregations."""
    user_id = await get_user_id_from_request(request, required=True)

    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Ingen text angiven")

    # Save pasted text as a training letter so it's included in future re-analyses
    await db_request("POST", "user_training_letters", data={
        "user_id": user_id,
        "filename": "Inklistrad text",
        "letter_text": text,
        "file_url": None
    })

    # Analyze tone and extract anecdotes in parallel
    import asyncio as _asyncio
    tone_analysis, _ = await _asyncio.gather(
        analyze_writing_tone_rich(text),
        extract_anecdotes_from_letter(user_id, text)
    )
    await save_letter_style(user_id, tone_analysis)

    return {"success": True, "tone_analysis": tone_analysis}


async def save_letter_style(user_id: str, analysis: dict):
    """Save or update letter style analysis in DB.
    Re-analyzes ALL training letters together so styles from multiple letters are combined."""
    # Fetch all training letters for this user
    all_letters = await db_request("GET", "user_training_letters",
        params={"user_id": f"eq.{user_id}", "select": "letter_text", "order": "uploaded_at.asc"}) or []

    letter_texts = [l.get("letter_text", "") for l in all_letters if l.get("letter_text") and not l["letter_text"].startswith("[")]

    # If we have multiple letters, re-analyze them all together
    if len(letter_texts) > 1:
        analysis = await analyze_writing_tone_multi(letter_texts)
    # If only one letter (or none with text), use the single-letter analysis as-is

    existing = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})
    data = {
        "tone": analysis.get("tone"),
        "writing_style": analysis.get("structure"),
        "liked_phrases": analysis.get("phrases", []),
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


async def extract_anecdotes_from_letter(user_id: str, letter_text: str):
    """Extract personal anecdotes and hobbies from a cover letter using AI.
    Adds new anecdotes to user_anecdotes, skipping duplicates by title."""
    if not ANTHROPIC_API_KEY or not letter_text or len(letter_text) < 50:
        return

    prompt = f"""Analysera detta personliga brev och extrahera ALLA personliga anekdoter, hobbys och personliga kopplingar som personen nämner.

Brev (kan vara på svenska ELLER engelska — extrahera oavsett språk):
{letter_text[:3000]}

Returnera ett JSON-objekt med en enda nyckel "anecdotes" som är en lista. Varje element ska ha:
- "title": kort titel (max 5 ord, på svenska), t.ex. "Svenska Kyrkan" eller "Gymma"
- "type": "anecdote" eller "hobby"
- "content": hela berättelsen/beskrivningen extraherad ur brevet (på svenska, översätt om brevet är på engelska)
- "keywords": lista med 3-8 nyckelord som matchar vilka jobb anekdoten passar för

Extrahera BARA saker som är personliga/unika — inte generell arbetslivserfarenhet.
Exempel på vad som räknas:
- Volontärarbete, ideellt engagemang
- Personliga kopplingar till organisationer
- Hobbys som nämns
- Personliga historier/berättelser
- Kopplingar till specifika platser eller kulturer

Om inga personliga anekdoter finns i brevet, returnera {{"anecdotes": []}}.

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
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=25
            )
            if response.status_code == 200:
                result = response.json()
                raw = result["content"][0]["text"].strip()
                import json as json_lib
                start = raw.find('{')
                end = raw.rfind('}') + 1
                if start >= 0 and end > start:
                    parsed = json_lib.loads(raw[start:end])
                    new_anecdotes = parsed.get("anecdotes", [])

                    if not new_anecdotes:
                        return

                    # Fetch existing anecdotes to avoid duplicates
                    existing = await db_request("GET", "user_anecdotes",
                        params={"user_id": f"eq.{user_id}", "select": "title"}) or []
                    existing_titles = {a["title"].lower().strip() for a in existing}

                    for a in new_anecdotes:
                        title = a.get("title", "").strip()
                        if not title or title.lower() in existing_titles:
                            continue
                        a_type = a.get("type", "anecdote")
                        if a_type not in ("anecdote", "hobby"):
                            a_type = "anecdote"
                        try:
                            await db_request("POST", "user_anecdotes", data={
                                "user_id": user_id,
                                "title": title,
                                "type": a_type,
                                "content": a.get("content", title),
                                "keywords": a.get("keywords", [])
                            })
                            existing_titles.add(title.lower())
                        except Exception as e:
                            logger.error(f"Error saving anecdote '{title}': {e}")
    except Exception as e:
        logger.error(f"Anecdote extraction error: {e}")


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
- "phrases": Lista med 3-6 fraser eller uttryck som personen faktiskt använder. EXKLUDERA fraser som innehåller specifik ålder (t.ex. "jag är en 27-årig") — åldern kan vara inaktuell.
- "avoid": Lista med ord eller fraser som personen INTE använder (t.ex. klichéer som de aktivt undviker)
- "length_preference": En mening om brevets längd och takt, t.ex. "Kortfattat, max 3 stycken, ingen onödig utfyllnad"
- "opening_style": En mening om hur personen brukar inleda, t.ex. "Börjar alltid med vad som drog dem till just det företaget". EXKLUDERA specifik ålder från öppningen.

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


async def analyze_writing_tone_multi(letter_texts: list) -> dict:
    """Analyze writing style across multiple training letters, noting differences between them."""
    if not ANTHROPIC_API_KEY:
        return {}

    letters_block = ""
    for i, text in enumerate(letter_texts, 1):
        letters_block += f"\n--- BREV {i} ---\n{text[:2000]}\n"

    prompt = f"""Du analyserar {len(letter_texts)} personliga brev på svenska från samma person. Breven kan vara skrivna för OLIKA typer av jobb och ha olika stil.

{letters_block}

Returnera ett JSON-objekt med dessa exakta nycklar:
- "tone": Beskriv tonen. Om breven har olika ton, beskriv BÅDA, t.ex. "Brev 1: Formellt och sakligt. Brev 2: Personligt och varmt"
- "structure": Beskriv strukturen. Om breven är uppbyggda olika, beskriv BÅDA skillnaderna, t.ex. "Brev 1: Klassiskt format med inledning-kropp-avslut. Brev 2: Punktlista med konkreta resultat"
- "phrases": Lista med ALLA unika fraser eller uttryck som personen faktiskt använder, samlade från ALLA brev. Ju fler brev, desto längre lista. Minst 3 per brev. EXKLUDERA fraser med specifik ålder (t.ex. "jag är en 27-årig") — åldern kan vara inaktuell.
- "avoid": Lista med ALLA ord eller fraser som personen konsekvent INTE använder (klichéer de undviker). Samla från alla brev. Ju fler brev, desto längre lista.
- "length_preference": Beskriv längd och tempo. Om breven skiljer sig, nämn det.
- "opening_style": Beskriv hur personen inleder. Om olika öppningar, beskriv båda.

VIKTIGT: Om breven har tydligt olika stil, visa BÅDA stilarna. Slå inte ihop dem till en generisk beskrivning.

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
                    "max_tokens": 1000,
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
        logger.error(f"Multi-letter tone analysis error: {e}")

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
                    "model": "claude-sonnet-4-5-20250929",
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


# ============== SAVE GENERATED LETTER AS TRAINING EXAMPLE ==============

@app.post("/api/user/save-letter-as-example")
async def save_letter_as_example(request: Request):
    """Save a generated cover letter as a training example.
    This re-trains the AI style and extracts any new anecdotes."""
    user_id = await get_user_id_from_request(request, required=True)

    body = await request.json()
    letter_text = body.get("letter_text", "").strip()
    job_title = body.get("job_title", "AI-genererat brev")

    if not letter_text:
        raise HTTPException(status_code=400, detail="Inget brev att spara")

    # Save as training letter
    await db_request("POST", "user_training_letters", data={
        "user_id": user_id,
        "filename": f"Bra exempel: {job_title}",
        "letter_text": letter_text,
        "file_url": None
    })

    # Re-analyze style and extract anecdotes in parallel
    import asyncio as _asyncio
    tone_analysis, _ = await _asyncio.gather(
        analyze_writing_tone_rich(letter_text),
        extract_anecdotes_from_letter(user_id, letter_text)
    )
    await save_letter_style(user_id, tone_analysis)

    return {"success": True, "message": "Brevet sparades som träningsexempel!"}


# ============== ANECDOTES & HOBBIES ==============

@app.get("/api/user/anecdotes")
async def get_user_anecdotes(request: Request):
    """Get all anecdotes and hobbies for the user"""
    user_id = await get_user_id_from_request(request, required=True)
    anecdotes = await db_request("GET", "user_anecdotes",
        params={"user_id": f"eq.{user_id}", "order": "created_at.desc"})
    return {"success": True, "anecdotes": anecdotes or []}


@app.post("/api/user/anecdotes")
async def create_user_anecdote(request: Request):
    """Create a new anecdote or hobby"""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()

    title = body.get("title", "").strip()
    anecdote_type = body.get("type", "anecdote")
    content = body.get("content", "").strip()
    keywords = body.get("keywords", [])

    if not title or not content:
        raise HTTPException(status_code=400, detail="Titel och innehåll krävs")
    if anecdote_type not in ("anecdote", "hobby"):
        raise HTTPException(status_code=400, detail="Typ måste vara 'anecdote' eller 'hobby'")

    result = await db_request("POST", "user_anecdotes", data={
        "user_id": user_id,
        "title": title,
        "type": anecdote_type,
        "content": content,
        "keywords": keywords
    }, params={"select": "*"})

    return {"success": True, "anecdote": result[0] if result else None}


@app.delete("/api/user/anecdotes/{anecdote_id}")
async def delete_user_anecdote(anecdote_id: str, request: Request):
    """Delete an anecdote or hobby"""
    user_id = await get_user_id_from_request(request, required=True)
    await db_request("DELETE", "user_anecdotes",
        params={"id": f"eq.{anecdote_id}", "user_id": f"eq.{user_id}"})
    return {"success": True}


# ============== STYLE FIELD EDITING ==============

@app.patch("/api/user/letter-style")
async def update_letter_style(request: Request):
    """Update individual style fields (tone, structure, length_preference, opening_style, custom_ai_instructions)"""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()

    # Only allow updating these specific fields
    allowed_fields = {
        "tone": "tone",
        "structure": "writing_style",
        "length_preference": "length_preference",
        "opening_style": "opening_style",
        "custom_ai_instructions": "custom_ai_instructions",
        "greeting_style": "greeting_style",
        "signature_style": "signature_style",
        "sign_off_name": "sign_off_name",
        "sign_off_phone": "sign_off_phone",
        "sign_off_email": "sign_off_email",
        "max_words": "max_words"
    }

    update_data = {}
    for frontend_key, db_column in allowed_fields.items():
        if frontend_key in body:
            update_data[db_column] = body[frontend_key]

    if not update_data:
        raise HTTPException(status_code=400, detail="Inga fält att uppdatera")

    update_data["updated_at"] = datetime.now().isoformat()

    existing = await db_request("GET", "user_cover_letter_preferences", params={"user_id": f"eq.{user_id}"})
    if existing and len(existing) > 0:
        await db_request("PATCH", "user_cover_letter_preferences",
            params={"user_id": f"eq.{user_id}"}, data=update_data)
    else:
        await db_request("POST", "user_cover_letter_preferences",
            data={"user_id": user_id, **update_data})

    return {"success": True}


# ============== STYLE PHRASE EDITING ==============

@app.patch("/api/user/letter-style/phrases")
async def update_letter_style_phrases(request: Request):
    """Add or remove phrases from the avoid or liked_phrases lists"""
    user_id = await get_user_id_from_request(request, required=True)
    body = await request.json()

    action = body.get("action")  # "add" or "remove"
    list_name = body.get("list")  # "avoid" or "phrases"
    phrase = body.get("phrase", "").strip()

    if action not in ("add", "remove") or list_name not in ("avoid", "phrases", "never_mention"):
        raise HTTPException(status_code=400, detail="Ogiltig action eller list")
    if not phrase:
        raise HTTPException(status_code=400, detail="Fras krävs")

    # Map frontend names to DB column names
    db_column_map = {"avoid": "avoid_phrases", "phrases": "liked_phrases", "never_mention": "never_mention"}
    db_column = db_column_map[list_name]

    # Get current preferences
    prefs = await db_request("GET", "user_cover_letter_preferences",
        params={"user_id": f"eq.{user_id}"})

    if not prefs or len(prefs) == 0:
        # Create preferences if they don't exist
        current_list = []
        if action == "add":
            current_list = [phrase]
        await db_request("POST", "user_cover_letter_preferences",
            data={"user_id": user_id, db_column: current_list})
    else:
        current_list = prefs[0].get(db_column, []) or []
        if not isinstance(current_list, list):
            current_list = []

        if action == "add" and phrase not in current_list:
            current_list.append(phrase)
        elif action == "remove":
            current_list = [p for p in current_list if p != phrase]

        await db_request("PATCH", "user_cover_letter_preferences",
            params={"user_id": f"eq.{user_id}"}, data={db_column: current_list})

    return {"success": True, db_column: current_list}


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})
