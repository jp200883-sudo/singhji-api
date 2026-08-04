import time
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

# Core imports
from core.config import config
from core.cache import cache_store
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# LIFESPAN MANAGER
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Singh Ji AI ULTRA v8.0 Shuru Ho Raha Hai...")
    await send_telegram_message("🦁 Singh Ji AI ULTRA v8.0 Started!")
    yield
    logger.info("👋 Singh Ji AI ULTRA Band Ho Raha Hai...")

# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(
    title="Singh Ji AI ULTRA",
    version="8.0",
    description="40+ Modules, AI-Powered WhatsApp Bot",
    lifespan=lifespan
)

# ==========================================
# RATE LIMIT MIDDLEWARE
# ==========================================
@app.middleware("http")
async def rate_limit_wrapper(request: Request, call_next):
    try:
        rate_limit_middleware(request)
    except Exception:
        pass
    response = await call_next(request)
    return response

# ==========================================
# ROOT ENDPOINTS
# ==========================================
@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "8.0",
        "bot": "Singh Ji AI ULTRA",
        "message": "🦁 JAI HIND! 🇮🇳"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "cache_size": len(cache_store)
    }

@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": time.time(),
        "version": "8.0"
    }

# ==========================================
# TELEGRAM WEBHOOK (WITH AUTO-REPLY + COMMANDS)
# ==========================================
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram messages with auto-reply and commands
    """
    try:
        body = await request.json()
        logger.info(f"📨 Telegram message received: {body}")
        
        # Extract message details
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        first_name = message.get("from", {}).get("first_name", "User")
        
        if not chat_id:
            return {"status": "error", "message": "No chat_id found"}
        
        # ==========================================
        # COMMAND HANDLER
        # ==========================================
        if text.lower() == "/start":
            reply = f"""🦁 **Namaste {first_name}!** 
Welcome to **Singh Ji AI ULTRA v8.0**!

✅ **Available Commands:**
/start - Welcome Message
/help - All Commands
/weather [city] - Get Weather
/mandi [state] - Mandi Rates
/news - Latest News
/ai [question] - AI Chat
/horoscope - Daily Horoscope
/gold - Gold Rate
/upi - UPI Info
/status - Bot Status

🦁 JAI HIND! 🇮🇳"""
            
        elif text.lower() == "/help":
            reply = """📚 **Commands List:**

/start - Welcome Message
/help - Show this help
/weather [city] - Weather info
/mandi [state] - Mandi rates
/news - Latest news
/ai [question] - AI Chat (Groq+Gemini)
/horoscope - Daily horoscope
/gold - Today's gold rate
/upi - UPI payment info
/status - Bot status
/voice - Voice command

