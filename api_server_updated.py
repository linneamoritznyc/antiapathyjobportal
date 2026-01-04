"""
Anti-Apathy Job Portal - FastAPI Server
REST API för React frontend with Supabase Auth
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import logging
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from job_portal_backend import AntiApathyJobPortal, ApplicationStatus
from config import get_settings
from auth import get_current_user
from rate_limit import limiter, setup_rate_limiting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

app = FastAPI(
    title="Anti-Apathy Job Portal API",
    description="AI-driven jobbsökningsportal för neurodivergenta profiler",
    version="1.0.0"
)

# Rate limiting disabled for local development
# setup_rate_limiting(app)

# CORS - restricted to localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # ["http://localhost:8000", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Global portal instance
portal = None


# Serve frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend.html")


def get_portal():
    global portal
    if portal is None:
        portal = AntiApathyJobPortal()
    return portal


# Pydantic models
class ApplyRequest(BaseModel):
    cover_letter: str
    gmail_draft_id: Optional[str] = None


class CreateDraftRequest(BaseModel):
    cover_letter: str
    to_email: Optional[str] = None


class GmailDraftRequest(BaseModel):
    subject: str
    body: str
    to_email: str


class SkipRequest(BaseModel):
    reason: Optional[str] = None


class GenerateLetterResponse(BaseModel):
    cover_letter: str
    job_id: str


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "anti-apathy-portal"}


# === GMAIL DRAFT ENDPOINT (NEW) ===

@app.post("/api/gmail/draft")
@limiter.limit("10/minute")
async def create_gmail_draft_direct(
    request: Request,
    draft: GmailDraftRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Skapar ett Gmail-utkast direkt med IMAP
    Detta är en DIREKT endpoint som inte kräver job_id
    PROTECTED: Requires authentication
    """
    try:
        # Get credentials from settings (loaded from .env)
        gmail_user = settings.gmail_user
        app_password = settings.gmail_app_password

        if not app_password or not gmail_user:
            raise HTTPException(
                status_code=500,
                detail="Gmail credentials not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD in .env"
            )
        
        # Skapa email-meddelandet
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = draft.to_email
        msg['Subject'] = draft.subject
        
        # Lägg till body
        msg.attach(MIMEText(draft.body, 'plain', 'utf-8'))
        
        # Konvertera till string
        message_string = msg.as_string()
        
        # Anslut till Gmail via IMAP
        logger.info(f"Connecting to Gmail IMAP for {gmail_user}...")
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(gmail_user, app_password)
        
        # Välj Drafts-mappen
        imap.select('[Gmail]/Drafts')
        
        # Lägg till meddelandet som utkast
        imap.append(
            '[Gmail]/Drafts',
            '',
            imaplib.Time2Internaldate(None),
            message_string.encode('utf-8')
        )
        
        logger.info(f"Draft created successfully for job application to {draft.to_email}")
        
        # Stäng anslutningen
        imap.logout()
        
        return {
            "success": True,
            "message": "Gmail-utkast skapat!",
            "drafts_url": "https://mail.google.com/mail/u/0/#drafts"
        }
        
    except imaplib.IMAP4.error as e:
        logger.error(f"Gmail authentication failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Gmail-autentisering misslyckades: {str(e)}. Kontrollera att GMAIL_APP_PASSWORD är korrekt."
        )
    except Exception as e:
        logger.error(f"Failed to create Gmail draft: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Kunde inte skapa Gmail-utkast: {str(e)}"
        )


# === JOB ENDPOINTS ===

