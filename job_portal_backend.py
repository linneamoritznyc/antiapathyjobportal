import sqlite3
import json
import os
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import imaplib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApplicationStatus(Enum):
    NEW = "new"
    DRAFT_SAVED = "draft_saved"
    SENT = "sent"

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
    def to_dict(self): return asdict(self)

class DatabaseManager:
    def __init__(self, db_path: str = "data/jobs.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, 
                     description TEXT, url TEXT, source TEXT, priority TEXT, deadline TEXT, contact_email TEXT, 
                     contact_name TEXT, why_perfect TEXT, created_at TEXT, link_status TEXT DEFAULT "active")''')
        c.execute('''CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT, 
                     status TEXT, cover_letter TEXT, gmail_draft_id TEXT, created_at TEXT, updated_at TEXT)''')
        conn.commit()
        conn.close()

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM jobs WHERE link_status = "active"'); total = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM applications WHERE status != "skipped"'); apps = c.fetchone()[0]
        conn.close()
        return {
            "total_jobs": total,
            "total_applications": apps,
            "sent_applications": apps,
            "interviews": 0,
            "pending_jobs": max(0, total - apps),
            "deadline_today": 0
        }

    def get_job_by_id(self, job_id: str):
        conn = sqlite3.connect(self.db_path)
        row = conn.cursor().execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        conn.close()
        return Job(*row) if row else None

    def get_next_job(self):
        conn = sqlite3.connect(self.db_path)
        row = conn.cursor().execute('SELECT j.* FROM jobs j LEFT JOIN applications a ON j.id = a.job_id WHERE a.id IS NULL LIMIT 1').fetchone()
        conn.close()
        return Job(*row) if row else None

class AntiApathyJobPortal:
    def __init__(self):
        self.db = DatabaseManager()

    def get_stats(self): return self.db.get_stats()
    def get_next_job(self):
        job = self.db.get_next_job()
        return job.to_dict() if job else None
    def run_scraping(self): return 0
    def skip_job(self, job_id): pass
    def generate_letter(self, job_id): return "Brev genereras..."
    def create_gmail_draft(self, job_id, cover_letter, to_email=None): return {"success": True}

