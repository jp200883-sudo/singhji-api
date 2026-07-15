"""
🦁 SINGH JI AI — TELEGRAM BOT HANDLER (Production Ready - FIXED v8.3)
modules/telegram_bot/handler.py
Version: v8.3 — Voice-to-Voice + Shabd Ka King
"""

from fastapi import APIRouter, Request, HTTPException
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters, ConversationHandler
)
from telegram.constants import ParseMode
import requests
import json
import os
import io
import time
import logging
import hmac
import hashlib
import asyncio
import random
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import Optional, Dict, Any
from functools import wraps

router = APIRouter()

# ═══════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('singhji_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://singhji-api-production-85ca.up.railway.app")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://singhji-api-production-85ca.up.railway.app/modules/telegram_bot/webhook")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "singh_ji_secret_token_2024")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    ADMIN_KEY = os.getenv("ADMIN_KEY", "singhji_admin_2024")
    MAX_MESSAGE_LENGTH = 4000
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))
    MEMORY_TTL = int(os.getenv("MEMORY_TTL", "86400"))

config = Config()

# ═══════════════════════════════════════════════════════
# SHABD KA KING — WORD GAME
# ═══════════════════════════════════════════════════════

class ShabdKaKing:
    def __init__(self):
        self.active_games = {}
        self.scores = {}
        self.words = {
            "easy": ["kisaan", "mandi", "baarish", "fasal", "kheti", "ganna", "gehu", "chawal", "doodh", "sabzi"],
            "medium": ["krishi", "pradhanmantri", "yojana", "sarkari", "bijli", "sichai", "kisan", "fasal", "anaj", "bazaar"],
            "hard": ["antyodaya", "pragati", "saururja", "jaivik", "kendriya", "prakritik", "sashakt", "samriddhi", "unnati", "vikas"]
        }

    def start_game(self, user_id: int, level: str = "easy") -> str:
        word = random.choice(self.words.get(level, self.words["easy"]))
        self.active_games[user_id] = {
            "word": word,
            "guessed": ["_"] * len(word),
            "attempts": 0,
            "max_attempts": 6,
            "level": level,
            "wrong_guesses": []
        }
        return self._format_game(user_id)

    def guess_letter(self, user_id: int, letter: str) -> str:
        if user_id not in self.active_games:
            return "❌ Pehle /shabd start karo!"

        game = self.active_games[user_id]
        word = game["word"]

        if letter in word:
            for i, char in enumerate(word):
                if char == letter:
                    game["guessed"][i] = letter
        else:
            game["wrong_guesses"].append(letter)
            game["attempts"] += 1

        if "_" not in game["guessed"]:
            points = {"easy": 10, "medium": 20, "hard": 30}.get(game["level"], 10)
            self.scores[user_id] = self.scores.get(user_id, 0) + points
            result = f"🎉 JEET GAYE!\n\nWord: {word}\n⭐ +{points} points!\n🏆 Total: {self.scores[user_id]}"
            del self.active_games[user_id]
            return result

        if game["attempts"] >= game["max_attempts"]:
            result = f"😢 HAAR GAYE!\n\nWord tha: {word}\n💔 Try again: /shabd"
            del self.active_games[user_id]
            return result

        return self._format_game(user_id)

    def _format_game(self, user_id: int) -> str:
        game = self.active_games[user_id]
        word_display = " ".join(game["guessed"])
        wrong = ", ".join(game["wrong_guesses"]) if game["wrong_guesses"] else "None"
        attempts_left = game["max_attempts"] - game["attempts"]

        return f"""🦁 SHABD KA KING

Word: {word_display}

❌ Wrong: {wrong}
❤️ Left: {attempts_left}

Letter bhejo!
Level: {game['level'].upper()}

🏆 /shabd score"""

    def get_score(self, user_id: int) -> str:
        score = self.scores.get(user_id, 0)
        top = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_text = "\n".join([f"{i+1}. User {uid}: {s} pts" for i, (uid, s) in enumerate(top)])
        return f"⭐ Your Score: {score}\n\n🏆 Leaderboard:\n{top_text}"

shabd_game = ShabdKaKing()

# ═══════════════════════════════════════════════════════
# CONVERSATION STATE MANAGER
# ═══════════════════════════════════════════════════════

