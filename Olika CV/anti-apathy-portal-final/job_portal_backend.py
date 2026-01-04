"""
Anti-Apathy Job Portal - Backend System
AI-driven jobbsökningsportal för neurodivergenta profiler
"""

import sqlite3
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import logging
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JobPriority(Enum):
    AKUT = "akut"  # Deadline inom 3 dagar
    STRATEGISK = "strategisk"  # Deadline 4-14 dagar
    HIDDEN = "hidden"  # Dolda jobb via nätverk


class ApplicationStatus(Enum):
    NEW = "new"
    LETTER_GENERATED = "letter_generated"
    DRAFT_SAVED = "draft_saved"
    SENT = "sent"
    FOLLOW_UP_SENT = "follow_up_sent"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


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


class DatabaseManager:
    """Hanterar SQLite databas för jobb och ansökningar"""
    
    def __init__(self, db_path: str = "data/jobs.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Jobs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                url TEXT,
                source TEXT,
                priority TEXT,
                deadline TEXT,
                contact_email TEXT,
                contact_name TEXT,
                why_perfect TEXT,
                created_at TEXT,
                link_status TEXT DEFAULT 'active'
            )
        ''')
        
        # Applications table
        c.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                status TEXT NOT NULL,
                cover_letter TEXT,
                gmail_draft_id TEXT,
                sent_at TEXT,
                follow_up_at TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        ''')
        
        # User data table
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Stats table
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                jobs_scraped INTEGER DEFAULT 0,
                applications_sent INTEGER DEFAULT 0,
                interviews INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def save_job(self, job: Job) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO jobs 
                (id, title, company, location, description, url, source, priority, 
                 deadline, contact_email, contact_name, why_perfect, created_at, link_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (job.id, job.title, job.company, job.location, job.description,
                  job.url, job.source, job.priority, job.deadline, job.contact_email,
                  job.contact_name, job.why_perfect, job.created_at, job.link_status))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return False
        finally:
            conn.close()
    
    def get_next_job(self) -> Optional[Job]:
        """Hämta nästa jobb att visa - prioriterar AKUT, sen STRATEGISK"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Platser att filtrera på
        allowed_locations = ["Stockholm", "Sollentuna", "Vetlanda", "Nässjö", "Eksjö", "Holsbybrunn", "Småland", "Jönköping"]
        location_filter = " OR ".join([f"j.location LIKE '%{loc}%'" for loc in allowed_locations])
        
        # Hitta jobb som inte har en ansökan ännu och matchar platserna
        c.execute(f'''
            SELECT j.* FROM jobs j
            LEFT JOIN applications a ON j.id = a.job_id
            WHERE a.id IS NULL AND j.link_status = 'active'
            AND ({location_filter})
            ORDER BY 
                CASE j.priority 
                    WHEN 'akut' THEN 1 
                    WHEN 'strategisk' THEN 2 
                    ELSE 3 
                END,
                j.deadline ASC NULLS LAST
            LIMIT 1
        ''')
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return Job(
                id=row[0], title=row[1], company=row[2], location=row[3],
                description=row[4], url=row[5], source=row[6], priority=row[7],
                deadline=row[8], contact_email=row[9], contact_name=row[10],
                why_perfect=row[11], created_at=row[12], link_status=row[13]
            )
        return None
    
    def get_all_jobs(self, limit: int = 100) -> List[Job]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        
        return [Job(
            id=r[0], title=r[1], company=r[2], location=r[3],
            description=r[4], url=r[5], source=r[6], priority=r[7],
            deadline=r[8], contact_email=r[9], contact_name=r[10],
            why_perfect=r[11], created_at=r[12], link_status=r[13]
        ) for r in rows]
    
    def save_application(self, job_id: str, status: str, cover_letter: str = None, 
                        gmail_draft_id: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        c.execute('''
            INSERT INTO applications (job_id, status, cover_letter, gmail_draft_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_id, status, cover_letter, gmail_draft_id, now, now))
        
        app_id = c.lastrowid
        conn.commit()
        conn.close()
        return app_id
    
    def update_application_status(self, job_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE applications SET status = ?, updated_at = ? WHERE job_id = ?
        ''', (status, datetime.now().isoformat(), job_id))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, int]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stats = {}
        
        c.execute('SELECT COUNT(*) FROM jobs WHERE link_status = "active"')
        stats['total_jobs'] = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM applications')
        stats['total_applications'] = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM applications WHERE status = "sent"')
        stats['sent_applications'] = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM applications WHERE status = "interview"')
        stats['interviews'] = c.fetchone()[0]
        
        c.execute('''
            SELECT COUNT(*) FROM jobs j
            LEFT JOIN applications a ON j.id = a.job_id
            WHERE a.id IS NULL AND j.link_status = 'active'
        ''')
        stats['pending_jobs'] = c.fetchone()[0]
        
        # Jobb med deadline idag
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            SELECT COUNT(*) FROM jobs 
            WHERE deadline LIKE ? AND link_status = 'active'
        ''', (f'{today}%',))
        stats['deadline_today'] = c.fetchone()[0]
        
        conn.close()
        return stats
    
    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return Job(
                id=row[0], title=row[1], company=row[2], location=row[3],
                description=row[4], url=row[5], source=row[6], priority=row[7],
                deadline=row[8], contact_email=row[9], contact_name=row[10],
                why_perfect=row[11], created_at=row[12], link_status=row[13]
            )
        return None


class JobScraper:
    """Scrapar jobb från Platsbanken API"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.base_url = "https://platsbanken-api.arbetsformedlingen.se/jobs/v1/search"
        
        # Linneas sökkriterier - endast Sverige
        self.search_keywords = [
            "servitör",
            "servitris", 
            "trädgård",
            "trädgårdsarbetare",
            "content moderator",
            "moderator svenska",
            "kundtjänst",
            "receptionist",
            "café",
            "barista"
        ]
        
        self.locations = ["Stockholm", "Sollentuna", "Vetlanda", "Nässjö", "Eksjö", "Holsbybrunn", "Småland", "Jönköping"]
    
    def generate_job_id(self, title: str, company: str, url: str) -> str:
        """Generera unikt ID för jobb"""
        content = f"{title}{company}{url}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def classify_priority(self, deadline: Optional[str]) -> str:
        """Klassificera jobb baserat på deadline"""
        if not deadline:
            return JobPriority.STRATEGISK.value
        
        try:
            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            days_left = (deadline_date - datetime.now(deadline_date.tzinfo)).days
            
            if days_left <= 3:
                return JobPriority.AKUT.value
            elif days_left <= 14:
                return JobPriority.STRATEGISK.value
            else:
                return JobPriority.STRATEGISK.value
        except:
            return JobPriority.STRATEGISK.value
    
    def scrape_platsbanken(self, keyword: str, location: str = None) -> List[Job]:
        """Scrapa jobb från Platsbanken API"""
        jobs = []
        
        try:
            response = requests.post(
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
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for hit in data.get("ads", []):
                    try:
                        job_id = hit.get("id", self.generate_job_id(
                            hit.get("title", ""),
                            hit.get("workplaceName", ""),
                            str(hit.get("id", ""))
                        ))
                        
                        deadline = hit.get("lastApplicationDate")
                        
                        job = Job(
                            id=str(job_id),
                            title=hit.get("title", "Okänd titel"),
                            company=hit.get("workplaceName", "Okänt företag"),
                            location=hit.get("workplace", location or "Sverige"),
                            description=hit.get("description", "")[:2000] if hit.get("description") else "",
                            url=f"https://arbetsformedlingen.se/platsbanken/annonser/{job_id}",
                            source="platsbanken",
                            priority=self.classify_priority(deadline),
                            deadline=deadline,
                            contact_email=None,
                            contact_name=None,
                            why_perfect=None,
                            created_at=datetime.now().isoformat()
                        )
                        jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job: {e}")
                        continue
                
                logger.info(f"Scraped {len(jobs)} jobs for '{keyword}' in {location or 'Sverige'}")
            else:
                logger.warning(f"Platsbanken API returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error scraping Platsbanken: {e}")
        
        return jobs
    
    def scrape_all(self) -> int:
        """Scrapa alla jobb baserat på sökkriterier"""
        total_jobs = 0
        
        for keyword in self.search_keywords:
            # Sök i alla locations
            for location in self.locations:
                jobs = self.scrape_platsbanken(keyword, location)
                for job in jobs:
                    if self.db.save_job(job):
                        total_jobs += 1
            
            # Sök utan location (remote/hela Sverige)
            jobs = self.scrape_platsbanken(keyword)
            for job in jobs:
                if self.db.save_job(job):
                    total_jobs += 1
        
        logger.info(f"Total jobs scraped and saved: {total_jobs}")
        return total_jobs


class AIContactFinder:
    """Använder Claude API för att hitta kontaktinfo"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def find_contact(self, company: str, job_title: str) -> Dict[str, str]:
        """Hitta kontaktperson för ett jobb"""
        if not self.api_key:
            logger.warning("No Anthropic API key set")
            return {}
        
        prompt = f"""Hitta kontaktinformation för att söka jobb hos {company} för positionen {job_title}.

Returnera JSON med:
- contact_name: Namn på HR-chef eller rekryterare om känt
- contact_email: Email om känt (gissa format som fornamn.efternamn@företag.se)
- contact_title: Titel på kontaktperson

Om du inte kan hitta specifik info, föreslå generisk rekrytering@{company.lower().replace(' ', '')}.se

Returnera ENDAST JSON, ingen annan text."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
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
                content = response.json()["content"][0]["text"]
                # Försök parsa JSON från svaret
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"Error finding contact: {e}")
        
        return {}


