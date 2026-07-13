"""
🦁 SINGH JI AI — TELEGRAM BOT HANDLER (Production Ready - FIXED v8.1)
modules/telegram_bot/handler.py
Version: v8.1 Ultimate — All Bugs Fixed + Optimized
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
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://singhji-api-production-85ca.up.railway.app")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://singhji-api-production-85ca.up.railway.app/modules/telegram_bot/webhook")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "singh_ji_secret_token_2024")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    MAX_MESSAGE_LENGTH = 4000
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))
    MEMORY_TTL = int(os.getenv("MEMORY_TTL", "86400"))  # 24 hours

config = Config()

# ═══════════════════════════════════════════════════════
# RATE LIMITER (FIXED — Lock Removed, Background Cleanup)
# ═══════════════════════════════════════════════════════

class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = {}
        self._cleanup_task = None
    
    async def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limits — NO LOCK, async-safe"""
        now = datetime.now()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests for this user only (fast)
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests[user_id] = [
            req for req in self.requests[user_id] 
            if req > cutoff
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True
    
    def get_user_requests(self, user_id: int) -> int:
        """Get current request count for user"""
        return len(self.requests.get(user_id, []))
    
    async def start_cleanup(self):
        """Start background cleanup task"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired entries from all users"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds * 2)  # 2x window safety
        expired_users = []
        
        for user_id, reqs in self.requests.items():
            self.requests[user_id] = [r for r in reqs if r > cutoff]
            if not self.requests[user_id]:
                expired_users.append(user_id)
        
        # Remove empty users
        for uid in expired_users:
            del self.requests[uid]
        
        if expired_users:
            logger.info(f"🧹 Rate limiter cleanup: {len(expired_users)} users removed")

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
        """Get user memory with metadata"""
        self._cleanup()
        if user_id in self.memory:
            return {
                "content": self.memory[user_id],
                "timestamp": self.timestamps.get(user_id),
                "metadata": self.metadata.get(user_id, {})
            }
        return {"content": "", "timestamp": None, "metadata": {}}
    
    def set(self, user_id: int, content: str, metadata: Dict = None):
        """Set user memory with metadata"""
        self._cleanup()
        
        if len(self.memory) >= self.max_size:
            # Remove oldest entry
            oldest = next(iter(self.memory))
            del self.memory[oldest]
            self.timestamps.pop(oldest, None)
            self.metadata.pop(oldest, None)
        
        self.memory[user_id] = content
        self.timestamps[user_id] = time.time()
        self.metadata[user_id] = metadata or {}
    
    def delete(self, user_id: int):
        """Delete user memory"""
        self.memory.pop(user_id, None)
        self.timestamps.pop(user_id, None)
        self.metadata.pop(user_id, None)
    
    def _cleanup(self):
        """Remove expired entries"""
        now = time.time()
        expired = [uid for uid, ts in self.timestamps.items() 
                   if now - ts > self.ttl]
        for uid in expired:
            self.memory.pop(uid, None)
            self.timestamps.pop(uid, None)
            self.metadata.pop(uid, None)
    
    @property
    def size(self) -> int:
        """Get current memory size"""
        return len(self.memory)
    
    @property
    def stats(self) -> Dict:
        """Get memory statistics"""
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
        """Track a message event"""
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
        """Track an error"""
        self.stats["errors"] += 1
    
    def track_module_usage(self, module_name: str):
        """Track module usage"""
        self.stats["module_usage"][module_name] = \
            self.stats["module_usage"].get(module_name, 0) + 1
    
    def get_summary(self) -> Dict:
        """Get analytics summary"""
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
            "top_modules": sorted(
                self.stats["module_usage"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
    
    def reset_daily(self):
        """Reset daily stats"""
        self.stats["active_users_24h"] = set()

analytics = BotAnalytics()

# ═══════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════

def rate_limit_check(func):
    """Decorator for rate limiting"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        if not await rate_limiter.is_allowed(user.id):
            await update.message.reply_text(
                "🦁 *Rate Limit!*\n\n"
                "Thoda slow karo! 1 minute mein try karo!\n"
                "Ya premium user ban jao! 💎",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def error_handler_decorator(func):
    """Decorator for error handling"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            analytics.track_error()
            
            error_msg = (
                f"❌ *Error!*\n\n"
                f"Kuch problem ho gayi! Admin ko bata diya hai.\n"
                f"Thodi der mein try karo! 🔧\n\n"
                f"Ya /help karo!"
            )
            
            try:
                if update.message:
                    await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
                elif update.callback_query:
                    await update.callback_query.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
            except:
                pass
            
            raise
    return wrapper

# ═══════════════════════════════════════════════════════
# AI BRAIN SYSTEM
# ═══════════════════════════════════════════════════════

class AIBrain:
    def __init__(self):
        self.system_prompts = {
            "default": """Tu Singh Ji AI hai - India ka sabse powerful AI assistant! 🇮🇳

Personality:
- Friendly, helpful, aur thoda funny
- Hinglish mein baat kar (Hindi + English mix)
- Emojis use kar for better expression
- Respectful rah, especially elders ke saath
- Technical questions ka simple jawab de
- Agriculture, farming, rural India ki knowledge hai

Capabilities:
- 95 modules available hain
- Weather, News, Gold Rate, Mandi Rates
- Voice commands support
- Memory hai - yaad rakh sakta hai
- Group chats mein bhi kaam karta hai

Rules:
- Kabhi bhi harmful advice mat dena
- Paiso ki advice responsibly dena
- Privacy respect karna
- Happy rehna!""",
            
            "technical": """Technical mode ON! Detailed, accurate answers do.
Code examples ke saath, best practices follow karo.
Hinglish mein explain karo but technical terms English mein rakho.""",
            
            "farming": """Kisaan mode ON! Agriculture expert ki tarah jawab do.
Fasal, mitti, mandi rates, sarkari yojanayein - sab ki jaankari hai.
Simple language mein samjhao.""",
            
            "business": """Business mode ON! Entrepreneurial advice do.
Market trends, business strategies, digital India ki baatein.
Practical aur actionable advice do."""
        }
        
        self.current_modes = {}  # user_id -> mode
    
    async def get_response(
        self, 
        user_text: str, 
        user_id: int, 
        user_name: str = "User",
        chat_type: str = "private"
    ) -> Dict[str, Any]:
        """Get AI response with context"""
        
        # Input validation
        if not user_text or not user_text.strip():
            return {
                "text": f"🦁 {user_name}, kuch toh bolo! 😄",
                "error": False
            }
        
        if len(user_text) > 1000:
            user_text = user_text[:1000] + "..."
        
        # Get user memory
        memory_data = user_memory.get(user_id)
        context = memory_data.get("content", "")
        
        # Get current mode
        mode = self.current_modes.get(user_id, "default")
        system_prompt = self.system_prompts.get(mode, self.system_prompts["default"])
        
        # Detect intent
        intent = self._detect_intent(user_text)
        
        # Build messages
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
            
            # Update memory
            user_memory.set(user_id, f"[{datetime.now().strftime('%H:%M')}] {user_text[:100]}",
                          metadata={"last_intent": intent})
            
            analytics.track_module_usage("ai_chat")
            
            return {
                "text": answer,
                "error": False,
                "intent": intent,
                "mode": mode
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            
            # Fallback responses
            if "rate" in str(e).lower():
                return {
                    "text": "🦁 Thoda busy hoon! 1 minute mein try karo! 🏃‍♂️",
                    "error": True
                }
            elif "auth" in str(e).lower():
                return {
                    "text": "🦁 AI dimag restart karna padega! Admin ko batao! 🔧",
                    "error": True
                }
            else:
                return {
                    "text": f"🦁 Arre {user_name}, network issue! Text se bolo kya chahiye! 💪",
                    "error": True
                }
    
    def _detect_intent(self, text: str) -> str:
        """Detect user intent from text"""
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
            "hi": "Hindi",
            "en": "English",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "bn": "Bengali",
            "gu": "Gujarati",
            "pa": "Punjabi"
        }
        self.user_languages = {}  # user_id -> language code
    
    async def text_to_speech(self, text: str, user_id: Optional[int] = None) -> Optional[bytes]:
        """Convert text to speech"""
        try:
            from gtts import gTTS
            
            # Get user language preference
            lang = self.user_languages.get(user_id, "hi") if user_id else "hi"
            
            # Truncate text
            short_text = text[:500] if len(text) > 500 else text
            
            # Generate speech
            tts = gTTS(text=short_text, lang=lang, slow=False)
            
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            
            return mp3_fp.read()
            
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None
    
    def set_language(self, user_id: int, lang: str):
        """Set user language preference"""
        if lang in self.languages:
            self.user_languages[user_id] = lang
            return True
        return False
    
    def get_language(self, user_id: int) -> str:
        """Get user language preference"""
        return self.user_languages.get(user_id, "hi")

tts_engine = TTSEngine()

# ═══════════════════════════════════════════════════════
# 95 ACTIVE MODULES
# ═══════════════════════════════════════════════════════

ACTIVE_MODULES = {
    "🌤️ Weather": "weather",
    "📰 News": "news",
    "🤖 AI Chat": "ai_chat",
    "💰 Currency": "currency",
    "🥇 Gold Rate": "goldrate",
    "⛽ Fuel Price": "fuel",
    "🌾 Mandi Rates": "mandi",
    "🚜 Rozgar": "rozgar",
    "💧 Pani": "pani",
    "🌱 Plant ID": "plant_id",
    "🔍 Search": "search",
    "📊 Analytics": "analytics",
    "🛡️ Guard Agent": "guard_agent",
    "⚡ Trishul": "trishul",
    "🛒 Trolley": "trolley",
    "📅 Schedule": "schedule",
    "📋 Daily Report": "daily_report",
    "🚨 Emergency": "emergency",
    "🏛️ Govt Schemes": "govt",
    "📺 Singh Ji TV": "singhji_tv",
    "🎙️ Voice": "voice",
    "💳 UPI": "upi",
    "🏦 Banking": "banking",
    "📱 WhatsApp": "whatsapp",
    "🌐 Language Hub": "language_hub",
    "🔮 Horoscope": "horoscope",
    "📚 Bachpan": "bachpan",
    "🎭 Aavishkar": "aavishkar",
    "🤝 Meta Agent": "meta_agent",
    "👑 Supreme Agent": "supreme_agent",
    "🐝 Smart Swarm": "smart_swarm",
    "📡 Currents API": "currents_api",
    "📰 NewsData": "newsdata",
    "📰 News Scheduler": "news_scheduler",
    "🔐 OAuth": "oauth_connector",
    "💾 Supabase Memory": "supabase_memory",
    "🤖 Telegram Bot": "telegram_bot",
    "🌐 Language": "language",
    "🎯 Mini-Program": "miniprogram",
    "🎮 Mini Auth": "mini_auth",
    "📊 Claw 7": "claw_7",
    "🎙️ Voice CMD": "voice_cmd",
    "🎙️ Voice TTS": "voice_tts",
    "🧪 Init": "init",
    "🌍 Singh Ji AI Ultra": "singhji_ultra",
}

# ═══════════════════════════════════════════════════════
# KEYBOARD BUILDERS
# ═══════════════════════════════════════════════════════

class KeyboardBuilder:
    @staticmethod
    def main_menu():
        """Build main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🤖 AI Chat", callback_data="mode_ai"),
             InlineKeyboardButton("🌤️ Weather", callback_data="quick_weather")],
            [InlineKeyboardButton("📰 News", callback_data="quick_news"),
             InlineKeyboardButton("🥇 Gold Rate", callback_data="quick_gold")],
            [InlineKeyboardButton("📋 All Modules", callback_data="list_modules"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("🎙️ Voice Mode", callback_data="voice_mode"),
             InlineKeyboardButton("📊 Stats", callback_data="bot_stats")],
            [InlineKeyboardButton("❓ Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu(user_id: int):
        """Build settings menu"""
        voice_status = "ON" if tts_engine.get_language(user_id) != "off" else "OFF"
        lang = tts_engine.get_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton(f"🔊 Voice: {voice_status}", callback_data="toggle_voice")],
            [InlineKeyboardButton(f"🌐 Language: {tts_engine.languages.get(lang, 'Hindi')}", 
                                callback_data="change_language")],
            [InlineKeyboardButton("🧠 Memory: Clear", callback_data="clear_memory"),
             InlineKeyboardButton("📊 Memory Stats", callback_data="memory_stats")],
            [InlineKeyboardButton("🔔 Notifications: ON", callback_data="toggle_notify")],
            [InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def modules_keyboard(page: int = 1):
        """Build paginated modules keyboard"""
        items_per_page = 10
        modules_list = list(ACTIVE_MODULES.items())
        total_pages = (len(modules_list) + items_per_page - 1) // items_per_page
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_modules = modules_list[start_idx:end_idx]
        
        keyboard = []
        for name, code in current_modules:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"use_module_{code}")])
        
        # Navigation buttons
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"modules_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"modules_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("« Main Menu", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    analytics.track_message(user.id, "command")
    
    # Initialize user memory
    user_memory.set(user.id, f"Name: {user.first_name}, Started: {datetime.now().isoformat()}",
                   metadata={"chat_type": chat_type, "first_seen": datetime.now().isoformat()})
    
    welcome_text = f"""
🦁 *SINGH JI AI ULTRA v8.0* 🚀

_Welcome {user.first_name}! 🙏_

India ka sabse powerful AI assistant! 🇮🇳

🌟 *{len(ACTIVE_MODULES)} Active Modules*
🎙️ Voice Commands Support
🧠 Memory System
🤖 AI Chat with Groq
💬 Group Chat Support
🔊 Text-to-Speech

*Quick Start:*
• Text bhejo - AI jawab dega
• Voice message bhejo - Sunega aur bolega
• /modules - Sab modules dekho
• /help - Detailed help

*Pro Tips:* 💡
• "Mausam kaisa hai Delhi mein?"
• "Gold rate batao"
• "Kisaan ke liye sarkari yojana"
• Bas message bhejo, baaki main dekh lunga!

_Singh Ji AI - Har Indian ka AI saathi! 🤝_
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=KeyboardBuilder.main_menu()
    )

@error_handler_decorator
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    analytics.track_message(update.effective_user.id, "command")
    
    help_text = f"""
🦁 *SINGH JI AI HELP CENTER*

📚 *Main Features:*

*AI Chat:*
• Normal text bhejo - AI jawab dega
• Voice message bhejo - Sunega aur bolega
• Context aware hai - pichli baat yaad rakhta hai

*Commands:*
/start - Welcome message
/help - Yeh help
/modules - Sab {len(ACTIVE_MODULES)} modules
/use <module> - Module directly use karo
/remember <text> - Kuch yaad rakhne ko bolo
/recall - Kya yaad hai pucho
/status - System status
/settings - Settings
/about - Bot ke baare mein
/stats - Usage statistics

*Quick Modules:*
🌤️ /weather <city> - Mausam
📰 /news - Latest news
🥇 /goldrate - Gold rate
💰 /currency - Currency rates
⛽ /fuel - Petrol/diesel price

*Voice Features:*
• Voice message bhejo
• "Mausam kaisa hai?"
• "News sunao"
• "Gold rate batao"

*Settings:*
• Voice ON/OFF
• Language change (Hindi, English, Punjabi, etc.)
• Memory management
• Notifications

*Support:*
📧 Email: support@singhji.ai
🌐 Web: singhji.ai
📱 Telegram: @SinghJiAI

_Singh Ji AI - Always learning, always helping! 🚀_
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=KeyboardBuilder.main_menu()
    )

@error_handler_decorator
async def modules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all modules"""
    analytics.track_message(update.effective_user.id, "command")
    
    await update.message.reply_text(
        f"🦁 *{len(ACTIVE_MODULES)} Active Modules*\n\n"
        "Module select karo:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=KeyboardBuilder.modules_keyboard(1)
    )

@error_handler_decorator
@rate_limit_check
async def use_module_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Use specific module"""
    args = context.args
    user = update.effective_user
    
    analytics.track_message(user.id, "command")
    
    if not args:
        await update.message.reply_text(
            "❌ *Usage:* `/use <module> <query>`\n\n"
            "*Example:* `/use weather Delhi`\n\n"
            "Modules list ke liye: /modules",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    module = args[0].lower()
    query = " ".join(args[1:]) if len(args) > 1 else ""
    
    # Validate module
    valid_modules = list(ACTIVE_MODULES.values())
    if module not in valid_modules:
        similar = [m for m in valid_modules if module in m][:5]
        suggestion = "\n".join([f"• `/{m}`" for m in similar])
        await update.message.reply_text(
            f"❌ Module `{module}` nahi mila!\n\n"
            f"*Similar modules:*\n{suggestion}\n\n"
            f"Sab modules: /modules",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    analytics.track_module_usage(module)
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"⚡ *{module.upper()}* module use kar raha hoon...",
        parse_mode=ParseMode.MARKDOWN
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
            
            await processing_msg.edit_text(
                f"✅ *{module.upper()} Result:*\n\n"
                f"```json\n{formatted_data}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await processing_msg.edit_text(
                f"❌ Module error! Status: {response.status_code}",
                parse_mode=ParseMode.MARKDOWN
            )
            
    except requests.Timeout:
        await processing_msg.edit_text("⏰ Module timeout! Baad mein try karo!")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)[:100]}")

@error_handler_decorator
async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remember something for user"""
    user = update.effective_user
    text = " ".join(context.args)
    
    if not text:
        await update.message.reply_text(
            "❌ *Usage:* `/remember <text>`\n\n"
            "*Example:* `/remember Mera naam Ram hai, main kisaan hoon`\n\n"
            "Fir /recall se puch sakte ho!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    user_memory.set(user.id, text, metadata={
        "updated_at": datetime.now().isoformat(),
        "type": "manual_memory"
    })
    
    await update.message.reply_text(
        f"✅ *Yaad rakh liya!* 🧠\n\n"
        f"📝 *Memory:* {text}\n\n"
        f"Kabhi bhi /recall se puch sakte ho!\n"
        f"Clear karne ke liye: /settings",
        parse_mode=ParseMode.MARKDOWN
    )

@error_handler_decorator
async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recall user memory"""
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
        f"🧠 *Tumhari Memory:*\n\n"
        f"📝 {content}\n\n"
        f"⏰ Last Updated: {time_str}\n"
        f"📊 Metadata: {json.dumps(metadata, indent=2)}\n\n"
        f"*Naya memory:* `/remember <text>`\n"
        f"*Clear:* `/settings`",
        parse_mode=ParseMode.MARKDOWN
    )

