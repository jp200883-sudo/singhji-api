# api.py — Singh Ji AI Ultra v7.0 — FastAPI Module Loader
# core/modules/ se dono type load karta hai
# Bharat to the World 🇮🇳

import os
import sys
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# ─── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ─── FastAPI App ─────────────────────────────────────────
app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="Bharat to the World 🇮🇳",
    version="7.0.0"
)

# ─── CORS ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Module Registry ─────────────────────────────────────
MODULES: Dict[str, Dict[str, Any]] = {}

# ─── Discover Modules ────────────────────────────────────
def discover_modules(modules_dir: str = "core/modules") -> list:
    modules_path = Path(modules_dir)
    
    if not modules_path.exists():
        logger.error(f"❌ modules folder NAHI mila: {modules_path.absolute()}")
        return []
    
    discovered = []
    
    for item in modules_path.iterdir():
        if item.name.startswith('_') or item.name.startswith('.'):
            continue
            
        # Folder module
        if item.is_dir():
            init_file = item / "__init__.py"
            handler_file = item / "handler.py"
            if init_file.exists() or handler_file.exists():
                discovered.append(item.name)
                logger.info(f"📁 Folder module: {item.name}")
        
        # File module
        elif item.is_file() and item.suffix == '.py':
            discovered.append(item.stem)
            logger.info(f"📄 File module: {item.stem}")
    
    logger.info(f"✅ Total mila: {len(discovered)} modules")
    return discovered

# ─── Load Single Module ─────────────────────────────────
def load_module(module_name: str, modules_dir: str = "core/modules") -> Optional[Dict]:
    modules_path = Path(modules_dir)
    module_path = modules_path / module_name
    info = {"name": module_name, "type": None, "handler": None, "status": "loading"}
    
    try:
        if module_path.is_dir():
            info["type"] = "folder"
            init_file = module_path / "__init__.py"
            handler_file = module_path / "handler.py"
            target = init_file if init_file.exists() else handler_file
            
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(target)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                info["handler"] = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                info["status"] = "loaded"
                logger.info(f"✅ Folder loaded: {module_name}")
        
        elif module_path.is_file() and module_path.suffix == '.py':
            info["type"] = "file"
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(module_path)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                info["handler"] = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                info["status"] = "loaded"
                logger.info(f"✅ File loaded: {module_name}")
        
        else:
            info["status"] = "not_found"
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
        logger.error(f"❌ Fail: {module_name} — {e}")
    
    return info

# ─── Init All Modules ───────────────────────────────────
def init_modules(modules_dir: str = "core/modules"):
    global MODULES
    MODULES = {}
    
    logger.info("=" * 50)
    logger.info("🚀 Singh Ji AI Ultra v7.0 — Module Loader")
    logger.info("🇮🇳 Bharat to the World")
    logger.info("=" * 50)
    
    discovered = discover_modules(modules_dir)
    
    for name in discovered:
        mod_info = load_module(name, modules_dir)
        if mod_info and mod_info["status"] == "loaded":
            MODULES[name] = mod_info
    
    logger.info("=" * 50)
    logger.info(f"📊 LOADED: {len(MODULES)}/{len(discovered)}")
    logger.info(f"📋 Active: {list(MODULES.keys())}")
    logger.info("=" * 50)

# ─── Startup Event ──────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_modules()

# ════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════

@app.get("/")
async def home():
    return {
        "status": "🟢 LIVE",
        "name": "Singh Ji AI Ultra v7.0",
        "tagline": "Bharat to the World 🇮🇳",
        "modules_loaded": len(MODULES),
        "modules": list(MODULES.keys()),
        "timestamp": datetime.utcnow().isoformat(),
        "server": "Render"
    }

@app.get("/api/modules")
async def list_modules():
    return {
        "total": len(MODULES),
        "modules": [
            {
                "name": name,
                "type": info.get("type"),
                "has_handler": info.get("handler") is not None
            }
            for name, info in MODULES.items()
        ]
    }

@app.api_route("/api/{module_name}", methods=["GET", "POST"])
async def module_route(module_name: str, request: Request):
    if module_name not in MODULES:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{module_name}' nahi mila. Available: {list(MODULES.keys())}"
        )
    
    handler = MODULES[module_name].get("handler")
    if not handler:
        raise HTTPException(status_code=500, detail=f"Module '{module_name}' mein handler nahi hai")
    
    # Request data prepare
    body = await request.body()
    try:
        json_body = await request.json() if body else {}
    except:
        json_body = {}
    
    req_data = {
        "method": request.method,
        "args": dict(request.query_params),
        "json": json_body,
        "headers": dict(request.headers),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = handler(req_data)
        return response
    except Exception as e:
        logger.error(f"❌ {module_name} error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "modules": len(MODULES),
        "version": "v7.0"
    }
