"""
🦁 SINGH JI AI ULTRA v7.0 — SARWAN 330 AGENT SWARM
Hybrid API: Railway (Primary) + Render (Fallback)
API Key Check: Missing key = graceful error, not crash
"""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import json
import asyncio
import aiohttp
import importlib.util
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🦁 ALL 26 API KEYS — Check which are available
# ═══════════════════════════════════════════════════════
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MAGIC_HOUR_API_KEY = os.getenv("MAGIC_HOUR_API_KEY")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
PLANT_ID_API = os.getenv("PLANT_ID_API")
PLANT_ID_URL = os.getenv("PLANT_ID_URL")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = os.getenv("TAVILY_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TZ = os.getenv("TZ", "Asia/Kolkata")

# Check available keys
AVAILABLE_KEYS = {
    "OPENWEATHER": bool(OPENWEATHER_API_KEY),
    "CURRENTS": bool(CURRENTS_API_KEY),
    "GROQ": bool(GROQ_API_KEY),
    "GEMINI": bool(GEMINI_API_KEY),
    "TELEGRAM": bool(TELEGRAM_TOKEN),
}

# ═══════════════════════════════════════════════════════
# 🦁 FALLBACK URLS — Render as backup
# ═══════════════════════════════════════════════════════
RENDER_URL = "https://singhji-api.onrender.com"

# ═══════════════════════════════════════════════════════
# 🦁 FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(
    title="🦁 Singh Ji AI Ultra v7.0",
    version="7.0.0-sarwan-hybrid",
    description="330 Agent Swarm | Hybrid API | Railway Primary + Render Fallback"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════
# 🦁 GLOBAL STORES
# ═══════════════════════════════════════════════════════
MODULES = {}
MEMORY_STORE = {}
AGENT_SWARM = {}
AGENT_QUEUE = []
AGENT_SCHEDULE = {}
USER_SESSIONS = {}
SYSTEM_LOAD = {"active_agents": 0, "max_agents": 100, "phase": 0}

MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")

# ═══════════════════════════════════════════════════════
# 🦁 SARWAN 330 AGENT DEFINITIONS
# ═══════════════════════════════════════════════════════
AGENT_DEFINITIONS = {}

for i in range(1, 101):
    AGENT_DEFINITIONS[f"agent_{i:03d}"] = {
        "phase": 1, "type": "core", "delay_minutes": 0,
        "priority": "critical", "role": "system"
    }

for i in range(101, 201):
    AGENT_DEFINITIONS[f"agent_{i:03d}"] = {
        "phase": 2, "type": "service", "delay_minutes": 5,
        "priority": "high", "role": "api"
    }

for i in range(201, 331):
    AGENT_DEFINITIONS[f"agent_{i:03d}"] = {
        "phase": 3, "type": "specialized", "delay_minutes": 10,
        "priority": "medium", "role": "ai"
    }

# ═══════════════════════════════════════════════════════
# 🦁 MODULE DISCOVERY
# ═══════════════════════════════════════════════════════
def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR):
        return modules
    try:
        for item in os.listdir(MODULES_DIR):
            item_path = os.path.join(MODULES_DIR, item)
            if os.path.isdir(item_path) and not item.startswith("__"):
                handler_path = os.path.join(item_path, "handler.py")
                if os.path.exists(handler_path):
                    modules[item] = {"type": "folder", "path": handler_path}
            elif item.endswith(".py") and not item.startswith("__"):
                modules[item[:-3]] = {"type": "file", "path": item_path}
    except Exception as e:
        logger.error(f"Module discovery error: {e}")
    return modules

