"""
🦁 Singh Ji AI Ultra v8.0 — Master Main.py
===========================================
modules/ + Root files dono auto-detect!
Railway $PORT fix, health check, CORS enabled.
"""

import os
import sys
import json
import importlib.util
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("SinghJi")

# ========== CONFIG ==========
MODULES_DIR = Path(__file__).parent / "modules"
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"
ROOT_DIR = Path(__file__).parent

PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")

# ========== REGISTRY ==========
loaded_modules = {}
root_modules = {}

# ========== ROOT FILES MAPPING ==========
# Kaunsi root file = kaunsa module name
ROOT_FILE_MAP = {
    "youtube_auto_upload.py": "youtube",
    "instagram_auto_post.py": "instagram",
    "facebook_long_token.py": "facebook",
    "auto_account.py": "auto_account",
    "auto_monetize.py": "auto_monetize",
    "trend_analysis.py": "trend_analysis",
    "agent_swarm_system.py": "swarm",
    "singhji_visual.py": "visual",
    "api.py": "api_core"
}

def discover_modules():
    """modules/ folder scan karo"""
    global loaded_modules
    if not MODULES_DIR.exists():
        logger.warning(f"Modules dir nahi mila: {MODULES_DIR}")
        return
    
    for module_path in sorted(MODULES_DIR.iterdir()):
        if not module_path.is_dir():
            continue
        module_name = module_path.name
        handler_file = module_path / "handler.py"
        
        if not handler_file.exists():
            continue
        
        try:
            spec = importlib.util.spec_from_file_location(f"modules.{module_name}", handler_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"modules.{module_name}"] = module
            spec.loader.exec_module(module)
            
            router = getattr(module, "router", None)
            handler = getattr(module, "handler", None)
            process = getattr(module, "process", None)
            
            loaded_modules[module_name] = {
                "path": str(module_path),
                "module": module,
                "router": router,
                "handler": handler,
                "process": process,
                "source": "modules_folder"
            }
            logger.info(f"✅ Module loaded: {module_name}")
        except Exception as e:
            logger.error(f"❌ {module_name} load fail: {e}")

def discover_root_files():
    """Root files ko bhi module ki tarah load karo"""
    global root_modules
    for filename, module_name in ROOT_FILE_MAP.items():
        file_path = ROOT_DIR / filename
        if not file_path.exists():
            logger.warning(f"⚠️ Root file missing: {filename}")
            continue
        
        try:
            spec = importlib.util.spec_from_file_location(f"root.{module_name}", file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"root.{module_name}"] = module
            spec.loader.exec_module(module)
            
            router = getattr(module, "router", None)
            handler = getattr(module, "handler", None)
            process = getattr(module, "process", None)
            
            # Agar handler nahi hai toh wrapper banao
            if not handler and not router:
                handler = create_root_handler(module_name, module)
            
            root_modules[module_name] = {
                "path": str(file_path),
                "module": module,
                "router": router,
                "handler": handler,
                "process": process,
                "source": "root_file"
            }
            loaded_modules[module_name] = root_modules[module_name]
            logger.info(f"✅ Root file loaded as module: {module_name} ← {filename}")
        except Exception as e:
            logger.error(f"❌ Root file {filename} load fail: {e}")

def create_root_handler(name, module):
    """Root file ke liye generic handler wrapper"""
    async def generic_handler(request_data=None):
        if not request_data:
            request_data = {}
        action = request_data.get("action", "status")
        
        # Common functions check karo
        for func_name in ["upload_video", "post_to_instagram", "post_to_facebook", 
                          "create_account", "monetize_content", "analyze_trends",
                          "execute", "generate_visual"]:
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                try:
                    if action == "status":
                        return {
                            "status": "success",
                            "module": name,
                            "source": "root_file",
                            "functions": [f for f in dir(module) if not f.startswith("_")],
                            "message": f"🦁 {name} module active!"
                        }
                    result = func(request_data)
                    return {"status": "success", "module": name, "action": action, "result": result}
                except Exception as e:
                    return {"status": "error", "module": name, "message": str(e)}
        
        return {
            "status": "success",
            "module": name,
            "source": "root_file",
            "functions": [f for f in dir(module) if not f.startswith("_")],
            "message": f"🦁 {name} module active! (no handler found, use specific function)"
        }
    
    return generic_handler

