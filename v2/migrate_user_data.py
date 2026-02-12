"""
Migrera Linneas data till Supabase
Kör med: python migrate_user_data.py
"""
import os
import httpx
import asyncio
from datetime import datetime

# Din user ID från Supabase
USER_ID = "da8ed517-3b67-4456-8831-6ed3cb7114ad"

# Supabase credentials (hämtas från miljövariabler)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Sätt SUPABASE_URL och SUPABASE_SERVICE_ROLE_KEY miljövariabler")
    print("export SUPABASE_URL=https://xxx.supabase.co")
    print("export SUPABASE_SERVICE_ROLE_KEY=xxx")
    exit(1)

# ============== LINNEAS DATA ==============

PROFILE_DATA = {
    "user_id": USER_ID,
    "full_name": "Linnea Moritz",
    "email": "linneamoritz1@gmail.com",
    "phone": "0761166109",
    "location": "Sollentuna",
    "photo_url": "https://lh3.googleusercontent.com/a/ACg8ocIjDB6ePOo0bQ5kWIBrfH0RMlePz1nNI9sY0b-goCZ9zZ5VuRZ7=s96-c",
    "drivers_license": True,
    "languages": ["Svenska (Modersmål)", "Engelska (Flytande)"],
    "updated_at": datetime.now().isoformat()
}

JOB_PREFERENCES = {
    "user_id": USER_ID,
    "job_titles": "servitör, kundtjänst, content moderator, butik, café",
    "locations": "Stockholm, Sollentuna, Sundbyberg",
    "job_types": ["full_time", "part_time"],
    "experience_level": "mid",
    "updated_at": datetime.now().isoformat()
}

EXPERIENCES = [
    {
        "user_id": USER_ID,
        "company": "House of Beans",
        "title": "Barista/Försäljare",
        "location": "Stockholm",
        "start_date": "2024-08",
        "end_date": "2025-02",
        "description": "Kaffe, te, försäljning, ensam i butik, kundkontakt",
        "categories": ["restaurant", "retail"]
    },
    {
        "user_id": USER_ID,
        "company": "Max Hamburgare",
        "title": "Restaurangbiträde",
        "location": "Stockholm",
        "start_date": "2024-04",
        "end_date": "2024-08",
        "description": "Drive-in, kök, servering, kassa, teamwork",
        "categories": ["restaurant"]
    },
    {
        "user_id": USER_ID,
        "company": "Clubhouse",
        "title": "Innehållsmoderator - Trust & Safety",
        "location": "Remote",
        "start_date": "2021-06",
        "end_date": "2022-01",
        "description": "Trust & Safety, innehållsgranskning, community support, policy enforcement",
        "categories": ["tech", "customerservice", "content"]
    },
    {
        "user_id": USER_ID,
        "company": "Minerva Project",
        "title": "Global Marketing Coordinator",
        "location": "San Francisco / Remote",
        "start_date": "2019-09",
        "end_date": "2020-04",
        "description": "Kundservice via Intercom, marknadsföring, internationell kommunikation",
        "categories": ["customerservice", "office"]
    },
    {
        "user_id": USER_ID,
        "company": "Google Ads (via Cognizant)",
        "title": "Innehållsanalytiker",
        "location": "Dublin",
        "start_date": "2018-05",
        "end_date": "2019-04",
        "description": "100+ annonser/dag, policy compliance, kvalitetsgranskning, dataanalys",
        "categories": ["tech", "content"]
    },
    {
        "user_id": USER_ID,
        "company": "Coffeehouse by George",
        "title": "Cafépersonal",
        "location": "Stockholm",
        "start_date": "2014",
        "end_date": "2015",
        "description": "Kassahantering, barista, kundservice",
        "categories": ["restaurant"]
    },
    {
        "user_id": USER_ID,
        "company": "ICA Maxi",
        "title": "Kassapersonal",
        "location": "Stockholm",
        "start_date": "2015",
        "end_date": "2019",
        "description": "Kassa, självscanning, frukt/grönt (sommarjobb 2015, 2017, 2019)",
        "categories": ["retail"]
    }
]

EDUCATION = [
    {
        "user_id": USER_ID,
        "school": "Minerva University",
        "degree": "Bachelor's Degree",
        "field_of_study": "Business, Arts & Humanities",
        "location": "San Francisco / Global",
        "start_date": "2016",
        "end_date": "2020"
    }
]

