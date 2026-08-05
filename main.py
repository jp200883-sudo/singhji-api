import os
import sys
import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# ==========================================
# CORE IMPORTS
# ==========================================
from core.config import (
    AVAILABLE_KEYS, 
    RATE_LIMIT_GLOBAL, 
    RATE_LIMIT_STRICT, 
    APP_URL,
    TELEGRAM_TOKEN,      # ✅ यह जोड़ें
    ADMIN_USER_ID        # ✅ यह जोड़ें
)
from core.database import SUPABASE_CLIENT
from core.rate_limit import _init_rate_limit, _is_rate_limited
from core.telegram import _ensure_correct_webhook, _check_webhook_config, _telegram_send_message
from core.swarm import SMART_SWARM
from core.scheduler import MASTER_SCHEDULER, USER_PREFERENCES, _load_user_preferences_sync, SinghJiMasterScheduler
from core.cache import _cache_get, _cache_set
from core.memory import _memory_get, _memory_save

# ==========================================
# API ROUTES
# ==========================================
from api.routes import router as api_router, set_http_client as set_api_http_client
from api.admin import router as admin_router
from api.payment import router as payment_router
from api.video import router as video_router
from api.social import router as social_router, set_http_client as set_social_http_client
from api.ai import router as ai_router, set_http_client as set_ai_http_client

# ==========================================
# TELEGRAM WEBHOOK (tg_bot/ — replaces old telegram/ folder)
# ==========================================
from tg_bot.webhook import router as telegram_router, set_http_client as set_tg_http_client

# ==========================================
# UTILS
# ==========================================
from utils.helpers import MODULES, MAIN_KEYBOARD

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

# ==========================================
# GLOBAL VARIABLES
# ==========================================
HTTP_CLIENT = None

# ==========================================
# LIFESPAN
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global HTTP_CLIENT, MASTER_SCHEDULER
    
    logger.info("🚀 Singh Ji AI Ultra v8.3 FINAL Starting...")
    
    # ---- HTTP Client ----
    HTTP_CLIENT = httpx.AsyncClient(
        timeout=20,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    
    # ---- Set HTTP Client in all modules ----
    set_api_http_client(HTTP_CLIENT)
    set_ai_http_client(HTTP_CLIENT)
    set_social_http_client(HTTP_CLIENT)
    set_tg_http_client(HTTP_CLIENT)
    
    # ---- Rate Limit ----
    _init_rate_limit()
    
    # ---- Social Agent Init ----
    try:
        from modules.social_agent import core as social_core
        social_core.init_social_agent(HTTP_CLIENT)
        await social_core.SOCIAL_AGENT.load_saved_facebook_token()
        logger.info("✅ Social Agent initialized")
    except Exception as e:
        logger.warning(f"⚠️ Social Agent init failed: {e}")
    
    # ---- Swarm ----
    sync = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    logger.info(f"✅ Swarm: {sync['active']}/{sync['total']} agents loaded")
    logger.info(f"✅ Active APIs: {sum(1 for v in AVAILABLE_KEYS.values() if v)}/{len(AVAILABLE_KEYS)}")
    
    # ---- Load Users ----
    from fastapi.concurrency import run_in_threadpool
    loaded_prefs = await run_in_threadpool(_load_user_preferences_sync)
    USER_PREFERENCES.update(loaded_prefs)
    logger.info(f"✅ {len(loaded_prefs)} subscribers reloaded from Supabase")
    
    # ---- Telegram Webhook ----
    if TELEGRAM_TOKEN and APP_URL:
        await _check_webhook_config(HTTP_CLIENT)
        await _ensure_correct_webhook(HTTP_CLIENT)
    else:
        logger.warning("⚠️ TELEGRAM_TOKEN or APP_URL missing — webhook not configured")
    
    # ---- Master Scheduler ----
    MASTER_SCHEDULER = SinghJiMasterScheduler(
        http_client=HTTP_CLIENT,
        telegram_send_func=_telegram_send_message,
        api_keys=AVAILABLE_KEYS,
        modules=MODULES,
        user_preferences=USER_PREFERENCES,
        admin_user_id=ADMIN_USER_ID,
    )
    await MASTER_SCHEDULER.start()
    
    # ---- 1st Broadcast ----
    if TELEGRAM_TOKEN and APP_URL:
        await MASTER_SCHEDULER._broadcast_with_rate_limit("🌅 Singh Ji AI Ultra v8.3 Live!", parse_mode="HTML")
    
    yield
    
    logger.info("🛑 Shutting down...")
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER.stop()
    if HTTP_CLIENT:
        await HTTP_CLIENT.aclose()
    logger.info("✅ Singh Ji AI Ultra Stopped!")

# ==========================================
# FASTAPI APP
# ==========================================
app = FastAPI(
    title="Singh Ji AI Ultra v8.3 FINAL — All 42+ Modules",
    version="8.3.0-final",
    lifespan=lifespan
)

# ==========================================
# CORS
# ==========================================
ALLOWED_ORIGINS = [
    "https://jp200883-sudo.github.io",
    "http://localhost:3000",
    "http://localhost:8000",
]
_extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
if _extra_origins:
    ALLOWED_ORIGINS.extend([o.strip() for o in _extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# STATIC FILES
# ==========================================
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# RATE LIMIT MIDDLEWARE
# ==========================================
STRICT_PATH_PREFIXES = (
    "/api/chat",
    "/api/whisper/",
    "/api/bhashini/",
    "/api/tts",
    "/api/plant/",
    "/modules/voice",
)
RATE_LIMITED_PREFIXES = ("/api/", "/modules/")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in STRICT_PATH_PREFIXES):
        if _is_rate_limited(request, "strict", *RATE_LIMIT_STRICT):
            return JSONResponse(
                {"error": "Rate limit exceeded. Please wait and try again.", "retry_after_seconds": 60},
                status_code=429
            )
    elif any(path.startswith(p) for p in RATE_LIMITED_PREFIXES):
        if _is_rate_limited(request, "global", *RATE_LIMIT_GLOBAL):
            return JSONResponse(
                {"error": "Rate limit exceeded. Please wait and try again.", "retry_after_seconds": 60},
                status_code=429
            )
    return await call_next(request)

# ==========================================
# REGISTER ROUTERS
# ==========================================
app.include_router(api_router)
app.include_router(admin_router, prefix="/api/admin")
app.include_router(payment_router, prefix="/api/payment")
app.include_router(video_router, prefix="/api/video")
app.include_router(social_router, prefix="/api/social")
app.include_router(ai_router, prefix="/api/ai")
app.include_router(telegram_router, prefix="/telegram")

# ==========================================
# ROOT ENDPOINTS
# ==========================================
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
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI Ultra v8.3 FINAL"}

@app.get("/ping")
@app.get("/api/ping")
async def ping():
    from datetime import datetime
    return {"status": "pong", "timestamp": datetime.now().isoformat(), "service": "Singh Ji AI Ultra v8.3"}

# ==========================================
# MAIN ENTRY
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=False
    )
