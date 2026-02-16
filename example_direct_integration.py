"""
Example: Direct Supabase + Claude Integration
No n8n needed! Just Python libraries.
"""

from supabase import create_client, Client
import anthropic
import os

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Initialize Claude client
claude = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Example: Fetch data from Supabase, process with Claude
def generate_cover_letter_with_db(job_id: str):
    # 1. Get job data from Supabase
    job = supabase.table("jobs").select("*").eq("id", job_id).single().execute()

    # 2. Get user CV from Supabase
    user_cv = supabase.table("user_profiles").select("cv_text").eq("user_id", "123").single().execute()

    # 3. Send to Claude
    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Write a cover letter for this job:\n{job.data}\n\nUsing this CV:\n{user_cv.data}"
        }]
    )

    cover_letter = message.content[0].text

    # 4. Save result back to Supabase
    supabase.table("applications").insert({
        "job_id": job_id,
        "cover_letter": cover_letter,
        "status": "draft"
    }).execute()

    return cover_letter

# That's it! No n8n needed.