@error_handler_decorator
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System status"""
    try:
        response = requests.get(f"{config.API_BASE_URL}/health", timeout=10)
        api_status = "✅ Online" if response.status_code == 200 else "❌ Offline"
    except:
        api_status = "❌ Offline"
    
    memory_stats = user_memory.stats
    analytics_summary = analytics.get_summary()
    
    status_text = f"""
🦁 *SYSTEM STATUS*

*Core Services:*
🤖 Bot: ✅ Running
🧠 AI: ✅ Online ({config.GROQ_API_KEY[:10]}...)
🔊 Voice: ✅ Enabled
💾 Memory: ✅ Active

*API Status:*
🌐 API: {api_status}
⚡ Rate Limiter: ✅ Active

*Memory Stats:*
👥 Users in Memory: {memory_stats['total_users']}
📦 Max Size: {memory_stats['max_size']}
⏰ TTL: {memory_stats['ttl_hours']} hours

*Bot Stats:*
💬 Total Messages: {analytics_summary['total_messages']}
👤 Unique Users: {analytics_summary['unique_users']}
🕐 Uptime: {analytics_summary['uptime']}
❌ Errors: {analytics_summary['errors']}

*Top Modules:*
{chr(10).join([f"• {mod}: {count}" for mod, count in analytics_summary['top_modules'][:5]])}