class CoverLetterGenerator:
    """Genererar personliga brev med Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.cv_path = "linnea_cv.pdf"
    
    def load_cv_summary(self) -> str:
        """Ladda CV-sammanfattning"""
        # Hårdkodad sammanfattning baserat på Linneas profil
        return """
        Linnea Moritz - Cubist Oil Painter & International Artist
        
        Erfarenhet:
        - Driver internationell konstverksamhet via Shopify (linneamoritz.com)
        - 39 utställningar i 21 städer, 10 länder, 4 kontinenter
        - Art Basel Hong Kong, Florence, Stockholm, Mexico City, Seoul, Dubai
        - 3 första pris i konsttävlingar
        - 5,800 Instagram-följare
        
        Färdigheter:
        - Projektledning och eventplanering
        - Digital marknadsföring och e-handel
        - Kundrelationer och försäljning
        - Flerspråkig: Svenska, Engelska, Norska, Danska
        - Kreativ problemlösning
        - Detaljorienterad och metodisk
        
        Personlighet:
        - Entreprenöriell och självgående
        - Internationell erfarenhet
        - Stark arbetsmoral
        - Flexibel och anpassningsbar
        """
    
    def generate_why_perfect(self, job: Job) -> str:
        """Generera 'Varför är detta jobb perfekt för dig?' text"""
        if not self.api_key:
            return "Matchar din profil och erfarenhet."
        
        cv_summary = self.load_cv_summary()
        
        prompt = f"""Baserat på denna CV:
{cv_summary}

