"""
Anti-Apathy Job Portal - FastAPI Server
REST API för React frontend
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import logging

from job_portal_backend import AntiApathyJobPortal, ApplicationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Anti-Apathy Job Portal API",
    description="AI-driven jobbsökningsportal för neurodivergenta profiler",
    version="1.0.0"
)

# CORS - tillåt React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


class SkipRequest(BaseModel):
    reason: Optional[str] = None


class GenerateLetterResponse(BaseModel):
    cover_letter: str
    job_id: str


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "anti-apathy-portal"}


@app.get("/")
async def root():
    return {
        "message": "🎯 Anti-Apathy Job Portal API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/jobs/next": "Hämta nästa jobb",
            "GET /api/jobs": "Lista alla jobb",
            "POST /api/jobs/{id}/generate-letter": "Generera personligt brev",
            "POST /api/jobs/{id}/apply": "Spara ansökan",
            "POST /api/jobs/{id}/skip": "Hoppa över jobb",
            "POST /api/scrape": "Starta scraping",
            "GET /api/stats": "Hämta statistik"
        }
    }


# === JOB ENDPOINTS ===

@app.get("/api/jobs/next")
async def get_next_job():
    """Hämta nästa jobb att visa"""
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
async def get_all_jobs(limit: int = 50):
    """Lista alla jobb"""
    p = get_portal()
    jobs = p.db.get_all_jobs(limit=limit)
    
    return {
        "success": True,
        "count": len(jobs),
        "jobs": [j.to_dict() for j in jobs]
    }


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Hämta specifikt jobb"""
    p = get_portal()
    job = p.db.get_job_by_id(job_id)
    
    if job:
        return {"success": True, "job": job.to_dict()}
    
    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs/{job_id}/generate-letter")
async def generate_letter(job_id: str):
    """Generera personligt brev för ett jobb"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    letter = p.generate_letter(job_id)
    
    if letter:
        return {
            "success": True,
            "job_id": job_id,
            "cover_letter": letter,
            "company": job.company,
            "title": job.title
        }
    
    raise HTTPException(status_code=500, detail="Failed to generate letter")


@app.post("/api/jobs/{job_id}/apply")
async def apply_to_job(job_id: str, request: ApplyRequest):
    """Spara ansökan (som Gmail-utkast eller bara i databasen)"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    app_id = p.save_application(
        job_id=job_id,
        cover_letter=request.cover_letter,
        gmail_draft_id=request.gmail_draft_id
    )
    
    return {
        "success": True,
        "application_id": app_id,
        "status": "draft_saved" if request.gmail_draft_id else "letter_generated",
        "message": "Ansökan sparad!" + (" Utkast finns i Gmail." if request.gmail_draft_id else "")
    }


@app.post("/api/jobs/{job_id}/skip")
async def skip_job(job_id: str, request: SkipRequest = None):
    """Hoppa över ett jobb"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    p.skip_job(job_id)
    
    return {
        "success": True,
        "message": "Jobb överhoppat",
        "reason": request.reason if request else None
    }


@app.post("/api/jobs/{job_id}/create-draft")
async def create_gmail_draft(job_id: str, request: CreateDraftRequest):
    """Skapa Gmail-utkast för ansökan"""
    p = get_portal()
    
    job = p.db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result = p.create_gmail_draft(
        job_id=job_id,
        cover_letter=request.cover_letter,
        to_email=request.to_email
    )
    
    if result.get("needs_email"):
        return {
            "success": False,
            "needs_email": True,
            "message": "Ange email-adress för mottagaren"
        }
    
    return result


@app.get("/api/jobs/{job_id}/contact")
async def get_job_contact(job_id: str):
    """Hämta kontaktinfo för ett jobb"""
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
async def start_scraping(background_tasks: BackgroundTasks):
    """Starta scraping i bakgrunden"""
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
async def scrape_sync():
    """Kör scraping synkront (väntar på resultat)"""
    p = get_portal()
    count = p.run_scraping()
    
    return {
        "success": True,
        "jobs_scraped": count,
        "message": f"Scraping klar! {count} jobb hittade."
    }


@app.post("/api/enrich-contacts")
async def enrich_contacts(background_tasks: BackgroundTasks, limit: int = 10):
    """Berika jobb med kontaktinfo via AI"""
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
async def get_stats():
    """Hämta statistik för dashboard"""
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
async def get_applications():
    """Lista alla ansökningar"""
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
    uvicorn.run(app, host="0.0.0.0", port=port)
