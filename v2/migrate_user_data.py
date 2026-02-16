"""
Migrera Linneas FULLSTANDIGA data till Supabase
Kor med: python migrate_user_data.py

Krav:
  export SUPABASE_URL=https://xxx.supabase.co
  export SUPABASE_SERVICE_ROLE_KEY=xxx
"""
import os
import sys
import requests
from datetime import datetime

# Din user ID fran Supabase
USER_ID = "da8ed517-3b67-4456-8831-6ed3cb7114ad"

# Supabase credentials (hamtas fran miljovariabler)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Satt SUPABASE_URL och SUPABASE_SERVICE_ROLE_KEY miljovariabler")
    print("export SUPABASE_URL=https://xxx.supabase.co")
    print("export SUPABASE_SERVICE_ROLE_KEY=xxx")
    sys.exit(1)

# ============== LINNEAS FULLSTANDIGA DATA ==============

PROFILE_DATA = {
    "user_id": USER_ID,
    "full_name": "Linnea Moritz",
    "email": "linneamoritz1@gmail.com",
    "phone": "0761166109",
    "location": "Sollentuna",
    "drivers_license": True,
    "languages": ["Svenska (Modersmal)", "Engelska (Flytande)", "Tyska (grundlaggande)", "Spanska (grundlaggande)", "Mandarin (HSK niva 3)"],
    "certificates": ["B-korkort (automat)", "ICA kassahantering", "Trygga mat", "Roda Korset forsta hjalpen"],
    "about_me": "Serviceinriktad och stresstalig med bred internationell erfarenhet. Minerva University (1.8% antagning). Jobbat i 7 lander. Flytande svenska och engelska.",
    "updated_at": datetime.now().isoformat()
}

JOB_PREFERENCES = {
    "user_id": USER_ID,
    "preferred_locations": ["Stockholm", "Sollentuna", "Sundbyberg", "Vetlanda"],
    "search_keywords": ["servitor", "kundtjanst", "content moderator", "butik", "cafe", "reception", "lager"],
    "excluded_keywords": [],
    "excluded_companies": [],
    "job_types": ["heltid", "deltid"],
    "remote_only": False,
    "updated_at": datetime.now().isoformat()
}

