# api.py — Singh Ji AI Ultra v7.0 — Main FastAPI Entry Point
# ROOT LEVEL FILE — NOT inside core/

import sys
import os
from pathlib import Path

# ✅ Ensure core/ is in Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="Bharat to the World — 220 Languages, 33 Modules",
    version="7.0.0"
)

# CORS — Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODULE LOADER
# ============================================================

modules_loaded = []
modules_failed = []

def load_module(mod_name, is_folder=False):
    """
    Smart module loader — tries multiple locations for router
    """
    locations = []
    
    if is_folder:
        # Folder modules: try __init__.py first, then handler.py
        locations = [
            f"core.modules.{mod_name}",           # __init__.py
            f"core.modules.{mod_name}.handler"    # handler.py
        ]
    else:
        # Flat modules: direct import
        locations = [f"core.modules.{mod_name}"]
    
    for loc in locations:
        try:
            mod = importlib.import_module(loc)
            if hasattr(mod, "router"):
                app.include_router(mod.router)
                return True, loc
        except Exception as e:
            continue
    
    return False, None

# ============================================================
# ALL 33 MODULES
# ============================================================

# Flat modules (.py files directly in core/modules/)
flat_modules = [
    "ai_chat", "currents_api", "email", "emergency", "govt",
    "karmachari", "mandi", "master_data", "meta_agent",
    "news_scheduler", "newsdata", "pani", "plant_id",
    "rozgar", "schedule", "search", "sewer", "singhji_agent",
    "singhji_tv", "social", "supabase_memory", "superior_agent",
    "upi", "voice", "voice_cmd", "voice_tts", "weather"
]

# Folder modules (subfolders with __init__.py or handler.py)
folder_modules = [
    "adminpanel", "banking", "currency", "entertainment",
    "language", "language_hub", "railway", "telegram_bot"
]

# Load flat modules
print("=" * 60)
print("🦁 LOADING SINGH JI AI ULTRA v7.0 MODULES")
print("=" * 60)

for mod_name in flat_modules:
    success, loc = load_module(mod_name, is_folder=False)
    if success:
        modules_loaded.append(mod_name)
        print(f"✅ Loaded: {mod_name}")
    else:
        modules_failed.append(mod_name)
        print(f"❌ Failed: {mod_name}")

# Load folder modules
for mod_name in folder_modules:
    success, loc = load_module(mod_name, is_folder=True)
    if success:
        modules_loaded.append(mod_name)
        print(f"✅ Loaded: {mod_name} ({loc})")
    else:
        modules_failed.append(mod_name)
        print(f"❌ Failed: {mod_name}")

# ============================================================
# STARTUP MESSAGE
# ============================================================

print("=" * 60)
print(f"🔥 Singh Ji AI Ultra v7.0 STARTED!")
print(f"✅ Loaded: {len(modules_loaded)} modules")
if modules_failed:
    print(f"❌ Failed: {modules_failed}")
print("👑 Singh Ji ka raj shuru!")
print("=" * 60)

# ============================================================
# API ROUTES
# ============================================================

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    """Root endpoint — supports GET and HEAD for Render health check"""
    return {
        "message": "👑 Singh Ji AI Ultra v7.0 — Bharat to the World!",
        "version": "7.0.0",
        "loaded_modules": len(modules_loaded),
        "failed_modules": len(modules_failed),
        "status": "🟢 Online",
        "mantra": "भारत में पैदा हो, दुनिया को कायदा सिखाओ"
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Singh Ji AI Ultra v7.0",
        "loaded": len(modules_loaded),
        "failed": len(modules_failed),
        "modules": modules_loaded
    }

@app.get("/status")
def status():
    """Detailed system status"""
    return {
        "app": "Singh Ji AI Ultra v7.0",
        "version": "7.0.0",
        "owner": "JP Singh Ji, Kanpur, UP, India",
        "modules": {
            "total": 33,
            "loaded": len(modules_loaded),
            "failed": len(modules_failed),
            "list": modules_loaded
        },
        "features": [
            "220 Languages", "AI Chat", "Weather", "Mandi Rates",
            "News", "UPI QR", "Plant ID", "Railway", "Govt Services",
            "Emergency", "Voice AI", "Telegram Bot", "Admin Panel"
        ],
        "payment_gateway": "ON HOLD (1000+ users required)",
        "patent": "Glocal PPP Token Pricing System — Filed"
    }

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "message": "कुछ गड़बड़ हो गई! Singh Ji जल्दी ठीक करेंगे!"
    }

# ============================================================
# RUN (for local development)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
