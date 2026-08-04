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
# 40+ MODULES IMPORT (AUTO-GENERATED)
# ==========================================
from modules.aavishkar.handler import router as aavishkar_router
from modules.ai_chat.handler import router as ai_chat_router
from modules.analytics.handler import router as analytics_router
from modules.banking.handler import router as banking_router
from modules.currency.handler import router as currency_router
from modules.currents_api.handler import router as currents_api_router
from modules.daily_report.handler import router as daily_report_router
from modules.emergency.handler import router as emergency_router
from modules.fuel.handler import router as fuel_router
from modules.goldrate.handler import router as goldrate_router
from modules.govt.handler import router as govt_router
from modules.guard_agent.handler import router as guard_agent_router
from modules.horoscope.handler import router as horoscope_router
from modules.kisaan_doctor.handler import router as kisaan_doctor_router
from modules.language.handler import router as language_router
from modules.language_hub.handler import router as language_hub_router
from modules.mandi.handler import router as mandi_router
from modules.master_scheduler.handler import router as master_scheduler_router
from modules.meta_agent.handler import router as meta_agent_router
from modules.news.handler import router as news_router
from modules.newsdata.handler import router as newsdata_router
from modules.oauth_connector.handler import router as oauth_connector_router
from modules.pani.handler import router as pani_router
from modules.plant_id.handler import router as plant_id_router
from modules.rozgar.handler import router as rozgar_router
from modules.scheme_swarm.handler import router as scheme_swarm_router
from modules.search.handler import router as search_router
from modules.sewer.handler import router as sewer_router
from modules.singhji_tv.handler import router as singhji_tv_router
from modules.social_agent.handler import router as social_agent_router
from modules.supabase_memory.handler import router as supabase_memory_router
from modules.supreme_agent.handler import router as supreme_agent_router
from modules.trolley.handler import router as trolley_router
from modules.upi.handler import router as upi_router
from modules.voice.handler import router as voice_router
from modules.voice_cmd.handler import router as voice_cmd_router
from modules.voice_tts.handler import router as voice_tts_router
from modules.weather.handler import router as weather_router
from modules.whatsapp.handler import router as whatsapp_router

# ==========================================
# 40+ MODULES REGISTER
# ==========================================
app.include_router(aavishkar_router, prefix="/api/v1/aavishkar")
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat")
app.include_router(analytics_router, prefix="/api/v1/analytics")
app.include_router(banking_router, prefix="/api/v1/banking")
app.include_router(currency_router, prefix="/api/v1/currency")
app.include_router(currents_api_router, prefix="/api/v1/currents")
app.include_router(daily_report_router, prefix="/api/v1/daily-report")
app.include_router(emergency_router, prefix="/api/v1/emergency")
app.include_router(fuel_router, prefix="/api/v1/fuel")
app.include_router(goldrate_router, prefix="/api/v1/goldrate")
app.include_router(govt_router, prefix="/api/v1/govt")
app.include_router(guard_agent_router, prefix="/api/v1/guard")
app.include_router(horoscope_router, prefix="/api/v1/horoscope")
app.include_router(kisaan_doctor_router, prefix="/api/v1/kisaan-doctor")
app.include_router(language_router, prefix="/api/v1/language")
app.include_router(language_hub_router, prefix="/api/v1/language-hub")
app.include_router(mandi_router, prefix="/api/v1/mandi")
app.include_router(master_scheduler_router, prefix="/api/v1/scheduler")
app.include_router(meta_agent_router, prefix="/api/v1/meta")
app.include_router(news_router, prefix="/api/v1/news")
app.include_router(newsdata_router, prefix="/api/v1/newsdata")
app.include_router(oauth_connector_router, prefix="/api/v1/oauth")
app.include_router(pani_router, prefix="/api/v1/pani")
app.include_router(plant_id_router, prefix="/api/v1/plant-id")
app.include_router(rozgar_router, prefix="/api/v1/rozgar")
app.include_router(scheme_swarm_router, prefix="/api/v1/scheme-swarm")
app.include_router(search_router, prefix="/api/v1/search")
app.include_router(sewer_router, prefix="/api/v1/sewer")
app.include_router(singhji_tv_router, prefix="/api/v1/tv")
app.include_router(social_agent_router, prefix="/api/v1/social")
app.include_router(supabase_memory_router, prefix="/api/v1/memory")
app.include_router(supreme_agent_router, prefix="/api/v1/supreme")
app.include_router(trolley_router, prefix="/api/v1/trolley")
app.include_router(upi_router, prefix="/api/v1/upi")
app.include_router(voice_router, prefix="/api/v1/voice")
app.include_router(voice_cmd_router, prefix="/api/v1/voice-cmd")
app.include_router(voice_tts_router, prefix="/api/v1/voice-tts")
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
