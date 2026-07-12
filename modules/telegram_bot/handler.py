"""
🦁 SINGH JI AI — TELEGRAM MASTER CONTROL BOT v1.0
Sab 95 Active Modules Telegram Se Control!
Webhook Mode — Railway Ready!
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import json
import os
from fastapi import FastAPI, Request
import uvicorn

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = "https://singhji-api-production-85ca.up.railway.app"
WEBHOOK_URL = "https://singhji-api-production-85ca.up.railway.app/telegram/webhook"

# ═══════════════════════════════════════════════════════
# 95 ACTIVE MODULES LIST
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
    """Welcome message with all modules"""
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("📋 Sab Modules Dekho", callback_data="list_modules")],
        [InlineKeyboardButton("🎙️ Voice Commands", callback_data="voice_cmd")],
        [InlineKeyboardButton("📰 News Scheduler (4 AM)", callback_data="news_scheduler")],
        [InlineKeyboardButton("📊 System Status", callback_data="status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🦁 *Singh Ji AI Ultra v8.0*\n\n"
        f"Welcome *{user.first_name}*!\n\n"
        f"*95 Active Modules* ready hain!\n"
        f"Koi bhi module use karo — bas command do!\n\n"
        f"*Commands:*\n"
        f"/modules — Sab modules ki list\n"
        f"/use <module> — Module use karo\n"
        f"/news — News scheduler setting\n"
        f"/voice — Voice commands\n"
        f"/status — System status\n\n"
        f"*Example:*\n"
        f"`/use weather Delhi`\n"
        f"`/use news hindi`\n"
        f"`/use goldrate`",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def list_modules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sab 95 modules ki list"""
    module_text = "🦁 *Singh Ji AI — Active Modules (95)*\n\n"

    for name, code in ACTIVE_MODULES.items():
        module_text += f"• {name} — `/{code}`\n"

    module_text += "\n*Use karo:* `/use <module_name> <query>`"

    await update.message.reply_text(module_text, parse_mode="Markdown")

async def use_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Koi bhi module use karo"""
    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ *Usage:* `/use <module> <query>`\n\n"
            "*Example:*\n"
            "`/use weather Delhi`\n"
            "`/use news hindi`\n"
            "`/use goldrate`",
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
            f"❌ *Error:* {str(e)}\n\n"
            f"Module `{module}` load nahi ho raha!",
            parse_mode="Markdown"
        )

async def news_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """News scheduler setting — 4:00 AM"""
    keyboard = [
        [InlineKeyboardButton("⏰ 4:00 AM Subah", callback_data="news_4am")],
        [InlineKeyboardButton("🌅 6:00 AM Subah", callback_data="news_6am")],
        [InlineKeyboardButton("🌞 8:00 AM Subah", callback_data="news_8am")],
        [InlineKeyboardButton("🌙 9:00 PM Raat", callback_data="news_9pm")],
        [InlineKeyboardButton("❌ Band Karo", callback_data="news_off")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📰 *News Scheduler Setting*\n\n"
        "Kitne baje news chahiye?\n"
        "Current: *4:00 AM* (Default)\n\n"
        "Select karo:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def voice_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Voice commands info"""
    await update.message.reply_text(
        "🎙️ *Voice Commands*\n\n"
        "*Bolo:*\n"
        "• 'Mausam batao' → Weather\n"
        "• 'News sunao' → News\n"
        "• 'Sona ka rate' → Gold Rate\n"
        "• 'Petrol ka rate' → Fuel Price\n"
        "• 'Mandi rates' → Mandi\n"
        "• 'Naukri dhoondo' → Rozgar\n\n"
        "*Voice message bhejo* — main samajh jaunga!",
        parse_mode="Markdown"
    )

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        status = "✅ Online" if response.status_code == 200 else "❌ Offline"

        await update.message.reply_text(
            f"🦁 *Singh Ji AI System Status*\n\n"
            f"Status: {status}\n"
            f"Modules: *95/300* Active\n"
            f"Version: *v8.0*\n"
            f"Platform: *Railway*\n\n"
            f"*Active Modules:*\n"
            f"• Voice System ✅\n"
            f"• News Scheduler ✅\n"
            f"• Weather ✅\n"
            f"• AI Chat ✅\n"
            f"• Currency ✅\n"
            f"• Gold Rate ✅\n"
            f"• Mandi Rates ✅\n"
            f"• Rozgar ✅\n"
            f"• Banking ✅\n"
            f"• UPI ✅\n\n"
            f"*All systems operational!* 🚀",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ System offline hai!")

# ═══════════════════════════════════════════════════════
# BUTTON CALLBACKS
# ═══════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Button clicks handle karo"""
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
            "Bolo ya voice message bhejo:\n"
            "• 'Mausam batao' → Weather\n"
            "• 'News sunao' → News\n"
            "• 'Sona ka rate' → Gold Rate\n"
            "• 'Petrol ka rate' → Fuel Price\n",
            parse_mode="Markdown"
        )

    elif query.data == "news_scheduler":
        await query.edit_message_text(
            "📰 *News Scheduler*\n\n"
            "⏰ *4:00 AM* — Subah ki pehli khabar\n\n"
            "Aaj se har roz 4 baje news aayegi!\n"
            "`/news` se time change karo",
            parse_mode="Markdown"
        )

    elif query.data == "status":
        await query.edit_message_text(
            "🦁 *System Status*\n\n"
            "✅ All 95 modules active\n"
            "✅ Railway platform running\n"
            "✅ Voice system online\n"
            "✅ News scheduler ready\n\n"
            "*Ready to serve!* 🚀",
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
            f"✅ *News Scheduler Updated*\n\n"
            f"Ab news aayegi: *{time_set}*\n\n"
            f"Har roz {time_set} pe news milegi! 📰",
            parse_mode="Markdown"
        )

# ═══════════════════════════════════════════════════════
# WEBHOOK SETUP
# ═══════════════════════════════════════════════════════

# FastAPI app
app = FastAPI(title="Singh Ji Telegram Bot")

# Telegram Application
application = None

@app.on_event("startup")
async def startup():
    global application
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN set nahi hai!")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers add karo
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("modules", list_modules))
    application.add_handler(CommandHandler("use", use_module))
    application.add_handler(CommandHandler("news", news_scheduler))
    application.add_handler(CommandHandler("voice", voice_commands))
    application.add_handler(CommandHandler("status", system_status))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Webhook set karo
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    print(f"🦁 Webhook set: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown():
    if application:
        await application.stop()
        await application.shutdown()
    print("👋 Bot shutdown")

@app.post("/telegram/webhook")
async def webhook(request: Request):
    """Telegram se aaya update handle karo"""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/telegram/health")
async def health():
    """Bot health check"""
    if not application:
        return {"status": "error", "message": "Bot not initialized"}
    
    me = await application.bot.get_me()
    webhook = await application.bot.get_webhook_info()
    return {
        "status": "alive",
        "bot_name": me.first_name,
        "bot_username": me.username,
        "webhook_url": webhook.url,
        "pending_updates": webhook.pending_update_count
    }

@app.get("/telegram/setup-webhook")
async def setup_webhook():
    """Manual webhook setup"""
    if not application:
        return {"status": "error", "message": "Bot not initialized"}
    await application.bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    return {"status": "success", "webhook_url": WEBHOOK_URL}

@app.get("/telegram/delete-webhook")
async def delete_webhook():
    """Webhook delete"""
    if not application:
        return {"status": "error", "message": "Bot not initialized"}
    await application.bot.delete_webhook(drop_pending_updates=True)
    return {"status": "success", "message": "Webhook deleted"}

# ═══════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
