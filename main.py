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
# MODULES IMPORT - SIRF modules/ WALE
# ==========================================
from modules.weather.handler import router as weather_router
from modules.mandi.handler import router as mandi_router
from modules.ai_chat.handler import router as ai_chat_router
from modules.news.handler import router as news_router
from modules.plant_id.handler import router as plant_router
from modules.whatsapp.handler import handler as whatsapp_handler
from modules.trolley.handler import handler as trolley_handler
from modules.daily_report.handler import router as daily_report_router
from modules.analytics.handler import handler as analytics_handler
from modules.upi.handler import handler as upi_handler
from modules.voice_tts.handler import handler as voice_tts_handler
from modules.language.handler import handler as language_handler
from modules.supreme_agent.handler import router as supreme_agent_router

# ==========================================
# ✅ TELEGRAM - DIRECT ROOT SE IMPORT
# ==========================================
from telegram.handler import router as telegram_router  # ✅ YEH SAHI HAI!

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
# ROUTERS REGISTER
# ==========================================
app.include_router(supreme_agent_router, prefix="/api/v1/supreme-agent")
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat")
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(mandi_router, prefix="/api/v1/mandi")
app.include_router(news_router, prefix="/api/v1/news")
app.include_router(plant_router, prefix="/api/v1/plant")
app.include_router(telegram_router, prefix="/api/v1/telegram")  # ✅ Direct root wala
app.add_api_route("/api/v1/whatsapp", whatsapp_handler, methods=["GET", "POST"])
app.add_api_route("/api/v1/trolley", trolley_handler, methods=["GET", "POST"])
app.include_router(daily_report_router, prefix="/api/v1/daily-report")
app.add_api_route("/api/v1/analytics", analytics_handler, methods=["GET", "POST"])
app.add_api_route("/api/v1/upi", upi_handler, methods=["GET", "POST"])
app.add_api_route("/api/v1/voice-tts", voice_tts_handler, methods=["GET", "POST"])
app.add_api_route("/api/v1/language", language_handler, methods=["GET", "POST"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
