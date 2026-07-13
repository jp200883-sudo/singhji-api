"""
🦁 SINGH JI AI ULTRA v8.0 — HYBRID SYSTEM
100% REAL | Railway Primary | All APIs Live
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
import json
import time
import asyncio
import hashlib
import base64
import io
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import requests
import logging
from collections import defaultdict, deque
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "1008554401796459")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
PLANT_ID_API = os.getenv("PLANT_ID_API")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID")
BHASHINI_ULCA_API_KEY = os.getenv("BHASHINI_ULCA_API_KEY")
BHASHINI_INFERENCE_API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

AVAILABLE_KEYS = {
    "ADMIN": bool(ADMIN_API_KEY),
    "CEREBRAS": bool(CEREBRAS_API_KEY),
    "CF": bool(CF_API_TOKEN),
    "CURRENTS": bool(CURRENTS_API_KEY),
    "DATABASE": bool(DATABASE_URL),
    "FACEBOOK": bool(FACEBOOK_ACCESS_TOKEN),
    "GEMINI": bool(GEMINI_API_KEY),
    "GROQ": bool(GROQ_API_KEY),
    "HUGGINGFACE": bool(HUGGINGFACE_TOKEN),
    "MANDI": bool(MANDI_API_KEY),
    "NEWSDATA": bool(NEWSDATA_API_KEY),
    "OPENWEATHER": bool(OPENWEATHER_API_KEY),
    "PLANT_ID": bool(PLANT_ID_API),
    "RAPIDAPI": bool(RAPIDAPI_KEY),
    "RAZORPAY": bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET),
    "SUPABASE": bool(SUPABASE_URL and SUPABASE_SERVICE_KEY),
    "TAVILY": bool(TAVILY_API_KEY),
    "TELEGRAM": bool(TELEGRAM_TOKEN),
    "TWILIO": bool(TWILIO_SID and TWILIO_TOKEN),
    "YOUTUBE": bool(YOUTUBE_API_KEY),
    "BHASHINI": bool(BHASHINI_USER_ID and BHASHINI_ULCA_API_KEY),
    "GMAIL": bool(GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET),
    "INSTAGRAM": bool(INSTAGRAM_ACCESS_TOKEN),
}

SUPABASE_CLIENT = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase connected")
except Exception as e:
    logger.warning(f"Supabase init failed: {e}")

CACHE_TTL = {
    "weather": 1800,
    "mandi": 21600,
    "ai_chat": 3600,
    "news": 900,
    "default": 300
}

def _cache_key(prefix, *args):
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()

def _cache_get(key):
    if SUPABASE_CLIENT:
        try:
            resp = SUPABASE_CLIENT.table("cache_store").select("*").eq("key", key).execute()
            if resp.data:
                entry = resp.data[0]
                if entry.get("expires_at") and datetime.now().isoformat() < entry["expires_at"]:
                    return entry["value"]
                SUPABASE_CLIENT.table("cache_store").delete().eq("key", key).execute()
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
    return None

def _cache_set(key, value, ttl=None):
    if not SUPABASE_CLIENT:
        return
    ttl = ttl or CACHE_TTL["default"]
    expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
    try:
        SUPABASE_CLIENT.table("cache_store").upsert({
            "key": key,
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

MEMORY_STORE = {}
MAX_MEMORY_SIZE = 1000

def _check_memory_limit():
    if len(MEMORY_STORE) > MAX_MEMORY_SIZE:
        keys_to_remove = list(MEMORY_STORE.keys())[:int(MAX_MEMORY_SIZE * 0.2)]
        for k in keys_to_remove:
            del MEMORY_STORE[k]
        logger.info(f"Memory cleaned: removed {len(keys_to_remove)} old entries")
USER_PREFERENCES = {}

def _memory_save(key, value, table="memory_store"):
    if SUPABASE_CLIENT:
        try:
            SUPABASE_CLIENT.table(table).upsert({
                "key": key,
                "value": value,
                "updated_at": datetime.now().isoformat()
            }).execute()
            return {"saved": True, "store": "supabase", "key": key}
        except Exception as e:
            logger.warning(f"Supabase save error: {e}")
    _check_memory_limit()
    MEMORY_STORE[key] = value
    return {"saved": True, "store": "ram", "key": key}

def _memory_get(key, table="memory_store"):
    if SUPABASE_CLIENT:
        try:
            resp = SUPABASE_CLIENT.table(table).select("*").eq("key", key).execute()
            if resp.data:
                return {"key": key, "data": resp.data[0]["value"], "exists": True, "store": "supabase"}
        except Exception as e:
            logger.warning(f"Supabase get error: {e}")
    if key in MEMORY_STORE:
        return {"key": key, "data": MEMORY_STORE[key], "exists": True, "store": "ram"}
    return {"key": key, "data": None, "exists": False}

def _check_admin_auth(request):
    if not ADMIN_API_KEY:
        return True
    provided = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    return provided == ADMIN_API_KEY

class _SmartSarwanSwarm:
    def __init__(self):
        self.all_agents = {}
        self.active_agents = {}
        self.CLAWS = {
            "claw_1_agriculture": {"name": "Agriculture", "agents": 30, "prefix": "AGR"},
            "claw_2_health": {"name": "Health", "agents": 30, "prefix": "HLT"},
            "claw_3_finance": {"name": "Finance", "agents": 30, "prefix": "FIN"},
            "claw_4_education": {"name": "Education", "agents": 30, "prefix": "EDU"},
            "claw_5_governance": {"name": "Governance", "agents": 30, "prefix": "GOV"},
            "claw_6_transport": {"name": "Transport", "agents": 30, "prefix": "TRP"},
            "claw_7_voice": {"name": "Voice", "agents": 30, "prefix": "VCE"},
            "claw_8_media": {"name": "Media", "agents": 30, "prefix": "MED"},
            "claw_9_safety": {"name": "Safety", "agents": 30, "prefix": "SFT"},
            "claw_10_boss": {"name": "Boss", "agents": 10, "prefix": "BOS"},
            "claw_11_core_ai": {"name": "Core AI", "agents": 20, "prefix": "AI"},
        }
        self._register_all()

    def _register_all(self):
        for claw_key, info in self.CLAWS.items():
            for i in range(1, info["agents"] + 1):
                agent_id = f"{info['prefix']}-{i:03d}"
                self.all_agents[agent_id] = {
                    "id": agent_id,
                    "name": f"{info['prefix']} Agent {i}",
                    "claw": claw_key,
                    "claw_name": info["name"],
                    "status": "offline"
                }
        logger.info(f"{len(self.all_agents)} agents registered")

    def sync(self, modules_status, available_keys):
        to_load = set()
        for agent_id, agent in self.all_agents.items():
            if agent["claw"] in ["claw_10_boss", "claw_11_core_ai"]:
                to_load.add(agent_id)
        self.active_agents = {}
        for aid in to_load:
            agent = self.all_agents[aid].copy()
            agent["status"] = "idle"
            agent["last_active"] = datetime.now().isoformat()
            self.active_agents[aid] = agent
        return {"loaded": len(to_load), "active": len(self.active_agents), "total": len(self.all_agents)}

    def get_status(self):
        return {
            "total_registered": len(self.all_agents),
            "currently_loaded": len(self.active_agents),
            "active_running": sum(1 for a in self.active_agents.values() if a["status"] == "active"),
            "idle": sum(1 for a in self.active_agents.values() if a["status"] == "idle"),
            "busy": sum(1 for a in self.active_agents.values() if a["status"] == "busy"),
        }

SMART_SWARM = _SmartSarwanSwarm()

MODULES = {
    "memory": {"needs_key": None, "active": True},
    "weather": {"needs_key": "OPENWEATHER", "active": AVAILABLE_KEYS["OPENWEATHER"]},
    "news": {"needs_key": "CURRENTS", "active": AVAILABLE_KEYS["CURRENTS"]},
    "mandi": {"needs_key": "MANDI", "active": AVAILABLE_KEYS["MANDI"]},
    "plant_id": {"needs_key": "PLANT_ID", "active": AVAILABLE_KEYS["PLANT_ID"]},
    "payment": {"needs_key": "RAZORPAY", "active": AVAILABLE_KEYS["RAZORPAY"]},
    "admin": {"needs_key": None, "active": True},
    "facebook": {"needs_key": "FACEBOOK", "active": AVAILABLE_KEYS["FACEBOOK"]},
    "instagram": {"needs_key": "INSTAGRAM", "active": AVAILABLE_KEYS["INSTAGRAM"]},
    "youtube": {"needs_key": "YOUTUBE", "active": AVAILABLE_KEYS["YOUTUBE"]},
    "gmail": {"needs_key": "GMAIL", "active": AVAILABLE_KEYS["GMAIL"]},
    "swarm": {"needs_key": None, "active": True},
    "telegram_bot": {"needs_key": "TELEGRAM", "active": AVAILABLE_KEYS["TELEGRAM"]},
    "aavishkar": {"needs_key": "GROQ", "active": AVAILABLE_KEYS["GROQ"] or AVAILABLE_KEYS["GEMINI"]},
    "bhashini": {"needs_key": "BHASHINI", "active": AVAILABLE_KEYS["BHASHINI"]},
    "whisper": {"needs_key": None, "active": True},
}

# ═══════════════════════════════════════════════════════
# 🦁 RATE LIMITER — per-IP, in-memory sliding window
# Global default limit on all /api/, /modules/, /telegram/ paths.
# Stricter limit on expensive/misuse-prone paths (voice, AI chat,
# bhashini, plant id).
# ═══════════════════════════════════════════════════════
_rate_lock = threading.Lock()
_rate_buckets = defaultdict(deque)

RATE_LIMIT_GLOBAL = (60, 60)   # 60 requests / 60 seconds per IP
RATE_LIMIT_STRICT = (8, 60)    # 8 requests / 60 seconds per IP
STRICT_PATH_PREFIXES = (
    "/api/chat",
    "/api/whisper/",
    "/api/bhashini/",
    "/api/tts",
    "/api/plant/",
    "/modules/voice",
)
RATE_LIMITED_PREFIXES = ("/api/", "/modules/")

def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _rate_check(key: str, max_calls: int, window_seconds: int) -> bool:
    """Returns True if the caller should be BLOCKED (limit exceeded)."""
    now = time.time()
    with _rate_lock:
        dq = _rate_buckets[key]
        while dq and dq[0] < now - window_seconds:
            dq.popleft()
        if len(dq) >= max_calls:
            return True
        dq.append(now)
        return False

def _is_rate_limited(request: Request, bucket: str, max_calls: int, window_seconds: int) -> bool:
    """IP-based check, for the global HTTP middleware."""
    ip = _client_ip(request)
    return _rate_check(f"{bucket}:{ip}", max_calls, window_seconds)

# Telegram webhook traffic all arrives from Telegram's own servers (same
# IP range for every user), so IP-based limiting would throttle the whole
# bot at once. Instead we rate-limit per Telegram user_id, checked inside
# the webhook handler itself — see RATE_LIMIT_TELEGRAM_USER below.
RATE_LIMIT_TELEGRAM_USER = (15, 60)  # 15 messages / 60 seconds per Telegram user


@asynccontextmanager
async def lifespan(app):
    logger.info("Singh Ji AI Ultra v8.0 HYBRID Starting...")
    sync = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    logger.info(f"Swarm: {sync['active']}/{sync['total']} agents loaded")
    logger.info(f"Active APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}")
    yield
    logger.info("Singh Ji AI Ultra v8.0 Stopped!")

app = FastAPI(title="Singh Ji AI Ultra v8.0 HYBRID", version="8.0.0-hybrid", lifespan=lifespan)

ALLOWED_ORIGINS = [
    "https://jp200883-sudo.github.io",
    "http://localhost:3000",
    "http://localhost:8000",
]
_extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
if _extra_origins:
    ALLOWED_ORIGINS.extend([o.strip() for o in _extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in STRICT_PATH_PREFIXES):
        limited = _is_rate_limited(request, "strict", *RATE_LIMIT_STRICT)
    elif any(path.startswith(p) for p in RATE_LIMITED_PREFIXES):
        limited = _is_rate_limited(request, "global", *RATE_LIMIT_GLOBAL)
    else:
        limited = False
    if limited:
        return JSONResponse(
            {"error": "Rate limit exceeded. Please wait a bit and try again.", "retry_after_seconds": 60},
            status_code=429
        )
    return await call_next(request)

@app.get("/")
@app.head("/")
async def root():
    active = [n for n, i in MODULES.items() if i["active"]]
    return {
        "name": "Singh Ji AI Ultra v8.0 HYBRID",
        "status": "LIVE",
        "total_modules": len(MODULES),
        "active_modules": active,
        "active_count": len(active),
        "agents": SMART_SWARM.get_status(),
        "apis": {k: v for k, v in AVAILABLE_KEYS.items()},
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI v8.0 HYBRID"}

@app.get("/api/status")
async def status():
    active = [n for n, i in MODULES.items() if i["active"]]
    inactive = [{"name": n, "needs_key": i["needs_key"]} for n, i in MODULES.items() if not i["active"]]
    return {
        "name": "Singh Ji AI Ultra v8.0",
        "total_modules": len(MODULES),
        "active_count": len(active),
        "active_modules": active,
        "inactive_modules": inactive,
        "agents": SMART_SWARM.get_status(),
        "apis": AVAILABLE_KEYS,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/check")
async def api_check():
    tests = {
        "OPENWEATHER": ("https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=" + str(OPENWEATHER_API_KEY or ""), {}, "GET"),
        "GROQ": ("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {GROQ_API_KEY or ''}"}, "GET"),
        "GEMINI": ("https://generativelanguage.googleapis.com/v1beta/models?key=" + str(GEMINI_API_KEY or ""), {}, "GET"),
        "TELEGRAM": (f"https://api.telegram.org/bot{TELEGRAM_TOKEN or ''}/getMe", {}, "GET"),
        "SUPABASE": (f"{SUPABASE_URL or ''}/rest/v1/", {"apikey": SUPABASE_SERVICE_KEY or "", "Authorization": f"Bearer {SUPABASE_SERVICE_KEY or ''}"}, "GET"),
        "FACEBOOK": (f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN or ''}", {}, "GET"),
        "YOUTUBE": (f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&maxResults=1&key={YOUTUBE_API_KEY or ''}", {}, "GET"),
        "CURRENTS": (f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY or ''}", {}, "GET"),
        "NEWSDATA": (f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY or ''}&q=test", {}, "GET"),
        "TAVILY": (f"https://api.tavily.com/search?api_key={TAVILY_API_KEY or ''}&query=test&max_results=1", {}, "GET"),
    }
    results = {}
    live = dead = 0
    for name, (url, headers, method) in tests.items():
        if not AVAILABLE_KEYS.get(name):
            results[name] = {"status": "MISSING", "code": None}
            dead += 1
            continue
        try:
            start = time.time()
            r = requests.get(url, headers=headers, timeout=8)
            elapsed = round((time.time() - start) * 1000, 2)
            if r.status_code in [200, 401, 403]:
                results[name] = {"status": "LIVE", "code": r.status_code, "ms": elapsed}
                live += 1
            else:
                results[name] = {"status": "ERROR", "code": r.status_code, "ms": elapsed}
                dead += 1
        except Exception as e:
            results[name] = {"status": "FAIL", "error": str(e)[:50]}
            dead += 1
    return {"timestamp": datetime.now().isoformat(), "summary": {"live": live, "dead": dead, "total": live + dead}, "results": results}

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    cache_key = _cache_key("weather", city)
    cached = _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY missing"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            result = {
                "city": city, "temp": data["main"]["temp"], "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"], "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"], "desc": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"], "source": "OPENWEATHER_LIVE"
            }
            _cache_set(cache_key, result, CACHE_TTL["weather"])
            return result
        return {"error": data.get("message", "Unknown error"), "code": resp.status_code}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/news/latest")
async def news_latest(source: str = "currents"):
    cache_key = _cache_key("news", source)
    cached = _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if source == "currents" and CURRENTS_API_KEY:
        try:
            resp = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}", timeout=10)
            data = resp.json()
            result = {"source": "CURRENTS_LIVE", "news": data.get("news", [])[:10]}
            _cache_set(cache_key, result, CACHE_TTL["news"])
            return result
        except Exception as e:
            return {"error": str(e)}
    if source == "newsdata" and NEWSDATA_API_KEY:
        try:
            resp = requests.get(f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=india", timeout=10)
            data = resp.json()
            result = {"source": "NEWSDATA_LIVE", "news": data.get("results", [])[:10]}
            _cache_set(cache_key, result, CACHE_TTL["news"])
            return result
        except Exception as e:
            return {"error": str(e)}
    return {"error": "No news API key available"}

MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"

@app.get("/api/mandi/{state}")
async def mandi_state(state: str, commodity: str = None, limit: int = 50):
    cache_key = _cache_key("mandi", state, commodity or "all", limit)
    cached = _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if not MANDI_API_KEY:
        return {"error": "MANDI_API_KEY missing"}
    try:
        params = {"api-key": MANDI_API_KEY, "format": "json", "limit": limit, "filters[state.keyword]": state}
        if commodity:
            params["filters[commodity.keyword]"] = commodity
        resp = requests.get(MANDI_BASE_URL, params=params, timeout=15)
        data = resp.json()
        result = {"state": state, "commodity_filter": commodity, "count": len(data.get("records", [])), "records": data.get("records", []), "source": "AGMARKNET_LIVE"}
        _cache_set(cache_key, result, CACHE_TTL["mandi"])
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "PLANT_ID_API missing"}
    data = await request.json()
    image_b64 = data.get("image_base64", "")
    if not image_b64:
        return {"error": "image_base64 required"}
    try:
        resp = requests.post(
            "https://api.plant.id/v3/identification",
            params={"details": "url,common_names,description"},
            headers={"Api-Key": PLANT_ID_API, "Content-Type": "application/json"},
            json={"images": [image_b64]},
            timeout=30
        )
        result = resp.json()
        suggestions = result.get("result", {}).get("classification", {}).get("suggestions", [])
        top = suggestions[0] if suggestions else None
        return {
            "status": "success",
            "is_plant": result.get("result", {}).get("is_plant", {}).get("binary"),
            "top_match": {"name": top.get("name"), "probability": top.get("probability"), "common_names": top.get("details", {}).get("common_names")} if top else None,
            "all_suggestions": suggestions[:5],
            "source": "PLANT.ID_LIVE"
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/chat")
async def ai_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "groq")
    user_id = data.get("user_id", "anonymous")

    personal_kw = ["password", "otp", "secret", "aadhar", "pan", "bank", "cvv", "pin"]
    is_personal = any(kw in prompt.lower() for kw in personal_kw)

    if not is_personal:
        cache_key = _cache_key("ai_chat", model, prompt[:100])
        cached = _cache_get(cache_key)
        if cached:
            cached["source"] = "CACHE"
            return cached

    if model in ["groq", "auto"] and GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]},
                timeout=30
            )
            result = resp.json()
            response_text = result["choices"][0]["message"]["content"]
            result_data = {"status": "success", "model": "groq", "response": response_text, "source": "GROQ_LIVE"}
            if not is_personal:
                _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": response_text, "model": "groq"})
            return result_data
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if model in ["gemini", "auto"] and GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            result_data = {"status": "success", "model": "gemini", "response": text, "source": "GEMINI_LIVE"}
            if not is_personal:
                _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": text, "model": "gemini"})
            return result_data
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")

    if model in ["cerebras", "auto"] and CEREBRAS_API_KEY:
        try:
            resp = requests.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {CEREBRAS_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b", "messages": [{"role": "user", "content": prompt}]},
                timeout=30
            )
            result = resp.json()
            text = result["choices"][0]["message"]["content"]
            return {"status": "success", "model": "cerebras", "response": text, "source": "CEREBRAS_LIVE"}
        except Exception as e:
            logger.warning(f"Cerebras failed: {e}")

    return {"error": "All AI models failed or no API keys"}

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return _memory_get(key)

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(int(time.time())))
    value = data.get("value", data)
    return _memory_save(key, value)

BHASHINI_PIPELINE_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"

@app.get("/api/bhashini/")
async def bhashini_root():
    return {"module": "Bhashini", "status": "active" if AVAILABLE_KEYS["BHASHINI"] else "missing_credentials"}

@app.post("/api/bhashini/translate")
async def bhashini_translate(request: Request):
    if not AVAILABLE_KEYS["BHASHINI"]:
        return {"error": "Bhashini credentials missing"}
    data = await request.json()
    text = data.get("text", "")
    source = data.get("source", "hi")
    target = data.get("target", "en")
    try:
        headers = {"userID": BHASHINI_USER_ID, "ulcaApiKey": BHASHINI_ULCA_API_KEY, "Content-Type": "application/json"}
        payload = {
            "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source, "targetLanguage": target}}}],
            "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
        }
        resp = requests.post(BHASHINI_PIPELINE_URL, headers=headers, json=payload, timeout=15)
        pipeline = resp.json()
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
        compute_url = pipeline["pipelineInferenceAPIEndPoint"]["callbackUrl"]
        key_name = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["name"]
        key_value = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["value"]
        compute_payload = {
            "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source, "targetLanguage": target}, "serviceId": service_id}}],
            "inputData": {"input": [{"source": text}]}
        }
        compute_resp = requests.post(compute_url, headers={key_name: key_value, "Content-Type": "application/json"}, json=compute_payload, timeout=20)
        result = compute_resp.json()
        translated = result["pipelineResponse"][0]["output"][0]["target"]
        return {"status": "success", "original": text, "translated": translated, "source": source, "target": target, "source_api": "BHASHINI_LIVE"}
    except Exception as e:
        return {"error": str(e)}

_whisper_model = None
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Whisper ({WHISPER_MODEL_SIZE})...")
            _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")
            return None
    return _whisper_model

@app.post("/api/whisper/transcribe")
async def whisper_transcribe(request: Request):
    data = await request.json()
    audio_b64 = data.get("audio_base64", "")
    language = data.get("language")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    model = _get_whisper_model()
    if model is None:
        return {"error": "Whisper model not available"}
    try:
        audio_bytes = base64.b64decode(audio_b64)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            segments, info = model.transcribe(tmp.name, language=language)
            transcript = " ".join(seg.text.strip() for seg in segments)
        return {"status": "success", "transcript": transcript, "detected_language": info.language, "language_probability": round(info.language_probability, 3), "source": "WHISPER_LOCAL"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/tts")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text", "")
    lang = data.get("lang", "hi")
    if not text:
        return {"error": "text required"}
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
        return {"status": "success", "audio_base64": audio_b64, "lang": lang, "source": "GTTS_LIVE"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/facebook/status")
async def facebook_status():
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=id,name,followers_count"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {"status": "connected", "page": {"id": data.get("id"), "name": data.get("name"), "followers": data.get("followers_count", 0)}}
        return {"error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/facebook/post")
async def facebook_post(request: Request):
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    data = await request.json()
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/feed"
        payload = {"access_token": FACEBOOK_ACCESS_TOKEN, "message": data.get("message", "")}
        if data.get("link"):
            payload["link"] = data["link"]
        resp = requests.post(url, data=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/instagram/status")
async def instagram_status():
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"error": "INSTAGRAM_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}?access_token={INSTAGRAM_ACCESS_TOKEN}&fields=id,username,followers_count"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {"status": "connected", "account": {"id": data.get("id"), "username": data.get("username"), "followers": data.get("followers_count", 0)}}
        return {"error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/youtube/search")
async def youtube_search(q: str = "", max_results: int = 10):
    if not YOUTUBE_API_KEY:
        return {"error": "YOUTUBE_API_KEY missing"}
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={q}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/search")
async def web_search(q: str = "", max_results: int = 5):
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY missing"}
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": q, "max_results": max_results, "search_depth": "basic"}
        resp = requests.post(url, json=payload, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/retirement/tax-calculate")
async def tax_calculate(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")
    deductions = data.get("deductions", 0)
    if regime == "new":
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = 15000 + (income - 600000) * 0.10
        elif income <= 1200000:
            tax = 45000 + (income - 900000) * 0.15
        elif income <= 1500000:
            tax = 90000 + (income - 1200000) * 0.20
        else:
            tax = 150000 + (income - 1500000) * 0.30
    else:
        taxable = max(0, income - 50000 - deductions)
        if taxable <= 250000:
            tax = 0
        elif taxable <= 500000:
            tax = (taxable - 250000) * 0.05
        elif taxable <= 1000000:
            tax = 12500 + (taxable - 500000) * 0.20
        else:
            tax = 112500 + (taxable - 1000000) * 0.30
    cess = tax * 0.04
    total_tax = tax + cess
    return {"income": income, "regime": regime, "tax": round(tax, 2), "cess": round(cess, 2), "total": round(total_tax, 2), "take_home": round(income - total_tax, 2)}

@app.get("/api/swarm/status")
async def swarm_status():
    return SMART_SWARM.get_status()

@app.post("/api/swarm/sync")
async def swarm_sync():
    result = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    return {"synced": True, **result}

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def _telegram_send_message(chat_id, text, reply_markup=None):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    try:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        resp = requests.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def _telegram_send_voice(chat_id, audio_b64, caption=""):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    try:
        audio_bytes = base64.b64decode(audio_b64)
        files = {"voice": ("voice.mp3", io.BytesIO(audio_bytes), "audio/mpeg")}
        data = {"chat_id": chat_id, "caption": caption}
        resp = requests.post(f"{TELEGRAM_API_BASE}/sendVoice", data=data, files=files, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "Weather", "callback_data": "weather"}, {"text": "News", "callback_data": "news"}],
        [{"text": "Mandi Bhav", "callback_data": "mandi"}, {"text": "AI Chat", "callback_data": "ai_chat"}],
        [{"text": "Voice", "callback_data": "voice"}, {"text": "Status", "callback_data": "status"}],
        [{"text": "Tax Calc", "callback_data": "tax"}, {"text": "Plant ID", "callback_data": "plant"}],
    ]
}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        if "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            query_data = callback["data"]

            if query_data == "status":
                status = SMART_SWARM.get_status()
                text = "Status\n\n"
                text += f"Agents: {status['currently_loaded']}/330\n"
                text += f"Active: {status['active_running']}\n"
                text += f"Idle: {status['idle']}\n"
                text += f"APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}"
                _telegram_send_message(chat_id, text)
            elif query_data == "weather":
                _telegram_send_message(chat_id, "Weather\n\nCity batao!")
            elif query_data == "news":
                if NEWSDATA_API_KEY:
                    try:
                        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=india&size=5"
                        resp = requests.get(url, timeout=10)
                        news_data = resp.json()
                        articles = news_data.get("results", [])[:5]
                        text = "News\n\n"
                        for i, article in enumerate(articles, 1):
                            text += f"{i}. {article.get('title', 'No title')}\n"
                            desc = article.get('description', 'No description')[:100]
                            text += f"   {desc}...\n\n"
                        _telegram_send_message(chat_id, text)
                    except Exception as e:
                        _telegram_send_message(chat_id, f"News error: {str(e)[:100]}")
                else:
                    _telegram_send_message(chat_id, "News API key missing")
            elif query_data == "mandi":
                _telegram_send_message(chat_id, "Mandi Bhav\n\nState batao!")
            elif query_data == "ai_chat":
                _telegram_send_message(chat_id, "AI Chat\n\nKuch bhi poochho!")
            elif query_data == "voice":
                _telegram_send_message(chat_id, "Voice\n\nVoice message bhejo!")
            elif query_data == "tax":
                _telegram_send_message(chat_id, "Tax Calculator\n\nIncome batao!")
            elif query_data == "plant":
                _telegram_send_message(chat_id, "Plant ID\n\nPlant ki photo bhejo!")

            return {"status": "ok"}

        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]

        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {"language": "hi", "location": None}

        if _rate_check(f"tg_user:{user_id}", *RATE_LIMIT_TELEGRAM_USER):
            _telegram_send_message(chat_id, "Thoda slow karo! 1 minute mein try karo.")
            return {"status": "ok"}

        # Voice messages have no "text" field, so they must be handled
        # here, BEFORE the text-based if/elif chain below — every branch
        # of that chain ends in an early return, so voice would never be
        # reached if checked after it.
        if "voice" in message:
            voice = message["voice"]
            file_id = voice["file_id"]
            try:
                file_resp = requests.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}", timeout=10)
                file_data = file_resp.json()
                if file_data.get("ok"):
                    file_path = file_data["result"]["file_path"]
                    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                    audio_resp = requests.get(file_url, timeout=15)
                    audio_bytes = audio_resp.content
                    model = _get_whisper_model()
                    if model:
                        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as tmp:
                            tmp.write(audio_bytes)
                            tmp.flush()
                            segments, info = model.transcribe(tmp.name)
                            transcript = " ".join(seg.text.strip() for seg in segments)
                        transcript_msg = "Transcript:" + chr(10) + transcript + chr(10) + chr(10) + "AI soch raha hai..."
                        _telegram_send_message(chat_id, transcript_msg)
                        ai_text = None
                        if GROQ_API_KEY:
                            ai_resp = requests.post(
                                "https://api.groq.com/openai/v1/chat/completions",
                                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                                json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": transcript}]},
                                timeout=30
                            )
                            ai_result = ai_resp.json()
                            ai_text = ai_result["choices"][0]["message"]["content"]
                            try:
                                from gtts import gTTS
                                tts_text = ai_text[:500] if len(ai_text) > 500 else ai_text
                                tts = gTTS(text=tts_text, lang="hi", slow=False)
                                mp3_fp = io.BytesIO()
                                tts.write_to_fp(mp3_fp)
                                mp3_fp.seek(0)
                                tts_b64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
                                _telegram_send_voice(chat_id, tts_b64, "AI Response (Hindi)")
                            except Exception:
                                ai_msg = "AI Response:" + chr(10) + chr(10) + ai_text
                                _telegram_send_message(chat_id, ai_msg)
                        _memory_save(f"telegram_voice:{user_id}:{int(time.time())}", {"transcript": transcript, "response": ai_text})
                    else:
                        _telegram_send_message(chat_id, "Whisper model not available")
                else:
                    _telegram_send_message(chat_id, "Could not download voice file")
            except Exception as e:
                logger.error(f"Voice processing error: {e}")
                err_msg = "Voice processing error: " + str(e)[:100]
                _telegram_send_message(chat_id, err_msg)
            return {"status": "ok"}

        if text == "/start":
            welcome = "Welcome to Singh Ji AI Ultra v8.0!\n\nMain aapka AI assistant hoon.\n"
            _telegram_send_message(chat_id, welcome, MAIN_KEYBOARD)
            return {"status": "ok"}

        elif text == "/help":
            help_text = "Commands\n\n/start\n/weather city\n/news\n/mandi state\n/tax income\n/status\n/ai question"
            _telegram_send_message(chat_id, help_text)
            return {"status": "ok"}

        elif text == "/status":
            status = SMART_SWARM.get_status()
            status_text = "Status\n\n"
            status_text += "Total Agents: 330\n"
            status_text += f"Loaded: {status['currently_loaded']}\n"
            status_text += f"Active: {status['active_running']}\n"
            status_text += f"Idle: {status['idle']}\n"
            api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
            status_text += f"Active APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
            status_text += f"Time: {datetime.now().strftime('%H:%M:%S')}"
            _telegram_send_message(chat_id, status_text)
            return {"status": "ok"}

        elif text.startswith("/weather "):
            city = text.replace("/weather ", "").strip()
            if OPENWEATHER_API_KEY:
                try:
                    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                    resp = requests.get(url, timeout=10)
                    data = resp.json()
                    if resp.status_code == 200:
                        weather_text = f"Weather in {city}\n\n"
                        weather_text += f"Temperature: {data['main']['temp']}C\n"
                        weather_text += f"Feels like: {data['main']['feels_like']}C\n"
                        weather_text += f"Humidity: {data['main']['humidity']}%\n"
                        weather_text += f"Wind: {data['wind']['speed']} m/s\n"
                        weather_text += f"{data['weather'][0]['description'].title()}"
                        _telegram_send_message(chat_id, weather_text)
                    else:
                        _telegram_send_message(chat_id, f"City not found: {city}")
                except Exception as e:
                    _telegram_send_message(chat_id, f"Error: {str(e)[:100]}")
            else:
                _telegram_send_message(chat_id, "Weather API key missing")
            return {"status": "ok"}

        elif text == "/news":
            if NEWSDATA_API_KEY:
                try:
                    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=india&size=5"
                    resp = requests.get(url, timeout=10)
                    news_data = resp.json()
                    articles = news_data.get("results", [])[:5]
                    news_text = "Latest News\n\n"
                    for i, article in enumerate(articles, 1):
                        news_text += f"{i}. {article.get('title', 'No title')}\n"
                        desc = article.get('description', 'No description')[:80]
                        news_text += f"   {desc}...\n\n"
                    _telegram_send_message(chat_id, news_text)
                except Exception as e:
                    _telegram_send_message(chat_id, f"News error: {str(e)[:100]}")
            else:
                _telegram_send_message(chat_id, "News API key missing")
            return {"status": "ok"}

        elif text.startswith("/mandi "):
            state = text.replace("/mandi ", "").strip()
            if MANDI_API_KEY:
                try:
                    params = {"api-key": MANDI_API_KEY, "format": "json", "limit": 10, "filters[state.keyword]": state}
                    resp = requests.get(MANDI_BASE_URL, params=params, timeout=15)
                    data = resp.json()
                    records = data.get("records", [])
                    mandi_text = f"Mandi Bhav - {state}\n\n"
                    for i, record in enumerate(records[:5], 1):
                        mandi_text += f"{i}. {record.get('commodity', 'Unknown')}\n"
                        mandi_text += f"   Rs {record.get('modal_price', 'N/A')}/quintal\n"
                        mandi_text += f"   {record.get('district', 'N/A')}, {record.get('market', 'N/A')}\n\n"
                    _telegram_send_message(chat_id, mandi_text)
                except Exception as e:
                    _telegram_send_message(chat_id, f"Error: {str(e)[:100]}")
            else:
                _telegram_send_message(chat_id, "Mandi API key missing")
            return {"status": "ok"}

        elif text.startswith("/tax "):
            try:
                income = float(text.replace("/tax ", "").strip())
                if income <= 300000:
                    tax = 0
                elif income <= 600000:
                    tax = (income - 300000) * 0.05
                elif income <= 900000:
                    tax = 15000 + (income - 600000) * 0.10
                elif income <= 1200000:
                    tax = 45000 + (income - 900000) * 0.15
                elif income <= 1500000:
                    tax = 90000 + (income - 1200000) * 0.20
                else:
                    tax = 150000 + (income - 1500000) * 0.30
                cess = tax * 0.04
                total = tax + cess
                tax_text = "Tax Calculation\n\n"
                tax_text += f"Income: Rs {income:,.0f}\n"
                tax_text += f"Tax: Rs {tax:,.2f}\n"
                tax_text += f"Health Cess (4%): Rs {cess:,.2f}\n"
                tax_text += f"Total Tax: Rs {total:,.2f}\n"
                tax_text += f"Take Home: Rs {income - total:,.2f}"
                _telegram_send_message(chat_id, tax_text)
            except Exception:
                _telegram_send_message(chat_id, "Invalid income. Example: /tax 500000")
            return {"status": "ok"}

        elif text.startswith("/ai "):
            prompt = text.replace("/ai ", "").strip()
            if GROQ_API_KEY:
                try:
                    resp = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]},
                        timeout=30
                    )
                    result = resp.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    if len(ai_response) > 4000:
                        ai_response = ai_response[:4000] + "...\n\n(Truncated)"
                    _telegram_send_message(chat_id, f"AI Response:\n\n{ai_response}")
                    _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": ai_response})
                except Exception as e:
                    _telegram_send_message(chat_id, f"AI Error: {str(e)[:100]}")
            else:
                _telegram_send_message(chat_id, "Groq API key missing")
            return {"status": "ok"}

        elif text.startswith("/broadcast "):
            admin_id = int(os.getenv("ADMIN_USER_ID", "0"))
            if user_id != admin_id:
                _telegram_send_message(chat_id, "Admin only command")
                return {"status": "ok"}
            broadcast_text = text.replace("/broadcast ", "").strip()
            sent = 0
            for uid in USER_PREFERENCES.keys():
                _telegram_send_message(uid, f"Broadcast\n\n{broadcast_text}")
                sent += 1
            _telegram_send_message(chat_id, f"Broadcast sent to {sent} users")
            return {"status": "ok"}

        else:
            if GROQ_API_KEY and text:
                try:
                    resp = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": text}]},
                        timeout=30
                    )
                    result = resp.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    if len(ai_response) > 4000:
                        ai_response = ai_response[:4000] + "...\n\n(Truncated)"
                    _telegram_send_message(chat_id, ai_response)
                    _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {"prompt": text, "response": ai_response})
                except Exception as e:
                    _telegram_send_message(chat_id, f"AI Error: {str(e)[:100]}")
            return {"status": "ok"}

    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return {"status": "error", "message": str(e)}

NEWS_SCHEDULE_ACTIVE = False

@app.post("/api/news/schedule/start")
async def start_news_scheduler(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    global NEWS_SCHEDULE_ACTIVE
    NEWS_SCHEDULE_ACTIVE = True
    asyncio.create_task(_news_scheduler_task())
    return {"status": "News scheduler started", "schedule": "4:00 AM daily"}

async def _news_scheduler_task():
    while NEWS_SCHEDULE_ACTIVE:
        now = datetime.now()
        next_run = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"News scheduler: Next run in {wait_seconds/3600:.1f} hours")
        await asyncio.sleep(min(wait_seconds, 3600))
        now = datetime.now()
        if now.hour == 4 and now.minute < 5:
            logger.info("Running 4 AM news broadcast...")
            try:
                if NEWSDATA_API_KEY:
                    url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q=india&size=10"
                    resp = requests.get(url, timeout=15)
                    news_data = resp.json()
                    articles = news_data.get("results", [])[:5]
                    news_text = "4 AM Daily News\n\nSingh Ji AI\n"
                    for i, article in enumerate(articles, 1):
                        news_text += f"\n{i}. {article.get('title', 'No title')}\n"
                        desc = article.get('description', 'No description')[:100]
                        news_text += f"   {desc}...\n"
                    for uid in USER_PREFERENCES.keys():
                        try:
                            _telegram_send_message(uid, news_text)
                        except Exception:
                            pass
                    logger.info(f"News sent to {len(USER_PREFERENCES)} users")
            except Exception as e:
                logger.error(f"News scheduler error: {e}")

@app.get("/api/admin/")
async def admin_root(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return {
        "module": "Admin Panel",
        "total_modules": len(MODULES),
        "active_modules": [n for n, i in MODULES.items() if i["active"]],
        "agents": SMART_SWARM.get_status(),
        "apis": AVAILABLE_KEYS,
        "users": len(USER_PREFERENCES),
        "memory_ram": len(MEMORY_STORE),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin/users")
async def admin_users(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return {"users": USER_PREFERENCES, "count": len(USER_PREFERENCES)}

@app.post("/api/admin/broadcast")
async def admin_broadcast(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    data = await request.json()
    message = data.get("message", "")
    sent = 0
    for uid in USER_PREFERENCES.keys():
        _telegram_send_message(uid, f"Admin Broadcast\n\n{message}")
        sent += 1
    return {"broadcast": True, "sent_to": sent}

@app.get("/api/payment/")
async def payment_root():
    return {"module": "Payment Gateway", "status": "ON_HOLD" if not AVAILABLE_KEYS["RAZORPAY"] else "ACTIVE", "upi_id": "jp200883@sbi", "note": "Activate at 1000+ daily users"}

@app.post("/api/payment/create-order")
async def payment_create_order(request: Request):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return {"error": "Razorpay keys missing"}
    data = await request.json()
    amount = data.get("amount", 0)
    currency = data.get("currency", "INR")
    receipt = data.get("receipt", f"order_{int(time.time())}")
    try:
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order = client.order.create({"amount": amount, "currency": currency, "receipt": receipt, "payment_capture": 1})
        return {"status": "success", "order": order, "source": "RAZORPAY_LIVE"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/gmail/")
async def gmail_root():
    return {"module": "Gmail", "status": "active" if AVAILABLE_KEYS["GMAIL"] else "missing_credentials"}

@app.get("/api/gmail/auth-url")
async def gmail_auth_url():
    if not GMAIL_CLIENT_ID:
        return {"error": "GMAIL_CLIENT_ID missing"}
    redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "https://singhji-ai.github.io/oauth/callback")
    scope = "https://www.googleapis.com/auth/gmail.send"
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GMAIL_CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&access_type=offline"
    return {"auth_url": url}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