Och detta jobb:
Titel: {job.title}
Företag: {job.company}
Beskrivning: {job.description[:1000]}

Skriv EN mening (max 20 ord) om varför detta jobb är perfekt för denna kandidat.
Var specifik och personlig. Fokusera på matchning mellan erfarenhet och jobbkrav.
Skriv på svenska. Ingen inledning, bara meningen."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 100,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"].strip()
                
        except Exception as e:
            logger.error(f"Error generating why_perfect: {e}")
        
        return "Matchar din bakgrund inom service och kundkontakt."
    
    def detect_job_category(self, job: Job) -> str:
        """Detektera jobbkategori baserat på titel och beskrivning"""
        text = f"{job.title} {job.description}".lower()
        
        categories = {
            "contentmoderation": ["content moderation", "moderator", "innehållsmoderator", "trust & safety", "trust and safety", "community guidelines", "moderation", "content review", "policy"],
            "restaurant": ["servitör", "servitris", "restaurang", "kock", "köksbiträde", "café", "kafé", "barista", "pizzeria", "bar", "krog", "steakhouse", "hamburgare", "mat", "servering"],
            "retail": ["butik", "kassa", "försäljare", "butikssäljare", "ica", "coop", "willys", "lidl", "säljare", "butiksmedarbetare"],
            "industry": ["industri", "lager", "fabrik", "produktion", "operatör", "montör", "trädgård", "park", "städ", "lokalvård", "fysiskt", "bygg"],
            "healthcare": ["vård", "omsorg", "äldreboende", "hemtjänst", "undersköterska", "vårdbiträde", "demens"],
            "tech": ["it", "tech", "data", "analyst", "digital", "programmering", "utvecklare", "software"],
            "customerservice": ["kundtjänst", "customer service", "support", "helpdesk", "kundsupport", "kundservice"],
            "reception": ["reception", "receptionist", "telefon", "administration", "kontor"],
            "art": ["konst", "konstnär", "galleri", "museum", "utställning", "kultur", "vikarie", "konstvikarie", "ateljé"]
        }
        
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        return "general"
    
    def get_relevant_experience(self, category: str) -> str:
        """Hämta relevant erfarenhet för jobbkategorin"""
        experiences = {
            "restaurant": """- Restaurangbiträde på Max Hamburgare (Apr-Aug 2024): Drive-in, fritös, kök, servering, kassa, städ
- Försäljare/Barista på House of Beans, Hötorgshallen (Aug 2024-Feb 2025): Sålde te, kaffe, choklad. Ensam i butiken 8h
- Cafépersonal på Coffeehouse by George, Nacka (2014-2015): Kassahantering, barista, matberedning, servering
- Köksbiträde på Vetlanda Kommun (Juli-Aug 2017): Matlagning och servering""",
            
            "retail": """- Försäljare på House of Beans, Hötorgshallen (Aug 2024-Feb 2025): Direktförsäljning, ensam i butik 8h
- Kassapersonal på ICA Maxi (2015, 2017, 2019): Kassa, självscanning, frukt/grönt, chark, blommor
- Gårdsvärd på Siggesta Gård (2014-2015): Kundbemötande, marknad med ~1000 besökare/söndag""",
            
            "industry": """- Anodiseringsoperatör på Profilgruppen, Åseda (Juli-Aug 2024): Tungt fysiskt arbete, tvåskift (06-14, 14-23), handtravers
- Trädgårdsarbete på Siggesta Gård (2014-2015): Gräsklippning, ogräsrensning, buskklippning, plantering, golfbil""",
            
            "healthcare": """- Timvikarie på Kvarngården äldreboende (Maj-Sep 2020): Omvårdnad, medicinhantering, måltidsassistans, dokumentation, demens/Alzheimers, morgon/kvällspass, covid-protokoll""",
            
            "tech": """- Kvalitetsgranskare på TikTok/ByteDance (Maj-Jun 2022): Granskade moderatorers arbete
- Innehållsmoderator på YouTube Ads (Feb-Jun 2022): Svenska marknaden, flaggade olämplig reklam
- Innehållsmoderator på Clubhouse (Jun 2021-Jan 2022): Trust & Safety, svenska/norska/danska marknaden, ökade produktivitet 98%
- Innehållsanalytiker på Google Ads (Maj 2018-Apr 2019): 100+ annonser/dag, svenska marknaden""",
            
            "reception": """- Gårdsvärd på Wallby Säteri (Jun-Aug 2016): Reception, bokningar, telefon, betalningar, café
- Global Marketing på Minerva Project (Sep 2019-Apr 2020): Kundservice via Intercom för 2000+ sökande"""
        }
        
        return experiences.get(category, experiences["restaurant"])
    
    def generate_email_body(self, job: Job, job_url: str = None) -> str:
        """Generera kort mail-pitch (max 60-80 ord) MED Platsbanken-länk"""
        if not self.api_key:
            return self._generate_template_email(job, job_url)
        
        category = self.detect_job_category(job)
        url = job_url or job.url or f"https://arbetsformedlingen.se/platsbanken/annonser/{job.id}"
        
        prompt = f"""Skriv ett KORT ansökningsmail på svenska (max 70 ord).

JOBBET:
Titel: {job.title}
Företag: {job.company}
Plats: {job.location}
Platsbanken-länk: {url}

REGLER - FÖLJ EXAKT:
1. Max 70 ord totalt
2. Börja med "Hej!" eller "Hej {job.company}!"
3. ANDRA MENINGEN måste vara: "Jag hittade er annons på Platsbanken ({url}) och är intresserad av tjänsten som {job.title}."
4. EN mening med din starkaste merit:
   - Restaurang/café: Nämn Max Hamburgare eller House of Beans
   - Butik: Nämn ICA kassaerfarenhet  
   - Industri: Nämn Profilgruppen
   - Vård: Nämn Kvarngården äldreboende
5. Nämn: flexibel med tider, tillgänglig omgående
6. Skriv: "Se bifogat CV och personligt brev."
7. Avsluta: "Vänliga hälsningar," ny rad "Linnea Moritz" ny rad "0761166109"

NÄMN ALDRIG konst, målning, utställningar eller Shopify.

Skriv ENDAST mailet."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 250,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"].strip()
                
        except Exception as e:
            logger.error(f"Error generating email: {e}")
        
        return self._generate_template_email(job, job_url)
    
    def _generate_template_email(self, job: Job, job_url: str = None) -> str:
        """Fallback template för mail"""
        url = job_url or job.url or f"https://arbetsformedlingen.se/platsbanken/annonser/{job.id}"
        return f"""Hej {job.company}!

