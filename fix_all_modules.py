python3 << 'EOF'
content = '''
"""
Singh Ji AI Ultra v8.4 — Standalone
"""

import os, sys, importlib.util
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

APP_NAME = "Singh Ji AI Ultra"
APP_VERSION = "v8.4"
ENV = os.getenv("ENV", "production")
PORT = int(os.getenv("PORT", "8000"))

LOADED = []

def ok(data=None, msg=""):
    return {"success": True, "data": data, "message": msg}

def err(msg="Error", code=500):
    return {"success": False, "data": None, "message": msg, "status_code": code}

def load_mod(name, path):
    try:
        ip = "modules." + name + ".router"
        if ip in sys.modules:
            return sys.modules[ip]
        spec = importlib.util.spec_from_file_location(ip, path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[ip] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("      ⚠️  " + name + ": " + str(e))
        return None

def discover(app):
    md = "/app/modules"
    if not os.path.exists(md):
        print("❌ modules/ nahi mili")
        return 0, 0
    
    dirs = [d for d in sorted(os.listdir(md)) 
            if os.path.isdir(os.path.join(md, d)) and not d.startswith(".")]
    
    print("\\n📦 " + str(len(dirs)) + " modules mil gaye")
    print("-" * 40)
    
    loaded = 0
    failed = 0
    for name in dirs:
        mp = os.path.join(md, name)
        rp = os.path.join(mp, "router.py")
        hp = os.path.join(mp, "handler.py")
        
        target = ""
        src = ""
        if os.path.exists(rp):
            target, src = rp, "router"
        elif os.path.exists(hp):
            target, src = hp, "handler"
        
        if not target:
            print("   ⚠️  " + name + ": koi router/handler nahi")
            failed += 1
            continue
        
        mod = load_mod(name, target)
        if not mod:
            print("   ❌ " + name + ": load fail")
            failed += 1
            continue
        
        if not hasattr(mod, "router"):
            print("   ⚠️  " + name + ": router object nahi hai")
            failed += 1
            continue
        
        try:
            app.include_router(mod.router, prefix="/api/" + name, tags=[name.replace("_", " ").title()])
            print("   ✅ " + name + " → /api/" + name)
            LOADED.append({"name": name, "src": src})
            loaded += 1
        except Exception as e:
            print("   ❌ " + name + ": " + str(e))
            failed += 1
    
    return loaded, failed

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("🚀 " + APP_NAME + " " + APP_VERSION)
    print("🌐 " + ENV + " | 🔌 Port " + str(PORT))
    print("=" * 60)
    l, f = discover(app)
    print("-" * 40)
    print("✅ Loaded: " + str(l) + " | ⚠️ Failed: " + str(f))
    print("=" * 60)
    print("🚀 Ready!")
    yield
    print("🛑 Shutdown...")

app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/ping")
def ping():
    return PlainTextResponse("pong", 200)

@app.exception_handler(Exception)
async def eh(request, exc):
    return JSONResponse(status_code=500, content=err("Internal error", 500))

@app.get("/")
@app.get("/health")
def health():
    return ok({
        "name": APP_NAME,
        "version": APP_VERSION,
        "env": ENV,
        "port": PORT,
        "modules": len(LOADED),
        "list": [m["name"] for m in LOADED]
    }, APP_NAME + " chal raha hai! 🚀")

@app.get("/status")
def status():
    return ok({
        "app": APP_NAME,
        "version": APP_VERSION,
        "env": ENV,
        "port": PORT,
        "modules": LOADED,
        "count": len(LOADED)
    }, "Status OK")

@app.get("/modules")
def list_mods():
    return ok(LOADED, str(len(LOADED)) + " modules")

@app.post("/webhook/telegram")
async def tg_webhook(request: Request):
    try:
        data = await request.json()
        return ok({"update_id": data.get("update_id")}, "Webhook OK")
    except:
        return err("Invalid data", 400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, log_level="info")
'''

with open('/app/main.py', 'w') as f:
    f.write(content.strip())

print("✅ /app/main.py written")
print("Size:", len(content), "bytes")
EOF
