from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
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
import httpx
import logging
from collections import defaultdict, deque
import threading
import sqlite3
from typing import Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from modules.kisaan_doctor.handler import router as kisaan_router
from modules.sarkari_yojana.handler import router as yojana_router
from modules.banking.handler import handler as banking_handler
from modules.currency.handler import router as currency_router, singhji_currency
from modules.aavishkar.handler import router as aavishkar_router
from modules.goldrate.handler import router as goldrate_router, gold_rate_city
from modules.fuel.handler import router as fuel_router, fuel_price
from modules.horoscope.handler import get_horoscope, format_telegram as _format_horoscope_telegram
from modules.language.handler import LanguageModule
from modules.emergency.handler import EMERGENCY_DATA
from modules.govt.handler import GOVT_DATA
from modules.trishul.handler import router as trishul_router
from modules.scheme_swarm.api_routes import router as scheme_swarm_router, engine as scheme_engine
from modules.scheme_swarm.eligibility import UserProfile
from modules.pani.handler import handler as pani_handler
from modules.sewer.handler import handler as sewer_handler
from modules.upi.handler import handler as upi_handler
from modules.guard_agent.handler import router as guard_router
from modules.oauth_connector.handler import router as oauth_router
from modules.social_agent.handler import router as social_router
import modules.social_agent.core as social_core
from modules.news.handler import router as news_router
from miniprogram.portal import router as miniprogram_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)   # token URLs अब लॉग में नहीं दिखेंगे

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

MAX_B64_BYTES = 10 * 1024 * 1024

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

SUPABASE_CLIENT = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase connected")
except Exception as e:
    logger.warning(f"Supabase init failed: {e}")

HTTP_CLIENT = None

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

MEMORY_STORE = {}
MAX_MEMORY_SIZE = 1000

def _check_memory_limit():
    if len(MEMORY_STORE) > MAX_MEMORY_SIZE:
        keys_to_remove = list(MEMORY_STORE.keys())[:int(MAX_MEMORY_SIZE * 0.2)]
        for k in keys_to_remove:
            del MEMORY_STORE[k]
        logger.info(f"Memory cleaned: removed {len(keys_to_remove)} old entries")

USER_PREFERENCES = {}

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

# ─── FIX #1: Startup पर subscriber लिस्ट Supabase से वापस लोड करो ─────
def _load_user_preferences_sync() -> Dict[int, Any]:
    """
    _memory_save() हर नए Telegram user को key=f"user_pref:{user_id}" के
    साथ table "user_memory" में सेव करता है। यह फ़ंक्शन वही रिकॉर्ड
    वापस पढ़कर USER_PREFERENCES (RAM dict) में भर देता है, ताकि restart के
    बाद भी broadcast/scheduler को पुराने सब्सक्राइबर दिखें।
    """
    loaded: Dict[int, Any] = {}
    if not SUPABASE_CLIENT:
        logger.warning("[STARTUP] Supabase कनेक्ट नहीं है — subscriber लिस्ट सिर्फ़ नए messages से बनेगी")
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
    except Exception as e:
        logger.error(f"[STARTUP] User preferences reload failed: {e}")
    return loaded

def _check_admin_auth(request):
    if not ADMIN_API_KEY:
        return True
    provided = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    return provided == ADMIN_API_KEY

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
    "miniprogram": {"needs_key": None, "active": True},
    "currency": {"needs_key": None, "active": True},
    "kisaan_doctor": {"needs_key": None, "active": True},
    "sarkari_yojana": {"needs_key": None, "active": True},
    "banking": {"needs_key": None, "active": True},
}

_rate_lock = threading.Lock()
_rate_buckets = defaultdict(deque)

RATE_LIMIT_GLOBAL = (60, 60)
RATE_LIMIT_STRICT = (8, 60)
STRICT_PATH_PREFIXES = (
    "/api/chat",
    "/api/whisper/",
    "/api/bhashini/",
    "/api/tts",
    "/api/plant/",
    "/modules/voice",
)
RATE_LIMITED_PREFIXES = ("/api/", "/modules/")

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

RATE_LIMIT_TELEGRAM_USER = (15, 60)

# Telegram helpers (moved up for scheduler access)
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def _telegram_send_message(chat_id, text, reply_markup=None, parse_mode=None):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    try:
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        resp = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
        result = resp.json()
        if not result.get("ok"):
            logger.error(f"[TELEGRAM SEND FAIL] chat_id={chat_id} | {result}")
        return result
    except Exception as e:
        logger.error(f"[TELEGRAM SEND EXCEPTION] chat_id={chat_id} | {e}")
        return {"error": str(e)}

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

# ─── FIX #2: Startup पर पता लगाओ Telegram असल में किस webhook को कॉल कर रहा है ──
async def _check_webhook_config():
    """
    इस फ़ाइल में /telegram/webhook (पूरी फ़ीचर वाला हैंडलर — commands, voice,
    AI chat, broadcast सब यहीं है) और modules/telegram_bot/handler.py का
    router /modules/telegram_bot/webhook पर mount है — दोनों एक साथ मौजूद
    हैं। Telegram सिर्फ़ एक ही URL पर webhook भेज सकता है, इसलिए startup पर
    getWebhookInfo चेक करके लॉग में साफ़ बता देता है कौन एक्टिव है।
    """
    if not TELEGRAM_TOKEN or not HTTP_CLIENT:
        return
    try:
        resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=10)
        info = resp.json().get("result", {})
        url = info.get("url", "")
        logger.info(f"[WEBHOOK CHECK] Telegram में सेट webhook URL: {url or '(कोई नहीं सेट)'}")

        if not url:
            logger.warning("[WEBHOOK CHECK] कोई webhook सेट नहीं है — बॉट को कोई भी अपडेट नहीं मिल रहा")
        elif url.rstrip("/").endswith("/modules/telegram_bot/webhook"):
            logger.warning(
                "[WEBHOOK CHECK] Telegram /modules/telegram_bot/webhook (telegram_router) को कॉल कर रहा है — "
                "इस फ़ाइल का पूरा /telegram/webhook हैंडलर (commands, voice, AI chat, broadcast) "
                "इस्तेमाल ही नहीं हो रहा! या तो setWebhook को /telegram/webhook पर repoint करें, "
                "या पुष्टि करें कि modules/telegram_bot/handler.py में बराबर की लॉजिक है।"
            )
        elif url.rstrip("/").endswith("/telegram/webhook"):
            logger.info(
                "[WEBHOOK CHECK] ठीक है — Telegram इसी फ़ाइल के /telegram/webhook को कॉल कर रहा है। "
                "/modules/telegram_bot/webhook (telegram_router में) फ़िलहाल dead code है, चाहें तो हटा सकते हैं।"
            )
        else:
            logger.warning(f"[WEBHOOK CHECK] अनजान webhook URL — मैन्युअल जाँच करें: {url}")
    except Exception as e:
        logger.warning(f"[WEBHOOK CHECK] getWebhookInfo कॉल फेल: {e}")