# ALL 19 EXPERIENCES fran Linneas 8 CV PDFs
EXPERIENCES = [
    {"user_id": USER_ID, "company": "Minerva University", "title": "Alumni Ambassador Western Europe", "location": "Stockholm", "dates": "Sep 2024 - Pagaende", "bullets": ["25% tjanst med sjalvstandig planering, cirka 40 timmar i manaden", "Genomfor strategisk marknadsforing genom resor till skolor och massor i Vasteuropa och Norden", "Bygger och underhaller databaser for skolkontakter, moten med SYO:er och studievagledare", "Ansvarar for logistik: bokning av flyg, hotell och transporter for stort geografiskt omrade"], "categories": ["office", "customerservice"], "sort_order": 1},
    {"user_id": USER_ID, "company": "House of Beans, Hotorgshallen", "title": "Forsaljare/Barista", "location": "Stockholm", "dates": "Aug 2024 - Feb 2025", "bullets": ["Sjalvstandigt butiksansvar med forsaljning av te, kaffe och choklad", "Direktforsaljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar", "Hanterade kassa, kundservice och lagerhantering"], "categories": ["restaurant", "retail"], "sort_order": 2},
    {"user_id": USER_ID, "company": "Profilgruppen", "title": "Anodiseringsoperator (Feriearbete)", "location": "Aseda", "dates": "Juli 2024 - Aug 2024", "bullets": ["Utforde tungt fysiskt arbete med fokus pa armlyft och materialhantering", "Arbetade pa tvaskift (06.00-14.00 och 14.00-23.00)", "Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor"], "categories": ["industry"], "sort_order": 3},
    {"user_id": USER_ID, "company": "Max Hamburgare", "title": "Restaurangbitrade", "location": "Vetlanda", "dates": "April 2024 - Aug 2024", "bullets": ["Arbetade i hogt tempo med drive-in, fritos, kok, servering, kassa och stad", "Levererade god kundservice och samarbetade effektivt med teamet under rusningstid"], "categories": ["restaurant"], "sort_order": 4},
    {"user_id": USER_ID, "company": "Keeping Tabs", "title": "Multimedia Technical Specialist", "location": "New York, USA", "dates": "Nov 2022 - Juni 2023", "bullets": ["Planerade och koordinerade konstsamling for Art Basel Hong Kong (70x30m skarm, Causeway Bay)", "Designade visuell merchandise och rullade ut forsaljnings- och logistikkampanj", "Utvecklade partnerskap med organisationer inom konstindustrin i USA", "Ansvarade for leadgenerering, orderleverans, fakturering och kundnojdhet"], "categories": ["art", "office"], "sort_order": 5},
    {"user_id": USER_ID, "company": "30 Campos Eliseos", "title": "Kubistisk malare", "location": "New York, USA", "dates": "2022 - 2024", "bullets": ["Scoutad som professionell kubistmalare till prestigefylld konstsamlargrupp grundad i Florens", "En av endast fem konstnarer utvalda bland 500+ sokande", "Deltog i utstallningar i New York, Dubai, Seoul, Madrid och Florens"], "categories": ["art"], "sort_order": 6},
    {"user_id": USER_ID, "company": "TikTok/ByteDance", "title": "Kvalitetsgranskare - Amerikanska marknaden", "location": "Nashville, USA", "dates": "Maj 2022 - Juni 2022", "bullets": ["Granskade innehallsmoderatorernas arbete for att sakerstalla att de foljer riktlinjer", "Kvalitetssakrade moderering och bidrog till forbattrade processer"], "categories": ["tech", "content"], "sort_order": 7},
    {"user_id": USER_ID, "company": "YouTube Ads (via Vaco)", "title": "Innehallsmoderator - Svenska marknaden", "location": "San Francisco, USA", "dates": "Feb 2022 - Juni 2022", "bullets": ["Flaggade olamplig reklam och bidrog till att utoka databaser med markerat innehall", "Foljde noggrant alla riktlinjer och samarbetade med det svenska teamet", "Deltog i regelbundna moten for att sakerstalla korrekt granskning av material"], "categories": ["tech", "content"], "sort_order": 8},
    {"user_id": USER_ID, "company": "Clubhouse (via Vaco)", "title": "Innehallsmoderator - Skandinaviska och amerikanska marknaden", "location": "Walnut Creek, USA", "dates": "Juni 2021 - Jan 2022", "bullets": ["Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media", "Kategorier inkluderade hatiskt tal, sexuell exploatering, valdsbejakande extremism, CSAM och falsk information", "Hade fullt ansvar for att hantera alla arenden inom svenska, norska och danska marknaden", "Identifierade brister i standardiserade arbetsrutiner och drev policyforbttringar", "Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes"], "categories": ["tech", "customerservice", "content"], "sort_order": 9},
    {"user_id": USER_ID, "company": "Svensk-amerikanska handelskammaren", "title": "Marknadsforing och forsaljningsutveckling", "location": "San Francisco, USA", "dates": "Juni 2021 - Sep 2021", "bullets": ["Byggde upp natverk med 100+ svenska startups, myndigheter och foretag genom konferenser och event", "Okade handelskammarens natverk med 20% genom effektiv e-post- och LinkedIn-marknadsforing", "Assisterade tva svenska konsultkunder med databas av 120 forsaljningsleads i USA", "Organiserade kraftskiva for 80 skandinaver och amerikaner i samarbete med Norska klubben"], "categories": ["office", "customerservice"], "sort_order": 10},
    {"user_id": USER_ID, "company": "Minerva University", "title": "Handledare for examensprojekt", "location": "San Francisco, USA", "dates": "Sep 2020 - Maj 2021", "bullets": ["Handledde 45 studenter i deras capstone-projekt inom VR, hallbart mode, varumarkesanalys och historiska romaner", "Ledde workshops, undervisade i projektledning och gav omfattande akademiskt stod", "Gav kvalitativ och kvantitativ aterkoppling till over 90 uppgifter och 40 lektioner"], "categories": ["office", "art"], "sort_order": 11},
    {"user_id": USER_ID, "company": "Kvarngarden aldreboende", "title": "Timvikarie", "location": "Vetlanda", "dates": "Maj 2020 - Sep 2020", "bullets": ["Omvardnad, medicinhantering, maltidsassistans, dokumentation och emotionellt stod", "Gav omsorg till aldre personer med demens och Alzheimers sjukdom", "Foljde noggrant covid-protokoll och arbetade bade morgon- och kvallspass"], "categories": ["healthcare"], "sort_order": 12},
    {"user_id": USER_ID, "company": "Minerva Project", "title": "Marknadsforing/Kundservice - Global Marketing Team", "location": "Berlin & Buenos Aires", "dates": "Sep 2019 - April 2020", "bullets": ["Samarbetade med globala marknadsforingsteamet for att oka antagningen till Minerva University", "Vagledde och stottade over 2000 sokande elever via Intercom med hogkvalitativ kundservice", "Svarade pa fragor fran elever i over 40 lander genom Intercom och personliga moten", "Anordnade rekryteringsevenemang i Norge med presentation om utbildningsprogrammet"], "categories": ["customerservice", "office"], "sort_order": 13},
    {"user_id": USER_ID, "company": "Google Ads (via Vaco)", "title": "Svensk innehallsanalytiker for gTech", "location": "Sunnyvale, USA / Seoul / Hyderabad", "dates": "Maj 2018 - April 2019", "bullets": ["Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak", "Utforde extraktion och granskning av innehall for over 100 annonser per dag", "Arbetade i USA och pa distans i Indien, Sydkorea och Stockholm. Hanterade tidszonskoordinering", "Det svenska teamet uppnadde 100% mal for tjanstenivaavatalet"], "categories": ["tech", "content"], "sort_order": 14},
    {"user_id": USER_ID, "company": "Minerva Project - Student Experience Team", "title": "Evenemangskoordinator och elevhemsvard", "location": "San Francisco, USA", "dates": "Sep 2017 - Maj 2018", "bullets": ["Organiserade 60 evenemang for 210 internationella studenter, 2-3 per vecka", "Ansvarade for moten, budgetkontroll, narvaro, schemalggning och marknadsforing", "Organiserade stadsskattjakt dar studenter upptackte San Francisco", "Koordinerade gastforelasare och anvande mjukvara for eventlogistik"], "categories": ["office", "customerservice"], "sort_order": 15},
    {"user_id": USER_ID, "company": "Wallby Sateri", "title": "Gardsvard/Receptionist", "location": "Vetlanda", "dates": "Juni 2016 - Aug 2016", "bullets": ["Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar", "Assisterade vid cafeet och bidrog till allman service"], "categories": ["reception", "customerservice"], "sort_order": 16},
    {"user_id": USER_ID, "company": "ICA Maxi Stormarknad", "title": "Kassapersonal, frukt och gront", "location": "Vetlanda & Varmdo", "dates": "2015, 2017, 2019", "bullets": ["Arbetade i kassan, sjalvscanningen, frukt och gront, charken och blomavdelningen", "ICA-certifierad inom kassahantering, Trygga mat och sakerhet i butik"], "categories": ["retail"], "sort_order": 17},
    {"user_id": USER_ID, "company": "Coffeehouse by George", "title": "Cafepersonal", "location": "Stockholm", "dates": "2014 - 2015", "bullets": ["Kassahantering och barista", "Hog serviceeniva i centralt lage"], "categories": ["restaurant"], "sort_order": 18},
    {"user_id": USER_ID, "company": "Siggesta Gard", "title": "Gardsvard/Tradgardsarbetare", "location": "Varmdo", "dates": "2014 - 2015", "bullets": ["Kundbemotande pa stor evenemangsanlaggning (minigolf, restauranger, konferenser, hotell)", "Overseende roll med kommunikation mellan avdelningar. Ansvarade for marknad med ~1000 besokare/sondag", "Tradgardsarbete: klippte gras, rensade ogras, planterade, skrapsortering. Korde golfbil"], "categories": ["industry", "reception"], "sort_order": 19},
]