Jag hittade er annons på Platsbanken ({url}) och är intresserad av tjänsten som {job.title}.

Jag har tidigare erfarenhet inom service och trivs i miljöer med högt tempo. Jag är flexibel med arbetstider och kan börja omgående.

Se bifogat CV och personligt brev.

Vänliga hälsningar,
Linnea Moritz
0761166109"""

    def generate_cover_letter(self, job: Job) -> str:
        """Generera personligt brev (längre, för PDF-bilaga)"""
        if not self.api_key:
            return self._generate_template_letter(job)
        
        # Detektera jobbkategori och hämta relevant erfarenhet
        category = self.detect_job_category(job)
        relevant_exp = self.get_relevant_experience(category)
        
        # Skapa Platsbanken-länk
        job_url = job.url if job.url else f"https://arbetsformedlingen.se/platsbanken/annonser/{job.id}"
        
        prompt = f"""Skriv ett PERSONLIGT BREV på svenska (ca 150-200 ord) som ska bifogas som PDF.

===MIN RELEVANTA ERFARENHET===
{relevant_exp}

===ÖVRIG INFO OM MIG===
- Linnea Moritz, 28 år
- Bor i Sollentuna
- Har B-körkort (automat)
- Tillgänglig omgående, flexibel med arbetstider (kvällar, helger)
- Telefon: 0761166109
- Språk: Svenska (modersmål), Engelska (flytande)
- Certifikat: ICA kassahantering, Röda Korset första hjälpen
- Examen från Minerva University (USA) - visar ansvarstagande och stabilitet

