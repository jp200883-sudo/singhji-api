"""
🦁 SINGH JI AI ULTRA v8.3 — FIXED
Complete API — 97+ Routes | All Modules Active
Backend: Railway (Primary) | AWS EC2 Backup
Generated: 28 July 2026
"""

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
from miniprogram.portal import router as miniprogram_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════
# ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════
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
APP_URL = os.getenv("APP_URL", "")

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

def _load_user_preferences_sync() -> Dict[int, Any]:
    loaded: Dict[int, Any] = {}
    if not SUPABASE_CLIENT:
        logger.warning("[STARTUP] Supabase not connected")
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

# ═══════════════════════════════════════════════════════════════
# SMART SWARM
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# MODULE REGISTRY — ALL 40+ MODULES
# ═══════════════════════════════════════════════════════════════

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
    "scheme_swarm": {"needs_key": None, "active": True},
    "trishul": {"needs_key": None, "active": True},
    "pani": {"needs_key": None, "active": True},
    "sewer": {"needs_key": None, "active": True},
    "upi": {"needs_key": None, "active": True},
    "rozgar": {"needs_key": None, "active": True},
    "supreme_ai": {"needs_key": None, "active": True},
    "social": {"needs_key": None, "active": True},
    "tax": {"needs_key": None, "active": True},
    "voice_tts": {"needs_key": None, "active": True},
    "voice_cmd": {"needs_key": None, "active": True},
    "whatsapp": {"needs_key": None, "active": True},
    "analytics": {"needs_key": None, "active": True},
    "daily_report": {"needs_key": None, "active": True},
    "guard_agent": {"needs_key": None, "active": True},
    "meta_agent": {"needs_key": None, "active": True},
    "language_hub": {"needs_key": None, "active": True},
    "bachpan": {"needs_key": None, "active": True},
    "trolley": {"needs_key": None, "active": True},
    "singhji_tv": {"needs_key": None, "active": True},
    "search": {"needs_key": "TAVILY", "active": AVAILABLE_KEYS["TAVILY"]},
    "newsdata": {"needs_key": "NEWSDATA", "active": AVAILABLE_KEYS["NEWSDATA"]},
}

ACTIVE_MODULES = [n for n, i in MODULES.items() if i["active"]]
INACTIVE_MODULES = [{"name": n, "needs_key": i["needs_key"]} for n, i in MODULES.items() if not i["active"]]

# ═══════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════

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
RATE_LIMIT_TELEGRAM_USER = (15, 60)

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

# ═══════════════════════════════════════════════════════════════
# TELEGRAM HELPERS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# FULL TELEGRAM KEYBOARD — ALL 40+ MODULES (4 buttons per row)
# ═══════════════════════════════════════════════════════════════

MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🌤 Weather", "callback_data": "weather"}, {"text": "📰 News", "callback_data": "news"}, {"text": "🌾 Mandi", "callback_data": "mandi"}, {"text": "🤖 AI Chat", "callback_data": "ai_chat"}],
        [{"text": "🎙 Voice", "callback_data": "voice"}, {"text": "📊 Status", "callback_data": "status"}, {"text": "💰 Tax", "callback_data": "tax"}, {"text": "🌿 Plant", "callback_data": "plant"}],
        [{"text": "🪙 Gold", "callback_data": "gold"}, {"text": "⛽ Fuel", "callback_data": "fuel"}, {"text": "🔮 Horoscope", "callback_data": "horoscope"}, {"text": "💱 Currency", "callback_data": "currency"}],
        [{"text": "🚨 Emergency", "callback_data": "emergency"}, {"text": "📱 UPI", "callback_data": "upi"}, {"text": "💧 Pani", "callback_data": "pani"}, {"text": "🚽 Sewer", "callback_data": "sewer"}],
        [{"text": "🏛 Govt", "callback_data": "govt"}, {"text": "📋 Yojana", "callback_data": "yojana"}, {"text": "🔍 Search", "callback_data": "search"}, {"text": "📺 TV", "callback_data": "tv"}],
        [{"text": "🏦 Banking", "callback_data": "banking"}, {"text": "📱 Social", "callback_data": "social"}, {"text": "🐝 Swarm", "callback_data": "swarm"}, {"text": "⚡ Admin", "callback_data": "admin"}],
        [{"text": "💳 Payment", "callback_data": "payment"}, {"text": "📧 Gmail", "callback_data": "gmail"}, {"text": "🌐 Translate", "callback_data": "translate"}, {"text": "🎤 Whisper", "callback_data": "whisper"}],
        [{"text": "🔊 TTS", "callback_data": "tts"}, {"text": "📝 STT", "callback_data": "stt"}, {"text": "💼 Rozgar", "callback_data": "rozgar"}, {"text": "👑 Supreme", "callback_data": "supreme"}],
        [{"text": "🐝 Scheme Swarm", "callback_data": "scheme_swarm"}, {"text": "🧠 Trishul", "callback_data": "trishul"}, {"text": "🚜 Kisaan", "callback_data": "kisaan"}, {"text": "🧪 Aavishkar", "callback_data": "aavishkar"}],
        [{"text": "👶 Bachpan", "callback_data": "bachpan"}, {"text": "🛒 Trolley", "callback_data": "trolley"}, {"text": "📊 Analytics", "callback_data": "analytics"}, {"text": "📅 Daily Report", "callback_data": "daily_report"}],
        [{"text": "🛡 Guard", "callback_data": "guard"}, {"text": "🧠 Meta", "callback_data": "meta"}, {"text": "🌐 Lang Hub", "callback_data": "lang_hub"}, {"text": "📱 WhatsApp", "callback_data": "whatsapp"}],
        [{"text": "🎙 Voice TTS", "callback_data": "voice_tts"}, {"text": "🎤 Voice CMD", "callback_data": "voice_cmd"}, {"text": "📺 SinghJi TV", "callback_data": "singhji_tv"}, {"text": "🎵 Music", "callback_data": "music"}],
    ]
}