EDUCATION = [
    {"user_id": USER_ID, "school": "Minerva University", "degree": "B.S in Social Science, Economics and Business Administration", "location": "San Francisco, USA", "dates": "Aug 2017 - Maj 2021", "bullets": ["Varldens mest innovativa universitet enligt WURI", "Antagningsgrad pa 1.8% - mest selektiva universitetet i USA", "Studerade i fem lander: USA, Sydkorea, Indien, Tyskland och Argentina", "Handledde 45 studenter i examensprojekt inom fem amnen och branscher"], "sort_order": 1},
    {"user_id": USER_ID, "school": "United World College Red Cross Nordic", "degree": "International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85)", "location": "Flekke, Norge", "dates": "Aug 2015 - Maj 2017", "bullets": ["Utvald som toppelev fran Sverige bland 120 sokande, fullt stipendium", "Bodde med 200 elever fran 96 olika lander med fokus pa internationell fred och forstaelse", "Roda Korsets diplom: Guldutmarkelse for teamwork, frivilligarbete och ledarskap (100+ timmar)"], "sort_order": 2},
]

SKILLS = [
    # General
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Kundservice"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Kommunikation"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Teamwork"},
    {"user_id": USER_ID, "category": "all", "skill_type": "soft", "skill_text": "Stresshantering"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Svenska (Modersmal)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Engelska (Flytande)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Tyska (grundlaggande)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Spanska (grundlaggande)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "language", "skill_text": "Mandarin (HSK niva 3)"},
    {"user_id": USER_ID, "category": "all", "skill_type": "certificate", "skill_text": "B-korkort"},
    {"user_id": USER_ID, "category": "all", "skill_type": "certificate", "skill_text": "ICA kassahantering"},
    {"user_id": USER_ID, "category": "all", "skill_type": "certificate", "skill_text": "Trygga mat"},
    {"user_id": USER_ID, "category": "all", "skill_type": "certificate", "skill_text": "Roda Korset forsta hjalpen"},
    # Restaurant
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Kassasystem"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Barista"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "technical", "skill_text": "Servering"},
    {"user_id": USER_ID, "category": "restaurant", "skill_type": "certificate", "skill_text": "Livsmedelshygien"},
    # Tech/Content
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Content Moderation"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Trust & Safety"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Policy Compliance"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Data Analysis"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Python"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "SQL"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Tableau"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Google Analytics"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Google Ads"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Facebook Ads"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Adobe Creative Suite"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Content SEO"},
    {"user_id": USER_ID, "category": "tech", "skill_type": "technical", "skill_text": "Excel/Google Sheets"},
    # Customer service
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "technical", "skill_text": "Intercom"},
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "technical", "skill_text": "Zendesk"},
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "technical", "skill_text": "CRM-system"},
    {"user_id": USER_ID, "category": "customerservice", "skill_type": "soft", "skill_text": "Problemlosning"},
    # Retail
    {"user_id": USER_ID, "category": "retail", "skill_type": "technical", "skill_text": "Kassasystem"},
    {"user_id": USER_ID, "category": "retail", "skill_type": "technical", "skill_text": "Lagerhantering"},
    {"user_id": USER_ID, "category": "retail", "skill_type": "technical", "skill_text": "Merforsaljning"},
]