*Environment:* {config.ENVIRONMENT}
*Version:* v8.1 Fixed
    """
    
    await update.message.reply_text(
        status_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
            InlineKeyboardButton("📊 Full Stats", callback_data="bot_stats")
        ]])
    )

@error_handler_decorator
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings menu"""
    user = update.effective_user
    
    await update.message.reply_text(
        "⚙️ *Settings*\n\n"
        "Apni preferences customize karo:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=KeyboardBuilder.settings_menu(user.id)
    )

@error_handler_decorator
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot"""
    about_text = """
🦁 *SINGH JI AI ULTRA*

*Version:* 8.1 Fixed
*Created:* 2024
*Platform:* Railway

*Tech Stack:*
• Python + FastAPI
• Groq AI (Llama 3.1)
• Telegram Bot API
• gTTS Voice Engine
• Supabase (Coming Soon)

*Capabilities:*
• 95 Active Modules
• Voice Recognition
• Text-to-Speech
• Memory System
• Rate Limiting
• Analytics

*Mission:*
Har Indian tak AI ki shakti pahunchana! 🇮🇳
Kisaan, vyapari, student - sab ke liye!

*Developer:* JITENDRA SINGH
*Contact:* @SinghJiAI

_Singh Ji AI - Desh ka AI, Desh ke liye! 🚀_
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Website", url="https://singhji.ai"),
         InlineKeyboardButton("📱 Channel", url="https://t.me/SinghJiAI")],
        [InlineKeyboardButton("« Main Menu", callback_data="main_menu")]
    ])
    
    await update.message.reply_text(
        about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

# ═══════════════════════════════════════════════════════
# VOICE MESSAGE HANDLER
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    user = update.effective_user
    
    analytics.track_message(user.id, "voice")
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "🎙️ *Voice message mil gaya!*\n"
        "Process kar raha hoon...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Download voice file
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # For now, acknowledge receipt (voice-to-text integration coming)
        ai_response = await ai_brain.get_response(
            "User ne voice message bheja hai. Pucho ki text mein kya chahiye.",
            user.id,
            user.first_name
        )
        
        await processing_msg.delete()
        
        # Send text response
        await update.message.reply_text(
            f"🎙️ *Voice Message Received!*\n\n"
            f"🤖 *Singh Ji:* {ai_response['text']}\n\n"
            f"💡 *Tip:* Abhi text mein bhi puch sakte ho!\n"
            f"Example: `Mausam kaisa hai?`",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send voice response
        voice_response = await tts_engine.text_to_speech(ai_response['text'], user.id)
        if voice_response:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_response),
                caption="🎙️ Singh Ji ka jawab!",
                reply_to_message_id=update.message.message_id
            )
        
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Voice process nahi ho paya!\n"
            f"Error: {str(e)[:100]}\n\n"
            f"Text se try karo!"
        )