# ─── FIX #4 (नया): हर startup पर Telegram को अपने आप सही webhook पर पॉइंट करो ──
async def _ensure_correct_webhook():
    """
    Telegram को हमेशा इसी फाइल के /telegram/webhook पर पॉइंट रखता है —
    ताकि modules/telegram_bot/webhook (जो USER_PREFERENCES में यूज़र सेव
    नहीं करता, इसलिए broadcast को कभी recipient नहीं मिलता) कभी गलती से
    एक्टिव न रह जाए। Railway पर APP_URL env var (पूरा https URL) सेट
    होना ज़रूरी है, वरना यह फंक्शन सिर्फ़ warning देकर रुक जाएगा।
    """
    if not TELEGRAM_TOKEN or not HTTP_CLIENT:
        return
    app_url = os.getenv("APP_URL", "")
    if not app_url:
        logger.warning("[WEBHOOK FIX] APP_URL env var सेट नहीं है — webhook auto-set स्किप हुआ")
        return
    correct_url = f"{app_url.rstrip('/')}/telegram/webhook"
    try:
        resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=10)
        current_url = resp.json().get("result", {}).get("url", "")
        if current_url.rstrip("/") == correct_url.rstrip("/"):
            logger.info(f"[WEBHOOK FIX] पहले से सही सेट है: {correct_url}")
            return
        set_resp = await HTTP_CLIENT.get(
            f"{TELEGRAM_API_BASE}/setWebhook",
            params={"url": correct_url},
            timeout=10
        )
        result = set_resp.json()
        if result.get("ok"):
            logger.info(f"[WEBHOOK FIX] Webhook सही जगह सेट हुआ: {correct_url}")
        else:
            logger.error(f"[WEBHOOK FIX] setWebhook फेल: {result}")
    except Exception as e:
        logger.error(f"[WEBHOOK FIX] Webhook auto-fix में त्रुटि: {e}")

MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "Weather", "callback_data": "weather"}, {"text": "News", "callback_data": "news"}],
        [{"text": "Mandi Bhav", "callback_data": "mandi"}, {"text": "AI Chat", "callback_data": "ai_chat"}],
        [{"text": "Voice", "callback_data": "voice"}, {"text": "Status", "callback_data": "status"}],
        [{"text": "Tax Calc", "callback_data": "tax"}, {"text": "Plant ID", "callback_data": "plant"}],
        [{"text": "Gold Rate", "callback_data": "gold"}, {"text": "Fuel Price", "callback_data": "fuel"}],
        [{"text": "Horoscope", "callback_data": "horoscope"}, {"text": "Currency", "callback_data": "currency"}],
        [{"text": "Emergency", "callback_data": "emergency"}, {"text": "UPI Info", "callback_data": "upi"}],
        [{"text": "🛡️ Guard Agent", "callback_data": "guard"}, {"text": "📱 Social Agent", "callback_data": "social"}],
    ]
}

