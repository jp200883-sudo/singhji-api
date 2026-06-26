# core/app.py — Singh Ji AI Ultra v5.0
# Fix: Underscores added back to module paths
# Date: 26 June 2026

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import importlib
import sys
import os

app = FastAPI(
    title="Singh Ji AI Ultra v5.0",
    description="भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
    version="5.0.0"
)

# ✅ CORS — Allow ALL origins (GitHub Pages, localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODULE REGISTRY (with underscores!) ==========
# Module path → API prefix
MODULES = {
    "modules.language": "/api/language",
    "modules.telegram_bot": "/api/telegram",      # ✅ underscore
    "modules.plant_id": "/api/plant",              # ✅ underscore
    "modules.supabase_memory": "/api/memory",      # ✅ underscore
    "modules.adminpanel": "/api/admin",
}

# ========== HEALTH CHECK ==========
@app.get("/api/health")
def health():
    return {"status": "🦁 Singh Ji AI Ultra v5.0 is LIVE!", "timestamp": str(__import__("datetime").datetime.now())}

@app.get("/api/status")
def status():
    loaded = []
    failed = []
    for mod_name, prefix in MODULES.items():
        try:
            mod = importlib.import_module(mod_name)
            loaded.append({"module": mod_name, "prefix": prefix, "status": "✅ Loaded"})
        except Exception as e:
            failed.append({"module": mod_name, "prefix": prefix, "error": str(e)})
    return {
        "app": "Singh Ji AI Ultra v5.0",
        "loaded_modules": loaded,
        "failed_modules": failed,
        "total": len(MODULES),
        "working": len(loaded),
        "broken": len(failed)
    }

# ========== DEBUG ENDPOINT ==========
@app.get("/api/debug/{module_name}")
def debug_module(module_name: str):
    """Inspect any module — returns file path, classes, functions, errors"""
    import inspect
    result = {
        "requested": module_name,
        "module_path": None,
        "file": None,
        "exists": False,
        "classes": [],
        "functions": [],
        "routes": [],
        "error": None
    }
    try:
        # Try with underscore variations
        candidates = [
            f"modules.{module_name}",
            f"modules.{module_name.replace('_', '')}",
        ]
        for cand in candidates:
            try:
                mod = importlib.import_module(cand)
                result["module_path"] = cand
                result["file"] = getattr(mod, "__file__", "Unknown")
                result["exists"] = True
                for name, obj in inspect.getmembers(mod):
                    if inspect.isclass(obj):
                        result["classes"].append(name)
                    elif inspect.isfunction(obj):
                        result["functions"].append(name)
                # Check for FastAPI router
                if hasattr(mod, "router"):
                    result["routes"] = [r.path for r in mod.router.routes]
                break
            except ImportError:
                continue
        if not result["exists"]:
            result["error"] = f"Module '{module_name}' not found in modules/"
    except Exception as e:
        result["error"] = str(e)
    return result

# ========== AUTO-LOAD ALL MODULES ==========
def load_modules():
    for mod_name, prefix in MODULES.items():
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "router"):
                app.include_router(mod.router, prefix=prefix)
                print(f"✅ Loaded: {mod_name} → {prefix}")
            else:
                print(f"⚠️ No router in: {mod_name}")
        except Exception as e:
            print(f"❌ Failed: {mod_name} → {e}")

# Load on startup
load_modules()

# ========== ROOT ==========
@app.get("/")
def root():
    return {
        "name": "Singh Ji AI Ultra v5.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप",
        "status": "🦁 LIVE",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "language": "/api/language",
            "telegram": "/api/telegram",
            "plant": "/api/plant",
            "memory": "/api/memory",
            "admin": "/api/admin",
            "debug": "/api/debug/{module}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
