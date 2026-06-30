import os
import sys
import inspect
import importlib.util
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Singh Ji AI Ultra v7.0", version="7.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

MODULES = {}; loaded = []; failed = {}

def auto_handler(name, mod):
    priority = ["process","main","run","chat","get_data","fetch","search","translate","predict","analyze","handle","get_weather","get_mandi","send_email","get_news","get_price","detect","recognize","speak","listen","query","execute","call","invoke","generate","forecast","check","verify","calculate","convert"]
    funcs = {n:f for n,f in vars(mod).items() if callable(f) and not n.startswith('_')}
    def handler(data=None):
        for fn in priority:
            if fn in funcs:
                try:
                    sig = inspect.signature(funcs[fn])
                    if len(list(sig.parameters)) == 0: return {"module":name,"status":"success","data":funcs[fn]()}
                    else: return {"module":name,"status":"success","data":funcs[fn](data)}
                except Exception as e: return {"module":name,"status":"error","error":f"{fn} failed: {str(e)}"}
        for fn,f in funcs.items():
            try:
                sig = inspect.signature(f)
                if len(list(sig.parameters)) == 0: return {"module":name,"status":"success","data":f()}
                else: return {"module":name,"status":"success","data":f(data)}
            except: continue
        return {"module":name,"status":"success","message":f"{name} active! 🦁"}
    return handler

def load_module(name, modules_dir):
    # FIX: Try with .py extension if not found
    p = modules_dir / name
    if not p.exists() and not name.endswith('.py'):
        p = modules_dir / (name + '.py')
    
    info = {"name":name,"handler":None,"status":"loading","type":None,"error":None,"traceback":None}
    try:
        if p.is_dir():
            info["type"] = "folder"
            entry = p/"__init__.py" if (p/"__init__.py").exists() else p/"handler.py"
            if not entry.exists():
                py_files = sorted(p.glob("*.py"))
                entry = py_files[0] if py_files else None
            if entry is None: info["status"]="not_found"; info["error"]="No .py file found"; return info
            spec = importlib.util.spec_from_file_location(f"modules.{name}", str(entry))
            
        elif p.is_file():
            info["type"] = "file"
            spec = importlib.util.spec_from_file_location(f"modules.{name}", str(p))
            
        else:
            info["status"]="not_found"
            info["error"]=f"Not found: {p}"
            return info
        
        if spec is None: info["status"]="error"; info["error"]="spec_from_file_location returned None"; return info
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"modules.{name}"] = mod
        
        try: spec.loader.exec_module(mod)
        except Exception as e:
            if f"modules.{name}" in sys.modules: del sys.modules[f"modules.{name}"]
            info["status"]="error"; info["error"]=f"EXEC: {type(e).__name__}: {e}"; info["traceback"]=traceback.format_exc(); return info
        
        h = getattr(mod,"handler",None) or getattr(mod,"Handler",None)
        if h: info["handler"]=h; info["status"]="loaded"; print(f"✅ {name} (native)")
        else: info["handler"]=auto_handler(name,mod); info["status"]="loaded"; print(f"✅ {name} (wrapped)")
    except Exception as e:
        info["status"]="error"; info["error"]=f"UNEXPECTED: {type(e).__name__}: {e}"; info["traceback"]=traceback.format_exc()
    return info

print("🚀 Loading Modules..."); print("="*60)

paths = []
try: paths.append(Path(__file__).resolve().parent.parent/"modules")
except: pass
paths.extend([Path.cwd()/"modules", Path("/app/modules"), Path("/opt/render/project/src/modules")])
if os.environ.get("MODULES_PATH"): paths.append(Path(os.environ.get("MODULES_PATH")))

modules_dir = None
for p in paths:
    if p and p.exists() and p.is_dir():
        try:
            has = any(f.endswith(".py") or '.' not in f for f in os.listdir(p) if os.path.isfile(p/f))
            if has: modules_dir=p; print(f"📁 Found: {p}"); break
        except: pass

if not modules_dir:
    for root,dirs,files in os.walk("/", topdown=True):
        if root.count("/")>6: del dirs[:]; continue
        if "modules" in dirs:
            c=Path(root)/"modules"
            try:
                if any(f.endswith(".py") or '.' not in f for f in os.listdir(c)): modules_dir=c; print(f"📁 Found: {c}"); break
            except: pass
        dirs[:] = [d for d in dirs if d not in ("proc","sys","dev","tmp","var","boot")]

if modules_dir and modules_dir.exists():
    print(f"📂 Scanning: {modules_dir}")
    for item in sorted(modules_dir.iterdir()):
        if item.name.startswith("_") or item.name.startswith("."): continue
        if item.name in ("__pycache__","app.py","init.py"): continue
        if item.is_file() and item.suffix not in ('.py',''): continue  # Allow extensionless files
        n = item.stem if item.is_file() else item.name
        r = load_module(n, modules_dir); MODULES[n]=r
        if r["status"]=="loaded": loaded.append(n)
        else: failed[n]=r.get("error","?"); print(f"❌ {n}: {r.get('error','?')[:100]}")
else: print(f"❌ modules/ NOT FOUND! CWD:{Path.cwd()}")

print("="*60); print(f"📊 LOADED: {len(loaded)}/{len(MODULES)}")
if loaded: print(f"✅ Active: {loaded}")
if failed: print(f"❌ Failed: {list(failed.keys())}")

@app.api_route("/api/{m}", methods=["GET","POST","HEAD"])
async def api(m:str, request:Request):
    if m not in MODULES or MODULES[m]["status"]!="loaded": return JSONResponse(status_code=404, content={"error":f"Module '{m}' not found"})
    h = MODULES[m].get("handler")
    if not h: return JSONResponse(status_code=500, content={"error":"No handler"})
    try:
        d = await request.json() if request.method=="POST" else (dict(request.query_params) if request.method=="GET" else {})
    except: d = {}
    try:
        if inspect.iscoroutinefunction(h): r = await h(d)
        else: r = h(d)
        return JSONResponse(content=r)
    except Exception as e: traceback.print_exc(); return JSONResponse(status_code=500, content={"error":f"Handler error: {str(e)}"})

@app.api_route("/api/health", methods=["GET","HEAD"])
def health(): return {"status":"🦁 LIVE","version":"7.0.0","loaded":len(loaded),"total":len(MODULES),"modules":loaded}

@app.api_route("/api/status", methods=["GET","HEAD"])
def status(): return {"loaded_count":len(loaded),"failed_count":len(failed),"loaded":loaded,"failed":failed,"details":{k:{"status":v["status"],"type":v.get("type"),"error":v.get("error","")[:200]} for k,v in MODULES.items()}}

@app.api_route("/", methods=["GET","HEAD"])
def root(): return {"name":"Singh Ji AI Ultra v7.0","loaded":len(loaded),"total":len(MODULES),"status":"🦁 LIVE"}