class ConversationState:
    IDLE = "idle"
    WEATHER_CITY = "weather_city"
    MANDI_STATE = "mandi_state"
    TAX_INCOME = "tax_income"
    GOLD_CITY = "gold_city"
    FUEL_CITY = "fuel_city"
    CURRENCY_PAIR = "currency_pair"
    SEARCH_QUERY = "search_query"
    SHABD_GUESS = "shabd_guess"

class ConversationManager:
    def __init__(self):
        self.states = {}
        self.ttl = 300

    def set_state(self, user_id: int, state: str, data: Dict = None):
        self.states[user_id] = {
            "state": state,
            "data": data or {},
            "timestamp": time.time()
        }

    def get_state(self, user_id: int) -> Dict:
        if user_id in self.states:
            if time.time() - self.states[user_id]["timestamp"] > self.ttl:
                self.clear_state(user_id)
                return {"state": ConversationState.IDLE, "data": {}}
            return self.states[user_id]
        return {"state": ConversationState.IDLE, "data": {}}

    def clear_state(self, user_id: int):
        if user_id in self.states:
            del self.states[user_id]

conversation_mgr = ConversationManager()

# ═══════════════════════════════════════════════════════
# LANGUAGE MANAGER
# ═══════════════════════════════════════════════════════

class LanguageManager:
    def __init__(self):
        self.user_langs = {}
        self.lang_names = {
            "hi": "Hindi (Hinglish)",
            "en": "English",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "bn": "Bengali",
            "gu": "Gujarati",
            "pa": "Punjabi"
        }

    def set_lang(self, user_id: int, lang: str):
        if lang in self.lang_names:
            self.user_langs[user_id] = lang
            return True
        return False

    def get_lang(self, user_id: int) -> str:
        return self.user_langs.get(user_id, "hi")

    def get_system_prompt(self, user_id: int) -> str:
        lang = self.get_lang(user_id)
        prompts = {
            "hi": """Tu Singh Ji AI hai - India ka sabse powerful AI assistant!
Personality:
- Friendly, helpful, aur thoda funny
- HINGLISH mein baat kar
- Emojis use kar
- Agriculture, farming, rural India ki knowledge hai
Rules:
- Kabhi bhi harmful advice mat dena
- Paiso ki advice responsibly dena
- Privacy respect karna""",
            "en": """You are Singh Ji AI - India\'s most powerful AI assistant!
Personality: Friendly, helpful, slightly funny
- Speak in clear, simple English
- Use emojis for better expression
- Knowledge about agriculture, farming, rural India"""
        }
        return prompts.get(lang, prompts["hi"])

lang_mgr = LanguageManager()

# ═══════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════

class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

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
            return {"content": self.memory[user_id], "timestamp": self.timestamps.get(user_id), "metadata": self.metadata.get(user_id, {})}
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
            "ttl_hours": self.ttl / 3600
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

analytics = BotAnalytics()

# ═══════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════

