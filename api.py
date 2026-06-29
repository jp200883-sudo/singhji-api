# api.py (ROOT LEVEL)
import sys
import os
from pathlib import Path

# ✅ ADD THIS: Ensure core/ is in Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "core"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib

app = FastAPI(title="Singh Ji AI Ultra v7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"🔍 Python path: {sys.path}")
print(f"🔍 BASE_DIR: {BASE_DIR}")
print(f"🔍 core exists: {(BASE_DIR / 'core').exists()}")
print(f"🔍 core/__init__.py exists: {(BASE_DIR / 'core' / '__init__.py').exists()}")

modules_loaded = []
modules_failed = []

# List of modules to load
module_names = [
    "ai_chat", "currents_api", "email", "emergency", "govt",
    "karmachari", "mandi", "master_data", "meta_agent",
    "news_scheduler", "newsdata", "pani", "plant_id",
    "rozgar", "schedule", "search", "sewer", "singhji_agent",
    "singhji_tv", "social", "supabase_memory", "superior_agent",
    "upi", "voice", "voice_cmd", "voice_tts", "weather"
]

# Load flat modules
for mod_name in module_names:
    try:
        mod = importlib.import_module(f"core.modules.{mod_name}")
        if hasattr(mod, "router"):
            app.include_router(mod.router)
            modules_loaded.append(mod_name)
            print(f"✅ Loaded: {mod_name}")
    except Exception as e:
        modules_failed.append(f"{mod_name}: {str(e)}")
        print(f"❌ Failed: {mod_name}: {str(e)}")

# Load folder modules
folder_modules = [
    "adminpanel", "banking", "currency", "entertainment",
    "language", "language_hub", "railway", "telegram_bot"
]

for mod_name in folder_modules:
    try:
        mod = importlib.import_module(f"core.modules.{mod_name}.handler")
        if hasattr(mod, "router"):
            app.include_router(mod.router)
            modules_loaded.append(mod_name)
            print(f"✅ Loaded: {mod_name}")
    except Exception as e:
        modules_failed.append(f"{mod_name}: {str(e)}")
        print(f"❌ Failed: {mod_name}: {str(e)}")

print(f"\n🔥 Singh Ji AI Ultra v7.0 STARTED!")
print(f"✅ Loaded: {len(modules_loaded)} modules")
if modules_failed:
    print(f"❌ Failed: {modules_failed}")
print("👑 Singh Ji ka raj shuru!")

@app.get("/")
def root():
    return {
        "message": "👑 Singh Ji AI Ultra v7.0 - Bharat to the World!",
        "loaded": len(modules_loaded),
        "failed": len(modules_failed)
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "loaded_modules": modules_loaded,
        "failed_modules": modules_failed
    }
