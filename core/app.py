"""
🦁 SINGH JI AI ULTRA v7.0 - LIGHTWEIGHT + SELF-PING
Lazy Loading + Auto Ping (Har 10 min mein Render ko jagaye)
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import json
import asyncio
import aiohttp
import requests 
import importlib.util
import inspect  
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

app = FastAPI(title="🦁 Singh Ji AI Ultra v7.0", version="7.0.0-light")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

MODULES = {}
MODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "modules")

def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR): 
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
        logger.error(f"Failed {name}: {e}")
        return None

# ============================================================
# 🦁 SELF-PING SYSTEM — Render ko sone nahi dega!
# ============================================================
async def self_ping():
    """Har 10 minute mein Render ko ping karega — server hamesha live"""
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
    logger.info("🦁 Singh Ji AI v7.0 started")
    logger.info("🦁 Self-ping enabled — Render will never sleep!")
    asyncio.create_task(self_ping())

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "name": "🦁 Singh Ji AI Ultra v7.0", 
        "version": "7.0.0-light", 
        "status": "🦁 LIVE", 
        "timestamp": datetime.now().isoformat()
    }

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_simple():
    return {"status": "ok", "version": "7.0", "service": "Singh Ji AI Ultra"}

@app.get("/api/status")
async def status():
    return {
        "loaded": len(MODULES), 
        "modules": list(MODULES.keys()), 
        "status": "🦁 LIVE"
    }

# ============================================================
# 🦁 RUN HANDLER — SYNC + ASYNC Support
# ============================================================
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

# ============================================================
# 🦁 TELEGRAM WEBHOOK
# ============================================================
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

# ============================================================
# 🦁 LAZY LOAD ROUTER — FIXED!
# ============================================================
@app.api_route("/api/{module_name}", methods=["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"])
async def router(request: Request, module_name: str):
    if module_name not in MODULES:
        all_modules = discover_modules()
        if module_name in all_modules:
            handler = load_module(module_name, all_modules[module_name])
            if handler:
                MODULES[module_name] = handler
                logger.info(f"✅ Lazy loaded: {module_name}")
            else:
                return JSONResponse(
                    status_code=404, 
                    content={"status": "error", "message": f"'{module_name}' failed to load"}
                )
        else:
            return JSONResponse(
                status_code=404, 
                content={"status": "error", "message": f"'{module_name}' not found"}
            )
    
    return await run_handler(module_name, request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