def load_module(name, info):
    try:
        if info["type"] == "folder":
            spec = importlib.util.spec_from_file_location(f"modules.{name}", info["path"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"modules.{name}"] = module
            spec.loader.exec_module(module)
            router = getattr(module, "router", None)
            if router:
                app.include_router(router)
                return "router_mounted"
            return getattr(module, "handler", None)
        else:
            spec = importlib.util.spec_from_file_location(name, info["path"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            router = getattr(module, "router", None)
            if router:
                app.include_router(router)
                return "router_mounted"
            return getattr(module, "handler", None)
    except Exception as e:
        logger.error(f"Failed {name}: {e}")
        return None

# ═══════════════════════════════════════════════════════
# 🦁 SYSTEM LOAD CHECK
# ═══════════════════════════════════════════════════════
async def check_system_load():
    active = SYSTEM_LOAD["active_agents"]
    max_allowed = SYSTEM_LOAD["max_agents"]
    if active >= max_allowed:
        return False
    load_percent = (active / max_allowed) * 100
    return load_percent < 90

# ═══════════════════════════════════════════════════════
# 🦁 FALLBACK FETCH — Try Railway first, then Render
# ═══════════════════════════════════════════════════════
async def fallback_fetch(endpoint: str, method="GET", data=None, headers=None):
    """Try Railway first, fallback to Render if key missing or fails"""
    urls = [
        f"{RENDER_URL}{endpoint}",  # Render has keys
    ]
    
    # Try Render first (it has all keys)
    for url in urls:
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), headers=headers or {}) as resp:
                        if resp.status == 200:
                            return await resp.json()
                elif method == "POST":
                    async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=15), headers=headers or {}) as resp:
                        if resp.status == 200:
                            return await resp.json()
        except Exception as e:
            logger.warning(f"Fallback fetch failed for {url}: {e}")
            continue
    
    return None

# ═══════════════════════════════════════════════════════
# 🦁 SARWAN AGENT SCHEDULER
# ═══════════════════════════════════════════════════════
async def sarwan_scheduler():
    await asyncio.sleep(30)
    
    phases = [1, 2, 3]
    phase_delays = {1: 0, 2: 300, 3: 600}
    
    for phase in phases:
        SYSTEM_LOAD["phase"] = phase
        logger.info(f"🦁 Sarwan Phase {phase} starting...")
        await asyncio.sleep(phase_delays[phase])
        
        phase_agents = [k for k, v in AGENT_DEFINITIONS.items() if v["phase"] == phase]
        
        for agent_id in phase_agents:
            can_add = await check_system_load()
            if not can_add:
                AGENT_QUEUE.append(agent_id)
                await asyncio.sleep(5)
                continue
            
            AGENT_SWARM[agent_id] = {
                "id": agent_id,
                "type": AGENT_DEFINITIONS[agent_id]["type"],
                "phase": phase,
                "status": "active",
                "registered_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "tasks_completed": 0,
                "config": {
                    "auto_execute": False,
                    "max_tasks_per_minute": 10,
                    "cooldown_seconds": 6
                }
            }
            SYSTEM_LOAD["active_agents"] += 1
            
            if int(agent_id.split("_")[1]) % 10 == 0:
                logger.info(f"✅ {agent_id} activated (Phase {phase})")
            
            await asyncio.sleep(0.2)
        
        logger.info(f"🦁 Phase {phase} complete: {len([a for a in AGENT_SWARM.values() if a.get('phase')==phase])} agents")
    
    while AGENT_QUEUE:
        can_add = await check_system_load()
        if can_add:
            agent_id = AGENT_QUEUE.pop(0)
            AGENT_SWARM[agent_id] = {
                "id": agent_id,
                "type": AGENT_DEFINITIONS[agent_id]["type"],
                "phase": AGENT_DEFINITIONS[agent_id]["phase"],
                "status": "active",
                "registered_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "tasks_completed": 0,
                "config": {"auto_execute": False, "max_tasks_per_minute": 10, "cooldown_seconds": 6}
            }
            SYSTEM_LOAD["active_agents"] += 1
        await asyncio.sleep(10)
    
    logger.info("🦁 SARWAN 330 ALL ACTIVE!")

# ═══════════════════════════════════════════════════════
# 🦁 SELF-PING
# ═══════════════════════════════════════════════════════
async def self_ping():
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://singhji-api-production-85ca.up.railway.app/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    logger.info(f"🦁 Self-ping: {resp.status}")
        except Exception as e:
            logger.error(f"Self-ping: {e}")
        await asyncio.sleep(10 * 60)

# ═══════════════════════════════════════════════════════
# 🦁 STARTUP
# ═══════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    try:
        all_modules = discover_modules()
        for name, info in all_modules.items():
            result = load_module(name, info)
            if result:
                MODULES[name] = result
        
        logger.info(f"🦁 {len(MODULES)} modules ready")
        logger.info(f"🦁 Available API Keys: {AVAILABLE_KEYS}")
        
        asyncio.create_task(sarwan_scheduler())
        asyncio.create_task(self_ping())
        
        logger.info("🦁 Sarwan 330 Swarm scheduler started")
    except Exception as e:
        logger.error(f"Startup error: {e}")

