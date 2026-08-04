import time
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# ---- अब सारे imports core से होंगे ----
from core.config import config
from core.database import supabase
from core.cache import cache_set, cache_get, cache_clear
from core.memory import save_memory, get_memory, get_all_memories
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message, format_telegram_message

# ---- Modules loader (import logic) ----
from modules.ai_chat.handler import router as ai_chat_router
from modules.mandi.handler import router as mandi_router
# ... इसी तरह सारे modules के routers import करें ...

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Singh Ji AI ULTRA v8.3 Starting...")
    yield
    # Shutdown
    logger.info("👋 Shutting down...")

app = FastAPI(title="Singh Ji AI ULTRA", version="8.3", lifespan=lifespan)

# ---- Middleware ----
@app.middleware("http")
async def rate_limit_middleware_wrapper(request: Request, call_next):
    rate_limit_middleware(request)
    response = await call_next(request)
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
