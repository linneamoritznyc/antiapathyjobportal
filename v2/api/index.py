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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

HF_SWEDISH_VIBE_MODEL = "https://api-inference.huggingface.co/models/KBLab/bert-base-swedish-cased"


def get_app_base_url() -> str:
    """Return the canonical base URL for this deployment (no trailing slash).
    Priority: APP_BASE_URL env var > REPLIT_DEV_DOMAIN > fallback localhost."""
    custom = os.getenv("APP_BASE_URL", "").rstrip("/")
    if custom:
        return custom
    replit_domain = os.getenv("REPLIT_DEV_DOMAIN", "") or os.getenv("REPLIT_DOMAINS", "").split(",")[0].strip()
    if replit_domain:
        return f"https://{replit_domain}"
    return "http://localhost:5000"

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

TOTALFÖRBJUDNA ORD (existerar inte på svenska, använd ALDRIG i någon form):
  "rondera", "ronder", "rond", "rondering" — dessa ord finns INTE. Om jobbannonsen nämner "rondera lokaler", skriv ISTÄLLET t.ex. "gå igenom lokalerna", "kolla att allt ser bra ut", "hålla koll på lokalerna".

FÖRBJUDNA FORMELLA/STELA UTTRYCK (använd det vardagliga alternativet):
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


class UrlJobRequest(BaseModel):
    url: str


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
