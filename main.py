import time
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

# Core imports (अब ये अलग files से आएंगे)
from core.config import config
from core.cache import cache_store
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message

# सारे modules import (36)
from modules.weather.handler import router as weather_router
from modules.news.handler import router as news_router
from modules.mandi.handler import router as mandi_router
# ... बाकी सब

app = FastAPI(title="Singh Ji AI ULTRA", version="8.3")

# Rate limit middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    rate_limit_middleware(request)
    return await call_next(request)

# Root
@app.get("/")
async def root():
    return {"status": "ok", "version": "8.3", "modules": 36}

# सारे routers register
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(news_router, prefix="/api/v1/news")
# ... बाकी सब

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)        "message": "🦁 JAI HIND! 🇮🇳"
    }

# === सारे Routers Register ===
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(mandi_router, prefix="/api/v1/mandi")
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat")
# ... बाकी सब

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)     await MASTER_SCHEDULER.stop()
    if HTTP_CLIENT:
        await HTTP_CLIENT.aclose()

# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(title="Singh Ji AI Ultra v8.3", version="8.3.0-final", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limit Middleware
STRICT_PATH_PREFIXES = ("/api/chat", "/api/whisper/", "/api/bhashini/", "/api/tts", "/api/plant/")
RATE_LIMITED_PREFIXES = ("/api/", "/modules/")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in STRICT_PATH_PREFIXES):
        if _is_rate_limited(request, "strict", *RATE_LIMIT_STRICT):
            return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)
    elif any(path.startswith(p) for p in RATE_LIMITED_PREFIXES):
        if _is_rate_limited(request, "global", *RATE_LIMIT_GLOBAL):
            return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)
    return await call_next(request)

# ---- Register Routers ----
app.include_router(api_router)
app.include_router(admin_router, prefix="/api/admin")
app.include_router(payment_router, prefix="/api/payment")
app.include_router(video_router, prefix="/api/video")
app.include_router(social_router, prefix="/api/social")
app.include_router(ai_router, prefix="/api/ai")
app.include_router(telegram_router, prefix="/telegram")

# ---- Root ----
@app.get("/")
@app.head("/")
async def root():
    from datetime import datetime
    from core.swarm import SMART_SWARM
    active = [n for n, i in MODULES.items() if i["active"]]
    return {
        "name": "Singh Ji AI Ultra v8.3 FINAL",
        "status": "LIVE",
        "total_modules": len(MODULES),
        "active_modules": active,
        "active_count": len(active),
        "agents": SMART_SWARM.get_status(),
        "apis": AVAILABLE_KEYS,
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI Ultra v8.3"}

@app.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")    response = await call_next(request)
    return response

# ---- Routes ----
@app.get("/")
async def root():
    return {"status": "ok", "version": "8.3", "modules": len(loaded_modules)}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

# ---- Module Routes Register ----
app.include_router(ai_chat_router, prefix="/api/v1/ai-chat", tags=["AI Chat"])
app.include_router(mandi_router, prefix="/api/v1/mandi", tags=["Mandi"])
# ... बाकी सारे routers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