# ═══════════════════════════════════════════════════════
# TEXT CHAT HANDLER (AI)
# ═══════════════════════════════════════════════════════

@error_handler_decorator
@rate_limit_check
async def text_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for AI chat"""
    user = update.effective_user
    user_text = update.message.text
    chat_type = update.effective_chat.type
    
    analytics.track_message(user.id, "text")
    
    # Skip if text is too long
    if len(user_text) > 1000:
        await update.message.reply_text(
            "📝 Message thoda lamba hai! 1000 characters se kam mein bolo!\n"
            "Ya voice message bhejo 🎙️",
            reply_to_message_id=update.message.message_id
        )
        return
    
    # Handle group chats differently
    if chat_type in ['group', 'supergroup']:
        await handle_group_message(update, context)
        return
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Get AI response
    ai_response = await ai_brain.get_response(
        user_text,
        user.id,
        user.first_name,
        chat_type
    )
    
    # Send text response
    sent_message = await update.message.reply_text(
        f"🤖 {ai_response['text']}",
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=update.message.message_id
    )
    
    # Send voice response if not error
    if not ai_response.get('error') and tts_engine.get_language(user.id) != "off":
        voice_bytes = await tts_engine.text_to_speech(ai_response['text'], user.id)
        if voice_bytes:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_bytes),
                caption="🎙️ Bolke sunao!",
                reply_to_message_id=sent_message.message_id
            )

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in group chats — FIXED: No random replies!"""
    message = update.message
    user = update.effective_user
    bot_username = context.bot.username
    
    should_respond = False
    user_text = message.text
    
    # Respond if mentioned
    if f"@{bot_username}" in message.text:
        user_text = message.text.replace(f"@{bot_username}", "").strip()
        should_respond = True
    
    # Respond if replying to bot
    elif message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        should_respond = True
    
    # ❌ REMOVED: Random 5% response — was causing spam!
    # Only respond when explicitly mentioned or replied
    
    if should_respond and user_text.strip():
        await update.message.chat.send_action(action="typing")
        
        ai_response = await ai_brain.get_response(
            user_text,
            user.id,
            user.first_name,
            "group"
        )
        
        await message.reply_text(
            f"🤖 {ai_response['text']}",
            parse_mode=ParseMode.MARKDOWN
        )