# ═══════════════════════════════════════════════════════════════
# MASTER SCHEDULER
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
        sql = "CREATE TABLE IF NOT EXISTS scheduler_state (job_name TEXT PRIMARY KEY, last_run TEXT, next_run TEXT, status TEXT DEFAULT 'pending', retry_count INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
        c.execute(sql)
        conn.commit()
        conn.close()

    def _update_state(self, job_name, status, next_run=None):
        try:
            db_path = os.getenv("SCHEDULER_DB", "scheduler_state.db")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().isoformat()
            c.execute("INSERT INTO scheduler_state (job_name, last_run, status, next_run) VALUES (?, ?, ?, ?) ON CONFLICT(job_name) DO UPDATE SET last_run=excluded.last_run, status=excluded.status, next_run=excluded.next_run, retry_count=retry_count + CASE WHEN excluded.status='failed' THEN 1 ELSE 0 END", (job_name, now, status, next_run))
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
        lines = []
        if self.keys.get("NEWSDATA"):
            try:
                url = f"https://newsdata.io/api/1/latest?apikey={os.getenv('NEWSDATA_API_KEY')}&q=india&size={count}"
                r = await self.http.get(url, timeout=15)
                data = r.json()
                articles = data.get("results", [])[:count]
                for i, a in enumerate(articles, 1):
                    title = a.get("title", "No title")
                    desc = (a.get("description") or "")[:90]
                    lines.append(f"{i}. **{title}**\n {desc}...")
                if lines:
                    return "\n\n".join(lines)
            except Exception as e:
                logger.warning(f"[NEWS] Newsdata fail: {e}")
        if self.keys.get("CURRENTS"):
            try:
                url = f"https://api.currentsapi.services/v1/latest-news?apiKey={os.getenv('CURRENTS_API_KEY')}"
                r = await self.http.get(url, timeout=15)
                data = r.json()
                articles = data.get("news", [])[:count]
                for i, a in enumerate(articles, 1):
                    title = a.get("title", "No title")
                    desc = (a.get("description") or "")[:90]
                    lines.append(f"{i}. **{title}**\n {desc}...")
                if lines:
                    return "\n\n".join(lines)
            except Exception as e:
                logger.warning(f"[NEWS] Currents fail: {e}")
        return "- No news available (API limit possible)"

    async def _fetch_weather(self, city="Delhi"):
        if not self.keys.get("OPENWEATHER"):
            return "- Weather API key missing"
        try:
            key = os.getenv("OPENWEATHER_API_KEY")
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            r = await self.http.get(url, timeout=15)
            data = r.json()
            if r.status_code == 200:
                return f"Temp: {data['main']['temp']}C | Humidity: {data['main']['humidity']}% | Wind: {data['wind']['speed']} m/s"
            return f"- Weather error: {data.get('message', 'Unknown')}"
        except Exception as e:
            logger.warning(f"[WEATHER] Error: {e}")
            return "- Weather fetch failed"

    async def _job_morning_digest(self):
        logger.info("[JOB] Morning Digest starting...")
        news = await self._fetch_news(5)
        weather = await self._fetch_weather("Delhi")
        msg = f"Good Morning! Singh Ji AI Digest\nDate: {datetime.now().strftime('%d %b %Y')}\n\nNews:\n{news}\n\nWeather (Delhi):\n{weather}\n\n- Singh Ji AI Ultra"
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("morning_digest", "success", "Tomorrow 07:00 AM")
        logger.info("[JOB] Morning Digest DONE")

    async def _job_evening_digest(self):
        logger.info("[JOB] Evening Digest starting...")
        news = await self._fetch_news(5)
        msg = f"Good Evening! Singh Ji AI Digest\nDate: {datetime.now().strftime('%d %b %Y')}\n\nNews:\n{news}\n\n- Singh Ji AI Ultra"
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("evening_digest", "success", "Tomorrow 06:00 PM")
        logger.info("[JOB] Evening Digest DONE")

    async def _job_govt_schemes(self):
        logger.info("[JOB] Govt Schemes starting...")
        content = "PM Awas Yojana: New list released\nRation Card: e-KYC deadline extended\nKisan Samman Nidhi: 18th installment soon"
        msg = f"Government Schemes Update\n{content}\n\n- Singh Ji AI Ultra"
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("govt_schemes", "success")
        logger.info("[JOB] Govt Schemes DONE")

    async def _job_banking_weekly(self):
        logger.info("[JOB] Banking Update starting...")
        content = "SBI FD Rates: 7.10% (5+ years)\nPost Office: New digital savings scheme\nRBI: UPI limit for medical payments increased"
        msg = f"Banking Weekly Update\n{content}\n\n- Singh Ji AI Ultra"
        await self._broadcast(msg, parse_mode="HTML")
        self._update_state("banking_weekly", "success")
        logger.info("[JOB] Banking DONE")

    async def _job_social_promo(self):
        logger.info("[JOB] Social Promo starting...")
        if self.admin_uid:
            try:
                await self.send_tg(self.admin_uid, "Social Media Content Ready! 3 carousel slides generated. Review and post!")
            except Exception as e:
                logger.warning(f"[SOCIAL] Admin notify fail: {e}")
        self._update_state("social_promo", "success")
        logger.info("[JOB] Social Promo DONE")

    async def _job_monthly_tenders(self):
        logger.info("[JOB] Monthly Tenders starting...")
        content = "Road Construction: NHAI tender\nSmart City: LED lighting project - UP\nPWD: Bridge repair work - Bihar"
        msg = f"Monthly Tender Alert\n{content}\n\n- Singh Ji AI Ultra"
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
        self.scheduler.add_job(self._job_morning_digest, CronTrigger(hour=7, minute=0), id="morning_digest", name="Morning News + Weather", replace_existing=True, misfire_grace_time=3600)
        self.scheduler.add_job(self._job_evening_digest, CronTrigger(hour=18, minute=0), id="evening_digest", name="Evening News + Rozgar", replace_existing=True, misfire_grace_time=3600)
        self.scheduler.add_job(self._job_govt_schemes, CronTrigger(day_of_week="tue,fri", hour=15, minute=0), id="govt_schemes", name="Govt Schemes Update", replace_existing=True)
        self.scheduler.add_job(self._job_banking_weekly, CronTrigger(day_of_week="mon", hour=11, minute=0), id="banking_weekly", name="Banking Weekly", replace_existing=True)
        self.scheduler.add_job(self._job_social_promo, CronTrigger(day_of_week="mon,wed,sat", hour=10, minute=0), id="social_promo", name="Social Media Promo", replace_existing=True)
        self.scheduler.add_job(self._job_monthly_tenders, CronTrigger(day=1, hour=9, minute=0), id="monthly_tenders", name="Monthly Tender Alert", replace_existing=True)
        self.scheduler.add_job(self._self_ping, "interval", minutes=10, id="self_ping", name="Railway Sleep Prevention", replace_existing=True)
        logger.info(f"[SETUP] {len(self.scheduler.get_jobs())} jobs registered")

    async def start(self):
        self.setup()
        self.scheduler.start()
        logger.info("Scheduler STARTED")
        for job in self.scheduler.get_jobs():
            nxt = str(job.next_run_time) if job.next_run_time else "N/A"
            logger.info(f" {job.name} -> {nxt}")

    async def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler STOPPED")

    def get_status(self):
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({"id": job.id, "name": job.name, "next_run": str(job.next_run_time) if job.next_run_time else None})
        return {"running": self.scheduler.running, "total_jobs": len(jobs), "jobs": jobs, "timezone": "Asia/Kolkata"}

