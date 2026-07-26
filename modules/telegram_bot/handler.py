
import logging
import os
import json
import io
import hmac
import hashlib
import asyncio
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from collections import OrderedDict

from fastapi import FastAPI, APIRouter, Request, HTTPException

# ✅ CORRECT IMPORTS for python-telegram-bot v20+
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

class Config:
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.API_BASE_URL = os.getenv("API_BASE_URL", "https://singhji.ai/api")
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "singhji_webhook_secret_2024")
        self.ADMIN_KEY = os.getenv("ADMIN_KEY", "singhji_admin_2024")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
        self.RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        self.MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))
        self.MEMORY_TTL = int(os.getenv("MEMORY_TTL", "86400"))

config = Config()

# ═══════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🤖 AGENTIC-A IMPORTS
# ═══════════════════════════════════════════════════════

import sys

agentic_path = os.path.join(os.path.dirname(__file__), '..', 'agentic_a')
if agentic_path not in sys.path:
    sys.path.insert(0, agentic_path)

video_gen_path = os.path.join(os.path.dirname(__file__), '..', 'video_gen')
if video_gen_path not in sys.path:
    sys.path.insert(0, video_gen_path)

oauth_path = os.path.join(os.path.dirname(__file__), '..', 'oauth_connector')
if oauth_path not in sys.path:
    sys.path.insert(0, oauth_path)

try:
    from agentic_brain import AgenticBrain
    agentic = AgenticBrain()
    AGENTIC_AVAILABLE = True
    logger.info("Agentic-A loaded successfully!")
except ImportError as e:
    logger.warning(f"Agentic-A not available: {e}")
    AGENTIC_AVAILABLE = False

# ═══════════════════════════════════════════════════════
# CONVERSATION STATE MANAGER
# ═══════════════════════════════════════════════════════

class ConversationState:
    NONE = "none"
    WEATHER_CITY = "weather_city"
    MANDI_STATE = "mandi_state"
    TAX_INCOME = "tax_income"
    GOLD_CITY = "gold_city"
    FUEL_CITY = "fuel_city"
    CURRENCY_PAIR = "currency_pair"
    SEARCH_QUERY = "search_query"
    # SCHEME SWARM STATES
    SCHEME_AGE = "scheme_age"
    SCHEME_INCOME = "scheme_income"
    SCHEME_STATE = "scheme_state"
    SCHEME_OCCUPATION = "scheme_occupation"
    SCHEME_CASTE = "scheme_caste"
    SCHEME_FAMILY = "scheme_family"

class ConversationManager:
    def __init__(self):
        self.states: Dict[int, str] = {}
        self.data: Dict[int, Dict] = {}

    def set_state(self, user_id: int, state: str, data: Dict = None):
        self.states[user_id] = state
        if data:
            self.data[user_id] = data
        else:
            self.data[user_id] = {}

    def get_state(self, user_id: int) -> Dict[str, Any]:
        return {
            "state": self.states.get(user_id, ConversationState.NONE),
            "data": self.data.get(user_id, {})
        }

    def clear_state(self, user_id: int):
        self.states.pop(user_id, None)
        self.data.pop(user_id, None)

    def update_data(self, user_id: int, key: str, value: Any):
        if user_id not in self.data:
            self.data[user_id] = {}
        self.data[user_id][key] = value

conversation_mgr = ConversationManager()

# ═══════════════════════════════════════════════════════
# LANGUAGE MANAGER
# ═══════════════════════════════════════════════════════

