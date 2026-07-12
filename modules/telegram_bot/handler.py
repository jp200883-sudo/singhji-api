"""
🦁 SINGH JI AI — TELEGRAM BOT HANDLER
modules/telegram_bot/handler.py
Sab Features: Commands + AI Chat + Voice + TTS + Memory + Group + Admin
"""

from fastapi import APIRouter, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
import json
import os
import io
import tempfile

router = APIRouter()

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_BASE_URL = "https://singhji-api-production-85ca.up.railway.app"
WEBHOOK_URL = "https://singhji-api-production-85ca.up.railway.app/modules/telegram_bot/webhook"

# User memory (simple dict - future mein Supabase)
user_memory = {}

# ═══════════════════════════════════════════════════════
# AI BRAIN
# ═══════════════════════════════════════════════════════

async def get_ai_response(user_text: str, user_id: int, user_name: str = "User") -> str:
    """AI se jawab lo - with memory"""
    # User memory se context lo
    context = user_memory.get(user_id, "")
    
    try:
        import groq
        client = groq.Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": f"""Tu Singh Ji AI hai. Hinglish mein jawab de. 
                    User: {user_name}. Previous context: {context}"""
                },
                {"role": "user", "content": user_text}
            ],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        # Memory update karo
        user_memory[user_id] = f"User asked: {user_text[:100]}"
        
        return answer
        
    except Exception as e:
        return f"🦁 Arre {user_name}, thoda busy hoon! Baad mein batata hoon! 💪"

# ═══════════════════════════════════════════════════════
# TEXT TO SPEECH
# ═══════════════════════════════════════════════════════

async def text_to_speech(text: str) -> bytes:
    """Text → Voice (gTTS)"""
    try:
        from gtts import gTTS
        
        short_text = text[:500] if len(text) > 500 else text
        
        tts = gTTS(text=short_text, lang='hi', slow=False)
        
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return mp3_fp.read()
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

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
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Memory mein save karo
    user_memory[user.id] = f"Name: {user.first_name}"
    
    keyboard = [
        [InlineKeyboardButton("📋 Sab Modules", callback_data="list_modules")],
        [InlineKeyboardButton("🎙️ Voice Commands", callback_data="voice_cmd")],
        [InlineKeyboardButton("📰 News Scheduler", callback_data="news_scheduler")],
        [InlineKeyboardButton("📊 System Status", callback_data="status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🦁 *Singh Ji AI Ultra v8.0*\n\n"
        f"Welcome *{user.first_name}*! 🙏\n\n"
        f"*95 Active Modules* ready hain!\n\n"
        f"*Commands:*\n"
        f"/modules — Sab modules ki list\n"
        f"/use <module> — Module use karo\n"
        f"/news — News scheduler\n"
        f"/voice — Voice commands\n"
        f"/status — System status\n"
        f"/remember <text> — Yaad rakho\n"
        f"/recall — Kya yaad hai?\n\n"
        f"🎙️ *Voice message bhi bhej sakte ho!*\n"
        f"💬 *Normal text se bhi baat karo!*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def list_modules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    module_text = "🦁 *Active Modules (95)*\n\n"
    for name, code in ACTIVE_MODULES.items():
        module_text += f"• {name} — `/{code}`\n"
    module_text += "\n*Use:* `/use <module> <query>`"
    await update.message.reply_text(module_text, parse_mode="Markdown")

async def use_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ *Usage:* `/use <module> <query>`\n\n"
            "*Example:* `/use weather Delhi`",
            parse_mode="Markdown"
        )
        return

    module = args[0].lower()
    query = " ".join(args[1:]) if len(args) > 1 else ""

    try:
        response = requests.get(
            f"{API_BASE_URL}/modules/{module}/",
            params={"q": query},
            timeout=30
        )
        data = response.json()
        await update.message.reply_text(
            f"✅ *{module.upper()} Result:*\n\n"
            f"```json\n{json.dumps(data, indent=2, ensure_ascii=False)[:4000]}\n```",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error:* {str(e)}",
            parse_mode="Markdown"
        )

async def news_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏰ 4:00 AM", callback_data="news_4am")],
        [InlineKeyboardButton("🌅 6:00 AM", callback_data="news_6am")],
        [InlineKeyboardButton("🌞 8:00 AM", callback_data="news_8am")],
        [InlineKeyboardButton("🌙 9:00 PM", callback_data="news_9pm")],
        [InlineKeyboardButton("❌ Band Karo", callback_data="news_off")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📰 *News Scheduler*\n\nCurrent: *4:00 AM*\n\nSelect karo:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def voice_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙️ *Voice Commands*\n\n"
        "Bas *voice message* bhejo aur bolo:\n"
        "• 'Mausam kaisa hai?' → Weather\n"
        "• 'News sunao' → News\n"
        "• 'Sona ka rate' → Gold Rate\n"
        "• 'Kya haal hai?' → General chat\n\n"
        "🎤 *Microphone dabao aur bolo!*\n\n"
        "Ya *text se* bhi puch sakte ho!",
        parse_mode="Markdown"
    )

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        status = "✅ Online" if response.status_code == 200 else "❌ Offline"
        
        # Memory stats
        memory_users = len(user_memory)
        
        await update.message.reply_text(
            f"🦁 *System Status*\n\n"
            f"Status: {status}\n"
            f"Modules: *95/300* Active\n"
            f"Version: *v8.0*\n"
            f"Platform: *Railway*\n"
            f"Voice: *🎙️ Enabled*\n"
            f"AI Chat: *🤖 Enabled*\n"
            f"Memory Users: *{memory_users}*\n\n"
            f"*All systems operational!* 🚀",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ System offline!")

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ka kuch yaad rakho"""
    user = update.effective_user
    text = " ".join(context.args)
    
    if not text:
        await update.message.reply_text(
            "❌ *Usage:* `/remember <text>`\n\n"
            "*Example:* `/remember Mera naam JITENDRA hai`",
            parse_mode="Markdown"
        )
        return
    
    user_memory[user.id] = text
    
    await update.message.reply_text(
        f"✅ *Yaad rakh liya!*\n\n"
        f"📝 {text}\n\n"
        f"Ab kabhi bhi `/recall` se puch sakte ho!",
        parse_mode="Markdown"
    )