# ═══════════════════════════════════════════════════════════════
#  MASTER SCHEDULER CLASS
# ═══════════════════════════════════════════════════════════════

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
            logger.error(f"[DB] State update failed for {job_name}: {e}")

    def _job_listener(self, event):
        if event.exception:
            logger.error(f"[JOB] {event.job_id} CRASHED: {event.exception}")
            self._update_state(event.job_id, "failed")
        else:
            logger.info(f"[JOB] {event.job_id} OK")
            self._update_state(event.job_id, "success")

    async def _broadcast(self, message, parse_mode=None):
        if not self.users:
            logger.warning("[BROADCAST] No users to send to")
            return
        user_ids = list(self.users.keys())
        sem = asyncio.Semaphore(20)
        async def _send_one(uid):
            async with sem:
                try:
                    await self.send_tg(uid, message, parse_mode=parse_mode)
                except Exception as e:
                    logger.warning(f"[BROADCAST] Failed for {uid}: {e}")
        await asyncio.gather(*(_send_one(uid) for uid in user_ids))
        logger.info(f"[BROADCAST] Sent to {len(user_ids)} users")

    async def _fetch_news(self, count=5):
        try:
            import modules.news.handler as news_module
            return await news_module.get_news_digest_text(count=count)
        except Exception as e:
            logger.warning(f"[NEWS] fail: {e}")
            return "• कोई समाचार उपलब्ध नहीं (API limit हो सकती है)"

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
                    f"💧 नमी: {data['main']['humidity']}%\n"
                    f"🌬️ हवा: {data['wind']['speed']} m/s\n"
                    f"☁️ {data['weather'][0]['description'].title()}"
                )
            return f"• Weather error: {data.get('message', 'Unknown')}"
        except Exception as e:
            logger.warning(f"[WEATHER] Error: {e}")
            return "• Weather fetch failed"

    async def _job_morning_digest(self):
        logger.info("[JOB] Morning Digest starting...")
        news = await self._fetch_news(5)
        weather = await self._fetch_weather("Delhi")
        msg = (
            f"🌅 <b>Singh Ji Morning Digest</b>\n"
            f"📅 {datetime.now().strftime('%d %b %Y, %A')}\n"
            f"{'─' * 28}\n\n"
            f"📰 <b>मुख्य समाचार:</b>\n{news}\n\n"
            f"🌤️ <b>मौसम (Delhi):</b>\n{weather}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("morning_digest", "success", "Tomorrow 07:00 AM")
        logger.info("[JOB] Morning Digest DONE")

    async def _job_evening_digest(self):
        logger.info("[JOB] Evening Digest starting...")
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
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("evening_digest", "success", "Tomorrow 06:00 PM")
        logger.info("[JOB] Evening Digest DONE")

    async def _job_govt_schemes(self):
        logger.info("[JOB] Govt Schemes starting...")
        content = (
            "• <b>PM Awas Yojana:</b> नई लिस्ट जारी — अपना नाम चेक करें\n"
            "• <b>Ration Card:</b> e-KYC deadline बढ़ी — 31 Aug 2026\n"
            "• <b>Kisan Samman Nidhi:</b> 18वीं किस्त जल्द आएगी"
        )
        msg = (
            f"🏛️ <b>सरकारी योजना अपडेट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("govt_schemes", "success")
        logger.info("[JOB] Govt Schemes DONE")

    async def _job_banking_weekly(self):
        logger.info("[JOB] Banking Update starting...")
        content = (
            "• <b>SBI FD Rates:</b> 7.10% (5+ years)\n"
            "• <b>Post Office:</b> New digital savings scheme launched\n"
            "• <b>RBI:</b> UPI limit for medical payments increased"
        )
        msg = (
            f"🏦 <b>बैंकिंग साप्ताहिक अपडेट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("banking_weekly", "success")
        logger.info("[JOB] Banking DONE")

    async def _job_fb_token_check(self):
        logger.info("[JOB] Facebook Token Check starting...")
        try:
            import modules.social_agent.core as social_core
            if social_core.SOCIAL_AGENT:
                result = await social_core.SOCIAL_AGENT.check_and_refresh_facebook_token()
                logger.info(f"[JOB] Facebook Token Check result: {result}")
                if result.get("refreshed") and self.admin_uid:
                    await self.send_tg(
                        self.admin_uid,
                        f"🔑 <b>Facebook Token Auto-Refresh</b>\n\n✅ नया token मिल गया, अब {result.get('new_expires_in_days', '?')} दिन और चलेगा"
                    )
                elif result.get("error") == "no_app_credentials" and self.admin_uid:
                    await self.send_tg(
                        self.admin_uid,
                        "⚠️ <b>Facebook Token जल्द Expire होगा</b>\n\nFACEBOOK_APP_ID/FACEBOOK_APP_SECRET सेट नहीं हैं इसलिए auto-refresh नहीं हो सका — Railway env vars में डालो"
                    )
        except Exception as e:
            logger.error(f"[JOB] Facebook Token Check fail: {e}")
        self._update_state("fb_token_check", "success")
        logger.info("[JOB] Facebook Token Check DONE")

    async def _job_social_promo(self):
        logger.info("[JOB] Social Promo starting...")
        try:
            import modules.social_agent.core as social_core
            if social_core.SOCIAL_AGENT:
                result = await social_core.SOCIAL_AGENT.create_and_publish()
                summary = f"✅ {result['success_count']}/{result['total']} platforms पर पोस्ट हो गया"
            else:
                summary = "⚠️ Social agent initialized नहीं है"
        except Exception as e:
            summary = f"💥 Social post fail: {e}"
            logger.error(f"[SOCIAL] auto-publish fail: {e}")
        if self.admin_uid:
            try:
                await self.send_tg(
                    self.admin_uid,
                    f"📱 <b>Social Media Auto-Post</b>\n\n{summary}"
                )
            except Exception as e:
                logger.warning(f"[SOCIAL] Admin notify fail: {e}")
        self._update_state("social_promo", "success")
        logger.info("[JOB] Social Promo DONE")

    async def _job_monthly_tenders(self):
        logger.info("[JOB] Monthly Tenders starting...")
        content = (
            "• <b>Road Construction:</b> NHAI tender — Last date 15 Aug\n"
            "• <b>Smart City:</b> LED lighting project — UP\n"
            "• <b>PWD:</b> Bridge repair work — Bihar"
        )
        msg = (
            f"📋 <b>मासिक टेंडर अलर्ट</b>\n"
            f"{'─' * 28}\n\n"
            f"{content}\n\n"
            f"— <i>Singh Ji AI Ultra</i>"
        )
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("monthly_tenders", "success")
        logger.info("[JOB] Tenders DONE")

    async def _self_ping(self):
        app_url = os.getenv("APP_URL", "")
        if not app_url:
            return
        try:
            r = await self.http.get(f"{app_url}/health", timeout=10)
            if r.status_code == 200:
                logger.debug("[PING] Self-ping OK")
            else:
                logger.warning(f"[PING] Self-ping status {r.status_code}")
        except Exception as e:
            logger.warning(f"[PING] Self-ping fail: {e}")

    def setup(self):
        self.scheduler.add_job(
            self._job_morning_digest,
            CronTrigger(hour=7, minute=0),
            id="morning_digest",
            name="Morning News + Weather",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        self.scheduler.add_job(
            self._job_evening_digest,
            CronTrigger(hour=18, minute=0),
            id="evening_digest",
            name="Evening News + Rozgar",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        self.scheduler.add_job(
            self._job_govt_schemes,
            CronTrigger(day_of_week="tue,fri", hour=15, minute=0),
            id="govt_schemes",
            name="Govt Schemes Update",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._job_banking_weekly,
            CronTrigger(day_of_week="mon", hour=11, minute=0),
            id="banking_weekly",
            name="Banking Weekly",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._job_social_promo,
            CronTrigger(day_of_week="mon,wed,sat", hour=10, minute=0),
            id="social_promo",
            name="Social Media Promo",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._job_monthly_tenders,
            CronTrigger(day=1, hour=9, minute=0),
            id="monthly_tenders",
            name="Monthly Tender Alert",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._job_fb_token_check,
            CronTrigger(day_of_week="sun", hour=3, minute=0),
            id="fb_token_check",
            name="Facebook Token Auto-Refresh Check",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self._self_ping,
            "interval",
            minutes=10,
            id="self_ping",
            name="Railway Sleep Prevention",
            replace_existing=True,
        )
        logger.info(f"[SETUP] {len(self.scheduler.get_jobs())} jobs registered")

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
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            })
        return {
            "running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": jobs,
            "timezone": "Asia/Kolkata",
        }

MASTER_SCHEDULER = None

# ═══════════════════════════════════════════════════════════════
#  LIFESPAN & APP SETUP
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app):
    global HTTP_CLIENT, MASTER_SCHEDULER
    HTTP_CLIENT = httpx.AsyncClient(timeout=20)
    logger.info("Singh Ji AI Ultra v8.0 HYBRID Starting...")

    social_core.init_social_agent(HTTP_CLIENT)
    await social_core.SOCIAL_AGENT.load_saved_facebook_token()
    logger.info("[STARTUP] Social Agent initialized")

    sync = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    logger.info(f"Swarm: {sync['active']}/{sync['total']} agents loaded")
    logger.info(f"Active APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}")

    # ─── FIX #1: पुराने subscribers Supabase से वापस RAM में लोड करो ───
    loaded_prefs = await run_in_threadpool(_load_user_preferences_sync)
    USER_PREFERENCES.update(loaded_prefs)
    logger.info(f"[STARTUP] {len(loaded_prefs)} subscriber(s) Supabase से reload हुए")

    # ─── FIX #2: कौन सा webhook असल में एक्टिव है, यह लॉग में बताओ ───
    await _check_webhook_config()

    # ─── FIX #4: Telegram को हमेशा इसी फाइल के /telegram/webhook पर सेट रखो ───
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

    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER.stop()
    await HTTP_CLIENT.aclose()
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

# ==========================================
# ROUTERS REGISTER
# ==========================================
app.include_router(kisaan_router, prefix="/modules/kisaan_doctor")
app.include_router(yojana_router, prefix="/modules/sarkari_yojana")
app.include_router(currency_router, prefix="/api")
app.include_router(aavishkar_router, prefix="/modules/aavishkar")
app.include_router(goldrate_router, prefix="/api/goldrate")
app.include_router(fuel_router, prefix="/api/fuel")
app.include_router(scheme_swarm_router)
app.include_router(trishul_router, prefix="/api/trishul")
app.include_router(guard_router, prefix="/api")
app.include_router(oauth_router, prefix="/api")
app.include_router(social_router)
app.include_router(news_router)
app.add_api_route("/api/banking", banking_handler, methods=["GET"])
app.add_api_route("/api/pani", pani_handler, methods=["GET", "POST"])
app.add_api_route("/api/sewer", sewer_handler, methods=["GET", "POST"])
app.add_api_route("/api/upi", upi_handler, methods=["GET", "POST"])
app.include_router(miniprogram_router, prefix="/api/v1/miniprogram")

LANG_MODULE = LanguageModule()

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
            {"error": "Rate limit exceeded. Please wait a bit and try again.", "retry_after_seconds": 60},
            status_code=429
        )
    return await call_next(request)

# ==========================================
# HEALTH CHECK ENDPOINTS
# ==========================================

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
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI v8.0 HYBRID"}

@app.get("/ping")
@app.get("/api/ping")
async def ping():
    return {
        "status": "pong",
        "timestamp": datetime.now().isoformat(),
        "service": "Singh Ji AI Ultra v8.0",
        "version": "8.0.0-hybrid"
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

    async def _check_one(name, url, headers):
        if not AVAILABLE_KEYS.get(name):
            return name, {"status": "MISSING", "code": None}
        try:
            start = time.time()
            r = await HTTP_CLIENT.get(url, headers=headers)
            elapsed = round((time.time() - start) * 1000, 2)
            if r.status_code in [200, 401, 403]:
                return name, {"status": "LIVE", "code": r.status_code, "ms": elapsed}
            return name, {"status": "ERROR", "code": r.status_code, "ms": elapsed}
        except Exception as e:
            return name, {"status": "FAIL", "error": str(e)[:50]}

    outcomes = await asyncio.gather(*(_check_one(n, u, h) for n, (u, h, m) in tests.items()))
    results = dict(outcomes)
    live = sum(1 for v in results.values() if v["status"] == "LIVE")
    dead = len(results) - live
    return {"timestamp": datetime.now().isoformat(), "summary": {"live": live, "dead": dead, "total": live + dead}, "results": results}

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
        resp = await HTTP_CLIENT.get(url)
        data = resp.json()
        if resp.status_code == 200:
            result = {
                "city": city, "temp": data["main"]["temp"], "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"], "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"], "desc": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"], "source": "OPENWEATHER_LIVE"
            }
            await _cache_set(cache_key, result, CACHE_TTL["weather"])
            return result
        return {"error": data.get("message", "Unknown error"), "code": resp.status_code}
    except Exception as e:
        return {"error": str(e)}

MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"

@app.get("/api/mandi/{state}")
async def mandi_state(state: str, commodity: str = None, limit: int = 50):
    cache_key = _cache_key("mandi", state, commodity or "all", limit)
    cached = await _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if not MANDI_API_KEY:
        return {"error": "MANDI_API_KEY missing"}
    try:
        params = {"api-key": MANDI_API_KEY, "format": "json", "limit": limit, "filters[state.keyword]": state}
        if commodity:
            params["filters[commodity.keyword]"] = commodity
        resp = await HTTP_CLIENT.get(MANDI_BASE_URL, params=params, timeout=45)
        data = resp.json()
        result = {"state": state, "commodity_filter": commodity, "count": len(data.get("records", [])), "records": data.get("records", []), "source": "AGMARKNET_LIVE"}
        await _cache_set(cache_key, result, CACHE_TTL["mandi"])
        return result
    except Exception as e:
        return {"error": str(e)}

def _b64_too_big(b64_str: str) -> bool:
    return (len(b64_str) * 3 / 4) > MAX_B64_BYTES

@app.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "PLANT_ID_API missing"}
    data = await request.json()
    image_b64 = data.get("image_base64", "")
    if not image_b64:
        return {"error": "image_base64 required"}
    if _b64_too_big(image_b64):
        return JSONResponse(status_code=413, content={"error": "image too large (max 10MB)"})
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
            "top_match": {"name": top.get("name"), "probability": top.get("probability"), "common_names": top.get("details", {}).get("common_names")} if top else None,
            "all_suggestions": suggestions[:5],
            "source": "PLANT.ID_LIVE"
        }
    except Exception as e:
        return {"error": str(e)}