def rate_limit_check(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not await rate_limiter.is_allowed(user.id):
            await update.message.reply_text("⏳ Thoda slow karo! 1 minute mein try karo!")
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
            try:
                if update.message:
                    await update.message.reply_text("❌ Kuch problem ho gayi! /start karo fir se.")
                elif update.callback_query:
                    await update.callback_query.message.reply_text("❌ Error! /start karo.")
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

        system_prompt = lang_mgr.get_system_prompt(user_id)
        intent = self._detect_intent(user_text)

        messages = [
            {"role": "system", "content": f"{system_prompt}\n\nUser: {user_name}\nIntent: {intent}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
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
            user_memory.set(user_id, f"[{datetime.now().strftime('%H:%M')}] {user_text[:100]}", metadata={"last_intent": intent})
            analytics.track_module_usage("ai_chat")
            return {"text": answer, "error": False, "intent": intent}
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {"text": "Thoda busy hoon! 1 minute mein try karo!", "error": True}

    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        intents = {
            "weather": ["mausam", "weather", "baarish", "garmi", "thand"],
            "news": ["news", "khabar", "samachar"],
            "gold": ["sona", "gold", "silver", "chandi"],
            "fuel": ["petrol", "diesel", "fuel", "tel"],
            "mandi": ["mandi", "bhav", "rate", "fasal"],
            "farming": ["kheti", "kisaan", "beej", "khad"],
            "greeting": ["hello", "hi", "namaste", "ram ram"],
            "help": ["help", "madad", "sahayata"],
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
        self.languages = {"hi": "Hindi", "en": "English", "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi"}
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
    "Govt Schemes": "govt", "Singh Ji TV": "singhji_tv", "Voice": "voice",
    "UPI": "upi", "Banking": "banking", "WhatsApp": "whatsapp",
    "Language Hub": "language_hub", "Horoscope": "horoscope", "Bachpan": "bachpan",
    "Aavishkar": "aavishkar", "Meta Agent": "meta_agent", "Supreme Agent": "supreme_agent",
    "Smart Swarm": "smart_swarm", "Currents API": "currents_api", "NewsData": "newsdata",
    "News Scheduler": "news_scheduler", "OAuth": "oauth_connector",
    "Supabase Memory": "supabase_memory", "Telegram Bot": "telegram_bot",
    "Language": "language", "Mini-Program": "miniprogram", "Mini Auth": "mini_auth",
    "Claw 7": "claw_7", "Voice CMD": "voice_cmd", "Voice TTS": "voice_tts",
    "Init": "init", "Singh Ji AI Ultra": "singhji_ultra",
    "Shabd Ka King": "shabd_ka_king",
}

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
             InlineKeyboardButton("🪙 Gold Rate", callback_data="quick_gold")],
            [InlineKeyboardButton("📦 All Modules", callback_data="list_modules"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("🎙️ Voice Mode", callback_data="voice_mode"),
             InlineKeyboardButton("🎮 Shabd Ka King", callback_data="shabd_game")],
            [InlineKeyboardButton("📊 Stats", callback_data="bot_stats"),
             InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu(user_id: int):
        voice_status = "ON" if tts_engine.get_language(user_id) != "off" else "OFF"
        current_lang = lang_mgr.lang_names.get(lang_mgr.get_lang(user_id), "Hindi")
        keyboard = [
            [InlineKeyboardButton(f"🔊 Voice: {voice_status}", callback_data="toggle_voice")],
            [InlineKeyboardButton(f"🌐 Language: {current_lang}", callback_data="change_language")],
            [InlineKeyboardButton("🧹 Clear Memory", callback_data="clear_memory"),
             InlineKeyboardButton("📈 Memory Stats", callback_data="memory_stats")],
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
    def shabd_menu():
        keyboard = [
            [InlineKeyboardButton("🟢 Easy", callback_data="shabd_easy"),
             InlineKeyboardButton("🟡 Medium", callback_data="shabd_medium")],
            [InlineKeyboardButton("🔴 Hard", callback_data="shabd_hard"),
             InlineKeyboardButton("🏆 Score", callback_data="shabd_score")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    analytics.track_message(user.id, "command")
    user_memory.set(user.id, f"Name: {user.first_name}, Started: {datetime.now().isoformat()}",
                   metadata={"chat_type": update.effective_chat.type})
    welcome = f"""🦁 SINGH JI AI ULTRA v8.3

Welcome {user.first_name}!

India ka sabse powerful AI assistant!

✅ Voice-to-Voice Replies
✅ {len(ACTIVE_MODULES)} Active Modules
✅ Shabd Ka King Game
✅ Multi-Language Support

Quick Start:
🎙️ Voice bhejo — AI awaaz se jawab dega!
🎮 /shabd — Word game khelo!
🤖 Text bhejo — AI jawab dega

Singh Ji AI - Har Indian ka AI saathi!"""
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.main_menu())

@error_handler_decorator
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analytics.track_message(update.effective_user.id, "command")
    help_text = """🦁 SINGH JI AI HELP

🎙️ Voice Features:
- Voice message bhejo
- AI awaaz se jawab dega!

🎮 Shabd Ka King:
/shabd — Game start
/shabd score — Leaderboard

Commands:
/start — Welcome
/help — Yeh help
/modules — All modules
/use module — Direct use
/remember text — Memory
/recall — Memory check
/status — System status
/settings — Preferences
/about — About bot

Singh Ji AI - Always learning!"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.main_menu())

@error_handler_decorator
async def modules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analytics.track_message(update.effective_user.id, "command")
    await update.message.reply_text(f"📦 {len(ACTIVE_MODULES)} Active Modules", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.modules_keyboard(1))

@error_handler_decorator
@rate_limit_check
async def use_module_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user
    analytics.track_message(user.id, "command")
    if not args:
        await update.message.reply_text("Usage: /use module query\nExample: /use weather Delhi", parse_mode=ParseMode.MARKDOWN)
        return
    module = args[0].lower()
    query = " ".join(args[1:]) if len(args) > 1 else ""
    valid_modules = list(ACTIVE_MODULES.values())
    if module not in valid_modules:
        similar = [m for m in valid_modules if module in m][:5]
        suggestion = "\n".join([f"- {m}" for m in similar])
        await update.message.reply_text(f"❌ Module nahi mila!\n\nSimilar:\n{suggestion}", parse_mode=ParseMode.MARKDOWN)
        return
    analytics.track_module_usage(module)
    processing = await update.message.reply_text(f"⏳ {module.upper()} use kar raha hoon...")
    try:
        response = requests.get(f"{config.API_BASE_URL}/modules/{module}/", params={"q": query}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            formatted = json.dumps(data, indent=2, ensure_ascii=False)[:3500]
            await processing.edit_text(f"✅ {module.upper()} Result:\n\n```json\n{formatted}\n```", parse_mode=ParseMode.MARKDOWN)
        else:
            await processing.edit_text(f"❌ Error! Status: {response.status_code}")
    except Exception as e:
        await processing.edit_text(f"❌ Error: {str(e)[:100]}")

@error_handler_decorator
async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /remember <text>\nExample: /remember Mera naam Ram hai", parse_mode=ParseMode.MARKDOWN)
        return
    user_memory.set(user.id, text, metadata={"updated_at": datetime.now().isoformat()})
    await update.message.reply_text(f"✅ Yaad rakh liya!\n\n📝 {text}\n\n/recall se puch sakte ho!", parse_mode=ParseMode.MARKDOWN)

@error_handler_decorator
async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    memory_data = user_memory.get(user.id)
    content = memory_data.get("content", "Kuch yaad nahi hai!")
    timestamp = memory_data.get("timestamp")
    time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "Unknown"
    await update.message.reply_text(f"🧠 Memory:\n\n{content}\n\n🕐 Last Updated: {time_str}", parse_mode=ParseMode.MARKDOWN)

@error_handler_decorator
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{config.API_BASE_URL}/health", timeout=10)
        api_status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
    except:
        api_status = "🔴 Offline"
    memory_stats = user_memory.stats
    analytics_summary = analytics.get_summary()
    status_text = f"""📊 SYSTEM STATUS

🟢 Bot: Running
{api_status} API
🎙️ Voice: Enabled
🧠 Memory: Active

📈 Stats:
Messages: {analytics_summary['total_messages']}
Users: {analytics_summary['unique_users']}
Uptime: {analytics_summary['uptime']}

🎮 Shabd Ka King Ready!
🎙️ Voice-to-Voice Ready!"""
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"), InlineKeyboardButton("📊 Full Stats", callback_data="bot_stats")]]))

@error_handler_decorator
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("⚙️ Settings", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.settings_menu(user.id))

@error_handler_decorator
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """🦁 SINGH JI AI ULTRA

Version: 8.3
Created: 2024
Platform: Railway

🆕 v8.3 Features:
✅ Voice-to-Voice Replies
✅ Shabd Ka King Game
✅ Multi-Language

Mission:
Har Indian tak AI ki shakti!

Developer: JITENDRA SINGH
Singh Ji AI - Desh ka AI!"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Website", url="https://singhji.ai"),
         InlineKeyboardButton("📢 Channel", url="https://t.me/SinghJiAI")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

# ═══════════════════════════════════════════════════════
# SHABD KA KING COMMAND
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def shabd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if not args or args[0] == "start":
        level = args[1] if len(args) > 1 else "easy"
        if level not in ["easy", "medium", "hard"]:
            level = "easy"
        text = shabd_game.start_game(user.id, level)
        conversation_mgr.set_state(user.id, ConversationState.SHABD_GUESS)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    elif args[0] == "score":
        text = shabd_game.get_score(user.id)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            "🎮 SHABD KA KING\n\nUsage:\n/shabd — Easy start\n/shabd medium — Medium\n/shabd hard — Hard\n/shabd score — Leaderboard",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=KeyboardBuilder.shabd_menu()
        )

# ═══════════════════════════════════════════════════════
# VOICE MESSAGE HANDLER — FIXED: Voice-to-Voice!
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    analytics.track_message(user.id, "voice")

    processing_msg = await update.message.reply_text("🎤 Voice samajh raha hoon...")

    try:
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        # Step 1: Transcribe via API
        transcript = ""
        try:
            import base64
            audio_b64 = base64.b64encode(voice_bytes).decode("utf-8")
            resp = requests.post(
                f"{config.API_BASE_URL}/api/whisper/transcribe",
                json={"audio_base64": audio_b64},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                transcript = data.get("transcript", "")
            else:
                transcript = "Voice samajh nahi aaya, text mein bolo!"
        except Exception as e:
            logger.error(f"Whisper API error: {e}")
            transcript = "Voice process nahi ho paya!"

        if not transcript:
            await processing_msg.edit_text("❌ Voice samajh nahi aaya! Text mein bolo.")
            return

        # Step 2: AI response
        ai_response = await ai_brain.get_response(transcript, user.id, user.first_name)

        await processing_msg.delete()

        # Step 3: VOICE REPLY (NOT TEXT!)
        voice_reply = await tts_engine.text_to_speech(ai_response["text"], user.id)

        if voice_reply:
            # 🔥 DIRECT VOICE REPLY — NO TEXT!
            await update.message.reply_voice(
                voice=io.BytesIO(voice_reply),
                caption=f"🎙️ {ai_response['text'][:100]}..." if len(ai_response["text"]) > 100 else f"🎙️ {ai_response['text']}"
            )
        else:
            # Fallback to text only if TTS fails
            await update.message.reply_text(
                f"🎙️ {ai_response['text']}",
                parse_mode=ParseMode.MARKDOWN
            )

        # Save memory
        user_memory.set(user.id, f"Voice: {transcript[:50]}... | AI: {ai_response['text'][:50]}...", 
                       metadata={"type": "voice_chat"})

    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        await processing_msg.edit_text("❌ Voice process nahi ho paya! Text se try karo.")

# ═══════════════════════════════════════════════════════
# TEXT CHAT HANDLER — FIXED: Shabd Ka King + Conversations
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def text_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text
    chat_type = update.effective_chat.type

    analytics.track_message(user.id, "text")

    if len(user_text) > 1000:
        await update.message.reply_text("⏳ Message lamba hai! 1000 chars se kam mein bolo!")
        return

    # Check conversation state
    conv_state = conversation_mgr.get_state(user.id)

    # Shabd Ka King — single letter guess
    if conv_state["state"] == ConversationState.SHABD_GUESS and len(user_text) == 1 and user_text.isalpha():
        result = shabd_game.guess_letter(user.id, user_text.lower())
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        if "JEET GAYE" in result or "HAAR GAYE" in result:
            conversation_mgr.clear_state(user.id)
        return

    # Weather city
    elif conv_state["state"] == ConversationState.WEATHER_CITY:
        await update.message.reply_text(f"🌤️ Weather for {user_text.strip()}...")
        conversation_mgr.clear_state(user.id)
        return

    # Mandi state
    elif conv_state["state"] == ConversationState.MANDI_STATE:
        await update.message.reply_text(f"📊 Mandi rates for {user_text.strip()}...")
        conversation_mgr.clear_state(user.id)
        return

    # Tax income
    elif conv_state["state"] == ConversationState.TAX_INCOME:
        try:
            income = float(user_text.replace(",", "").strip())
            await update.message.reply_text(f"💰 Tax calc for Rs.{income:,.0f}...")
        except ValueError:
            await update.message.reply_text("❌ Galat number! Sirf digits bhejo.")
        conversation_mgr.clear_state(user.id)
        return

    # Group chat handling
    if chat_type in ["group", "supergroup"]:
        await handle_group_message(update, context)
        return

    # Normal AI chat
    await update.message.chat.send_action(action="typing")
    ai_response = await ai_brain.get_response(user_text, user.id, user.first_name, chat_type)

    sent_message = await update.message.reply_text(
        ai_response["text"],
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=update.message.message_id
    )

    # Optional TTS for text messages too (if voice enabled)
    if tts_engine.get_language(user.id) != "off":
        voice_bytes = await tts_engine.text_to_speech(ai_response["text"], user.id)
        if voice_bytes:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_bytes),
                caption="🎙️ Bolke sunao!",
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
        ai_response = await ai_brain.get_response(user_text, user.id, user.first_name, "group")
        await message.reply_text(ai_response["text"], parse_mode=ParseMode.MARKDOWN)

# ═══════════════════════════════════════════════════════
# CALLBACK QUERY HANDLER — FIXED: Shabd Ka King buttons
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    data = query.data

    try:
        if data == "main_menu":
            conversation_mgr.clear_state(user.id)
            await query.edit_message_text("🔥 Main Menu\n\nKya karna chahte ho?", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.main_menu())

        elif data == "help":
            await help_command(update, context)

        elif data == "about":
            await about_command(update, context)

        elif data == "list_modules":
            await query.edit_message_text(f"📦 {len(ACTIVE_MODULES)} Modules", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.modules_keyboard(1))

        elif data.startswith("modules_page_"):
            page = int(data.split("_")[-1])
            await query.edit_message_text(f"📦 Page {page}", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.modules_keyboard(page))

        elif data.startswith("use_module_"):
            module = data.replace("use_module_", "")
            await query.edit_message_text(f"📦 {module.upper()}\n\nUse: /use {module} <query>", parse_mode=ParseMode.MARKDOWN)

        # Quick actions
        elif data == "quick_weather":
            conversation_mgr.set_state(user.id, ConversationState.WEATHER_CITY)
            await query.edit_message_text("🌤️ Weather\n\nCity batao!\nExample: Delhi, Mumbai", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]]))

        elif data == "quick_news":
            await query.edit_message_text("📰 News fetch kar raha hoon...")

        elif data == "quick_gold":
            await query.edit_message_text("🪙 Gold rate fetch kar raha hoon...")

        # Settings
        elif data == "settings":
            await query.edit_message_text("⚙️ Settings", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.settings_menu(user.id))

        elif data == "toggle_voice":
            current = tts_engine.get_language(user.id)
            if current == "off":
                tts_engine.set_language(user.id, "hi")
                status = "ON 🔊"
            else:
                tts_engine.set_language(user.id, "off")
                status = "OFF 🔇"
            await query.edit_message_text(f"🔊 Voice: {status}", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.settings_menu(user.id))

        elif data == "change_language":
            keyboard = []
            row = []
            for code, name in lang_mgr.lang_names.items():
                row.append(InlineKeyboardButton(name, callback_data=f"set_lang_{code}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="settings")])
            await query.edit_message_text("🌐 Language select karo:", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

        elif data.startswith("set_lang_"):
            lang_code = data.replace("set_lang_", "")
            if lang_mgr.set_lang(user.id, lang_code):
                tts_engine.set_language(user.id, lang_code)
                await query.edit_message_text(f"✅ Language: {lang_mgr.lang_names.get(lang_code, lang_code)}", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Settings", callback_data="settings")]]))

        elif data == "clear_memory":
            user_memory.delete(user.id)
            await query.edit_message_text("🧹 Memory clear kar di!", reply_markup=KeyboardBuilder.settings_menu(user.id))

        # Voice mode
        elif data == "voice_mode":
            await query.edit_message_text("🎙️ Voice Mode\n\nVoice message bhejo — AI awaaz se jawab dega!\n\nYa text se bhi puch sakte ho!", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))

        # Bot stats
        elif data in ["bot_stats", "refresh_status"]:
            summary = analytics.get_summary()
            await query.edit_message_text(
                f"📊 Stats\n\nMessages: {summary['total_messages']}\nUsers: {summary['unique_users']}\nVoice: {summary['voice_messages']}\nText: {summary['text_messages']}\nUptime: {summary['uptime']}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="bot_stats"), InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
            )

        # AI Mode
        elif data == "mode_ai":
            await query.edit_message_text("🤖 AI Mode\n\nAbhi default mode mein hoon!", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))

        # 🔥 SHABD KA KING BUTTONS
        elif data == "shabd_game":
            await query.edit_message_text("🎮 SHABD KA KING\n\nHindi word guessing game!", parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.shabd_menu())

        elif data == "shabd_easy":
            text = shabd_game.start_game(user.id, "easy")
            conversation_mgr.set_state(user.id, ConversationState.SHABD_GUESS)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))

        elif data == "shabd_medium":
            text = shabd_game.start_game(user.id, "medium")
            conversation_mgr.set_state(user.id, ConversationState.SHABD_GUESS)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))

        elif data == "shabd_hard":
            text = shabd_game.start_game(user.id, "hard")
            conversation_mgr.set_state(user.id, ConversationState.SHABD_GUESS)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))

        elif data == "shabd_score":
            text = shabd_game.get_score(user.id)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=KeyboardBuilder.shabd_menu())

    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            await query.edit_message_text("❌ Error! /start karo fir se.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Restart", callback_data="main_menu")]]))
        except:
            pass