# ═══════════════════════════════════════════════════════
# 🦁 HEALTH
# ═══════════════════════════════════════════════════════
@app.get("/")
@app.head("/")
async def root():
    return {
        "name": "🦁 Singh Ji AI Ultra v7.0",
        "version": "7.0.0-sarwan-hybrid",
        "modules": len(MODULES),
        "agents_active": SYSTEM_LOAD["active_agents"],
        "agents_queued": len(AGENT_QUEUE),
        "phase": SYSTEM_LOAD["phase"],
        "available_keys": AVAILABLE_KEYS,
        "status": "🦁 LIVE",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
@app.head("/health")
def health():
    return {
        "status": "ok",
        "service": "Singh Ji AI",
        "agents": SYSTEM_LOAD["active_agents"],
        "available_keys": {k: v for k, v in AVAILABLE_KEYS.items()}
    }

@app.get("/api/health")
@app.head("/api/health")
def api_health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def status():
    return {
        "name": "Singh Ji AI v7.0 Sarwan Hybrid",
        "modules": len(MODULES),
        "agents": {
            "total": 330,
            "active": SYSTEM_LOAD["active_agents"],
            "queued": len(AGENT_QUEUE),
            "phase": SYSTEM_LOAD["phase"],
            "phases": {
                "phase_1": len([a for a in AGENT_SWARM.values() if a.get("phase") == 1]),
                "phase_2": len([a for a in AGENT_SWARM.values() if a.get("phase") == 2]),
                "phase_3": len([a for a in AGENT_SWARM.values() if a.get("phase") == 3])
            }
        },
        "available_keys": AVAILABLE_KEYS,
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 DYNAMIC MODULE ROUTER
# ═══════════════════════════════════════════════════════
async def run_handler(module_name: str, request: Request):
    handler_func = MODULES[module_name]
    if handler_func == "router_mounted":
        return JSONResponse(status_code=400, content={"error": "Use direct route path"})
    try:
        if asyncio.iscoroutinefunction(handler_func):
            result = await handler_func(request)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, handler_func, request)
        if isinstance(result, dict) and "statusCode" in result:
            return JSONResponse(status_code=result.get("statusCode", 200), content=json.loads(result.get("body", "{}")) if isinstance(result.get("body"), str) else result.get("body"))
        return JSONResponse(content=result) if isinstance(result, dict) else result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.api_route("/api/{module_name}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
async def dynamic_router(request: Request, module_name: str):
    if module_name not in MODULES:
        all_modules = discover_modules()
        if module_name in all_modules:
            handler = load_module(module_name, all_modules[module_name])
            if handler:
                MODULES[module_name] = handler
            else:
                return JSONResponse(status_code=404, content={"error": f"'{module_name}' failed to load"})
        else:
            return JSONResponse(status_code=404, content={"error": f"'{module_name}' not found", "available": list(discover_modules().keys())})
    return await run_handler(module_name, request)

# ═══════════════════════════════════════════════════════
# 🦁 MEMORY MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/memory/")
async def memory_list():
    return {"status": "Memory Active", "records": len(MEMORY_STORE), "keys": list(MEMORY_STORE.keys())[:20]}

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return {"key": key, "data": MEMORY_STORE.get(key), "exists": key in MEMORY_STORE}

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(datetime.now().timestamp()))
    MEMORY_STORE[key] = data.get("value", data)
    return {"saved": True, "key": key, "total": len(MEMORY_STORE)}

@app.delete("/api/memory/{key}")
async def memory_delete(key: str):
    if key in MEMORY_STORE:
        del MEMORY_STORE[key]
        return {"deleted": True}
    return {"deleted": False, "error": "Key not found"}

# ═══════════════════════════════════════════════════════
# 🦁 WEATHER MODULE — WITH FALLBACK TO RENDER
# ═══════════════════════════════════════════════════════
@app.get("/api/weather/")
async def weather_root():
    return {"module": "Weather", "status": "active", "source": "Railway Primary"}

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    # Try Railway first (if key available)
    if OPENWEATHER_API_KEY:
        try:
            import requests
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if resp.status_code == 200:
                return {
                    "city": city,
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "desc": data["weather"][0]["description"],
                    "source": "Railway"
                }
        except Exception as e:
            logger.warning(f"Railway weather failed: {e}")
    
    # Fallback to Render
    try:
        fallback_data = await fallback_fetch(f"/api/weather/{city}")
        if fallback_data:
            fallback_data["source"] = "Render (Fallback)"
            return fallback_data
    except Exception as e:
        logger.warning(f"Render weather fallback failed: {e}")
    
    # No keys available — return demo data
    return {
        "city": city,
        "temp": 32.0,
        "humidity": 65,
        "desc": "haze (demo — add OPENWEATHER_API_KEY to Railway)",
        "source": "DEMO",
        "note": "Add OPENWEATHER_API_KEY to Railway Variables or use Render API"
    }

# ═══════════════════════════════════════════════════════
# 🦁 NEWS MODULE — WITH FALLBACK
# ═══════════════════════════════════════════════════════
@app.get("/api/news/")
async def news_root():
    return {"module": "News", "status": "active"}

@app.get("/api/news/latest")
async def news_latest():
    if CURRENTS_API_KEY:
        try:
            import requests
            resp = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}", timeout=10)
            return resp.json()
        except Exception as e:
            logger.warning(f"Railway news failed: {e}")
    
    # Fallback to Render
    fallback_data = await fallback_fetch("/api/news/latest")
    if fallback_data:
        fallback_data["source"] = "Render (Fallback)"
        return fallback_data
    
    return {
        "status": "demo",
        "news": [
            {"title": "🦁 Singh Ji AI News", "description": "Add CURRENTS_API_KEY to Railway", "url": "#"}
        ],
        "source": "DEMO"
    }