class LanguageManager:
    def __init__(self):
        self.lang_names = {
            "hi": "🇮🇳 Hindi",
            "en": "🇬🇧 English",
            "ta": "🇮🇳 Tamil",
            "te": "🇮🇳 Telugu",
            "mr": "🇮🇳 Marathi",
            "bn": "🇮🇳 Bengali",
            "gu": "🇮🇳 Gujarati",
            "pa": "🇮🇳 Punjabi"
        }
        self.user_langs: Dict[int, str] = {}

    def get_system_prompt(self, user_id: int) -> str:
        lang = self.user_langs.get(user_id, "hi")
        prompts = {
            "hi": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Hinglish (Hindi + English mixed). Be friendly, helpful, and respectful.
Use simple language that everyone can understand.
Rules:
- Never give harmful advice
- Give financial advice responsibly
- Respect privacy
- Stay positive!
- Be respectful, especially to elders
- Give simple answers to technical questions
- Have knowledge about agriculture, farming, rural India""",
            "en": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in English. Be friendly, helpful, and respectful.
Use simple English that everyone can understand.
Rules:
- Never give harmful advice
- Give financial advice responsibly
- Respect privacy
- Stay positive!""",
            "ta": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Tamil language. Be friendly, helpful, and respectful.
Use simple Tamil that everyone can understand.""",
            "te": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Telugu language. Be friendly, helpful, and respectful.
Use simple Telugu that everyone can understand.""",
            "mr": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Marathi language. Be friendly, helpful, and respectful.
Use simple Marathi that everyone can understand.""",
            "bn": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Bengali language. Be friendly, helpful, and respectful.
Use simple Bengali that everyone can understand.""",
            "gu": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Gujarati language. Be friendly, helpful, and respectful.
Use simple Gujarati that everyone can understand.""",
            "pa": """You are Singh Ji AI - India's most powerful AI assistant!
Respond in Punjabi language. Be friendly, helpful, and respectful.
Use simple Punjabi that everyone can understand."""
        }
        return prompts.get(lang, prompts["hi"])

    def get_all_langs_keyboard(self):
        keyboard = []
        row = []
        for code, name in self.lang_names.items():
            row.append(InlineKeyboardButton(name, callback_data=f"set_lang_{code}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="settings")])
        return InlineKeyboardMarkup(keyboard)

    def set_lang(self, user_id: int, lang_code: str) -> bool:
        if lang_code in self.lang_names:
            self.user_langs[user_id] = lang_code
            return True
        return False

    def get_lang_name(self, user_id: int) -> str:
        lang = self.user_langs.get(user_id, "hi")
        return self.lang_names.get(lang, "Hindi")

lang_mgr = LanguageManager()

# ═══════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════

class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = {}

    async def is_allowed(self, user_id: int) -> bool:
        now = datetime.now()
        if user_id not in self.requests:
            self.requests[user_id] = []
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests[user_id] = [req for req in self.requests[user_id] if req > cutoff]
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        self.requests[user_id].append(now)
        return True

    def get_user_requests(self, user_id: int) -> int:
        return len(self.requests.get(user_id, []))

rate_limiter = RateLimiter(config.RATE_LIMIT_MAX, config.RATE_LIMIT_WINDOW)

# ═══════════════════════════════════════════════════════
# LRU MEMORY SYSTEM
# ═══════════════════════════════════════════════════════

class UserMemory:
    def __init__(self, max_size: int = 1000, ttl: int = 86400):
        self.memory = OrderedDict()
        self.timestamps = {}
        self.metadata = {}
        self.max_size = max_size
        self.ttl = ttl

    def get(self, user_id: int) -> Dict[str, Any]:
        self._cleanup()
        if user_id in self.memory:
            return {
                "content": self.memory[user_id],
                "timestamp": self.timestamps.get(user_id),
                "metadata": self.metadata.get(user_id, {})
            }
        return {"content": "", "timestamp": None, "metadata": {}}

    def set(self, user_id: int, content: str, metadata: Dict = None):
        self._cleanup()
        if len(self.memory) >= self.max_size:
            oldest = next(iter(self.memory))
            del self.memory[oldest]
            self.timestamps.pop(oldest, None)
            self.metadata.pop(oldest, None)
        self.memory[user_id] = content
        self.timestamps[user_id] = time.time()
        self.metadata[user_id] = metadata or {}

    def delete(self, user_id: int):
        self.memory.pop(user_id, None)
        self.timestamps.pop(user_id, None)
        self.metadata.pop(user_id, None)

    def _cleanup(self):
        now = time.time()
        expired = [uid for uid, ts in self.timestamps.items() if now - ts > self.ttl]
        for uid in expired:
            self.memory.pop(uid, None)
            self.timestamps.pop(uid, None)
            self.metadata.pop(uid, None)

    @property
    def size(self) -> int:
        return len(self.memory)

    @property
    def stats(self) -> Dict:
        return {
            "total_users": len(self.memory),
            "max_size": self.max_size,
            "ttl_hours": self.ttl / 3600,
            "oldest_entry": min(self.timestamps.values()) if self.timestamps else None,
            "newest_entry": max(self.timestamps.values()) if self.timestamps else None
        }

user_memory = UserMemory(config.MEMORY_MAX_SIZE, config.MEMORY_TTL)

# ═══════════════════════════════════════════════════════
# ANALYTICS SYSTEM
# ═══════════════════════════════════════════════════════

class BotAnalytics:
    def __init__(self):
        self.stats = {
            "total_messages": 0,
            "voice_messages": 0,
            "text_messages": 0,
            "commands": 0,
            "ai_responses": 0,
            "errors": 0,
            "unique_users": set(),
            "active_users_24h": set(),
            "module_usage": {}
        }
        self.start_time = datetime.now()

    def track_message(self, user_id: int, message_type: str):
        self.stats["total_messages"] += 1
        self.stats["unique_users"].add(user_id)
        self.stats["active_users_24h"].add(user_id)
        if message_type == "voice":
            self.stats["voice_messages"] += 1
        elif message_type == "text":
            self.stats["text_messages"] += 1
        elif message_type == "command":
            self.stats["commands"] += 1

    def track_error(self):
        self.stats["errors"] += 1

    def track_module_usage(self, module_name: str):
        self.stats["module_usage"][module_name] = self.stats["module_usage"].get(module_name, 0) + 1

    def get_summary(self) -> Dict:
        uptime = datetime.now() - self.start_time
        return {
            "uptime": str(uptime),
            "total_messages": self.stats["total_messages"],
            "unique_users": len(self.stats["unique_users"]),
            "active_users_24h": len(self.stats["active_users_24h"]),
            "voice_messages": self.stats["voice_messages"],
            "text_messages": self.stats["text_messages"],
            "commands": self.stats["commands"],
            "errors": self.stats["errors"],
            "top_modules": sorted(self.stats["module_usage"].items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def reset_daily(self):
        self.stats["active_users_24h"] = set()

analytics = BotAnalytics()

# ═══════════════════════════════════════════════════════
# SAFE SEND HELPERS — parse_mode entity crash से बचने के लिए
# ═══════════════════════════════════════════════════════

async def safe_reply_text(message_obj, text: str, parse_mode=None, reply_markup=None, **kwargs):
    """
    update.message.reply_text की जगह इसे इस्तेमाल करो। अगर parse_mode
    (Markdown/HTML) के साथ भेजने पर 'Can't parse entities' जैसी BadRequest
    एरर आती है (क्योंकि टेक्स्ट में * _ ` [ जैसे unmatched characters हैं
    — जो अक्सर AI response, news headline, या यूज़र-इनपुट में होते हैं),
    तो यह अपने आप बिना parse_mode के प्लेन टेक्स्ट भेज देगा — ताकि मैसेज
    कम से कम पहुँचे तो सही, भले फॉर्मैटिंग (bold/italic) चली जाए।
    """
    from telegram.error import BadRequest
    try:
        return await message_obj.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)
    except BadRequest as e:
        if "can't parse entities" in str(e).lower() or "can't find end" in str(e).lower():
            logger.warning(f"[SAFE_SEND] parse_mode एंटिटी एरर, plain text से भेजा जा रहा है: {e}")
            return await message_obj.reply_text(text, parse_mode=None, reply_markup=reply_markup, **kwargs)
        raise


async def safe_edit_text(query_obj, text: str, parse_mode=None, reply_markup=None, **kwargs):
    """query.edit_message_text के लिए वही सुरक्षा — ऊपर safe_reply_text जैसा"""
    from telegram.error import BadRequest
    try:
        return await query_obj.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)
    except BadRequest as e:
        if "can't parse entities" in str(e).lower() or "can't find end" in str(e).lower():
            logger.warning(f"[SAFE_SEND] parse_mode एंटिटी एरर (edit), plain text से भेजा जा रहा है: {e}")
            return await query_obj.edit_message_text(text, parse_mode=None, reply_markup=reply_markup, **kwargs)
        raise


async def safe_edit_text_msg(msg_obj, text: str, parse_mode=None, reply_markup=None, **kwargs):
    """Message.edit_text के लिए सुरक्षा — video/post commands में use होगा"""
    from telegram.error import BadRequest
    try:
        return await msg_obj.edit_text(text, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)
    except BadRequest as e:
        if "can't parse entities" in str(e).lower() or "can't find end" in str(e).lower():
            logger.warning(f"[SAFE_SEND] parse_mode एंटिटी एरर (msg edit), plain text से भेजा जा रहा है: {e}")
            return await msg_obj.edit_text(text, parse_mode=None, reply_markup=reply_markup, **kwargs)
        raise

# ═══════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════

def rate_limit_check(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not await rate_limiter.is_allowed(user.id):
            await safe_reply_text(
                update.message,
                "🚫 Rate Limit! Thoda slow karo! 1 minute mein try karo!",
                parse_mode=None
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def error_handler_decorator(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            analytics.track_error()
            error_msg = "❌ Error! Kuch problem ho gayi! Admin ko bata diya hai. Thodi der mein try karo!"
            try:
                if update.message:
                    await safe_reply_text(update.message, error_msg, parse_mode=None)
                elif update.callback_query:
                    await safe_reply_text(update.callback_query.message, error_msg, parse_mode=None)
            except:
                pass
            raise
    return wrapper

# ═══════════════════════════════════════════════════════
# AI BRAIN SYSTEM
# ═══════════════════════════════════════════════════════

class AIBrain:
    def __init__(self):
        self.current_modes = {}

    async def get_response(self, user_text: str, user_id: int, user_name: str = "User", chat_type: str = "private") -> Dict[str, Any]:
        if not user_text or not user_text.strip():
            return {"text": f"{user_name}, kuch toh bolo!", "error": False}
        if len(user_text) > 1000:
            user_text = user_text[:1000] + "..."
        memory_data = user_memory.get(user_id)
        context = memory_data.get("content", "")
        system_prompt = lang_mgr.get_system_prompt(user_id)
        intent = self._detect_intent(user_text)
        messages = [
            {
                "role": "system",
                "content": f"""{system_prompt}
Current Context:
- User: {user_name}
- Chat Type: {chat_type}
- Previous Memory: {context}
- Detected Intent: {intent}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            },
            {"role": "user", "content": user_text}
        ]
        try:
            import groq
            client = groq.Groq(api_key=config.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            answer = response.choices[0].message.content
            user_memory.set(user_id, f"[{datetime.now().strftime('%H:%M')}] {user_text[:100]}",
                          metadata={"last_intent": intent})
            analytics.track_module_usage("ai_chat")
            return {"text": answer, "error": False, "intent": intent}
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            if "rate" in str(e).lower():
                return {"text": "⏳ Thoda busy hoon! 1 minute mein try karo!", "error": True}
            elif "auth" in str(e).lower():
                return {"text": "🔑 AI dimag restart karna padega! Admin ko batao!", "error": True}
            else:
                return {"text": f"Arre {user_name}, network issue! Text se bolo kya chahiye!", "error": True}

    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        intents = {
            "weather": ["mausam", "weather", "baarish", "garmi", "thand"],
            "news": ["news", "khabar", "samachar", "aaj ki news"],
            "gold": ["sona", "gold", "silver", "chandi"],
            "fuel": ["petrol", "diesel", "fuel", "tel"],
            "mandi": ["mandi", "bhav", "rate", "fasal"],
            "farming": ["kheti", "kisaan", "beej", "khad"],
            "greeting": ["hello", "hi", "namaste", "ram ram"],
            "help": ["help", "madad", "sahayata", "kya kar sakte ho"],
            "joke": ["joke", "majak", "hasi", "funny"],
            "technical": ["code", "programming", "bug", "error", "api"]
        }
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                return intent
        return "general"

ai_brain = AIBrain()

# ═══════════════════════════════════════════════════════
# TEXT TO SPEECH SYSTEM
# ═══════════════════════════════════════════════════════

class TTSEngine:
    def __init__(self):
        self.languages = {
            "hi": "Hindi", "en": "English", "ta": "Tamil", "te": "Telugu",
            "mr": "Marathi", "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi"
        }
        self.user_languages = {}

    async def text_to_speech(self, text: str, user_id: Optional[int] = None) -> Optional[bytes]:
        try:
            from gtts import gTTS
            lang = self.user_languages.get(user_id, "hi") if user_id else "hi"
            short_text = text[:500] if len(text) > 500 else text
            tts = gTTS(text=short_text, lang=lang, slow=False)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.read()
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

    def set_language(self, user_id: int, lang: str):
        if lang in self.languages:
            self.user_languages[user_id] = lang
            return True
        return False

    def get_language(self, user_id: int) -> str:
        return self.user_languages.get(user_id, "hi")

tts_engine = TTSEngine()

# ═══════════════════════════════════════════════════════
# ACTIVE MODULES
# ═══════════════════════════════════════════════════════

ACTIVE_MODULES = {
    "Weather": "weather", "News": "news", "AI Chat": "ai_chat",
    "Currency": "currency", "Gold Rate": "goldrate", "Fuel Price": "fuel",
    "Mandi Rates": "mandi", "Rozgar": "rozgar", "Pani": "pani",
    "Plant ID": "plant_id", "Search": "search", "Analytics": "analytics",
    "Guard Agent": "guard_agent", "Trishul": "trishul", "Trolley": "trolley",
    "Schedule": "schedule", "Daily Report": "daily_report", "Emergency": "emergency",
    "Scheme Swarm": "scheme_swarm", "Singh Ji TV": "singhji_tv", "Voice": "voice",
    "UPI": "upi", "Banking": "banking", "WhatsApp": "whatsapp",
    "Language Hub": "language_hub", "Horoscope": "horoscope", "Bachpan": "bachpan",
    "Aavishkar": "aavishkar", "Meta Agent": "meta_agent", "Supreme Agent": "supreme_agent",
    "Smart Swarm": "smart_swarm", "Currents API": "currents_api", "NewsData": "newsdata",
    "News Scheduler": "news_scheduler", "OAuth": "oauth_connector",
    "Supabase Memory": "supabase_memory", "Telegram Bot": "telegram_bot",
    "Language": "language", "Mini-Program": "miniprogram", "Mini Auth": "mini_auth",
    "Claw 7": "claw_7", "Voice CMD": "voice_cmd", "Voice TTS": "voice_tts",
    "Init": "init", "Singh Ji AI Ultra": "singhji_ultra",
}

# ═══════════════════════════════════════════════════════
# API HELPERS
# ═══════════════════════════════════════════════════════

async def fetch_and_send_weather(update: Update, city: str):
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/weather/",
            params={"city": city},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            temp = data.get("temperature", "N/A")
            condition = data.get("condition", "N/A")
            humidity = data.get("humidity", "N/A")
            await update.message.reply_text(
                f"🌤️ Weather in {city.title()}\n\n"
                f"🌡️ Temperature: {temp}°C\n"
                f"☁️ Condition: {condition}\n"
                f"💧 Humidity: {humidity}%\n\n"
                f"Singh Ji AI - Har pal saath!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.main_menu()
            )
        else:
            await safe_reply_text(
                update.message,
                f"❌ {city} ka weather nahi mila! Sahi city name try karo!",
                parse_mode=None
            )
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        await safe_reply_text(
            update.message,
            "❌ Weather service down! Baad mein try karo!",
            parse_mode=None
        )

async def fetch_and_send_mandi(update: Update, state: str):
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/mandi/",
            params={"state": state},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", [])
            if rates:
                msg = f"🌾 Mandi Rates - {state.title()}\n\n"
                for rate in rates[:10]:
                    msg += f"- {rate.get('commodity', 'N/A')}: Rs.{rate.get('price', 'N/A')}/quintal\n"
                await safe_reply_text(
                    update.message,
                    msg,
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.main_menu()
                )
            else:
                await safe_reply_text(
                    update.message,
                    f"❌ {state.title()} ke liye koi data nahi mila!",
                    parse_mode=None
                )
        else:
            await safe_reply_text(
                update.message,
                f"❌ {state} ka data nahi mila!",
                parse_mode=None
            )
    except Exception as e:
        logger.error(f"Mandi fetch error: {e}")
        await safe_reply_text(
            update.message,
            "❌ Mandi service down! Baad mein try karo!",
            parse_mode=None
        )

async def calculate_and_send_tax(update: Update, income: float):
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/tax/",
            params={"income": income},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            tax = data.get("tax", 0)
            regime = data.get("regime", "N/A")
            await update.message.reply_text(
                f"💰 Tax Calculation\n\n"
                f"Income: Rs.{income:,.0f}\n"
                f"Tax: Rs.{tax:,.0f}\n"
                f"Regime: {regime}\n\n"
                f"⚠️ Ye estimate hai, CA se confirm karo!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.main_menu()
            )
        else:
            await safe_reply_text(
                update.message,
                "❌ Tax calculation failed!",
                parse_mode=None
            )
    except Exception as e:
        logger.error(f"Tax calc error: {e}")
        await safe_reply_text(
            update.message,
            "❌ Tax service down! Baad mein try karo!",
            parse_mode=None
        )

async def fetch_and_send_gold(update: Update, city: str = "India"):
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/goldrate/",
            params={"city": city},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            gold_24k = data.get("gold_24k", "N/A")
            gold_22k = data.get("gold_22k", "N/A")
            silver = data.get("silver", "N/A")
            await update.message.reply_text(
                f"🥇 Gold Rate - {city.title()}\n\n"
                f"24K: Rs.{gold_24k}/10g\n"
                f"22K: Rs.{gold_22k}/10g\n"
                f"Silver: Rs.{silver}/kg\n\n"
                f"Rate change hote rehte hain!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.main_menu()
            )
        else:
            await safe_reply_text(update.message, "❌ Gold rate nahi mila!", parse_mode=None)
    except Exception as e:
        logger.error(f"Gold fetch error: {e}")
        await safe_reply_text(update.message, "❌ Gold service down!", parse_mode=None)

async def fetch_and_send_fuel(update: Update, city: str):
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/fuel/",
            params={"city": city},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            petrol = data.get("petrol", "N/A")
            diesel = data.get("diesel", "N/A")
            await update.message.reply_text(
                f"⛽ Fuel Prices - {city.title()}\n\n"
                f"Petrol: Rs.{petrol}/L\n"
                f"Diesel: Rs.{diesel}/L\n\n"
                f"Aaj ka rate!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.main_menu()
            )
        else:
            await safe_reply_text(update.message, "❌ Fuel price nahi mila!", parse_mode=None)
    except Exception as e:
        logger.error(f"Fuel fetch error: {e}")
        await safe_reply_text(update.message, "❌ Fuel service down!", parse_mode=None)

# ═══════════════════════════════════════════════════════
# 🏛️ SCHEME SWARM HELPERS
# ═══════════════════════════════════════════════════════

SCHEMES_DATA = []

def load_schemes_data():
    global SCHEMES_DATA
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'modules', 'scheme_swarm', 'data', 'central_schemes.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                SCHEMES_DATA = json.load(f)
            logger.info(f"Loaded {len(SCHEMES_DATA)} schemes from JSON")
        else:
            SCHEMES_DATA = [
                {"id": "pmkisan", "name": "PM-KISAN", "category": "Agriculture", "min_age": 18, "max_age": 100, "max_income": 200000, "occupations": ["farmer"], "castes": ["all"], "amount": 6000, "frequency": "Yearly", "description": "₹6000 per year direct income support to farmers", "documents": ["Aadhaar", "Bank Passbook", "Land Records"], "website": "pmkisan.gov.in"},
                {"id": "pmay", "name": "PMAY (Housing)", "category": "Housing", "min_age": 18, "max_age": 70, "max_income": 300000, "occupations": ["all"], "castes": ["all"], "amount": 250000, "frequency": "One-time", "description": "Affordable housing for all", "documents": ["Aadhaar", "Income Certificate", "Bank Account"], "website": "pmaymis.gov.in"},
                {"id": "ayushman", "name": "Ayushman Bharat", "category": "Health", "min_age": 0, "max_age": 100, "max_income": 500000, "occupations": ["all"], "castes": ["all"], "amount": 500000, "frequency": "Per year", "description": "Health insurance up to ₹5 lakh per family per year", "documents": ["Aadhaar", "Ration Card", "SECC Data"], "website": "pmjay.gov.in"},
                {"id": "mudra", "name": "MUDRA Loan", "category": "Business", "min_age": 18, "max_age": 65, "max_income": 10000000, "occupations": ["business", "self-employed"], "castes": ["all"], "amount": 1000000, "frequency": "Loan", "description": "Loans up to ₹10 lakh for small businesses", "documents": ["Identity Proof", "Business Plan", "Bank Statement"], "website": "mudra.org.in"},
                {"id": "ujjwala", "name": "PM Ujjwala Yojana", "category": "Social Welfare", "min_age": 18, "max_age": 100, "max_income": 0, "occupations": ["all"], "castes": ["all"], "amount": 1600, "frequency": "One-time", "description": "Free LPG connection to BPL families", "documents": ["BPL Card", "Aadhaar", "Bank Account"], "website": "pmuy.gov.in"},
                {"id": "jan_dhan", "name": "PM Jan Dhan Yojana", "category": "Banking", "min_age": 10, "max_age": 100, "max_income": 10000000, "occupations": ["all"], "castes": ["all"], "amount": 0, "frequency": "Account", "description": "Zero balance bank account with insurance", "documents": ["Aadhaar", "Photo"], "website": "pmjdy.gov.in"},
                {"id": "sukanya", "name": "Sukanya Samriddhi", "category": "Girl Child", "min_age": 0, "max_age": 10, "max_income": 10000000, "occupations": ["all"], "castes": ["all"], "amount": 150000, "frequency": "Yearly deposit", "description": "Savings scheme for girl child education", "documents": ["Birth Certificate", "Parent ID", "Bank Account"], "website": "nsiindia.co.in"},
                {"id": "atal_pension", "name": "Atal Pension Yojana", "category": "Pension", "min_age": 18, "max_age": 40, "max_income": 10000000, "occupations": ["all"], "castes": ["all"], "amount": 5000, "frequency": "Monthly pension", "description": "Guaranteed pension of ₹1000-5000/month after 60", "documents": ["Aadhaar", "Bank Account", "Mobile"], "website": "npscra.nsdl.co.in"},
                {"id": "fasal_bima", "name": "PM Fasal Bima Yojana", "category": "Agriculture", "min_age": 18, "max_age": 100, "max_income": 10000000, "occupations": ["farmer"], "castes": ["all"], "amount": 0, "frequency": "Insurance", "description": "Crop insurance for farmers at low premium", "documents": ["Land Records", "Aadhaar", "Bank Account"], "website": "pmfby.gov.in"},
                {"id": "skill_india", "name": "Skill India Mission", "category": "Employment", "min_age": 15, "max_age": 45, "max_income": 500000, "occupations": ["student", "unemployed"], "castes": ["all"], "amount": 0, "frequency": "Training", "description": "Free skill training and certification", "documents": ["Aadhaar", "Education Certificate"], "website": "skillindia.gov.in"},
            ]
            logger.info(f"Loaded {len(SCHEMES_DATA)} fallback schemes")
    except Exception as e:
        logger.error(f"Error loading schemes: {e}")
        SCHEMES_DATA = []

load_schemes_data()

def match_schemes(age: int, income: int, state: str, occupation: str, caste: str, family_size: int) -> List[Dict]:
    matched = []
    for scheme in SCHEMES_DATA:
        score = 0
        reasons = []
        if scheme["min_age"] <= age <= scheme["max_age"]:
            score += 25
        else:
            continue
        if scheme["max_income"] == 0 or income <= scheme["max_income"]:
            score += 25
        else:
            continue
        if "all" in scheme["occupations"] or occupation.lower() in [o.lower() for o in scheme["occupations"]]:
            score += 20
        else:
            score += 5
            reasons.append("Occupation partial match")
        if "all" in scheme["castes"] or caste.lower() in [c.lower() for c in scheme["castes"]]:
            score += 15
        if family_size >= 4 and scheme["category"] in ["Social Welfare", "Housing", "Health"]:
            score += 10
            reasons.append("Large family bonus")
        if occupation.lower() == "farmer" and scheme["category"] == "Agriculture":
            score += 5
            reasons.append("Farmer priority")
        if score >= 50:
            scheme_copy = scheme.copy()
            scheme_copy["match_score"] = min(score, 100)
            scheme_copy["match_reasons"] = reasons
            matched.append(scheme_copy)
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return matched

def get_scheme_by_id(scheme_id: str) -> Optional[Dict]:
    for scheme in SCHEMES_DATA:
        if scheme["id"] == scheme_id:
            return scheme
    return None

# ═══════════════════════════════════════════════════════
# KEYBOARD BUILDERS
# ═══════════════════════════════════════════════════════

class KeyboardBuilder:
    @staticmethod
    def main_menu():
        keyboard = [
            [InlineKeyboardButton("🤖 AI Chat", callback_data="mode_ai"),
             InlineKeyboardButton("🌤️ Weather", callback_data="quick_weather")],
            [InlineKeyboardButton("📰 News", callback_data="quick_news"),
             InlineKeyboardButton("🥇 Gold Rate", callback_data="quick_gold")],
            [InlineKeyboardButton("🏛️ Schemes", callback_data="schemes_menu"),
             InlineKeyboardButton("📦 All Modules", callback_data="list_modules")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
             InlineKeyboardButton("📊 Stats", callback_data="bot_stats")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu(user_id: int):
        voice_status = "ON" if tts_engine.get_language(user_id) != "off" else "OFF"
        current_lang = lang_mgr.get_lang_name(user_id)
        keyboard = [
            [InlineKeyboardButton(f"🔊 Voice: {voice_status}", callback_data="toggle_voice")],
            [InlineKeyboardButton(f"🌐 Language: {current_lang}", callback_data="change_language")],
            [InlineKeyboardButton("🧹 Memory: Clear", callback_data="clear_memory"),
             InlineKeyboardButton("📊 Memory Stats", callback_data="memory_stats")],
            [InlineKeyboardButton("🔔 Notifications: ON", callback_data="toggle_notify")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def modules_keyboard(page: int = 1):
        items_per_page = 10
        modules_list = list(ACTIVE_MODULES.items())
        total_pages = (len(modules_list) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_modules = modules_list[start_idx:end_idx]
        keyboard = []
        for name, code in current_modules:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"use_module_{code}")])
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"modules_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"modules_page_{page+1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def schemes_menu_keyboard():
        keyboard = [
            [InlineKeyboardButton("📋 Profile Banayein", callback_data="scheme_profile_start")],
            [InlineKeyboardButton("🔍 Schemes Dhoondhein", callback_data="scheme_search")],
            [InlineKeyboardButton("📊 Mera Status", callback_data="scheme_status")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def scheme_list_keyboard(schemes: List[Dict], page: int = 0):
        keyboard = []
        start = page * 5
        end = start + 5
        page_schemes = schemes[start:end]
        for scheme in page_schemes:
            score = scheme.get("match_score", 0)
            keyboard.append([InlineKeyboardButton(
                f"{scheme['name']} ({score}% match)",
                callback_data=f"scheme_detail_{scheme['id']}"
            )])
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"scheme_page_{page-1}"))
        if end < len(schemes):
            nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"scheme_page_{page+1}"))
        if nav:
            keyboard.append(nav)
        keyboard.append([InlineKeyboardButton("🔙 Schemes Menu", callback_data="schemes_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def scheme_detail_keyboard(scheme_id: str):
        scheme = get_scheme_by_id(scheme_id)
        website = scheme.get('website', 'india.gov.in') if scheme else 'india.gov.in'
        keyboard = [
            [InlineKeyboardButton("📄 Documents Checklist", callback_data=f"scheme_docs_{scheme_id}")],
            [InlineKeyboardButton("🌐 Official Website", url=f"https://{website}")],
            [InlineKeyboardButton("🔙 Back to List", callback_data="scheme_search")]
        ]
        return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_type = update.effective_chat.type
    analytics.track_message(user.id, "command")
    user_memory.set(user.id, f"Name: {user.first_name}, Started: {datetime.now().isoformat()}",
                   metadata={"chat_type": chat_type, "first_seen": datetime.now().isoformat()})
    welcome_text = f"""
🌟 *SINGH JI AI ULTRA v8.3* 🌟

Welcome {user.first_name}!

🇮🇳 India ka sabse powerful AI assistant!

✅ {len(ACTIVE_MODULES)} Active Modules
🎤 Voice Commands Support
🧠 Memory System
🤖 AI Chat with Groq
👥 Group Chat Support
🔊 Text-to-Speech
🌐 Multi-Language Support

*Quick Start:*
- 📝 Text bhejo - AI jawab dega
- 🎙️ Voice message bhejo - Sunega aur bolega
- 🖲️ Button dabao - Weather, News, Gold direct!
- ⚙️ /settings - Language change karo

*Pro Tips:*
🌤️ "Mausam kaisa hai Delhi mein?"
🥇 "Gold rate batao"
🌾 "Kisaan ke liye sarkari yojana"
🛡️ /bachpan - Child safety helplines
🏛️ /yojana 45 150000 farmer - Sarkari yojana check
🏛️ /scheme_profile - 6-step scheme wizard

Bas message bhejo, baaki main dekh lunga!

*Singh Ji AI - Har Indian ka AI saathi!* 🇮🇳
    """
    await update.message.reply_text(
        welcome_text,
        parse_mode=None,
        reply_markup=KeyboardBuilder.main_menu()
    )

@error_handler_decorator
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analytics.track_message(update.effective_user.id, "command")
    help_text = f"""
📚 *SINGH JI AI HELP CENTER* 📚

*Main Features:*

🤖 *AI Chat:*
- Normal text bhejo - AI jawab dega
- Voice message bhejo - Sunega aur bolega
- Context aware hai - pichli baat yaad rakhta hai

*Commands:*
/start - Welcome message
/help - Yeh help
/modules - Sab {len(ACTIVE_MODULES)} modules
/use <module> - Module directly use karo
/remember <text> - Kuch yaad rakhne ko bolo
/recall - Kya yaad hai pucho
/status - System status
/settings - Settings (Language change!)
/about - Bot ke baare mein
/stats - Usage statistics
/bachpan - Child safety helplines 🛡️
/yojana <age> <income> <occupation> - Sarkari yojana check 🏛️
/scheme_profile - Scheme profile wizard 🏛️
/schemes - Auto-matched schemes 🏛️
/scheme_status <id> - Application tracking 🏛️

*Quick Modules:*
/weather <city> - Mausam
/news - Latest news
/goldrate - Gold rate
/currency - Currency rates
/fuel - Petrol/diesel price

*Voice Features:*
- Voice message bhejo
- "Mausam kaisa hai?"
- "News sunao"
- "Gold rate batao"

*Settings:*
- Voice ON/OFF
- Language change (Hindi, English, Tamil, Telugu, etc.)
- Memory management
- Notifications

*Support:*
Email: support@singhji.ai
Web: singhji.ai
Telegram: @SinghJiAI

*Singh Ji AI - Always learning, always helping!* 🚀
    """
    await update.message.reply_text(
        help_text,
        parse_mode=None,
        reply_markup=KeyboardBuilder.main_menu()
    )

@error_handler_decorator
async def modules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analytics.track_message(update.effective_user.id, "command")
    await update.message.reply_text(
        f"📦 {len(ACTIVE_MODULES)} Active Modules\n\nModule select karo:",
        parse_mode=None,
        reply_markup=KeyboardBuilder.modules_keyboard(1)
    )

@error_handler_decorator
@rate_limit_check
async def use_module_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user
    analytics.track_message(user.id, "command")
    if not args:
        await update.message.reply_text(
            "Usage: /use <module> <query>\n\nExample: /use weather Delhi\n\nModules list ke liye: /modules",
            parse_mode=None
        )
        return
    module = args[0].lower()
    query = " ".join(args[1:]) if len(args) > 1 else ""
    valid_modules = list(ACTIVE_MODULES.values())
    if module not in valid_modules:
        similar = [m for m in valid_modules if module in m][:5]
        suggestion = "\n".join([f"- /{m}" for m in similar])
        await update.message.reply_text(
            f"❌ Module {module} nahi mila!\n\nSimilar modules:\n{suggestion}\n\nSab modules: /modules",
            parse_mode=None
        )
        return
    analytics.track_module_usage(module)
    processing_msg = await update.message.reply_text(
        f"⏳ {module.upper()} module use kar raha hoon...",
        parse_mode=None
    )
    try:
        response = requests.get(
            f"{config.API_BASE_URL}/modules/{module}/",
            params={"q": query},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            if len(formatted_data) > 3500:
                formatted_data = formatted_data[:3500] + "\n... (truncated)"
            # ⚠️ JSON में ``` से जुड़ा markdown code-block होने से पहले भी
            # entity-parse crash हो सकता था अगर JSON में ` या * हों —
            # safe_edit_text इसे प्लेन टेक्स्ट में गिरा देगा तो भी मैसेज पहुँचेगा
            await safe_edit_text(
                processing_msg,
                f"📊 {module.upper()} Result:\n\n```json\n{formatted_data}\n```",
                parse_mode=None
            )
        else:
            await processing_msg.edit_text(
                f"❌ Module error! Status: {response.status_code}",
                parse_mode=None
            )
    except requests.Timeout:
        await processing_msg.edit_text("⏳ Module timeout! Baad mein try karo!")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)[:100]}")

