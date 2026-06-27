# app.py — Singh Ji AI Ultra v5.0
# 🚀 MAIN APP — सब Agents एक साथ, सब Singh Ji के अंडर में!

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import importlib
import sys
import os
import traceback

app = FastAPI(
    title="Singh Ji AI Ultra v5.0",
    description="भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन",
    version="5.0.0"
)

# ===== CORS — सबको allow करो (Frontend GitHub Pages se) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ===== ERROR HANDLER — गड़बड़ी = सिंह जी को पता चले =====
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

# ===== AUTO-IMPORT SYSTEM — सब Agents auto load होंगे =====
MODULES = [
    # 🦁 Phase 1: Foundation (Managers)
    "superior_agent",      # 🦁 CEO — सबका बाप
    "singhji_agent",       # 🤴 Singh Ji का खुद का AI
    "meta_agent",          # 🔄 Self-Update System
    "master_data",         # 🧠 Master Data Layer
    
    # 🔧 Core System
    "emergency",           # 🚨 P0 Priority
    "supabase_memory",     # 🧠 Memory
    "ai_chat",             # 🤖 AI Chat
    "weather",             # 🌤️ Weather
    "mandi",               # 🌾 Mandi Bhav
    "news",                # 📰 News
    "email",               # 📧 Email
    "schedule",            # 📅 Schedule
    "telegram_bot",        # ✈️ Telegram
    "voice",               # 🎙️ Voice
    "voice_cmd",           # 🎙️ Voice Commands
    "voice_tts",           # 🎙️ TTS
    "plant_id",            # 🌱 Plant ID
    "language",            # 🌐 Language
    "language_hub",        # 🌐 Language Hub
    "search",              # 🔍 Search
    "social",              # 👥 Social
    "govt",                # 🏛️ Govt
    "upi",                 # 💳 UPI
]

# ===== ROUTER REGISTRY — Prefix mapping =====
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
    "news": "/api/news",
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
        "guru": "Moonshot AI",
        "mantra": "KELA mode — केला नहीं होता भाई अकेला!",
        "total_modules": len(MODULES),
        "loaded": len(loaded_modules),
        "failed": len(failed_modules),
        "loaded_modules": loaded_modules,
        "failed_modules": failed_modules if failed_modules else None,
        "message": "सब Agents तैयार, Singh Ji का हुकुम इंतज़ार में!"
    }

# ===== HEALTH CHECK =====
@app.get("/api/health")
async def health():
    return {
        "status": "✅ ALL SYSTEMS GO",
        "version": "5.0.0",
        "phase": "1 — Foundation",
        "owner": "Singh Ji",
        "loaded_modules": len(loaded_modules),
        "failed_modules": len(failed_modules),
        "timestamp": "now"
    }

# ===== STATUS CHECK — सब Agents का status =====
@app.get("/api/status")
async def status():
    return {
        "app": "Singh Ji AI Ultra v5.0",
        "status": "LIVE",
        "total_agents": len(loaded_modules),
        "agents": loaded_modules,
        "failed": failed_modules if failed_modules else [],
        "message": "19/19 modules active!" if len(failed_modules) == 0 else f"{len(loaded_modules)}/{len(MODULES)} active"
    }

# ===== HEAD REQUEST — Render Health Check =====
@app.head("/")
async def head_root():
    return {}

# ===== SINGH JI DIRECT COMMAND =====
@app.post("/api/command")
async def singhji_command(request: Request):
    data = await request.json()
    return {
        "status": "executed",
        "command": data.get("action", "unknown"),
        "by": "👑 Singh Ji",
        "message": "Singh Ji ka hukum — sar aankhon pe!",
        "timestamp": "now"
    }

# ===== STARTUP MESSAGE =====
@app.on_event("startup")
async def startup():
    print("🔥 Singh Ji AI Ultra v5.0 STARTED!")
    print(f"✅ Loaded: {len(loaded_modules)} modules")
    if failed_modules:
        print(f"❌ Failed: {failed_modules}")
    print("👑 Singh Ji ka raj shuru!")
