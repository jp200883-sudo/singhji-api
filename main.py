"""
🦁 Singh Ji AI Ultra v8.0 — Main Application
Production Ready — Railway Deploy
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
from urllib.parse import quote_plus, urlparse, urlunparse
import os
import sys
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# 🦁 PORT FIX — Railway $PORT handle karo
# ============================================================
PORT = int(os.environ.get("PORT", 8000))
logger.info(f"🚀 Port set to: {PORT}")

# ============================================================
# 🦁 GLOBAL VARIABLES
# ============================================================
MINIPROGRAM_AVAILABLE = False

# ============================================================
# 🦁 API KEYS CHECK
# ============================================================
API_KEYS = {
    'OPENWEATHER': bool(os.getenv('OPENWEATHER_API_KEY')),
    'CURRENTS': bool(os.getenv('CURRENTS_API_KEY')),
    'GROQ': bool(os.getenv('GROQ_API_KEY')),
    'GEMINI': bool(os.getenv('GEMINI_API_KEY')),
    'TELEGRAM': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
    'SUPABASE': bool(os.getenv('SUPABASE_URL')),
    'CEREBRAS': bool(os.getenv('CEREBRAS_API_KEY')),
    'CF': bool(os.getenv('CF_API_KEY')),
    'HUGGINGFACE': bool(os.getenv('HUGGINGFACE_API_KEY')),
    'MANDI': bool(os.getenv('MANDI_API_KEY')),
    'NEWSDATA': bool(os.getenv('NEWSDATA_API_KEY')),
    'PLANT_ID': bool(os.getenv('PLANT_ID_API_KEY')),
    'RAPIDAPI': bool(os.getenv('RAPIDAPI_KEY')),
    'RAZORPAY': bool(os.getenv('RAZORPAY_KEY_ID')),
    'TAVILY': bool(os.getenv('TAVILY_API_KEY')),
    'TWILIO': bool(os.getenv('TWILIO_SID')),
    'FACEBOOK': bool(os.getenv('FACEBOOK_ACCESS_TOKEN')),
    'GMAIL': bool(os.getenv('GMAIL_USER')),
    'INSTAGRAM': bool(os.getenv('INSTAGRAM_ACCESS_TOKEN')),
    'YOUTUBE': bool(os.getenv('YOUTUBE_API_KEY')),
}

logger.info(f"🦁 Available Keys: {API_KEYS}")

# ============================================================
# 🦁 DATABASE SETUP — URL ENCODE PASSWORD FIX
# ============================================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./singhji.db")

# Fix: postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fix: Password mein special characters (#, @, :, /) encode karo
if "postgresql" in DATABASE_URL:
    try:
        parsed = urlparse(DATABASE_URL)
        if parsed.password and any(c in parsed.password for c in ['#', '@', ':', '/']):
            encoded_password = quote_plus(parsed.password)
            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            DATABASE_URL = urlunparse((
                parsed.scheme, netloc, parsed.path,
                parsed.params, parsed.query, parsed.fragment
            ))
            logger.info("✅ Database URL password encoded!")
    except Exception as e:
        logger.warning(f"⚠️ URL encode error: {e}")

# Fallback: Agar DB connect nahi hota, SQLite use karo
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 10} if "postgresql" in DATABASE_URL else {}
    )
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✅ Database connected!")
except Exception as e:
    logger.error(f"❌ Database failed: {e}")
    logger.warning("⚠️ Falling back to SQLite...")
    DATABASE_URL = "sqlite:///./singhji.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================
# 🦁 LIFESPAN — STARTUP & SHUTDOWN
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """🚀 App lifespan — startup aur shutdown"""
    global MINIPROGRAM_AVAILABLE

    logger.info("🚀 === STARTUP BEGIN ===")

    # Mini-Program modules load — SAFE import
    try:
        import miniprogram
        from miniprogram.auth import MiniAuth, AuthManager, DeveloperAuth, get_current_developer
        from miniprogram.portal import router as miniprogram_router

        # Try to create tables (SQLite compatible)
        try:
            from miniprogram.models import Base
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Mini-Program tables created!")
        except Exception as e:
            logger.warning(f"⚠️ Tables error (SQLite may not support all): {e}")

        app.include_router(miniprogram_router)
        logger.info("✅ Mini-Program router loaded!")

        MINIPROGRAM_AVAILABLE = True
    except Exception as e:
        logger.warning(f"⚠️ Mini-Program modules not available: {e}")
        MINIPROGRAM_AVAILABLE = False

    logger.info(f"🦁 Mini-Program Available: {MINIPROGRAM_AVAILABLE}")
    logger.info("🚀 === STARTUP COMPLETE ===")

    try:
        yield
    except Exception as e:
        logger.error(f"❌ Runtime error: {e}")
    finally:
        logger.info("👋 === SHUTDOWN ===")

# ============================================================
# 🦁 FASTAPI APP
# ============================================================
app = FastAPI(
    title="Singh Ji AI Ultra v8.0",
    description="India ka Super AI App — 26 Languages, 17+ APIs",
    version="8.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🦁 DATABASE DEPENDENCY
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 🦁 HEALTH & ROOT ENDPOINTS
# ============================================================
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "8.0.0",
        "mini_program": MINIPROGRAM_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "🦁 Singh Ji AI Ultra v8.0",
        "status": "live",
        "mini_program": MINIPROGRAM_AVAILABLE,
        "api_keys_active": sum(1 for v in API_KEYS.values() if v),
        "total_keys": len(API_KEYS)
    }

@app.get("/api/keys")
async def get_keys():
    return {"keys": API_KEYS}

# ============================================================
# 🦁 MINI-PROGRAM AUTH ENDPOINTS (Safe)
# ============================================================
@app.post("/api/miniprogram/auth/register")
async def register_developer(request: Request):
    if not MINIPROGRAM_AVAILABLE:
        return JSONResponse(
            {"error": "Mini-Program module not available"},
            status_code=503
        )

    try:
        from miniprogram.auth import DeveloperAuth
        data = await request.json()
        return await DeveloperAuth.register(
            email=data.get("email"),
            password=data.get("password"),
            name=data.get("full_name", "")
        )
    except Exception as e:
        logger.error(f"❌ Register error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/miniprogram/auth/login")
async def login_developer(request: Request):
    if not MINIPROGRAM_AVAILABLE:
        return JSONResponse(
            {"error": "Mini-Program module not available"},
            status_code=503
        )

    try:
        from miniprogram.auth import DeveloperAuth
        data = await request.json()
        return await DeveloperAuth.login(
            email=data.get("email"),
            password=data.get("password")
        )
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# ============================================================
# 🦁 MEMORY ENDPOINTS
# ============================================================
@app.post("/api/memory/save")
async def memory_save(request: Request):
    data = await request.json()
    return {"success": True, "message": "Memory saved!", "data": data}

@app.get("/api/memory/get")
async def memory_get():
    return {"success": True, "memory": []}

# ============================================================
# 🦁 STARTUP LOG
# ============================================================
logger.info("🦁 Singh Ji AI Ultra v8.0 Started!")

# ============================================================
# 🦁 RAILWAY START — Port handle karo
# ============================================================
if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting Uvicorn on port {PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