VOLUNTEER = [
    {"user_id": USER_ID, "organization": "LEAF (Living Environment and Future)", "dates": "2016 - 2017", "bullets": ["Ledde elevgrupp for att utbilda skolan i miljotank. Organiserade presentationer och kampanjer", "Skapade modemagasin for att sponsra hallbart jordbruksprojekt i Ghana. Samlade in 30,000 kr"], "sort_order": 1},
    {"user_id": USER_ID, "organization": "The Right Solution Project", "dates": "Mars 2013 - April 2015", "bullets": ["Tog initiativ att finansiera NGO for kvinnors utbildning vid 15 ars alder", "Samlade in over 120,000 kr genom evenemang och forsaljning", "Tillhandaholl 400+ vardpaket med hygienprodukter till etiopiska skolor. Tacktes i media tva ganger"], "sort_order": 2},
    {"user_id": USER_ID, "organization": "India Unlimited Utbytesprogram", "dates": "Nov 2014 - Feb 2015", "bullets": ["Deltog i EU-projekt for att framja fredliga relationer mellan Sverige och Indien", "Koordinerade hygienprojekt och fick kunskap om hallbar utveckling i utvecklingslander"], "sort_order": 3},
    {"user_id": USER_ID, "organization": "Varmdo Forsamling", "dates": "2012 - 2014", "bullets": ["Ledare for 3 konfirmandgrupper under 2 ar. Ledare pa tre veckos sommarlager pa Angsholmen", "Svenska Kyrkan: Ledarskapskurs steg 1 och 2"], "sort_order": 4},
]

AWARDS = [
    {"user_id": USER_ID, "award_text": "1:a pris Stockholms Konstsalong 2024 - Jurybedomd utstallning, nominerad Publikens Favorit", "sort_order": 1},
    {"user_id": USER_ID, "award_text": "1:a pris Greenpoint Gallery Brooklyn 2023 - Vann bland 60 konstnarer, fick soloutstallning", "sort_order": 2},
    {"user_id": USER_ID, "award_text": "1:a pris Murrays Creative Contest 2022 - Detroit-baserad tavling med specialdesign", "sort_order": 3},
    {"user_id": USER_ID, "award_text": "Global Startup Weekend Stockholm - Vinnare for Terra Finance (Google for Startups & Techstars)", "sort_order": 4},
    {"user_id": USER_ID, "award_text": "Tredje pris Chinese Bridge - Nationell tavling i kinesiskt sprak, Bergen 2016", "sort_order": 5},
    {"user_id": USER_ID, "award_text": "Roda Korsets diplom - Guldutmarkelse for teamwork och ledarskap (100+ volontartimmar)", "sort_order": 6},
    {"user_id": USER_ID, "award_text": "Minerva University Award for Initiative 2018", "sort_order": 7},
]

COVER_LETTER_PREFS = {
    "user_id": USER_ID,
    "tone": "professional_friendly",
    "max_words": 200,
    "greeting_style": "Hej!",
    "signature_style": "Med vanliga halsningar",
    "sign_off_name": "Linnea Moritz",
    "sign_off_phone": "076-116 61 09",
    "sign_off_email": "linneamoritz1@gmail.com",
    "always_mention": ["flexibel med tider", "korkort", "flytande engelska"],
    "never_mention": ["konst", "malning", "utstallningar", "Shopify", "e-handel", "oljemaalning", "linneamoritz.com"],
    "custom_ai_instructions": "Skriv pa naturlig, flytande svenska. Undvik AI-floskler som 'gedigen', 'brinner for', 'vittnar om'. Beratta varfor jag vill ha just det jobbet.",
}