async def _call_groq(prompt: str, timeout=30):
    resp = await HTTP_CLIENT.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "openai/gpt-oss-20b", "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout
    )
    result = resp.json()
    return result["choices"][0]["message"]["content"]

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
            result_data = {"status": "success", "model": "groq", "response": response_text, "source": "GROQ_LIVE"}
            if not is_personal:
                await _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": response_text, "model": "groq"})
            return result_data
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if model in ["gemini", "auto"] and GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp = await HTTP_CLIENT.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            result_data = {"status": "success", "model": "gemini", "response": text, "source": "GEMINI_LIVE"}
            if not is_personal:
                await _cache_set(cache_key, result_data, CACHE_TTL["ai_chat"])
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": text, "model": "gemini"})
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

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return await _memory_get(key)

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(int(time.time())))
    value = data.get("value", data)
    return await _memory_save(key, value)

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
        resp = await HTTP_CLIENT.post(BHASHINI_PIPELINE_URL, headers=headers, json=payload, timeout=15)
        pipeline = resp.json()
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
        compute_url = pipeline["pipelineInferenceAPIEndPoint"]["callbackUrl"]
        key_name = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["name"]
        key_value = pipeline["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["value"]
        compute_payload = {
            "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source, "targetLanguage": target}, "serviceId": service_id}}],
            "inputData": {"input": [{"source": text}]}
        }
        compute_resp = await HTTP_CLIENT.post(compute_url, headers={key_name: key_value, "Content-Type": "application/json"}, json=compute_payload, timeout=20)
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

@app.post("/api/whisper/transcribe")
async def whisper_transcribe(request: Request):
    data = await request.json()
    audio_b64 = data.get("audio_base64", "")
    language = data.get("language")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    if _b64_too_big(audio_b64):
        return JSONResponse(status_code=413, content={"error": "audio too large (max 10MB)"})
    try:
        audio_bytes = base64.b64decode(audio_b64)
        out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".wav", language)
        if out is None:
            return {"error": "Whisper model not available"}
        transcript, detected_lang, lang_prob = out
        return {"status": "success", "transcript": transcript, "detected_language": detected_lang, "language_probability": round(lang_prob, 3), "source": "WHISPER_LOCAL"}
    except Exception as e:
        return {"error": str(e)}

def _tts_sync(text: str, lang: str) -> bytes:
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()

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
        return {"error": str(e)}