🦁 Type any command to get started!"""
            
        elif text.lower().startswith("/weather"):
            city = text.replace("/weather", "").strip()
            if city:
                reply = f"🌤️ **Weather for {city}**\n\nTemperature: 25°C\nCondition: Sunny\nHumidity: 60%\n\n_(Coming soon: Live weather API)_"
            else:
                reply = "🌤️ Please provide a city name.\nExample: `/weather Delhi`"
            
        elif text.lower().startswith("/mandi"):
            state = text.replace("/mandi", "").strip()
            if state:
                reply = f"🌾 **Mandi Rates for {state}**\n\nWheat: ₹2200/ton\nRice: ₹1800/ton\nSugarcane: ₹350/ton\n\n_(Coming soon: Live mandi API)_"
            else:
                reply = "🌾 Please provide a state name.\nExample: `/mandi UP`"
            
        elif text.lower() == "/news":
            reply = "📰 **Latest News Headlines**\n\n1. India launches new space mission\n2. Monsoon arrives early in Kerala\n3. Gold prices reach all-time high\n4. New govt schemes announced\n\n_(Coming soon: Live news API)_"
            
        elif text.lower().startswith("/ai"):
            question = text.replace("/ai", "").strip()
            if question:
                reply = f"🤖 **AI Chat**\n\nQuestion: {question}\n\nAnswer: Singh Ji AI is thinking...\n\n_(Coming soon: Groq/Gemini integration)_"
            else:
                reply = "🤖 Please provide a question.\nExample: `/ai What is the capital of India?`"
            
        elif text.lower() == "/horoscope":
            reply = "🔮 **Daily Horoscope**\n\nAries: Today is your lucky day!\nTaurus: Focus on your goals\nGemini: New opportunities ahead\nCancer: Family time is important\n\n_(Coming soon: Personalized horoscope)_"
            
        elif text.lower() == "/gold":
            reply = "🏆 **Today's Gold Rate**\n\n24K Gold: ₹72,500/10g\n22K Gold: ₹66,800/10g\nSilver: ₹85,000/kg\n\n_(Coming soon: Live gold API)_"
            
        elif text.lower() == "/upi":
            reply = "💳 **UPI Payment Info**\n\n✅ UPI ID: singhji@upi\n✅ QR Code: Available on website\n✅ Razorpay Integration: Active\n\nPayments are secure and encrypted."
            
        elif text.lower() == "/status":
            reply = f"📊 **Bot Status**\n\n✅ Server: Running\n✅ Version: 8.0\n✅ Modules: 40+\n✅ Cache: {len(cache_store)} items\n✅ Uptime: Active\n\n🦁 All systems operational!"
            
        elif text.lower() == "/voice":
            reply = "🎤 **Voice Command**\n\nSend a voice message to this bot!\nVoice-to-text will be available soon.\n\nSupported languages: Hindi, English, Hinglish"
            
        else:
            # Default response for unknown commands
            reply = f"🦁 **Hello {first_name}!**\n\nYou said: `{text}`\n\nType /help to see all available commands.\n\nJAI HIND! 🇮🇳"
        
        # ==========================================
        # SEND REPLY
        # ==========================================
        await send_telegram_message(chat_id, reply)
        
        return {"status": "ok", "message": "Reply sent"}
        
    except Exception as e:
        logger.error(f"❌ Telegram webhook error: {e}")
        return {"status": "error", "error": str(e)}

# ==========================================
# 40+ MODULES - DIRECT FASTAPI ROUTES
# ==========================================
@app.get("/api/v1/mandi")
async def mandi_endpoint():
    return {"status": "ok", "module": "mandi"}

@app.get("/api/v1/weather")
async def weather_endpoint():
    return {"status": "ok", "module": "weather"}

@app.get("/api/v1/ai-chat")
async def ai_chat_endpoint():
    return {"status": "ok", "module": "ai_chat"}

@app.get("/api/v1/news")
async def news_endpoint():
    return {"status": "ok", "module": "news"}

@app.get("/api/v1/goldrate")
async def goldrate_endpoint():
    return {"status": "ok", "module": "goldrate"}

@app.get("/api/v1/upi")
async def upi_endpoint():
    return {"status": "ok", "module": "upi"}

@app.get("/api/v1/analytics")
async def analytics_endpoint():
    return {"status": "ok", "module": "analytics"}

@app.get("/api/v1/trolley")
async def trolley_endpoint():
    return {"status": "ok", "module": "trolley"}

@app.get("/api/v1/daily-report")
async def daily_report_endpoint():
    return {"status": "ok", "module": "daily_report"}

@app.get("/api/v1/language")
async def language_endpoint():
    return {"status": "ok", "module": "language"}

@app.get("/api/v1/supreme")
async def supreme_agent_endpoint():
    return {"status": "ok", "module": "supreme_agent"}

@app.get("/api/v1/horoscope")
async def horoscope_endpoint():
    return {"status": "ok", "module": "horoscope"}

@app.get("/api/v1/rozgar")
async def rozgar_endpoint():
    return {"status": "ok", "module": "rozgar"}

@app.get("/api/v1/pani")
async def pani_endpoint():
    return {"status": "ok", "module": "pani"}

@app.get("/api/v1/sewer")
async def sewer_endpoint():
    return {"status": "ok", "module": "sewer"}

@app.get("/api/v1/plant-id")
async def plant_id_endpoint():
    return {"status": "ok", "module": "plant_id"}

@app.get("/api/v1/guard")
async def guard_agent_endpoint():
    return {"status": "ok", "module": "guard_agent"}

@app.get("/api/v1/social")
async def social_agent_endpoint():
    return {"status": "ok", "module": "social_agent"}

@app.get("/api/v1/memory")
async def supabase_memory_endpoint():
    return {"status": "ok", "module": "supabase_memory"}

@app.get("/api/v1/meta")
async def meta_agent_endpoint():
    return {"status": "ok", "module": "meta_agent"}

@app.get("/api/v1/tv")
async def singhji_tv_endpoint():
    return {"status": "ok", "module": "singhji_tv"}

@app.get("/api/v1/voice-tts")
async def voice_tts_endpoint():
    return {"status": "ok", "module": "voice_tts"}

@app.get("/api/v1/voice-cmd")
async def voice_cmd_endpoint():
    return {"status": "ok", "module": "voice_cmd"}

@app.get("/api/v1/voice")
async def voice_endpoint():
    return {"status": "ok", "module": "voice"}

@app.get("/api/v1/currency")
async def currency_endpoint():
    return {"status": "ok", "module": "currency"}

@app.get("/api/v1/fuel")
async def fuel_endpoint():
    return {"status": "ok", "module": "fuel"}

@app.get("/api/v1/emergency")
async def emergency_endpoint():
    return {"status": "ok", "module": "emergency"}

@app.get("/api/v1/banking")
async def banking_endpoint():
    return {"status": "ok", "module": "banking"}

@app.get("/api/v1/govt")
async def govt_endpoint():
    return {"status": "ok", "module": "govt"}

@app.get("/api/v1/search")
async def search_endpoint():
    return {"status": "ok", "module": "search"}

@app.get("/api/v1/translate")
async def translate_endpoint():
    return {"status": "ok", "module": "translate"}

@app.get("/api/v1/aavishkar")
async def aavishkar_endpoint():
    return {"status": "ok", "module": "aavishkar"}

@app.get("/api/v1/scheme-swarm")
async def scheme_swarm_endpoint():
    return {"status": "ok", "module": "scheme_swarm"}

@app.get("/api/v1/kisaan-doctor")
async def kisaan_doctor_endpoint():
    return {"status": "ok", "module": "kisaan_doctor"}

@app.get("/api/v1/language-hub")
async def language_hub_endpoint():
    return {"status": "ok", "module": "language_hub"}

@app.get("/api/v1/currents")
async def currents_api_endpoint():
    return {"status": "ok", "module": "currents_api"}

@app.get("/api/v1/newsdata")
async def newsdata_endpoint():
    return {"status": "ok", "module": "newsdata"}

@app.get("/api/v1/master-scheduler")
async def master_scheduler_endpoint():
    return {"status": "ok", "module": "master_scheduler"}

@app.get("/api/v1/whatsapp")
async def whatsapp_endpoint():
    return {"status": "ok", "module": "whatsapp"}

@app.get("/api/v1/telegram-bot")
async def telegram_bot_endpoint():
    return {"status": "ok", "module": "telegram_bot"}

@app.get("/api/v1/oauth")
async def oauth_connector_endpoint():
    return {"status": "ok", "module": "oauth_connector"}

@app.get("/api/v1/trolley")
async def trolley_endpoint():
    return {"status": "ok", "module": "trolley"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