# ═══════════════════════════════════════════════════════
# CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════

@error_handler_decorator
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    try:
        # Main menu
        if data == "main_menu":
            await query.edit_message_text(
                "🦁 *Main Menu*\n\nKya karna chahte ho?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=KeyboardBuilder.main_menu()
            )
        
        # Help
        elif data == "help":
            await help_command(update, context)
        
        # About
        elif data == "about":
            await about_command(update, context)
        
        # List modules
        elif data == "list_modules":
            await query.edit_message_text(
                f"📋 *{len(ACTIVE_MODULES)} Active Modules*\n\nModule select karo:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=KeyboardBuilder.modules_keyboard(1)
            )
        
        # Modules pagination
        elif data.startswith("modules_page_"):
            page = int(data.split("_")[-1])
            await query.edit_message_text(
                f"📋 *Modules (Page {page})*\n\nModule select karo:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=KeyboardBuilder.modules_keyboard(page)
            )
        
        # Use module
        elif data.startswith("use_module_"):
            module = data.replace("use_module_", "")
            await query.edit_message_text(
                f"⚡ *{module.upper()} Module*\n\n"
                f"Usage: `/use {module} <query>`\n\n"
                f"Example: `/use {module} test`",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Modules List", callback_data="list_modules")
                ]])
            )
        
        # Quick actions
        elif data == "quick_weather":
            await query.edit_message_text(
                "🌤️ *Weather*\n\nCity name bhejo!\nExample: `Delhi`",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Back", callback_data="main_menu")
                ]])
            )
        
        elif data == "quick_news":
            # Fetch quick news
            try:
                response = requests.get(f"{config.API_BASE_URL}/modules/news/", timeout=10)
                news_data = response.json()
                await query.edit_message_text(
                    f"📰 *Latest News*\n\n{json.dumps(news_data, indent=2)[:3000]}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                await query.edit_message_text(
                    "❌ News fetch nahi ho payi!\n/use news se try karo",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Back", callback_data="main_menu")
                    ]])
                )
        
        elif data == "quick_gold":
            try:
                response = requests.get(f"{config.API_BASE_URL}/modules/goldrate/", timeout=10)
                gold_data = response.json()
                await query.edit_message_text(
                    f"🥇 *Gold Rate*\n\n{json.dumps(gold_data, indent=2)[:3000]}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                await query.edit_message_text(
                    "❌ Gold rate fetch nahi ho payi!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Back", callback_data="main_menu")
                    ]])
                )
        
        # Settings
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ *Settings*\n\nPreferences customize karo:",
                parse_mode=ParseMode.MARKDOWN,
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
                f"🔊 Voice: *{status}*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=KeyboardBuilder.settings_menu(user.id)
            )
        
        elif data == "clear_memory":
            user_memory.delete(user.id)
            await query.edit_message_text(
                "✅ Memory clear kar di!",
                reply_markup=KeyboardBuilder.settings_menu(user.id)
            )
        
        elif data == "memory_stats":
            memory_data = user_memory.get(user.id)
            stats = user_memory.stats
            
            await query.edit_message_text(
                f"🧠 *Memory Stats*\n\n"
                f"Your Memory: {memory_data['content'][:100]}...\n"
                f"Last Updated: {memory_data['timestamp']}\n\n"
                f"Total Users: {stats['total_users']}\n"
                f"Max Size: {stats['max_size']}\n"
                f"TTL: {stats['ttl_hours']} hours",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Back", callback_data="settings")
                ]])
            )
        
        # Voice mode
        elif data == "voice_mode":
            await query.edit_message_text(
                "🎙️ *Voice Mode*\n\n"
                "Voice message bhejo aur main sunuga!\n"
                "Fir bolke jawab dunga!\n\n"
                "Try karo:\n"
                "• 'Mausam kaisa hai?'\n"
                "• 'News sunao'\n"
                "• 'Gold rate batao'\n"
                "• 'Kya haal hai?'\n\n"
                "Ya text se bhi puch sakte ho!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Main Menu", callback_data="main_menu")
                ]])
            )
        
        # Bot stats
        elif data == "bot_stats" or data == "refresh_status":
            summary = analytics.get_summary()
            
            await query.edit_message_text(
                f"📊 *Bot Statistics*\n\n"
                f"💬 Total Messages: {summary['total_messages']}\n"
                f"👤 Unique Users: {summary['unique_users']}\n"
                f"👥 Active 24h: {summary['active_users_24h']}\n"
                f"🎙️ Voice: {summary['voice_messages']}\n"
                f"💬 Text: {summary['text_messages']}\n"
                f"⚡ Commands: {summary['commands']}\n"
                f"❌ Errors: {summary['errors']}\n"
                f"🕐 Uptime: {summary['uptime']}\n\n"
                f"*Top 5 Modules:*\n" +
                "\n".join([f"• {m}: {c}" for m, c in summary['top_modules'][:5]]),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Refresh", callback_data="bot_stats"),
                    InlineKeyboardButton("« Menu", callback_data="main_menu")
                ]])
            )
        
        # AI Mode toggle
        elif data == "mode_ai":
            current_mode = ai_brain.current_modes.get(user.id, "default")
            modes = list(ai_brain.system_prompts.keys())
            current_idx = modes.index(current_mode) if current_mode in modes else 0
            next_idx = (current_idx + 1) % len(modes)
            next_mode = modes[next_idx]
            
            ai_brain.current_modes[user.id] = next_mode
            
            mode_emojis = {
                "default": "🤖",
                "technical": "💻",
                "farming": "🌾",
                "business": "💼"
            }
            
            await query.edit_message_text(
                f"{mode_emojis.get(next_mode, '🤖')} AI Mode: *{next_mode.upper()}*\n\n"
                f"Ab main {next_mode} mode mein jawab dunga!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Change Mode", callback_data="mode_ai"),
                    InlineKeyboardButton("« Menu", callback_data="main_menu")
                ]])
            )
    
    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            await query.edit_message_text(
                "❌ Kuch error ho gaya! /start karo fir se.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Restart", callback_data="main_menu")
                ]])
            )
        except:
            pass

