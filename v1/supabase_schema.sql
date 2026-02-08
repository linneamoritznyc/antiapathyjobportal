-- Anti-Apathy Job Portal - Supabase Schema
-- Run this in your Supabase SQL Editor to set up the database

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    url TEXT,
    source TEXT DEFAULT 'platsbanken',
    priority TEXT DEFAULT 'strategisk',
    deadline TEXT,
    contact_email TEXT,
    contact_name TEXT,
    why_perfect TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    link_status TEXT DEFAULT 'active'
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'new',
    cover_letter TEXT,
    gmail_draft_id TEXT,
    sent_at TIMESTAMPTZ,
    follow_up_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority);
CREATE INDEX IF NOT EXISTS idx_jobs_deadline ON jobs(deadline);
CREATE INDEX IF NOT EXISTS idx_jobs_link_status ON jobs(link_status);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Enable Row Level Security (optional - for multi-user later)
-- ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Upsert function for jobs (handles duplicates)
CREATE OR REPLACE FUNCTION upsert_job(job_data JSONB)
RETURNS VOID AS $$
BEGIN
    INSERT INTO jobs (id, title, company, location, description, url, source, priority, deadline, contact_email, contact_name, why_perfect, link_status)
    VALUES (
        job_data->>'id',
        job_data->>'title',
        job_data->>'company',
        job_data->>'location',
        job_data->>'description',
        job_data->>'url',
        COALESCE(job_data->>'source', 'platsbanken'),
        COALESCE(job_data->>'priority', 'strategisk'),
        job_data->>'deadline',
        job_data->>'contact_email',
        job_data->>'contact_name',
        job_data->>'why_perfect',
        COALESCE(job_data->>'link_status', 'active')
    )
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        company = EXCLUDED.company,
        location = EXCLUDED.location,
        description = EXCLUDED.description,
        url = EXCLUDED.url,
        deadline = EXCLUDED.deadline,
        contact_email = COALESCE(EXCLUDED.contact_email, jobs.contact_email),
        contact_name = COALESCE(EXCLUDED.contact_name, jobs.contact_name),
        why_perfect = COALESCE(EXCLUDED.why_perfect, jobs.why_perfect);
END;
$$ LANGUAGE plpgsql;