@app.get("/api/facebook/status")
async def facebook_status():
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=id,name,followers_count"
        resp = await HTTP_CLIENT.get(url)
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
        resp = await HTTP_CLIENT.get(url)
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
        resp = await HTTP_CLIENT.post(url, json=payload, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/retirement/tax-calculate")
async def tax_calculate(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")
    deductions = data.get("deductions", 0)
    return _calculate_tax(income, regime, deductions)

@app.get("/api/swarm/status")
async def swarm_status():
    return SMART_SWARM.get_status()

@app.post("/api/swarm/sync")
async def swarm_sync():
    result = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    return {"synced": True, **result}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        if "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            user_id = callback["from"]["id"]
            query_data = callback["data"]

            if query_data == "status":
                status = SMART_SWARM.get_status()
                text = "Status\n\n"
                text += f"Agents: {status['currently_loaded']}/330\n"
                text += f"Active: {status['active_running']}\n"
                text += f"Idle: {status['idle']}\n"
                text += f"APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}"
                await _telegram_send_message(chat_id, text)
            elif query_data == "weather":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "weather"
                await _telegram_send_message(chat_id, "Weather\n\nCity batao!")
            elif query_data == "news":
                try:
                    import modules.news.handler as news_module
                    text = "News\n\n" + await news_module.get_news_digest_text(count=5)
                    await _telegram_send_message(chat_id, text)
                except Exception as e:
                    await _telegram_send_message(chat_id, f"News error: {str(e)[:100]}")
            elif query_data == "mandi":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "mandi"
                await _telegram_send_message(chat_id, "Mandi Bhav\n\nState batao!")
            elif query_data == "ai_chat":
                await _telegram_send_message(chat_id, "AI Chat\n\nKuch bhi poochho!")
            elif query_data == "voice":
                await _telegram_send_message(chat_id, "Voice\n\nVoice message bhejo!")
            elif query_data == "tax":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "tax"
                await _telegram_send_message(chat_id, "Tax Calculator\n\nIncome batao!")
            elif query_data == "plant":
                await _telegram_send_message(chat_id, "Plant ID\n\nPlant ki photo bhejo!")
            elif query_data == "gold":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "gold"
                await _telegram_send_message(chat_id, "Gold Rate\n\nCity batao! (ya sirf Enter dabao Delhi ke liye)")
            elif query_data == "fuel":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "fuel"
                await _telegram_send_message(chat_id, "Fuel Price\n\nCity batao!")
            elif query_data == "horoscope":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "horoscope"
                await _telegram_send_message(chat_id, "Horoscope\n\nRashi batao! (jaise: Mesh, Simha, Tula)")
            elif query_data == "currency":
                USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = "currency"
                await _telegram_send_message(chat_id, "Currency Convert\n\nFormat: USD INR 100")
            elif query_data == "emergency":
                emg_text = "Emergency Numbers\n\n"
                for k, v in EMERGENCY_DATA.items():
                    emg_text += f"{k.title()}: {v['number']}" + (f" / {v['alt']}" if v.get("alt") else "") + "\n"
                await _telegram_send_message(chat_id, emg_text)
            elif query_data == "upi":
                upi_id = os.getenv("UPI_ID", "jp200883@sbi")
                upi_text = f"UPI Info\n\nUPI ID: {upi_id}\nApps: PhonePe, Google Pay, Paytm, BHIM\nDaily Limit: Rs 1,00,000"
                await _telegram_send_message(chat_id, upi_text)
            elif query_data == "guard":
                try:
                    import modules.guard_agent.handler as guard_module
                    g = guard_module.singhji_guard
                    guard_text = f"Guard Agent\n\nCameras: {len(g.cameras_db)}\nAlerts: {len(g.alerts_db)}\nDetection agents: vehicle, human, sound, face, anpr, fire, crowd, object, behavior"
                except Exception as e:
                    guard_text = f"Guard Agent not loaded: {str(e)[:100]}"
                await _telegram_send_message(chat_id, guard_text)
            elif query_data == "social":
                try:
                    import modules.social_agent.core as social_core
                    s = social_core.SOCIAL_AGENT
                    if s:
                        on = getattr(s, "auto_post_enabled", True)
                        social_text = f"Social Agent\n\nPosts published: {len(s.posted_history)}\nAuto-post: {'ON' if on else 'OFF'}\nPlatforms: Facebook, Instagram, Bluesky"
                    else:
                        social_text = "Social Agent not initialized"
                except Exception as e:
                    social_text = f"Social Agent not loaded: {str(e)[:100]}"
                await _telegram_send_message(chat_id, social_text)

            return {"status": "ok"}

        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]

        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {"language": "hi", "location": None}
            await _memory_save(f"user_pref:{user_id}", USER_PREFERENCES[user_id], table="user_memory")

        # ─── बटन-प्रेस के बाद आई प्लेन टेक्स्ट को सही मॉड्यूल कमांड में बदलो ───
        pending = USER_PREFERENCES.get(user_id, {}).pop("waiting_for", None)
        if pending and text and not text.startswith("/"):
            if pending == "weather":
                text = "/weather " + text.strip()
            elif pending == "mandi":
                text = "/mandi " + text.strip()
            elif pending == "tax":
                text = "/tax " + text.strip()
            elif pending == "gold":
                text = "/gold " + text.strip()
            elif pending == "fuel":
                text = "/fuel " + text.strip()
            elif pending == "horoscope":
                text = "/horoscope " + text.strip()
            elif pending == "currency":
                text = "/currency " + text.strip()
        # ────────────────────────────────────────────────────────────

        if _rate_check(f"tg_user:{user_id}", *RATE_LIMIT_TELEGRAM_USER):
            await _telegram_send_message(chat_id, "Thoda slow karo! 1 minute mein try karo.")
            return {"status": "ok"}

        if "voice" in message:
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
                        transcript_msg = "Transcript:" + chr(10) + transcript + chr(10) + chr(10) + "AI soch raha hai..."
                        await _telegram_send_message(chat_id, transcript_msg)
                        ai_text = None
                        if GROQ_API_KEY:
                            ai_text = await _call_groq(transcript)
                            try:
                                tts_text = ai_text[:500] if len(ai_text) > 500 else ai_text
                                tts_bytes = await run_in_threadpool(_tts_sync, tts_text, "hi")
                                tts_b64 = base64.b64encode(tts_bytes).decode("utf-8")
                                await _telegram_send_voice(chat_id, tts_b64, "AI Response (Hindi)")
                            except Exception:
                                ai_msg = "AI Response:" + chr(10) + chr(10) + ai_text
                                await _telegram_send_message(chat_id, ai_msg)
                        await _memory_save(f"telegram_voice:{user_id}:{int(time.time())}", {"transcript": transcript, "response": ai_text})
                    else:
                        await _telegram_send_message(chat_id, "Whisper model not available")
                else:
                    await _telegram_send_message(chat_id, "Could not download voice file")
            except Exception as e:
                logger.error(f"Voice processing error: {e}")
                err_msg = "Voice processing error: " + str(e)[:100]
                await _telegram_send_message(chat_id, err_msg)
            return {"status": "ok"}

        if text == "/start":
            welcome = "Welcome to Singh Ji AI Ultra v8.0!\n\nMain aapka AI assistant hoon.\n"
            await _telegram_send_message(chat_id, welcome, MAIN_KEYBOARD)
            return {"status": "ok"}

        elif text == "/help":
            help_text = (
                "Commands\n\n"
                "/start\n/weather city\n/news\n/mandi state\n/tax income\n/status\n/ai question\n"
                "/gold city\n/fuel city\n/horoscope rashi\n/currency USD INR 100\n"
                "/translate en text\n/emergency type\n/upi\n/pani\n/sewer\n/yojana age income category\n"
                "/govt aadhaar\n/search query\n/tv educational"
            )
            await _telegram_send_message(chat_id, help_text)
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

            try:
                import modules.guard_agent.handler as guard_module
                g = guard_module.singhji_guard
                status_text += f"\nGuard Agent: {len(g.alerts_db)} alerts, {len(g.cameras_db)} cameras\n"
            except Exception:
                status_text += "\nGuard Agent: not loaded\n"

            try:
                import modules.social_agent.core as social_core
                s = social_core.SOCIAL_AGENT
                if s:
                    cfg = s.get_stats()["platforms_configured"]
                    on = ", ".join(p for p, v in cfg.items() if v) or "none"
                    status_text += f"Social Agent: {len(s.posted_history)} posts | live: {on}\n"
                else:
                    status_text += "Social Agent: not loaded\n"
            except Exception:
                status_text += "Social Agent: not loaded\n"

            status_text += f"Time: {datetime.now().strftime('%H:%M:%S')}"
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
                        weather_text = f"Weather in {city}\n\n"
                        weather_text += f"Temperature: {data['main']['temp']}C\n"
                        weather_text += f"Feels like: {data['main']['feels_like']}C\n"
                        weather_text += f"Humidity: {data['main']['humidity']}%\n"
                        weather_text += f"Wind: {data['wind']['speed']} m/s\n"
                        weather_text += f"{data['weather'][0]['description'].title()}"
                        await _telegram_send_message(chat_id, weather_text)
                    else:
                        await _telegram_send_message(chat_id, f"City not found: {city}")
                except Exception as e:
                    await _telegram_send_message(chat_id, f"Error: {str(e)[:100]}")
            else:
                await _telegram_send_message(chat_id, "Weather API key missing")
            return {"status": "ok"}

        elif text == "/news":
            try:
                import modules.news.handler as news_module
                news_text = "Latest News\n\n" + await news_module.get_news_digest_text(count=5)
                await _telegram_send_message(chat_id, news_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"News error: {str(e)[:100]}")
            return {"status": "ok"}

        elif text.startswith("/mandi "):
            state = text.replace("/mandi ", "").strip()
            if MANDI_API_KEY:
                try:
                    params = {"api-key": MANDI_API_KEY, "format": "json", "limit": 10, "filters[state.keyword]": state}
                    resp = await HTTP_CLIENT.get(MANDI_BASE_URL, params=params, timeout=45)
                    data = resp.json()
                    records = data.get("records", [])
                    mandi_text = f"Mandi Bhav - {state}\n\n"
                    for i, record in enumerate(records[:5], 1):
                        mandi_text += f"{i}. {record.get('commodity', 'Unknown')}\n"
                        mandi_text += f"   Rs {record.get('modal_price', 'N/A')}/quintal\n"
                        mandi_text += f"   {record.get('district', 'N/A')}, {record.get('market', 'N/A')}\n\n"
                    await _telegram_send_message(chat_id, mandi_text)
                except Exception as e:
                    await _telegram_send_message(chat_id, f"Error: {str(e)[:100]}")
            else:
                await _telegram_send_message(chat_id, "Mandi API key missing")
            return {"status": "ok"}

        elif text.startswith("/tax "):
            try:
                income = float(text.replace("/tax ", "").strip())
                r = _calculate_tax(income, "new")
                tax_text = "Tax Calculation\n\n"
                tax_text += f"Income: Rs {r['income']:,.0f}\n"
                tax_text += f"Tax: Rs {r['tax']:,.2f}\n"
                tax_text += f"Health Cess (4%): Rs {r['cess']:,.2f}\n"
                tax_text += f"Total Tax: Rs {r['total']:,.2f}\n"
                tax_text += f"Take Home: Rs {r['take_home']:,.2f}"
                await _telegram_send_message(chat_id, tax_text)
            except Exception:
                await _telegram_send_message(chat_id, "Invalid income. Example: /tax 500000")
            return {"status": "ok"}

        elif text.startswith("/gold"):
            city = text.replace("/gold", "").strip() or "delhi"
            try:
                resp = await gold_rate_city(city)
                body = json.loads(bytes(resp.body))
                d = body["data"]
                cr = d.get("city_rates", {})
                gold_text = f"Gold Rate - {cr.get('city', city.title())}\n\n"
                gold_text += f"Source: {d.get('source', 'N/A')}\n"
                gold_text += f"24K (1g): Rs {cr.get('price_gram_24k', 'N/A')}\n"
                gold_text += f"22K (1g): Rs {cr.get('price_gram_22k', 'N/A')}\n"
                gold_text += f"24K (10g): Rs {cr.get('price_10g_24k', 'N/A')}\n"
                gold_text += f"Updated: {d.get('last_updated', 'N/A')}"
                await _telegram_send_message(chat_id, gold_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"Gold rate error: {str(e)[:100]}")
            return {"status": "ok"}

        elif text.startswith("/fuel"):
            city = text.replace("/fuel", "").strip() or "delhi"
            try:
                resp = await fuel_price(city)
                body = json.loads(bytes(resp.body))
                d = body["data"]
                fuel_text = f"Fuel Price - {d.get('city', city.title())}\n\n"
                fuel_text += f"Petrol: Rs {d.get('petrol', 'N/A')}/L\n"
                fuel_text += f"Diesel: Rs {d.get('diesel', 'N/A')}/L\n"
                fuel_text += f"Source: {d.get('source', 'N/A')}\n"
                fuel_text += f"Updated: {d.get('last_updated', 'N/A')}"
                await _telegram_send_message(chat_id, fuel_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"Fuel price error: {str(e)[:100]}")
            return {"status": "ok"}

        elif text.startswith("/horoscope"):
            rashi = text.replace("/horoscope", "").strip() or "मेष"
            try:
                h = get_horoscope(rashi, "daily", "hi")
                horo_text = _format_horoscope_telegram(h)
                await _telegram_send_message(chat_id, horo_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"Horoscope error: {str(e)[:100]}")
            return {"status": "ok"}

        elif text.startswith("/currency"):
            parts = text.replace("/currency", "").strip().split()
            try:
                base = parts[0].upper() if len(parts) > 0 else "USD"
                target = parts[1].upper() if len(parts) > 1 else "INR"
                amount = float(parts[2]) if len(parts) > 2 else 1.0
                result = await singhji_currency.convert(base, target, amount)
                cur_text = f"Currency Convert\n\n{amount} {base} = {result.converted} {target}\n"
                cur_text += f"Rate: 1 {base} = {result.rate} {target}\n"
                cur_text += f"Source: {result.source}"
                await _telegram_send_message(chat_id, cur_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"Currency error: {str(e)[:100]}\n\nFormat: /currency USD INR 100")
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
                    await _telegram_send_message(chat_id, f"Translation ({result.get('target_name', target_lang)})\n\n{result['translated']}")
                else:
                    await _telegram_send_message(chat_id, f"Translate error: {result.get('error', 'unknown')[:100]}")
            except Exception as e:
                await _telegram_send_message(chat_id, f"Translate error: {str(e)[:100]}\n\nFormat: /translate en Namaste kaise ho")
            return {"status": "ok"}

        elif text.startswith("/emergency"):
            type_ = text.replace("/emergency", "").strip().lower()
            if type_ and type_ in EMERGENCY_DATA:
                v = EMERGENCY_DATA[type_]
                emg_text = f"{type_.title()}\n\nNumber: {v['number']}"
                if v.get("alt"):
                    emg_text += f"\nAlt: {v['alt']}"
                emg_text += f"\n{v.get('info', '')}"
            else:
                emg_text = "Emergency Numbers\n\n"
                for k, v in EMERGENCY_DATA.items():
                    emg_text += f"{k.title()}: {v['number']}" + (f" / {v['alt']}" if v.get("alt") else "") + "\n"
            await _telegram_send_message(chat_id, emg_text)
            return {"status": "ok"}

        elif text == "/upi":
            upi_id = os.getenv("UPI_ID", "jp200883@sbi")
            upi_text = f"UPI Info\n\nUPI ID: {upi_id}\nApps: PhonePe, Google Pay, Paytm, BHIM\nDaily Limit: Rs 1,00,000"
            await _telegram_send_message(chat_id, upi_text)
            return {"status": "ok"}

        elif text == "/pani":
            pani_text = (
                "Pani (Water) Helplines\n\n"
                "National: 1800-180-1818\n"
                "Jal Jeevan Mission: 1800-111-555\n\n"
                "Schemes: Jal Jeevan Mission, AMRUT 2.0, Swajal Scheme\n"
                "Complaint: jaljeevanmission.gov.in"
            )
            await _telegram_send_message(chat_id, pani_text)
            return {"status": "ok"}

        elif text == "/sewer":
            sewer_text = (
                "Sewer/Sanitation Helplines\n\n"
                "Swachh Bharat: 1800-180-1818\n"
                "Urban Sewer: 1800-111-555\n"
                "Complaint: 1969\n\n"
                "Portal: swachhbharaturban.gov.in"
            )
            await _telegram_send_message(chat_id, sewer_text)
            return {"status": "ok"}

        elif text.startswith("/govt"):
            service = text.replace("/govt", "").strip().lower()
            if service and service in GOVT_DATA:
                d = GOVT_DATA[service]
                govt_text = f"{d['title']}\n\nHelpline: {d['helpline']}\nWebsite: {d['website']}\nServices: {', '.join(d['services'])}"
            else:
                govt_text = "Govt Services\n\n" + ", ".join(GOVT_DATA.keys())
                govt_text += "\n\nFormat: /govt aadhaar (ya pan, passport, voter, ration, driving, ayushman, pmkisan)"
            await _telegram_send_message(chat_id, govt_text)
            return {"status": "ok"}

        elif text.startswith("/search "):
            query = text.replace("/search ", "").strip()
            if TAVILY_API_KEY:
                try:
                    url = "https://api.tavily.com/search"
                    payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 5, "search_depth": "basic"}
                    resp = await HTTP_CLIENT.post(url, json=payload, timeout=15)
                    data = resp.json()
                    results = data.get("results", [])[:5]
                    search_text = f"Search: {query}\n\n"
                    for i, r in enumerate(results, 1):
                        search_text += f"{i}. {r.get('title', 'No title')}\n   {r.get('url', '')}\n\n"
                    if not results:
                        search_text += "Koi result nahi mila"
                    await _telegram_send_message(chat_id, search_text)
                except Exception as e:
                    await _telegram_send_message(chat_id, f"Search error: {str(e)[:100]}")
            else:
                await _telegram_send_message(chat_id, "Search API key missing")
            return {"status": "ok"}

        elif text.startswith("/tv"):
            category = text.replace("/tv", "").strip().lower()
            tv_content = {
                "educational": ["Digital India Explained (10 min)", "PM Kisan Process (5 min)", "UPI Safety Tips (3 min)", "Aadhaar Update Guide (7 min)"],
                "news": ["Daily Headlines (15 min)", "Mandi Rates Update (5 min)", "Weather Forecast (3 min)"],
                "entertainment": ["Folk Music Collection (30 min)", "Regional Movies (120 min)"],
                "health": ["Yoga for Beginners (20 min)", "Healthy Cooking (15 min)", "First Aid Basics (10 min)"],
            }
            if category and category in tv_content:
                tv_text = f"Singh Ji TV - {category.title()}\n\n" + "\n".join(tv_content[category])
            else:
                tv_text = "Singh Ji TV Categories\n\n" + ", ".join(tv_content.keys())
                tv_text += "\n\nFormat: /tv educational"
            await _telegram_send_message(chat_id, tv_text)
            return {"status": "ok"}

        elif text.startswith("/yojana"):
            parts = text.replace("/yojana", "").strip().split()
            try:
                age = int(parts[0]) if len(parts) > 0 else 30
                income = float(parts[1]) if len(parts) > 1 else 0
                category = parts[2].lower() if len(parts) > 2 else ""
                profile = UserProfile(
                    age=age,
                    gender="other",
                    caste_category="general",
                    annual_income=income,
                    state="UP",
                    occupation=category or "other",
                    is_farmer=(category == "farmer"),
                    is_student=(category == "student"),
                    is_widow=(category == "widow"),
                    is_senior_citizen=(age >= 60),
                )
                matches = await run_in_threadpool(scheme_engine.get_top_matches, profile, 5)
                if matches:
                    yojana_text = f"Sarkari Yojana Matches (Age {age}, Income {income:.0f}, {category or 'general'})\n\n"
                    for i, m in enumerate(matches, 1):
                        yojana_text += f"{i}. {m.scheme_name} (match {m.match_score}%)\n   {m.benefits_summary}\n\n"
                else:
                    yojana_text = "Koi matching scheme nahi mili. Details sahi bharo: /yojana age income category"
                await _telegram_send_message(chat_id, yojana_text)
            except Exception as e:
                await _telegram_send_message(chat_id, f"Yojana error: {str(e)[:100]}\n\nFormat: /yojana 45 150000 farmer")
            return {"status": "ok"}

        elif text.startswith("/ai "):
            prompt = text.replace("/ai ", "").strip()
            if GROQ_API_KEY:
                try:
                    ai_response = await _call_groq(prompt)
                    if len(ai_response) > 4000:
                        ai_response = ai_response[:4000] + "...\n\n(Truncated)"
                    await _telegram_send_message(chat_id, f"AI Response:\n\n{ai_response}")
                    await _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": ai_response})
                except Exception as e:
                    await _telegram_send_message(chat_id, f"AI Error: {str(e)[:100]}")
            else:
                await _telegram_send_message(chat_id, "Groq API key missing")
            return {"status": "ok"}

        elif text.startswith("/broadcast "):
            if user_id != ADMIN_USER_ID:
                await _telegram_send_message(chat_id, "Admin only command")
                return {"status": "ok"}
            broadcast_text = text.replace("/broadcast ", "").strip()
            sem = asyncio.Semaphore(20)
            async def _send(uid):
                async with sem:
                    await _telegram_send_message(uid, f"Broadcast\n\n{broadcast_text}")
            await asyncio.gather(*(_send(uid) for uid in list(USER_PREFERENCES.keys())))
            await _telegram_send_message(chat_id, f"Broadcast sent to {len(USER_PREFERENCES)} users")
            return {"status": "ok"}

        else:
            if GROQ_API_KEY and text:
                try:
                    ai_response = await _call_groq(text)
                    if len(ai_response) > 4000:
                        ai_response = ai_response[:4000] + "...\n\n(Truncated)"
                    await _telegram_send_message(chat_id, ai_response)
                    await _memory_save(f"telegram_chat:{user_id}:{int(time.time())}", {"prompt": text, "response": ai_response})
                except Exception as e:
                    await _telegram_send_message(chat_id, f"AI Error: {str(e)[:100]}")
            return {"status": "ok"}

    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return {"status": "error", "message": str(e)}

# ==========================================
# ADMIN ROUTES
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
    sem = asyncio.Semaphore(20)
    async def _send(uid):
        async with sem:
            await _telegram_send_message(uid, f"Admin Broadcast\n\n{message}")
    await asyncio.gather(*(_send(uid) for uid in list(USER_PREFERENCES.keys())))
    return {"broadcast": True, "sent_to": len(USER_PREFERENCES)}

# ==========================================
# PAYMENT ROUTES
# ==========================================

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

    def _create_order_sync():
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.order.create({"amount": amount, "currency": currency, "receipt": receipt, "payment_capture": 1})

    try:
        order = await run_in_threadpool(_create_order_sync)
        return {"status": "success", "order": order, "source": "RAZORPAY_LIVE"}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# GMAIL ROUTES
# ==========================================

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

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