CV_BRANSCHER = [
    {"user_id": USER_ID, "bransch_id": "restaurant", "bransch_name": "Restaurang & Cafe", "focus": "Service, tempo, kundkontakt", "keywords": ["servitor", "servitris", "restaurang", "cafe", "barista", "kok"], "is_active": True, "sort_order": 1},
    {"user_id": USER_ID, "bransch_id": "retail", "bransch_name": "Butik & Kassa", "focus": "Forsaljning, kassa, kundservice", "keywords": ["butik", "kassa", "saljare", "ica", "coop"], "is_active": True, "sort_order": 2},
    {"user_id": USER_ID, "bransch_id": "customerservice", "bransch_name": "Kundtjanst & Support", "focus": "Kommunikation, problemlosning, internationell erfarenhet", "keywords": ["kundtjanst", "support", "kundservice", "helpdesk"], "is_active": True, "sort_order": 3},
    {"user_id": USER_ID, "bransch_id": "content", "bransch_name": "Content & Moderation", "focus": "Trust & Safety, policy, granskning", "keywords": ["moderator", "content", "review", "granskning", "trust"], "is_active": True, "sort_order": 4},
    {"user_id": USER_ID, "bransch_id": "tech", "bransch_name": "Tech & Kontor", "focus": "Analytiskt arbete, data, tech-bolag", "keywords": ["tech", "IT", "data", "analyst", "kontor"], "is_active": True, "sort_order": 5},
    {"user_id": USER_ID, "bransch_id": "industry", "bransch_name": "Industri & Tradgard", "focus": "Fysiskt arbete, skift, materialhantering", "keywords": ["industri", "lager", "produktion", "operator", "tradgard"], "is_active": True, "sort_order": 6},
    {"user_id": USER_ID, "bransch_id": "healthcare", "bransch_name": "Vard & Omsorg", "focus": "Omvardnad, empati, medicinhantering", "keywords": ["vard", "omsorg", "aldre", "sjukvard"], "is_active": True, "sort_order": 7},
    {"user_id": USER_ID, "bransch_id": "art", "bransch_name": "Konst & Kultur", "focus": "Konstnarligt arbete, utstallningar, projektledning", "keywords": ["konst", "kultur", "galleri", "museum", "kreativ"], "is_active": True, "sort_order": 8},
]

