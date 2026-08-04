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
# 40+ MODULES IMPORT (ROUTER-FREE)
# ==========================================
from modules.aavishkar.handler import handler as aavishkar_handler
from modules.ai_chat.handler import handler as ai_chat_handler
from modules.analytics.handler import handler as analytics_handler
from modules.banking.handler import handler as banking_handler
from modules.currency.handler import handler as currency_handler
from modules.currents_api.handler import handler as currents_api_handler
from modules.daily_report.handler import handler as daily_report_handler
from modules.emergency.handler import handler as emergency_handler
from modules.fuel.handler import handler as fuel_handler
from modules.goldrate.handler import handler as goldrate_handler
from modules.govt.handler import handler as govt_handler
from modules.guard_agent.handler import handler as guard_agent_handler
from modules.horoscope.handler import handler as horoscope_handler
from modules.kisaan_doctor.handler import handler as kisaan_doctor_handler
from modules.language.handler import handler as language_handler
from modules.language_hub.handler import handler as language_hub_handler
from modules.mandi.handler import handler as mandi_handler
from modules.master_scheduler.handler import handler as master_scheduler_handler
from modules.meta_agent.handler import handler as meta_agent_handler
from modules.news.handler import handler as news_handler
from modules.newsdata.handler import handler as newsdata_handler
from modules.oauth_connector.handler import handler as oauth_connector_handler
from modules.pani.handler import handler as pani_handler
from modules.plant_id.handler import handler as plant_id_handler
from modules.rozgar.handler import handler as rozgar_handler
from modules.scheme_swarm.handler import handler as scheme_swarm_handler
from modules.search.handler import handler as search_handler
from modules.sewer.handler import handler as sewer_handler
from modules.singhji_tv.handler import handler as singhji_tv_handler
from modules.social_agent.handler import handler as social_agent_handler
from modules.supabase_memory.handler import handler as supabase_memory_handler
from modules.supreme_agent.handler import handler as supreme_agent_handler
from modules.trolley.handler import handler as trolley_handler
from modules.upi.handler import handler as upi_handler
from modules.voice.handler import handler as voice_handler
from modules.voice_cmd.handler import handler as voice_cmd_handler
from modules.voice_tts.handler import handler as voice_tts_handler
from modules.weather.handler import handler as weather_handler
from modules.whatsapp.handler import handler as whatsapp_handler

# ==========================================
# 40+ MODULES REGISTER (DIRECT HANDLER - NO ROUTER)
# ==========================================
app.get("/api/v1/aavishkar")(aavishkar_handler)
app.get("/api/v1/ai-chat")(ai_chat_handler)
app.get("/api/v1/analytics")(analytics_handler)
app.get("/api/v1/banking")(banking_handler)
app.get("/api/v1/currency")(currency_handler)
app.get("/api/v1/currents")(currents_api_handler)
app.get("/api/v1/daily-report")(daily_report_handler)
app.get("/api/v1/emergency")(emergency_handler)
app.get("/api/v1/fuel")(fuel_handler)
app.get("/api/v1/goldrate")(goldrate_handler)
app.get("/api/v1/govt")(govt_handler)
app.get("/api/v1/guard")(guard_agent_handler)
app.get("/api/v1/horoscope")(horoscope_handler)
app.get("/api/v1/kisaan-doctor")(kisaan_doctor_handler)
app.get("/api/v1/language")(language_handler)
app.get("/api/v1/language-hub")(language_hub_handler)
app.get("/api/v1/mandi")(mandi_handler)
app.get("/api/v1/scheduler")(master_scheduler_handler)
app.get("/api/v1/meta")(meta_agent_handler)
app.get("/api/v1/news")(news_handler)
app.get("/api/v1/newsdata")(newsdata_handler)
app.get("/api/v1/oauth")(oauth_connector_handler)
app.get("/api/v1/pani")(pani_handler)
app.get("/api/v1/plant-id")(plant_id_handler)
app.get("/api/v1/rozgar")(rozgar_handler)
app.get("/api/v1/scheme-swarm")(scheme_swarm_handler)
app.get("/api/v1/search")(search_handler)
app.get("/api/v1/sewer")(sewer_handler)
app.get("/api/v1/tv")(singhji_tv_handler)
app.get("/api/v1/social")(social_agent_handler)
app.get("/api/v1/memory")(supabase_memory_handler)
app.get("/api/v1/supreme")(supreme_agent_handler)
app.get("/api/v1/trolley")(trolley_handler)
app.get("/api/v1/upi")(upi_handler)
app.get("/api/v1/voice")(voice_handler)
app.get("/api/v1/voice-cmd")(voice_cmd_handler)
app.get("/api/v1/voice-tts")(voice_tts_handler)
app.get("/api/v1/weather")(weather_handler)
app.get("/api/v1/whatsapp")(whatsapp_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
