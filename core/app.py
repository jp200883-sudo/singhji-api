import os
import sys
import inspect
import importlib.util
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ─── FastAPI App ─────────────────────────────────────────────────────
app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    version="7.0.0",
    description="🇮🇳 India's AI Super App — 37 Modules Dynamic Loader"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# ─── Globals ─────────────────────────────────────────────────────────
MODULES = {}
loaded = []
failed = {}

# ─── Auto-Wrapper for File Modules (no handler function) ─────────────
def auto_handler(name: str, mod):
    """
    Creates a smart handler for modules that don't export 'handler' or 'Handler'.
    Tries common function names first, then falls back to any callable.
    """
    # Priority function names to try
    priority_names = ["process", "main", "run", "chat", "get_data", "fetch", 
                      "search", "translate", "predict", "analyze", "handle"]
    
    all_funcs = {
        n: f for n, f in vars(mod).items() 
        if callable(f) and not n.startswith('_')
    }
    
    def handler(data=None):
        # Try priority functions first
        for func_name in priority_names:
            if func_name in all_funcs:
                f = all_funcs[func_name]
                try:
                    sig = inspect.signature(f)
                    params = list(sig.parameters.keys())
                    if len(params) == 0:
                        return {"module": name, "status": "success", "data": f()}
                    elif len(params) == 1:
                        return {"module": name, "status": "success", "data": f(data)}
                    else:
                        return {"module": name, "status": "success", "data": f(data, **{})}
                except Exception as e:
                    return {"module": name, "status": "error", "error": f"{func_name} failed: {str(e)}"}
        
        # Fallback: try ANY function
        for func_name, f in all_funcs.items():
            try:
                sig = inspect.signature(f)
                if len(sig.parameters) == 0:
                    return {"module": name, "status": "success", "data": f()}
                else:
                    return {"module": name, "status": "success", "data": f(data)}
            except Exception as e:
                continue
        
        # Ultimate fallback
        return {"module": name, "status": "success", "message": f"{name} is active! 🦁"}
    
    return handler

# ─── Module Loader ───────────────────────────────────────────────────
def load_module(name: str):
    """
    Dynamically loads a module from the modules/ directory.
    Supports both folder modules (with __init__.py or handler.py) 
    and file modules (.py files).
    """
    # Get absolute path to modules/ directory
    base_dir = Path(__file__).parent.parent  # core/ -> root/
    modules_dir = base_dir / "modules"
    module_path = modules_dir / name
    
    info = {
        "name": name,
        "handler": None,
        "status": "loading",
        "type": None,
        "error": None
    }
    
    try:
        # Determine module type and entry point
        if module_path.is_dir():
            info["type"] = "folder"
            # Try __init__.py first, then handler.py
            if (module_path / "__init__.py").exists():
                entry_file = module_path / "__init__.py"
            elif (module_path / "handler.py").exists():
                entry_file = module_path / "handler.py"
            else:
                info["status"] = "not_found"
                info["error"] = "No __init__.py or handler.py found"
                return info
            
            spec = importlib.util.spec_from_file_location(f"modules.{name}", str(entry_file))
            
        elif module_path.suffix == ".py" and module_path.is_file():
            info["type"] = "file"
            spec = importlib.util.spec_from_file_location(f"modules.{name}", str(module_path))
            
        else:
            info["status"] = "not_found"
            info["error"] = "Not a valid Python module"
            return info
        
        # Load the module
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"modules.{name}"] = module
        spec.loader.exec_module(module)
        
        # Find handler
        handler = getattr(module, "handler", None) or getattr(module, "Handler", None)
        
        if handler:
            info["handler"] = handler
            info["status"] = "loaded"
            print(f"✅ {name} (native handler)")
        else:
            # Use auto-wrapper
            info["handler"] = auto_handler(name, module)
            info["status"] = "loaded"
            print(f"✅ {name} (auto-wrapped)")
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = f"{type(e).__name__}: {str(e)}"
        print(f"❌ {name}: {info['error']}")
        traceback.print_exc()
    
    return info

# ─── Load All Modules ────────────────────────────────────────────────
print("🚀 Singh Ji AI Ultra v7.0 — Loading Modules...")
print("=" * 50)

base_dir = Path(__file__).parent.parent
modules_dir = base_dir / "modules"

if modules_dir.exists() and modules_dir.is_dir():
    for item in sorted(modules_dir.iterdir()):
        # Skip hidden files, __pycache__, non-.py files
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        if item.is_file() and item.suffix != ".py":
            continue
        if item.is_dir() and item.name == "__pycache__":
            continue
            
        module_name = item.stem if item.is_file() else item.name
        result = load_module(module_name)
        MODULES[module_name] = result
        
        if result["status"] == "loaded":
            loaded.append(module_name)
        else:
            failed[module_name] = result.get("error", "Unknown error")
else:
    print(f"❌ modules/ directory not found at {modules_dir}")

print("=" * 50)
print(f"📊 LOADED: {len(loaded)}/{len(MODULES)}")
if loaded:
    print(f"✅ Active: {loaded}")
if failed:
    print(f"❌ Failed: {list(failed.keys())}")

# ─── API Routes ──────────────────────────────────────────────────────

@app.post("/api/{module_name}")
@app.get("/api/{module_name}")
async def api_route(module_name: str, request: Request):
    """
    Universal API endpoint for all modules.
    POST: JSON body passed to handler
    GET: Query params passed to handler
    """
    if module_name not in MODULES or MODULES[module_name]["status"] != "loaded":
        return JSONResponse(
            status_code=404,
            content={"error": f"Module '{module_name}' not found or not loaded"}
        )
    
    handler = MODULES[module_name].get("handler")
    if not handler:
        return JSONResponse(
            status_code=500,
            content={"error": f"Module '{module_name}' has no handler"}
        )
    
    # Parse request data
    try:
        if request.method == "POST":
            data = await request.json()
        else:
            data = dict(request.query_params)
    except Exception:
        data = {}
    
    # Execute handler
    try:
        # Check if handler is async
        if inspect.iscoroutinefunction(handler):
            result = await handler(data)
        else:
            result = handler(data)
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Handler error in {module_name}: {str(e)}"}
        )

@app.get("/api/health")
def health_check():
    return {
        "status": "🦁 LIVE",
        "version": "7.0.0",
        "loaded": len(loaded),
        "total": len(MODULES),
        "modules": loaded
    }

@app.get("/api/status")
def status():
    return {
        "loaded_count": len(loaded),
        "failed_count": len(failed),
        "loaded_modules": loaded,
        "failed_modules": failed,
        "all_modules": {k: v["status"] for k, v in MODULES.items()}
    }

@app.get("/")
def root():
    return {
        "name": "Singh Ji AI Ultra v7.0",
        "tagline": "🇮🇳 India's AI Super App",
        "modules_loaded": len(loaded),
        "modules_total": len(MODULES),
        "status": "🦁 LIVE",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "module_api": "/api/{module_name}"
        }
    }

# ─── Render Deployment Note ─────────────────────────────────────────
# Start Command (Render Dashboard):
#   uvicorn core.app:app --host 0.0.0.0 --port $PORT
#
# Do NOT rely on __main__ block for Render — use the start command above.