SKILLS = [
    # Allmänna
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Kundservice"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Kommunikation"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Teamwork"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Stresshantering"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Svenska (Modersmål)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Engelska (Flytande)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "certificate", "skill_text": "B-körkort"},

    # Restaurang
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Kassasystem"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Barista"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Servering"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "certificate", "skill_text": "Livsmedelshygien"},

    # Tech/Content
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Content Moderation"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Trust & Safety"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Policy Compliance"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Data Analysis"},

    # Kundtjänst
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "technical", "skill_text": "Intercom"},
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "technical", "skill_text": "Zendesk"},
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "soft", "skill_text": "Problemlösning"},
]

# CV-versioner för olika branscher
CV_VERSIONS = [
    {
        "user_id": USER_ID,
        "vibe_id": "restaurant",
        "vibe_name": "Restaurang & Café",
        "vibe_emoji": "🍽️",
        "cv_text": """LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Serviceinriktad och stresstålig person med bred erfarenhet från restaurang och café. Trivs i högt tempo och är van vid att ge gäster en bra upplevelse. B-körkort och flexibel med arbetstider.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Ansvarade för kaffe- och teservering
• Arbetade ofta ensam i butik med fullt ansvar
• Byggde upp kundrelationer och merförsäljning

Restaurangbiträde - Max Hamburgare (Apr - Aug 2024)
• Drive-in, kök och kassahantering
• Effektiv i stressiga miljöer
• Teamwork och snabb inlärning av nya system

Cafépersonal - Coffeehouse by George (2014-2015)
• Kassahantering och barista
• Hög servicenivå i centralt läge

UTBILDNING
Minerva University - Bachelor's Degree (2016-2020)

SPRÅK & ÖVRIGT
Svenska (modersmål), Engelska (flytande)
B-körkort, Livsmedelshygien
"""
    },
    {
        "user_id": USER_ID,
        "vibe_id": "customerservice",
        "vibe_name": "Kundtjänst & Support",
        "vibe_emoji": "💬",
        "cv_text": """LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Kommunikativ och lösningsorienterad med internationell erfarenhet inom kundservice och support. Van vid att hantera ärenden via telefon, mail och chat. Flytande svenska och engelska.

ERFARENHET
Innehållsmoderator, Trust & Safety - Clubhouse (Jun 2021 - Jan 2022)
• Hanterade användarrapporter och support-ärenden
• Tillämpade community guidelines och policy
• Arbetade i ett globalt, remote team

Global Marketing Coordinator - Minerva Project (Sep 2019 - Apr 2020)
• Kundservice via Intercom
• Internationell kommunikation med studenter och partners
• Marknadsföring och eventkoordinering

Innehållsanalytiker - Google Ads (Maj 2018 - Apr 2019)
• Granskade 100+ annonser dagligen
• Policy compliance och kvalitetssäkring
• Datadriven analys och rapportering

UTBILDNING
Minerva University - Bachelor's Degree, Business & Humanities (2016-2020)

FÄRDIGHETER
Intercom, Zendesk, CRM-system
Problemlösning, Multitasking
Svenska (modersmål), Engelska (flytande)
"""
    },
    {
        "user_id": USER_ID,
        "vibe_id": "content",
        "vibe_name": "Content & Moderation",
        "vibe_emoji": "📱",
        "cv_text": """LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Erfaren innehållsgranskare med bakgrund inom Trust & Safety och policy compliance. Analytisk, noggrann och van vid att fatta snabba beslut baserat på riktlinjer. Erfarenhet från tech-bolag som Google och Clubhouse.

ERFARENHET
Innehållsmoderator, Trust & Safety - Clubhouse (Jun 2021 - Jan 2022)
• Trust & Safety för social audio-plattform
• Granskade rapporterat innehåll enligt community guidelines
• Eskalerade komplexa ärenden till senior team
• Remote-arbete i globalt team

Innehållsanalytiker - Google Ads (Maj 2018 - Apr 2019)
• Granskade 100+ annonser dagligen för policy compliance
• Identifierade vilseledande och skadligt innehåll
• Hög accuracy och effektivitet under press
• Bidrog till förbättring av granskningsprocesser

UTBILDNING
Minerva University - Bachelor's Degree (2016-2020)
Tvärvetenskaplig utbildning i 7 länder

FÄRDIGHETER
Content Moderation, Trust & Safety
Policy Compliance, Riktlinjetolkning
Dataanalys, Kvalitetssäkring
Svenska (modersmål), Engelska (flytande)
"""
    },
    {
        "user_id": USER_ID,
        "vibe_id": "retail",
        "vibe_name": "Butik & Kassa",
        "vibe_emoji": "🛒",
        "cv_text": """LINNEA MORITZ
Sollentuna | 0761166109 | linneamoritz1@gmail.com

PROFIL
Serviceinriktad med erfarenhet från både butik och café. Van vid kassahantering, kundkontakt och att arbeta självständigt. Pålitlig och flexibel med arbetstider.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Försäljning av kaffe, te och tillbehör
• Arbetade ofta ensam med fullt butiksansvar
• Kassahantering och lagerhantering
• Byggde kundrelationer och merförsäljning

Kassapersonal - ICA Maxi (Somrar 2015, 2017, 2019)
• Kassahantering och självscanning
• Frukt- och gröntavdelningen
• Kundservice i högt tempo

Cafépersonal - Coffeehouse by George (2014-2015)
• Kassa och kundservice
• Barista i centralt läge

UTBILDNING
Minerva University - Bachelor's Degree (2016-2020)

FÄRDIGHETER
Kassasystem, Kortterminaler
Lagerhantering, Varupåfyllning
Kundservice, Merförsäljning
Svenska (modersmål), Engelska (flytande)
B-körkort
"""
    }
]