===JOBBET===
Titel: {job.title}
Företag: {job.company}
Plats: {job.location}
Beskrivning: {job.description[:1500]}

===REGLER===
1. Skriv 150-200 ord
2. Börja med "Hej {job.company}!" eller "Till {job.company},"
3. Förklara VARFÖR du vill jobba just där
4. Lyft fram 2-3 konkreta erfarenheter från listan ovan som matchar jobbet
5. Visa personlighet - berätta kort vad du trivs med i arbetet
6. Nämn att du är stabil, ansvarsfull och har lång arbetslivserfarenhet
7. Om HELTID nämns: Skriv att du söker heltid
8. Nämn Sollentuna + B-körkort + flexibel med tider
9. Avsluta med: "Jag ser fram emot att höra från er."
10. Signera: "Med vänlig hälsning, Linnea Moritz" + telefon + email

NÄMN ALDRIG konst, målning, utställningar, Shopify eller e-handel.

Skriv ENDAST brevet."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
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
            logger.error(f"Error generating cover letter: {e}")
        
        return self._generate_template_letter(job)
    
    def _generate_template_letter(self, job: Job) -> str:
        """Fallback template om API inte fungerar"""
        category = self.detect_job_category(job)
        relevant_exp = self.get_relevant_experience(category)
        
        # Ta första erfarenheten för kategorin
        first_exp = relevant_exp.split('\n')[0] if relevant_exp else "kundservice och försäljning"
        
        return f"""Hej!

Jag söker tjänsten som {job.title} hos {job.company}.

Jag har bred erfarenhet från olika branscher - allt från restaurang och butik till äldreomsorg och tech. {first_exp}

Jag bor i Sollentuna, har B-körkort och är flexibel med arbetstider. Jag kan börja omgående.

Jag ser fram emot att höra från er.

Med vänlig hälsning,
Linnea Moritz
0761166109
linneamoritz1@gmail.com"""