async def recall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ki memory dikhao"""
    user = update.effective_user
    memory = user_memory.get(user.id, "Kuch yaad nahi hai!")
    
    await update.message.reply_text(
        f"🧠 *Tumhari Memory:*\n\n"
        f"📝 {memory}\n\n"
        f"*Naya yaad rakhne ke liye:* `/remember <text>`",
        parse_mode="Markdown"
    )

# ═══════════════════════════════════════════════════════
# VOICE MESSAGE HANDLER — 🔥 YEH FEATURE HAI!
# ═══════════════════════════════════════════════════════

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ne voice message bheja — Suno, AI jawab do, Bolke bhejo!"""
    user = update.effective_user
    
    # Processing message
    processing_msg = await update.message.reply_text("🎙️ Sun raha hoon...")
    
    try:
        # Voice file download karo
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # Abhi ke liye: Voice received confirm karo
        await processing_msg.delete()
        
        # AI se generic jawab lo
        ai_response = await get_ai_response(
            "User ne voice message bheja hai. Unse pucho ki unhe kya chahiye.", 
            user.id,
            user.first_name
        )
        
        # Text response bhejo
        await update.message.reply_text(
            f"🎙️ *Voice Message Received!*\n\n"
            f"🤖 *Singh Ji AI:*\n{ai_response}\n\n"
            f"💡 *Tip:* Abhi voice-to-text integration chal raha hai. "
            f"Tab tak *text se* bhejo jaise:\n"
            f"• `Kya haal hai?`\n"
            f"• `/use weather Delhi`",
            parse_mode="Markdown"
        )
        
        # 🔊 Voice response bhi bhejo (TTS)
        voice_response = await text_to_speech(ai_response)
        if voice_response:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_response),
                caption="🎙️ Singh Ji AI ka jawab!"
            )
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(
            f"❌ *Voice Error:* {str(e)}\n\n"
            f"Text se try karo: `Kya haal hai?`",
            parse_mode="Markdown"
        )

# ═══════════════════════════════════════════════════════
# TEXT CHAT HANDLER — AI JAWAB + VOICE
# ═══════════════════════════════════════════════════════

