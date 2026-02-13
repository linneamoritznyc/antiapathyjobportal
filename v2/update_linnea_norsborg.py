"""
Uppdatera Linneas data efter flytt till Norsborg
+ Lägga till jobbsökningar för specifika företag

Kör med: python update_linnea_norsborg.py
"""
import os
import requests
from datetime import datetime, timedelta
import uuid

# Din user ID från Supabase
USER_ID = "da8ed517-3b67-4456-8831-6ed3cb7114ad"

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Sätt SUPABASE_URL och SUPABASE_SERVICE_ROLE_KEY miljövariabler")
    print("export SUPABASE_URL=https://xxx.supabase.co")
    print("export SUPABASE_SERVICE_ROLE_KEY=xxx")
    exit(1)

# ============== UPPDATERAD DATA ==============

# Ny adress efter flytt till Norsborg
NEW_LOCATION = "Norsborg"

# Uppdaterad profil
UPDATED_PROFILE = {
    "user_id": USER_ID,
    "full_name": "Linnea Moritz",
    "email": "linneamoritz1@gmail.com",
    "phone": "0761166109",
    "location": NEW_LOCATION,  # UPPDATERAD!
    "photo_url": "https://lh3.googleusercontent.com/a/ACg8ocIjDB6ePOo0bQ5kWIBrfH0RMlePz1nNI9sY0b-goCZ9zZ5VuRZ7=s96-c",
    "drivers_license": True,
    "languages": ["Svenska (Modersmål)", "Engelska (Flytande)"],
    "updated_at": datetime.now().isoformat()
}

# Uppdaterade jobbpreferenser med Norsborg
UPDATED_JOB_PREFERENCES = {
    "user_id": USER_ID,
    "job_titles": "servitör, kundtjänst, butik, vaktmästare, trädgård, städ, industri",
    "locations": "Norsborg, Botkyrka, Hallunda, Tumba, Stockholm",
    "preferred_locations": ["Norsborg", "Botkyrka", "Hallunda", "Tumba", "Stockholm", "Huddinge"],
    "search_keywords": ["vaktmästare", "trädgård", "butik", "industri", "städ", "lager"],
    "job_types": ["full_time", "part_time"],
    "experience_level": "mid",
    "updated_at": datetime.now().isoformat()
}