# ========== LIFESPAN ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Singh Ji AI Ultra v8.0 starting...")
    discover_modules()
    discover_root_files()
    mount_routers() 
    logger.info(f"📦 Total modules: {len(loaded_modules)}")
    yield
    logger.info("🛑 Shutting down...")
# ========== APP ==========
app = FastAPI(
    title="🦁 Singh Ji AI Ultra v8.0",
    description="India ka Super App — modules/ + Root files auto-detect",
    version="8.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ========== ENDPOINTS ==========
@app.get("/")
async def root():
    return {
        "name": "Singh Ji AI Ultra v8.0",
        "version": "8.0.0",
        "status": "LIVE",
        "modules": len(loaded_modules),
        "modules_loaded": list(loaded_modules.keys()),
        "agents_active": 0,
        "timestamp": str(__import__('datetime').datetime.now())
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_modules": list(loaded_modules.keys()),
        "inactive_modules": [],
        "module_details": {
            name: {
                "status": "active",
                "source": info["source"],
                "has_router": info["router"] is not None,
                "has_handler": info["handler"] is not None
            }
            for name, info in loaded_modules.items()
        }
    }

@app.get("/api/modules")
async def list_modules():
    return {
        "total": len(loaded_modules),
        "modules": [
            {
                "name": name,
                "source": info["source"],
                "has_router": info["router"] is not None,
                "has_handler": info["handler"] is not None
            }
            for name, info in loaded_modules.items()
        ]
    }

# ========== MODULE HANDLER ==========
@app.get("/modules/{module_name}")
async def module_get(module_name: str, request: Request):
    if module_name not in loaded_modules:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' nahi mila!")
    
    info = loaded_modules[module_name]
    
    if info["router"]:
        raise HTTPException(status_code=400, detail="Use router endpoint directly")
    
    if info["handler"]:
        try:
            body = dict(request.query_params)
            result = await info["handler"](body) if __import__('inspect').iscoroutinefunction(info["handler"]) else info["handler"](body)
            return JSONResponse(content={"module": module_name, "data": result})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content={"module": module_name, "status": "loaded"})

@app.post("/modules/{module_name}")
async def module_post(module_name: str, request: Request):
    if module_name not in loaded_modules:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' nahi mila!")
    
    info = loaded_modules[module_name]
    
    try:
        body = await request.json()
    except:
        body = {}
    
    if info["handler"]:
        try:
            result = await info["handler"](body) if __import__('inspect').iscoroutinefunction(info["handler"]) else info["handler"](body)
            return JSONResponse(content={"module": module_name, "data": result})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content={"module": module_name, "status": "loaded"})

# ========== MOUNT ROUTERS ==========
def mount_routers():
    for name, info in loaded_modules.items():
        if info["router"]:
            try:
                prefix = f"/modules/{name}"
                app.include_router(info["router"], prefix=prefix, tags=[name])
                logger.info(f"🔗 Router mounted: {prefix}")
            except Exception as e:
                logger.error(f"❌ Router mount fail {name}: {e}")

# ========== ADMIN ==========
@app.get("/admin")
async def admin_dashboard():
    admin_file = TEMPLATES_DIR / "admin.html"
    if admin_file.exists():
        return HTMLResponse(content=admin_file.read_text())
    return JSONResponse(content={"admin": "Singh Ji AI", "modules": list(loaded_modules.keys())})

# ========== STARTUP ==========
if __name__ == "__main__":
    mount_routers()
    logger.info(f"🚀 Starting on {HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False, log_level="info")