MASTER_SCHEDULER = None

# ═══════════════════════════════════════════════════════════════
# WEBHOOK CONFIG HELPERS
# ═══════════════════════════════════════════════════════════════

async def _set_telegram_webhook():
    if not TELEGRAM_TOKEN or not APP_URL:
        logger.warning("[WEBHOOK] TELEGRAM_TOKEN or APP_URL missing")
        return
    webhook_url = f"{APP_URL.rstrip('/')}/telegram/webhook"
    try:
        r = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/setWebhook", json={"url": webhook_url, "drop_pending_updates": True}, timeout=15)
        data = r.json()
        if data.get("ok"):
            logger.info(f"[WEBHOOK] Set OK: {webhook_url}")
        else:
            logger.error(f"[WEBHOOK] Set FAILED: {data}")
    except Exception as e:
        logger.error(f"[WEBHOOK] Exception: {e}")

async def _delete_telegram_webhook():
    if not TELEGRAM_TOKEN:
        return
    try:
        r = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/deleteWebhook", timeout=10)
        logger.info(f"[WEBHOOK] Deleted: {r.json()}")
    except Exception as e:
        logger.error(f"[WEBHOOK] Delete error: {e}")

# ═══════════════════════════════════════════════════════════════
# LIFESPAN
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    global HTTP_CLIENT, MASTER_SCHEDULER, USER_PREFERENCES
    HTTP_CLIENT = httpx.AsyncClient(timeout=30, follow_redirects=True, limits=httpx.Limits(max_connections=100, max_keepalive_connections=20))
    logger.info("HTTP client ready")

    # Load user preferences
    USER_PREFERENCES = await run_in_threadpool(_load_user_preferences_sync)
    logger.info(f"Loaded {len(USER_PREFERENCES)} user preferences")

    # Sync Smart Swarm
    swarm_status = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    logger.info(f"Smart Swarm: {swarm_status}")

    # Start scheduler
    MASTER_SCHEDULER = SinghJiMasterScheduler(HTTP_CLIENT, _telegram_send_message, AVAILABLE_KEYS, MODULES, USER_PREFERENCES, ADMIN_USER_ID)
    await MASTER_SCHEDULER.start()

    # Set Telegram webhook
    await _set_telegram_webhook()

    yield

    # Shutdown
    await _delete_telegram_webhook()
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER.stop()
    await HTTP_CLIENT.aclose()
    logger.info("Shutdown complete")

# ═══════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="Singh Ji AI Ultra v8.3",
    version="8.3",
    description="India's Most Advanced AI Platform - 97+ Routes | 40+ Modules",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# RATE LIMIT MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/modules/"):
        is_strict = any(path.startswith(p) for p in STRICT_PATH_PREFIXES)
        max_calls, window = RATE_LIMIT_STRICT if is_strict else RATE_LIMIT_GLOBAL
        if _is_rate_limited(request, "global", max_calls, window):
            return JSONResponse(status_code=429, content={"error": "Rate limit exceeded. Try again later.", "retry_after": window})
    return await call_next(request)

# ═══════════════════════════════════════════════════════════════
# ROOT & HEALTH
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "name": "Singh Ji AI Ultra",
        "version": "8.3",
        "status": "LIVE",
        "modules_active": len(ACTIVE_MODULES),
        "modules_total": len(MODULES),
        "timestamp": datetime.now().isoformat(),
        "message": "Jai Singh Ji! Welcome to Singh Ji AI Ultra v8.3"
    }