# Uppdaterade CV-versioner med Norsborg istället för Sollentuna
UPDATED_CV_VERSIONS = [
    {
        "user_id": USER_ID,
        "vibe_id": "restaurant",
        "vibe_name": "Restaurang & Café",
        "vibe_emoji": "🍽️",
        "cv_text": """LINNEA MORITZ
Norsborg | 0761166109 | linneamoritz1@gmail.com

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
Norsborg | 0761166109 | linneamoritz1@gmail.com

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
Norsborg | 0761166109 | linneamoritz1@gmail.com

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
Norsborg | 0761166109 | linneamoritz1@gmail.com

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
    },
    {
        "user_id": USER_ID,
        "vibe_id": "facility",
        "vibe_name": "Vaktmästare & Fastighetsskötsel",
        "vibe_emoji": "🔧",
        "cv_text": """LINNEA MORITZ
Norsborg | 0761166109 | linneamoritz1@gmail.com

PROFIL
Pålitlig och serviceinriktad person med körkort och erfarenhet av självständigt arbete. Praktiskt lagd och van vid varierande arbetsuppgifter. Trivs med att hålla ordning och se till att saker fungerar.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Ansvarade för hela butiken självständigt
• Öppning, stängning och daglig skötsel
• Lagerhantering och underhåll av utrustning
• Kontakt med leverantörer

Kassapersonal - ICA Maxi (Somrar 2015, 2017, 2019)
• Varierande arbetsuppgifter i stor butik
• Frukt- och gröntavdelning med varupåfyllning
• Kundservice och problemlösning

UTBILDNING
Minerva University - Bachelor's Degree (2016-2020)

FÄRDIGHETER & KVALIFIKATIONER
• B-körkort
• Självständigt arbete
• Praktiskt lagd
• Ordningsam och noggrann
• Svenska (modersmål), Engelska (flytande)
"""
    },
    {
        "user_id": USER_ID,
        "vibe_id": "outdoor",
        "vibe_name": "Trädgård & Utomhusarbete",
        "vibe_emoji": "🌿",
        "cv_text": """LINNEA MORITZ
Norsborg | 0761166109 | linneamoritz1@gmail.com

PROFIL
Energisk och praktiskt lagd person som trivs med utomhusarbete. Har körkort och är van vid fysiskt arbete och varierande väder. Självgående och pålitlig.

ERFARENHET
Barista/Försäljare - House of Beans (Aug 2024 - Feb 2025)
• Arbetade självständigt med fullt ansvar
• Daglig skötsel och underhåll
• Van vid tidiga morgnar och flexibla tider

Kassapersonal - ICA Maxi (Somrar 2015, 2017, 2019)
• Fysiskt arbete med varor och lager
• Frukt- och gröntavdelning
• Uthållighet i högt tempo

UTBILDNING
Minerva University - Bachelor's Degree (2016-2020)
Studerat i 7 olika länder - van vid att anpassa sig

FÄRDIGHETER & KVALIFIKATIONER
• B-körkort
• Fysiskt arbete
• Självständig och pålitlig
• Flexibel med arbetstider
• Svenska (modersmål), Engelska (flytande)
"""
    }
]

# Jobb att söka - specifika företag och positioner
# Dessa läggs in i jobs-tabellen så de kan visas i jobbportalen
TARGET_JOBS = [
    {
        "id": f"manual-oob-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Butikspersonal",
        "company": "ÖoB (Överskottsbolaget)",
        "location": "Norsborg / Botkyrka",
        "description": """Söker jobb hos ÖoB i Norsborg-området.

ÖoB är Sveriges ledande lågpriskedja med ett brett sortiment.
Arbetsuppgifter kan inkludera kassaarbete, varupåfyllning, kundservice.""",
        "url": "https://www.oob.se/jobb",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-rusta-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Butikspersonal",
        "company": "Rusta",
        "location": "Norsborg / Botkyrka",
        "description": """Söker jobb hos Rusta i Norsborg-området.

Rusta är en populär lågpriskedja med hem, trädgård och fritidsprodukter.
Arbetsuppgifter kan inkludera kassaarbete, varupåfyllning, kundservice och lagerpåfyllning.""",
        "url": "https://karriar.rusta.com/",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-systembolaget-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Butikssäljare",
        "company": "Systembolaget",
        "location": "Norsborg / Botkyrka / Tumba",
        "description": """Söker jobb hos Systembolaget i Norsborg-området.

Systembolaget söker ofta personal med god kundservice och kunskapstörst.
Arbetsuppgifter inkluderar kundservice, rådgivning, kassaarbete och varupåfyllning.""",
        "url": "https://karriar.systembolaget.se/",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-industri-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Industrijobb / Lagerarbetare",
        "company": "Industri Botkyrka",
        "location": "Norsborg / Botkyrka / Tumba",
        "description": """Söker industrijobb eller lagerarbete i Norsborg-området.

Många företag i industriområdena kring Botkyrka och Tumba.
Kan inkludera lagerarbete, produktion, plockning och packning.""",
        "url": "https://arbetsformedlingen.se/",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-skrap-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Skräpplockning / Städpersonal utomhus",
        "company": "Botkyrka kommun / Städentreprenör",
        "location": "Norsborg / Botkyrka",
        "description": """Söker jobb med skräpplockning och utomhusstädning i Norsborg.

Kommunen och privata entreprenörer anställer ofta säsongsarbetare för:
• Skräpplockning i parker och grönområden
• Gatustädning
• Allmän utomhusskötsel""",
        "url": "https://botkyrka.se/jobba-hos-oss",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-tradgard-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Trädgårdsarbetare",
        "company": "Botkyrka kommun / Trädgårdsentreprenör",
        "location": "Norsborg / Botkyrka",
        "description": """Söker trädgårdsjobb i Norsborg-området.

Arbetsuppgifter kan inkludera:
• Gräsklippning och häckklippning
• Plantering och skötsel
• Ogräsrensning
• Park- och grönyteskötsel""",
        "url": "https://botkyrka.se/jobba-hos-oss",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "priority": "normal",
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "id": f"manual-vaktmastare-kyrka-norsborg-{datetime.now().strftime('%Y%m%d')}",
        "title": "Vaktmästare",
        "company": "Svenska Kyrkan Norsborg",
        "location": "Norsborg",
        "description": """DRÖMJOBB: Vaktmästare hos Svenska Kyrkan i Norsborg!

Svenska Kyrkan söker ibland vaktmästare för:
• Skötsel av kyrkobyggnader och lokaler
• Trädgårds- och markskötsel
• Praktiska uppgifter vid evenemang
• Snöröjning och allmänt underhåll

Kontakt: Botkyrka-Salem församling
https://www.svenskakyrkan.se/botkyrka-salem""",
        "url": "https://www.svenskakyrkan.se/botkyrka-salem/lediga-jobb",
        "deadline": (datetime.now() + timedelta(days=60)).isoformat(),
        "priority": "urgent",  # Markera som högt prioriterat då det är drömjobbet!
        "source": "manual_search",
        "scraped_at": datetime.now().isoformat()
    }
]


