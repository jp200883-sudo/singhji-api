# ═══════════════════════════════════════════════════════
#   SINGH JI AI ULTRA v7.0 — app.py (CLEAN)
#   Dynamic module scanner + Auto-wrapper
#   37/37 modules load hone chahiye!
# ═══════════════════════════════════════════════════════

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import importlib.util
import sys
import inspect
from pathlib import Path
from typing import Dict, Any, Callable, Optional

# ========== FASTAPI APP ==========
app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="भारत से दुनिया तक — 220 भाषाएं, Glocal AI",
    version="7.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODULE REGISTRY ==========
MODULES: Dict[str, Dict] = {}
loaded_modules = []
failed_modules = {}


# ─── Auto Handler Wrapper ───────────────────────────────
def create_auto_handler(module_name: str, module_obj) -> Callable:
    def auto_handler(request_data: Any = None) -> Dict:
        functions = {
            name: func 
            for name, func in vars(module_obj).items()
            if callable(func) and not name.startswith('_')
        }
        main_func = None
        main_name = None
        for name, func in functions.items():
            if name not in ('handler', 'Handler', 'create_auto_handler', 'auto_handler'):
                main_func = func
                main_name = name
                break
        if main_func:
            try:
                sig = inspect.signature(main_func)
                if len(sig.parameters) > 0:
                    result = main_func(request_data)
                else:
                    result = main_func()
                return {
                    "module": module_name,
                    "status": "success",
                    "handler_type": "auto",
                    "function_called": main_name,
                    "data": result
                }
            except Exception as e:
                return {
                    "module": module_name,
                    "status": "error",
                    "handler_type": "auto",
                    "error": str(e),
                    "available_functions": list(functions.keys())
                }
        return {
            "module": module_name,
            "status": "success",
            "handler_type": "auto",
            "message": f"{module_name} active!",
            "available_functions": list(functions.keys())
        }
    return auto_handler


# ─── Load Single Module ─────────────────────────────────
def load_single_module(module_name: str, modules_dir: str = "modules") -> Optional[Dict]:
    modules_path = Path(modules_dir)
    module_path = modules_path / module_name
    info = {
        "name": module_name,
        "type": None,
        "handler": None,
        "router": None,
        "status": "loading"
    }
    try:
        if module_path.is_dir():
            info["type"] = "folder"
            init_file = module_path / "__init__.py"
            handler_file = module_path / "handler.py"
            target = init_file if init_file.exists() else handler_file
            if not target.exists():
                info["status"] = "not_found"
                info["error"] = "No __init__.py or handler.py"
                return info
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(target)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                info["router"] = getattr(mod, 'router', None)
                info["handler"] = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                info["status"] = "loaded"
                print(f"✅ Folder loaded: {module_name}")
        elif module_path.is_file() and module_path.suffix == '.py':
            info["type"] = "file"
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(module_path)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                info["router"] = getattr(mod, 'router', None)
                handler = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                if handler:
                    info["handler"] = handler
                    info["status"] = "loaded"
                    print(f"✅ File loaded (handler): {module_name}")
                else:
                    info["handler"] = create_auto_handler(module_name, mod)
                    info["status"] = "loaded"
                    print(f"✅ File loaded (auto-wrap): {module_name}")
        else:
            info["status"] = "not_found"
            info["error"] = "Not a valid module"
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
        print(f"❌ Fail: {module_name} — {e}")
    return info


# ─── Load All Modules ───────────────────────────────────
def load_all_modules(modules_dir: str = "modules") -> Dict[str, Dict]:
    modules_path = Path(modules_dir)
    loaded = {}
    print(f"🔍 Scanning: {modules_path.absolute()}")
    if not modules_path.exists():
        print(f"❌ Modules dir NOT FOUND!")
        return loaded
    all_items = list(modules_path.iterdir())
    print(f"🔍 Found {len(all_items)} items")
    for item in all_items:
        name = item.stem if item.is_file() else item.name
        if name.startswith('_') or name.startswith('.'):
            continue
        if item.is_file() and item.suffix != '.py':
            continue
        print(f"📦 Loading: {name} ({'folder' if item.is_dir() else 'file'})")
        info = load_single_module(name, modules_dir)
        loaded[name] = info
        if info["status"] == "loaded":
            MODULES[name] = info
            loaded_modules.append(name)
            if info["router"]:
                try:
                    app.include_router(info["router"], prefix=f"/api/{name}")
                    print(f"   🔗 Router mounted: /api/{name}")
                except Exception as e:
                    print(f"   ⚠️ Router mount failed: {e}")
        else:
            failed_modules[name] = info.get("error", "Unknown")
    total = len(loaded)
    success = sum(1 for v in loaded.values() if v["status"] == "loaded")
    failed = sum(1 for v in loaded.values() if v["status"] == "error")
    print(f"\n{'='*55}")
    print(f"🦁 SINGH JI AI v7.0 — MODULE LOAD SUMMARY")
    print(f"{'='*55}")
    print(f"📁 Total found:    {total}")
    print(f"✅ Loaded:         {success}")
    print(f"❌ Failed:         {failed}")
    print(f"🎯 Target:         37/37")
    print(f"{'='*55}\n")
    return loaded


# ========== STARTUP: LOAD ALL MODULES ==========
print("🚀 Singh Ji AI Ultra v7.0 starting...")
print("="*55)
modules_data = load_all_modules("modules")
print(f"✅ Startup complete! {len(loaded_modules)} modules active.")


# ========== UNIVERSAL API ENDPOINT ==========
@app.post("/api/{module_name}")
@app.get("/api/{module_name}")
async def universal_handler(module_name: str, request: Request):
    if module_name not in MODULES or MODULES[module_name]["status"] != "loaded":
        return JSONResponse(status_code=404, content={"error": f"Module '{module_name}' not found"})
    handler = MODULES[module_name].get("handler")
    if not handler:
        return JSONResponse(status_code=500, content={"error": f"No handler for '{module_name}'"})
    try:
        data = await request.json() if request.method == "POST" else dict(request.query_params)
    except:
        data = {}
    try:
        result = handler(data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ========== HEALTH & STATUS ==========
@app.get("/api/health")
def health():
    return {
        "status": "🦁 LIVE",
        "app": "Singh Ji AI Ultra v7.0",
        "version": "7.0.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप",
        "modules_total": len(MODULES),
        "modules_loaded": len(loaded_modules),
        "modules_failed": len(failed_modules),
        "active_modules": loaded_modules
    }

@app.get("/api/status")
def status():
    return {
        "app": "Singh Ji AI Ultra v7.0",
        "total_modules": len(MODULES),
        "loaded": len(loaded_modules),
        "failed": len(failed_modules),
        "working": loaded_modules,
        "errors": failed_modules,
        "module_details": {
            name: {
                "type": info["type"],
                "has_router": info["router"] is not None,
                "has_handler": info["handler"] is not None
            }
            for name, info in MODULES.items()
        }
    }

@app.get("/")
def root():
    return {
        "name": "Singh Ji AI Ultra v7.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
        "status": "🦁 LIVE",
        "modules_loaded": len(loaded_modules),
        "modules_total": len(MODULES),
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "universal": "/api/{module_name}"
        }
    }

# ========== PORT BINDING ==========
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
