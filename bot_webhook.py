"""
🤖 Singh Ji AI Ultra — Telegram Bot Webhook
Backend: Render (singhji-api)
Python-Telegram-Bot v20+ with FastAPI webhook
"""

import os
import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ─── CONFIG ─────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "https://singhji-api.onrender.com/webhook")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://singhji-api.onrender.com")

# ─── LOGGING ────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── HANDLERS ─────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with menu"""
    keyboard = [
        [InlineKeyboardButton("🤴 Core Agents", callback_data="hub_core")],
        [InlineKeyboardButton("🎬 Entertainment", callback_data="hub_ent")],
        [InlineKeyboardButton("🍔 Lifestyle", callback_data="hub_life")],
        [InlineKeyboardButton("🏦 Banking", callback_data="hub_bank")],
        [InlineKeyboardButton("📚 Education", callback_data="hub_edu")],
        [InlineKeyboardButton("🌍 Global", callback_data="hub_global")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = """🦁 *Welcome to Singh Ji AI Ultra!*

Your all-in-one India Super App is now on Telegram!

✅ *23 Core Agents* — Chat, Search, Image, Code
✅ *Banking Hub* — UPI, Bills, Loans
✅ *26 Languages* — Bhashini powered
✅ *24/7 Available* — Zero phone load!

🍌 *केला मोड ON — केला नहीं होता भाई अकेला!*

Choose a hub below 👇"""

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """🛠️ *Singh Ji Bot Commands:*

/start — Main menu
/help — This message
/ai <question> — Ask AI anything
/image <prompt> — Generate AI image
/weather <city> — Get weather
/news — Latest news
/translate <text> — Translate to Hindi
/balance — Check bank balance
/pay <upi> <amount> — UPI payment

🍌 *केला मोड ON!*"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI chat handler"""
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("🤔 *Usage:* /ai <your question>\n\nExample: /ai What is quantum computing?", parse_mode="Markdown")
        return

    await update.message.reply_text("🧠 *Singh Ji AI thinking...*", parse_mode="Markdown")
    # TODO: Connect to your OpenAI/GPT backend
    await update.message.reply_text(
        f"🦁 *Singh Ji says:*\n\nYou asked: *{query}*\n\n"
        "[This will connect to your GPT-4 backend via singhji-api]\n\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DALL-E image generation"""
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("🎨 *Usage:* /image <description>\n\nExample: /image a lion in space", parse_mode="Markdown")
        return

    await update.message.reply_text("🎨 *Generating image...*", parse_mode="Markdown")
    # TODO: Connect to DALL-E backend
    await update.message.reply_text(
        f"🖼️ *Image prompt:* {prompt}\n\n"
        "[This will connect to your DALL-E backend via singhji-api]\n\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Weather handler"""
    city = " ".join(context.args) or "Delhi"
    await update.message.reply_text(
        f"🌤️ *Weather for {city}*\n\n"
        "[Connect to Weather API backend]\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """News handler"""
    await update.message.reply_text(
        "📰 *Latest News*\n\n"
        "1. 🇮🇳 ISRO's Next Moon Mission Announced\n"
        "2. 🌍 Global AI Summit 2026 Key Takeaways\n"
        "3. 💰 Rupee Hits New High Against Dollar\n"
        "4. 🏏 India Wins Cricket World Cup 2026!\n\n"
        "[Connect to News API backend]\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translation handler"""
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🌐 *Usage:* /translate <text>\n\nExample: /translate Hello", parse_mode="Markdown")
        return

    await update.message.reply_text(
        f"🌐 *Translation*\n\n"
        f"English: {text}\n"
        f"Hindi: [Bhashini API pending]\n"
        f"Punjabi: [Bhashini API pending]\n\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bank balance check"""
    await update.message.reply_text(
        "🏦 *Your Bank Balance*\n\n"
        "💰 Total: *₹2,45,780.50*\n"
        "📱 UPI ID: singhji@paytm\n"
        "🏛️ Account: ****4521\n\n"
        "[Connect to Banking API backend]\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def upi_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """UPI payment handler"""
    if len(context.args) < 2:
        await update.message.reply_text("💸 *Usage:* /pay <upi-id> <amount>\n\nExample: /pay ram@paytm 500", parse_mode="Markdown")
        return

    upi_id = context.args[0]
    amount = context.args[1]

    await update.message.reply_text(
        f"💸 *UPI Payment Initiated*\n\n"
        f"To: {upi_id}\n"
        f"Amount: ₹{amount}\n"
        f"Status: ⏳ Processing...\n\n"
        "[Connect to Razorpay/UPI backend]\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline button handler"""
    query = update.callback_query
    await query.answer()

    hub_responses = {
        "hub_core": "🤴 *Core Agents Hub*\n\n23 AI agents ready!\nUse /ai <question> to chat.",
        "hub_ent": "🎬 *Entertainment Hub*\n\nMovies, music, games & memes!\nComing soon on Telegram.",
        "hub_life": "🍔 *Lifestyle Hub*\n\nFood, fitness, fashion & travel!\nComing soon on Telegram.",
        "hub_bank": "🏦 *Banking Hub*\n\nUse /balance or /pay <upi> <amount>",
        "hub_edu": "📚 *Education Hub*\n\nCourses, exams & tutoring!\nComing soon on Telegram.",
        "hub_global": "🌍 *Global Hub*\n\nNews, translation & travel!\nUse /news or /translate <text>",
    }

    response = hub_responses.get(query.data, "🍌 *केला मोड ON!*")
    await query.edit_message_text(response, parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default message handler"""
    await update.message.reply_text(
        f"🦁 *Singh Ji heard you:* "{update.message.text}"\n\n"
        "Try /help for commands or /ai for AI chat!\n"
        "🍌 *केला मोड ON!*",
        parse_mode="Markdown"
    )

# ─── FASTAPI APP ──────────────────────────────────

# Initialize PTB application
ptb = (
    Application.builder()
    .updater(None)
    .token(BOT_TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

# Add handlers
ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CommandHandler("help", help_cmd))
ptb.add_handler(CommandHandler("ai", ai_chat))
ptb.add_handler(CommandHandler("image", generate_image))
ptb.add_handler(CommandHandler("weather", weather))
ptb.add_handler(CommandHandler("news", news))
ptb.add_handler(CommandHandler("translate", translate))
ptb.add_handler(CommandHandler("balance", balance))
ptb.add_handler(CommandHandler("pay", upi_pay))
ptb.add_handler(CallbackQueryHandler(button_callback))
ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup and shutdown events"""
    await ptb.bot.setWebhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook set to: {WEBHOOK_URL}")
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

app = FastAPI(lifespan=lifespan, title="Singh Ji Telegram Bot")

@app.post("/webhook")
async def process_update(request: Request):
    """Receive Telegram updates"""
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "🍌 केला मोड ON",
        "bot": "Singh Ji AI Ultra v5.0",
        "webhook": WEBHOOK_URL,
        "backend": "Render",
        "commands": ["/start", "/help", "/ai", "/image", "/weather", "/news", "/translate", "/balance", "/pay"]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "bot": "online"}

# ─── LOCAL DEV (polling fallback) ───────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
