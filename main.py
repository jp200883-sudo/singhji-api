import time
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

# Core imports
from core.config import config
from core.cache import cache_store
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message

# ==========================================
# ACTUAL MODULES - REPO KE HISAB SE
# ==========================================
from modules.weather.handler import router as weather_router
from modules.mandi.handler import router as mandi_router
from modules.ai_chat.handler import router as ai_chat_router
from modules.news.handler import router as news_router
from modules.plant_id.handler import router as plant_router
from modules.telegram.handler import router as telegram_router
from modules.whatsapp.handler import router as whatsapp_router
from modules.trolley.handler import router as trolley_router
from modules.daily_report.handler import router as daily_report_router
from modules.analytics.handler import router as analytics_router
from modules.upi.handler import router as upi_router
from modules.voice_tts.handler import router as voice_tts_router
from modules.language.handler import router as language_router
from modules.supreme_agent.handler import router as supreme_agent_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Singh Ji AI ULTRA v8.0 Starting...")
    try:
        await send_telegram_message("🦁 Singh Ji AI ULTRA v8.0 Started!")
    except Exception as e:
        logger.warning(f"⚠️ Telegram notification failed: {e}")
    yield
    logger.info("👋 Singh Ji AI ULTRA Shutting down...")

app = FastAPI(
    title="Singh Ji AI ULTRA",
    version="8.0",
    lifespan=lifespan
)

@app.middleware("http")
async def rate_limit_wrapper(request: Request, call_next):
    await rate_limit_middleware(request)
    return await call_next(request)

# ==========================================
# ROOT ENDPOINTS
# ==========================================
@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "8.0",
        "modules": 14,
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
# ROUTERS REGISTER - REPO PATHS
# ==========================================
app.include_router(supreme_agent_router, prefix="/api/v1/supreme-agent")
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat")
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(mandi_router, prefix="/api/v1/mandi")
app.include_router(news_router, prefix="/api/v1/news")
app.include_router(plant_router, prefix="/api/v1/plant")
app.include_router(telegram_router, prefix="/api/v1/telegram")
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp")
app.include_router(trolley_router, prefix="/api/v1/trolley")
app.include_router(daily_report_router, prefix="/api/v1/daily-report")
app.include_router(analytics_router, prefix="/api/v1/analytics")
app.include_router(upi_router, prefix="/api/v1/upi")
app.include_router(voice_tts_router, prefix="/api/v1/voice-tts")
app.include_router(language_router, prefix="/api/v1/language")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