# ═══════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    analytics.track_error()
    if update and isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("❌ Unexpected error! /start karo.")
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
        raise ValueError("TELEGRAM_BOT_TOKEN required")

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("help", "Help & guide"),
        BotCommand("modules", "All modules"),
        BotCommand("use", "Use module"),
        BotCommand("remember", "Save memory"),
        BotCommand("recall", "View memory"),
        BotCommand("status", "System status"),
        BotCommand("settings", "Preferences"),
        BotCommand("about", "About bot"),
        BotCommand("shabd", "Shabd Ka King game"),
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
    application.add_handler(CommandHandler("shabd", shabd_command))

    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_chat_handler))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot setup complete!")
    return application

# ═══════════════════════════════════════════════════════
# WEBHOOK HANDLERS
# ═══════════════════════════════════════════════════════

def verify_webhook_secret(request: Request) -> bool:
    if config.ENVIRONMENT == "development":
        return True
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    return secret_token and hmac.compare_digest(secret_token, config.WEBHOOK_SECRET)

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

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot": "Singh Ji AI v8.3",
        "timestamp": datetime.now().isoformat(),
        "modules": len(ACTIVE_MODULES),
        "token_set": bool(config.TELEGRAM_BOT_TOKEN),
        "voice_enabled": True,
        "shabd_ka_king": True,
        "environment": config.ENVIRONMENT
    }

