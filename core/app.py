import os
import sys
import inspect
import importlib.util
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════════
# 🦁 SINGH JI AI ULTRA v7.0 — DYNAMIC MODULE LOADER
# ═══════════════════════════════════════════════════════════════════

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

# ─── Auto-Wrapper for File Modules ───────────────────────────────────
def auto_handler(name: str, mod):
    """Smart handler for modules without native handler function."""
    priority_names = [
        "process", "main", "run", "chat", "get_data", "fetch", 
        "search", "translate", "predict", "analyze", "handle",
        "get_weather", "get_mandi", "send_email", "get_news",
        "get_price", "detect", "recognize", "speak", "listen",
        "query", "execute", "call", "invoke", "generate"
    ]
    
    all_funcs = {
        n: f for n, f in vars(mod).items() 
        if callable(f) and not n.startswith('_')
    }
    
    def handler(data=None):
        for func_name in priority_names:
            if func_name in all_funcs:
                f = all_funcs[func_name]
                try:
                    sig = inspect.signature(f)
                    params = list(sig.parameters.keys())
                    if len(params) == 0:
                        return {"module": name, "status": "success", "data": f()}
                    else:
                        return {"module": name, "status": "success", "data": f(data)}
                except Exception as e:
                    return {"module": name, "status": "error", "error": f"{func_name} failed: {str(e)}"}
        
        for func_name, f in all_funcs.items():
            try:
                sig = inspect.signature(f)
                if len(sig.parameters) == 0:
                    return {"module": name, "status": "success", "data": f()}
                else:
                    return {"module": name, "status": "success", "data": f(data)}
            except:
                continue
        
        return {"module": name, "status": "success", "message": f"{name} is active! 🦁"}
    
    return handler

# ─── Module Loader ───────────────────────────────────────────────────
def load_module(name: str, modules_dir: Path):
    """Dynamically loads a module from the given modules directory."""
    module_path = modules_dir / name
    
    info = {
        "name": name,
        "handler": None,
        "status": "loading",
        "type": None,
        "error": None
    }
    
    try:
        if module_path.is_dir():
            info["type"] = "folder"
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
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"modules.{name}"] = module
        spec.loader.exec_module(module)
        
        handler = getattr(module, "handler", None) or getattr(module, "Handler", None)
        
        if handler:
            info["handler"] = handler
            info["status"] = "loaded"
            print(f"✅ {name} (native handler)")
        else:
            info["handler"] = auto_handler(name, module)
            info["status"] = "loaded"
            print(f"✅ {name} (auto-wrapped)")
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = f"{type(e).__name__}: {str(e)}"
        print(f"❌ {name}: {info['error']}")
        traceback.print_exc()
    
    return info

# ─── CRITICAL: Find modules/ directory ───────────────────────────────
print("🚀 Singh Ji AI Ultra v7.0 — Loading Modules...")
print("=" * 50)

possible_paths = []

# 1. Relative to this file (core/app.py -> root/modules)
try:
    file_dir = Path(__file__).resolve().parent.parent
    possible_paths.append(file_dir / "modules")
except:
    pass

# 2. Current working directory
possible_paths.append(Path.cwd() / "modules")

# 3. Environment variable
if os.environ.get("MODULES_PATH"):
    possible_paths.append(Path(os.environ.get("MODULES_PATH")))

# 4. Common Render paths
possible_paths.extend([
    Path("/app/modules"),
    Path("/opt/render/project/src/modules"),
    Path("/home/render/modules"),
])

modules_dir = None
for p in possible_paths:
    if p and p.exists() and p.is_dir():
        has_py = any(f.endswith(".py") for f in os.listdir(p) if os.path.isfile(p / f))
        has_dirs = any(os.path.isdir(p / d) and not d.startswith("_") for d in os.listdir(p))
        if has_py or has_dirs:
            modules_dir = p
            print(f"📁 Found modules/ at: {p.absolute()}")
            break

# Last resort: search from root
if not modules_dir:
    print("⚠️  Searching for modules/ directory...")
    for root, dirs, files in os.walk("/", topdown=True):
        if root.count("/") > 6:
            del dirs[:]
            continue
        if "modules" in dirs:
            candidate = Path(root) / "modules"
            if any(f.endswith(".py") for f in os.listdir(candidate)):
                modules_dir = candidate
                print(f"📁 Found modules/ at: {candidate}")
                break
        dirs[:] = [d for d in dirs if d not in ("proc", "sys", "dev", "tmp", "var")]

if modules_dir and modules_dir.exists():
    print(f"📂 Scanning: {modules_dir}")
    print(f"📂 Contents: {[f.name for f in modules_dir.iterdir()]}")
    
    for item in sorted(modules_dir.iterdir()):
        # SKIP these: hidden, pycache, non-py, init files
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        if item.name in ("__pycache__", "app.py", "init.py"):
            continue
        if item.is_file() and item.suffix != ".py":
            continue
            
        module_name = item.stem if item.is_file() else item.name
        result = load_module(module_name, modules_dir)
        MODULES[module_name] = result
        
        if result["status"] == "loaded":
            loaded.append(module_name)
        else:
            failed[module_name] = result.get("error", "Unknown error")
else:
    print(f"❌ CRITICAL: modules/ directory NOT FOUND!")
    print(f"   CWD: {Path.cwd()}")
    print(f"   __file__: {__file__ if '__file__' in dir() else 'N/A'}")

print("=" * 50)
print(f"📊 LOADED: {len(loaded)}/{len(MODULES)}")
if loaded:
    print(f"✅ Active: {loaded}")
if failed:
    print(f"❌ Failed: {list(failed.keys())}")

# ─── API Routes (FIXED: api_route with HEAD support) ───────────────

@app.api_route("/api/{module_name}", methods=["GET", "POST", "HEAD"])
async def api_route(module_name: str, request: Request):
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
    
    try:
        if request.method == "POST":
            data = await request.json()
        elif request.method == "GET":
            data = dict(request.query_params)
        else:  # HEAD
            data = {}
    except Exception:
        data = {}
    
    try:
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

@app.api_route("/api/health", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "🦁 LIVE",
        "version": "7.0.0",
        "loaded": len(loaded),
        "total": len(MODULES),
        "modules": loaded
    }

@app.api_route("/api/status", methods=["GET", "HEAD"])
def status():
    return {
        "loaded_count": len(loaded),
        "failed_count": len(failed),
        "loaded_modules": loaded,
        "failed_modules": failed,
        "all_modules": {k: v["status"] for k, v in MODULES.items()}
    }

@app.api_route("/", methods=["GET", "HEAD"])
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

# Render Start Command: uvicorn core.app:app --host 0.0.0.0 --port $PORT
