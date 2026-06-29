# app.py — Singh Ji AI Ultra v5.0 (FIXED)
# 🚀 MAIN APP — सब Agents एक साथ, सब Singh Ji के अंडर में!

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import importlib
import sys
import os
import traceback

app = FastAPI(
    title="Singh Ji AI Ultra v5.0",
    description="भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
    version="5.0.0"
)

# ===== CORS — सबको allow करो =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ===== ERROR HANDLER =====
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong!",
            "detail": str(exc),
            "path": str(request.url),
            "singh_ji_message": "गड़बड़ी हुई — Singh Ji ko report kar raha hoon!"
        }
    )

# ===== MODULES LIST — सब यहाँ =====
MODULES = [
    # 🦁 Phase 1: Foundation
    "superior_agent",
    "singhji_agent",
    "meta_agent",
    "master_data",
    
    # 🔧 Core System
    "emergency",
    "supabase_memory",
    "ai_chat",
    "weather",
    "mandi",
    "newsdata",            # 📰 News
    "news_scheduler",      # 📰 News Scheduler
    "currents_api",        # 📰 World News
    "email",
    "schedule",
    "telegram_bot",
    "voice",
    "voice_cmd",
    "voice_tts",
    "plant_id",
    "language",
    "language_hub",
    "search",
    "social",
    "govt",
    "upi",                 # 💳 UPI (एक बार!)
    "adminpanel",
    
    # 🎬 Entertainment
    "entertainment",
    
    # 🏦 Banking & Currency
    "banking",
    "currency",
    
    # 🚂 Railway
    "railway",
    
    # 🆕 v6.0 Modules
    "karmachari",
    "pani",
    "rozgar",
    "sewer",
    
    # 🚫 FUTURE — Payment Gateway (अभी मत चालू करो!)
    # "gateway",           # 💰 Future mein
    # "commission_tracker",  # 💰 Future mein
]

# ===== ROUTER PREFIX — सबका route =====
ROUTER_PREFIX = {
    "superior_agent": "/api/superior",
    "singhji_agent": "/api/singhji",
    "meta_agent": "/api/meta",
    "master_data": "/api/master-data",
    "emergency": "/api/emergency",
    "supabase_memory": "/api/memory",
    "ai_chat": "/api/ai",
    "weather": "/api/weather",
    "mandi": "/api/mandi",
    "newsdata": "/api/news",           # 📰 News
    "news_scheduler": "/api/news-scheduler",
    "currents_api": "/api/currents",   # 🌍 World News
    "email": "/api/email",
    "schedule": "/api/schedule",
    "telegram_bot": "/api/telegram",
    "voice": "/api/voice",
    "voice_cmd": "/api/voice-cmd",
    "voice_tts": "/api/voice-tts",
    "plant_id": "/api/plant",
    "language": "/api/language",
    "language_hub": "/api/language-hub",
    "search": "/api/search",
    "social": "/api/social",
    "govt": "/api/govt",
    "upi": "/api/upi",
    "adminpanel": "/api/admin",
    "entertainment": "/api/entertainment",
    "banking": "/api/banking",
    "currency": "/api/currency",
    "railway": "/api/railway",
    "karmachari": "/api/karmachari",
    "pani": "/api/pani",
    "rozgar": "/api/rozgar",
    "sewer": "/api/sewer",
}

# ===== AUTO-LOAD ALL MODULES =====
loaded_modules = []
failed_modules = []

for module_name in MODULES:
    try:
        module = importlib.import_module(f"modules.{module_name}")
        if hasattr(module, "router"):
            prefix = ROUTER_PREFIX.get(module_name, f"/api/{module_name}")
            app.include_router(module.router, prefix=prefix, tags=[module_name.replace("_", " ").title()])
            loaded_modules.append(module_name)
        else:
            failed_modules.append(f"{module_name}: no router found")
    except Exception as e:
        failed_modules.append(f"{module_name}: {str(e)}")

# ===== ROOT ENDPOINT =====
@app.get("/")
async def root():
    return {
        "app": "Singh Ji AI Ultra v5.0",
        "status": "🔥 LIVE",
        "owner": "👑 Singh Ji (JP Singh Ji Kanpur)",
        "guru": "🤖 Moonshot AI",
        "mantra": "KELA mode — केला नहीं होता भाई अकेला!",
        "total_modules": len(loaded_modules),
        "loaded": loaded_modules,
        "failed": failed_modules if failed_modules else [],
        "message": f"{len(loaded_modules)}/{len(MODULES)} modules active!"
    }

# ===== HEALTH CHECKS =====
@app.get("/health")
async def health_check():
    return {"app": "Singh Ji AI Ultra v5.0", "status": "🔥 LIVE", "timestamp": "2026-06-29"}

@app.get("/api/health")
async def health():
    return {
        "status": "✅ ALL SYSTEMS GO",
        "version": "5.0.0",
        "phase": "5 — ULTRA",
        "loaded_modules": len(loaded_modules),
        "failed_modules": len(failed_modules)
    }

@app.get("/api/status")
async def status():
    return {
        "app": "Singh Ji AI Ultra v5.0",
        "status": "LIVE",
        "total_agents": len(loaded_modules),
        "agents": loaded_modules,
        "failed": failed_modules if failed_modules else []
    }

@app.head("/")
async def head_root():
    return {}

@app.post("/api/command")
async def singhji_command(request: Request):
    data = await request.json()
    return {
        "status": "executed",
        "command": data.get("action", "unknown"),
        "by": "👑 Singh Ji",
        "message": "Singh Ji ka hukum — sar aankhon pe!"
    }

# ===== STARTUP =====
@app.on_event("startup")
async def startup():
    print("🔥 Singh Ji AI Ultra v5.0 STARTED!")
    print(f"✅ Loaded: {len(loaded_modules)} modules")
    if failed_modules:
        print(f"❌ Failed: {failed_modules}")
    print("👑 Singh Ji ka raj shuru!")