# Full CV texts for each industry
CV_VERSIONS = [
    {"user_id": USER_ID, "vibe_id": "restaurant", "vibe_name": "Restaurang & Cafe", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021
- Varldens mest innovativa universitet enligt World's Universities with Real Impact (WURI).
- En antagningsgrans pa 1.8% gor Minerva till det mest selektiva universitetet i USA.
- Studerade i fem lander under fyra ar; USA, Sydkorea, Indien, Tyskland och Argentina.
- Handledde 45 studenter i deras examensprojekt inom fem olika amnen och branscher.

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma - Engelska och Svenska (GPA: 3.85) | Aug 2015 - Maj 2017
- Utvald som en toppelev fran Sverige bland 120 sokande och fick fullt stipendium.
- Bodde med 200 elever fran 96 olika lander med fokus pa internationell fred och forstaelse.
- Roda Korsets diplom; Guldutmarkelse for teamwork, frivilligarbete och ledarskap (100+ timmar).

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende
- 25% tjanst med sjalvstandig planering, cirka 40 timmar i manaden.
- Genomfor strategisk marknadsforing genom resor till skolor och massor i Vasteuropa och Norden.
- Bygger och underhaller databaser for skolkontakter, moten med SYO:er och studievagledare.
- Ansvarar for logistik: bokning av flyg, hotell och transporter for stort geografiskt omrade.

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025
- Sjalvstandigt butiksansvar med forsaljning av te, kaffe och choklad.
- Direktforsaljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
- Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbitrade | April 2024 - Aug 2024
- Arbetade i hogt tempo med drive-in, fritos, kok, servering, kassa och stad.
- Levererade god kundservice och samarbetade effektivt med teamet under rusningstid.

ICA Maxi Stormarknad - Vetlanda & Varmdo
Kassapersonal, frukt och gront | 2015, 2017, 2019
- Arbetade i kassan, sjalvscanningen, frukt och gront, charken och blomavdelningen.
- ICA-certifierad inom kassahantering, Trygga mat och sakerhet i butik.

Wallby Sateri - Vetlanda
Gardsvard/Receptionist | Juni 2016 - Aug 2016
- Arbetade i receptionen med bokningar, telefonsamtal, in- och utcheckning samt betalningar.
- Assisterade vid cafeet och bidrog till allman service.

Coffeehouse by George - Nacka
Cafepersonal | 2014 - 2015
- Kassahantering, kundbemotande, barista, matberedning och servering.

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen"""},
    {"user_id": USER_ID, "vibe_id": "retail", "vibe_name": "Butik & Kassa", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025
- Sjalvstandigt butiksansvar med forsaljning av te, kaffe och choklad.
- Direktforsaljning till kunder och barista. Arbetade 8 timmar ensam, mycket eget ansvar.
- Hanterade kassa, kundservice och lagerhantering.

Max Hamburgare - Vetlanda
Restaurangbitrade | April 2024 - Aug 2024

ICA Maxi Stormarknad - Vetlanda & Varmdo
Kassapersonal, frukt och gront | 2015, 2017, 2019
- Arbetade i kassan, sjalvscanningen, frukt och gront, charken och blomavdelningen.
- ICA-certifierad inom kassahantering, Trygga mat och sakerhet i butik.

Wallby Sateri - Vetlanda
Gardsvard/Receptionist | Juni 2016 - Aug 2016

Siggesta Gard - Varmdo
Gardsvard/Tradgardsarbetare | 2014 - 2015

Coffeehouse by George - Nacka
Cafepersonal | 2014 - 2015

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen"""},
    {"user_id": USER_ID, "vibe_id": "customerservice", "vibe_name": "Kundtjanst & Support", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025

Clubhouse (via Vaco) - Walnut Creek, USA
Innehallsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 - Jan 2022
- Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media.
- Hade fullt ansvar for att hantera alla arenden inom svenska, norska och danska marknaden.
- Identifierade brister i standardiserade arbetsrutiner och drev policyforbattringar.
- Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes.

Minerva Project - Berlin & Buenos Aires
Marknadsforing/Kundservice - Global Marketing Team | Sep 2019 - April 2020
- Vagledde och stottade over 2000 sokande elever via Intercom med hogkvalitativ kundservice.
- Svarade pa fragor fran elever i over 40 lander genom Intercom och personliga moten.

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehallsanalytiker for gTech | Maj 2018 - April 2019
- Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak.
- Utforde extraktion och granskning av innehall for over 100 annonser per dag.

ICA Maxi Stormarknad - Vetlanda & Varmdo
Kassapersonal, frukt och gront | 2015, 2017, 2019

Wallby Sateri - Vetlanda
Gardsvard/Receptionist | Juni 2016 - Aug 2016

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen
Tekniska fardigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Excel/Google Sheets"""},
    {"user_id": USER_ID, "vibe_id": "content", "vibe_name": "Content & Moderation", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 - Juni 2022
- Granskade innehallsmoderatorernas arbete for att sakerstalla att de foljer riktlinjer.
- Kvalitetssakrade moderering och bidrog till forbattrade processer.

YouTube Ads (via Vaco) - San Francisco, USA
Innehallsmoderator - Svenska marknaden | Feb 2022 - Juni 2022
- Flaggade olamplig reklam och bidrog till att utoka databaser med markerat innehall.
- Foljde noggrant alla riktlinjer och samarbetade med det svenska teamet.

Clubhouse (via Vaco) - Walnut Creek, USA
Innehallsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 - Jan 2022
- Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media.
- Hade fullt ansvar for alla arenden inom svenska, norska och danska marknaden.
- Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes.

Svensk-amerikanska handelskammaren - San Francisco, USA
Marknadsforing och forsaljningsutveckling | Juni 2021 - Sep 2021

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehallsanalytiker for gTech | Maj 2018 - April 2019
- Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak.
- Utforde extraktion och granskning av innehall for over 100 annonser per dag.

Minerva Project - Berlin & Buenos Aires
Marknadsforing/Kundservice - Global Marketing Team | Sep 2019 - April 2020

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen
Tekniska fardigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Excel/Google Sheets"""},
    {"user_id": USER_ID, "vibe_id": "tech", "vibe_name": "Tech & Kontor", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

TikTok/ByteDance - Nashville, USA
Kvalitetsgranskare - Amerikanska marknaden | Maj 2022 - Juni 2022

YouTube Ads (via Vaco) - San Francisco, USA
Innehallsmoderator - Svenska marknaden | Feb 2022 - Juni 2022

Clubhouse (via Vaco) - Walnut Creek, USA
Innehallsmoderator - Skandinaviska och amerikanska marknaden | Juni 2021 - Jan 2022
- Granskade Trust & Safety-arenden inom samtliga 16 kategorier for ljudbaserad social media.
- Okade produktiviteten med 98% samtidigt som alla dagliga kvalitetsmal uppfylldes.

Svensk-amerikanska handelskammaren - San Francisco, USA
Marknadsforing och forsaljningsutveckling | Juni 2021 - Sep 2021

Google Ads (via Vaco) - Sunnyvale, USA / Seoul / Hyderabad
Svensk innehallsanalytiker for gTech | Maj 2018 - April 2019
- Forbattrade och granskade svensk annonsering med expertkunskap inom svensk kultur och sprak.
- Utforde extraktion och granskning av innehall for over 100 annonser per dag.
- Det svenska teamet uppnadde 100% mal for tjanstenivaavatalet.

Minerva Project - Berlin & Buenos Aires
Marknadsforing/Kundservice - Global Marketing Team | Sep 2019 - April 2020

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen
Tekniska fardigheter: Python, SQL, Tableau, Google Analytics, Google Ads, Facebook Ads, Adobe Creative Suite, Intercom, CRM-system, Canva, Content SEO, Excel/Google Sheets"""},
    {"user_id": USER_ID, "vibe_id": "industry", "vibe_name": "Industri & Tradgard", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

Profilgruppen - Aseda
Anodiseringsoperator (Feriearbete) | Juli 2024 - Aug 2024
- Utforde tungt fysiskt arbete med fokus pa armlyft och materialhantering.
- Arbetade pa tvaskift (06.00-14.00 och 14.00-23.00).
- Genomgick utbildning i handtravers och samarbetade med dagligen roterande kollegor.

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025

Max Hamburgare - Vetlanda
Restaurangbitrade | April 2024 - Aug 2024

Kvarngarden aldreboende - Vetlanda
Timvikarie | Maj 2020 - Sep 2020

ICA Maxi Stormarknad - Vetlanda & Varmdo
Kassapersonal, frukt och gront | 2015, 2017, 2019

Siggesta Gard - Varmdo
Gardsvard/Tradgardsarbetare | 2014 - 2015
- Kundbemotande pa stor evenemangsanlaggning (minigolf, restauranger, konferenser, hotell).
- Overseende roll med kommunikation mellan avdelningar.
- Tradgardsarbete: klippte gras, rensade ogras, planterade, skrapsortering. Korde golfbil.

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen"""},
    {"user_id": USER_ID, "vibe_id": "healthcare", "vibe_name": "Vard & Omsorg", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025

Max Hamburgare - Vetlanda
Restaurangbitrade | April 2024 - Aug 2024

Kvarngarden aldreboende - Vetlanda
Timvikarie | Maj 2020 - Sep 2020
- Omvardnad, medicinhantering, maltidsassistans, dokumentation och emotionellt stod.
- Gav omsorg till aldre personer med demens och Alzheimers sjukdom.
- Foljde noggrant covid-protokoll och arbetade bade morgon- och kvallspass.

ICA Maxi Stormarknad - Vetlanda & Varmdo
Kassapersonal, frukt och gront | 2015, 2017, 2019

Wallby Sateri - Vetlanda
Gardsvard/Receptionist | Juni 2016 - Aug 2016

Siggesta Gard - Varmdo
Gardsvard/Tradgardsarbetare | 2014 - 2015

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen"""},
    {"user_id": USER_ID, "vibe_id": "art", "vibe_name": "Konst & Kultur", "vibe_emoji": "", "cv_text": """Linnea Moritz
Innehar B-Korkort | Sollentuna | 0761166109 | linneamoritzcv@gmail.com

UTBILDNING

Minerva University - San Francisco, USA
B.S in Social Science, Economics and Business Administration (GPA: 3.6) | Aug 2017 - Maj 2021

United World College Red Cross Nordic - Flekke, Norge
International Baccalaureate Bilingual Diploma (GPA: 3.85) | Aug 2015 - Maj 2017

ARBETSLIVSERFARENHET

Keeping Tabs - New York, USA
Multimedia Technical Specialist | Nov 2022 - Juni 2023
- Planerade och koordinerade konstsamling for Art Basel Hong Kong.
- Designade visuell merchandise och rullade ut forsaljnings- och logistikkampanj.

30 Campos Eliseos - New York, USA
Kubistisk malare | 2022 - 2024
- Scoutad som professionell kubistmalare till prestigefylld konstsamlargrupp grundad i Florens.
- En av endast fem konstnarer utvalda bland 500+ sokande.

Minerva University - Stockholm
Alumni Ambassador Western Europe | Sep 2024 - Pagaende

Minerva University - San Francisco, USA
Handledare for examensprojekt | Sep 2020 - Maj 2021
- Handledde 45 studenter i capstone-projekt inom VR, hallbart mode, varumarkesanalys och historiska romaner.

Minerva Project - Berlin & Buenos Aires
Marknadsforing/Kundservice - Global Marketing Team | Sep 2019 - April 2020

Minerva Project - Student Experience Team - San Francisco, USA
Evenemangskoordinator och elevhemsvard | Sep 2017 - Maj 2018
- Organiserade 60 evenemang for 210 internationella studenter, 2-3 per vecka.

House of Beans, Hotorgshallen - Stockholm
Forsaljare/Barista | Aug 2024 - Feb 2025

SPRAK & KVALIFIKATIONER
Sprak: Svenska (Modersmal), Engelska (flytande), Tyska (grundlaggande), Spanska (grundlaggande), Mandarin (HSK niva 3)
Certifikat: B-korkort (automat), ICA kassahantering, Trygga mat, Roda Korset forsta hjalpen"""},
]


def db_request(method, table, data=None, params=None):
    """Make request to Supabase REST API using service role key."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=30)
        else:
            return None

        if response.status_code >= 400:
            print(f"  VARNING {table}: {response.status_code} - {response.text[:200]}")
            return None

        return response.json() if response.text else []
    except Exception as e:
        print(f"  FEL {table}: {e}")
        return None


def migrate():
    print(f"\n{'='*60}")
    print(f"MIGRERAR FULLSTANDIG DATA for anvandare: {USER_ID}")
    print(f"Email: linneamoritz1@gmail.com")
    print(f"Supabase: {SUPABASE_URL}")
    print(f"{'='*60}\n")

    # 1. Profil
    print("1/10. Sparar profil...")
    result = db_request("POST", "user_profiles?on_conflict=user_id", PROFILE_DATA)
    if result:
        print("   OK Profil sparad")
    else:
        print("   FEL Profil kunde inte sparas")

    # 2. Jobbpreferenser
    print("2/10. Sparar jobbpreferenser...")
    result = db_request("POST", "user_job_preferences?on_conflict=user_id", JOB_PREFERENCES)
    if result:
        print("   OK Preferenser sparade")
    else:
        print("   FEL Preferenser kunde inte sparas")

    # 3. Erfarenheter (radera gamla, batch-insarta nya)
    print(f"3/10. Sparar {len(EXPERIENCES)} arbetslivserfarenheter...")
    db_request("DELETE", "user_experiences", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_experiences", EXPERIENCES)
    if result:
        print(f"   OK {len(EXPERIENCES)} erfarenheter sparade")
    else:
        print("   FEL Erfarenheter - forsoker en i taget...")
        ok = 0
        for exp in EXPERIENCES:
            r = db_request("POST", "user_experiences", exp)
            if r:
                ok += 1
        print(f"   {ok}/{len(EXPERIENCES)} erfarenheter sparade")

    # 4. Utbildning
    print(f"4/10. Sparar {len(EDUCATION)} utbildningar...")
    db_request("DELETE", "user_education", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_education", EDUCATION)
    if result:
        print(f"   OK {len(EDUCATION)} utbildningar sparade")
    else:
        print("   FEL Utbildning - forsoker en i taget...")
        for edu in EDUCATION:
            db_request("POST", "user_education", edu)

    # 5. Fardigheter
    print(f"5/10. Sparar {len(SKILLS)} fardigheter...")
    db_request("DELETE", "user_skills", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_skills", SKILLS)
    if result:
        print(f"   OK {len(SKILLS)} fardigheter sparade")
    else:
        print("   FEL Skills - forsoker en i taget...")
        ok = 0
        for skill in SKILLS:
            r = db_request("POST", "user_skills", skill)
            if r:
                ok += 1
        print(f"   {ok}/{len(SKILLS)} fardigheter sparade")

    # 6. Volontararbete
    print(f"6/10. Sparar {len(VOLUNTEER)} volontararbeten...")
    db_request("DELETE", "user_volunteer", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_volunteer", VOLUNTEER)
    if result:
        print(f"   OK {len(VOLUNTEER)} volontararbeten sparade")
    else:
        for vol in VOLUNTEER:
            db_request("POST", "user_volunteer", vol)

    # 7. Utmarkelser
    print(f"7/10. Sparar {len(AWARDS)} utmarkelser...")
    db_request("DELETE", "user_awards", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_awards", AWARDS)
    if result:
        print(f"   OK {len(AWARDS)} utmarkelser sparade")
    else:
        for award in AWARDS:
            db_request("POST", "user_awards", award)

    # 8. Cover letter preferences
    print("8/10. Sparar personligt brev-installningar...")
    result = db_request("POST", "user_cover_letter_preferences?on_conflict=user_id", COVER_LETTER_PREFS)
    if result:
        print("   OK Cover letter prefs sparade")

    # 9. CV-branscher
    print(f"9/10. Sparar {len(CV_BRANSCHER)} CV-branscher...")
    db_request("DELETE", "user_cv_branscher", params={"user_id": f"eq.{USER_ID}"})
    result = db_request("POST", "user_cv_branscher", CV_BRANSCHER)
    if result:
        print(f"   OK {len(CV_BRANSCHER)} branscher sparade")
    else:
        for b in CV_BRANSCHER:
            db_request("POST", "user_cv_branscher", b)

    # 10. CV-versioner
    print(f"10/10. Sparar {len(CV_VERSIONS)} CV-versioner...")
    db_request("DELETE", "user_cvs", params={"user_id": f"eq.{USER_ID}"})
    for cv in CV_VERSIONS:
        cv["created_at"] = datetime.now().isoformat()
    result = db_request("POST", "user_cvs", CV_VERSIONS)
    if result:
        print(f"   OK {len(CV_VERSIONS)} CV-versioner sparade")
    else:
        print("   FEL CVs - forsoker en i taget...")
        ok = 0
        for cv in CV_VERSIONS:
            r = db_request("POST", "user_cvs", cv)
            if r:
                ok += 1
                print(f"   OK {cv['vibe_name']}")
        print(f"   {ok}/{len(CV_VERSIONS)} CV-versioner sparade")

    print(f"\n{'='*60}")
    print("MIGRATION KLAR!")
    print(f"{'='*60}")
    print(f"   Profil: OK")
    print(f"   Preferenser: OK")
    print(f"   Erfarenheter: {len(EXPERIENCES)} st")
    print(f"   Utbildning: {len(EDUCATION)} st")
    print(f"   Fardigheter: {len(SKILLS)} st")
    print(f"   Volontararbete: {len(VOLUNTEER)} st")
    print(f"   Utmarkelser: {len(AWARDS)} st")
    print(f"   Cover letter prefs: OK")
    print(f"   CV-branscher: {len(CV_BRANSCHER)} st")
    print(f"   CV-versioner: {len(CV_VERSIONS)} st")
    print(f"\nVerifiera pa: https://platsbanken-ai.vercel.app")


if __name__ == "__main__":
    migrate()