@error_handler_decorator
async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text(
            "Usage: /remember <text>\n\nExample: /remember Mera naam Ram hai, main kisaan hoon\n\nFir /recall se puch sakte ho!",
            parse_mode=None
        )
        return
    user_memory.set(user.id, text, metadata={
        "updated_at": datetime.now().isoformat(),
        "type": "manual_memory"
    })
    await update.message.reply_text(
        f"✅ Yaad rakh liya!\n\nMemory: {text}\n\nKabhi bhi /recall se puch sakte ho!\nClear karne ke liye: /settings",
        parse_mode=None
    )

@error_handler_decorator
async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    memory_data = user_memory.get(user.id)
    content = memory_data.get("content", "Kuch yaad nahi hai!")
    metadata = memory_data.get("metadata", {})
    timestamp = memory_data.get("timestamp")
    if timestamp:
        time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        time_str = "Unknown"
    await update.message.reply_text(
        f"🧠 Tumhari Memory:\n\n{content}\n\nLast Updated: {time_str}\nMetadata: {json.dumps(metadata, indent=2)}\n\nNaya memory: /remember <text>\nClear: /settings",
        parse_mode=None
    )

@error_handler_decorator
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{config.API_BASE_URL}/health", timeout=10)
        api_status = "Online ✅" if response.status_code == 200 else "Offline ❌"
    except:
        api_status = "Offline ❌"
    memory_stats = user_memory.stats
    analytics_summary = analytics.get_summary()
    status_text = f"""
📊 *SYSTEM STATUS*

*Core Services:*
🤖 Bot: Running
🧠 AI: Online ({config.GROQ_API_KEY[:10]}...)
🔊 Voice: Enabled
💾 Memory: Active
🌐 Language: Multi-lang

*API Status:*
🔌 API: {api_status}
⏱️ Rate Limiter: Active

*Memory Stats:*
👥 Users in Memory: {memory_stats['total_users']}
📦 Max Size: {memory_stats['max_size']}
⏰ TTL: {memory_stats['ttl_hours']} hours

*Bot Stats:*
📝 Total Messages: {analytics_summary['total_messages']}
👤 Unique Users: {analytics_summary['unique_users']}
⏱️ Uptime: {analytics_summary['uptime']}
❌ Errors: {analytics_summary['errors']}

*Top Modules:*
{chr(10).join([f"- {mod}: {count}" for mod, count in analytics_summary['top_modules'][:5]])}

*Environment:* {config.ENVIRONMENT}
*Version:* v8.3 Fixed
    """
    await update.message.reply_text(
        status_text,
        parse_mode=None,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
            InlineKeyboardButton("📊 Full Stats", callback_data="bot_stats")
        ]])
    )

