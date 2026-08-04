import os
import sys
import json
import time
import asyncio
import hashlib
import base64
import io
import tempfile
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict, deque
from contextlib import asynccontextmanager

import httpx
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

# ==========================================
# 🦁 SINGH JI AI ULTRA v8.3 FINAL
# ALL 42+ MODULES UNIFIED
# Date: 04 August 2026
# Backend: Railway (PRIMARY)
# AWS Backup: 15.134.36.7
# ==========================================
# LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout  # bina isके default stderr par jaata hai, Railway usse "error" maan leta hai
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

# ==========================================
# ENVIRONMENT VARIABLES VALIDATION
# ==========================================
def validate_env_vars():
    """Check if all required environment variables are set"""
    required = ["TELEGRAM_TOKEN", "APP_URL"]
    optional = [
        "ADMIN_API_KEY", "CEREBRAS_API_KEY", "CF_API_TOKEN", "CURRENTS_API_KEY",
        "DATABASE_URL", "FACEBOOK_ACCESS_TOKEN", "FACEBOOK_PAGE_ID",
        "GEMINI_API_KEY", "GROQ_API_KEY", "HUGGINGFACE_TOKEN",
        "MANDI_API_KEY", "NEWSDATA_API_KEY", "OPENWEATHER_API_KEY",
        "PLANT_ID_API", "RAPIDAPI_KEY", "RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET",
        "SUPABASE_SERVICE_KEY", "SUPABASE_URL", "TAVILY_API_KEY",
        "TWILIO_SID", "TWILIO_TOKEN", "YOUTUBE_API_KEY",
        "BHASHINI_USER_ID", "BHASHINI_ULCA_API_KEY", "BHASHINI_INFERENCE_API_KEY",
        "GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "INSTAGRAM_ACCESS_TOKEN",
        "INSTAGRAM_BUSINESS_ID", "ADMIN_USER_ID", "SEEDANCE_API_KEY",
        "KLING_API_KEY", "HAILUO_API_KEY", "LUMA_API_KEY",
        "PIKA_API_KEY", "VEO_API_KEY"
    ]

    missing_required = [v for v in required if not os.getenv(v)]
    if missing_required:
        raise ValueError(f"Missing required env vars: {', '.join(missing_required)}")

    logger.info(f"✅ All required environment variables present")
    logger.info(f"📊 Optional keys: {sum(1 for v in optional if os.getenv(v))}/{len(optional)} present")

validate_env_vars()

# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================
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
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY")
KLING_API_KEY = os.getenv("KLING_API_KEY")
HAILUO_API_KEY = os.getenv("HAILUO_API_KEY")
LUMA_API_KEY = os.getenv("LUMA_API_KEY")
PIKA_API_KEY = os.getenv("PIKA_API_KEY")
VEO_API_KEY = os.getenv("VEO_API_KEY")
APP_URL = os.getenv("APP_URL", "").rstrip('/')

# ==========================================
# CONSTANTS
# ==========================================
MAX_B64_BYTES = 10 * 1024 * 1024
MAX_MEMORY_SIZE = 5000

MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"

# State name normalization for Mandi API
STATE_MAP = {
    "up": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh", "uttarpradesh": "Uttar Pradesh",
    "mp": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh", "madhyapradesh": "Madhya Pradesh",
    "bihar": "Bihar", "rajasthan": "Rajasthan", "rajsthan": "Rajasthan",
    "punjab": "Punjab", "haryana": "Haryana",
    "maharashtra": "Maharashtra", "gujarat": "Gujarat",
    "wb": "West Bengal", "west bengal": "West Bengal", "westbengal": "West Bengal",
    "odisha": "Odisha", "orissa": "Odisha",
    "telangana": "Telangana", "andhra": "Andhra Pradesh", "andhra pradesh": "Andhra Pradesh",
    "karnataka": "Karnataka", "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
    "kerala": "Kerala", "jharkhand": "Jharkhand",
    "chhattisgarh": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
    "uttarakhand": "Uttarakhand", "uttranchal": "Uttarakhand",
    "himachal": "Himachal Pradesh", "himachal pradesh": "Himachal Pradesh",
    "assam": "Assam", "tripura": "Tripura", "meghalaya": "Meghalaya",
}

def _normalize_state(state: str) -> str:
    """Convert short state names to full names for AGMARKNET API"""
    key = state.strip().lower()
    return STATE_MAP.get(key, state.strip().title())


RATE_LIMIT_GLOBAL = (
    int(os.getenv("RATE_LIMIT_GLOBAL_CALLS", 30)),
    int(os.getenv("RATE_LIMIT_GLOBAL_WINDOW", 60))
)
RATE_LIMIT_STRICT = (
    int(os.getenv("RATE_LIMIT_STRICT_CALLS", 5)),
    int(os.getenv("RATE_LIMIT_STRICT_WINDOW", 60))
)
RATE_LIMIT_TELEGRAM_USER = (
    int(os.getenv("RATE_LIMIT_TELEGRAM_CALLS", 10)),
    int(os.getenv("RATE_LIMIT_TELEGRAM_WINDOW", 60))
)

CACHE_TTL = {
    "weather": int(os.getenv("CACHE_TTL_WEATHER", 1800)),
    "mandi": int(os.getenv("CACHE_TTL_MANDI", 21600)),
    "ai_chat": int(os.getenv("CACHE_TTL_AI", 3600)),
    "news": int(os.getenv("CACHE_TTL_NEWS", 900)),
    "default": int(os.getenv("CACHE_TTL_DEFAULT", 300))
}

# ==========================================
# AVAILABLE KEYS STATUS
# ==========================================
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
    "BLUESKY": bool(os.getenv("BLUESKY_HANDLE") and os.getenv("BLUESKY_APP_PASSWORD")),
}

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_CLIENT = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("✅ Supabase connected successfully")
except Exception as e:
    logger.warning(f"⚠️ Supabase init failed: {e}")

# ==========================================
# GLOBAL VARIABLES
# ==========================================
HTTP_CLIENT = None
MASTER_SCHEDULER = None
MEMORY_STORE = {}
USER_PREFERENCES = {}
_whisper_model = None
_rate_lock = threading.Lock()
_rate_buckets = defaultdict(deque)

# ==========================================
# CACHE FUNCTIONS
# ==========================================
def _cache_key(prefix, *args):
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()

def _cache_get_sync(key):
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

async def _cache_get(key):
    return await run_in_threadpool(_cache_get_sync, key)

def _cache_set_sync(key, value, ttl=None):
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

async def _cache_set(key, value, ttl=None):
    await run_in_threadpool(_cache_set_sync, key, value, ttl)

def _check_memory_limit():
    if len(MEMORY_STORE) > MAX_MEMORY_SIZE:
        keys_to_remove = list(MEMORY_STORE.keys())[:int(MAX_MEMORY_SIZE * 0.2)]
        for k in keys_to_remove:
            del MEMORY_STORE[k]
        logger.info(f"Memory cleaned: removed {len(keys_to_remove)} old entries")

# ==========================================
# MEMORY FUNCTIONS
# ==========================================
def _memory_save_sync(key, value, table="memory_store"):
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

async def _memory_save(key, value, table="memory_store"):
    return await run_in_threadpool(_memory_save_sync, key, value, table)

def _memory_get_sync(key, table="memory_store"):
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

async def _memory_get(key, table="memory_store"):
    return await run_in_threadpool(_memory_get_sync, key, table)

def _load_user_preferences_sync() -> Dict[int, Any]:
    loaded: Dict[int, Any] = {}
    if not SUPABASE_CLIENT:
        logger.warning("⚠️ Supabase not connected — subscribers will load from new messages")
        return loaded
    try:
        resp = SUPABASE_CLIENT.table("user_memory").select("*").execute()
        for row in (resp.data or []):
            key = row.get("key", "")
            if not key.startswith("user_pref:"):
                continue
            try:
                uid = int(key.split(":", 1)[1])
            except (IndexError, ValueError):
                continue
            loaded[uid] = row.get("value") or {"language": "hi", "location": None}
        logger.info(f"✅ Loaded {len(loaded)} subscribers from Supabase")
    except Exception as e:
        logger.error(f"❌ User preferences reload failed: {e}")
    return loaded

# ==========================================
# RATE LIMITING
# ==========================================
def _client_ip(request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _rate_check(key: str, max_calls: int, window_seconds: int) -> bool:
    now = time.time()
    with _rate_lock:
        dq = _rate_buckets[key]
        while dq and dq[0] < now - window_seconds:
            dq.popleft()
        if len(dq) >= max_calls:
            return True
        dq.append(now)
        return False

def _is_rate_limited(request, bucket: str, max_calls: int, window_seconds: int) -> bool:
    ip = _client_ip(request)
    return _rate_check(f"{bucket}:{ip}", max_calls, window_seconds)

# ==========================================
# TELEGRAM HELPERS
# ==========================================
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def _telegram_send_message(chat_id, text, reply_markup=None, parse_mode=None):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            payload = {"chat_id": chat_id, "text": text}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            resp = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
            result = resp.json()
            if result.get("ok"):
                return result
            else:
                error_msg = result.get("description", "Unknown error")
                if "Too Many Requests" in error_msg and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error(f"❌ Telegram send failed: {error_msg}")
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            logger.error(f"❌ Telegram send exception: {e}")
            return {"error": str(e)}
    return {"error": "Max retries exceeded"}

async def _telegram_send_voice(chat_id, audio_b64, caption=""):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    try:
        audio_bytes = base64.b64decode(audio_b64)
        files = {"voice": ("voice.mp3", io.BytesIO(audio_bytes), "audio/mpeg")}
        data = {"chat_id": chat_id, "caption": caption}
        resp = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/sendVoice", data=data, files=files, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

async def _check_webhook_config():
    if not TELEGRAM_TOKEN or not HTTP_CLIENT:
        return
    try:
        resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=10)
        info = resp.json().get("result", {})
        url = info.get("url", "")
        logger.info(f"🔍 Current webhook URL: {url or '(none)'}")
        correct_url = f"{APP_URL}/telegram/webhook"
        if url.rstrip("/") != correct_url:
            logger.warning(f"⚠️ Webhook points to {url} but should be {correct_url}")
            await _ensure_correct_webhook()
    except Exception as e:
        logger.warning(f"⚠️ Webhook check failed: {e}")

async def _ensure_correct_webhook():
    if not TELEGRAM_TOKEN or not HTTP_CLIENT or not APP_URL:
        logger.warning("⚠️ Cannot set webhook: missing TELEGRAM_TOKEN or APP_URL")
        return
    correct_url = f"{APP_URL}/telegram/webhook"
    try:
        set_resp = await HTTP_CLIENT.get(
            f"{TELEGRAM_API_BASE}/setWebhook",
            params={"url": correct_url},
            timeout=10
        )
        result = set_resp.json()
        if result.get("ok"):
            logger.info(f"✅ Webhook set to: {correct_url}")
        else:
            logger.error(f"❌ Webhook set failed: {result}")
    except Exception as e:
        logger.error(f"❌ Webhook set error: {e}")

# ==========================================
# MODULES IMPORT — SAFE (individual try/except)
# ==========================================
_imported_modules = {}
_import_errors = []

# --- CORE MODULES ---
try:
    from modules.kisaan_doctor.handler import router as kisaan_router
    _imported_modules["kisaan_doctor"] = "router"
except Exception as e:
    logger.warning(f"⚠️ kisaan_doctor: {e}"); _import_errors.append("kisaan_doctor")
    kisaan_router = None