# ═══════════════════════════════════════════════════════
# 🦁 MANDI MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/mandi/")
async def mandi_root():
    return {"module": "Mandi", "status": "active"}

@app.get("/api/mandi/{state}")
async def mandi_state(state: str):
    return {"state": state, "commodities": ["Wheat", "Rice", "Corn", "Soybean", "Cotton"]}

# ═══════════════════════════════════════════════════════
# 🦁 PLANT ID MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/plant/")
async def plant_root():
    return {"module": "Plant ID", "status": "active"}

@app.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "API key not set", "note": "Add PLANT_ID_API to Railway Variables"}
    data = await request.json()
    return {"status": "pending", "image": data.get("image_url", "none")}

# ═══════════════════════════════════════════════════════
# 🦁 PAYMENT MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/payment/")
async def payment_root():
    return {
        "module": "Singh Ji Payment Gateway",
        "status": "ON_HOLD",
        "activate_at": "1000+ daily users",
        "upi_id": "jp200883@sbi"
    }

# ═══════════════════════════════════════════════════════
# 🦁 ADMIN MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/")
async def admin_root():
    return {
        "module": "Admin",
        "modules": len(MODULES),
        "memory": len(MEMORY_STORE),
        "agents": {
            "total": 330,
            "active": SYSTEM_LOAD["active_agents"],
            "queued": len(AGENT_QUEUE),
            "phase": SYSTEM_LOAD["phase"]
        },
        "available_keys": AVAILABLE_KEYS
    }