@error_handler_decorator
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "⚙️ Settings\n\nApni preferences customize karo:",
        parse_mode=None,
        reply_markup=KeyboardBuilder.settings_menu(user.id)
    )

@error_handler_decorator
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
🌟 *SINGH JI AI ULTRA* 🌟

Version: 8.3 Fixed
Created: 2024
Platform: Railway

*Tech Stack:*
- Python + FastAPI
- Groq AI (Llama 3.1)
- Telegram Bot API
- gTTS Voice Engine
- Supabase (Coming Soon)

*New in v8.3:*
✅ Conversation Flow (Button -> Reply works!)
✅ Multi-Language Support
✅ Payment Webhook Ready
✅ Bachpan Child Safety Module
✅ Kisaan Doctor (Photo Diagnosis)
✅ Sarkari Yojana Check
✅ Scheme Swarm Integration

*Capabilities:*
- 40+ Active Modules
- Voice Recognition
- Text-to-Speech
- Memory System
- Rate Limiting
- Analytics

*Mission:*
Har Indian tak AI ki shakti pahunchana!
Kisaan, vyapari, student - sab ke liye!

*Developer:* JITENDRA SINGH
Contact: @SinghJiAI

*Singh Ji AI - Desh ka AI, Desh ke liye!* 🇮🇳
    """
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Website", url="https://singhji.ai"),
         InlineKeyboardButton("📢 Channel", url="https://t.me/SinghJiAI")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])
    await update.message.reply_text(
        about_text,
        parse_mode=None,
        reply_markup=keyboard
    )

# ═══════════════════════════════════════════════════════
# 🛡️ BACHPAN COMMAND — Child Safety
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def bachpan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    analytics.track_message(user.id, "command")
    bachpan_text = """🛡️ *BACHPAN — बच्चों की सुरक्षा* 🛡️

🇮🇳 *सरकारी हेल्पलाइन (100% REAL):*

📞 *1098* — चाइल्डलाइन (24x7, FREE)
📞 *100* — पुलिस (24x7, FREE)
📞 *181* — महिला हेल्पलाइन
📞 *108* — एम्बुलेंस
📞 *1930* — साइबर क्राइम
📞 *1800-572-1929* — NCPCR

🟢 *अच्छा स्पर्श:*
• सुरक्षित, खुशी, आराम
• माँ-बाप का प्यार
• डॉक्टर की जाँच

🔴 *बुरा स्पर्श:*
• असहज, डर, गुप्त
• अंडरवियर के अंदर
• अकेले में कोई छूए

🛡️ *स्वर्णिम मंत्र:*
"मेरा शरीर मेरा है"
"मैं मदद मांग सकता हूँ"

⚡ *Singh Ji AI Ultra v8.3*"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Helplines", callback_data="bachpan_helplines"),
         InlineKeyboardButton("🟢 Good Touch", callback_data="bachpan_good")],
        [InlineKeyboardButton("🔴 Bad Touch", callback_data="bachpan_bad"),
         InlineKeyboardButton("🚨 Emergency", callback_data="bachpan_emergency")],
        [InlineKeyboardButton("📝 Report", callback_data="bachpan_report"),
         InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])
    await update.message.reply_text(bachpan_text, parse_mode=None, reply_markup=keyboard)

# ═══════════════════════════════════════════════════════
# 🌾 KISAAN DOCTOR — Photo Handler
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    analytics.track_message(user.id, "photo")
    processing_msg = await update.message.reply_text("📸 Photo check kar raha hoon...")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_url = file.file_path
        response = requests.post(
            f"{config.API_BASE_URL}/modules/kisaan_doctor/diagnose",
            json={"photo_url": photo_url},
            timeout=30
        )
        result = response.json()
        if result.get("error"):
            await processing_msg.edit_text(f"❌ Error: {result['error'][:200]}")
            return
        if result.get("healthy"):
            await processing_msg.edit_text("✅ Paudha swasth hai! Koi bimari nahi mili.")
        else:
            text = f"🦠 Bimari: {result.get('disease_name', 'Unknown')}\n"
            text += f"Confidence: {result.get('confidence', 0)}%\n\n"
            if result.get("treatment_chemical"):
                text += f"💊 Chemical: {', '.join(result['treatment_chemical'][:3])}\n"
            if result.get("treatment_biological"):
                text += f"🌿 Biological: {', '.join(result['treatment_biological'][:3])}\n"
            await processing_msg.edit_text(text)
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await processing_msg.edit_text("❌ Photo process nahi ho payi! Dobara try karo.")