async def db_request(method: str, table: str, data: dict = None, params: dict = None):
    """Make request to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    async with httpx.AsyncClient() as client:
        if method == "POST":
            response = await client.post(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers, params=params, timeout=10)
        else:
            return None

        if response.status_code >= 400:
            print(f"  ⚠️  {table}: {response.status_code} - {response.text[:100]}")
            return None

        return response.json() if response.text else []


async def migrate():
    print(f"\n🚀 Migrerar data för användare: {USER_ID}")
    print(f"   Email: linneamoritz1@gmail.com")
    print(f"   Supabase: {SUPABASE_URL}\n")

    # 1. Profil
    print("1️⃣  Sparar profil...")
    result = await db_request("POST", "user_profiles", PROFILE_DATA)
    if result:
        print("   ✓ Profil sparad")

    # 2. Jobbpreferenser
    print("2️⃣  Sparar jobbpreferenser...")
    result = await db_request("POST", "user_job_preferences", JOB_PREFERENCES)
    if result:
        print("   ✓ Preferenser sparade")

    # 3. Erfarenheter
    print("3️⃣  Sparar arbetslivserfarenhet...")
    for i, exp in enumerate(EXPERIENCES):
        result = await db_request("POST", "user_experiences", exp)
        if result:
            print(f"   ✓ {exp['company']} - {exp['title']}")

    # 4. Utbildning
    print("4️⃣  Sparar utbildning...")
    for edu in EDUCATION:
        result = await db_request("POST", "user_education", edu)
        if result:
            print(f"   ✓ {edu['school']}")

    # 5. Färdigheter
    print("5️⃣  Sparar färdigheter...")
    for skill in SKILLS:
        result = await db_request("POST", "user_skills", skill)
    print(f"   ✓ {len(SKILLS)} färdigheter sparade")

    # 6. CV-versioner
    print("6️⃣  Sparar CV-versioner...")
    for cv in CV_VERSIONS:
        cv["created_at"] = datetime.now().isoformat()
        result = await db_request("POST", "user_cvs", cv)
        if result:
            print(f"   ✓ {cv['vibe_emoji']} {cv['vibe_name']}")

    print("\n✅ Migration klar!")
    print(f"   Profil: ✓")
    print(f"   Preferenser: ✓")
    print(f"   Erfarenheter: {len(EXPERIENCES)} st")
    print(f"   Utbildning: {len(EDUCATION)} st")
    print(f"   Färdigheter: {len(SKILLS)} st")
    print(f"   CV-versioner: {len(CV_VERSIONS)} st")


if __name__ == "__main__":
    asyncio.run(migrate())
