"""
🦁 SINGH JI AI ULTRA v7.0 - PHASE 1 (15 MODULES)
Dynamic Module Loader
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import importlib.util
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🦁 SINGH JI AI ULTRA v7.0 - ALL 26 API KEYS
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MAGIC_HOUR_API_KEY = os.getenv("MAGIC_HOUR_API_KEY")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
PLANT_ID_API = os.getenv("PLANT_ID_API")
PLANT_ID_URL = os.getenv("PLANT_ID_URL")
PYTHON_VERSION = os.getenv("PYTHON_VERSION", "3.11")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = os.getenv("TAVILY_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TZ = os.getenv("TZ", "Asia/Kolkata")

app = FastAPI(title="🦁 Singh Ji AI Ultra v7.0", version="7.0.0-phase1")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MODULES = {}
MODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "modules")

def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR): return modules
    for item in os.listdir(MODULES_DIR):
        item_path = os.path.join(MODULES_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("__"):
            handler_path = os.path.join(item_path, "handler.py")
            if os.path.exists(handler_path): modules[item] = {"type": "folder", "path": handler_path}
        elif item.endswith(".py") and not item.startswith("__"):
            modules[item[:-3]] = {"type": "file", "path": item_path}
    return modules

def load_module(name, info):
    try:
        if info["type"] == "folder":
            spec = importlib.util.spec_from_file_location(f"modules.{name}", info["path"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"modules.{name}"] = module
            spec.loader.exec_module(module)
            return getattr(module, "handler", None)
        else:
            spec = importlib.util.spec_from_file_location(name, info["path"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return getattr(module, "handler", None)
    except Exception as e:
        logger.error(f"Failed {name}: {e}")
        return None

def load_all_modules():
    global MODULES
    for name, info in discover_modules().items():
        handler = load_module(name, info)
        if handler:
            MODULES[name] = handler
            logger.info(f"✅ {name}")
        else:
            logger.warning(f"⚠️ {name}")
    return len(MODULES)

@app.on_event("startup")
async def startup():
    logger.info(f"🦁 Phase 1 - {load_all_modules()} modules loaded!")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"name": "🦁 Singh Ji AI Ultra v7.0", "version": "7.0.0-phase1", "modules_loaded": len(MODULES), "status": "🦁 LIVE", "timestamp": datetime.now().isoformat()}

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def status():
    return {"name": "Singh Ji AI v7.0 Phase 1", "loaded": len(MODULES), "modules": list(MODULES.keys()), "status": "🦁 LIVE"}

# 🦁 TELEGRAM WEBHOOK - DEDICATED ROUTE (BEFORE generic router)
@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Telegram Bot Webhook Handler"""
    try:
        data = await request.json()
        logger.info(f"📩 Telegram webhook: {data.get('message', {}).get('text', 'no text')}")
        
        # Forward to telegram_bot module if loaded
        if "telegram_bot" in MODULES:
            return await MODULES["telegram_bot"](request)
        
        # Basic acknowledgment
        return JSONResponse(status_code=200, content={"status": "ok", "message": "Webhook received, telegram_bot module not loaded yet"})
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse(status_code=200, content={"status": "ok", "error": str(e)})

# Generic router - AFTER specific routes
@app.api_route("/api/{module_name}", methods=["GET", "POST", "HEAD"])
async def router(request: Request, module_name: str):
    if module_name not in MODULES:
        return JSONResponse(status_code=404, content={"status": "error", "message": f"'{module_name}' not found", "available": list(MODULES.keys())})
    try:
        return await MODULES[module_name](request)
    except Exception as e:
        logger.error(f"Error {module_name}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "module": module_name, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))