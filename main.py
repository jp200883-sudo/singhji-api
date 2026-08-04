"""
Singh Ji AI Ultra v8.4 — Main Application
SAFE MODE — sirf router.py wale modules load honge
"""

import os
import sys
import importlib
import importlib.util
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ==================== CORE IMPORTS (with fallback) ====================

# Config
try:
    from core.config import settings, Constants
except ImportError:
    # Fallback agar core module nahi mila
    class Constants:
        APP_NAME = "Singh Ji AI Ultra"
        APP_VERSION = "v8.4"
        APP_DESCRIPTION = "Bharat ka AI super app"
        TELEGRAM_WEBHOOK_PATH = "/webhook/telegram"

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

        @property
        def is_production(self):
            return self.ENV == "production"

        @property
        def is_development(self):
            return self.ENV == "development"

        def required_keys_present(self):
            missing = []
            if not self.SUPABASE_URL or not self.SUPABASE_KEY:
                missing.append("SUPABASE")
            if not self.TELEGRAM_BOT_TOKEN:
                missing.append("TELEGRAM_BOT_TOKEN")
            if not self.GROQ_API_KEY and not self.GEMINI_API_KEY:
                missing.append("AI_KEY")
            return missing

    settings = Settings()

# Database
try:
    from core.database import get_supabase_client, supabase
except ImportError:
    get_supabase_client = lambda: None
    supabase = None

# Rate limit
try:
    from core.rate_limit import rate_limit_middleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
    class DummyMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    def rate_limit_middleware():
        return DummyMiddleware

# Telegram
try:
    from core.telegram import set_webhook_telegram
except ImportError:
    def set_webhook_telegram(url):
        return {"ok": False, "error": "core.telegram not available"}

# Utils
try:
    from utils.helpers import format_response, format_error
except ImportError:
    def format_response(success=True, data=None, message="", status_code=200, meta=None):
        r = {"success": success, "data": data, "message": message, "status_code": status_code}
        if meta: r["meta"] = meta
        return r

    def format_error(message="Error", error_code="ERROR", details=None, status_code=500):
        return format_response(False, None, message, status_code, {"error_code": error_code, "details": details})


# ==================== MODULE DISCOVERY (ONLY router.py) ====================

MODULES_REGISTRY: List[Dict[str, Any]] = []


def _discover_modules() -> List[Dict[str, Any]]:
    """SIRF router.py wale modules discover karta hai — handler.py IGNORE"""
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    discovered = []

    if not os.path.exists(modules_dir):
        print("⚠️  modules/ directory nahi mili")
        return discovered

    for module_name in sorted(os.listdir(modules_dir)):
        module_path = os.path.join(modules_dir, module_name)

        if not os.path.isdir(module_path):
            continue
        if module_name.startswith("__") or module_name.startswith("."):
            continue
        if module_name.endswith(".md"):
            continue

        # SIRF router.py check karo — handler.py IGNORE
        router_file = os.path.join(module_path, "router.py")

        if os.path.exists(router_file):
            discovered.append({
                "name": module_name,
                "path": module_path,
                "import_path": f"modules.{module_name}.router",
            })

    return discovered


def _safe_import_module(import_path: str):
    """Module ko safely import karta hai — koi error nahi"""
    try:
        if import_path in sys.modules:
            return sys.modules[import_path]

        # Direct file load (bina sys.path change kiye)
        parts = import_path.split(".")
        module_name = parts[-1]

        # modules/<name>/router.py ka path
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "modules", parts[1], f"{module_name}.py")

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
        print(f"   ⚠️  Import error: {e}")
        return None


def _register_module(module_info: Dict[str, Any], app: FastAPI) -> bool:
    """Module ki routes register karta hai"""
    name = module_info["name"]
    import_path = module_info["import_path"]

    try:
        module = _safe_import_module(import_path)
        if module is None:
            print(f"   ⚠️  {name}: Module load nahi hua")
            return False

        if not hasattr(module, "router"):
            print(f"   ⚠️  {name}: 'router' object nahi mila")
            return False

        router_obj = module.router
        prefix = f"/api/{name}"
        tag = name.replace("_", " ").title()

        app.include_router(router_obj, prefix=prefix, tags=[tag])
        print(f"   ✅ {name} → {prefix}")
        return True

    except Exception as e:
        print(f"   ❌ {name}: {e}")
        return False


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print(f"🚀 {Constants.APP_NAME} {Constants.APP_VERSION}")
    print(f"🌐 Environment: {settings.ENV}")
    print(f"🔌 Port: {settings.PORT}")
    print("=" * 60)

    # Supabase connect
    try:
        get_supabase_client()
    except Exception as e:
        print(f"⚠️  Supabase: {e}")

    # Missing keys
    try:
        missing = settings.required_keys_present()
        if missing:
            print(f"⚠️  Missing keys: {missing}")
        else:
            print("✅ All required keys present")
    except:
        pass

    # Telegram webhook
    if settings.is_production and settings.TELEGRAM_BOT_TOKEN:
        try:
            webhook_url = f"{settings.RAILWAY_STATIC_URL}{Constants.TELEGRAM_WEBHOOK_PATH}"
            if settings.RAILWAY_STATIC_URL:
                result = set_webhook_telegram(webhook_url)
                print(f"📡 Webhook: {result.get('ok', False)}")
        except Exception as e:
            print(f"⚠️  Webhook setup failed: {e}")

    # Module discovery
    global MODULES_REGISTRY
    MODULES_REGISTRY = _discover_modules()

    print(f"\n📦 {len(MODULES_REGISTRY)} modules with router.py found")
    print("-" * 40)

    loaded = 0
    failed = 0

    for module_info in MODULES_REGISTRY:
        if _register_module(module_info, app):
            loaded += 1
        else:
            failed += 1

    print("-" * 40)
    print(f"✅ Loaded: {loaded} | ⚠️ Skipped: {failed}")
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

try:
    app.add_middleware(rate_limit_middleware())
except:
    pass


# ==================== EXCEPTION HANDLER ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=format_error(
            message="Internal server error",
            error_code="INTERNAL_ERROR",
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
        },
        message=f"{Constants.APP_NAME} chal raha hai! 🚀",
    )


@app.get("/status")
async def status():
    modules_status = []
    for m in MODULES_REGISTRY:
        modules_status.append({
            "name": m["name"],
            "prefix": f"/api/{m['name']}",
        })

    return format_response(
        data={
            "app": Constants.APP_NAME,
            "version": Constants.APP_VERSION,
            "environment": settings.ENV,
            "port": settings.PORT,
            "modules": modules_status,
            "modules_count": len(MODULES_REGISTRY),
        },
        message="System status OK",
    )


@app.get("/modules")
async def list_modules():
    return format_response(
        data=MODULES_REGISTRY,
        message=f"{len(MODULES_REGISTRY)} modules available",
    )


# ==================== TELEGRAM WEBHOOK FALLBACK ====================

@app.post(Constants.TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook_fallback(request: Request):
    try:
        data = await request.json()
        return format_response(
            data={"update_id": data.get("update_id")},
            message="Webhook received (fallback)",
        )
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