@app.get("/api/jobs/next")
async def get_next_job(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Hämta nästa jobb att visa - PROTECTED"""
    p = get_portal()
    job = p.get_next_job()
    
    if job:
        return {
            "success": True,
            "job": job
        }
    
    return {
        "success": True,
        "job": None,
        "message": "Inga fler jobb just nu. Kör scraping för att hämta nya!"
    }


@app.get("/api/jobs")
@limiter.limit("30/minute")
async def get_all_jobs(
    request: Request,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Lista alla jobb - PROTECTED"""
    p = get_portal()
    jobs = p.db.get_all_jobs(limit=limit)
    
    return {
        "success": True,
        "count": len(jobs),
        "jobs": [j.to_dict() for j in jobs]
    }


@app.get("/api/jobs/{job_id}")
@limiter.limit("60/minute")
async def get_job(
    request: Request,
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Hämta specifikt jobb - PROTECTED"""
    p = get_portal()
    job = p.db.get_job_by_id(job_id)
    
    if job:
        return {"success": True, "job": job.to_dict()}
    
    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs/{job_id}/generate-letter")
async def generate_letter(
    request: Request,
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generera personligt brev för ett jobb - PROTECTED"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    logger.info(f"Generating letter for job {job_id} ({job.title} at {job.company})")
    
    try:
        letter = p.generate_letter(job_id)
        
        if letter:
            logger.info(f"Successfully generated letter for job {job_id}")
            return {
                "success": True,
                "job_id": job_id,
                "cover_letter": letter,
                "company": job.company,
                "title": job.title
            }
        
        logger.error(f"Letter generation returned None for job {job_id}")
        raise HTTPException(status_code=500, detail="Failed to generate letter")
    except Exception as e:
        logger.error(f"Error generating letter for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Letter generation error: {str(e)}")


@app.post("/api/jobs/{job_id}/apply")
async def apply_to_job(
    request: Request,
    job_id: str,
    apply_request: ApplyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Spara ansökan (som Gmail-utkast eller bara i databasen) - PROTECTED"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    app_id = p.save_application(
        job_id=job_id,
        cover_letter=apply_request.cover_letter,
        gmail_draft_id=apply_request.gmail_draft_id
    )

    return {
        "success": True,
        "application_id": app_id,
        "status": "draft_saved" if apply_request.gmail_draft_id else "letter_generated",
        "message": "Ansökan sparad!" + (" Utkast finns i Gmail." if apply_request.gmail_draft_id else "")
    }


@app.post("/api/jobs/{job_id}/skip")
async def skip_job(
    request: Request,
    job_id: str,
    skip_request: SkipRequest,
    current_user: dict = Depends(get_current_user)
):
    """Hoppa över ett jobb - PROTECTED"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    p.skip_job(job_id)
    
    return {
        "success": True,
        "message": "Jobb överhoppat",
        "reason": skip_request.reason if skip_request else None
    }


@app.post("/api/jobs/{job_id}/create-draft")
async def create_gmail_draft(
    request: Request,
    job_id: str,
    draft_request: CreateDraftRequest,
    current_user: dict = Depends(get_current_user)
):
    """Skapa Gmail-utkast för ansökan - PROTECTED"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result = p.create_gmail_draft(
        job_id=job_id,
        cover_letter=draft_request.cover_letter,
        to_email=draft_request.to_email
    )
    
    if result.get("needs_email"):
        return {
            "success": False,
            "needs_email": True,
            "message": "Ange email-adress för mottagaren"
        }
    
    return result


@app.get("/api/jobs/{job_id}/contact")
@limiter.limit("60/minute")
async def get_job_contact(
    request: Request,
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Hämta kontaktinfo för ett jobb - PROTECTED"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "success": True,
        "contact_email": job.contact_email,
        "contact_name": job.contact_name,
        "company": job.company
    }


# === SCRAPING ENDPOINTS ===

@app.post("/api/scrape")
@limiter.limit("5/hour")
async def start_scraping(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Starta scraping i bakgrunden - PROTECTED"""
    p = get_portal()
    
    def run_scrape():
        count = p.run_scraping()
        logger.info(f"Scraping completed: {count} jobs")
    
    background_tasks.add_task(run_scrape)
    
    return {
        "success": True,
        "message": "Scraping startad i bakgrunden",
        "status": "running"
    }


@app.post("/api/scrape/sync")
async def scrape_sync(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Kör scraping synkront (väntar på resultat) - PROTECTED"""
    p = get_portal()
    count = p.run_scraping()
    
    return {
        "success": True,
        "jobs_scraped": count,
        "message": f"Scraping klar! {count} jobb hittade."
    }


@app.post("/api/enrich-contacts")
@limiter.limit("5/hour")
async def enrich_contacts(
    request: Request,
    background_tasks: BackgroundTasks,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Berika jobb med kontaktinfo via AI - PROTECTED"""
    p = get_portal()
    
    def run_enrich():
        jobs = p.db.get_all_jobs(limit=limit)
        enriched = 0
        for job in jobs:
            if not job.contact_email:
                p.enrich_job(job)
                enriched += 1
        logger.info(f"Enriched {enriched} jobs with contact info")
    
    background_tasks.add_task(run_enrich)
    
    return {
        "success": True,
        "message": f"Berikar upp till {limit} jobb med kontaktinfo",
        "status": "running"
    }


# === STATS ENDPOINTS ===

@app.get("/api/stats")
async def get_stats(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Hämta statistik för dashboard - PROTECTED"""
    p = get_portal()
    stats = p.get_stats()
    
    return {
        "success": True,
        "stats": {
            "total_jobs": stats.get("total_jobs", 0),
            "pending_jobs": stats.get("pending_jobs", 0),
            "total_applications": stats.get("total_applications", 0),
            "sent_applications": stats.get("sent_applications", 0),
            "interviews": stats.get("interviews", 0),
            "deadline_today": stats.get("deadline_today", 0)
        }
    }


@app.get("/api/applications")
@limiter.limit("30/minute")
async def get_applications(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Lista alla ansökningar - PROTECTED"""
    p = get_portal()
    
    import sqlite3
    conn = sqlite3.connect(p.db.db_path)
    c = conn.cursor()
    c.execute('''
        SELECT a.*, j.title, j.company 
        FROM applications a 
        JOIN jobs j ON a.job_id = j.id 
        ORDER BY a.created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    
    applications = []
    for row in rows:
        applications.append({
            "id": row[0],
            "job_id": row[1],
            "status": row[2],
            "cover_letter": row[3][:200] + "..." if row[3] and len(row[3]) > 200 else row[3],
            "gmail_draft_id": row[4],
            "sent_at": row[5],
            "follow_up_at": row[6],
            "created_at": row[8],
            "job_title": row[10],
            "company": row[11]
        })
    
    return {
        "success": True,
        "count": len(applications),
        "applications": applications
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Anti-Apathy Job Portal API on port {port}")
    print(f"📧 Gmail Draft endpoint: POST /api/gmail/draft")
    print(f"⚠️  Remember to set GMAIL_APP_PASSWORD environment variable!")
    uvicorn.run(app, host="0.0.0.0", port=port)
