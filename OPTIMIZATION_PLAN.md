# Code Optimization Plan — Anti-Apathy Job Portal

> Skapad: 2026-02-18
> Status: Implementering pågår
> Mål: Minska `v2/api/index.py` (6,443 rader) och `v2/frontend.html` (5,760 rader) med ~20% utan att ändra funktionalitet

---

## Varför?

Båda filerna har vuxit organiskt och passerat smärtgränsen:
- `frontend.html` är **325 KB** — större än verktygets max-läsgräns (256 KB)
- `api/index.py` har **6,443 rader** med tydliga dupliceringsmönster
- Samma kod upprepas 30+ gånger i backend (auth-pattern)
- Samma fetch-mönster upprepas 25+ gånger i frontend
- Två separata GDPR export/delete-endpoints gör exakt samma sak

---

## Backend: `v2/api/index.py`

### 1. Extract `get_user_id_from_request()` — ~200 rader sparas

**Problem:** 30+ endpoints upprepar detta 12-raders mönster:
```python
auth_header = request.headers.get("Authorization", "")
user_id = None
if auth_header.startswith("Bearer "):
    token = auth_header.replace("Bearer ", "")
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if user_response.status_code == 200:
                user_id = user_response.json().get("id")
    except Exception:
        pass
```

**Lösning:** En enda helper:
```python
async def get_user_id_from_request(request: Request, required: bool = False) -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        if required:
            raise HTTPException(status_code=401, detail="Ej inloggad")
        return None
    token = auth_header.replace("Bearer ", "")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                return resp.json().get("id")
    except Exception:
        pass
    if required:
        raise HTTPException(status_code=401, detail="Ej inloggad")
    return None
```

**Endpoints som berörs (30+):**
- `/api/jobs` (line 1042), `/api/jobs/{id}/interaction` (1102), `/api/applications` POST (1170)
- `/api/jobs/{id}/save` (1263), DELETE save (1317), `/api/cv/master` POST (1385)
- `/api/cv/master` GET (1493), `/api/cv/generate-branscher` (1665), `/api/cv/all` (1714)
- `/api/master-cv` GET (1772), och 20+ fler endpoints

---

### 2. Supabase headers-konstant — ~150 rader sparas

**Problem:** Headers byggs om 50+ gånger:
```python
headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
```

**Lösning:**
```python
def get_supabase_headers(prefer: str = "return=representation") -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer
    }
```

---

### 3. Hardcoded CV-migrationsdata — ~810 rader (lines 2673-3483)

**Problem:** `CV_VERSIONS` i `/api/migrate-my-data` innehåller 8 fullständiga CV-texter som strängliteraler — 810 rader hårdkodad data.

**Nuläge:** Detta är en engångs-migreringsendpoint (Linneas CV-data). Den fungerar och borde inte störa, men utgör 12.5% av hela backend-filen.

**Lösning:** Flytta data till en separat JSON-fil (`v2/api/migration_data.json`) som laddas vid behov. Alternativt: markera som legacy och ignorera tills den rensas.

**Risk:** Låg — denna endpoint körs sällan.

---

### 4. Konsolidera filuppladdning — ~200 rader sparas

**Problem:** Tre nästan identiska upload-handlers:
- CV-upload (lines 5693-5810)
- Profilfoto-upload (lines 5813-5897)
- Training letter-upload (lines 6208-6287)

Alla gör: auth → fil → extension → upload till Supabase Storage → spara URL i DB.

**Lösning:** Gemensam `upload_to_supabase_storage()` helper:
```python
async def upload_to_supabase_storage(
    user_id: str, file: UploadFile, bucket: str, path: str
) -> str:
    """Upload file to Supabase Storage, return public URL."""
    ...
```

---

### 5. Duplicerade GDPR export/delete — ~270 rader sparas

**Problem:** Två separata implementationer av exakt samma funktionalitet:

| Endpoint | Funktion | Rader |
|----------|----------|-------|
| `GET /api/auth/export-data` | `export_user_data` | 4779-4845 |
| `GET /api/user/export-data` | `export_user_data_gdpr` | 5364-5425 |
| `DELETE /api/auth/delete-account` | `delete_account` | 4687-4775 |
| `DELETE /api/user/delete-account` | `delete_user_account` | 5429-5479 |

**Lösning:** Behåll en implementation per funktion, låt den andra routen peka till samma handler.

---

### 6. Claude API-wrapper — ~80 rader sparas

**Problem:** 5 ställen gör nästan identiska POST till `api.anthropic.com/v1/messages`:
- `generate_cover_letter()` (line 621)
- `generate_cv_vibe()` (line 765)
- CV-analys (line ~4511)
- Writing tone-analys (line ~6360 och ~6407)

**Lösning:**
```python
async def call_claude_api(
    prompt: str, model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 600, timeout: int = 25
) -> Optional[str]:
    ...
```

---

