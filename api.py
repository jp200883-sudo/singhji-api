# api.py — DEBUG VERSION — Singh Ji AI Ultra v7.0

import sys
import os
import traceback
from pathlib import Path

# ✅ Ensure core/ is in Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

print(f"🔍 BASE_DIR: {BASE_DIR}")
print(f"🔍 sys.path: {sys.path[:3]}")
print(f"🔍 core exists: {(BASE_DIR / 'core').exists()}")
print(f"🔍 core/__init__.py exists: {(BASE_DIR / 'core' / '__init__.py').exists()}")
print(f"🔍 core/modules exists: {(BASE_DIR / 'core' / 'modules').exists()}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib

app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="Bharat to the World",
    version="7.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

modules_loaded = []
modules_failed = []

def load_module(mod_name, is_folder=False):
    """
    Smart module loader with FULL ERROR PRINTING
    """
    locations = []
    
    if is_folder:
        locations = [
            f"core.modules.{mod_name}",
            f"core.modules.{mod_name}.handler"
        ]
    else:
        locations = [f"core.modules.{mod_name}"]
    
    errors = []
    
    for loc in locations:
        try:
            print(f"  🔍 Trying: {loc}")
            mod = importlib.import_module(loc)
            print(f"  ✅ Module imported: {loc}")
            
            if hasattr(mod, "router"):
                app.include_router(mod.router)
                print(f"  ✅ Router found in: {loc}")
                return True, loc
            else:
                print(f"  ⚠️ No router in: {loc}")
                errors.append(f"{loc}: No router attribute")
                
        except Exception as e:
            error_msg = f"{loc}: {type(e).__name__}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ Error: {error_msg}")
            traceback.print_exc()
            continue
    
    return False, errors

# ============================================================
# LOAD ALL MODULES
# ============================================================

print("=" * 60)
print("🦁 LOADING SINGH JI AI ULTRA v7.0 MODULES")
print("=" * 60)

flat_modules = [
    "ai_chat", "currents_api", "email", "emergency", "govt",
    "karmachari", "mandi", "master_data", "meta_agent",
    "news_scheduler", "newsdata", "pani", "plant_id",
    "rozgar", "schedule", "search", "sewer", "singhji_agent",
    "singhji_tv", "social", "supabase_memory", "superior_agent",
    "upi", "voice", "voice_cmd", "voice_tts", "weather"
]

folder_modules = [
    "adminpanel", "banking", "currency", "entertainment",
    "language", "language_hub", "railway", "telegram_bot"
]

# Load first module with FULL DEBUG
print("\n🔬 DEBUGGING FIRST MODULE (ai_chat):")
success, result = load_module("ai_chat", is_folder=False)

# Load remaining flat modules
for mod_name in flat_modules[1:]:
    success, result = load_module(mod_name, is_folder=False)
    if success:
        modules_loaded.append(mod_name)
        print(f"✅ Loaded: {mod_name}")
    else:
        modules_failed.append(f"{mod_name}: {result}")
        print(f"❌ Failed: {mod_name}: {result}")

# Load folder modules
for mod_name in folder_modules:
    success, result = load_module(mod_name, is_folder=True)
    if success:
        modules_loaded.append(mod_name)
        print(f"✅ Loaded: {mod_name}")
    else:
        modules_failed.append(f"{mod_name}: {result}")
        print(f"❌ Failed: {mod_name}: {result}")

print("=" * 60)
print(f"🔥 Singh Ji AI Ultra v7.0 STARTED!")
print(f"✅ Loaded: {len(modules_loaded)} modules")
print(f"❌ Failed: {len(modules_failed)} modules")
print("👑 Singh Ji ka raj shuru!")
print("=" * 60)

# ============================================================
# ROUTES
# ============================================================

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "message": "👑 Singh Ji AI Ultra v7.0 — Bharat to the World!",
        "loaded": len(modules_loaded),
        "failed": len(modules_failed),
        "status": "🟢 Online"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "loaded": len(modules_loaded),
        "failed": len(modules_failed),
        "modules": modules_loaded
    }