# ═══════════════════════════════════════════════════════
# 🏛️ SARKARI YOJANA — Command
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def yojana_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    analytics.track_message(update.effective_user.id, "command")
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: /yojana <age> <income> <occupation>\nExample: /yojana 45 150000 farmer",
            parse_mode=None
        )
        return
    try:
        age, income, occupation = int(args[0]), int(args[1]), args[2]
        response = requests.post(
            f"{config.API_BASE_URL}/modules/sarkari_yojana/check-eligibility",
            json={"age": age, "income": income, "occupation": occupation},
            timeout=15
        )
        result = response.json()
        if result.get("eligible_count", 0) == 0:
            await safe_reply_text(update.message, "❌ Filhaal koi scheme match nahi hui.")
            return
        text = f"🏛️ {result['eligible_count']} schemes mile!\n\n"
        for s in result["schemes"]:
            text += f"✅ {s['name']}\nAmount: Rs {s['amount']} ({s['frequency']})\nNext step: {s['next_step']}\n\n"
        await safe_reply_text(update.message, text[:4000], parse_mode=None)
    except ValueError:
        await update.message.reply_text("❌ Age aur income number mein bhejo.\nExample: /yojana 45 150000 farmer")
    except Exception as e:
        logger.error(f"Yojana command error: {e}")
        await safe_reply_text(update.message, "❌ Error aa gaya, dobara try karo.")

# ═══════════════════════════════════════════════════════
# 🏛️ SCHEME SWARM COMMANDS
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def scheme_profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start 6-step scheme profile wizard"""
    user = update.effective_user
    analytics.track_message(user.id, "command")
    analytics.track_module_usage("scheme_swarm")
    conversation_mgr.set_state(user.id, ConversationState.SCHEME_AGE, {"step": "age", "profile": {}})
    await update.message.reply_text(
        "🏛️ *Scheme Profile Wizard* — Step 1/6\n\n"
        "Apni *umr* batao (in years):\n"
        "Example: 35\n\n"
        "❌ Cancel karne ke liye /start dabao",
        parse_mode=None,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])
    )

@error_handler_decorator
async def schemes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show matched schemes based on profile"""
    user = update.effective_user
    analytics.track_message(user.id, "command")
    analytics.track_module_usage("scheme_swarm")
    mem = user_memory.get(user.id)
    profile = mem.get("metadata", {}).get("scheme_profile", {})
    if not profile:
        await update.message.reply_text(
            "🏛️ Pehle apna profile banayein!\n\n"
            "/scheme_profile se 6-step wizard start karo!",
            parse_mode=None,
            reply_markup=KeyboardBuilder.schemes_menu_keyboard()
        )
        return
    matched = match_schemes(
        profile.get("age", 30),
        profile.get("income", 0),
        profile.get("state", ""),
        profile.get("occupation", ""),
        profile.get("caste", ""),
        profile.get("family_size", 4)
    )
    if not matched:
        await update.message.reply_text(
            "❌ Filhaal koi scheme match nahi hui!\n"
            "Profile update karo: /scheme_profile",
            parse_mode=None
        )
        return
    conversation_mgr.set_state(user.id, ConversationState.NONE, {"matched_schemes": matched})
    text = f"🏛️ *{len(matched)} Schemes Mile!*\n\n"
    text += "Top matches:\n\n"
    for i, s in enumerate(matched[:5], 1):
        text += f"{i}. *{s['name']}* — {s['match_score']}% match\n"
        text += f"   💰 Rs {s['amount']} ({s['frequency']})\n"
        text += f"   📋 {s['category']}\n\n"
    await update.message.reply_text(
        text,
        parse_mode=None,
        reply_markup=KeyboardBuilder.scheme_list_keyboard(matched, 0)
    )

@error_handler_decorator
async def scheme_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track scheme application status"""
    args = context.args
    user = update.effective_user
    analytics.track_message(user.id, "command")
    if not args:
        await update.message.reply_text(
            "Usage: /scheme_status <scheme_id>\n\n"
            "Example: /scheme_status pmkisan\n\n"
            "Scheme ID ke liye /schemes se list dekho!",
            parse_mode=None
        )
        return
    scheme_id = args[0].lower()
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        await update.message.reply_text(
            f"❌ Scheme '{scheme_id}' nahi mili!\n"
            "Sahi ID ke liye /schemes dekho.",
            parse_mode=None
        )
        return
    status_text = f"""
📊 *Application Status*

Scheme: *{scheme['name']}*
ID: `{scheme_id}`
Category: {scheme['category']}

📝 Status: *Under Review* ⏳
📅 Applied: Not yet applied
🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d')}

*Next Steps:*
1. Documents collect karo
2. Official website pe apply karo
3. Application number save karo

*Documents Required:*
{chr(10).join(['• ' + d for d in scheme['documents']])}

