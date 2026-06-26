# core/app.py — Singh Ji AI Ultra v5.0
# COMPLETE VERSION — All Modules

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib

app = FastAPI(
    title="Singh Ji AI Ultra v5.0",
    description="भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
    version="5.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ALL MODULES ==========
MODULES = {
    # Core (Done ✅)
    "modules.language": "/api/language",
    "modules.telegram_bot": "/api/telegram",
    "modules.plant_id": "/api/plant",
    "modules.supabase_memory": "/api/memory",
    "modules.adminpanel": "/api/admin",

    # AI (New 🔥)
    "modules.ai_chat": "/api/ai",

    # Utilities (New 🔥)
    "modules.weather": "/api/weather",
    "modules.mandi": "/api/mandi",
    "modules.search": "/api/search",
    "modules.news": "/api/news",

    # Emergency & Govt (New 🔥)
    "modules.emergency": "/api/emergency",
    "modules.govt": "/api/govt",

    # Payments & Services (New 🔥)
    "modules.upi": "/api/upi",
    "modules.email": "/api/email",
    "modules.social": "/api/social",

    # Automation (New 🔥)
    "modules.schedule": "/api/schedule",
    "modules.voice": "/api/voice",
}

# Load modules
loaded = []
failed = []

for mod_name, prefix in MODULES.items():
    try:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix=prefix)
            loaded.append(mod_name)
            print(f"✅ {mod_name}")
        else:
            failed.append(f"{mod_name} — no router")
            print(f"⚠️ {mod_name} — no router")
    except Exception as e:
        failed.append(f"{mod_name} — {str(e)[:50]}")
        print(f"❌ {mod_name} — {e}")

# ========== HEALTH & STATUS ==========
@app.get("/api/health")
def health():
    return {
        "status": "🦁 LIVE",
        "app": "Singh Ji AI Ultra v5.0",
        "version": "5.0.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप",
        "modules_loaded": len(loaded),
        "modules_failed": len(failed)
    }

@app.get("/api/status")
def status():
    return {
        "app": "Singh Ji AI Ultra v5.0",
        "total_modules": len(MODULES),
        "loaded": len(loaded),
        "failed": len(failed),
        "working": loaded,
        "errors": failed,
        "all_endpoints": list(MODULES.values())
    }

@app.get("/")
def root():
    return {
        "name": "Singh Ji AI Ultra v5.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
        "status": "🦁 LIVE",
        "modules": len(loaded),
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "language": "/api/language",
            "telegram": "/api/telegram",
            "plant": "/api/plant",
            "memory": "/api/memory",
            "admin": "/api/admin",
            "ai": "/api/ai",
            "weather": "/api/weather",
            "mandi": "/api/mandi",
            "search": "/api/search",
            "news": "/api/news",
            "emergency": "/api/emergency",
            "govt": "/api/govt",
            "upi": "/api/upi",
            "email": "/api/email",
            "social": "/api/social",
            "schedule": "/api/schedule",
            "voice": "/api/voice"
        }
    }
