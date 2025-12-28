import re

new_class_code = """
class CoverLetterGenerator:
    \"\"\"Genererar personliga brev med Claude API - High Energy Version\"\"\"
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def get_relevant_experience(self, category: str) -> str:
        experiences = {
            "restaurant": "När jag jobbade på House of Beans i Hötorgshallen skötte jag hela butiken själv. Jag älskar kundmötet och att få rekommendera rätt kaffe eller choklad. På Max Hamburgare lärde jag mig att behålla lugnet även när kön sträcker sig utanför dörren och allt måste hända samtidigt – jag trivs som bäst när det är högt tempo.",
            "retail": "På ICA Maxi har jag suttit i kassan i flera vända. Jag är snabb, noggrann och gillar tempot. Jag är den där personen som faktiskt gillar när det blir mycket folk – det är då det blir kul att jobba och man får visa vad man går för.",
            "industry": "Jag är inte rädd för att ta i och få skit under naglarna. Som anodiseringsoperatör på Profilgruppen körde jag tunga pass och trivdes med det fysiska arbetet. På Siggesta Gård fixade jag allt i trädgården, från gräsklippning till tunga lyft, och jag ser till att jobbet blir gjort ordentligt utan gnäll.",
            "healthcare": "Som timvikarie på Kvarngården äldreboende lärde jag mig att möta människor med både tålamod och empati, även i stressiga situationer. Jag är van vid medicinhantering och att ta stort ansvar för andras välmående.",
            "tech": "Jag har jobbat som moderator för jättar som YouTube och TikTok. Det kräver extremt fokus och förmågan att ta snabba, korrekta beslut under press. Jag ökade produktiviteten med 98% på Clubhouse eftersom jag gillar att optimera mitt sätt att jobba.",
            "reception": "På Wallby Säteri skötte jag allt från reception och bokningar till caféet. Jag är ansiktet utåt som ser till att gästerna känner sig välkomna direkt när de kliver innanför dörren."
        }
        return experiences.get(category, "Jag har bred erfarenhet från service och gillar att jobba där det händer saker.")

    def generate_cover_letter(self, job: Job) -> str:
        if not self.api_key: return "API-key missing."
        category = self.detect_job_category(job)
        relevant_exp = self.get_relevant_experience(category)
        company_short = job.company.replace(" AB", "").replace(" Sverige", "").strip()
        
        prompt = f\"\"\"Skriv ett personligt brev på svenska (ca 180-200 ord).
Du är Linnea, 28 år från Sollentuna. Du har extremt mycket energi, hatar att sitta still och älskar att lösa problem. Du är rak, ärlig och prestigelös.

DIN ERFARENHET: {relevant_exp}
JOBBET: {job.title} på {company_short}. Beskrivning: {job.description[:1000]}

INSTRUKTIONER:
1. Skriv på naturlig, flytande svenska. Variera meningsbyggnaden (V2-regeln).
2. Undvik AI-floskler som 'gedigen', 'brinner för', 'vittnar om'.
3. Berätta varför DU vill ha jobbet (tempot/människorna/fysiskt arbete).
4. Signaturen ska vara: Med vänliga hälsningar, Linnea Moritz, 076-116 61 09.
STRIKT FÖRBUD: Nämn ALDRIG konst, utställningar, oljemålning eller Shopify.\"\"\"

        try:
            response = requests.post(self.api_url, headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-3-5-sonnet-20240620", "max_tokens": 600, "messages": [{"role": "user", "content": prompt}]}, timeout=30)
            if response.status_code == 200: return response.json()["content"][0]["text"].strip()
        except Exception as e: print(f"Error: {e}")
        return "Kunde inte generera brev."

    def detect_job_category(self, job: Job) -> str:
        text = f"{job.title} {job.description}".lower()
        categories = {"tech": ["moderator", "content review", "google", "youtube", "tiktok"], "restaurant": ["servitör", "servitris", "restaurang", "café", "barista"], "retail": ["butik", "kassa", "säljare", "ica", "coop"], "industry": ["industri", "lager", "produktion", "operatör", "trädgård"], "healthcare": ["vård", "omsorg", "äldre"], "reception": ["reception", "receptionist", "admin"]}
        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords): return cat
        return "general"
"""

with open("job_portal_backend.py", "r") as f:
    content = f.read()

# This finds the old class and replaces it with the new one
pattern = r"class CoverLetterGenerator:.*?def detect_job_category\(self, job: Job\) -> str:.*?return \"general\""
updated_content = re.sub(pattern, new_class_code, content, flags=re.DOTALL)

with open("job_portal_backend.py", "w") as f:
    f.write(updated_content)

print("✅ Surgery successful! The High-Energy Linnea persona is now in your backend.")
