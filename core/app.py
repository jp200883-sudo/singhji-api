"""
🦁 SINGH JI AI ULTRA v7.0 - LIGHTWEIGHT + NEWS SCHEDULER
Lazy Loading + Background Jobs
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

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

app = FastAPI(title="🦁 Singh Ji AI Ultra v7.0", version="7.0.0-light")

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

@app.on_event("startup")
async def startup():
    logger.info("🦁 Singh Ji AI v7.0 started")
    # News scheduler auto-load होगा module से

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"name": "🦁 Singh Ji AI Ultra v7.0", "version": "7.0.0-light", "status": "🦁 LIVE", "timestamp": datetime.now().isoformat()}

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def status():
    return {"loaded": len(MODULES), "modules": list(MODULES.keys()), "status": "🦁 LIVE"}

# 🦁 TELEGRAM WEBHOOK
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📩 Telegram: {data.get('message', {}).get('text', 'no text')}")
        
        if "telegram_bot" in MODULES:
            return await MODULES["telegram_bot"](request)
        
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return JSONResponse(status_code=200, content={"status": "ok"})

# 🦁 LAZY LOAD ROUTER
@app.api_route("/api/{module_name}", methods=["GET", "POST", "HEAD"])
async def router(request: Request, module_name: str):
    if module_name not in MODULES:
        all_modules = discover_modules()
        if module_name in all_modules:
            handler = load_module(module_name, all_modules[module_name])
            if handler:
                MODULES[module_name] = handler
                logger.info(f"✅ Lazy loaded: {module_name}")
            else:
                return JSONResponse(status_code=404, content={"status": "error", "message": f"'{module_name}' failed to load"})
        else:
            return JSONResponse(status_code=404, content={"status": "error", "message": f"'{module_name}' not found"})
    
    try:
        return await MODULES[module_name](request)
    except Exception as e:
        logger.error(f"Error {module_name}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "module": module_name, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