class GmailDraftManager:
    """Hanterar Gmail-utkast via IMAP"""
    
    def __init__(self):
        self.email = "linneamoritzcv@gmail.com"
        self.app_password = os.environ.get('GMAIL_APP_PASSWORD', "xcwu agnn brcq unng")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        
        # CV-paths per kategori - nya professionella CVer
        base_path = os.path.dirname(__file__)
        self.cv_paths = {
            "restaurant": os.path.join(base_path, "CV_Linnea_Moritz_Restaurang_Cafe.pdf"),
            "retail": os.path.join(base_path, "CV_Linnea_Moritz_Butik_Kassa.pdf"),
            "industry": os.path.join(base_path, "CV_Linnea_Moritz_Industri_Tradgard.pdf"),
            "healthcare": os.path.join(base_path, "CV_Linnea_Moritz_Vard_Omsorg.pdf"),
            "tech": os.path.join(base_path, "CV_Linnea_Moritz_Tech_Kontor.pdf"),
            "art": os.path.join(base_path, "CV_Linnea_Moritz_Konst_Kultur.pdf"),
            "customerservice": os.path.join(base_path, "CV_Linnea_Moritz_Kundtjanst.pdf"),
            "reception": os.path.join(base_path, "CV_Linnea_Moritz_Kundtjanst.pdf"),
            "contentmoderation": os.path.join(base_path, "CV_Linnea_Moritz_Content_Moderation.pdf"),
            "moderation": os.path.join(base_path, "CV_Linnea_Moritz_Content_Moderation.pdf"),
            "general": os.path.join(base_path, "CV_Linnea_Moritz_Restaurang_Cafe.pdf"),
        }
        
        # CV-filnamn för bilagan (så du ser vilken typ)
        self.cv_filenames = {
            "restaurant": "CV_Linnea_Moritz_Restaurang_Cafe.pdf",
            "retail": "CV_Linnea_Moritz_Butik_Kassa.pdf",
            "industry": "CV_Linnea_Moritz_Industri_Tradgard.pdf",
            "healthcare": "CV_Linnea_Moritz_Vard_Omsorg.pdf",
            "tech": "CV_Linnea_Moritz_Tech_Kontor.pdf",
            "art": "CV_Linnea_Moritz_Konst_Kultur.pdf",
            "customerservice": "CV_Linnea_Moritz_Kundtjanst.pdf",
            "reception": "CV_Linnea_Moritz_Kundtjanst.pdf",
            "contentmoderation": "CV_Linnea_Moritz_Content_Moderation.pdf",
            "moderation": "CV_Linnea_Moritz_Content_Moderation.pdf",
            "general": "CV_Linnea_Moritz_Restaurang_Cafe.pdf",
        }
    
    def get_cv_path(self, category: str) -> str:
        """Hämta rätt CV baserat på jobbkategori"""
        return self.cv_paths.get(category, self.cv_paths["general"])
    
    def get_cv_filename(self, category: str) -> str:
        """Hämta rätt CV-filnamn baserat på jobbkategori"""
        return self.cv_filenames.get(category, self.cv_filenames["general"])
    
    def create_cover_letter_pdf(self, cover_letter: str, job_title: str, company: str) -> bytes:
        """Skapa snygg PDF av personligt brev enligt svensk standard"""
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Marginaler
        left_margin = 2.5 * cm
        right_margin = 2.5 * cm
        top_margin = 2.5 * cm
        y = height - top_margin
        
        # === AVSÄNDARE (högst upp till höger) ===
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - right_margin, y, "Linnea Moritz")
        y -= 16
        c.setFont("Helvetica", 10)
        c.drawRightString(width - right_margin, y, "Sollentuna")
        y -= 14
        c.drawRightString(width - right_margin, y, "0761166109")
        y -= 14
        c.drawRightString(width - right_margin, y, "linneamoritz1@gmail.com")
        y -= 30
        
        # === DATUM (vänster) ===
        c.setFont("Helvetica", 10)
        c.drawString(left_margin, y, datetime.now().strftime("%Y-%m-%d"))
        y -= 30
        
        # === MOTTAGARE (vänster) ===
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, company)
        y -= 40
        
        # === ÄMNESRAD ===
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, f"Ansökan: {job_title}")
        y -= 30
        
        # === BRÖDTEXT ===
        c.setFont("Helvetica", 11)
        max_width = width - left_margin - right_margin
        line_height = 16
        
        for paragraph in cover_letter.split('\n'):
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
                y -= 10  # Paragrafmellanrum
            
            if y < 3 * cm:
                c.showPage()
                y = height - top_margin
                c.setFont("Helvetica", 11)
        
        c.save()
        buffer.seek(0)
        return buffer.read()
    
    def create_draft(self, to_email: str, subject: str, email_body: str = None, cover_letter: str = None, job_url: str = None, job_title: str = None, company: str = None, category: str = "general") -> dict:
        """Skapa ett utkast i Gmail via IMAP med bilagor"""
        from email.mime.application import MIMEApplication
        
        logger.info(f"Creating draft - cover_letter present: {cover_letter is not None}, length: {len(cover_letter) if cover_letter else 0}")
        
        try:
            # Skapa email
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Använd genererad email_body (kort pitch)
            if email_body:
                msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            else:
                # Fallback
                fallback_body = f"""Hej!

Jag är intresserad av tjänsten och bifogar mitt CV och personligt brev.

Vänliga hälsningar,
Linnea Moritz
0761166109"""
                msg.attach(MIMEText(fallback_body, 'plain', 'utf-8'))
            
            # Bifoga personligt brev som PDF - ALLTID om cover_letter finns
            if cover_letter and len(cover_letter) > 10:
                try:
                    logger.info(f"Creating cover letter PDF for: {job_title} at {company}")
                    cover_letter_pdf = self.create_cover_letter_pdf(cover_letter, job_title or "Tjänsten", company or "Företaget")
                    logger.info(f"Cover letter PDF created, size: {len(cover_letter_pdf)} bytes")
                    cover_attachment = MIMEApplication(cover_letter_pdf, _subtype='pdf')
                    cover_attachment.add_header('Content-Disposition', 'attachment', filename='Personligt_Brev_Linnea_Moritz.pdf')
                    msg.attach(cover_attachment)
                    logger.info("✅ Cover letter PDF attached successfully")
                except Exception as e:
                    logger.error(f"❌ Could not create cover letter PDF: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f"⚠️ No cover letter provided or too short: {len(cover_letter) if cover_letter else 0} chars")
            
            # Bifoga rätt CV baserat på kategori - med rätt filnamn
            cv_path = self.get_cv_path(category)
            cv_filename = self.get_cv_filename(category)
            logger.info(f"Looking for CV at: {cv_path}")
            if os.path.exists(cv_path):
                with open(cv_path, 'rb') as f:
                    cv_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    cv_attachment.add_header('Content-Disposition', 'attachment', filename=cv_filename)
                    msg.attach(cv_attachment)
                    logger.info(f"✅ CV PDF attached: {cv_filename}")
            else:
                logger.warning(f"❌ CV not found at {cv_path}")
            
            # Anslut till IMAP och spara som utkast
            imap = imaplib.IMAP4_SSL(self.imap_server)
            imap.login(self.email, self.app_password)
            
            # Välj Drafts-mappen
            imap.select('[Gmail]/Drafts')
            
            # Spara meddelandet som utkast
            result = imap.append(
                '[Gmail]/Drafts',
                '',
                imaplib.Time2Internaldate(datetime.now().timestamp()),
                msg.as_bytes()
            )
            
            imap.logout()
            
            if result[0] == 'OK':
                logger.info(f"Draft created successfully for {to_email}")
                return {
                    "success": True,
                    "message": f"Utkast skapat till {to_email} med bilagor",
                    "to_email": to_email,
                    "subject": subject
                }
            else:
                return {"success": False, "error": "Failed to save draft"}
                
        except Exception as e:
            logger.error(f"Error creating Gmail draft: {e}")
            return {"success": False, "error": str(e)}
    
    def send_email(self, to_email: str, subject: str, body: str) -> dict:
        """Skicka email direkt (om du vill)"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.app_password)
            server.sendmail(self.email, to_email, msg.as_string())
            server.quit()
            
            return {"success": True, "message": f"Email skickat till {to_email}"}
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}


class AntiApathyJobPortal:
    """Huvudorkestrator för hela systemet"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = JobScraper(self.db)
        self.contact_finder = AIContactFinder()
        self.letter_generator = CoverLetterGenerator()
        self.gmail = GmailDraftManager()
        logger.info("Anti-Apathy Job Portal initialized")
    
    def run_scraping(self) -> int:
        """Kör full scraping"""
        return self.scraper.scrape_all()
    
    def enrich_job(self, job: Job) -> Job:
        """Berika jobb med kontaktinfo och why_perfect"""
        # Hitta kontaktinfo
        contact = self.contact_finder.find_contact(job.company, job.title)
        if contact:
            job.contact_email = contact.get("contact_email")
            job.contact_name = contact.get("contact_name")
        
        # Generera why_perfect
        if not job.why_perfect:
            job.why_perfect = self.letter_generator.generate_why_perfect(job)
        
        # Spara uppdaterat jobb
        self.db.save_job(job)
        return job
    
    def get_next_job(self) -> Optional[Dict]:
        """Hämta nästa jobb att visa"""
        job = self.db.get_next_job()
        if job:
            # Berika om det saknas info
            if not job.why_perfect:
                job = self.enrich_job(job)
            return job.to_dict()
        return None
    
    def generate_letter(self, job_id: str) -> Optional[str]:
        """Generera personligt brev för ett jobb"""
        job = self.db.get_job_by_id(job_id)
        if job:
            return self.letter_generator.generate_cover_letter(job)
        return None
    
    def save_application(self, job_id: str, cover_letter: str, gmail_draft_id: str = None) -> int:
        """Spara ansökan"""
        return self.db.save_application(
            job_id=job_id,
            status=ApplicationStatus.DRAFT_SAVED.value if gmail_draft_id else ApplicationStatus.LETTER_GENERATED.value,
            cover_letter=cover_letter,
            gmail_draft_id=gmail_draft_id
        )
    
    def create_gmail_draft(self, job_id: str, cover_letter: str = None, to_email: str = None) -> dict:
        """Skapa Gmail-utkast för en ansökan med kort mail + bilagor"""
        job = self.db.get_job_by_id(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        # Använd jobbets kontakt-email eller den som skickades in
        recipient = to_email or job.contact_email
        if not recipient:
            return {"success": False, "error": "No email address provided", "needs_email": True}
        
        # Detektera jobbkategori
        category = self.letter_generator.detect_job_category(job)
        
        # Generera kort mail-pitch med Platsbanken-länk
        job_url = job.url if job.url else f"https://arbetsformedlingen.se/platsbanken/annonser/{job.id}"
        email_body = self.letter_generator.generate_email_body(job, job_url)
        
        # Generera längre personligt brev (för PDF-bilaga) - utan länk
        personal_letter = cover_letter or self.letter_generator.generate_cover_letter(job)
        
        # Skapa ämnesrad
        subject = f"Ansökan: {job.title} - Linnea Moritz"
        
        # Skapa utkast med bilagor (rätt CV baserat på kategori)
        result = self.gmail.create_draft(
            to_email=recipient,
            subject=subject,
            email_body=email_body,
            cover_letter=personal_letter,
            job_url=job_url,
            job_title=job.title,
            company=job.company,
            category=category
        )
        
        if result.get("success"):
            # Spara ansökan med draft-status
            self.save_application(job_id, personal_letter, "gmail_draft")
        
        return result
    
    def skip_job(self, job_id: str):
        """Hoppa över ett jobb (markera som skipped)"""
        self.db.save_application(job_id, "skipped")
    
    def get_stats(self) -> Dict:
        """Hämta statistik"""
        return self.db.get_stats()


# CLI för testing
if __name__ == "__main__":
    portal = AntiApathyJobPortal()
    
    print("🎯 Anti-Apathy Job Portal")
    print("=" * 40)
    
    # Kör scraping
    print("\n📡 Scraping jobs...")
    count = portal.run_scraping()
    print(f"✅ Scraped {count} jobs")
    
    # Visa stats
    stats = portal.get_stats()
    print(f"\n📊 Stats:")
    print(f"   Total jobs: {stats['total_jobs']}")
    print(f"   Pending: {stats['pending_jobs']}")
    print(f"   Applications: {stats['total_applications']}")
    
    # Visa nästa jobb
    print("\n🎯 Next job:")
    next_job = portal.get_next_job()
    if next_job:
        print(f"   {next_job['title']} @ {next_job['company']}")
        print(f"   {next_job['location']}")
        print(f"   Priority: {next_job['priority']}")
        if next_job.get('why_perfect'):
            print(f"   Why: {next_job['why_perfect']}")
    else:
        print("   No jobs available")
