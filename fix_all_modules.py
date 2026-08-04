"""
Singh Ji AI Ultra v8.4 — Main Application
Production Ready — 41 Modules Auto-Discovery
"""

import os
import sys
import importlib.util
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

# ==================== CONFIG ====================

class Constants:
    APP_NAME = "Singh Ji AI Ultra"
    APP_VERSION = "v8.4"
    APP_DESCRIPTION = "Bharat ka AI super app"
    TELEGRAM_WEBHOOK_PATH = "/webhook/telegram"
    CACHE_TTL_SHORT = 60
    CACHE_TTL_MEDIUM = 300
    CACHE_TTL_LONG = 3600
    CACHE_TTL_DAY = 86400

class Settings:
    ENV = os.getenv("ENV", "production")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

    @property
    def is_production(self): return self.ENV == "production"
    @property
    def is_development(self): return self.ENV == "development"

settings = Settings()

def format_response(success=True, data=None, message="", status_code=200):
    return {"success": success, "data": data, "message": message, "status_code": status_code}

def format_error(message="Error", status_code=500):
    return format_response(False, None, message, status_code)

# ==================== MODULE LOADER ====================

MODULES_REGISTRY: List[Dict[str, Any]] = []


def _load_module_from_file(module_name: str, file_path: str):
    """Module ko file se directly load karta hai"""
    try:
        import_path = f"modules.{module_name}.router"

        if import_path in sys.modules:
            return sys.modules[import_path]

        if not os.path.exists(file_path):
            return None

        spec = importlib.util.spec_from_file_location(import_path, file_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[import_path] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"   ⚠️  Load error: {e}")
        return None


def _discover_and_load_modules(app: FastAPI):
    """Sab modules discover aur load karta hai"""
    modules_dir = "/app/modules"

    if not os.path.exists(modules_dir):
        print(f"❌ modules/ directory nahi mili: {modules_dir}")
        return 0, 0

    discovered = []
    for name in sorted(os.listdir(modules_dir)):
        path = os.path.join(modules_dir, name)
        if os.path.isdir(path) and not name.startswith("__") and not name.startswith("."):
            discovered.append(name)

    print(f"\n📦 {len(discovered)} modules found")
    print("-" * 40)

    loaded = 0
    failed = 0

    for name in discovered:
        module_path = os.path.join(modules_dir, name)
        router_file = os.path.join(module_path, "router.py")
        handler_file = os.path.join(module_path, "handler.py")

        # Priority: router.py > handler.py
        target_file = None
        file_type = None

        if os.path.exists(router_file):
            target_file = router_file
            file_type = "router"
        elif os.path.exists(handler_file):
            target_file = handler_file
            file_type = "handler"

        if not target_file:
            print(f"   ⚠️  {name}: No router.py or handler.py")
            failed += 1
            continue

        # Load module
        module = _load_module_from_file(name, target_file)
        if module is None:
            print(f"   ❌ {name}: Load failed")
            failed += 1
            continue

        # Check for router object
        if hasattr(module, "router"):
            try:
                app.include_router(
                    module.router,
                    prefix=f"/api/{name}",
                    tags=[name.replace("_", " ").title()]
                )
                print(f"   ✅ {name} → /api/{name} ({file_type})")
                loaded += 1

                MODULES_REGISTRY.append({
                    "name": name,
                    "type": file_type,
                    "prefix": f"/api/{name}",
                })
            except Exception as e:
                print(f"   ❌ {name}: Router register failed: {e}")
                failed += 1
        else:
            print(f"   ⚠️  {name}: No 'router' object in {file_type}.py")
            failed += 1

    return loaded, failed


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print(f"🚀 {Constants.APP_NAME} {Constants.APP_VERSION}")
    print(f"🌐 Environment: {settings.ENV}")
    print(f"🔌 Port: {settings.PORT}")
    print("=" * 60)

    loaded, failed = _discover_and_load_modules(app)

    print("-" * 40)
    print(f"✅ Loaded: {loaded} | ⚠️ Failed: {failed}")
    print("=" * 60)
    print("🚀 App ready!")

    yield
    print("🛑 Shutting down...")


# ==================== FASTAPI APP ====================

app = FastAPI(
    title=Constants.APP_NAME,
    version=Constants.APP_VERSION,
    description=Constants.APP_DESCRIPTION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== RAILWAY HEALTHCHECK ====================

@app.get("/ping")
async def ping():
    return PlainTextResponse("pong", status_code=200)


# ==================== EXCEPTION HANDLER ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=format_error(
            message="Internal server error",
            details=str(exc) if settings.is_development else None,
        )
    )


# ==================== HEALTH & STATUS ====================

@app.get("/")
@app.get("/health")
async def health_check():
    return format_response(
        data={
            "name": Constants.APP_NAME,
            "version": Constants.APP_VERSION,
            "status": "healthy",
            "environment": settings.ENV,
            "port": settings.PORT,
            "modules_loaded": len(MODULES_REGISTRY),
            "modules": [m["name"] for m in MODULES_REGISTRY],
        },
        message=f"{Constants.APP_NAME} chal raha hai! 🚀",
    )


@app.get("/status")
async def status():
    return format_response(
        data={
            "app": Constants.APP_NAME,
            "version": Constants.APP_VERSION,
            "environment": settings.ENV,
            "port": settings.PORT,
            "modules_count": len(MODULES_REGISTRY),
            "modules": MODULES_REGISTRY,
        },
        message="System status OK",
    )


@app.get("/modules")
async def list_modules():
    return format_response(
        data=MODULES_REGISTRY,
        message=f"{len(MODULES_REGISTRY)} modules available",
    )


# ==================== TELEGRAM WEBHOOK ====================

@app.post(Constants.TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        return format_response(data={"update_id": data.get("update_id")}, message="Webhook received")
    except Exception as e:
        return format_error(message=str(e), status_code=400)


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
        log_level="info",
    )