try:
    from modules.banking.handler import handler as banking_handler
    _imported_modules["banking"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ banking: {e}"); _import_errors.append("banking")
    banking_handler = None

try:
    from modules.currency.handler import router as currency_router, singhji_currency
    _imported_modules["currency"] = "router"
except Exception as e:
    logger.warning(f"⚠️ currency: {e}"); _import_errors.append("currency")
    currency_router = None; singhji_currency = None

try:
    from modules.aavishkar.handler import router as aavishkar_router
    _imported_modules["aavishkar"] = "router"
except Exception as e:
    logger.warning(f"⚠️ aavishkar: {e}"); _import_errors.append("aavishkar")
    aavishkar_router = None

try:
    from modules.goldrate.handler import router as goldrate_router, gold_rate_city, get_gold_silver_summary
    _imported_modules["goldrate"] = "router"
except Exception as e:
    logger.warning(f"⚠️ goldrate: {e}"); _import_errors.append("goldrate")
    goldrate_router = None; gold_rate_city = None; get_gold_silver_summary = None

try:
    from modules.fuel.handler import router as fuel_router, fuel_price
    _imported_modules["fuel"] = "router"
except Exception as e:
    logger.warning(f"⚠️ fuel: {e}"); _import_errors.append("fuel")
    fuel_router = None; fuel_price = None

try:
    from modules.horoscope.handler import get_horoscope, get_all_horoscopes, format_telegram as _format_horoscope_telegram
    _imported_modules["horoscope"] = "functions"
except Exception as e:
    logger.warning(f"⚠️ horoscope: {e}"); _import_errors.append("horoscope")
    get_horoscope = None; get_all_horoscopes = None; _format_horoscope_telegram = None

try:
    from modules.language.handler import LanguageModule
    _imported_modules["language"] = "class"
except Exception as e:
    logger.warning(f"⚠️ language: {e}"); _import_errors.append("language")
    LanguageModule = None

try:
    from modules.emergency.handler import EMERGENCY_DATA
    _imported_modules["emergency"] = "data"
except Exception as e:
    logger.warning(f"⚠️ emergency: {e}"); _import_errors.append("emergency")
    EMERGENCY_DATA = {}

try:
    from modules.govt.handler import GOVT_DATA
    _imported_modules["govt"] = "data"
except Exception as e:
    logger.warning(f"⚠️ govt: {e}"); _import_errors.append("govt")
    GOVT_DATA = {}

try:
    from modules.trishul.handler import router as trishul_router
    _imported_modules["trishul"] = "router"
except Exception as e:
    logger.warning(f"⚠️ trishul: {e}"); _import_errors.append("trishul")
    trishul_router = None

try:
    from modules.scheme_swarm.api_routes import router as scheme_swarm_router, engine as scheme_engine
    from modules.scheme_swarm.eligibility import UserProfile
    _imported_modules["scheme_swarm"] = "router"
except Exception as e:
    logger.warning(f"⚠️ scheme_swarm: {e}"); _import_errors.append("scheme_swarm")
    scheme_swarm_router = None; scheme_engine = None; UserProfile = None

try:
    from modules.pani.handler import handler as pani_handler
    _imported_modules["pani"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ pani: {e}"); _import_errors.append("pani")
    pani_handler = None

try:
    from modules.sewer.handler import handler as sewer_handler
    _imported_modules["sewer"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ sewer: {e}"); _import_errors.append("sewer")
    sewer_handler = None

try:
    from modules.upi.handler import handler as upi_handler
    _imported_modules["upi"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ upi: {e}"); _import_errors.append("upi")
    upi_handler = None

try:
    from modules.guard_agent.handler import router as guard_router
    _imported_modules["guard_agent"] = "router"
except Exception as e:
    logger.warning(f"⚠️ guard_agent: {e}"); _import_errors.append("guard_agent")
    guard_router = None

try:
    from modules.oauth_connector.handler import router as oauth_router
    _imported_modules["oauth_connector"] = "router"
except Exception as e:
    logger.warning(f"⚠️ oauth_connector: {e}"); _import_errors.append("oauth_connector")
    oauth_router = None

try:
    from modules.social_agent.handler import router as social_router
    import modules.social_agent.core as social_core
    _imported_modules["social_agent"] = "router"
except Exception as e:
    logger.warning(f"⚠️ social_agent: {e}"); _import_errors.append("social_agent")
    social_router = None; social_core = None

try:
    from modules.oauth_connector.router import SmartVideoRouter
    from modules.oauth_connector.base import PlatformCredentials, VideoGenerationRequest
    _imported_modules["oauth_connector_router"] = "class"
except Exception as e:
    logger.warning(f"⚠️ oauth_connector.router: {e}"); _import_errors.append("oauth_connector_router")
    SmartVideoRouter = None; PlatformCredentials = None; VideoGenerationRequest = None

try:
    from modules.search.handler import handler as search_handler
    _imported_modules["search"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ search: {e}"); _import_errors.append("search")
    search_handler = None

try:
    from modules.rozgar.handler import handler as rozgar_handler
    from modules.rozgar import handler as rozgar_module
    _imported_modules["rozgar"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ rozgar: {e}"); _import_errors.append("rozgar")
    rozgar_handler = None; rozgar_module = None

try:
    from modules.news.handler import router as news_router
    _imported_modules["news"] = "router"
except Exception as e:
    logger.warning(f"⚠️ news: {e}"); _import_errors.append("news")
    news_router = None

try:
    from miniprogram.portal import router as miniprogram_router
    _imported_modules["miniprogram"] = "router"
except Exception as e:
    logger.warning(f"⚠️ miniprogram: {e}"); _import_errors.append("miniprogram")
    miniprogram_router = None

try:
    from modules.mandi.handler import handler as mandi_handler
    _imported_modules["mandi"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ mandi: {e}"); _import_errors.append("mandi")
    mandi_handler = None

# --- NEW MODULES v8.3 ---
try:
    from modules.ai_chat.handler import handler as ai_chat_handler
    _imported_modules["ai_chat"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ ai_chat: {e}"); _import_errors.append("ai_chat")
    ai_chat_handler = None

try:
    from modules.analytics.handler import handler as analytics_handler
    _imported_modules["analytics"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ analytics: {e}"); _import_errors.append("analytics")
    analytics_handler = None

try:
    from modules.currents_api.handler import handler as currents_handler
    _imported_modules["currents_api"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ currents_api: {e}"); _import_errors.append("currents_api")
    currents_handler = None

try:
    from modules.daily_report.handler import handler as daily_report_handler
    _imported_modules["daily_report"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ daily_report: {e}"); _import_errors.append("daily_report")
    daily_report_handler = None

try:
    from modules.init.handler import handler as init_handler
    _imported_modules["init"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ init: {e}"); _import_errors.append("init")
    init_handler = None

try:
    from modules.language_hub.handler import handler as language_hub_handler
    _imported_modules["language_hub"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ language_hub: {e}"); _import_errors.append("language_hub")
    language_hub_handler = None

try:
    from modules.meta_agent.handler import handler as meta_handler
    _imported_modules["meta_agent"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ meta_agent: {e}"); _import_errors.append("meta_agent")
    meta_handler = None

try:
    from modules.newsdata.handler import router as newsdata_router
    _imported_modules["newsdata"] = "router"
except Exception as e:
    logger.warning(f"⚠️ newsdata: {e}"); _import_errors.append("newsdata")
    newsdata_router = None

try:
    from modules.plant_id.handler import handler as plant_id_handler
    _imported_modules["plant_id"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ plant_id: {e}"); _import_errors.append("plant_id")
    plant_id_handler = None

try:
    from modules.singhji_tv.handler import handler as singhji_tv_handler
    _imported_modules["singhji_tv"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ singhji_tv: {e}"); _import_errors.append("singhji_tv")
    singhji_tv_handler = None

try:
    from modules.supabase_memory.handler import handler as supabase_memory_handler
    _imported_modules["supabase_memory"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ supabase_memory: {e}"); _import_errors.append("supabase_memory")
    supabase_memory_handler = None

# FIX: supreme_agent exports router, not handler
try:
    from modules.supreme_agent.handler import router as supreme_router
    _imported_modules["supreme_agent"] = "router"
except Exception as e:
    logger.warning(f"⚠️ supreme_agent: {e}"); _import_errors.append("supreme_agent")
    supreme_router = None

try:
    from modules.telegram.handler import handler as telegram_handler
    _imported_modules["telegram"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ telegram: {e}"); _import_errors.append("telegram")
    telegram_handler = None

try:
    from modules.trolley.handler import handler as trolley_handler
    _imported_modules["trolley"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ trolley: {e}"); _import_errors.append("trolley")
    trolley_handler = None

try:
    from modules.voice.handler import handler as voice_handler
    _imported_modules["voice"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ voice: {e}"); _import_errors.append("voice")
    voice_handler = None

try:
    from modules.voice_cmd.handler import handler as voice_cmd_handler
    _imported_modules["voice_cmd"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ voice_cmd: {e}"); _import_errors.append("voice_cmd")
    voice_cmd_handler = None

try:
    from modules.voice_tts.handler import handler as voice_tts_handler
    _imported_modules["voice_tts"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ voice_tts: {e}"); _import_errors.append("voice_tts")
    voice_tts_handler = None

try:
    from modules.weather.handler import router as weather_router
    _imported_modules["weather"] = "router"
except Exception as e:
    logger.warning(f"⚠️ weather: {e}"); _import_errors.append("weather")
    weather_router = None

try:
    from modules.whatsapp.handler import handler as whatsapp_handler
    _imported_modules["whatsapp"] = "handler"
except Exception as e:
    logger.warning(f"⚠️ whatsapp: {e}"); _import_errors.append("whatsapp")
    whatsapp_handler = None

# --- ROOT FILES ---
try:
    import agent_swarm_system
    _imported_modules["agent_swarm_system"] = "module"
except Exception as e:
    logger.warning(f"⚠️ agent_swarm_system: {e}")
    agent_swarm_system = None

try:
    import auto_account
    _imported_modules["auto_account"] = "module"
except Exception as e:
    logger.warning(f"⚠️ auto_account: {e}")
    auto_account = None

try:
    import auto_monetize
    _imported_modules["auto_monetize"] = "module"
except Exception as e:
    logger.warning(f"⚠️ auto_monetize: {e}")
    auto_monetize = None

try:
    import facebook_long_token
    _imported_modules["facebook_long_token"] = "module"
except Exception as e:
    logger.warning(f"⚠️ facebook_long_token: {e}")
    facebook_long_token = None

try:
    import singhji_visual
    _imported_modules["singhji_visual"] = "module"
except Exception as e:
    logger.warning(f"⚠️ singhji_visual: {e}")
    singhji_visual = None

try:
    import trend_analysis
    _imported_modules["trend_analysis"] = "module"
except Exception as e:
    logger.warning(f"⚠️ trend_analysis: {e}")
    trend_analysis = None

# --- SERVICES ---
try:
    import services.bhashini_integration as bhashini_service
    _imported_modules["bhashini_service"] = "service"
except Exception as e:
    logger.warning(f"⚠️ bhashini_service: {e}")
    bhashini_service = None

try:
    import services.ddg_search as ddg_search
    _imported_modules["ddg_search"] = "service"
except Exception as e:
    logger.warning(f"⚠️ ddg_search: {e}")
    ddg_search = None

try:
    import services.mandi_rates as mandi_rates_service
    _imported_modules["mandi_rates_service"] = "service"
except Exception as e:
    logger.warning(f"⚠️ mandi_rates_service: {e}")
    mandi_rates_service = None

try:
    import services.pnr as pnr_service
    _imported_modules["pnr_service"] = "service"
except Exception as e:
    logger.warning(f"⚠️ pnr_service: {e}")
    pnr_service = None

try:
    import services.train_tracking as train_tracking_service
    _imported_modules["train_tracking_service"] = "service"
except Exception as e:
    logger.warning(f"⚠️ train_tracking_service: {e}")
    train_tracking_service = None

try:
    import services.travily_search as travily_search_service
    _imported_modules["travily_search_service"] = "service"
except Exception as e:
    logger.warning(f"⚠️ travily_search_service: {e}")
    travily_search_service = None

if _import_errors:
    logger.warning(f"⚠️ {_import_errors} modules failed to import (see above)")
logger.info(f"✅ Module imports complete: {len(_imported_modules)} modules loaded successfully")

# ==========================================
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
        logger.info(f"✅ {len(self.all_agents)} agents registered")

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

# ==========================================
# MODULES CONFIGURATION
# ==========================================
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
    "miniprogram": {"needs_key": None, "active": True},
    "currency": {"needs_key": None, "active": True},
    "kisaan_doctor": {"needs_key": None, "active": True},
    "banking": {"needs_key": None, "active": True},
    "ai_chat": {"needs_key": "GROQ", "active": AVAILABLE_KEYS["GROQ"] or AVAILABLE_KEYS["GEMINI"]},
    "analytics": {"needs_key": None, "active": True},
    "currents_api": {"needs_key": "CURRENTS", "active": AVAILABLE_KEYS["CURRENTS"]},
    "daily_report": {"needs_key": "CURRENTS", "active": AVAILABLE_KEYS["CURRENTS"]},
    "init": {"needs_key": None, "active": True},
    "language_hub": {"needs_key": None, "active": True},
    "meta_agent": {"needs_key": None, "active": True},
    "newsdata": {"needs_key": "NEWSDATA", "active": AVAILABLE_KEYS["NEWSDATA"]},
    "plant_id": {"needs_key": "PLANT_ID", "active": AVAILABLE_KEYS["PLANT_ID"]},
    "singhji_tv": {"needs_key": None, "active": True},
    "supabase_memory": {"needs_key": "SUPABASE", "active": AVAILABLE_KEYS["SUPABASE"]},
    "supreme_agent": {"needs_key": None, "active": True},
    "telegram": {"needs_key": "TELEGRAM", "active": AVAILABLE_KEYS["TELEGRAM"]},
    "trolley": {"needs_key": None, "active": True},
    "voice": {"needs_key": None, "active": True},
    "voice_cmd": {"needs_key": None, "active": True},
    "voice_tts": {"needs_key": "ELEVENLABS", "active": AVAILABLE_KEYS.get("ELEVENLABS", False)},
    "weather": {"needs_key": "OPENWEATHER", "active": AVAILABLE_KEYS["OPENWEATHER"]},
    "whatsapp": {"needs_key": None, "active": True},
    "agent_swarm": {"needs_key": None, "active": True},
    "auto_account": {"needs_key": None, "active": True},
    "auto_monetize": {"needs_key": None, "active": True},
    "facebook_long_token": {"needs_key": "FACEBOOK", "active": AVAILABLE_KEYS["FACEBOOK"]},
    "singhji_visual": {"needs_key": None, "active": True},
    "trend_analysis": {"needs_key": None, "active": True},
    "bhashini_service": {"needs_key": "BHASHINI", "active": AVAILABLE_KEYS["BHASHINI"]},
    "ddg_search": {"needs_key": None, "active": True},
    "mandi_rates_service": {"needs_key": "MANDI", "active": AVAILABLE_KEYS["MANDI"]},
    "pnr_service": {"needs_key": None, "active": True},
    "train_tracking_service": {"needs_key": None, "active": True},
    "travily_search_service": {"needs_key": "TAVILY", "active": AVAILABLE_KEYS["TAVILY"]},
}

# ==========================================
# MAIN KEYBOARD
# ==========================================
MAIN_KEYBOARD = {
    "inline_keyboard": [
        # Row 1: Daily essentials
        [{"text": "🌤️ Weather", "callback_data": "weather"}, {"text": "📰 News", "callback_data": "news"}],
        # Row 2: Agriculture
        [{"text": "🌾 Mandi Bhav", "callback_data": "mandi"}, {"text": "🌿 Plant Doctor", "callback_data": "plant"}],
        # Row 3: Money
        [{"text": "🥇 Gold Rate", "callback_data": "gold"}, {"text": "⛽ Fuel Price", "callback_data": "fuel"}],
        # Row 4: Finance
        [{"text": "💰 Tax Calc", "callback_data": "tax"}, {"text": "💱 Currency", "callback_data": "currency"}],
        # Row 5: Govt & Jobs
        [{"text": "🏛️ Govt Schemes", "callback_data": "govt"}, {"text": "💼 Rozgar/Jobs", "callback_data": "rozgar"}],
        # Row 6: Services
        [{"text": "💧 Pani Helpline", "callback_data": "pani"}, {"text": "🚽 Sewer/Swachh", "callback_data": "sewer"}],
        # Row 7: AI & Tools
        [{"text": "🤖 AI Chat", "callback_data": "ai_chat"}, {"text": "🎤 Voice AI", "callback_data": "voice"}],
        # Row 8: Search & Translate
        [{"text": "🔍 Search Web", "callback_data": "search"}, {"text": "🔤 Translate", "callback_data": "translate"}],
        # Row 9: Media
        [{"text": "📺 SinghJi TV", "callback_data": "tv"}, {"text": "🎬 Video Gen", "callback_data": "video"}],
        # Row 10: Personal
        [{"text": "🔮 Horoscope", "callback_data": "horoscope"}, {"text": "📋 Yojana Match", "callback_data": "yojana"}],
        # Row 11: Emergency & UPI
        [{"text": "🚨 Emergency", "callback_data": "emergency"}, {"text": "💳 UPI Info", "callback_data": "upi"}],
        # Row 12: Agents
        [{"text": "🛡️ Guard Agent", "callback_data": "guard"}, {"text": "📱 Social Agent", "callback_data": "social"}],
        # Row 13: System
        [{"text": "📊 System Status", "callback_data": "status"}, {"text": "❓ Help / Commands", "callback_data": "help"}],
        # Row 14: New Modules
        [{"text": "🤖 AI Chat v2", "callback_data": "ai_chat_v2"}, {"text": "📊 Analytics", "callback_data": "analytics"}],
        # Row 15: Voice & Media
        [{"text": "🎙️ Voice System", "callback_data": "voice_system"}, {"text": "📺 SinghJi TV", "callback_data": "singhji_tv"}],
        # Row 16: More Services
        [{"text": "🌿 Plant Doctor", "callback_data": "plant_id"}, {"text": "🛒 Trolley/Cart", "callback_data": "trolley"}],
        # Row 17: Advanced
        [{"text": "🔮 Supreme AI", "callback_data": "supreme"}, {"text": "📡 Meta Agent", "callback_data": "meta_agent"}],
        # Row 18: Memory & Tools
        [{"text": "💾 Supabase Memory", "callback_data": "supabase_memory"}, {"text": "🔤 Language Hub", "callback_data": "language_hub"}],
        # Row 19: WhatsApp & More
        [{"text": "💬 WhatsApp", "callback_data": "whatsapp"}, {"text": "📰 Daily Report", "callback_data": "daily_report"}],
        # Row 20: System v2
        [{"text": "🎬 Video Gen", "callback_data": "video_gen"}, {"text": "🧠 Swarm Status", "callback_data": "swarm_v2"}],
    ]
}

# ==========================================
# MASTER SCHEDULER CLASS
# ==========================================
class SinghJiMasterScheduler:
    def __init__(self, http_client, telegram_send_func, api_keys, modules, user_preferences, admin_user_id=0):
        self.http = http_client
        self.send_tg = telegram_send_func
        self.keys = api_keys
        self.modules = modules
        self.users = user_preferences
        self.admin_uid = admin_user_id
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        self._init_db()

    def _init_db(self):
        db_path = os.getenv("SCHEDULER_DB", "scheduler_state.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS scheduler_state (
                job_name TEXT PRIMARY KEY,
                last_run TEXT,
                next_run TEXT,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _update_state(self, job_name, status, next_run=None):
        try:
            db_path = os.getenv("SCHEDULER_DB", "scheduler_state.db")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().isoformat()
            c.execute("""
                INSERT INTO scheduler_state (job_name, last_run, status, next_run)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(job_name) DO UPDATE SET
                    last_run=excluded.last_run,
                    status=excluded.status,
                    next_run=excluded.next_run,
                    retry_count=retry_count + CASE WHEN excluded.status='failed' THEN 1 ELSE 0 END
            """, (job_name, now, status, next_run))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ DB state update failed: {e}")

    def _job_listener(self, event):
        if event.exception:
            logger.error(f"❌ Job {event.job_id} crashed: {event.exception}")
            self._update_state(event.job_id, "failed")
        else:
            logger.info(f"✅ Job {event.job_id} completed successfully")
            self._update_state(event.job_id, "success")

    async def _broadcast_with_rate_limit(self, message, parse_mode=None):
        if not self.users:
            logger.warning("⚠️ No users to broadcast to")
            return
        user_ids = list(self.users.keys())
        logger.info(f"📢 Broadcasting to {len(user_ids)} users")
        batch_size = 20
        success_count = 0
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i+batch_size]
            tasks = []
            for uid in batch:
                tasks.append(self.send_tg(uid, message, parse_mode=parse_mode))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count += sum(1 for r in results if not isinstance(r, Exception))
            if i + batch_size < len(user_ids):
                await asyncio.sleep(1)
        logger.info(f"✅ Broadcast sent to {success_count}/{len(user_ids)} users")

    async def _fetch_news(self, count=5):
        try:
            import modules.news.handler as news_module
            return await news_module.get_news_digest_text(count=count)
        except Exception as e:
            logger.warning(f"⚠️ News fetch failed: {e}")
            return f"• News error: {str(e)[:150]}"

    async def _fetch_weather(self, city="Delhi"):
        if not self.keys.get("OPENWEATHER"):
            return "• Weather API key missing"
        try:
            key = os.getenv("OPENWEATHER_API_KEY")
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            r = await self.http.get(url, timeout=15)
            data = r.json()
            if r.status_code == 200:
                return (
                    f"🌡️ तापमान: {data['main']['temp']}°C (Feel: {data['main']['feels_like']}°C)\n"
                    f"💧 नमी: {data['main']['humidity']}%%\n"
                    f"🌬️ हवा: {data['wind']['speed']} m/s\n"
                    f"☁️ {data['weather'][0]['description'].title()}"
                )
            return f"• Weather error: {data.get('message', 'Unknown')}"
        except Exception as e:
            logger.warning(f"⚠️ Weather fetch failed: {e}")
            return "• Weather fetch failed"

    async def _fetch_mandi(self, state="Uttar Pradesh", limit=5):
        if not MANDI_API_KEY:
            return "• Mandi API key missing"
        try:
            normalized = _normalize_state(state)
            params = {"api-key": MANDI_API_KEY, "format": "json", "limit": limit, "filters[state.keyword]": normalized}
            r = await self.http.get(MANDI_BASE_URL, params=params, timeout=45)
            data = r.json()

            # Check API error
            if "error" in data:
                return f"• Mandi API error: {data.get('error', 'Unknown')}"

            records = data.get("records", [])
            if not records:
                return f"• {normalized} ke liye aaj mandi data available nahi hai\n• Koi aur state try karo: /mandi Punjab"

            lines = [f"🌾 Mandi Bhav — {normalized}\n"]
            for rec in records[:limit]:
                commodity = rec.get("commodity", "?")
                market = rec.get("market", "?")
                district = rec.get("district", "")
                price = rec.get("modal_price", "?")
                min_price = rec.get("min_price", "?")
                max_price = rec.get("max_price", "?")
                date = rec.get("arrival_date", "")
                lines.append(f"📍 {commodity}")
                lines.append(f"   Market: {market}, {district}")
                lines.append(f"   Price: ₹{price}/q (₹{min_price}-{max_price})")
                if date:
                    lines.append(f"   Date: {date}")
                lines.append("")
            return "\n".join(lines)
        except (httpx.TimeoutException, asyncio.TimeoutError):
            logger.warning("⚠️ Mandi fetch timeout (45s se zyada)")
            return "• Mandi data.gov.in अभी धीमा है, थोड़ी देर बाद कोशिश करें\n• Format: /mandi Uttar Pradesh"
        except Exception as e:
            error_text = str(e) or type(e).__name__  # kuch exceptions ka str() khaali hota hai
            logger.warning(f"⚠️ Mandi fetch failed: {error_text}")
            return f"• Mandi error: {error_text[:100]}\n• Format: /mandi Uttar Pradesh"

    async def _fetch_gold_silver(self, city="Delhi"):
        try:
            data = await get_gold_silver_summary(city)
            return (
                f"🥇 Gold 24K: ₹{data.get('gold_gram_24k')}/g | 22K: ₹{data.get('gold_gram_22k')}/g\n"
                f"🥈 Silver (approx): ₹{data.get('silver_gram')}/g"
            )
        except Exception as e:
            error_text = str(e) or type(e).__name__
            logger.warning(f"⚠️ Gold fetch failed: {error_text}")
            return f"• Gold/Silver error: {error_text[:100]}"

    def _fetch_horoscope_summary(self):
        try:
            data = get_all_horoscopes(period="daily", language="hi")
            lines = []
            for entry in data.get("rashis", [])[:12]:
                rashi = entry.get("rashi", "?")
                pred = entry.get("prediction", "")[:60]
                lines.append(f"{rashi}: {pred}")
            return "\n".join(lines) if lines else "• Aaj rashifal available nahi hai"
        except Exception as e:
            logger.warning(f"⚠️ Horoscope fetch failed: {e}")
            return f"• Horoscope error: {str(e)[:100]}"

    async def _job_with_retry(self, job_func, job_name, max_retries=3):
        for attempt in range(max_retries):
            try:
                await job_func()
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Job {job_name} failed after {max_retries} attempts: {e}")
                    self._update_state(job_name, "failed")
                    return False
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Job {job_name} attempt {attempt+1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
        return False

    async def _job_morning_digest(self):
        logger.info("🌅 Morning Digest starting...")
        news_task = self._fetch_news(5)
        weather_task = self._fetch_weather("Delhi")
        mandi_task = self._fetch_mandi("Uttar Pradesh", limit=5)
        gold_task = self._fetch_gold_silver("Delhi")
        horoscope_task = run_in_threadpool(self._fetch_horoscope_summary)
        results = await asyncio.gather(news_task, weather_task, mandi_task, gold_task, horoscope_task, return_exceptions=True)
        news, weather, mandi, gold_silver, horoscope = results
        msg = (
            f"🌅 <b>Singh Ji Morning Digest</b>\n"
            f"📅 {datetime.now().strftime('%d %b %Y, %A')}\n"
            f"{'─' * 28}\n\n"
            f"📰 <b>मुख्य समाचार:</b>\n{news if not isinstance(news, Exception) else 'News unavailable'}\n\n"
            f"🌤️ <b>मौसम (Delhi):</b>\n{weather if not isinstance(weather, Exception) else 'Weather unavailable'}\n\n"
            f"🌾 <b>मंडी भाव (UP):</b>\n{mandi if not isinstance(mandi, Exception) else 'Mandi unavailable'}\n\n"
            f"💰 <b>Gold/Silver:</b>\n{gold_silver if not isinstance(gold_silver, Exception) else 'Gold rates unavailable'}\n\n"
            f"🔮 <b>राशिफल (आज):</b>\n{horoscope if not isinstance(horoscope, Exception) else 'Horoscope unavailable'}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
        self._update_state("morning_digest", "success", "Tomorrow 07:00 AM")
        logger.info("✅ Morning Digest completed")

    async def _job_evening_digest(self):
        logger.info("🌆 Evening Digest starting...")
        news = await self._fetch_news(5)
        rozgar = (
            "• 50+ सरकारी नौकरियाँ आज जारी\n"
            "• UPSSC: 1200+ पदों पर भर्ती\n"
            "• Railway: Group D notification जल्द"
        )
        msg = (
            f"🌆 <b>Singh Ji Evening Digest</b>\n"
            f"📅 {datetime.now().strftime('%d %b %Y')}\n"
            f"{'─' * 28}\n\n"
            f"📰 <b>शाम के समाचार:</b>\n{news}\n\n"
            f"💼 <b>रोज़गार अपडेट:</b>\n{rozgar}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
        self._update_state("evening_digest", "success", "Tomorrow 06:00 PM")
        logger.info("✅ Evening Digest completed")

    async def _job_govt_schemes(self):
        logger.info("🏛️ Govt Schemes starting...")
        content = (
            "• <b>PM Awas Yojana:</b> नई लिस्ट जारी\n"
            "• <b>Ration Card:</b> e-KYC deadline बढ़ी\n"
            "• <b>Kisan Samman Nidhi:</b> 18वीं किस्त जल्द"
        )
        msg = (
            f"🏛️ <b>सरकारी योजना अपडेट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
        self._update_state("govt_schemes", "success")
        logger.info("✅ Govt Schemes completed")

    async def _job_banking_weekly(self):
        logger.info("🏦 Banking Update starting...")
        content = (
            "• <b>SBI FD Rates:</b> 7.10%% (5+ years)\n"
            "• <b>Post Office:</b> New digital savings scheme\n"
            "• <b>RBI:</b> UPI limit for medical payments increased"
        )
        msg = (
            f"🏦 <b>बैंकिंग साप्ताहिक अपडेट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
        self._update_state("banking_weekly", "success")
        logger.info("✅ Banking update completed")

    async def _job_fb_token_check(self):
        logger.info("🔑 Facebook Token Check starting...")
        try:
            if social_core.SOCIAL_AGENT:
                result = await social_core.SOCIAL_AGENT.check_and_refresh_facebook_token()
                logger.info(f"Facebook token check result: {result}")
                if result.get("refreshed") and self.admin_uid:
                    await self.send_tg(self.admin_uid, f"🔑 <b>Facebook Token Auto-Refresh</b>\n\n✅ नया token मिल गया")
        except Exception as e:
            logger.error(f"❌ Facebook token check failed: {e}")
        self._update_state("fb_token_check", "success")
        logger.info("✅ Facebook token check completed")

    async def _job_social_promo(self):
        logger.info("📱 Social Promo starting...")
        try:
            if social_core.SOCIAL_AGENT:
                result = await social_core.SOCIAL_AGENT.create_and_publish()
                summary = f"✅ {result['success_count']}/{result['total']} platforms posted"
            else:
                summary = "⚠️ Social agent not initialized"
        except Exception as e:
            summary = f"💥 Social post failed: {e}"
            logger.error(f"❌ Social promo failed: {e}")
        if self.admin_uid:
            await self.send_tg(self.admin_uid, f"📱 <b>Social Media Auto-Post</b>\n\n{summary}")
        self._update_state("social_promo", "success")
        logger.info("✅ Social promo completed")

    async def _job_monthly_tenders(self):
        logger.info("📋 Monthly Tenders starting...")
        content = (
            "• <b>Road Construction:</b> NHAI tender\n"
            "• <b>Smart City:</b> LED lighting project\n"
            "• <b>PWD:</b> Bridge repair work"
        )
        msg = (
            f"📋 <b>मासिक टेंडर अलर्ट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
        self._update_state("monthly_tenders", "success")
        logger.info("✅ Monthly tenders completed")

    # ─── FLOOD WATCH (File 2 se liya) ───
    FLOOD_WATCH_CITIES = ["Kanpur", "Lucknow", "Gorakhpur", "Varanasi", "Patna", "Muzaffarpur", "Darbhanga"]
    FLOOD_RAIN_THRESHOLD_MM = 100

    async def _check_flood_risk(self, city: str) -> Optional[Dict[str, Any]]:
        if not self.keys.get("OPENWEATHER"):
            return None
        try:
            key = os.getenv("OPENWEATHER_API_KEY")
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={key}&units=metric"
            r = await self.http.get(url, timeout=15)
            if r.status_code != 200:
                return None
            data = r.json()
            periods = data.get("list", [])[:13]
            total_rain = sum(p.get("rain", {}).get("3h", 0) for p in periods)
            if total_rain >= self.FLOOD_RAIN_THRESHOLD_MM:
                return {"city": city, "expected_rain_mm": round(total_rain, 1)}
            return None
        except Exception as e:
            logger.warning(f"[FLOOD] {city} check fail: {e}")
            return None

    async def _job_flood_watch(self):
        logger.info("[JOB] Flood Watch check starting...")
        risky = []
        for city in self.FLOOD_WATCH_CITIES:
            result = await self._check_flood_risk(city)
            if result:
                risky.append(result)
        if risky:
            lines = "\n".join(f"⚠️ {r['city']}: agle 24-40 ghante mein ~{r['expected_rain_mm']}mm baarish ka anumaan" for r in risky)
            msg = (
                f"🌊 <b>Baadh Chetavani (Flood Watch)</b>\n"
                f"{'─' * 28}\n\n"
                f"{lines}\n\n"
                f"Savdhaan rahein, nichle/nadi-kinare ke ilakon mein khaas dhyan dein.\n\n"
                f"— <i>Singh Ji AI Ultra</i>"
            )
            await self._broadcast_with_rate_limit(msg, parse_mode="HTML")
            logger.info(f"[JOB] Flood Watch: {len(risky)} cities flagged")
        else:
            logger.info("[JOB] Flood Watch: koi risk nahi mila")
        self._update_state("flood_watch", "success")

    async def _self_ping(self):
        if not APP_URL:
            return
        try:
            r = await self.http.get(f"{APP_URL}/health", timeout=10)
            if r.status_code != 200:
                logger.warning(f"⚠️ Self-ping status {r.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Self-ping failed: {e}")

    def setup(self):
        jobs = [
            {"id": "morning_digest", "func": self._job_morning_digest, "trigger": CronTrigger(hour=7, minute=0), "name": "Morning News + Weather", "misfire_grace_time": 3600},
            {"id": "evening_digest", "func": self._job_evening_digest, "trigger": CronTrigger(hour=18, minute=0), "name": "Evening News + Rozgar", "misfire_grace_time": 3600},
            {"id": "flood_watch", "func": self._job_flood_watch, "trigger": CronTrigger(hour="*/6", minute=0), "name": "Flood Watch (24-40hr forecast)", "misfire_grace_time": 3600},
            {"id": "govt_schemes", "func": self._job_govt_schemes, "trigger": CronTrigger(day_of_week="tue,fri", hour=15, minute=0), "name": "Govt Schemes Update"},
            {"id": "banking_weekly", "func": self._job_banking_weekly, "trigger": CronTrigger(day_of_week="mon", hour=11, minute=0), "name": "Banking Weekly"},
            {"id": "social_promo", "func": self._job_social_promo, "trigger": CronTrigger(day_of_week="mon,wed,sat", hour=10, minute=0), "name": "Social Media Promo"},
            {"id": "monthly_tenders", "func": self._job_monthly_tenders, "trigger": CronTrigger(day=1, hour=9, minute=0), "name": "Monthly Tender Alert"},
            {"id": "fb_token_check", "func": self._job_fb_token_check, "trigger": CronTrigger(day_of_week="sun", hour=3, minute=0), "name": "Facebook Token Refresh"},
            {"id": "self_ping", "func": self._self_ping, "trigger": IntervalTrigger(minutes=30), "name": "Railway Sleep Prevention"},
        ]
        for job_config in jobs:
            self.scheduler.add_job(
                job_config["func"],
                job_config["trigger"],
                id=job_config["id"],
                name=job_config["name"],
                replace_existing=True,
                misfire_grace_time=job_config.get("misfire_grace_time", 60)
            )
        logger.info(f"✅ {len(jobs)} jobs registered")

    async def start(self):
        self.setup()
        self.scheduler.start()
        logger.info("🚀 Singh Ji Master Scheduler STARTED")
        for job in self.scheduler.get_jobs():
            nxt = str(job.next_run_time) if job.next_run_time else "N/A"
            logger.info(f"   ⏰ {job.name} → {nxt}")

    async def stop(self):
        self.scheduler.shutdown()
        logger.info("🛑 Singh Ji Master Scheduler STOPPED")

    def get_status(self):
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({"id": job.id, "name": job.name, "next_run": str(job.next_run_time) if job.next_run_time else None})
        return {"running": self.scheduler.running, "total_jobs": len(jobs), "jobs": jobs, "timezone": "Asia/Kolkata"}

# ==========================================
# VIDEO CREDENTIALS HELPER
# ==========================================
def _build_video_credentials() -> Dict[str, "PlatformCredentials"]:
    creds = {}
    key_map = {
        "seedance": SEEDANCE_API_KEY,
        "kling": KLING_API_KEY,
        "hailuo": HAILUO_API_KEY,
        "luma": LUMA_API_KEY,
        "pika": PIKA_API_KEY,
        "veo": VEO_API_KEY,
    }
    for platform, api_key in key_map.items():
        if api_key:
            creds[platform] = PlatformCredentials(platform=platform, api_key=api_key)
    return creds

# ==========================================
# TAX CALCULATOR
# ==========================================
def _calculate_tax(income: float, regime: str = "new", deductions: float = 0):
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
    return {
        "income": income, "regime": regime,
        "tax": round(tax, 2), "cess": round(cess, 2),
        "total": round(total_tax, 2),
        "take_home": round(income - total_tax, 2)
    }

# ==========================================
# ADMIN AUTH CHECK
# ==========================================
def _check_admin_auth(request):
    if not ADMIN_API_KEY:
        return True
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return token == ADMIN_API_KEY
    provided = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    return provided == ADMIN_API_KEY

# ==========================================
# WHISPER HELPERS
# ==========================================
def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            logger.info(f"Loading Whisper ({model_size})...")
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Whisper load failed: {e}")
            return None
    return _whisper_model

def _transcribe_sync(audio_bytes: bytes, suffix: str, language=None):
    model = _get_whisper_model()
    if model is None:
        return None
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, info = model.transcribe(tmp.name, language=language)
        transcript = " ".join(seg.text.strip() for seg in segments)
    return transcript, info.language, info.language_probability

def _tts_sync(text: str, lang: str) -> bytes:
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()

def _b64_too_big(b64_str: str) -> bool:
    return (len(b64_str) * 3 / 4) > MAX_B64_BYTES

# ==========================================
# API FUNCTIONS
# ==========================================
async def _call_groq(prompt: str, timeout=30):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")
    resp = await HTTP_CLIENT.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout
    )
    result = resp.json()
    if "choices" not in result:
        raise ValueError(f"Groq API error: {result}")
    return result["choices"][0]["message"]["content"]

# ==========================================
# LIFESPAN MANAGER
# ==========================================
@asynccontextmanager
async def lifespan(app):
    global HTTP_CLIENT, MASTER_SCHEDULER, USER_PREFERENCES
    logger.info("🚀 Singh Ji AI Ultra v8.0 HYBRID Starting...")
    HTTP_CLIENT = httpx.AsyncClient(
        timeout=20,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    try:
        social_core.init_social_agent(HTTP_CLIENT)
        await social_core.SOCIAL_AGENT.load_saved_facebook_token()
        logger.info("✅ Social Agent initialized")
    except Exception as e:
        logger.warning(f"⚠️ Social Agent init failed: {e}")
    sync = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    logger.info(f"✅ Swarm: {sync['active']}/{sync['total']} agents loaded")
    logger.info(f"✅ Active APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}")
    loaded_prefs = await run_in_threadpool(_load_user_preferences_sync)
    USER_PREFERENCES.update(loaded_prefs)
    logger.info(f"✅ {len(loaded_prefs)} subscribers reloaded from Supabase")
    if TELEGRAM_TOKEN and APP_URL:
        await _check_webhook_config()
        await _ensure_correct_webhook()
    MASTER_SCHEDULER = SinghJiMasterScheduler(
        http_client=HTTP_CLIENT,
        telegram_send_func=_telegram_send_message,
        api_keys=AVAILABLE_KEYS,
        modules=MODULES,
        user_preferences=USER_PREFERENCES,
        admin_user_id=ADMIN_USER_ID,
    )
    await MASTER_SCHEDULER.start()
    yield
    logger.info("🛑 Shutting down...")
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER.stop()
    if HTTP_CLIENT:
        await HTTP_CLIENT.aclose()
    logger.info("✅ Singh Ji AI Ultra Stopped!")

# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(
    title="Singh Ji AI Ultra v8.3 FINAL — All 42+ Modules",
    version="8.3.0-final",
    lifespan=lifespan
)

# ==========================================
# CORS MIDDLEWARE
# ==========================================
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

# ==========================================
# RATE LIMITING MIDDLEWARE
# ==========================================
STRICT_PATH_PREFIXES = (
    "/api/chat",
    "/api/whisper/",
    "/api/bhashini/",
    "/api/tts",
    "/api/plant/",
    "/modules/voice",
)
RATE_LIMITED_PREFIXES = ("/api/", "/modules/")

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in STRICT_PATH_PREFIXES):
        limited = _is_rate_limited(request, "strict", *RATE_LIMIT_STRICT)
    elif any(path.startswith(p) for p in RATE_LIMITED_PREFIXES):
        limited = _is_rate_limited(request, "global", *RATE_LIMIT_GLOBAL)
    else:
        limited = False
    if limited:
        return JSONResponse(
            {"error": "Rate limit exceeded. Please wait and try again.", "retry_after_seconds": 60},
            status_code=429
        )
    return await call_next(request)

# ==========================================
# REGISTER ROUTERS — SAFE
# ==========================================
_registered_routes = []

if kisaan_router:
    app.include_router(kisaan_router, prefix="/modules/kisaan_doctor")
    _registered_routes.append("kisaan_doctor")
if currency_router:
    app.include_router(currency_router, prefix="/api")
    _registered_routes.append("currency")
if aavishkar_router:
    app.include_router(aavishkar_router, prefix="/modules/aavishkar")
    _registered_routes.append("aavishkar")
if goldrate_router:
    app.include_router(goldrate_router, prefix="/api/goldrate")
    _registered_routes.append("goldrate")
if fuel_router:
    app.include_router(fuel_router, prefix="/api/fuel")
    _registered_routes.append("fuel")
if scheme_swarm_router:
    app.include_router(scheme_swarm_router)
    _registered_routes.append("scheme_swarm")
if trishul_router:
    app.include_router(trishul_router, prefix="/api/trishul")
    _registered_routes.append("trishul")
if guard_router:
    app.include_router(guard_router, prefix="/api")
    _registered_routes.append("guard_agent")
if oauth_router:
    app.include_router(oauth_router, prefix="/api")
    _registered_routes.append("oauth_connector")
if social_router:
    app.include_router(social_router)
    _registered_routes.append("social_agent")
if news_router:
    app.include_router(news_router)
    _registered_routes.append("news")
if miniprogram_router:
    app.include_router(miniprogram_router, prefix="/api/v1/miniprogram")
    _registered_routes.append("miniprogram")
if newsdata_router:
    app.include_router(newsdata_router, prefix="/api/newsdata")
    _registered_routes.append("newsdata")
if weather_router:
    app.include_router(weather_router, prefix="/api/weather")
    _registered_routes.append("weather")
if supreme_router:
    app.include_router(supreme_router, prefix="/api/supreme")
    _registered_routes.append("supreme_agent")

# API Routes (handler-based)
if banking_handler:
    app.add_api_route("/api/banking", banking_handler, methods=["GET"])
    _registered_routes.append("banking")
if pani_handler:
    app.add_api_route("/api/pani", pani_handler, methods=["GET", "POST"])
    _registered_routes.append("pani")
if sewer_handler:
    app.add_api_route("/api/sewer", sewer_handler, methods=["GET", "POST"])
    _registered_routes.append("sewer")
if upi_handler:
    app.add_api_route("/api/upi", upi_handler, methods=["GET", "POST"])
    _registered_routes.append("upi")
if mandi_handler:
    app.add_api_route("/api/mandi", mandi_handler, methods=["GET"])
    _registered_routes.append("mandi")
if search_handler:
    app.add_api_route("/api/search", search_handler, methods=["GET", "POST"])
    _registered_routes.append("search")
if rozgar_handler:
    app.add_api_route("/api/rozgar", rozgar_handler, methods=["GET", "POST"])
    _registered_routes.append("rozgar")
if ai_chat_handler:
    app.add_api_route("/api/ai_chat", ai_chat_handler, methods=["GET", "POST"])
    _registered_routes.append("ai_chat")
if analytics_handler:
    app.add_api_route("/api/analytics", analytics_handler, methods=["GET", "POST"])
    _registered_routes.append("analytics")
if currents_handler:
    app.add_api_route("/api/currents", currents_handler, methods=["GET", "POST"])
    _registered_routes.append("currents_api")
if init_handler:
    app.add_api_route("/api/init", init_handler, methods=["GET", "POST"])
    _registered_routes.append("init")
if language_hub_handler:
    app.add_api_route("/api/language_hub", language_hub_handler, methods=["GET", "POST"])
    _registered_routes.append("language_hub")
if meta_handler:
    app.add_api_route("/api/meta", meta_handler, methods=["GET", "POST"])
    _registered_routes.append("meta_agent")
if plant_id_handler:
    app.add_api_route("/api/plant_id", plant_id_handler, methods=["GET", "POST"])
    _registered_routes.append("plant_id")
if singhji_tv_handler:
    app.add_api_route("/api/singhji_tv", singhji_tv_handler, methods=["GET", "POST"])
    _registered_routes.append("singhji_tv")
if supabase_memory_handler:
    app.add_api_route("/api/supabase_memory", supabase_memory_handler, methods=["GET", "POST"])
    _registered_routes.append("supabase_memory")
if telegram_handler:
    app.add_api_route("/api/telegram", telegram_handler, methods=["GET", "POST"])
    _registered_routes.append("telegram")
if trolley_handler:
    app.add_api_route("/api/trolley", trolley_handler, methods=["GET", "POST"])
    _registered_routes.append("trolley")
if voice_handler:
    app.add_api_route("/api/voice", voice_handler, methods=["GET", "POST"])
    _registered_routes.append("voice")
if voice_cmd_handler:
    app.add_api_route("/api/voice_cmd", voice_cmd_handler, methods=["GET", "POST"])
    _registered_routes.append("voice_cmd")
if voice_tts_handler:
    app.add_api_route("/api/voice_tts", voice_tts_handler, methods=["GET", "POST"])
    _registered_routes.append("voice_tts")
if whatsapp_handler:
    app.add_api_route("/api/whatsapp", whatsapp_handler, methods=["GET", "POST"])
    _registered_routes.append("whatsapp")
if daily_report_handler:
    app.add_api_route("/api/daily_report", daily_report_handler, methods=["GET", "POST"])
    _registered_routes.append("daily_report")

logger.info(f"✅ Routes registered: {len(_registered_routes)} modules active")
for r in _registered_routes:
    logger.info(f"   ✅ {r}")

# ==========================================
# VIDEO GENERATION ENDPOINTS
# ==========================================
@app.post("/api/video/generate")
async def video_generate(prompt: str, duration: int = 5, aspect_ratio: str = "16:9"):
    creds = _build_video_credentials()
    if not creds:
        return {"success": False, "error": "No video API keys set (SEEDANCE/KLING/HAILUO/LUMA/PIKA/VEO)"}
    router_ = SmartVideoRouter(creds)
    await router_.initialize()
    result = await router_.generate_video(VideoGenerationRequest(
        prompt=prompt, duration=duration, aspect_ratio=aspect_ratio
    ))
    return result.__dict__

@app.get("/api/video/status")
async def video_status():
    creds = _build_video_credentials()
    if not creds:
        return {"configured_platforms": 0, "platforms": {}}
    router_ = SmartVideoRouter(creds)
    await router_.initialize()
    return router_.get_status_summary()

# ==========================================
# LANGUAGE MODULE
# ==========================================
LANG_MODULE = LanguageModule()

# ==========================================
# HEALTH & STATUS ENDPOINTS
# ==========================================
@app.get("/")
@app.head("/")
async def root():
    active = [n for n, i in MODULES.items() if i["active"]]
    return {
        "name": "Singh Ji AI Ultra v8.3 FINAL",
        "status": "LIVE",
        "total_modules": len(MODULES),
        "active_modules": active,
        "active_count": len(active),
        "agents": SMART_SWARM.get_status(),
        "apis": {k: v for k, v in AVAILABLE_KEYS.items()},
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI Ultra v8.3 FINAL"}

@app.get("/ping")
@app.get("/api/ping")
async def ping():
    return {
        "status": "pong",
        "timestamp": datetime.now().isoformat(),
        "service": "Singh Ji AI Ultra v8.0",
        "version": "8.3.0-final"
    }

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
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/check")
async def api_check():
    tests = {
        "OPENWEATHER": (f"https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={OPENWEATHER_API_KEY or ''}", {}, "GET"),
        "GROQ": ("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {GROQ_API_KEY or ''}"}, "GET"),
        "GEMINI": (f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY or ''}", {}, "GET"),
        "TELEGRAM": (f"https://api.telegram.org/bot{TELEGRAM_TOKEN or ''}/getMe", {}, "GET"),
        "SUPABASE": (f"{SUPABASE_URL or ''}/rest/v1/", {"apikey": SUPABASE_SERVICE_KEY or "", "Authorization": f"Bearer {SUPABASE_SERVICE_KEY or ''}"}, "GET"),
        "FACEBOOK": (f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN or ''}", {}, "GET"),
        "YOUTUBE": (f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&maxResults=1&key={YOUTUBE_API_KEY or ''}", {}, "GET"),
        "CURRENTS": (f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY or ''}", {}, "GET"),
        "NEWSDATA": (f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY or ''}&q=test", {}, "GET"),
        "TAVILY": (f"https://api.tavily.com/search?api_key={TAVILY_API_KEY or ''}&query=test&max_results=1", {}, "GET"),
    }

    async def _check_one(name, url, headers):
        if not AVAILABLE_KEYS.get(name):
            return name, {"status": "MISSING", "code": None}
        try:
            start = time.time()
            r = await HTTP_CLIENT.get(url, headers=headers, timeout=10)
            elapsed = round((time.time() - start) * 1000, 2)
            if r.status_code in [200, 401, 403]:
                return name, {"status": "LIVE", "code": r.status_code, "ms": elapsed}
            return name, {"status": "ERROR", "code": r.status_code, "ms": elapsed}
        except Exception as e:
            return name, {"status": "FAIL", "error": str(e)[:50]}

    outcomes = await asyncio.gather(*(_check_one(n, u, h) for n, (u, h, m) in tests.items()))
    results = dict(outcomes)
    live = sum(1 for v in results.values() if v["status"] == "LIVE")
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {"live": live, "total": len(results)},
        "results": results
    }

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    cache_key = _cache_key("weather", city)
    cached = await _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY missing"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = await HTTP_CLIENT.get(url, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            result = {
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "desc": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "source": "OPENWEATHER_LIVE"
            }
            await _cache_set(cache_key, result, CACHE_TTL["weather"])
            return result
        return {"error": data.get("message", "Unknown error"), "code": resp.status_code}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return {"error": str(e)}

# ==========================================
# PLANT ID ENDPOINT
# ==========================================
@app.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "PLANT_ID_API missing"}
    data = await request.json()
    image_b64 = data.get("image_base64", "")
    if not image_b64:
        return {"error": "image_base64 required"}
    if _b64_too_big(image_b64):
        return JSONResponse(status_code=413, content={"error": "Image too large (max 10MB)"})
    try:
        resp = await HTTP_CLIENT.post(
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
            "top_match": {
                "name": top.get("name"),
                "probability": top.get("probability"),
                "common_names": top.get("details", {}).get("common_names")
            } if top else None,
            "all_suggestions": suggestions[:5],
            "source": "PLANT.ID_LIVE"
        }
    except Exception as e:
        logger.error(f"Plant identification error: {e}")
        return {"error": str(e)}

# ==========================================
# AI CHAT ENDPOINT
# ==========================================
@app.post("/api/chat")
async def ai_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "groq")
    user_id = data.get("user_id", "anonymous")

    personal_kw = ["password", "otp", "secret", "aadhar", "pan", "bank", "cvv", "pin"]
    is_personal = any(kw in prompt.lower() for kw in personal_kw)

    cache_key = None
    if not is_personal:
        cache_key = _cache_key("ai_chat", model, prompt[:100])
        cached = await _cache_get(cache_key)
        if cached:
            cached["source"] = "CACHE"
            return cached

    if model in ["groq", "auto"] and GROQ_API_KEY:
        try:
            response_text = await _call_groq(prompt)
            result_data = {
                "status": "success",
                "model": "groq",
                "response": response_text,
                "source": "GROQ_LIVE"
            }
            if not is_personal:
                await _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {
                "prompt": prompt, "response": response_text, "model": "groq"
            })
            return result_data
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if model in ["gemini", "auto"] and GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp = await HTTP_CLIENT.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            result_data = {
                "status": "success",
                "model": "gemini",
                "response": text,
                "source": "GEMINI_LIVE"
            }
            if not is_personal:
                await _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {
                "prompt": prompt, "response": text, "model": "gemini"
            })
            return result_data
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")

    if model in ["cerebras", "auto"] and CEREBRAS_API_KEY:
        try:
            resp = await HTTP_CLIENT.post(
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

# ==========================================
# MEMORY ENDPOINTS
# ==========================================
@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return await _memory_get(key)

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(int(time.time())))
    value = data.get("value", data)
    return await _memory_save(key, value)

# ==========================================
# BHASHINI ENDPOINTS
# ==========================================
BHASHINI_PIPELINE_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"

@app.get("/api/bhashini/")
async def bhashini_root():
    return {
        "module": "Bhashini",
        "status": "active" if AVAILABLE_KEYS["BHASHINI"] else "missing_credentials"
    }

@app.post("/api/bhashini/translate")
async def bhashini_translate(request: Request):
    if not AVAILABLE_KEYS["BHASHINI"]:
        return {"error": "Bhashini credentials missing"}
    data = await request.json()
    text = data.get("text", "")
    source = data.get("source", "hi")
    target = data.get("target", "en")
    try:
        headers = {
            "userID": BHASHINI_USER_ID,
            "ulcaApiKey": BHASHINI_ULCA_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "pipelineTasks": [{
                "taskType": "translation",
                "config": {"language": {"sourceLanguage": source, "targetLanguage": target}}
            }],
            "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
        }
        resp = await HTTP_CLIENT.post(BHASHINI_PIPELINE_URL, headers=headers, json=payload, timeout=15)
        pipeline = resp.json()
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
        compute_url = pipeline["pipelineInferenceAPIEndPoint"]["callbackUrl"]
        key_name = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["name"]
        key_value = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["value"]

        compute_payload = {
            "pipelineTasks": [{
                "taskType": "translation",
                "config": {"language": {"sourceLanguage": source, "targetLanguage": target}, "serviceId": service_id}
            }],
            "inputData": {"input": [{"source": text}]}
        }
        compute_resp = await HTTP_CLIENT.post(
            compute_url,
            headers={key_name: key_value, "Content-Type": "application/json"},
            json=compute_payload,
            timeout=20
        )
        result = compute_resp.json()
        translated = result["pipelineResponse"][0]["output"][0]["target"]
        return {
            "status": "success",
            "original": text,
            "translated": translated,
            "source": source,
            "target": target,
            "source_api": "BHASHINI_LIVE"
        }
    except Exception as e:
        logger.error(f"Bhashini error: {e}")
        return {"error": str(e)}

# ==========================================
# WHISPER (VOICE TRANSCRIPTION) ENDPOINT
# ==========================================
@app.post("/api/whisper/transcribe")
async def whisper_transcribe(request: Request):
    data = await request.json()
    audio_b64 = data.get("audio_base64", "")
    language = data.get("language")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    if _b64_too_big(audio_b64):
        return JSONResponse(status_code=413, content={"error": "Audio too large (max 10MB)"})
    try:
        audio_bytes = base64.b64decode(audio_b64)
        out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".wav", language)
        if out is None:
            return {"error": "Whisper model not available"}
        transcript, detected_lang, lang_prob = out
        return {
            "status": "success",
            "transcript": transcript,
            "detected_language": detected_lang,
            "language_probability": round(lang_prob, 3),
            "source": "WHISPER_LOCAL"
        }
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return {"error": str(e)}

# ==========================================
# TEXT-TO-SPEECH ENDPOINT
# ==========================================
@app.post("/api/tts")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text", "")
    lang = data.get("lang", "hi")
    if not text:
        return {"error": "text required"}
    try:
        audio_bytes = await run_in_threadpool(_tts_sync, text, lang)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"status": "success", "audio_base64": audio_b64, "lang": lang, "source": "GTTS_LIVE"}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {"error": str(e)}

# ==========================================
# SOCIAL MEDIA ENDPOINTS
# ==========================================
@app.get("/api/facebook/status")
async def facebook_status():
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=id,name,followers_count"
        resp = await HTTP_CLIENT.get(url)
        data = resp.json()
        if resp.status_code == 200:
            return {
                "status": "connected",
                "page": {"id": data.get("id"), "name": data.get("name"), "followers": data.get("followers_count", 0)}
            }
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
        resp = await HTTP_CLIENT.post(url, data=payload)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/instagram/status")
async def instagram_status():
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"error": "INSTAGRAM_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}?access_token={INSTAGRAM_ACCESS_TOKEN}&fields=id,username,followers_count"
        resp = await HTTP_CLIENT.get(url)
        data = resp.json()
        if resp.status_code == 200:
            return {
                "status": "connected",
                "account": {"id": data.get("id"), "username": data.get("username"), "followers": data.get("followers_count", 0)}
            }
        return {"error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/youtube/search")
async def youtube_search(q: str = "", max_results: int = 10):
    if not YOUTUBE_API_KEY:
        return {"error": "YOUTUBE_API_KEY missing"}
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={q}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
        resp = await HTTP_CLIENT.get(url)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# TAX CALCULATOR ENDPOINT
# ==========================================
@app.post("/api/retirement/tax-calculate")
async def tax_calculate(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")
    deductions = data.get("deductions", 0)
    return _calculate_tax(income, regime, deductions)

# ==========================================
# SWARM ENDPOINTS
# ==========================================
@app.get("/api/swarm/status")
async def swarm_status():
    return SMART_SWARM.get_status()

@app.post("/api/swarm/sync")
async def swarm_sync():
    result = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    return {"synced": True, **result}

# ==========================================
# PAYMENT ENDPOINTS
# ==========================================
@app.get("/api/payment/")
async def payment_root():
    return {
        "module": "Payment Gateway",
        "status": "ON_HOLD" if not AVAILABLE_KEYS["RAZORPAY"] else "ACTIVE",
        "upi_id": "jp200883@sbi",
        "note": "Activate at 1000+ daily users"
    }

@app.post("/api/payment/create-order")
async def payment_create_order(request: Request):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return {"error": "Razorpay keys missing"}
    data = await request.json()
    amount = data.get("amount", 0)
    currency = data.get("currency", "INR")
    receipt = data.get("receipt", f"order_{int(time.time())}")

    def _create_order_sync():
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.order.create({
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1
        })

    try:
        order = await run_in_threadpool(_create_order_sync)
        return {"status": "success", "order": order, "source": "RAZORPAY_LIVE"}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# GMAIL ENDPOINTS
# ==========================================
@app.get("/api/gmail/")
async def gmail_root():
    return {
        "module": "Gmail",
        "status": "active" if AVAILABLE_KEYS["GMAIL"] else "missing_credentials"
    }

@app.get("/api/gmail/auth-url")
async def gmail_auth_url():
    if not GMAIL_CLIENT_ID:
        return {"error": "GMAIL_CLIENT_ID missing"}
    redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "https://singhji-ai.github.io/oauth/callback")
    scope = "https://www.googleapis.com/auth/gmail.send"
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GMAIL_CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&access_type=offline"
    return {"auth_url": url}

# ==========================================
# ADMIN ENDPOINTS
# ==========================================
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
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
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
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER._broadcast_with_rate_limit(f"Admin Broadcast\n\n{message}")
        return {"broadcast": True, "sent_to": len(USER_PREFERENCES)}
    return {"error": "Scheduler not initialized"}

# ==========================================
# TELEGRAM WEBHOOK
# ==========================================
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        # Handle callback queries
        if "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            user_id = callback["from"]["id"]
            query_data = callback["data"]

            # ─── BUTTONS THAT NEED USER INPUT (waiting_for) ───
            input_buttons = {
                "weather": ("🌤️ Weather", "City batao! (jaise: Delhi, Mumbai, Kanpur)"),
                "mandi": ("🌾 Mandi Bhav", "State batao! (jaise: UP, Punjab, Haryana)"),
                "tax": ("💰 Tax Calc", "Annual income batao! (jaise: 500000)"),
                "gold": ("🥇 Gold Rate", "City batao! (default: Delhi)"),
                "fuel": ("⛽ Fuel Price", "City batao! (default: Delhi)"),
                "horoscope": ("🔮 Horoscope", "Rashi batao! (jaise: मेष, सिंह, तुला)"),
                "currency": ("💱 Currency", "Format: USD INR 100"),
                "rozgar": ("💼 Rozgar", "Keyword + Country batao! (jaise: software IN)"),
                "search": ("🔍 Search", "Kya search karna hai?"),
                "translate": ("🔤 Translate", "Format: en Namaste kaise ho"),
                "yojana": ("📋 Yojana", "Format: 30 100000 farmer"),
                "tv": ("📺 SinghJi TV", "Category batao! (educational/news/health)"),
                "video": ("🎬 Video", "Video ka prompt batao!"),
            }

            if query_data in input_buttons:
                label, prompt = input_buttons[query_data]
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = query_data
                await _telegram_send_message(chat_id, f"{label}\n\n{prompt}")
                return {"status": "ok"}

            # ─── INSTANT REPLY BUTTONS ───
            if query_data == "status":
                status = SMART_SWARM.get_status()
                api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
                text = (
                    f"📊 Singh Ji AI Status\n\n"
                    f"🤖 Agents: {status['currently_loaded']}/330\n"
                    f"⚡ Active: {status['active_running']}\n"
                    f"😴 Idle: {status['idle']}\n"
                    f"🔌 APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
                    f"👥 Users: {len(USER_PREFERENCES)}\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                await _telegram_send_message(chat_id, text)

            elif query_data == "news":
                try:
                    import modules.news.handler as news_module
                    text = "📰 Latest News\n\n" + await news_module.get_news_digest_text(count=5)
                    await _telegram_send_message(chat_id, text)
                except Exception as e:
                    await _telegram_send_message(chat_id, f"❌ News error: {str(e)[:100]}")

            elif query_data == "emergency":
                emg_text = "🚨 Emergency Numbers\n\n"
                for k, v in EMERGENCY_DATA.items():
                    emg_text += f"{k.title()}: {v['number']}"
                    if v.get("alt"):
                        emg_text += f" / {v['alt']}"
                    emg_text += "\n"
                await _telegram_send_message(chat_id, emg_text)

            elif query_data == "upi":
                upi_id = os.getenv("UPI_ID", "jp200883@sbi")
                upi_text = f"💳 UPI Info\n\nUPI ID: {upi_id}\nApps: PhonePe, GPay, Paytm, BHIM\nDaily Limit: ₹1,00,000"
                await _telegram_send_message(chat_id, upi_text)

            elif query_data == "pani":
                pani_text = (
                    "💧 Pani (Water) Helplines\n\n"
                    "National: 1800-180-1818\n"
                    "Jal Jeevan: 1800-111-555\n\n"
                    "Schemes: Jal Jeevan Mission, AMRUT 2.0, Swajal\n"
                    "Portal: jaljeevanmission.gov.in"
                )
                await _telegram_send_message(chat_id, pani_text)

            elif query_data == "sewer":
                sewer_text = (
                    "🚽 Sewer/Sanitation Helplines\n\n"
                    "Swachh Bharat: 1800-180-1818\n"
                    "Urban Sewer: 1800-111-555\n"
                    "Complaint: 1969\n\n"
                    "Portal: swachhbharaturban.gov.in"
                )
                await _telegram_send_message(chat_id, sewer_text)

            elif query_data == "govt":
                govt_text = (
                    "🏛️ Govt Services\n\n"
                    "/govt aadhaar — Aadhaar services\n"
                    "/govt pan — PAN card\n"
                    "/govt passport — Passport\n"
                    "/govt voter — Voter ID\n"
                    "/govt ration — Ration card\n"
                    "/govt driving — Driving license\n"
                    "/govt ayushman — Ayushman Bharat\n"
                    "/govt pmkisan — PM Kisan"
                )
                await _telegram_send_message(chat_id, govt_text)

            elif query_data == "ai_chat":
                await _telegram_send_message(chat_id, '🤖 AI Chat\n\nKuch bhi poochho! Main jawab dunga.\n\nExample: "India ka capital kya hai?"')

            elif query_data == "voice":
                await _telegram_send_message(chat_id, "🎤 Voice AI\n\nVoice message bhejo!\n\nMain transcribe karke AI se jawab launga.")

            elif query_data == "plant":
                await _telegram_send_message(chat_id, "🌿 Plant Doctor\n\nPlant ki photo bhejo!\n\nDisease detect karke ilaj bataunga.")

            elif query_data == "guard":
                try:
                    import modules.guard_agent.handler as guard_module
                    g = guard_module.singhji_guard
                    guard_text = (
                        f"🛡️ Guard Agent\n\n"
                        f"📹 Cameras: {len(g.cameras_db)}\n"
                        f"🚨 Alerts: {len(g.alerts_db)}\n"
                        f"🔍 Detection: vehicle, human, sound, face, ANPR, fire, crowd"
                    )
                except Exception as e:
                    guard_text = f"🛡️ Guard Agent\n\nStatus: Loading...\n{str(e)[:80]}"
                await _telegram_send_message(chat_id, guard_text)

            elif query_data == "social":
                try:
                    s = social_core.SOCIAL_AGENT
                    if s:
                        cfg = s.get_stats()["platforms_configured"]
                        live = ", ".join(p for p, v in cfg.items() if v) or "none"
                        social_text = (
                            f"📱 Social Agent\n\n"
                            f"📤 Posts: {len(s.posted_history)}\n"
                            f"🟢 Live: {live}"
                        )
                    else:
                        social_text = "📱 Social Agent\n\nStatus: Initializing..."
                except Exception as e:
                    social_text = f"📱 Social Agent\n\nStatus: {str(e)[:80]}"
                await _telegram_send_message(chat_id, social_text)

            elif query_data == "help":
                help_text = (
                    "📚 Singh Ji AI Commands\n\n"
                    "🌤️ /weather Delhi\n"
                    "📰 /news\n"
                    "🌾 /mandi UP\n"
                    "💰 /tax 500000\n"
                    "🥇 /gold Delhi\n"
                    "⛽ /fuel Delhi\n"
                    "🔮 /horoscope मेष\n"
                    "💱 /currency USD INR 100\n"
                    "🔍 /search AI news\n"
                    "🔤 /translate en Namaste\n"
                    "🚨 /emergency police\n"
                    "💳 /upi\n"
                    "💧 /pani\n"
                    "🚽 /sewer\n"
                    "🏛️ /govt aadhaar\n"
                    "💼 /rozgar software IN\n"
                    "📋 /yojana 30 100000 farmer\n"
                    "🤖 /ai question\n"
                    "📢 /broadcast message (admin only)"
                )
                await _telegram_send_message(chat_id, help_text)

            # --- NEW CALLBACKS v8.3 ---
            elif query_data == "ai_chat_v2":
                await _telegram_send_message(chat_id, "🤖 AI Chat v2\n\nKuch bhi poochho! Advanced AI with Groq/Gemini/Cerebras failover.\n\nExample: /ai_v2 India ka capital kya hai?")

            elif query_data == "analytics":
                active_count = sum(1 for v in MODULES.values() if v["active"])
                total_count = len(MODULES)
                await _telegram_send_message(chat_id, f"📊 Analytics\n\nTotal Modules: {total_count}\nActive: {active_count}\nInactive: {total_count - active_count}\n\nSab kuch track ho raha hai!")

            elif query_data == "voice_system":
                await _telegram_send_message(chat_id, "🎙️ Voice System\n\nVoice message bhejo!\n• Transcribe (Whisper)\n• AI Response\n• TTS Reply\n\nBolo Singh Ji!")

            elif query_data == "singhji_tv":
                await _telegram_send_message(chat_id, "📺 SinghJi TV\n\nLive channels:\n• Educational\n• News\n• Health\n• Entertainment\n\n/channel educational")

            elif query_data == "plant_id":
                await _telegram_send_message(chat_id, "🌿 Plant Doctor\n\nPlant ki photo bhejo!\n• Disease detect karunga\n• Treatment bataunga\n• Healthy hai toh bataunga\n\nPhoto bhejo directly!")

            elif query_data == "trolley":
                await _telegram_send_message(chat_id, "🛒 Trolley\n\nShopping Cart:\n• Products dekho\n• Cart mein add karo\n• Order karo\n\n/trolley products")

            elif query_data == "supreme":
                await _telegram_send_message(chat_id, "🔮 Supreme AI\n\nAdvanced AI Agent:\n• Multi-model brain\n• Memory system\n• Voice clone\n• Real-time calls\n\n/supreme start")

            elif query_data == "meta_agent":
                await _telegram_send_message(chat_id, "📡 Meta Agent\n\nMeta-level AI:\n• Agent orchestration\n• Task delegation\n• Performance tracking\n\n/meta status")

            elif query_data == "supabase_memory":
                await _telegram_send_message(chat_id, "💾 Supabase Memory\n\nCloud Memory:\n• Save kuch bhi\n• Recall anytime\n• Cross-device sync\n\n/memory save key value")

            elif query_data == "language_hub":
                await _telegram_send_message(chat_id, "🔤 Language Hub\n\nLanguages supported:\n• Hindi\n• English\n• Bengali\n• Telugu\n• Tamil\n• Marathi\n• Gujarati\n\n/lang hi")

            elif query_data == "whatsapp":
                await _telegram_send_message(chat_id, "💬 WhatsApp Business\n\nWhatsApp integration:\n• Business API\n• Auto-replies\n• Broadcast messages\n\n/whatsapp status")

            elif query_data == "daily_report":
                await _telegram_send_message(chat_id, "📰 Daily Report\n\nAutomated daily digest:\n• Morning 7 AM\n• Evening 6 PM\n• News + Weather + Mandi\n\n/report now")

            elif query_data == "video_gen":
                await _telegram_send_message(chat_id, "🎬 Video Generation\n\nAI Video create karo:\n• Seedance\n• Kling\n• Hailuo\n• Luma\n• Pika\n• Veo\n\n/video prompt")

            elif query_data == "swarm_v2":
                status = SMART_SWARM.get_status()
                await _telegram_send_message(chat_id, f"🧠 Smart Swarm v2\n\nTotal Agents: {status['total_registered']}\nLoaded: {status['currently_loaded']}\nActive: {status['active_running']}\nIdle: {status['idle']}\nBusy: {status['busy']}")

            return {"status": "ok"}

        # Handle regular messages
        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]

        # Register new user
        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {"language": "hi", "location": None}
            await _memory_save(f"user_pref:{user_id}", USER_PREFERENCES[user_id], table="user_memory")
            logger.info(f"✅ New user registered: {user_id}")

        # Handle pending actions (button press ke baad aaya text)
        pending = USER_PREFERENCES.get(user_id, {}).pop("waiting_for", None)
        if pending and text and not text.startswith("/"):
            pending_map = {
                "weather": "/weather ",
                "mandi": "/mandi ",
                "tax": "/tax ",
                "gold": "/gold ",
                "fuel": "/fuel ",
                "horoscope": "/horoscope ",
                "currency": "/currency ",
                "rozgar": "/rozgar ",
                "search": "/search ",
                "translate": "/translate ",
                "yojana": "/yojana ",
                "tv": "/tv ",
                "video": "/video ",
            }
            if pending in pending_map:
                text = pending_map[pending] + text.strip()

        # Rate limit check
        if _rate_check(f"tg_user:{user_id}", *RATE_LIMIT_TELEGRAM_USER):
            await _telegram_send_message(chat_id, "⏳ Please slow down! Try again in 1 minute.")
            return {"status": "ok"}

        # Process voice messages
        if "voice" in message:
            return await _handle_voice_message(chat_id, user_id, message)

        # Process photo messages
        if "photo" in message:
            return await _handle_photo_message(chat_id, message)

        # Process text commands
        if text.startswith("/"):
            return await _handle_command(chat_id, user_id, text)

        # Default: AI chat
        if GROQ_API_KEY and text:
            try:
                ai_response = await _call_groq(text)
                await _telegram_send_message(chat_id, ai_response[:4000])
                await _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {
                    "prompt": text, "response": ai_response
                })
            except Exception as e:
                await _telegram_send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")
            return {"status": "ok"}

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Telegram webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

# ==========================================
# TELEGRAM HELPER FUNCTIONS
# ==========================================
async def _handle_voice_message(chat_id, user_id, message):
    voice = message["voice"]
    file_id = voice["file_id"]
    try:
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        if file_data.get("ok"):
            file_path = file_data["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            audio_resp = await HTTP_CLIENT.get(file_url, timeout=15)
            audio_bytes = audio_resp.content

            out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".ogg", None)
            if out:
                transcript, _, _ = out
                await _telegram_send_message(chat_id, f"🎤 Transcript:\n{transcript}")
                if GROQ_API_KEY:
                    ai_text = await _call_groq(transcript)
                    await _telegram_send_message(chat_id, f"🤖 AI Response:\n{ai_text[:4000]}")
                    await _memory_save(f"telegram_voice:{user_id}:{int(time.time())}", {
                        "transcript": transcript, "response": ai_text
                    })
            else:
                await _telegram_send_message(chat_id, "❌ Whisper model not available")
        else:
            await _telegram_send_message(chat_id, "❌ Could not download voice file")
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await _telegram_send_message(chat_id, f"❌ Voice error: {str(e)[:100]}")
    return {"status": "ok"}

async def _handle_photo_message(chat_id, message):
    try:
        photos = message["photo"]
        file_id = photos[-1]["file_id"]
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        if file_data.get("ok"):
            file_path = file_data["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            img_resp = await HTTP_CLIENT.get(file_url, timeout=15)
            img_b64 = base64.b64encode(img_resp.content).decode("utf-8")
            await _telegram_send_message(chat_id, "🌿 Analyzing plant...")

            from modules.kisaan_doctor.handler import _detect_disease
            result = await _detect_disease(img_b64)
            if result is None:
                await _telegram_send_message(chat_id, "❌ Plant ID API key not set")
            elif result["is_healthy"]:
                await _telegram_send_message(chat_id, f"✅ Plant looks healthy! ({result['health_probability']:.0%%})")
            else:
                plant_text = "🌿 Disease Detection Result\n\n"
                for d in result["diseases"]:
                    plant_text += f"🔴 {d['name']} ({d['probability']:.0%%})\n{d['description'][:200]}\n\n"
                await _telegram_send_message(chat_id, plant_text[:4000])
        else:
            await _telegram_send_message(chat_id, "❌ Could not download photo")
    except Exception as e:
        logger.error(f"Plant detect error: {e}")
        await _telegram_send_message(chat_id, f"❌ Plant detection error: {str(e)[:100]}")
    return {"status": "ok"}

async def _handle_command(chat_id, user_id, text):
    if text == "/start":
        welcome = "🌅 Welcome to Singh Ji AI Ultra v8.0!\n\nI'm your AI assistant. Use the buttons below or commands like /help"
        await _telegram_send_message(chat_id, welcome, MAIN_KEYBOARD)
        return {"status": "ok"}

    elif text == "/help":
        help_text = (
            "📚 Commands:\n\n"
            "/weather city - Get weather\n"
            "/news - Latest news\n"
            "/mandi state - Mandi prices\n"
            "/tax income - Tax calculation\n"
            "/status - System status\n"
            "/ai question - AI chat\n"
            "/gold city - Gold rates\n"
            "/fuel city - Fuel prices\n"
            "/horoscope rashi - Daily horoscope\n"
            "/currency USD INR 100 - Currency convert\n"
            "/translate en text - Translate\n"
            "/emergency type - Emergency numbers\n"
            "/upi - UPI information\n"
            "/search query - Web search\n"
            "/rozgar keyword country - Jobs"
        )
        await _telegram_send_message(chat_id, help_text)
        return {"status": "ok"}

    elif text == "/status":
        status = SMART_SWARM.get_status()
        status_text = (
            f"📊 Status\n\n"
            f"Agents: {status['currently_loaded']}/330\n"
            f"Active: {status['active_running']}\n"
            f"Idle: {status['idle']}\n"
            f"APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}\n"
            f"Users: {len(USER_PREFERENCES)}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        await _telegram_send_message(chat_id, status_text)
        return {"status": "ok"}

    elif text.startswith("/weather "):
        city = text.replace("/weather ", "").strip()
        if OPENWEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                resp = await HTTP_CLIENT.get(url)
                data = resp.json()
                if resp.status_code == 200:
                    weather_text = (
                        f"🌤️ Weather in {city}\n\n"
                        f"🌡️ Temp: {data['main']['temp']}°C\n"
                        f"💧 Humidity: {data['main']['humidity']}%%\n"
                        f"🌬️ Wind: {data['wind']['speed']} m/s\n"
                        f"☁️ {data['weather'][0]['description'].title()}"
                    )
                    await _telegram_send_message(chat_id, weather_text)
                else:
                    await _telegram_send_message(chat_id, f"❌ City not found: {city}")
            except Exception as e:
                await _telegram_send_message(chat_id, f"❌ Weather error: {str(e)[:100]}")
        else:
            await _telegram_send_message(chat_id, "❌ Weather API key missing")
        return {"status": "ok"}

    elif text == "/news":
        try:
            import modules.news.handler as news_module
            news_text = "📰 Latest News\n\n" + await news_module.get_news_digest_text(count=5)
            await _telegram_send_message(chat_id, news_text)
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ News error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/mandi "):
        raw_state = text.replace("/mandi ", "").strip()
        state = _normalize_state(raw_state)
        if MANDI_API_KEY:
            try:
                params = {"api-key": MANDI_API_KEY, "format": "json", "limit": 10, "filters[state.keyword]": state}
                resp = await HTTP_CLIENT.get(MANDI_BASE_URL, params=params, timeout=45)
                data = resp.json()

                if "error" in data:
                    await _telegram_send_message(chat_id, f"❌ Mandi API error: {data.get('error', 'Unknown')}")
                    return {"status": "ok"}

                records = data.get("records", [])
                if not records:
                    await _telegram_send_message(chat_id, f"❌ {state} ke liye data nahi mila\n\nTry karo:\n/mandi Punjab\n/mandi Haryana\n/mandi UP")
                    return {"status": "ok"}

                mandi_text = f"🌾 Mandi Bhav — {state}\n\n"
                for i, record in enumerate(records[:5], 1):
                    commodity = record.get("commodity", "Unknown")
                    modal = record.get("modal_price", "N/A")
                    min_p = record.get("min_price", "N/A")
                    max_p = record.get("max_price", "N/A")
                    market = record.get("market", "N/A")
                    district = record.get("district", "N/A")
                    mandi_text += f"{i}. {commodity}\n"
                    mandi_text += f"   ₹{modal}/q (₹{min_p}-₹{max_p})\n"
                    mandi_text += f"   📍 {market}, {district}\n\n"
                await _telegram_send_message(chat_id, mandi_text)
            except (httpx.TimeoutException, asyncio.TimeoutError):
                await _telegram_send_message(chat_id, "❌ Mandi data.gov.in अभी धीमा है, थोड़ी देर बाद कोशिश करें\n\nFormat: /mandi Uttar Pradesh")
            except Exception as e:
                error_text = str(e) or type(e).__name__
                await _telegram_send_message(chat_id, f"❌ Mandi error: {error_text[:100]}\n\nFormat: /mandi Uttar Pradesh")
        else:
            await _telegram_send_message(chat_id, "❌ Mandi API key missing")
        return {"status": "ok"}

    elif text.startswith("/tax "):
        try:
            income = float(text.replace("/tax ", "").strip())
            r = _calculate_tax(income, "new")
            tax_text = (
                f"💰 Tax Calculation\n\n"
                f"Income: ₹{r['income']:,.0f}\n"
                f"Tax: ₹{r['tax']:,.2f}\n"
                f"Cess: ₹{r['cess']:,.2f}\n"
                f"Total: ₹{r['total']:,.2f}\n"
                f"Take Home: ₹{r['take_home']:,.2f}"
            )
            await _telegram_send_message(chat_id, tax_text)
        except Exception:
            await _telegram_send_message(chat_id, "❌ Invalid income. Example: /tax 500000")
        return {"status": "ok"}

    elif text.startswith("/gold"):
        city = text.replace("/gold", "").strip() or "delhi"
        try:
            resp = await gold_rate_city(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            cr = d.get("city_rates", {})
            gold_text = (
                f"🥇 Gold Rate - {cr.get('city', city.title())}\n\n"
                f"24K (1g): ₹{cr.get('price_gram_24k', 'N/A')}\n"
                f"22K (1g): ₹{cr.get('price_gram_22k', 'N/A')}\n"
                f"24K (10g): ₹{cr.get('price_10g_24k', 'N/A')}\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await _telegram_send_message(chat_id, gold_text)
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Gold error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/fuel"):
        city = text.replace("/fuel", "").strip() or "delhi"
        try:
            resp = await fuel_price(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            fuel_text = (
                f"⛽ Fuel Price - {d.get('city', city.title())}\n\n"
                f"Petrol: ₹{d.get('petrol', 'N/A')}/L\n"
                f"Diesel: ₹{d.get('diesel', 'N/A')}/L\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await _telegram_send_message(chat_id, fuel_text)
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Fuel error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/horoscope"):
        rashi = text.replace("/horoscope", "").strip() or "मेष"
        try:
            h = get_horoscope(rashi, "daily", "hi")
            horo_text = _format_horoscope_telegram(h)
            await _telegram_send_message(chat_id, horo_text)
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Horoscope error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/currency"):
        parts = text.replace("/currency", "").strip().split()
        try:
            if len(parts) == 1:
                try:
                    amount = float(parts[0])
                    base, target = "USD", "INR"
                except ValueError:
                    base, target, amount = parts[0].upper(), "INR", 1.0
            else:
                base = parts[0].upper() if len(parts) > 0 else "USD"
                target = parts[1].upper() if len(parts) > 1 else "INR"
                amount = float(parts[2]) if len(parts) > 2 else 1.0
            result = await singhji_currency.convert(base, target, amount)
            cur_text = (
                f"💱 Currency Convert\n\n"
                f"{amount} {base} = {result.converted} {target}\n"
                f"Rate: 1 {base} = {result.rate} {target}"
            )
            await _telegram_send_message(chat_id, cur_text)
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Currency error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/rozgar"):
        raw = text.replace("/rozgar", "").strip()
        parts = raw.split()
        known_countries = set(rozgar_module.PORTALS["regional"].keys())
        country = ""
        keyword_parts = []
        for p in parts:
            if p.upper() in known_countries and not country:
                country = p.upper()
            else:
                keyword_parts.append(p)
        keyword = " ".join(keyword_parts).strip().lower()
        try:
            search_term = rozgar_module.KEYWORD_MAP.get(keyword, keyword) if keyword else ""
            if keyword and country:
                result = rozgar_module._search_keyword(keyword, search_term)
                result = rozgar_module._filter_by_country(result, country)
            elif keyword:
                result = rozgar_module._search_keyword(keyword, search_term)
            elif country:
                result = rozgar_module._country_only(country)
            else:
                result = {"global": [], "regional": [], "govt": [], "categories": []}

            rozgar_text = "💼 Rozgar/Jobs\n\n"
            for section, label in [("govt", "🏛️ Government"), ("regional", "📍 Regional"), ("global", "🌐 Global")]:
                for entry in result.get(section, [])[:5]:
                    name = entry.get("name", "")
                    site = entry.get("site", "")
                    rozgar_text += f"{label}: {name} — {site}\n"
            if not any(result.get(s) for s in ("govt", "regional", "global")):
                rozgar_text += "No results found. Example: /rozgar software IN"
            await _telegram_send_message(chat_id, rozgar_text[:4000])
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Rozgar error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/translate "):
        parts = text.replace("/translate ", "").strip().split(" ", 1)
        try:
            target_lang = parts[0].lower()
            to_translate = parts[1] if len(parts) > 1 else ""
            if not to_translate:
                await _telegram_send_message(chat_id, "Format: /translate en Namaste kaise ho")
                return {"status": "ok"}
            result = await run_in_threadpool(LANG_MODULE.translate, to_translate, target_lang, "auto")
            if result.get("success"):
                await _telegram_send_message(chat_id, f"🔤 Translation ({result.get('target_name', target_lang)})\n\n{result['translated']}")
            else:
                await _telegram_send_message(chat_id, f"❌ Translate error: {result.get('error', 'unknown')[:100]}")
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ Translate error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text.startswith("/emergency"):
        type_ = text.replace("/emergency", "").strip().lower()
        if type_ and type_ in EMERGENCY_DATA:
            v = EMERGENCY_DATA[type_]
            emg_text = f"🚨 {type_.title()}\n\nNumber: {v['number']}"
            if v.get("alt"):
                emg_text += f"\nAlt: {v['alt']}"
            emg_text += f"\n{v.get('info', '')}"
        else:
            emg_text = "🚨 Emergency Numbers\n\n"
            for k, v in EMERGENCY_DATA.items():
                emg_text += f"{k.title()}: {v['number']}"
                if v.get("alt"):
                    emg_text += f" / {v['alt']}"
                emg_text += "\n"
        await _telegram_send_message(chat_id, emg_text)
        return {"status": "ok"}

    elif text == "/upi":
        upi_id = os.getenv("UPI_ID", "jp200883@sbi")
        upi_text = f"💳 UPI Info\n\nUPI ID: {upi_id}\nApps: PhonePe, Google Pay, Paytm, BHIM\nDaily Limit: ₹1,00,000"
        await _telegram_send_message(chat_id, upi_text)
        return {"status": "ok"}

    elif text.startswith("/search "):
        query = text.replace("/search ", "").strip()
        if TAVILY_API_KEY:
            try:
                url = "https://api.tavily.com/search"
                payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 5}
                resp = await HTTP_CLIENT.post(url, json=payload, timeout=15)
                data = resp.json()
                results = data.get("results", [])[:5]
                search_text = f"🔍 Search: {query}\n\n"
                for i, r in enumerate(results, 1):
                    search_text += f"{i}. {r.get('title', 'No title')}\n   {r.get('url', '')}\n\n"
                if not results:
                    search_text += "No results found"
                await _telegram_send_message(chat_id, search_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"❌ Search error: {str(e)[:100]}")
        else:
            await _telegram_send_message(chat_id, "❌ Search API key missing")
        return {"status": "ok"}

    elif text.startswith("/ai "):
        prompt = text.replace("/ai ", "").strip()
        if GROQ_API_KEY:
            try:
                ai_response = await _call_groq(prompt)
                await _telegram_send_message(chat_id, f"🤖 AI Response:\n\n{ai_response[:4000]}")
                await _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {
                    "prompt": prompt, "response": ai_response
                })
            except Exception as e:
                await _telegram_send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")
        else:
            await _telegram_send_message(chat_id, "❌ Groq API key missing")
        return {"status": "ok"}

    elif text.startswith("/broadcast "):
        if user_id != ADMIN_USER_ID:
            await _telegram_send_message(chat_id, "⛔ Admin only command")
            return {"status": "ok"}
        broadcast_text = text.replace("/broadcast ", "").strip()
        if MASTER_SCHEDULER:
            await MASTER_SCHEDULER._broadcast_with_rate_limit(f"📢 Broadcast\n\n{broadcast_text}")
            await _telegram_send_message(chat_id, f"✅ Broadcast sent to {len(USER_PREFERENCES)} users")
        else:
            await _telegram_send_message(chat_id, "❌ Scheduler not initialized")
        return {"status": "ok"}


    # --- NEW COMMANDS v8.3 ---
    elif text == "/ai_v2" or text.startswith("/ai_v2 "):
        prompt = text.replace("/ai_v2", "").strip()
        if not prompt:
            await _telegram_send_message(chat_id, "🤖 AI Chat v2\n\nKuch bhi poochho!\nExample: /ai_v2 India ka capital kya hai?")
            return {"status": "ok"}
        try:
            # Try Groq first, then Gemini, then Cerebras
            response = None
            if GROQ_API_KEY:
                response = await _call_groq(prompt)
            elif GEMINI_API_KEY:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                resp = await HTTP_CLIENT.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                result = resp.json()
                response = result["candidates"][0]["content"]["parts"][0]["text"]
            elif CEREBRAS_API_KEY:
                resp = await HTTP_CLIENT.post("https://api.cerebras.ai/v1/chat/completions", headers={"Authorization": f"Bearer {CEREBRAS_API_KEY}"}, json={"model": "llama-3.1-8b", "messages": [{"role": "user", "content": prompt}]}, timeout=30)
                result = resp.json()
                response = result["choices"][0]["message"]["content"]
            if response:
                await _telegram_send_message(chat_id, f"🤖 AI v2 ({'Groq' if GROQ_API_KEY else 'Gemini' if GEMINI_API_KEY else 'Cerebras'}):\n\n{response[:4000]}")
            else:
                await _telegram_send_message(chat_id, "❌ Koi AI API key set nahi hai")
        except Exception as e:
            await _telegram_send_message(chat_id, f"❌ AI v2 error: {str(e)[:100]}")
        return {"status": "ok"}

    elif text == "/channel" or text.startswith("/channel "):
        category = text.replace("/channel", "").strip() or "educational"
        await _telegram_send_message(chat_id, f"📺 SinghJi TV — {category.title()}\n\nChannel list loading...\nAPI: /api/singhji_tv/{category}")
        return {"status": "ok"}

    elif text == "/trolley" or text.startswith("/trolley "):
        action = text.replace("/trolley", "").strip() or "products"
        await _telegram_send_message(chat_id, f"🛒 Trolley — {action.title()}\n\n• Wheat, Rice, Sugar, Oil, Dal, Salt, Onion, Potato\n\nAPI: /api/trolley")
        return {"status": "ok"}

    elif text == "/supreme" or text.startswith("/supreme "):
        await _telegram_send_message(chat_id, "🔮 Supreme AI Agent\n\nAdvanced features:\n• Multi-model AI brain\n• Long-term memory\n• Voice cloning\n• Real-time phone calls\n\nAPI: /api/supreme")
        return {"status": "ok"}

    elif text == "/meta" or text.startswith("/meta "):
        await _telegram_send_message(chat_id, "📡 Meta Agent\n\nMeta-level orchestration:\n• Agent management\n• Task routing\n• Performance analytics\n\nAPI: /api/meta")
        return {"status": "ok"}

    elif text == "/memory" or text.startswith("/memory "):
        parts = text.replace("/memory", "").strip().split(" ", 1)
        if len(parts) >= 2 and parts[0] == "save":
            kv = parts[1].split(" ", 1)
            if len(kv) == 2:
                await _memory_save(kv[0], kv[1])
                await _telegram_send_message(chat_id, f"💾 Saved: {kv[0]} = {kv[1][:50]}")
            else:
                await _telegram_send_message(chat_id, "Format: /memory save key value")
        elif len(parts) >= 1 and parts[0] == "get":
            if len(parts) >= 2:
                result = await _memory_get(parts[1])
                if result["exists"]:
                    await _telegram_send_message(chat_id, f"💾 {parts[1]}: {str(result['data'])[:500]}")
                else:
                    await _telegram_send_message(chat_id, f"❌ {parts[1]} not found")
            else:
                await _telegram_send_message(chat_id, "Format: /memory get key")
        else:
            await _telegram_send_message(chat_id, "💾 Supabase Memory\n\n/memory save key value\n/memory get key")
        return {"status": "ok"}

    elif text == "/lang" or text.startswith("/lang "):
        lang = text.replace("/lang", "").strip()
        if lang in ["hi", "en", "bn", "te", "ta", "mr", "gu"]:
            USER_PREFERENCES[user_id]["language"] = lang
            await _memory_save(f"user_pref:{user_id}", USER_PREFERENCES[user_id], table="user_memory")
            lang_names = {"hi": "Hindi", "en": "English", "bn": "Bengali", "te": "Telugu", "ta": "Tamil", "mr": "Marathi", "gu": "Gujarati"}
            await _telegram_send_message(chat_id, f"🔤 Language set to: {lang_names.get(lang, lang)}")
        else:
            await _telegram_send_message(chat_id, "🔤 Language Hub\n\nSupported:\n• hi — Hindi\n• en — English\n• bn — Bengali\n• te — Telugu\n• ta — Tamil\n• mr — Marathi\n• gu — Gujarati\n\nExample: /lang hi")
        return {"status": "ok"}

    elif text == "/whatsapp" or text.startswith("/whatsapp "):
        await _telegram_send_message(chat_id, "💬 WhatsApp Business\n\nFeatures:\n• Business API\n• Auto-replies\n• Broadcast\n• Status check\n\nAPI: /api/whatsapp")
        return {"status": "ok"}

    elif text == "/report" or text.startswith("/report "):
        await _telegram_send_message(chat_id, "📰 Daily Report\n\nSchedules:\n• Morning: 7:00 AM\n• Evening: 6:00 PM\n• Flood Watch: Every 6 hours\n• Govt Schemes: Tue/Fri 3 PM\n\nAPI: /api/daily_report")
        return {"status": "ok"}

    elif text == "/video" or text.startswith("/video "):
        prompt = text.replace("/video", "").strip()
        if not prompt:
            await _telegram_send_message(chat_id, "🎬 Video Generation\n\nPlatforms:\n• Seedance\n• Kling\n• Hailuo\n• Luma\n• Pika\n• Veo\n\nExample: /video Indian farmer in field")
            return {"status": "ok"}
        await _telegram_send_message(chat_id, f"🎬 Generating video...\n\nPrompt: {prompt[:100]}\n\nAPI: /api/video/generate")
        return {"status": "ok"}

    elif text == "/swarm" or text.startswith("/swarm "):
        status = SMART_SWARM.get_status()
        swarm_text = (
            f"🧠 Smart Swarm Status\n\n"
            f"Total: {status['total_registered']}\n"
            f"Loaded: {status['currently_loaded']}\n"
            f"Active: {status['active_running']}\n"
            f"Idle: {status['idle']}\n"
            f"Busy: {status['busy']}"
        )
        await _telegram_send_message(chat_id, swarm_text)
        return {"status": "ok"}

    elif text == "/modules" or text.startswith("/modules"):
        active = [n for n, i in MODULES.items() if i["active"]]
        inactive = [n for n, i in MODULES.items() if not i["active"]]
        mod_text = f"📦 Modules ({len(active)}/{len(MODULES)} Active)\n\n✅ Active:\n"
        for m in active[:15]:
            mod_text += f"• {m}\n"
        if inactive:
            mod_text += "\n❌ Inactive:\n"
            for m in inactive[:10]:
                mod_text += f"• {m}\n"
        await _telegram_send_message(chat_id, mod_text[:4000])
        return {"status": "ok"}

    elif text == "/apis" or text.startswith("/apis"):
        live = [k for k, v in AVAILABLE_KEYS.items() if v]
        missing = [k for k, v in AVAILABLE_KEYS.items() if not v]
        api_text = f"🔑 API Keys ({len(live)}/{len(AVAILABLE_KEYS)} Set)\n\n✅ Set:\n"
        for k in live:
            api_text += f"• {k}\n"
        if missing:
            api_text += "\n❌ Missing:\n"
            for k in missing:
                api_text += f"• {k}\n"
        await _telegram_send_message(chat_id, api_text[:4000])
        return {"status": "ok"}

    elif text == "/voice" or text.startswith("/voice "):
        await _telegram_send_message(chat_id, "🎙️ Voice Commands\n\n• /voice transcribe — Audio to text\n• /voice tts — Text to speech\n• /voice clone — Voice clone\n• Voice message bhejo directly!\n\nAPI: /api/voice")
        return {"status": "ok"}

    elif text == "/train" or text.startswith("/train "):
        pnr = text.replace("/train", "").strip()
        if pnr:
            await _telegram_send_message(chat_id, f"🚂 PNR Status: {pnr}\n\nChecking...\nAPI: /api/train/pnr/{pnr}")
        else:
            await _telegram_send_message(chat_id, "🚂 Train Services\n\n• /train PNR_NUMBER — PNR status\n• /train track TRAIN_NO — Live tracking\n\nAPI: /api/train")
        return {"status": "ok"}

    else:
        await _telegram_send_message(chat_id, "❌ Unknown command. Type /help for available commands")
        return {"status": "ok"}

# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=False
    )