@router.get("/setup-webhook")
async def setup_webhook():
    try:
        app = await setup_application()
        await app.initialize()
        await app.bot.set_webhook(
            url=config.WEBHOOK_URL,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        webhook_info = await app.bot.get_webhook_info()
        return {
            "status": "success",
            "webhook_url": webhook_info.url,
            "pending_updates": webhook_info.pending_update_count
        }
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delete-webhook")
async def delete_webhook():
    try:
        if application:
            await application.bot.delete_webhook(drop_pending_updates=True)
        return {"status": "success", "message": "Webhook deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/stats")
async def get_stats():
    return {
        "analytics": analytics.get_summary(),
        "memory": user_memory.stats,
        "config": {
            "environment": config.ENVIRONMENT,
            "modules_count": len(ACTIVE_MODULES),
            "voice_enabled": True,
            "shabd_ka_king": True
        }
    }

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
            return {"status": "failed", "error": "Missing fields"}
        secret = config.RAZORPAY_KEY_SECRET
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, razorpay_signature):
            return {"status": "failed", "error": "Invalid signature"}
        return {"status": "success", "order_id": razorpay_order_id, "payment_id": razorpay_payment_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════
# STARTUP/SHUTDOWN
# ═══════════════════════════════════════════════════════

@router.on_event("startup")
async def startup_event():
    if config.ENVIRONMENT == "development":
        try:
            app = await setup_application()
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("Polling mode started!")
        except Exception as e:
            logger.error(f"Startup error: {e}")
    else:
        logger.info("Production mode — webhook only!")

@router.on_event("shutdown")
async def shutdown_event():
    global application
    if application:
        try:
            await application.stop()
            await application.shutdown()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("handler:router", host="0.0.0.0", port=port, reload=config.ENVIRONMENT == "development")