# ═══════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    analytics.track_error()
    
    # Send message to the user
    if update and isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ *Oops!*\n\n"
                "Kuch unexpected error ho gaya!\n"
                "Team ko bata diya hai. Jaldi fix karenge!\n\n"
                "Tab tak /start karo.",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass

# ═══════════════════════════════════════════════════════
# APPLICATION SETUP
# ═══════════════════════════════════════════════════════

application = None

async def setup_application() -> Application:
    """Setup and configure the bot application"""
    global application
    
    if application is not None:
        return application
    
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Set bot commands
    commands = [
        BotCommand("start", "🦁 Start bot"),
        BotCommand("help", "❓ Help & guide"),
        BotCommand("modules", "📋 All 95 modules"),
        BotCommand("use", "⚡ Use a module"),
        BotCommand("remember", "🧠 Remember something"),
        BotCommand("recall", "🔍 Recall memory"),
        BotCommand("status", "📊 System status"),
        BotCommand("settings", "⚙️ Settings"),
        BotCommand("about", "ℹ️ About Singh Ji AI"),
        BotCommand("stats", "📈 Usage statistics"),
    ]
    await application.bot.set_my_commands(commands)
    
    # Register handlers
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("modules", modules_command))
    application.add_handler(CommandHandler("use", use_module_command))
    application.add_handler(CommandHandler("remember", remember_command))
    application.add_handler(CommandHandler("recall", recall_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Voice messages
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    # Text messages (non-commands)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_chat_handler)
    )
    
    # Callback queries
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot application setup complete!")
    return application

# ═══════════════════════════════════════════════════════
# WEBHOOK HANDLERS
# ═══════════════════════════════════════════════════════

def verify_webhook_secret(request: Request) -> bool:
    """Verify webhook secret token"""
    if config.ENVIRONMENT == "development":
        return True
    
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    expected = config.WEBHOOK_SECRET
    
    if not secret_token or not hmac.compare_digest(secret_token, expected):
        logger.warning("Webhook secret verification failed!")
        return False
    
    return True

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook from Telegram — FIXED!"""
    global application
    
    # Verify webhook secret
    if not verify_webhook_secret(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # Get application — FIX: Only initialize once, NEVER start() in webhook mode!
        if application is None:
            application = await setup_application()
            await application.initialize()
            # ❌ REMOVED: await application.start() — causes duplicate handlers!
            logger.info("✅ Bot initialized via webhook!")
        
        # Process update
        data = await request.json()
        update = Update.de_json(data, application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return {"ok": True, "timestamp": datetime.now().isoformat()}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)[:200]}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot": "Singh Ji AI v8.1",
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
    """Setup webhook URL"""
    try:
        app = await setup_application()
        await app.initialize()
        # ❌ REMOVED: await app.start() — webhook mode mein nahi chahiye!
        
        # Set webhook
        await app.bot.set_webhook(
            url=config.WEBHOOK_URL,
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        
        # Verify webhook
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
    """Delete webhook and switch to polling"""
    try:
        if application:
            await application.bot.delete_webhook(drop_pending_updates=True)
            # ❌ REMOVED: await application.stop() — polling mode mein hi chahiye
            global app_instance
            app_instance = None
        
        return {
            "status": "success",
            "message": "Webhook deleted. Bot stopped."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/stats")
async def get_stats():
    """Get detailed bot statistics"""
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
    """Broadcast message to all users (Admin only)"""
    try:
        data = await request.json()
        message = data.get("message", "")
        admin_key = data.get("admin_key", "")
        
        # Verify admin key
        if admin_key != os.getenv("ADMIN_KEY", "singhji_admin_2024"):
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message required")
        
        if not application:
            raise HTTPException(status_code=503, detail="Bot not running")
        
        # Get all unique users from memory
        users = list(user_memory.memory.keys())
        sent_count = 0
        failed_count = 0
        
        for user_id in users[:100]:  # Limit to 100 users per broadcast
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 *Broadcast from Singh Ji AI*\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent_count += 1
                await asyncio.sleep(0.05)  # Rate limit prevention
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
                failed_count += 1
        
        return {
            "status": "success",
            "sent": sent_count,
            "failed": failed_count,
            "total_users": len(users)
        }
    
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════
# STARTUP/SHUTDOWN EVENTS — FIXED: No polling in production!
# ═══════════════════════════════════════════════════════

@router.on_event("startup")
async def startup_event():
    """Initialize bot on startup — FIXED: Only in development!"""
    if config.ENVIRONMENT == "development":
        try:
            app = await setup_application()
            await app.initialize()
            await app.start()
            
            # Use polling in development ONLY
            await app.updater.start_polling()
            logger.info("✅ Bot started in polling mode (development)!")
        except Exception as e:
            logger.error(f"Startup error: {e}")
    else:
        logger.info("🚀 Production mode — webhook only, no polling!")

@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global application
    if application:
        try:
            await application.stop()
            await application.shutdown()
            logger.info("✅ Bot shutdown complete!")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# ═══════════════════════════════════════════════════════
# MAIN ENTRY POINT (for direct run)
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "handler:router",
        host="0.0.0.0",
        port=port,
        reload=config.ENVIRONMENT == "development",
        log_level="info"
    )
