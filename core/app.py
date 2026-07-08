"""
🦁 SINGH JI AI ULTRA v7.0 - core/app.py
Main FastAPI App — सब Routers यहां Register होते हैं!
"""

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import os
import sys
import json
import asyncio
import aiohttp
import requests 
import importlib.util
from datetime import datetime
import logging

# 🧠 TRISHUL MEMORY ROUTER — TOP पे IMPORT
from modules.trishul.handler import router as trishul_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

MODULES = {}
FASTAPI_ROUTERS = {}
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
            
            router = getattr(module, "router", None)
            handler = getattr(module, "handler", None)
            
            if router and isinstance(router, APIRouter):
                return {"type": "router", "router": router}
            elif handler:
                return {"type": "handler", "handler": handler}
            else:
                return None
                
        else:
            spec = importlib.util.spec_from_file_location(name, info["path"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            handler = getattr(module, "handler", None)
            return {"type": "handler", "handler": handler} if handler else None
            
    except Exception as e:
        logger.error(f"Failed {name}: {e}")
        return None

async def self_ping():
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://singhji-api.onrender.com/api/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    logger.info(f"🦁 Self-ping: {resp.status}")
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {e}")
        await asyncio.sleep(10 * 60)

def create_app():
    app = FastAPI(
        title="🦁 Singh Ji AI Ultra v7.0",
        version="7.0.0-light"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # 🧠 TRISHUL MEMORY — REGISTER HERE (CORS के बाद!)
    app.include_router(trishul_router, prefix="/api/memory", tags=["Trishul Memory"])
    logger.info("🧠 Trishul Memory Router Registered!")
    
    # AUTO-DISCOVER OTHER MODULES
    all_modules = discover_modules()
    loaded_handlers = 0
    loaded_routers = 0
    skipped = []
    
    for name, info in all_modules.items():
        # Skip trishul (already loaded)
        if name == "trishul":
            continue
            
        result = load_module(name, info)
        if result:
            if result["type"] == "router":
                FASTAPI_ROUTERS[name] = result["router"]
                app.include_router(result["router"], prefix=f"/api/{name}", tags=[name])
                loaded_routers += 1
                logger.info(f"✅ Router: {name}")
            else:
                MODULES[name] = result["handler"]
                loaded_handlers += 1
                logger.info(f"✅ Handler: {name}")
        else:
            skipped.append(name)
            logger.warning(f"⚠️ Skipped {name}: no router/handler")
    
    logger.info(f"🦁 Started — {loaded_handlers} handlers + {loaded_routers} routers")
    if skipped:
        logger.warning(f"⚠️ Skipped: {', '.join(skipped)}")
    
    # ROOT ENDPOINTS
    @app.api_route("/", methods=["GET", "HEAD"])
    async def root():
        return {
            "name": "🦁 Singh Ji AI Ultra v7.0", 
            "version": "7.0.0-light",
            "trishul": "🧠 Active",
            "modules_loaded": len(MODULES),
            "routers_loaded": len(FASTAPI_ROUTERS),
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
            "loaded_handlers": len(MODULES), 
            "loaded_routers": len(FASTAPI_ROUTERS),
            "trishul_active": True,
            "handlers": list(MODULES.keys()),
            "routers": list(FASTAPI_ROUTERS.keys()),
            "status": "🦁 LIVE"
        }

    @app.post("/telegram/webhook")
    async def telegram_webhook(request: Request):
        try:
            data = await request.json()
            message = data.get('message', {})
            text = message.get('text', '')
            chat_id = message.get('chat', {}).get('id')
            
            if text == '/start':
                reply = "🦁 Singh Ji AI Bot"
            elif text == '/help':
                reply = "🦁 Madad\n/start — Shuru\n/status — Check"
            elif text == '/status':
                reply = "🟢 Active"
            else:
                reply = f"🦁 Aapne: {text}"
            
            if TELEGRAM_TOKEN and chat_id:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"}, timeout=10)
            
            return JSONResponse(status_code=200, content={"status": "ok"})
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return JSONResponse(status_code=200, content={"status": "ok"})

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
            logger.error(f"❌ Error: {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/api/{module_name}")
    async def redirect_slash(module_name: str):
        if module_name in FASTAPI_ROUTERS:
            return RedirectResponse(url=f"/api/{module_name}/", status_code=307)
        return JSONResponse(status_code=404, content={"error": "Not found"})

    @app.api_route("/api/{module_name}/", methods=["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"])
    async def lazy_router(request: Request, module_name: str):
        if module_name not in MODULES:
            all_modules = discover_modules()
            if module_name in all_modules:
                result = load_module(module_name, all_modules[module_name])
                if result and result["type"] == "handler":
                    MODULES[module_name] = result["handler"]
                    logger.info(f"✅ Lazy loaded: {module_name}")
                else:
                    return JSONResponse(status_code=404, content={"error": f"'{module_name}' not a handler"})
            else:
                return JSONResponse(status_code=404, content={"error": f"'{module_name}' not found"})
        
        return await run_handler(module_name, request)

    return app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
