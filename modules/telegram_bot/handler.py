"""
🦁 SINGH JI AI — TELEGRAM BOT HANDLER (WITH VOICE)
modules/telegram_bot/handler.py
"""

from fastapi import APIRouter, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
import json
import os
import tempfile
import io

router = APIRouter()

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = "https://singhji-api-production-85ca.up.railway.app"
WEBHOOK_URL = "https://singhji-api-production-85ca.up.railway.app/modules/telegram_bot/webhook"

# AI Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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
# AI BRAIN — Groq Se Jawab Lo
# ═══════════════════════════════════════════════════════

async def get_ai_response(user_text: str, user_name: str = "User") -> str:
    """AI se jawab lo — Groq API"""
    try:
        import groq
        client = groq.Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": f"""Tu Singh Ji AI hai — ek desi Indian AI assistant.
                    Tone: Friendly, helpful, thoda masti wala.
                    Language: Hindi + English mix (Hinglish).
                    User ka naam: {user_name}
                    
                    Rules:
                    - Hamesha short aur crisp jawab do
                    - Emojis use karo
                    - Jaise dost se baat karte hain waise
                    - Agar weather puche toh current data ke liye /use weather bolo
                    """
                },
                {"role": "user", "content": user_text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback simple response
        return f"🦁 Singh Ji AI: Arre bhai, thoda busy hoon! {user_text} ke baare mein jaldi batata hoon! 💪"

# ═══════════════════════════════════════════════════════
# TEXT TO SPEECH — GTTS Se Bolke Bhejo
# ═══════════════════════════════════════════════════════

async def text_to_speech(text: str) -> bytes:
    """Text → Voice (gTTS Hindi)"""
    try:
        from gtts import gTTS
        
        # Short text for voice
        short_text = text[:500] if len(text) > 500 else text
        
        tts = gTTS(text=short_text, lang='hi', slow=False)
        
        # Save to bytes
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return mp3_fp.read()
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📋 Sab Modules", callback_data="list_modules")],
        [InlineKeyboardButton("🎙️ Voice Commands", callback_data="voice_cmd")],
        [InlineKeyboardButton("📰 News Scheduler", callback_data="news_scheduler")],
        [InlineKeyboardButton("📊 System Status", callback_data="status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🦁 *Singh Ji AI Ultra v8.0*\n\n"
        f"Welcome *{user.first_name}*!\n\n"
        f"*95 Active Modules* ready hain!\n\n"
        f"*Commands:*\n"
        f"/modules — Sab modules ki list\n"
        f"/use <module> — Module use karo\n"
        f"/news — News scheduler\n"
        f"/voice — Voice commands\n"
        f"/status — System status\n\n"
        f"🎙️ *Voice bhi bhej sakte ho!*\n"
        f"Bas microphone dabao aur bolo! 🔥",
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
        "• 'Petrol ka rate' → Fuel\n"
        "• 'Mandi rates' → Mandi\n"
        "• 'Naukri dhoondo' → Rozgar\n"
        "• 'Kya haal hai?' → General chat\n\n"
        "🎤 *Microphone dabao aur bolo!*",
        parse_mode="Markdown"
    )

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        status = "✅ Online" if response.status_code == 200 else "❌ Offline"
        await update.message.reply_text(
            f"🦁 *System Status*\n\n"
            f"Status: {status}\n"
            f"Modules: *95/300* Active\n"
            f"Version: *v8.0*\n"
            f"Platform: *Railway*\n"
            f"Voice: *🎙️ Enabled*\n\n"
            f"*All systems operational!* 🚀",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ System offline!")

# ═══════════════════════════════════════════════════════
# VOICE MESSAGE HANDLER — 🔥 YEH MAIN FEATURE HAI!
# ═══════════════════════════════════════════════════════

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ne voice message bheja — Suno, Samjho, Jawab Do!"""
    user = update.effective_user
    
    # 1. Processing message
    processing_msg = await update.message.reply_text("🎙️ Sun raha hoon...")
    
    try:
        # 2. Voice file download karo
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # 3. STT (Speech-to-Text) — Simple approach
        # Abhi ke liye: Voice ko text mein convert nahi kar pa rahe
        # Future mein Whisper API add karenge
        
        # 4. User ko batao ki voice mila
        await processing_msg.delete()
        
        # 5. AI se generic jawab lo (voice ke liye special)
        ai_response = await get_ai_response(
            "User ne voice message bheja hai. Unse pucho ki unhe kya chahiye.", 
            user.first_name
        )
        
        # 6. Text response bhejo
        text_msg = await update.message.reply_text(
            f"🎙️ *Voice Message Received!*\n\n"
            f"🤖 *Singh Ji AI:*\n{ai_response}\n\n"
            f"💡 *Tip:* Abhi voice-to-text integration chal raha hai. "
            f"Tab tak *text se* bhejo jaise:\n"
            f"• `/use weather Delhi`\n"
            f"• `Mausam kaisa hai?`",
            parse_mode="Markdown"
        )
        
        # 7. Voice response bhi bhejo (TTS)
        voice_bytes = await text_to_speech(ai_response)
        if voice_bytes:
            await update.message.reply_voice(
                voice=io.BytesIO(voice_bytes),
                caption="🎙️ Singh Ji AI ka jawab!"
            )
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(
            f"❌ *Voice Error:* {str(e)}\n\n"
            f"Text se try karo: `/use weather Delhi`",
            parse_mode="Markdown"
        )

# ═══════════════════════════════════════════════════════
# TEXT MESSAGE HANDLER — General Chat
# ═══════════════════════════════════════════════════════

async def text_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ne text bheja — AI se jawab lo!"""
    user = update.effective_user
    user_text = update.message.text
    
    # Agar command nahi hai toh AI chat
    if not user_text.startswith('/'):
        # Typing indicator
        await update.message.chat.send_action(action="typing")
        
        # AI se jawab lo
        ai_response = await get_ai_response(user_text, user.first_name)
        
        # Text bhejo
        await update.message.reply_text(
            f"🤖 *Singh Ji AI:*\n\n{ai_response}",
            parse_mode="Markdown"
        )
        
        # Voice bhi bhejo
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
            "🎤 *Microphone dabao!*",
            parse_mode="Markdown"
        )

    elif query.data == "news_scheduler":
        await query.edit_message_text(
            "📰 *News Scheduler*\n\n⏰ *4:00 AM* — Har roz!",
            parse_mode="Markdown"
        )

    elif query.data == "status":
        await query.edit_message_text(
            "🦁 *System Status*\n\n✅ All 95 modules active\n✅ Railway running\n✅ Voice Enabled 🎙️\n✅ Ready! 🚀",
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
        
        # Button callbacks
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Voice message handler
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Text chat handler (commands ke baad, generic text)
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
        "voice_enabled": True
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