### 7. Content-type-mappning — ~60 rader sparas

**Problem:** Fil-extension → content-type mappas 4 gånger på olika ställen.

**Lösning:** Modul-nivå-konstant:
```python
CONTENT_TYPE_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".txt": "text/plain",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp",
}
```

---

### 8. CV-kategoridefinitioner — ~80 rader sparas

**Problem:** `CV_BRANSCHER` definieras globalt (line 232), sedan dupliceras i:
- `vibe_keywords` i `match_job_to_cv_vibe()` (line 827)
- `categories` i `get_fallback_recommendations()` (line ~4550)
- `CV_BRANSCHER` i `/api/migrate-my-data` (line 2662)

**Lösning:** En enda definitionsplats, alla andra refererar till den.

---

### Backend-sammanfattning

| # | Optimering | Rader sparas | Komplexitet |
|---|-----------|-------------|-------------|
| 1 | Auth helper | ~200 | Låg |
| 2 | Supabase headers | ~150 | Låg |
| 3 | CV-migrationsdata | ~810 | Medium |
| 4 | Filuppladdning | ~200 | Medium |
| 5 | GDPR export/delete | ~270 | Låg |
| 6 | Claude API wrapper | ~80 | Låg |
| 7 | Content-type map | ~60 | Låg |
| 8 | CV-kategorier | ~80 | Låg |
| **TOTAL** | | **~1,850** | |

**Estimerad ny storlek:** ~4,600 rader (28% minskning)

---

## Frontend: `v2/frontend.html`

### 1. Extract `authFetch()` helper — ~180 rader sparas

**Problem:** 25-30 ställen upprepar:
```javascript
const token = localStorage.getItem('auth_token');
const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
};
const res = await fetch('/api/...', { method: 'POST', headers, body: JSON.stringify(...) });
```

**Lösning:**
```javascript
const authFetch = async (url, options = {}) => {
    const token = localStorage.getItem('auth_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };
    return fetch(url, { ...options, headers });
};
```

---

### 2. Remove dead `_ONBOARDING_OLD_UNUSED` — ~350 rader sparas

**Plats:** Lines 4409-4761
**Problem:** Hela funktionen är oläsbar, invirad i `.hidden`, inte renderad nånstans.
**Lösning:** Ta bort helt.

---

### 3. Button style-konstanter — ~80 rader sparas

**Problem:** Samma Tailwind-klasser upprepas 20-50 gånger:
```javascript
className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
```

**Lösning:**
```javascript
const BTN = {
    primary: "bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700",
    secondary: "border border-slate-200 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50",
    danger: "bg-red-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-red-700",
};
```

---

### 4. Konsolidera filuppladdnings-handlers — ~90 rader sparas

**Problem:** 4 nästan identiska `createFileInput(accept, onSelect)` mönster.

---

### 5. Extrahera `<ModalHeader>` komponent — ~50 rader sparas

**Problem:** Modal-headers med gradient och titel upprepas i 4+ modaler.

---

### 6. Deduplika option/checkbox-mönster — ~60 rader sparas

**Problem:** Lan/Kommun/Working hours/Dealbreaker-knappar följer identiskt mönster.

---

### Frontend-sammanfattning

| # | Optimering | Rader sparas | Komplexitet |
|---|-----------|-------------|-------------|
| 1 | authFetch() helper | ~180 | Låg |
| 2 | Ta bort dead code | ~350 | Låg |
| 3 | Button-konstanter | ~80 | Låg |
| 4 | Filuppladdning | ~90 | Medium |
| 5 | ModalHeader | ~50 | Låg |
| 6 | Option-knappar | ~60 | Medium |
| **TOTAL** | | **~810** | |

**Estimerad ny storlek:** ~4,950 rader (14% minskning)

---

## Implementeringsordning

### Fas 1 — Låg risk, stort impact (backend)
1. Lägg till `get_user_id_from_request()`, `get_supabase_headers()`, `call_claude_api()`, `CONTENT_TYPE_MAP`
2. Ersätt alla 30+ auth-block med helper-anrop
3. Ersätt Supabase headers med helper
4. Slå ihop duplicerade GDPR-endpoints

### Fas 2 — Medium risk (backend)
5. Konsolidera filuppladdning
6. Flytta CV-migrationsdata till separat fil

### Fas 3 — Frontend
7. Lägg till `authFetch()` och `BTN`-konstanter
8. Ta bort `_ONBOARDING_OLD_UNUSED`
9. Extrahera delade komponenter

---

## Totalt

| Fil | Före | Efter | Minskning |
|-----|------|-------|-----------|
| `v2/api/index.py` | 6,443 | ~4,600 | 28% |
| `v2/frontend.html` | 5,760 | ~4,950 | 14% |
| **Totalt** | **12,203** | **~9,550** | **~22%** |

Ingen funktionalitet ändras. Inga nya features. Bara renare, mer underhållbar kod.