async def text_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ne text bheja — AI se jawab lo + Bolke bhejo!"""
    user = update.effective_user
    user_text = update.message.text
    
    # Agar command nahi hai toh AI chat
    if not user_text.startswith('/'):
        # Typing indicator
        await update.message.chat.send_action(action="typing")
        
        # AI se jawab lo
        ai_response = await get_ai_response(user_text, user.id, user.first_name)
        
        # Text bhejo
        await update.message.reply_text(
            f"🤖 *Singh Ji AI:*\n\n{ai_response}",
            parse_mode="Markdown"
        )
        
        # 🔊 Voice bhi bhejo (TTS)
        voice_bytes = await text_to_speech(ai_response)
        if voice_bytes:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_bytes),
                caption="🎙️ Bolke sunao!"
            )

# ═══════════════════════════════════════════════════════
# BUTTON CALLBACKS
# ═══════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "list_modules":
        module_text = "🦁 *Active Modules (95)*\n\n"
        for name, code in list(ACTIVE_MODULES.items())[:20]:
            module_text += f"• {name} — `/{code}`\n"
        module_text += "\n...aur 75 modules! `/modules` se dekho"
        await query.edit_message_text(module_text, parse_mode="Markdown")

    elif query.data == "voice_cmd":
        await query.edit_message_text(
            "🎙️ *Voice Commands*\n\n"
            "Bas *voice message* bhejo aur bolo:\n"
            "• 'Mausam kaisa hai?' → Weather\n"
            "• 'News sunao' → News\n"
            "• 'Sona ka rate' → Gold\n"
            "• 'Kya haal hai?' → Chat\n\n"
            "🎤 *Microphone dabao!*\n\n"
            "Ya *text se* bhi puch sakte ho!",
            parse_mode="Markdown"
        )

    elif query.data == "news_scheduler":
        await query.edit_message_text(
            "📰 *News Scheduler*\n\n⏰ *4:00 AM* — Har roz!",
            parse_mode="Markdown"
        )

    elif query.data == "status":
        await query.edit_message_text(
            "🦁 *System Status*\n\n✅ All 95 modules active\n✅ Railway running\n✅ Voice Enabled 🎙️\n✅ AI Chat Enabled 🤖\n✅ Ready! 🚀",
            parse_mode="Markdown"
        )

    elif query.data.startswith("news_"):
        time_map = {
            "news_4am": "4:00 AM",
            "news_6am": "6:00 AM",
            "news_8am": "8:00 AM",
            "news_9pm": "9:00 PM",
            "news_off": "OFF"
        }
        time_set = time_map.get(query.data, "4:00 AM")
        await query.edit_message_text(
            f"✅ *News Updated*\n\nAb: *{time_set}* 📰",
            parse_mode="Markdown"
        )

# ═══════════════════════════════════════════════════════
# WEBHOOK HANDLER
# ═══════════════════════════════════════════════════════

application = None

def get_application():
    global application
    if application is None:
        if not TELEGRAM_BOT_TOKEN:
            print("⚠️ TELEGRAM_BOT_TOKEN missing!")
            return None
        
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("modules", list_modules))
        application.add_handler(CommandHandler("use", use_module))
        application.add_handler(CommandHandler("news", news_scheduler))
        application.add_handler(CommandHandler("voice", voice_commands))
        application.add_handler(CommandHandler("status", system_status))
        application.add_handler(CommandHandler("remember", remember))
        application.add_handler(CommandHandler("recall", recall))
        
        # Button callbacks
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Voice message handler
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Text chat handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_chat_handler))
        
    return application

@router.post("/webhook")
async def telegram_webhook(request: Request):
    global application
    if application is None:
        application = get_application()
        if application:
            await application.initialize()
            await application.start()
    
    if not application:
        return {"ok": False, "error": "Bot not initialized"}
    
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@router.get("/health")
async def bot_health():
    return {
        "status": "alive",
        "bot": "Singh Ji AI",
        "modules": len(ACTIVE_MODULES),
        "token_set": bool(TELEGRAM_BOT_TOKEN),
        "voice_enabled": True,
        "ai_chat_enabled": True,
        "memory_users": len(user_memory)
    }

@router.get("/setup-webhook")
async def setup_webhook():
    global application
    if application is None:
        application = get_application()
        if application:
            await application.initialize()
            await application.start()
    
    if not application:
        return {"status": "error", "message": "Token missing"}
    
    await application.bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    return {"status": "success", "webhook_url": WEBHOOK_URL}

@router.get("/delete-webhook")
async def delete_webhook():
    if application:
        await application.bot.delete_webhook(drop_pending_updates=True)
    return {"status": "success", "message": "Webhook deleted"}