🌐 [Official Website](https://{scheme['website']})
    """
    await safe_reply_text(
        update.message,
        status_text,
        parse_mode=None,
        reply_markup=KeyboardBuilder.scheme_detail_keyboard(scheme_id)
    )

# ═══════════════════════════════════════════════════════
# VOICE MESSAGE HANDLER
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    analytics.track_message(user.id, "voice")
    processing_msg = await update.message.reply_text(
        "🎤 Voice sun raha hoon...",
        parse_mode=None
    )
    try:
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        transcript = ""
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                files={"file": ("voice.ogg", io.BytesIO(voice_bytes), "audio/ogg")},
                data={"model": "whisper-large-v3", "language": "hi"},
                timeout=30
            )
            if resp.status_code == 200:
                transcript = resp.json().get("text", "")
                logger.info(f"Voice transcribed: {transcript[:50]}...")
            else:
                logger.error(f"Groq Whisper error: {resp.status_code} - {resp.text[:100]}")
                transcript = "Voice samajh nahi aaya!"
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            transcript = "Voice process nahi ho paya!"
        if not transcript or transcript == "Voice samajh nahi aaya!":
            await processing_msg.edit_text(
                "❌ Voice samajh nahi aaya!\n\nText mein bolo ya dobara bhejo!"
            )
            return
        ai_response = await ai_brain.get_response(
            transcript,
            user.id,
            user.first_name
        )
        await processing_msg.delete()
        voice_reply = await tts_engine.text_to_speech(ai_response["text"], user.id)
        if voice_reply:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_reply),
                caption=f"🎙️ {transcript[:50]}... → {ai_response['text'][:50]}..."
            )
        else:
            # ⚠️ ai_response['text'] AI मॉडल का dynamic output है — इसमें
            # markdown special chars (* _ ` [) unmatched आ सकते हैं और
            # ParseMode.MARKDOWN के साथ पूरा मैसेज crash कर सकता है।
            # safe_reply_text इसे handle करेगा — असफल होने पर plain टेक्स्ट भेजेगा
            await safe_reply_text(
                update.message,
                f"🎙️ *Aapne kaha:* {transcript}\n\n*Singh Ji:* {ai_response['text']}",
                parse_mode=None
            )
        user_memory.set(user.id, f"Voice: {transcript[:50]}... | AI: {ai_response['text'][:50]}...",
                       metadata={"type": "voice_chat"})
    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        await processing_msg.edit_text(
            f"❌ Voice process nahi ho paya!\n\nText se try karo!"
        )

# ═══════════════════════════════════════════════════════
# TEXT CHAT HANDLER
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def text_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text
    chat_type = update.effective_chat.type
    analytics.track_message(user.id, "text")
    if len(user_text) > 1000:
        await update.message.reply_text(
            "📝 Message thoda lamba hai! 1000 characters se kam mein bolo!\nYa voice message bhejo",
            reply_to_message_id=update.message.message_id
        )
        return
    conv_state = conversation_mgr.get_state(user.id)

    # WEATHER FLOW
    if conv_state["state"] == ConversationState.WEATHER_CITY:
        city = user_text.strip()
        await fetch_and_send_weather(update, city)
        conversation_mgr.clear_state(user.id)
        return
    # MANDI FLOW
    elif conv_state["state"] == ConversationState.MANDI_STATE:
        state = user_text.strip()
        await fetch_and_send_mandi(update, state)
        conversation_mgr.clear_state(user.id)
        return
    # TAX FLOW
    elif conv_state["state"] == ConversationState.TAX_INCOME:
        try:
            income = float(user_text.replace(",", "").strip())
            await calculate_and_send_tax(update, income)
        except ValueError:
            await update.message.reply_text(
                "❌ Galat number! Sirf digits bhejo (jaise: 500000)",
                parse_mode=None
            )
        conversation_mgr.clear_state(user.id)
        return
    # GOLD FLOW
    elif conv_state["state"] == ConversationState.GOLD_CITY:
        city = user_text.strip()
        await fetch_and_send_gold(update, city)
        conversation_mgr.clear_state(user.id)
        return
    # FUEL FLOW
    elif conv_state["state"] == ConversationState.FUEL_CITY:
        city = user_text.strip()
        await fetch_and_send_fuel(update, city)
        conversation_mgr.clear_state(user.id)
        return
    # CURRENCY FLOW
    elif conv_state["state"] == ConversationState.CURRENCY_PAIR:
        await update.message.reply_text(
            f"💰 Currency rate for {user_text} fetch kar raha hoon...",
            parse_mode=None
        )
        conversation_mgr.clear_state(user.id)
        return
    # SEARCH FLOW
    elif conv_state["state"] == ConversationState.SEARCH_QUERY:
        query = user_text.strip()
        await update.message.reply_text(
            f"🔍 {query} ke liye search kar raha hoon...",
            parse_mode=None
        )
        conversation_mgr.clear_state(user.id)
        return

    # 🏛️ SCHEME SWARM PROFILE BUILDER FLOW
    elif conv_state["state"] == ConversationState.SCHEME_AGE:
        try:
            age = int(user_text.strip())
            conversation_mgr.update_data(user.id, "age", age)
            conversation_mgr.set_state(user.id, ConversationState.SCHEME_INCOME, {"step": "income", "profile": {"age": age}})
            await update.message.reply_text(
                "🏛️ *Scheme Profile Wizard* — Step 2/6\n\n"
                "Apni *saalana income* batao (in Rs):\n"
                "Example: 150000\n\n"
                "❌ Cancel: /start",
                parse_mode=None
            )
        except ValueError:
            await update.message.reply_text("❌ Sirf number bhejo! Example: 35")
        return
    elif conv_state["state"] == ConversationState.SCHEME_INCOME:
        try:
            income = int(user_text.replace(",", "").strip())
            profile = conversation_mgr.data.get(user.id, {}).get("profile", {})
            profile["income"] = income
            conversation_mgr.set_state(user.id, ConversationState.SCHEME_STATE, {"step": "state", "profile": profile})
            await update.message.reply_text(
                "🏛️ *Scheme Profile Wizard* — Step 3/6\n\n"
                "Apna *state* batao:\n"
                "Example: Uttar Pradesh, Bihar, Maharashtra\n\n"
                "❌ Cancel: /start",
                parse_mode=None
            )
        except ValueError:
            await update.message.reply_text("❌ Sirf number bhejo! Example: 150000")
        return
    elif conv_state["state"] == ConversationState.SCHEME_STATE:
        state = user_text.strip()
        profile = conversation_mgr.data.get(user.id, {}).get("profile", {})
        profile["state"] = state
        conversation_mgr.set_state(user.id, ConversationState.SCHEME_OCCUPATION, {"step": "occupation", "profile": profile})
        await update.message.reply_text(
            "🏛️ *Scheme Profile Wizard* — Step 4/6\n\n"
            "Apni *occupation* batao:\n"
            "Options: farmer, student, business, self-employed, unemployed, employed\n\n"
            "❌ Cancel: /start",
            parse_mode=None
        )
        return
    elif conv_state["state"] == ConversationState.SCHEME_OCCUPATION:
        occupation = user_text.strip().lower()
        profile = conversation_mgr.data.get(user.id, {}).get("profile", {})
        profile["occupation"] = occupation
        conversation_mgr.set_state(user.id, ConversationState.SCHEME_CASTE, {"step": "caste", "profile": profile})
        await update.message.reply_text(
            "🏛️ *Scheme Profile Wizard* — Step 5/6\n\n"
            "Apni *caste category* batao:\n"
            "Options: general, obc, sc, st, all\n\n"
            "❌ Cancel: /start",
            parse_mode=None
        )
        return
    elif conv_state["state"] == ConversationState.SCHEME_CASTE:
        caste = user_text.strip().lower()
        profile = conversation_mgr.data.get(user.id, {}).get("profile", {})
        profile["caste"] = caste
        conversation_mgr.set_state(user.id, ConversationState.SCHEME_FAMILY, {"step": "family", "profile": profile})
        await update.message.reply_text(
            "🏛️ *Scheme Profile Wizard* — Step 6/6\n\n"
            "*Family size* batao (total members):\n"
            "Example: 5\n\n"
            "❌ Cancel: /start",
            parse_mode=None
        )
        return
    elif conv_state["state"] == ConversationState.SCHEME_FAMILY:
        try:
            family_size = int(user_text.strip())
            profile = conversation_mgr.data.get(user.id, {}).get("profile", {})
            profile["family_size"] = family_size
            # Save profile to memory
            user_memory.set(user.id, f"Scheme Profile: {profile}", metadata={
                "scheme_profile": profile,
                "updated_at": datetime.now().isoformat()
            })
            conversation_mgr.clear_state(user.id)
            # Show matched schemes
            matched = match_schemes(
                profile.get("age", 30),
                profile.get("income", 0),
                profile.get("state", ""),
                profile.get("occupation", ""),
                profile.get("caste", ""),
                profile.get("family_size", 4)
            )
            if matched:
                text = f"✅ *Profile Complete!* {len(matched)} schemes mile!\n\n"
                for i, s in enumerate(matched[:5], 1):
                    text += f"{i}. *{s['name']}* — {s['match_score']}% match\n"
                    text += f"   💰 Rs {s['amount']} ({s['frequency']})\n"
                    text += f"   📋 {s['category']}\n\n"
                await safe_reply_text(
                    update.message,
                    text,
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.scheme_list_keyboard(matched, 0)
                )
            else:
                await update.message.reply_text(
                    "✅ *Profile Complete!*\n\n"
                    "❌ Filhaal koi scheme match nahi hui.\n"
                    "Profile update karo: /scheme_profile",
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.schemes_menu_keyboard()
                )
        except ValueError:
            await update.message.reply_text("❌ Sirf number bhejo! Example: 5")
        return

    if chat_type in ['group', 'supergroup']:
        await handle_group_message(update, context)
        return
    await update.message.chat.send_action(action="typing")
    ai_response = await ai_brain.get_response(
        user_text,
        user.id,
        user.first_name,
        chat_type
    )
    # ⚠️ ai_response['text'] Groq से आया dynamic output है — इसमें
    # markdown-breaking characters आ सकते हैं (जैसे कोड, बुलेट में * आदि)।
    # safe_reply_text इस्तेमाल करके entity-parse crash से बचाया गया है।
    sent_message = await safe_reply_text(
        update.message,
        f"{ai_response['text']}",
        parse_mode=None,
        reply_to_message_id=update.message.message_id
    )
    if not ai_response.get('error') and tts_engine.get_language(user.id) != "off":
        voice_bytes = await tts_engine.text_to_speech(ai_response['text'], user.id)
        if voice_bytes:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_bytes),
                caption="🔊 Bolke sunao!",
                reply_to_message_id=sent_message.message_id
            )

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    bot_username = context.bot.username
    should_respond = False
    user_text = message.text
    if f"@{bot_username}" in message.text:
        user_text = message.text.replace(f"@{bot_username}", "").strip()
        should_respond = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        should_respond = True
    if should_respond and user_text.strip():
        await update.message.chat.send_action(action="typing")
        ai_response = await ai_brain.get_response(
            user_text,
            user.id,
            user.first_name,
            "group"
        )
        # ⚠️ यहाँ भी AI का dynamic output है — safe_reply_text से भेजो
        await safe_reply_text(
            message,
            f"{ai_response['text']}",
            parse_mode=None
        )

# ═══════════════════════════════════════════════════════
# CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    data = query.data
    try:
        # MAIN MENU
        if data == "main_menu":
            conversation_mgr.clear_state(user.id)
            await query.edit_message_text(
                "🏠 Main Menu\n\nKya karna chahte ho?",
                parse_mode=None,
                reply_markup=KeyboardBuilder.main_menu()
            )
        # HELP / ABOUT
        elif data == "help":
            await help_command(update, context)
        elif data == "about":
            await about_command(update, context)
        # MODULES
        elif data == "list_modules":
            await query.edit_message_text(
                f"📦 {len(ACTIVE_MODULES)} Active Modules\n\nModule select karo:",
                parse_mode=None,
                reply_markup=KeyboardBuilder.modules_keyboard(1)
            )
        elif data.startswith("modules_page_"):
            page = int(data.split("_")[-1])
            await query.edit_message_text(
                f"📦 Modules (Page {page})\n\nModule select karo:",
                parse_mode=None,
                reply_markup=KeyboardBuilder.modules_keyboard(page)
            )
        elif data.startswith("use_module_"):
            module = data.replace("use_module_", "")
            await query.edit_message_text(
                f"🔧 {module.upper()} Module\n\nUsage: /use {module} <query>\n\nExample: /use {module} test",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📦 Modules List", callback_data="list_modules")]])
            )
        # QUICK ACTIONS
        elif data == "quick_weather":
            conversation_mgr.set_state(user.id, ConversationState.WEATHER_CITY)
            await query.edit_message_text(
                "🌤️ Weather\n\nKaunsa city?\nExample: Delhi, Mumbai, Patna",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])
            )
        elif data == "quick_news":
            try:
                response = requests.get(f"{config.API_BASE_URL}/modules/news/", timeout=10)
                news_data = response.json()
                # ⚠️ news_data JSON में headline/description जैसे dynamic
                # टेक्स्ट होते हैं जिनमें * _ ` जैसे characters unmatched आ
                # सकते हैं — safe_edit_text से crash नहीं होगा
                await safe_edit_text(
                    query,
                    f"📰 Latest News\n\n{json.dumps(news_data, indent=2)[:3000]}",
                    parse_mode=None
                )
            except:
                await query.edit_message_text(
                    "❌ News fetch nahi ho payi!\n/use news se try karo",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
                )
        elif data == "quick_gold":
            conversation_mgr.set_state(user.id, ConversationState.GOLD_CITY)
            await query.edit_message_text(
                "🥇 Gold Rate\n\nKaunsa city? (ya 'India' for national rate)\nExample: Delhi, Mumbai",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])
            )
        # SETTINGS
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ Settings\n\nPreferences customize karo:",
                parse_mode=None,
                reply_markup=KeyboardBuilder.settings_menu(user.id)
            )
        elif data == "toggle_voice":
            current_lang = tts_engine.get_language(user.id)
            if current_lang == "off":
                tts_engine.set_language(user.id, "hi")
                status = "ON (Hindi)"
            else:
                tts_engine.set_language(user.id, "off")
                status = "OFF"
            await query.edit_message_text(
                f"🔊 Voice: {status}",
                parse_mode=None,
                reply_markup=KeyboardBuilder.settings_menu(user.id)
            )
        elif data == "change_language":
            await query.edit_message_text(
                "🌐 Select Language\n\nApni bhasha chuno:\n\nCurrent: " + lang_mgr.get_lang_name(user.id),
                parse_mode=None,
                reply_markup=lang_mgr.get_all_langs_keyboard()
            )
        elif data.startswith("set_lang_"):
            lang_code = data.replace("set_lang_", "")
            if lang_mgr.set_lang(user.id, lang_code):
                tts_engine.set_language(user.id, lang_code)
                await query.edit_message_text(
                    f"✅ Language set to: {lang_mgr.get_lang_name(user.id)}\n\nAb main isi bhasha mein jawab dunga!",
                    parse_mode=None,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Back to Settings", callback_data="settings")]])
                )
            else:
                await query.edit_message_text(
                    "❌ Invalid language!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Try Again", callback_data="change_language")]])
                )
        elif data == "clear_memory":
            user_memory.delete(user.id)
            await query.edit_message_text(
                "🧹 Memory clear kar di!",
                reply_markup=KeyboardBuilder.settings_menu(user.id)
            )
        elif data == "memory_stats":
            memory_data = user_memory.get(user.id)
            stats = user_memory.stats
            await query.edit_message_text(
                f"🧠 Memory Stats\n\nYour Memory: {memory_data['content'][:100]}...\nLast Updated: {memory_data['timestamp']}\n\nTotal Users: {stats['total_users']}\nMax Size: {stats['max_size']}\nTTL: {stats['ttl_hours']} hours",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="settings")]])
            )
        elif data == "voice_mode":
            await query.edit_message_text(
                "🎤 Voice Mode\n\nVoice message bhejo aur main sunuga!\nFir bolke jawab dunga!\n\nTry karo:\n- Mausam kaisa hai?\n- News sunao\n- Gold rate batao\n- Kya haal hai?\n\nYa text se bhi puch sakte ho!",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
            )
        # STATS
        elif data == "bot_stats" or data == "refresh_status":
            summary = analytics.get_summary()
            await query.edit_message_text(
                f"📊 Bot Statistics\n\nTotal Messages: {summary['total_messages']}\nUnique Users: {summary['unique_users']}\nActive 24h: {summary['active_users_24h']}\nVoice: {summary['voice_messages']}\nText: {summary['text_messages']}\nCommands: {summary['commands']}\nErrors: {summary['errors']}\nUptime: {summary['uptime']}\n\nTop 5 Modules:\n" + "\n".join([f"- {m}: {c}" for m, c in summary['top_modules'][:5]]),
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="bot_stats"), InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]])
            )
        # AI MODE
        elif data == "mode_ai":
            current_mode = ai_brain.current_modes.get(user.id, "default")
            modes = ["default", "technical", "farming", "business"]
            current_idx = modes.index(current_mode) if current_mode in modes else 0
            next_idx = (current_idx + 1) % len(modes)
            next_mode = modes[next_idx]
            ai_brain.current_modes[user.id] = next_mode
            await query.edit_message_text(
                f"🤖 AI Mode: {next_mode.upper()}\n\nAb main {next_mode} mode mein jawab dunga!",
                parse_mode=None,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Change Mode", callback_data="mode_ai"), InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]])
            )

        # 🏛️ SCHEME SWARM CALLBACKS
        elif data == "schemes_menu":
            await query.edit_message_text(
                "🏛️ *Scheme Swarm* — Sarkari Yojana Finder\n\n"
                "Apne profile ke hisaab se schemes paayein!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.schemes_menu_keyboard()
            )
        elif data == "scheme_profile_start":
            conversation_mgr.set_state(user.id, ConversationState.SCHEME_AGE, {"step": "age", "profile": {}})
            await query.edit_message_text(
                "🏛️ *Scheme Profile Wizard* — Step 1/6\n\n"
                "Apni *umr* batao (in years):\n"
                "Example: 35\n\n"
                "❌ Cancel: /start",
                parse_mode=None
            )
        elif data == "scheme_search":
            mem = user_memory.get(user.id)
            profile = mem.get("metadata", {}).get("scheme_profile", {})
            if not profile:
                await query.edit_message_text(
                    "🏛️ Pehle apna profile banayein!\n\n"
                    "📋 Profile Banayein button dabao!",
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.schemes_menu_keyboard()
                )
                return
            matched = match_schemes(
                profile.get("age", 30),
                profile.get("income", 0),
                profile.get("state", ""),
                profile.get("occupation", ""),
                profile.get("caste", ""),
                profile.get("family_size", 4)
            )
            if matched:
                conversation_mgr.set_state(user.id, ConversationState.NONE, {"matched_schemes": matched})
                text = f"🏛️ *{len(matched)} Schemes Mile!*\n\n"
                text += "Top matches:\n\n"
                for i, s in enumerate(matched[:5], 1):
                    text += f"{i}. *{s['name']}* — {s['match_score']}% match\n"
                    text += f"   💰 Rs {s['amount']} ({s['frequency']})\n"
                    text += f"   📋 {s['category']}\n\n"
                await safe_edit_text(
                    query,
                    text,
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.scheme_list_keyboard(matched, 0)
                )
            else:
                await query.edit_message_text(
                    "❌ Filhaal koi scheme match nahi hui!\n"
                    "Profile update karo!",
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.schemes_menu_keyboard()
                )
        elif data == "scheme_status":
            await query.edit_message_text(
                "📊 *Scheme Status*\n\n"
                "Scheme ID batao:\n"
                "Example: pmkisan, ayushman, pmay\n\n"
                "Ya /scheme_status <id> command use karo!",
                parse_mode=None,
                reply_markup=KeyboardBuilder.schemes_menu_keyboard()
            )
        elif data.startswith("scheme_page_"):
            page = int(data.split("_")[-1])
            conv_data = conversation_mgr.data.get(user.id, {})
            matched = conv_data.get("matched_schemes", [])
            if matched:
                start = page * 5
                end = start + 5
                text = f"🏛️ *Schemes (Page {page+1})*\n\n"
                for i, s in enumerate(matched[start:end], start+1):
                    text += f"{i}. *{s['name']}* — {s['match_score']}% match\n"
                    text += f"   💰 Rs {s['amount']} ({s['frequency']})\n"
                    text += f"   📋 {s['category']}\n\n"
                await safe_edit_text(
                    query,
                    text,
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.scheme_list_keyboard(matched, page)
                )
        elif data.startswith("scheme_detail_"):
            scheme_id = data.replace("scheme_detail_", "")
            scheme = get_scheme_by_id(scheme_id)
            if scheme:
                text = f"🏛️ *{scheme['name']}*\n\n"
                text += f"📋 Category: {scheme['category']}\n"
                text += f"💰 Amount: Rs {scheme['amount']} ({scheme['frequency']})\n"
                text += f"📝 {scheme['description']}\n\n"
                text += f"📅 Age: {scheme['min_age']}-{scheme['max_age']} years\n"
                text += f"💵 Max Income: Rs {scheme['max_income']}\n"
                text += f"👔 Occupations: {', '.join(scheme['occupations'])}\n"
                text += f"🏷️ Caste: {', '.join(scheme['castes'])}\n\n"
                text += f"🌐 Website: {scheme['website']}"
                await safe_edit_text(
                    query,
                    text,
                    parse_mode=None,
                    reply_markup=KeyboardBuilder.scheme_detail_keyboard(scheme_id)
                )
        elif data.startswith("scheme_docs_"):
            scheme_id = data.replace("scheme_docs_", "")
            scheme = get_scheme_by_id(scheme_id)
            if scheme:
                docs_text = f"📄 *Documents for {scheme['name']}*\n\n"
                for i, doc in enumerate(scheme['documents'], 1):
                    docs_text += f"{i}. {doc}\n"
                docs_text += f"\n🌐 [Apply Online](https://{scheme['website']})"
                await safe_edit_text(
                    query,
                    docs_text,
                    parse_mode=None,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"scheme_detail_{scheme_id}")]])
                )

        # 🛡️ BACHPAN CALLBACKS
        elif data == "bachpan_helplines":
            text = """📞 *HELPLINES* 📞

1098 — चाइल्डलाइन
100 — पुलिस  
181 — महिला हेल्पलाइन
108 — एम्बुलेंस
1930 — साइबर क्राइम
1800-572-1929 — NCPCR
9152987821 — आत्महत्या रोकथाम

सभी FREE और 24x7!"""
            await query.edit_message_text(text, parse_mode=None, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bachpan_back")]]))
        elif data == "bachpan_good":
            text = """🟢 *GOOD TOUCH* 🟢

✅ सुरक्षित महसूस कराता है
✅ खुशी देता है
✅ आरामदायक है

Examples:
• माँ-बाप का गले लगाना
• डॉक्टर की जाँच (मम्मी-पापा के सामने)
• दोस्त का हाई-फाइव
• नानी-दादी का आशीर्वाद

Rule: Good Touch = Safe + Happy + Comfortable"""
            await query.edit_message_text(text, parse_mode=None, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bachpan_back")]]))
        elif data == "bachpan_bad":
            text = """🔴 *BAD TOUCH* 🔴

❌ असहज महसूस कराता है
❌ डरावना लगता है
❌ गुप्त रखने को कहे

Examples:
• अंडरवियर/बनियान के अंदर कोई छूए
• जबरदस्ती गले लगाना
• अकेले में छूने की कोशिश
• अश्लील वीडियो दिखाना

Rule: Bad Touch = Uncomfortable + Scared + Secret

🚨 *तुरंत मम्मी-पापा को बताओ!*"""
            await query.edit_message_text(text, parse_mode=None, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bachpan_back")]]))
        elif data == "bachpan_emergency":
            text = """🚨 *EMERGENCY STEPS* 🚨

1️⃣ चिल्लाओ — जोर से 'बचाओ' बोलो
2️⃣ भागो — सुरक्षित जगह की ओर
3️⃣ बताओ — मम्मी-पापा, टीचर, पुलिस
4️⃣ 1098 पर कॉल करो
5️⃣ कभी डरो मत — तुम्हारी कोई गलती नहीं!

📞 *1098 — Childline*
📞 *100 — Police*

*तुम बहादुर हो!* 💪"""
            await query.edit_message_text(text, parse_mode=None, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bachpan_back")]]))
        elif data == "bachpan_report":
            text = """📝 *REPORT INCIDENT* 📝

शिकायत दर्ज करनें के लिए:

1️⃣ 1098 पर कॉल करें
2️⃣ नजदीकी पुलिस स्टेशन जाएं
3️⃣ NCPCR e-Box: ncpcr.gov.in
4️⃣ POCSO Act के तहत कार्रवाई

*24 घंटे में कार्रवाई होगी*

*तुम्हारी आवाज़ सुनी जाएगी!* 🛡️"""
            await query.edit_message_text(text, parse_mode=None, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="bachpan_back")]]))
        elif data == "bachpan_back":
            bachpan_text = """🛡️ *BACHPAN — बच्चों की सुरक्षा* 🛡️

🇮🇳 *सरकारी हेल्पलाइन (100% REAL):*

📞 *1098* — चाइल्डलाइन (24x7, FREE)
📞 *100* — पुलिस (24x7, FREE)
📞 *181* — महिला हेल्पलाइन
📞 *108* — एम्बुलेंस
📞 *1930* — साइबर क्राइम
📞 *1800-572-1929* — NCPCR

🟢 *अच्छा स्पर्श:*
• सुरक्षित, खुशी, आराम
• माँ-बाप का प्यार
• डॉक्टर की जाँच

🔴 *बुरा स्पर्श:*
• असहज, डर, गुप्त
• अंडरवियर के अंदर
• अकेले में कोई छूए

🛡️ *स्वर्णिम मंत्र:*
"मेरा शरीर मेरा है"
"मैं मदद मांग सकता हूँ"

⚡ *Singh Ji AI Ultra v8.3*"""
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Helplines", callback_data="bachpan_helplines"), InlineKeyboardButton("🟢 Good Touch", callback_data="bachpan_good")],
                [InlineKeyboardButton("🔴 Bad Touch", callback_data="bachpan_bad"), InlineKeyboardButton("🚨 Emergency", callback_data="bachpan_emergency")],
                [InlineKeyboardButton("📝 Report", callback_data="bachpan_report"), InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
            ])
            await query.edit_message_text(bachpan_text, parse_mode=None, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            await query.edit_message_text(
                "❌ Kuch error ho gaya! /start karo fir se.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Restart", callback_data="main_menu")]])
            )
        except:
            pass

# ═══════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    analytics.track_error()
    if update and isinstance(update, Update) and update.effective_message:
        try:
            await safe_reply_text(
                update.effective_message,
                "❌ Oops! Kuch unexpected error ho gaya! Team ko bata diya hai. Jaldi fix karenge! Tab tak /start karo.",
                parse_mode=None
            )
        except:
            pass

# ═══════════════════════════════════════════════════════
# APPLICATION SETUP
# ═══════════════════════════════════════════════════════

application = None

async def setup_application() -> Application:
    global application
    if application is not None:
        return application
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("help", "Help & guide"),
        BotCommand("modules", "All modules"),
        BotCommand("use", "Use a module"),
        BotCommand("remember", "Remember something"),
        BotCommand("recall", "Recall memory"),
        BotCommand("status", "System status"),
        BotCommand("settings", "Settings"),
        BotCommand("about", "About Singh Ji AI"),
        BotCommand("stats", "Usage statistics"),
        BotCommand("bachpan", "Child safety helplines"),
        BotCommand("yojana", "Sarkari yojana check"),
        BotCommand("scheme_profile", "Scheme profile wizard"),
        BotCommand("schemes", "Auto-matched schemes"),
        BotCommand("scheme_status", "Track application status"),
        BotCommand("agentic", "Agentic AI auto content"),
        BotCommand("video", "Generate video"),
        BotCommand("post", "Post to social media"),
    ]
    await application.bot.set_my_commands(commands)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("modules", modules_command))
    application.add_handler(CommandHandler("use", use_module_command))
    application.add_handler(CommandHandler("remember", remember_command))
    application.add_handler(CommandHandler("recall", recall_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("bachpan", bachpan_command))
    application.add_handler(CommandHandler("yojana", yojana_command))
    # SCHEME SWARM COMMANDS
    application.add_handler(CommandHandler("scheme_profile", scheme_profile_command))
    application.add_handler(CommandHandler("schemes", schemes_command))
    application.add_handler(CommandHandler("scheme_status", scheme_status_command))
    if AGENTIC_AVAILABLE:
        application.add_handler(CommandHandler("agentic", agentic_command))
        application.add_handler(CommandHandler("video", video_command))
        application.add_handler(CommandHandler("post", post_command))
        logger.info("Agentic-A handlers registered!")
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_chat_handler))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    logger.info("Bot application setup complete!")
    return application

# ═══════════════════════════════════════════════════════
# FASTAPI ROUTER
# ═══════════════════════════════════════════════════════

router = APIRouter()

# ═══════════════════════════════════════════════════════
# WEBHOOK ROUTES
# ═══════════════════════════════════════════════════════

def verify_webhook_secret(request: Request) -> bool:
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "NOT_PRESENT")
    expected = config.WEBHOOK_SECRET
    logger.info(f"Webhook verify | Got: '{secret_token}' | Expected: '{expected}' | ENV: {config.ENVIRONMENT}")
    logger.info("Webhook allowed (temporarily bypassing secret check)")
    return True

@router.post("/webhook")
async def telegram_webhook(request: Request):
    global application
    if not verify_webhook_secret(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        if application is None:
            application = await setup_application()
            await application.initialize()
            logger.info("Bot initialized via webhook!")
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)[:200]}

@router.get("/")
async def root():
    return {
        "status": "running",
        "bot": "Singh Ji AI v8.3",
        "timestamp": datetime.now().isoformat(),
        "modules": len(ACTIVE_MODULES)
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot": "Singh Ji AI v8.3",
        "timestamp": datetime.now().isoformat(),
        "modules": len(ACTIVE_MODULES),
        "token_set": bool(config.TELEGRAM_BOT_TOKEN),
        "groq_set": bool(config.GROQ_API_KEY),
        "voice_enabled": True,
        "ai_enabled": True,
        "memory_users": user_memory.size,
        "total_messages": analytics.stats["total_messages"],
        "unique_users": len(analytics.stats["unique_users"]),
        "environment": config.ENVIRONMENT,
        "webhook_url": config.WEBHOOK_URL
    }

@router.get("/setup-webhook")
async def setup_webhook():
    try:
        app = await setup_application()
        await app.initialize()
        await app.bot.set_webhook(
            url=config.WEBHOOK_URL,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        webhook_info = await app.bot.get_webhook_info()
        return {
            "status": "success",
            "webhook_url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections
        }
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delete-webhook")
async def delete_webhook():
    try:
        if application:
            await application.bot.delete_webhook(drop_pending_updates=True)
        return {"status": "success", "message": "Webhook deleted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/stats")
async def get_stats():
    summary = analytics.get_summary()
    memory_stats = user_memory.stats
    return {
        "analytics": summary,
        "memory": memory_stats,
        "rate_limiter": {
            "active_users": len(rate_limiter.requests),
            "max_requests": rate_limiter.max_requests,
            "window_seconds": rate_limiter.window_seconds
        },
        "config": {
            "environment": config.ENVIRONMENT,
            "modules_count": len(ACTIVE_MODULES),
            "voice_enabled": True,
            "ai_model": "llama-3.1-8b-instant"
        }
    }

@router.post("/broadcast")
async def broadcast_message(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        admin_key = data.get("admin_key", "")
        if admin_key != config.ADMIN_KEY:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not message:
            raise HTTPException(status_code=400, detail="Message required")
        if not application:
            raise HTTPException(status_code=503, detail="Bot not running")
        users = list(user_memory.memory.keys())
        sent_count = 0
        failed_count = 0
        for user_id in users[:100]:
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 Broadcast from Singh Ji AI\n\n{message}",
                    parse_mode=None
                )
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
                failed_count += 1
        return {"status": "success", "sent": sent_count, "failed": failed_count, "total_users": len(users)}
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════
# PAYMENT WEBHOOK
# ═══════════════════════════════════════════════════════

@router.post("/payment/verify")
async def verify_payment(request: Request):
    try:
        data = await request.json()
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return {"status": "failed", "error": "Missing required fields"}
        secret = config.RAZORPAY_KEY_SECRET
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, razorpay_signature):
            logger.warning(f"Invalid payment signature for order: {razorpay_order_id}")
            return {"status": "failed", "error": "Invalid signature"}
        logger.info(f"Payment verified! Order: {razorpay_order_id}, Payment: {razorpay_payment_id}")
        return {
            "status": "success",
            "order_id": razorpay_order_id,
            "payment_id": razorpay_payment_id,
            "message": "Payment verified successfully!"
        }
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/payment/webhook")
async def razorpay_webhook(request: Request):
    try:
        webhook_signature = request.headers.get("X-Razorpay-Signature", "")
        body = await request.body()
        secret = config.RAZORPAY_KEY_SECRET
        expected_signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, webhook_signature):
            logger.warning("Invalid Razorpay webhook signature!")
            raise HTTPException(status_code=400, detail="Invalid signature")
        data = json.loads(body)
        event = data.get("event")
        payload = data.get("payload", {})
        logger.info(f"Razorpay webhook received: {event}")
        if event == "payment.captured":
            payment = payload.get("payment", {}).get("entity", {})
            order_id = payment.get("order_id")
            payment_id = payment.get("id")
            amount = payment.get("amount", 0) / 100
            logger.info(f"Payment captured! Order: {order_id}, Amount: Rs.{amount}")
            return {"status": "success", "event": event}
        elif event == "payment.failed":
            payment = payload.get("payment", {}).get("entity", {})
            order_id = payment.get("order_id")
            logger.warning(f"Payment failed! Order: {order_id}")
            return {"status": "success", "event": event}
        return {"status": "success", "event": event, "message": "Event received"}
    except Exception as e:
        logger.error(f"Razorpay webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment/status/{order_id}")
async def payment_status(order_id: str):
    return {
        "order_id": order_id,
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# AGENTIC-A COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def agentic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AGENTIC_AVAILABLE:
        await update.message.reply_text("Agentic-A abhi available nahi hai!")
        return
    args = context.args
    if not args:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Kisaan", callback_data="agentic_kisaan"),
             InlineKeyboardButton("Student", callback_data="agentic_student")],
            [InlineKeyboardButton("Business", callback_data="agentic_business"),
             InlineKeyboardButton("Health", callback_data="agentic_health")],
            [InlineKeyboardButton("Spiritual", callback_data="agentic_spiritual"),
             InlineKeyboardButton("Video", callback_data="agentic_video")],
        ])
        await update.message.reply_text(
            "AGENTIC-A SYSTEM\n\nMain apne aap content banaunga!\n\n"
            "Usage: /agentic <goal>\n"
            "Example: /agentic kisaano ke liye content banao",
            parse_mode=None,
            reply_markup=keyboard
        )
        return
    prompt = " ".join(args)
    msg = await update.message.reply_text(f"Working: {prompt[:50]}...")
    try:
        result = await agentic.run(prompt)
        content = result.get('content', 'No content generated')
        # ⚠️ agentic result AI-generated है — safe_edit_text इस्तेमाल करो
        await safe_edit_text(
            msg,
            f"Done!\n\nGoal: {result.get('goal', 'N/A')[:50]}\n"
            f"Category: {result.get('category', 'general').title()}\n\n"
            f"{content[:800]}",
            parse_mode=None
        )
        for action in result.get('actions', []):
            if action['type'] == 'video' and action['result'].get('success'):
                await update.message.reply_text(
                    f"Video bhi ban gaya!\nSource: {action['result'].get('source')}"
                )
    except Exception as e:
        logger.error(f"Agentic error: {e}")
        await safe_edit_text_msg(msg, f"Error: {str(e)[:100]}")

@error_handler_decorator
@rate_limit_check
async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AGENTIC_AVAILABLE:
        await update.message.reply_text("Video system nahi hai!")
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Video Generator\n\nUsage: /video <prompt>\nExample: /video kisaan ki zindagi",
            parse_mode=None
        )
        return
    prompt = " ".join(args)
    msg = await update.message.reply_text(f"Generating: {prompt[:50]}...")
    try:
        result = await agentic.generate_video(prompt)
        if result.get("success"):
            await msg.edit_text(
                f"Video Generated!\n\nSource: {result.get('source')}\n"
                f"Prompt: {prompt[:100]}"
            )
            if result.get("url"):
                await update.message.reply_video(video=result["url"])
        else:
            await msg.edit_text(
                f"Failed\n\nError: {result.get('error')}\n\nVideo gen modules check karo!"
            )
    except Exception as e:
        logger.error(f"Video error: {e}")
        await safe_edit_text_msg(msg, f"Error: {str(e)[:100]}")

@error_handler_decorator
@rate_limit_check
async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AGENTIC_AVAILABLE:
        await update.message.reply_text("Auto-poster nahi hai!")
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Social Media Poster\n\nUsage: /post <message>\nExample: /post Kisaano ke liye nayi scheme!",
            parse_mode=None
        )
        return
    message = " ".join(args)
    msg = await update.message.reply_text(f"Posting: {message[:50]}...")
    try:
        result = await agentic.post_to_all(message)
        successful = result.get("successful", 0)
        total = result.get("total", 0)
        platform_status = ""
        for plat, res in result.get('results', {}).items():
            icon = "OK" if res.get('success') else "FAIL"
            platform_status += f"{icon} {plat.title()}\n"
        await msg.edit_text(
            f"Posted!\n\n{successful}/{total} platforms\n\n{platform_status}"
        )
    except Exception as e:
        logger.error(f"Post error: {e}")
        await safe_edit_text_msg(msg, f"Error: {str(e)[:100]}")

# ═══════════════════════════════════════════════════════
# STARTUP/SHUTDOWN EVENTS
# ═══════════════════════════════════════════════════════

@router.on_event("startup")
async def startup_event():
    if config.ENVIRONMENT == "development":
        try:
            app = await setup_application()
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("Bot started in polling mode (development)!")
        except Exception as e:
            logger.error(f"Startup error: {e}")
    else:
        logger.info("Production mode - webhook only, no polling!")

@router.on_event("shutdown")
async def shutdown_event():
    global application
    if application:
        try:
            await application.stop()
            await application.shutdown()
            logger.info("Bot shutdown complete!")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