@app.get("/api/admin/stats")
async def admin_stats():
    return {
        "modules": len(MODULES),
        "memory": len(MEMORY_STORE),
        "agents_active": SYSTEM_LOAD["active_agents"],
        "agents_queued": len(AGENT_QUEUE),
        "phase": SYSTEM_LOAD["phase"],
        "load": f"{(SYSTEM_LOAD['active_agents']/SYSTEM_LOAD['max_agents']*100):.1f}%",
        "available_keys": AVAILABLE_KEYS,
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 SARWAN 330 SWARM ROUTES
# ═══════════════════════════════════════════════════════
@app.get("/api/swarm/")
async def swarm_root():
    return {
        "module": "Sarwan 330 Agent Swarm",
        "status": "active",
        "total": 330,
        "active": SYSTEM_LOAD["active_agents"],
        "queued": len(AGENT_QUEUE),
        "current_phase": SYSTEM_LOAD["phase"],
        "max_concurrent": SYSTEM_LOAD["max_agents"],
        "phases": {
            "phase_1": {"range": "1-100", "type": "Core", "delay": "0 min", "status": "active" if SYSTEM_LOAD["phase"] >= 1 else "pending"},
            "phase_2": {"range": "101-200", "type": "Service", "delay": "5 min", "status": "active" if SYSTEM_LOAD["phase"] >= 2 else "pending"},
            "phase_3": {"range": "201-330", "type": "Specialized", "delay": "10 min", "status": "active" if SYSTEM_LOAD["phase"] >= 3 else "pending"}
        }
    }

@app.get("/api/swarm/agents")
async def swarm_list():
    return {
        "total": len(AGENT_SWARM),
        "active": SYSTEM_LOAD["active_agents"],
        "queued": len(AGENT_QUEUE),
        "sample": {k: {"type": v["type"], "phase": v["phase"], "status": v["status"]} 
                   for k, v in list(AGENT_SWARM.items())[:10]}
    }

@app.get("/api/swarm/agent/{agent_id}")
async def swarm_agent_get(agent_id: str):
    if agent_id in AGENT_SWARM:
        return AGENT_SWARM[agent_id]
    if agent_id in AGENT_QUEUE:
        return {"agent_id": agent_id, "status": "queued", "position": AGENT_QUEUE.index(agent_id)}
    if agent_id in AGENT_DEFINITIONS:
        return {"agent_id": agent_id, "status": "scheduled", "phase": AGENT_DEFINITIONS[agent_id]["phase"]}
    return {"error": "Agent not found"}

@app.post("/api/swarm/agent/{agent_id}/execute")
async def swarm_agent_execute(agent_id: str, request: Request):
    if agent_id not in AGENT_SWARM:
        return {"error": "Agent not active yet"}
    data = await request.json()
    task = data.get("task", "unknown")
    AGENT_SWARM[agent_id]["last_active"] = datetime.now().isoformat()
    AGENT_SWARM[agent_id]["tasks_completed"] += 1
    return {
        "agent_id": agent_id,
        "task": task,
        "status": "executed",
        "tasks_completed": AGENT_SWARM[agent_id]["tasks_completed"]
    }

@app.post("/api/swarm/broadcast")
async def swarm_broadcast(request: Request):
    data = await request.json()
    message = data.get("message", "")
    targets = data.get("targets", list(AGENT_SWARM.keys())[:10])
    results = []
    for agent_id in targets:
        if agent_id in AGENT_SWARM:
            AGENT_SWARM[agent_id]["last_active"] = datetime.now().isoformat()
            results.append({"agent": agent_id, "status": "received"})
    return {"broadcast": True, "message": message, "recipients": len(results)}

# ═══════════════════════════════════════════════════════
# 🦁 RETIREMENT TAX MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/retirement/")
async def retirement_root():
    return {"module": "Retirement & Tax", "features": ["PF", "NPS", "Tax", "SIP"]}

@app.post("/api/retirement/tax-calculate")
async def retirement_tax(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")
    tax = 0
    if regime == "new":
        if income <= 300000: tax = 0
        elif income <= 600000: tax = (income - 300000) * 0.05
        elif income <= 900000: tax = 15000 + (income - 600000) * 0.10
        elif income <= 1200000: tax = 45000 + (income - 900000) * 0.15
        elif income <= 1500000: tax = 90000 + (income - 1200000) * 0.20
        else: tax = 150000 + (income - 1500000) * 0.30
    else:
        taxable = max(0, income - 50000 - data.get("deductions", 0))
        if taxable <= 250000: tax = 0
        elif taxable <= 500000: tax = (taxable - 250000) * 0.05
        elif taxable <= 1000000: tax = 12500 + (taxable - 500000) * 0.20
        else: tax = 112500 + (taxable - 1000000) * 0.30
    cess = tax * 0.04
    return {
        "income": income,
        "regime": regime,
        "tax": round(tax, 2),
        "cess": round(cess, 2),
        "total": round(tax + cess, 2),
        "take_home": round(income - tax - cess, 2)
    }

# ═══════════════════════════════════════════════════════
# 🦁 TELEGRAM WEBHOOK
# ═══════════════════════════════════════════════════════
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        message = data.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        if text == '/status':
            reply = f"🦁 Singh Ji AI\nAgents: {SYSTEM_LOAD['active_agents']}/330\nPhase: {SYSTEM_LOAD['phase']}"
        else:
            reply = "🦁 Singh Ji AI Bot\nCommands: /status"
        if TELEGRAM_TOKEN and chat_id:
            import requests
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"}, timeout=10)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Telegram: {e}")
        return {"status": "ok"}

# ═══════════════════════════════════════════════════════
# 🦁 RUN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
