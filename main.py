import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# ---- Core Imports (जो हमने अभी बनाए हैं) ----
from core.config import config
from core.database import supabase
from core.cache import cache_set, cache_get, cache_clear
from core.memory import save_memory, get_memory, get_all_memories
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message, format_telegram_message

# ==========================================
# 1. सारे Modules के Routers को Import करो
# ==========================================
from modules.weather.handler import router as weather_router
from modules.news.handler import router as news_router
from modules.mandi.handler import router as mandi_router
from modules.plant_doctor.handler import router as plant_doctor_router
from modules.gold.handler import router as gold_router
from modules.fuel.handler import router as fuel_router
from modules.tax_calc.handler import router as tax_calc_router
from modules.currency.handler import router as currency_router
from modules.govt_schemes.handler import router as govt_schemes_router
from modules.rozgar.handler import router as rozgar_router
from modules.pani_helpline.handler import router as pani_helpline_router
from modules.sewer.handler import router as sewer_router
from modules.ai_chat.handler import router as ai_chat_router
from modules.ai_chat_v2.handler import router as ai_chat_v2_router
from modules.voice_ai.handler import router as voice_ai_router
from modules.search_web.handler import router as search_web_router
from modules.translate.handler import router as translate_router
from modules.singhji_tv.handler import router as singhji_tv_router
from modules.video_gen.handler import router as video_gen_router
from modules.horoscope.handler import router as horoscope_router
from modules.yojana_match.handler import router as yojana_match_router
from modules.emergency.handler import router as emergency_router
from modules.upi_info.handler import router as upi_info_router
from modules.guard_agent.handler import router as guard_agent_router
from modules.social_agent.handler import router as social_agent_router
from modules.system_status.handler import router as system_status_router
from modules.help_commands.handler import router as help_commands_router
from modules.analytics.handler import router as analytics_router
from modules.daily_report.handler import router as daily_report_router
from modules.supreme_ai.handler import router as supreme_ai_router
from modules.supabase_memory.handler import router as supabase_memory_router
from modules.whatsapp.handler import router as whatsapp_router
from modules.meta_agent.handler import router as meta_agent_router
from modules.language_hub.handler import router as language_hub_router
from modules.swarm_status.handler import router as swarm_status_router
from modules.trolley.handler import router as trolley_router

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan Manager (Startup/Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Singh Ji AI ULTRA v8.3 - सारे फीचर्स के साथ शुरू हो रहा है...")
    logger.info(f"📦 कुल मॉड्यूल्स: 36")
    yield
    logger.info("👋 सर्वर बंद हो रहा है...")

# FastAPI App
app = FastAPI(
    title="Singh Ji AI ULTRA",
    version="8.3",
    description="40+ मॉड्यूल्स, 300 एजेंट स्वार्म, हर फीचर के साथ",
    lifespan=lifespan
)

# ---- Middleware (Rate Limit) ----
@app.middleware("http")
async def rate_limit_middleware_wrapper(request: Request, call_next):
    rate_limit_middleware(request)  # यह IP ट्रैक करेगा
    response = await call_next(request)
    return response

# ---- Global Routes ----
@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "8.3",
        "bot_name": "Singh Ji AI ULTRA",
        "total_modules": 36,
        "message": "सारे फीचर्स लोड हो चुके हैं! 🚀"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time(), "cache_size": len(cache_store)}

# ==========================================
# 3. सारे Routers को App में रजिस्टर करो
# ==========================================
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(news_router, prefix="/api/v1/news", tags=["News"])
app.include_router(mandi_router, prefix="/api/v1/mandi", tags=["Mandi"])
app.include_router(plant_doctor_router, prefix="/api/v1/plant-doctor", tags=["Plant Doctor"])
app.include_router(gold_router, prefix="/api/v1/gold", tags=["Gold"])
app.include_router(fuel_router, prefix="/api/v1/fuel", tags=["Fuel"])
app.include_router(tax_calc_router, prefix="/api/v1/tax", tags=["Tax"])
app.include_router(currency_router, prefix="/api/v1/currency", tags=["Currency"])
app.include_router(govt_schemes_router, prefix="/api/v1/govt-schemes", tags=["Govt Schemes"])
app.include_router(rozgar_router, prefix="/api/v1/rozgar", tags=["Jobs"])
app.include_router(pani_helpline_router, prefix="/api/v1/pani", tags=["Helpline"])
app.include_router(sewer_router, prefix="/api/v1/sewer", tags=["Swachh"])
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat", tags=["AI Chat"])
app.include_router(ai_chat_v2_router, prefix="/api/v1/ai-chat-v2", tags=["AI Chat v2"])
app.include_router(voice_ai_router, prefix="/api/v1/voice-ai", tags=["Voice AI"])
app.include_router(search_web_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(translate_router, prefix="/api/v1/translate", tags=["Translate"])
app.include_router(singhji_tv_router, prefix="/api/v1/tv", tags=["TV"])
app.include_router(video_gen_router, prefix="/api/v1/video-gen", tags=["Video Gen"])
app.include_router(horoscope_router, prefix="/api/v1/horoscope", tags=["Horoscope"])
app.include_router(yojana_match_router, prefix="/api/v1/yojana", tags=["Yojana"])
app.include_router(emergency_router, prefix="/api/v1/emergency", tags=["Emergency"])
app.include_router(upi_info_router, prefix="/api/v1/upi", tags=["UPI"])
app.include_router(guard_agent_router, prefix="/api/v1/guard", tags=["Guard Agent"])
app.include_router(social_agent_router, prefix="/api/v1/social", tags=["Social Agent"])
app.include_router(system_status_router, prefix="/api/v1/status", tags=["System"])
app.include_router(help_commands_router, prefix="/api/v1/help", tags=["Help"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(daily_report_router, prefix="/api/v1/daily", tags=["Daily Report"])
app.include_router(supreme_ai_router, prefix="/api/v1/supreme", tags=["Supreme AI"])
app.include_router(supabase_memory_router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
app.include_router(meta_agent_router, prefix="/api/v1/meta", tags=["Meta Agent"])
app.include_router(language_hub_router, prefix="/api/v1/language", tags=["Language Hub"])
app.include_router(swarm_status_router, prefix="/api/v1/swarm", tags=["Swarm"])
app.include_router(trolley_router, prefix="/api/v1/trolley", tags=["Trolley/Cart"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