def db_request(method: str, table: str, data: dict = None, params: dict = None):
    """Make request to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, params=params, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=10)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            return None

        if response.status_code >= 400:
            print(f"  Warning {table}: {response.status_code} - {response.text[:200]}")
            return None

        return response.json() if response.text else []
    except Exception as e:
        print(f"  Error {table}: {e}")
        return None


def update_data():
    print(f"\n{'='*60}")
    print("UPPDATERAR LINNEAS DATA EFTER FLYTT TILL NORSBORG")
    print(f"{'='*60}")
    print(f"\nAnvändare: {USER_ID}")
    print(f"Email: linneamoritz1@gmail.com")
    print(f"Ny adress: {NEW_LOCATION}")
    print(f"Supabase: {SUPABASE_URL}\n")

    # 1. Uppdatera profil med ny adress
    print("1. Uppdaterar profil med ny adress (Norsborg)...")
    result = db_request("POST", "user_profiles", UPDATED_PROFILE)
    if result:
        print(f"   ✓ Profil uppdaterad - Plats: {NEW_LOCATION}")
    else:
        print("   ⚠ Kunde inte uppdatera profil")

    # 2. Uppdatera jobbpreferenser
    print("\n2. Uppdaterar jobbpreferenser med Norsborg-området...")
    result = db_request("POST", "user_job_preferences", UPDATED_JOB_PREFERENCES)
    if result:
        print(f"   ✓ Preferenser uppdaterade")
        print(f"   Platser: {UPDATED_JOB_PREFERENCES['locations']}")
    else:
        print("   ⚠ Kunde inte uppdatera preferenser")

    # 3. Uppdatera CV-versioner med ny adress
    print("\n3. Uppdaterar CV-versioner med Norsborg...")
    for cv in UPDATED_CV_VERSIONS:
        cv["updated_at"] = datetime.now().isoformat()
        result = db_request("POST", "user_cvs", cv)
        if result:
            print(f"   ✓ {cv['vibe_emoji']} {cv['vibe_name']}")
        else:
            print(f"   ⚠ Kunde inte uppdatera {cv['vibe_name']}")

    # 4. Lägg till målföretag som jobb
    print("\n4. Lägger till jobb för målföretag...")
    for job in TARGET_JOBS:
        result = db_request("POST", "jobs", job)
        if result:
            priority_icon = "🌟" if job['priority'] == 'urgent' else "📋"
            print(f"   {priority_icon} {job['company']} - {job['title']}")
        else:
            print(f"   ⚠ Kunde inte lägga till {job['company']}")

    # 5. Skapa jobbansökningar (status: saved) för att spåra intresse
    print("\n5. Sparar jobb som intressanta (saved)...")
    for job in TARGET_JOBS:
        application = {
            "user_id": USER_ID,
            "job_id": job["id"],
            "status": "saved",
            "notes": f"Intresserad av {job['company']} - tillagd {datetime.now().strftime('%Y-%m-%d')}",
            "created_at": datetime.now().isoformat()
        }
        result = db_request("POST", "applications", application)
        if result:
            print(f"   ✓ Sparad: {job['company']}")

    # Sammanfattning
    print(f"\n{'='*60}")
    print("SAMMANFATTNING")
    print(f"{'='*60}")
    print(f"\n✓ Profil uppdaterad till: {NEW_LOCATION}")
    print(f"✓ Jobbpreferenser uppdaterade för Norsborg-området")
    print(f"✓ {len(UPDATED_CV_VERSIONS)} CV-versioner uppdaterade med ny adress")
    print(f"✓ {len(TARGET_JOBS)} jobb tillagda att söka:")
    for job in TARGET_JOBS:
        priority = "⭐ DRÖMJOBB" if job['priority'] == 'urgent' else ""
        print(f"   - {job['company']}: {job['title']} {priority}")

    print(f"\n🎯 Nästa steg:")
    print("   1. Gå in på jobbportalen och se dina sparade jobb")
    print("   2. Besök företagens karriärsidor direkt:")
    print("      - ÖoB: https://www.oob.se/jobb")
    print("      - Rusta: https://karriar.rusta.com/")
    print("      - Systembolaget: https://karriar.systembolaget.se/")
    print("      - Svenska Kyrkan: https://www.svenskakyrkan.se/botkyrka-salem/lediga-jobb")
    print("      - Botkyrka kommun: https://botkyrka.se/jobba-hos-oss")
    print("\nLycka till med jobbsökandet i Norsborg! 🏠✨")


if __name__ == "__main__":
    update_data()
