import os
import sys
import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---- Core imports ----
from core.config import AVAILABLE_KEYS, RATE_LIMIT_GLOBAL, RATE_LIMIT_STRICT
from core.database import SUPABASE_CLIENT
from core.rate_limit import _init_rate_limit, _is_rate_limited
from core.telegram import _ensure_correct_webhook
from core.swarm import SMART_SWARM
from core.scheduler import MASTER_SCHEDULER, USER_PREFERENCES

# ---- API routes ----
from api.routes import router as api_router
from api.admin import router as admin_router
from api.payment import router as payment_router
from api.video import router as video_router
from api.social import router as social_router
from api.ai import router as ai_router

# ---- Telegram webhook ----
from telegram.webhook import router as telegram_router

# ---- Utils ----
from utils.helpers import validate_env_vars, MODULES, MAIN_KEYBOARD

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ==========================================
# LIFESPAN
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global HTTP_CLIENT, MASTER_SCHEDULER
    logger.info("🚀 Singh Ji AI Ultra v8.3 FINAL Starting...")
    
    HTTP_CLIENT = httpx.AsyncClient(timeout=20, limits=httpx.Limits(max_keepalive_connections=20, max_connections=100))
    _init_rate_limit()
    
    # Init Swarm
    SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    
    # Load users
    from core.scheduler import _load_user_preferences_sync
    from fastapi.concurrency import run_in_threadpool
    loaded = await run_in_threadpool(_load_user_preferences_sync)
    USER_PREFERENCES.update(loaded)
    
    # Webhook
    await _ensure_correct_webhook(HTTP_CLIENT)
    
    # Start Scheduler
    from core.scheduler import SinghJiMasterScheduler
    from core.telegram import _telegram_send_message
    MASTER_SCHEDULER = SinghJiMasterScheduler(
        http_client=HTTP_CLIENT,
        telegram_send_func=_telegram_send_message,
        api_keys=AVAILABLE_KEYS,
        modules=MODULES,
        user_preferences=USER_PREFERENCES,
        admin_user_id=ADMIN_USER_ID,
    )
    await MASTER_SCHEDULER.start()
    
    yield
    
    logger.info("🛑 Shutting down...")
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER.stop()
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