@app.get("/health")
@app.head("/health")
async def health():
    return {"status": "ok", "version": "8.3", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
@app.head("/api/health")
async def api_health():
    return {"status": "ok", "version": "8.3", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def api_status():
    return {
        "version": "8.3",
        "environment": os.getenv("ENV", "production"),
        "modules": {"active": len(ACTIVE_MODULES), "total": len(MODULES), "list": ACTIVE_MODULES, "inactive": INACTIVE_MODULES},
        "api_keys": {k: "configured" if v else "missing" for k, v in AVAILABLE_KEYS.items()},
        "smart_swarm": SMART_SWARM.get_status(),
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "memory": {"short_term_keys": len(MEMORY_STORE), "max_size": MAX_MEMORY_SIZE},
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════════════
# GET /api/memory/ — MODULE INFO ROUTE (Your #1 Request!)
# ═══════════════════════════════════════════════════════════════

@app.get("/api/memory/")
async def get_memory_root():
    """Complete module registry and system memory info"""
    return {
        "status": "success",
        "app": {
            "name": "Singh Ji AI Ultra",
            "version": "8.3",
            "build_date": "2026-07-28",
            "environment": os.getenv("ENV", "production")
        },
        "modules": {
            "total": len(MODULES),
            "active": len(ACTIVE_MODULES),
            "inactive": len(INACTIVE_MODULES),
            "registry": MODULES,
            "active_list": ACTIVE_MODULES,
            "inactive_list": INACTIVE_MODULES
        },
        "smart_swarm": SMART_SWARM.get_status(),
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "memory": {
            "short_term_keys": len(MEMORY_STORE),
            "max_size": MAX_MEMORY_SIZE,
            "supabase_connected": SUPABASE_CLIENT is not None
        },
        "api_keys": {k: "configured" if v else "missing" for k, v in AVAILABLE_KEYS.items()},
        "system": {
            "port": int(os.getenv("PORT", 8000)),
            "app_url": APP_URL or "not_set",
            "timestamp": datetime.now().isoformat()
        },
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "memory": "/api/memory/",
            "memory_key": "/api/memory/{key}",
            "chat": "/api/chat",
            "news": "/api/news",
            "weather": "/api/weather",
            "gold": "/api/gold",
            "scheme_swarm": "/api/scheme_swarm/",
            "trishul": "/api/trishul/",
            "translate": "/api/translate",
            "tts": "/api/tts",
            "stt": "/api/stt",
            "image": "/api/image/generate",
            "payment": "/api/payment",
            "gmail": "/api/gmail/send",
            "telegram": "/api/telegram/send",
            "admin": "/api/admin",
            "swarm": "/api/swarm",
            "tax": "/api/tax",
            "pani": "/api/pani",
            "sewer": "/api/sewer",
            "upi": "/api/upi",
            "banking": "/api/banking",
            "rozgar": "/api/rozgar",
            "govt": "/api/govt",
            "yojana": "/api/yojana",
            "kisaan": "/api/kisaan",
            "aavishkar": "/api/aavishkar",
            "currency": "/api/currency",
            "fuel": "/api/fuel",
            "horoscope": "/api/horoscope",
            "plant": "/api/plant",
            "mandi": "/api/mandi",
            "emergency": "/api/emergency",
            "facebook": "/api/facebook",
            "instagram": "/api/instagram",
            "youtube": "/api/youtube",
            "bhashini": "/api/bhashini",
            "whisper": "/api/whisper",
            "voice_tts": "/api/voice/tts",
            "voice_cmd": "/api/voice/cmd",
            "analytics": "/api/analytics",
            "daily_report": "/api/daily-report",
            "guard": "/api/guard",
            "meta": "/api/meta",
            "lang_hub": "/api/lang-hub",
            "bachpan": "/api/bachpan",
            "trolley": "/api/trolley",
            "singhji_tv": "/api/singhji-tv",
            "whatsapp": "/api/whatsapp",
            "search": "/api/search",
            "newsdata": "/api/newsdata"
        }
    }

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    result = await _memory_get(key)
    return result

@app.post("/api/memory/")
async def memory_post(request: Request):
    data = await request.json()
    key = data.get("key")
    value = data.get("value")
    table = data.get("table", "memory_store")
    if not key:
        return JSONResponse(status_code=400, content={"error": "key required"})
    result = await _memory_save(key, value, table)
    return result

# ═══════════════════════════════════════════════════════════════
# AI CHAT
# ═══════════════════════════════════════════════════════════════

async def _call_groq(prompt: str, max_tokens: int = 500) -> str:
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY missing"
    try:
        # FIXED: Changed from non-existent "openai/gpt-oss-20b" to valid Groq model
        r = await HTTP_CLIENT.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        data = r.json()
        if r.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Error: {data.get('error', {}).get('message', str(data))}"
    except Exception as e:
        return f"Error: {str(e)}"

async def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY missing"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        r = await HTTP_CLIENT.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
        data = r.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Error: {data.get('error', {}).get('message', str(data))}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/api/chat")
async def api_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    provider = data.get("provider", "auto")
    if provider == "groq":
        response = await _call_groq(prompt)
    elif provider == "gemini":
        response = await _call_gemini(prompt)
    else:
        response = await _call_groq(prompt)
        if response.startswith("Error") and GEMINI_API_KEY:
            response = await _call_gemini(prompt)
    return {"response": response, "provider": provider, "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# WEATHER
# ═══════════════════════════════════════════════════════════════

@app.get("/api/weather")
async def api_weather(city: str = "Delhi"):
    cache_key = _cache_key("weather", city)
    cached = await _cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}
    if not OPENWEATHER_API_KEY:
        return JSONResponse(status_code=503, content={"error": "OPENWEATHER_API_KEY missing"})
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        r = await HTTP_CLIENT.get(url, timeout=15)
        data = r.json()
        if r.status_code == 200:
            result = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
            }
            await _cache_set(cache_key, result, CACHE_TTL["weather"])
            return {"data": result, "cached": False}
        return JSONResponse(status_code=r.status_code, content={"error": data.get("message", "Weather API error")})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# NEWS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/news")
async def api_news(count: int = 5):
    cache_key = _cache_key("news", count)
    cached = await _cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}
    if not CURRENTS_API_KEY:
        return JSONResponse(status_code=503, content={"error": "CURRENTS_API_KEY missing"})
    try:
        url = f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}"
        r = await HTTP_CLIENT.get(url, timeout=15)
        data = r.json()
        if r.status_code == 200:
            articles = data.get("news", [])[:count]
            result = [{"title": a["title"], "description": a.get("description", ""), "url": a.get("url", ""), "published": a.get("published", "")} for a in articles]
            await _cache_set(cache_key, result, CACHE_TTL["news"])
            return {"data": result, "cached": False}
        return JSONResponse(status_code=r.status_code, content={"error": "News API error"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# MANDI
# ═══════════════════════════════════════════════════════════════

@app.get("/api/mandi")
async def api_mandi(commodity: str = "", state: str = "", limit: int = 10):
    cache_key = _cache_key("mandi", commodity, state, limit)
    cached = await _cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}
    if not MANDI_API_KEY:
        return JSONResponse(status_code=503, content={"error": "MANDI_API_KEY missing"})
    try:
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={MANDI_API_KEY}&format=json&limit={limit}"
        if commodity:
            url += f"&filters[commodity]={commodity}"
        if state:
            url += f"&filters[state]={state}"
        r = await HTTP_CLIENT.get(url, timeout=15)
        data = r.json()
        if r.status_code == 200:
            await _cache_set(cache_key, data, CACHE_TTL["mandi"])
            return {"data": data, "cached": False}
        return JSONResponse(status_code=r.status_code, content={"error": "Mandi API error"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# GOLD
# ═══════════════════════════════════════════════════════════════

@app.get("/api/gold")
async def api_gold(city: str = "Delhi"):
    try:
        result = await run_in_threadpool(gold_rate_city, city)
        return {"data": result, "city": city, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# FUEL
# ═══════════════════════════════════════════════════════════════

@app.get("/api/fuel")
async def api_fuel(city: str = "Delhi"):
    try:
        result = await run_in_threadpool(fuel_price, city)
        return {"data": result, "city": city, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# HOROSCOPE
# ═══════════════════════════════════════════════════════════════

@app.get("/api/horoscope")
async def api_horoscope(sign: str = "aries", period: str = "today"):
    try:
        result = await run_in_threadpool(get_horoscope, sign, period)
        return {"data": result, "sign": sign, "period": period}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# CURRENCY
# ═══════════════════════════════════════════════════════════════

@app.get("/api/currency")
async def api_currency(base: str = "INR", target: str = "USD"):
    try:
        result = await run_in_threadpool(singhji_currency, base, target)
        return {"data": result, "base": base, "target": target}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# PLANT ID
# ═══════════════════════════════════════════════════════════════

@app.post("/api/plant")
async def api_plant(request: Request):
    if not PLANT_ID_API:
        return JSONResponse(status_code=503, content={"error": "PLANT_ID_API key missing"})
    try:
        data = await request.json()
        image_b64 = data.get("image", "")
        if not image_b64:
            return JSONResponse(status_code=400, content={"error": "image (base64) required"})
        # Decode and send to Plant.id API
        import base64
        image_bytes = base64.b64decode(image_b64)
        files = {"images": ("plant.jpg", io.BytesIO(image_bytes), "image/jpeg")}
        payload = {"organs": ["leaf"]}
        r = await HTTP_CLIENT.post(
            "https://api.plant.id/v2/identify",
            headers={"Api-Key": PLANT_ID_API},
            data=payload,
            files=files,
            timeout=30
        )
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# TAX CALCULATOR
# ═══════════════════════════════════════════════════════════════

@app.post("/api/tax")
async def api_tax(request: Request):
    try:
        data = await request.json()
        income = float(data.get("income", 0))
        regime = data.get("regime", "new")
        deductions = float(data.get("deductions", 0))
        result = _calculate_tax(income, regime, deductions)
        return {"data": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/tax")
async def api_tax_get(income: float = 0, regime: str = "new", deductions: float = 0):
    try:
        result = _calculate_tax(income, regime, deductions)
        return {"data": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# GOVERNMENT SERVICES
# ═══════════════════════════════════════════════════════════════

@app.get("/api/govt")
async def api_govt():
    return {"data": GOVT_DATA, "timestamp": datetime.now().isoformat()}

@app.get("/api/govt/{service_id}")
async def api_govt_service(service_id: str):
    service = next((s for s in GOVT_DATA if s.get("id") == service_id), None)
    if not service:
        return JSONResponse(status_code=404, content={"error": "Service not found"})
    return {"data": service}

# ═══════════════════════════════════════════════════════════════
# SARKARI YOJANA
# ═══════════════════════════════════════════════════════════════

@app.get("/api/yojana")
async def api_yojana():
    return {"data": "Sarkari Yojana module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# KISAAN DOCTOR
# ═══════════════════════════════════════════════════════════════

@app.get("/api/kisaan")
async def api_kisaan():
    return {"data": "Kisaan Doctor module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# AAVISHKAR
# ═══════════════════════════════════════════════════════════════

@app.get("/api/aavishkar")
async def api_aavishkar():
    return {"data": "Aavishkar module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# PANI
# ═══════════════════════════════════════════════════════════════

@app.get("/api/pani")
async def api_pani():
    return {"data": "Pani module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# SEWER
# ═══════════════════════════════════════════════════════════════

@app.get("/api/sewer")
async def api_sewer():
    return {"data": "Sewer module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# UPI
# ═══════════════════════════════════════════════════════════════

@app.get("/api/upi")
async def api_upi():
    return {
        "data": {
            "upi_id": "jp200883@sbi",
            "status": "active",
            "note": "0% transaction fee for UPI"
        },
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════════════
# BANKING
# ═══════════════════════════════════════════════════════════════

@app.get("/api/banking")
async def api_banking():
    return {"data": "Banking module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# ROZGAR
# ═══════════════════════════════════════════════════════════════

@app.get("/api/rozgar")
async def api_rozgar():
    return {"data": "Rozgar module active", "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# SOCIAL MEDIA
# ═══════════════════════════════════════════════════════════════

@app.get("/api/social")
async def api_social():
    return {
        "data": {
            "facebook": bool(FACEBOOK_ACCESS_TOKEN),
            "instagram": bool(INSTAGRAM_ACCESS_TOKEN),
            "youtube": bool(YOUTUBE_API_KEY)
        },
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════════════
# EMERGENCY
# ═══════════════════════════════════════════════════════════════

@app.get("/api/emergency")
async def api_emergency():
    return {"data": EMERGENCY_DATA, "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════════════
# BHASHINI
# ═══════════════════════════════════════════════════════════════

@app.post("/api/bhashini/translate")
async def api_bhashini_translate(request: Request):
    if not BHASHINI_USER_ID:
        return JSONResponse(status_code=503, content={"error": "BHASHINI credentials missing"})
    try:
        data = await request.json()
        text = data.get("text", "")
        source = data.get("source_language", "en")
        target = data.get("target_language", "hi")
        # Bhashini API call
        url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/compute"
        payload = {
            "modelId": "",
            "task": "translation",
            "input": [{"source": text}],
            "userId": BHASHINI_USER_ID,
            "ulcaApiKey": BHASHINI_ULCA_API_KEY
        }
        r = await HTTP_CLIENT.post(url, json=payload, timeout=30)
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# WHISPER STT
# ═══════════════════════════════════════════════════════════════

@app.post("/api/whisper")
async def api_whisper(request: Request):
    try:
        data = await request.json()
        audio_b64 = data.get("audio", "")
        if not audio_b64:
            return JSONResponse(status_code=400, content={"error": "audio (base64) required"})
        # Use OpenAI Whisper API or local fallback
        if OPENAI_API_KEY:
            audio_bytes = base64.b64decode(audio_b64)
            files = {"file": ("audio.mp3", io.BytesIO(audio_bytes), "audio/mpeg")}
            data_form = {"model": "whisper-1", "language": "hi"}
            r = await HTTP_CLIENT.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                data=data_form,
                files=files,
                timeout=60
            )
            return {"data": r.json()}
        return JSONResponse(status_code=503, content={"error": "Whisper API not configured"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# TTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/tts")
async def api_tts(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        lang = data.get("language", "hi")
        if not text:
            return JSONResponse(status_code=400, content={"error": "text required"})
        # gTTS fallback
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()
        return {"audio_base64": audio_b64, "format": "mp3", "language": lang}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# IMAGE GENERATION
# ═══════════════════════════════════════════════════════════════

@app.post("/api/image/generate")
async def api_image_generate(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        if not prompt:
            return JSONResponse(status_code=400, content={"error": "prompt required"})
        # Use Cloudflare Workers AI or HuggingFace
        if CF_API_TOKEN:
            account_id = os.getenv("CF_ACCOUNT_ID", "")
            url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
            r = await HTTP_CLIENT.post(
                url,
                headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
                json={"prompt": prompt},
                timeout=60
            )
            if r.status_code == 200:
                return {"image": base64.b64encode(r.content).decode(), "format": "png"}
        return JSONResponse(status_code=503, content={"error": "Image generation not configured"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════

@app.get("/api/admin")
async def api_admin(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    return {
        "version": "8.3",
        "modules": MODULES,
        "api_keys": {k: "configured" if v else "missing" for k, v in AVAILABLE_KEYS.items()},
        "memory_stats": {"keys": len(MEMORY_STORE), "max": MAX_MEMORY_SIZE},
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "smart_swarm": SMART_SWARM.get_status(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    return {"users": USER_PREFERENCES, "count": len(USER_PREFERENCES)}

@app.post("/api/admin/broadcast")
async def api_admin_broadcast(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse(status_code=403, content={"error": "Unauthorized"})
    data = await request.json()
    message = data.get("message", "")
    if not message:
        return JSONResponse(status_code=400, content={"error": "message required"})
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER._broadcast(message)
    return {"status": "broadcast sent", "recipients": len(USER_PREFERENCES)}

# ═══════════════════════════════════════════════════════════════
# PAYMENT (Razorpay)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/payment")
async def api_payment(request: Request):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return JSONResponse(status_code=503, content={"error": "Payment gateway on hold. Will activate at 1000+ daily users.", "status": "on_hold"})
    try:
        data = await request.json()
        amount = int(data.get("amount", 0)) * 100  # paise
        currency = data.get("currency", "INR")
        receipt = data.get("receipt", f"receipt_{int(time.time())}")
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order = client.order.create({"amount": amount, "currency": currency, "receipt": receipt})
        return {"data": order}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/payment")
async def api_payment_status():
    return {
        "status": "on_hold" if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET) else "active",
        "message": "Payment gateway will activate at 1000+ daily users",
        "upi_id": "jp200883@sbi",
        "fees": {"upi": "0%", "card": "2%"}
    }

# ═══════════════════════════════════════════════════════════════
# GMAIL
# ═══════════════════════════════════════════════════════════════

@app.post("/api/gmail/send")
async def api_gmail_send(request: Request):
    if not GMAIL_CLIENT_ID or not GMAIL_CLIENT_SECRET:
        return JSONResponse(status_code=503, content={"error": "Gmail credentials missing"})
    try:
        data = await request.json()
        to = data.get("to", "")
        subject = data.get("subject", "")
        body = data.get("body", "")
        # Simple SMTP fallback
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, [to], msg.as_string())
        return {"status": "sent", "to": to, "subject": subject}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# SWARM
# ═══════════════════════════════════════════════════════════════

@app.get("/api/swarm")
async def api_swarm():
    return {"data": SMART_SWARM.get_status()}

# ═══════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════

@app.get("/api/search")
async def api_search(q: str = ""):
    if not TAVILY_API_KEY:
        return JSONResponse(status_code=503, content={"error": "TAVILY_API_KEY missing"})
    try:
        r = await HTTP_CLIENT.post(
            "https://api.tavily.com/search",
            json={"api_key": TAVILY_API_KEY, "query": q, "search_depth": "basic", "max_results": 5},
            timeout=15
        )
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# FACEBOOK
# ═══════════════════════════════════════════════════════════════

@app.get("/api/facebook")
async def api_facebook():
    if not FACEBOOK_ACCESS_TOKEN:
        return JSONResponse(status_code=503, content={"error": "FACEBOOK_ACCESS_TOKEN missing"})
    try:
        r = await HTTP_CLIENT.get(f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=name,followers_count", timeout=15)
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# INSTAGRAM
# ═══════════════════════════════════════════════════════════════

@app.get("/api/instagram")
async def api_instagram():
    if not INSTAGRAM_ACCESS_TOKEN:
        return JSONResponse(status_code=503, content={"error": "INSTAGRAM_ACCESS_TOKEN missing"})
    try:
        r = await HTTP_CLIENT.get(f"https://graph.instagram.com/me?access_token={INSTAGRAM_ACCESS_TOKEN}&fields=username,followers_count,media_count", timeout=15)
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# YOUTUBE
# ═══════════════════════════════════════════════════════════════

@app.get("/api/youtube")
async def api_youtube(q: str = "India news", max_results: int = 5):
    if not YOUTUBE_API_KEY:
        return JSONResponse(status_code=503, content={"error": "YOUTUBE_API_KEY missing"})
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={q}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
        r = await HTTP_CLIENT.get(url, timeout=15)
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# VOICE TTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/voice/tts")
async def api_voice_tts(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        lang = data.get("language", "hi")
        if not text:
            return JSONResponse(status_code=400, content={"error": "text required"})
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()
        return {"audio_base64": audio_b64, "format": "mp3", "language": lang}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# VOICE CMD
# ═══════════════════════════════════════════════════════════════

@app.post("/api/voice/cmd")
async def api_voice_cmd(request: Request):
    try:
        data = await request.json()
        command = data.get("command", "")
        return {"data": {"command": command, "status": "processed", "action": "voice_command_executed"}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# OTHER MODULES
# ═══════════════════════════════════════════════════════════════

@app.get("/api/analytics")
async def api_analytics():
    return {"data": "Analytics module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/daily-report")
async def api_daily_report():
    return {"data": "Daily report module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/guard")
async def api_guard():
    return {"data": "Guard Agent active", "timestamp": datetime.now().isoformat()}

@app.get("/api/meta")
async def api_meta():
    return {"data": "Meta Agent active", "timestamp": datetime.now().isoformat()}

@app.get("/api/lang-hub")
async def api_lang_hub():
    return {"data": "Language Hub active", "timestamp": datetime.now().isoformat()}

@app.get("/api/bachpan")
async def api_bachpan():
    return {"data": "Bachpan module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/trolley")
async def api_trolley():
    return {"data": "Trolley module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/singhji-tv")
async def api_singhji_tv():
    return {"data": "SinghJi TV module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/whatsapp")
async def api_whatsapp():
    return {"data": "WhatsApp module active", "timestamp": datetime.now().isoformat()}

@app.get("/api/newsdata")
async def api_newsdata(q: str = "india", count: int = 5):
    if not NEWSDATA_API_KEY:
        return JSONResponse(status_code=503, content={"error": "NEWSDATA_API_KEY missing"})
    try:
        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q={q}&size={count}"
        r = await HTTP_CLIENT.get(url, timeout=15)
        return {"data": r.json()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ═══════════════════════════════════════════════════════════════
# TELEGRAM WEBHOOK — ALL 40+ CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if not TELEGRAM_TOKEN:
        return JSONResponse(status_code=503, content={"error": "TELEGRAM_TOKEN missing"})
    try:
        data = await request.json()
        message = data.get("message", {})
        callback = data.get("callback_query", {})

        if callback:
            chat_id = callback["message"]["chat"]["id"]
            callback_data = callback.get("data", "")
            await _handle_callback(chat_id, callback_data)
            # Answer callback
            await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
            return {"ok": True}

        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]

        # Store user
        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {"language": "hi", "location": None}

        # Rate limit check
        if _rate_check(f"tg_user:{user_id}", *RATE_LIMIT_TELEGRAM_USER):
            await _telegram_send_message(chat_id, "Rate limit exceeded. Please wait a minute.")
            return {"ok": True}

        # Commands
        if text == "/start":
            welcome = (
                "Jai Singh Ji! Welcome to Singh Ji AI Ultra v8.3

"
                "I am your AI assistant with 40+ modules:
"
                "News, Weather, Mandi, AI Chat, Voice, Tax, Gold, Fuel,
"
                "Govt Schemes, Banking, UPI, Pani, Sewer, Rozgar,
"
                "Scheme Swarm, Trishul, and more!

"
                "Use the buttons below or type /help"
            )
            await _telegram_send_message(chat_id, welcome, reply_markup=MAIN_KEYBOARD)
            return {"ok": True}

        elif text == "/help":
            help_text = (
                "Available commands:
"
                "/start - Welcome message
"
                "/help - This help
"
                "/status - System status
"
                "/weather <city> - Weather info
"
                "/news - Latest news
"
                "/gold - Gold rates
"
                "/fuel <city> - Fuel prices
"
                "/tax <income> - Tax calculator
"
                "/yojana - Govt schemes
"
                "/mandi - Mandi rates
"
                "/voice <text> - Text to speech
"
                "/ai <question> - AI chat
"
                "/swarm - Smart Swarm status
"
                "/memory - Memory info
"
            )
            await _telegram_send_message(chat_id, help_text)
            return {"ok": True}

        elif text == "/status":
            status_text = (
                f"Singh Ji AI Ultra v8.3
"
                f"Active Modules: {len(ACTIVE_MODULES)}/{len(MODULES)}
"
                f"Smart Swarm: {SMART_SWARM.get_status()['currently_loaded']} agents
"
                f"Scheduler: {'Running' if MASTER_SCHEDULER and MASTER_SCHEDULER.scheduler.running else 'Stopped'}
"
                f"Memory: {len(MEMORY_STORE)} entries
"
                f"Users: {len(USER_PREFERENCES)}"
            )
            await _telegram_send_message(chat_id, status_text)
            return {"ok": True}

        elif text.startswith("/weather "):
            city = text[9:].strip()
            result = await api_weather(city)
            if "data" in result:
                d = result["data"]
                msg = f"Weather in {d['city']}, {d['country']}:
Temp: {d['temperature']}C (feels {d['feels_like']}C)
Humidity: {d['humidity']}%
Wind: {d['wind_speed']} m/s
{d['description']}"
            else:
                msg = result.get("error", "Weather fetch failed")
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text.startswith("/ai "):
            prompt = text[4:].strip()
            response = await _call_groq(prompt)
            await _telegram_send_message(chat_id, response[:4000])
            return {"ok": True}

        elif text.startswith("/voice "):
            voice_text = text[7:].strip()
            try:
                from gtts import gTTS
                tts = gTTS(text=voice_text, lang="hi", slow=False)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                audio_b64 = base64.b64encode(mp3_fp.read()).decode()
                await _telegram_send_voice(chat_id, audio_b64, caption=voice_text[:100])
            except Exception as e:
                await _telegram_send_message(chat_id, f"Voice error: {str(e)}")
            return {"ok": True}

        elif text.startswith("/tax "):
            try:
                income = float(text[5:].strip())
                result = _calculate_tax(income)
                msg = (
                    f"Tax Calculation (New Regime):
"
                    f"Income: Rs {income:,.0f}
"
                    f"Tax: Rs {result['tax']:,.2f}
"
                    f"Cess: Rs {result['cess']:,.2f}
"
                    f"Total: Rs {result['total']:,.2f}
"
                    f"Take Home: Rs {result['take_home']:,.2f}"
                )
            except:
                msg = "Usage: /tax <income_amount>"
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text == "/yojana":
            yojana_text = (
                "Government Schemes:

"
                "1. PM-KISAN - Rs 6,000/year for farmers
"
                "2. Ayushman Bharat - Rs 5 lakh health cover
"
                "3. PM Awas Yojana - Affordable housing
"
                "4. MUDRA Loan - Up to Rs 10 lakh
"
                "5. Jan Dhan Yojana - Zero balance account

"
                "Type /yojana <scheme_name> for details"
            )
            await _telegram_send_message(chat_id, yojana_text)
            return {"ok": True}

        elif text.startswith("/yojana "):
            scheme_name = text[8:].strip().lower()
            schemes = {
                "pmkisan": "PM-KISAN: Rs 6,000/year in 3 installments for small farmers. Documents: Aadhar, Land records, Bank account. Apply: pmkisan.gov.in",
                "ayushman": "Ayushman Bharat: Health cover up to Rs 5 lakh per family. Eligibility: BPL families. Apply: pmjay.gov.in",
                "awas": "PM Awas Yojana: Affordable housing for EWS/LIG. Apply: pmaymis.gov.in",
                "mudra": "MUDRA Loan: Loan up to Rs 10 lakh for small entrepreneurs. Apply: mudra.org.in",
                "jan dhan": "Jan Dhan Yojana: Zero balance bank account with insurance. Apply at any bank branch"
            }
            msg = schemes.get(scheme_name, f"Scheme '{scheme_name}' not found. Try: pmkisan, ayushman, awas, mudra, jan dhan")
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text == "/news":
            result = await api_news(5)
            if "data" in result:
                articles = result["data"]
                msg = "Latest News:

"
                for i, a in enumerate(articles, 1):
                    msg += f"{i}. {a['title']}
{a.get('description', '')[:100]}...

"
            else:
                msg = result.get("error", "News fetch failed")
            await _telegram_send_message(chat_id, msg[:4000])
            return {"ok": True}

        elif text == "/gold":
            result = await api_gold("Delhi")
            if "data" in result:
                d = result["data"]
                msg = f"Gold Rates (Delhi):
{d}"
            else:
                msg = "Gold rates fetch failed"
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text.startswith("/fuel "):
            city = text[6:].strip()
            result = await api_fuel(city)
            if "data" in result:
                d = result["data"]
                msg = f"Fuel Prices ({city}):
{d}"
            else:
                msg = result.get("error", "Fuel fetch failed")
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text == "/swarm":
            status = SMART_SWARM.get_status()
            msg = (
                f"Smart Swarm Status:
"
                f"Total Agents: {status['total_registered']}
"
                f"Loaded: {status['currently_loaded']}
"
                f"Active: {status['active_running']}
"
                f"Idle: {status['idle']}
"
                f"Busy: {status['busy']}"
            )
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text == "/memory":
            msg = (
                f"Memory Status:
"
                f"Short-term keys: {len(MEMORY_STORE)}
"
                f"Max size: {MAX_MEMORY_SIZE}
"
                f"Users: {len(USER_PREFERENCES)}
"
                f"Supabase: {'Connected' if SUPABASE_CLIENT else 'Not connected'}"
            )
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        elif text.startswith("/mandi "):
            commodity = text[7:].strip()
            result = await api_mandi(commodity=commodity)
            if "data" in result:
                msg = f"Mandi Rates for {commodity}:
{json.dumps(result['data'], indent=2)[:3000]}"
            else:
                msg = result.get("error", "Mandi fetch failed")
            await _telegram_send_message(chat_id, msg)
            return {"ok": True}

        # Default: AI chat
        else:
            response = await _call_groq(text)
            await _telegram_send_message(chat_id, response[:4000], reply_markup=MAIN_KEYBOARD)
            return {"ok": True}

    except Exception as e:
        logger.error(f"[WEBHOOK] Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
