"""
🦁 SINGH JI AI ULTRA v7.0 — AGENT SWARM SCHEDULER
Phased deployment | Queue system | Zero overload
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
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🦁 ALL 26 API KEYS
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

# ═══════════════════════════════════════════════════════
# 🦁 FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(
    title="🦁 Singh Ji AI Ultra v7.0",
    version="7.0.0-swarm",
    description="60 Modules | 330 Agent Swarm | Phased Deployment"
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
AGENT_QUEUE = []  # Pending agents queue
AGENT_SCHEDULE = {}  # Schedule tracker
USER_SESSIONS = {}
SYSTEM_LOAD = {"cpu": 0, "memory": 0, "active_agents": 0, "max_agents": 50}  # Max 50 concurrent

MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")

# ═══════════════════════════════════════════════════════
# 🦁 330 AGENT DEFINITIONS
# ═══════════════════════════════════════════════════════
AGENT_DEFINITIONS = {
    # Phase 1: Core Agents (1-100)
    **{f"agent_{i:03d}": {
        "phase": 1,
        "type": "core",
        "delay_minutes": 0,
        "priority": "critical"
    } for i in range(1, 101)},
    
    # Phase 2: Service Agents (101-200)
    **{f"agent_{i:03d}": {
        "phase": 2,
        "type": "service",
        "delay_minutes": 5,
        "priority": "high"
    } for i in range(101, 201)},
    
    # Phase 3: Specialized Agents (201-330)
    **{f"agent_{i:03d}": {
        "phase": 3,
        "type": "specialized",
        "delay_minutes": 10,
        "priority": "medium"
    } for i in range(201, 331)}
}

# ═══════════════════════════════════════════════════════
# 🦁 MODULE DISCOVERY
# ═══════════════════════════════════════════════════════
def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR):
        return modules
    for item in os.listdir(MODULES_DIR):
        item_path = os.path.join(MODULES_DIR, item)
        if os.path.isdir(item_path) and not item.startswith("__"):
            handler_path = os.path.join(item_path, "handler.py")
            if os.path.exists(handler_path):
                modules[item] = {"type": "folder", "path": handler_path}
        elif item.endswith(".py") and not item.startswith("__"):
            modules[item[:-3]] = {"type": "file", "path": item_path}
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
        logger.error(f"❌ Failed {name}: {e}")
        return None

# ═══════════════════════════════════════════════════════
# 🦁 SYSTEM LOAD CHECKER
# ═══════════════════════════════════════════════════════
async def check_system_load():
    """Check if system can handle more agents"""
    active = SYSTEM_LOAD["active_agents"]
    max_allowed = SYSTEM_LOAD["max_agents"]
    
    if active >= max_allowed:
        logger.warning(f"⚠️ System at capacity: {active}/{max_allowed} agents")
        return False
    
    # Simulate load check (in real: check CPU/memory)
    load_percent = (active / max_allowed) * 100
    logger.info(f"🦁 System load: {load_percent:.1f}% ({active}/{max_allowed})")
    return load_percent < 80  # Only add if under 80%

# ═══════════════════════════════════════════════════════
# 🦁 AGENT SCHEDULER
# ═══════════════════════════════════════════════════════
async def agent_scheduler():
    """Background task: Activate agents in phases"""
    await asyncio.sleep(30)  # Wait 30s after startup
    
    phases = [1, 2, 3]
    phase_delays = {1: 0, 2: 300, 3: 600}  # 0min, 5min, 10min
    
    for phase in phases:
        logger.info(f"🦁 Phase {phase} starting in {phase_delays[phase]} seconds...")
        await asyncio.sleep(phase_delays[phase])
        
        phase_agents = [k for k, v in AGENT_DEFINITIONS.items() if v["phase"] == phase]
        logger.info(f"🦁 Phase {phase}: {len(phase_agents)} agents to activate")
        
        for agent_id in phase_agents:
            # Check system load before adding
            can_add = await check_system_load()
            if not can_add:
                logger.warning(f"⏳ Queueing {agent_id} - system busy")
                AGENT_QUEUE.append(agent_id)
                await asyncio.sleep(5)
                continue
            
            # Register agent
            AGENT_SWARM[agent_id] = {
                "id": agent_id,
                "type": AGENT_DEFINITIONS[agent_id]["type"],
                "phase": phase,
                "status": "active",
                "registered_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "tasks_completed": 0,
                "config": {
                    "auto_execute": False,  # Don't auto-run tasks
                    "max_tasks_per_minute": 10,  # Rate limit
                    "cooldown_seconds": 6  # 6s between tasks
                }
            }
            SYSTEM_LOAD["active_agents"] += 1
            logger.info(f"✅ {agent_id} activated (Phase {phase})")
            
            # Small delay between agents to prevent spike
            await asyncio.sleep(0.5)  # 2 agents per second max
        
        logger.info(f"🦁 Phase {phase} complete: {len([a for a in AGENT_SWARM.values() if a['phase']==phase])} agents active")
    
    # Process queued agents
    logger.info(f"🦁 Processing {len(AGENT_QUEUE)} queued agents...")
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
            logger.info(f"✅ Queued {agent_id} now activated")
        await asyncio.sleep(10)
    
    logger.info(f"🦁 ALL 330 AGENTS ACTIVE! Swarm ready!")

# ═══════════════════════════════════════════════════════
# 🦁 AGENT TASK EXECUTOR (Rate Limited)
# ═══════════════════════════════════════════════════════
async def execute_agent_task(agent_id: str, task: str):
    """Execute task with rate limiting"""
    if agent_id not in AGENT_SWARM:
        return {"error": "Agent not found"}
    
    agent = AGENT_SWARM[agent_id]
    
    # Check rate limit
    last_active = datetime.fromisoformat(agent["last_active"])
    cooldown = agent["config"]["cooldown_seconds"]
    time_since = (datetime.now() - last_active).total_seconds()
    
    if time_since < cooldown:
        wait_time = cooldown - time_since
        logger.warning(f"⏳ {agent_id} rate limited. Wait {wait_time:.1f}s")
        await asyncio.sleep(wait_time)
    
    # Execute
    agent["last_active"] = datetime.now().isoformat()
    agent["tasks_completed"] += 1
    
    # Simulate work
    await asyncio.sleep(0.1)
    
    return {
        "agent_id": agent_id,
        "task": task,
        "status": "executed",
        "result": f"Task '{task}' completed by {agent_id}",
        "tasks_completed": agent["tasks_completed"]
    }

# ═══════════════════════════════════════════════════════
# 🦁 SELF-PING
# ═══════════════════════════════════════════════════════
async def self_ping():
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://singhji-api-production-85ca.up.railway.app/api/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    logger.info(f"🦁 Self-ping: {resp.status}")
        except Exception as e:
            logger.error(f"❌ Self-ping: {e}")
        await asyncio.sleep(10 * 60)

# ═══════════════════════════════════════════════════════
# 🦁 STARTUP
# ═══════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    all_modules = discover_modules()
    for name, info in all_modules.items():
        result = load_module(name, info)
        if result:
            MODULES[name] = result
    
    logger.info(f"🦁 {len(MODULES)} modules ready")
    
    # Start background tasks
    asyncio.create_task(self_ping())
    asyncio.create_task(agent_scheduler())
    
    logger.info("🦁 Agent scheduler started - Phased deployment active")

# ═══════════════════════════════════════════════════════
# 🦁 ROOT & HEALTH
# ═══════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "name": "🦁 Singh Ji AI Ultra v7.0",
        "version": "7.0.0-swarm",
        "modules": len(MODULES),
        "agents_active": SYSTEM_LOAD["active_agents"],
        "agents_queued": len(AGENT_QUEUE),
        "status": "🦁 LIVE",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "load": f"{SYSTEM_LOAD['active_agents']}/{SYSTEM_LOAD['max_agents']}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def status():
    return {
        "modules": len(MODULES),
        "agents": {
            "total": 330,
            "active": SYSTEM_LOAD["active_agents"],
            "queued": len(AGENT_QUEUE),
            "phases": {
                "phase_1": len([a for a in AGENT_SWARM.values() if a.get("phase") == 1]),
                "phase_2": len([a for a in AGENT_SWARM.values() if a.get("phase") == 2]),
                "phase_3": len([a for a in AGENT_SWARM.values() if a.get("phase") == 3])
            }
        },
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 SWARM ROUTES
# ═══════════════════════════════════════════════════════
@app.get("/api/swarm/")
async def swarm_root():
    return {
        "module": "330 Agent Swarm",
        "status": "active",
        "total": 330,
        "active": SYSTEM_LOAD["active_agents"],
        "queued": len(AGENT_QUEUE),
        "max_concurrent": SYSTEM_LOAD["max_agents"],
        "phases": {
            "phase_1": "Core Agents (1-100) - Immediate",
            "phase_2": "Service Agents (101-200) - After 5 min",
            "phase_3": "Specialized Agents (201-330) - After 10 min"
        }
    }

@app.get("/api/swarm/agents")
async def swarm_list():
    return {
        "total": len(AGENT_SWARM),
        "active": SYSTEM_LOAD["active_agents"],
        "queued": len(AGENT_QUEUE),
        "agents": {k: {
            "type": v["type"],
            "phase": v["phase"],
            "status": v["status"],
            "tasks": v["tasks_completed"]
        } for k, v in list(AGENT_SWARM.items())[:20]}  # Show first 20
    }

@app.get("/api/swarm/agent/{agent_id}")
async def swarm_agent_get(agent_id: str):
    if agent_id not in AGENT_SWARM:
        # Check if in queue
        if agent_id in AGENT_QUEUE:
            return {"agent_id": agent_id, "status": "queued", "position": AGENT_QUEUE.index(agent_id)}
        # Check if defined but not yet scheduled
        if agent_id in AGENT_DEFINITIONS:
            return {"agent_id": agent_id, "status": "scheduled", "phase": AGENT_DEFINITIONS[agent_id]["phase"]}
        return {"error": "Agent not found"}
    return AGENT_SWARM[agent_id]

@app.post("/api/swarm/agent/{agent_id}/execute")
async def swarm_agent_execute(agent_id: str, request: Request):
    data = await request.json()
    task = data.get("task", "unknown")
    result = await execute_agent_task(agent_id, task)
    return result

@app.post("/api/swarm/broadcast")
async def swarm_broadcast(request: Request):
    data = await request.json()
    message = data.get("message", "")
    targets = data.get("targets", list(AGENT_SWARM.keys())[:10])  # Max 10 at once
    
    results = []
    for agent_id in targets:
        if agent_id in AGENT_SWARM:
            result = await execute_agent_task(agent_id, "broadcast: " + message)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limit broadcasts
    
    return {
        "broadcast": True,
        "message": message,
        "recipients": len(results),
        "results": results
    }

# ═══════════════════════════════════════════════════════
# 🦁 MEMORY MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/memory/")
async def memory_list():
    return {"status": "Memory Active", "records": len(MEMORY_STORE), "keys": list(MEMORY_STORE.keys())[:20]}

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(datetime.now().timestamp()))
    MEMORY_STORE[key] = data.get("value", data)
    return {"saved": True, "key": key, "total": len(MEMORY_STORE)}

# ═══════════════════════════════════════════════════════
# 🦁 WEATHER MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/weather/")
async def weather_root():
    return {"module": "Weather", "status": "active"}

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    if not OPENWEATHER_API_KEY:
        return {"error": "API key not set"}
    try:
        import requests
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "desc": data["weather"][0]["description"]
            }
        return {"error": data.get("message")}
    except Exception as e:
        return {"error": str(e)}

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
            "queued": len(AGENT_QUEUE)
        }
    }

@app.get("/api/admin/stats")
async def admin_stats():
    return {
        "modules": len(MODULES),
        "memory": len(MEMORY_STORE),
        "agents_active": SYSTEM_LOAD["active_agents"],
        "agents_queued": len(AGENT_QUEUE),
        "system_load": f"{(SYSTEM_LOAD['active_agents']/SYSTEM_LOAD['max_agents']*100):.1f}%",
        "timestamp": datetime.now().isoformat()
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
            reply = f"🦁 Singh Ji AI\nAgents: {SYSTEM_LOAD['active_agents']}/330\nLoad: {(SYSTEM_LOAD['active_agents']/SYSTEM_LOAD['max_agents']*100):.0f}%"
        else:
            reply = "🦁 Singh Ji AI Bot\nCommands: /status"
        
        if TELEGRAM_TOKEN and chat_id:
            import requests
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"}, timeout=10)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return {"status": "ok"}

# ═══════════════════════════════════════════════════════
# 🦁 RUN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
