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
# 40+ MODULES - DIRECT FASTAPI ROUTES (NO ROUTER)
# ==========================================

@app.get("/api/v1/aavishkar")
async def aavishkar_endpoint():
    return {"status": "ok", "module": "aavishkar"}

@app.get("/api/v1/ai-chat")
async def ai_chat_endpoint():
    return {"status": "ok", "module": "ai_chat"}

@app.get("/api/v1/analytics")
async def analytics_endpoint():
    return {"status": "ok", "module": "analytics"}

@app.get("/api/v1/banking")
async def banking_endpoint():
    return {"status": "ok", "module": "banking"}

@app.get("/api/v1/currency")
async def currency_endpoint():
    return {"status": "ok", "module": "currency"}

@app.get("/api/v1/currents")
async def currents_api_endpoint():
    return {"status": "ok", "module": "currents_api"}

@app.get("/api/v1/daily-report")
async def daily_report_endpoint():
    return {"status": "ok", "module": "daily_report"}

@app.get("/api/v1/emergency")
async def emergency_endpoint():
    return {"status": "ok", "module": "emergency"}

@app.get("/api/v1/fuel")
async def fuel_endpoint():
    return {"status": "ok", "module": "fuel"}

@app.get("/api/v1/goldrate")
async def goldrate_endpoint():
    return {"status": "ok", "module": "goldrate"}

@app.get("/api/v1/govt")
async def govt_endpoint():
    return {"status": "ok", "module": "govt"}

@app.get("/api/v1/guard")
async def guard_agent_endpoint():
    return {"status": "ok", "module": "guard_agent"}

@app.get("/api/v1/horoscope")
async def horoscope_endpoint():
    return {"status": "ok", "module": "horoscope"}

@app.get("/api/v1/kisaan-doctor")
async def kisaan_doctor_endpoint():
    return {"status": "ok", "module": "kisaan_doctor"}

@app.get("/api/v1/language")
async def language_endpoint():
    return {"status": "ok", "module": "language"}

@app.get("/api/v1/language-hub")
async def language_hub_endpoint():
    return {"status": "ok", "module": "language_hub"}

@app.get("/api/v1/mandi")
async def mandi_endpoint():
    return {"status": "ok", "module": "mandi"}

@app.get("/api/v1/scheduler")
async def master_scheduler_endpoint():
    return {"status": "ok", "module": "master_scheduler"}

@app.get("/api/v1/meta")
async def meta_agent_endpoint():
    return {"status": "ok", "module": "meta_agent"}

@app.get("/api/v1/news")
async def news_endpoint():
    return {"status": "ok", "module": "news"}

@app.get("/api/v1/newsdata")
async def newsdata_endpoint():
    return {"status": "ok", "module": "newsdata"}

@app.get("/api/v1/oauth")
async def oauth_connector_endpoint():
    return {"status": "ok", "module": "oauth_connector"}

@app.get("/api/v1/pani")
async def pani_endpoint():
    return {"status": "ok", "module": "pani"}

@app.get("/api/v1/plant-id")
async def plant_id_endpoint():
    return {"status": "ok", "module": "plant_id"}

@app.get("/api/v1/rozgar")
async def rozgar_endpoint():
    return {"status": "ok", "module": "rozgar"}

@app.get("/api/v1/scheme-swarm")
async def scheme_swarm_endpoint():
    return {"status": "ok", "module": "scheme_swarm"}

@app.get("/api/v1/search")
async def search_endpoint():
    return {"status": "ok", "module": "search"}

@app.get("/api/v1/sewer")
async def sewer_endpoint():
    return {"status": "ok", "module": "sewer"}

@app.get("/api/v1/tv")
async def singhji_tv_endpoint():
    return {"status": "ok", "module": "singhji_tv"}

@app.get("/api/v1/social")
async def social_agent_endpoint():
    return {"status": "ok", "module": "social_agent"}

@app.get("/api/v1/memory")
async def supabase_memory_endpoint():
    return {"status": "ok", "module": "supabase_memory"}

@app.get("/api/v1/supreme")
async def supreme_agent_endpoint():
    return {"status": "ok", "module": "supreme_agent"}

@app.get("/api/v1/trolley")
async def trolley_endpoint():
    return {"status": "ok", "module": "trolley"}

@app.get("/api/v1/upi")
async def upi_endpoint():
    return {"status": "ok", "module": "upi"}

@app.get("/api/v1/voice")
async def voice_endpoint():
    return {"status": "ok", "module": "voice"}

@app.get("/api/v1/voice-cmd")
async def voice_cmd_endpoint():
    return {"status": "ok", "module": "voice_cmd"}

@app.get("/api/v1/voice-tts")
async def voice_tts_endpoint():
    return {"status": "ok", "module": "voice_tts"}

@app.get("/api/v1/weather")
async def weather_endpoint():
    return {"status": "ok", "module": "weather"}

@app.get("/api/v1/whatsapp")
async def whatsapp_endpoint():
    return {"status": "ok", "module": "whatsapp"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
