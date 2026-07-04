"""
🦁 SINGH JI AI ULTRA v7.0 - MERGED
Phase 1 Features + Lightweight Self-Ping + Lazy Loading
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import json
import asyncio
import aiohttp
import importlib.util
import inspect
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🦁 ALL 26 API KEYS
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
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # ➕ ADDED
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = os.getenv("TAVILY_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TZ = os.getenv("TZ", "Asia/Kolkata")

app = FastAPI(title="🦁 Singh Ji AI Ultra v7.0", version="7.0.0-merged")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

MODULES = {}
MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")

def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR):
        logger.warning(f"⚠️ modules/ not found at {MODULES_DIR}")
        return modules
    for item in os.listdir(MODULES_DIR):
        item_path = os.path.join(MODULES_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("__"):
            handler_path = os.path.join(item_path, "handler.py")
            if os.path.exists(handler_path):
                modules[item] = {"type": "folder", "path": handler_path}
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
        logger.error(f"❌ Failed {name}: {e}")
        return None

# 🦁 SELF-PING SYSTEM — Render ko sone nahi dega!
async def self_ping():
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://singhji-api.onrender.com/api/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    logger.info(f"🦁 Self-ping: {resp.status} | Render awake!")
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {e}")
        await asyncio.sleep(10 * 60)

@app.on_event("startup")
async def startup():
    count = len(discover_modules())
    logger.info(f"🦁 Phase 1 — {count} modules discovered!")
    logger.info("🦁 Self-ping enabled — Render will never sleep!")
    asyncio.create_task(self_ping())

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "name": "🦁 Singh Ji AI Ultra v7.0",
        "version": "7.0.0-merged",
        "modules_loaded": len(MODULES),
        "modules": list(MODULES.keys()),
        "status": "🦁 LIVE",
        "timestamp": datetime.now().isoformat()
    }

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health")  # ➕ ADDED
async def health_simple():
    return {"status": "ok", "version": "7.0", "service": "Singh Ji AI Ultra"}

@app.get("/api/status")
async def status():
    return {
        "name": "Singh Ji AI v7.0 Merged",
        "loaded": len(MODULES),
        "modules": list(MODULES.keys()),
        "status": "🦁 LIVE"
    }

# ✅ FIXED: Universal handler runner — SYNC + ASYNC
async def run_handler(module_name: str, request: Request):
    handler_func = MODULES[module_name]
    try:
        if asyncio.iscoroutinefunction(handler_func):
            result = await handler_func(request)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, handler_func, request)
        
        if isinstance(result, dict):
            if "statusCode" in result:
                status_code = result.get("statusCode", 200)
                headers = result.get("headers", {})
                body = result.get("body", "{}")
                if isinstance(body, str):
                    try:
                        body = json.loads(body)
                    except:
                        body = {"response": body}
                return JSONResponse(status_code=status_code, headers=headers, content=body)
            else:
                return JSONResponse(content=result)
        return result
    except Exception as e:
        logger.error(f"❌ Error in {module_name}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "module": module_name, "error": str(e)})

# 🦁 DYNAMIC MODULE ROUTER — Lazy Loading + Async Support
@app.api_route("/api/{module_name}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
async def router(request: Request, module_name: str):
    # Lazy load if not loaded
    if module_name not in MODULES:
        all_modules = discover_modules()
        if module_name in all_modules:
            handler = load_module(module_name, all_modules[module_name])
            if handler:
                MODULES[module_name] = handler
                logger.info(f"✅ Lazy loaded: {module_name}")
            else:
                return JSONResponse(status_code=404, content={
                    "status": "error", "message": f"'{module_name}' failed to load"
                })
        else:
            return JSONResponse(status_code=404, content={
                "status": "error", "message": f"'{module_name}' not found",
                "available": list(discover_modules().keys())
            })
    
    return await run_handler(module_name, request)

# 🦁 TELEGRAM WEBHOOK
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        message = data.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        
        logger.info(f"📩 Telegram: {text} from chat {chat_id}")
        
        if text == '/start':
            reply = "🦁 <b>Singh Ji AI Bot</b>\n\nShuruwat ho gayi!\n\nCommands:\n/start — Shuruwat\n/help — Madad\n/status — System check"
        elif text == '/help':
            reply = "🦁 <b>Madad</b>\n\n/start — Bot shuru\n/status — API status\nKuch bhi likho — Main jawab dunga!"
        elif text == '/status':
            reply = "🟢 <b>Singh Ji AI Status</b>\n\n✅ Bot Active\n✅ API Connected\n🦁 Singh Ji AI v7.0"
        else:
            reply = f"🦁 Aapne likha: <b>{text}</b>\n\nMain abhi sirf commands samajhta hoon:\n/start, /help, /status"
        
        if TELEGRAM_TOKEN and chat_id:
            import requests
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": reply,
                "parse_mode": "HTML"
            }, timeout=10)
            logger.info(f"✅ Reply sent to {chat_id}")
        
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return JSONResponse(status_code=200, content={"status": "ok"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
