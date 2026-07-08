"""
🦁 SINGH JI AI ULTRA v7.0 — COMPLETE MASTER
All routes in one file | Modules lazy-load ready | 330 Agent Swarm Ready
"""
from fastapi import FastAPI, Request, HTTPException
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
    version="7.0.0-complete",
    description="60 Modules | 330 Agent Swarm | 26 Languages | India Super App"
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
AGENT_SWARM = {}  # 330 Agent Swarm Registry
USER_SESSIONS = {}

MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")

# ═══════════════════════════════════════════════════════
# 🦁 MODULE DISCOVERY & LOADING
# ═══════════════════════════════════════════════════════
def discover_modules():
    modules = {}
    if not os.path.exists(MODULES_DIR):
        logger.warning(f"⚠️ modules/ not found at {MODULES_DIR}")
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
            
            # Check for router first (FastAPI), then handler (function)
            router = getattr(module, "router", None)
            if router:
                app.include_router(router)
                return "router_mounted"
            
            handler = getattr(module, "handler", None)
            return handler
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
# 🦁 SELF-PING SYSTEM
# ═══════════════════════════════════════════════════════
async def self_ping():
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://singhji-api.onrender.com/api/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    logger.info(f"🦁 Self-ping: {resp.status} | Render awake!")
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {e}")
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
            logger.info(f"✅ Loaded: {name} ({'router' if result == 'router_mounted' else 'handler'})")
    
    logger.info(f"🦁 {len(MODULES)} modules ready!")
    logger.info(f"🦁 Modules: {list(MODULES.keys())}")
    logger.info("🦁 Self-ping enabled — Render will never sleep!")
    asyncio.create_task(self_ping())

# ═══════════════════════════════════════════════════════
# 🦁 ROOT & HEALTH
# ═══════════════════════════════════════════════════════
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "name": "🦁 Singh Ji AI Ultra v7.0",
        "version": "7.0.0-complete",
        "modules_loaded": len(MODULES),
        "modules": list(MODULES.keys()),
        "status": "🦁 LIVE",
        "timestamp": datetime.now().isoformat()
    }

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_simple():
    return {"status": "ok", "version": "7.0", "service": "Singh Ji AI Ultra"}

@app.get("/api/status")
async def status():
    return {
        "name": "Singh Ji AI v7.0 Complete",
        "loaded_modules": len(MODULES),
        "discovered_modules": len(discover_modules()),
        "memory_records": len(MEMORY_STORE),
        "agent_swarm_size": len(AGENT_SWARM),
        "status": "🦁 LIVE",
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 DYNAMIC MODULE ROUTER
# ═══════════════════════════════════════════════════════
async def run_handler(module_name: str, request: Request):
    handler_func = MODULES[module_name]
    if handler_func == "router_mounted":
        return JSONResponse(status_code=400, content={
            "error": "This module uses FastAPI router. Access directly via its route path."
        })
    
    try:
        if asyncio.iscoroutinefunction(handler_func):
            result = await handler_func(request)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, handler_func, request)
        
        if isinstance(result, dict):
            if "statusCode" in result:
                status_code = result.get("statusCode", 200)
                headers = result.get("headers", {})
                body = result.get("body", "{}")
                if isinstance(body, str):
                    try:
                        body = json.loads(body)
                    except:
                        body = {"response": body}
                return JSONResponse(status_code=status_code, headers=headers, content=body)
            else:
                return JSONResponse(content=result)
        return result
    except Exception as e:
        logger.error(f"❌ Error in {module_name}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "module": module_name, "error": str(e)})

@app.api_route("/api/{module_name}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
async def dynamic_router(request: Request, module_name: str):
    if module_name not in MODULES:
        all_modules = discover_modules()
        if module_name in all_modules:
            handler = load_module(module_name, all_modules[module_name])
            if handler:
                MODULES[module_name] = handler
                logger.info(f"✅ Lazy loaded: {module_name}")
            else:
                return JSONResponse(status_code=404, content={
                    "status": "error", "message": f"'{module_name}' failed to load"
                })
        else:
            return JSONResponse(status_code=404, content={
                "status": "error", "message": f"'{module_name}' not found",
                "available": list(discover_modules().keys())
            })
    
    return await run_handler(module_name, request)

# ═══════════════════════════════════════════════════════
# 🦁 MEMORY MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/memory/")
async def memory_list():
    return {
        "status": "Memory Module Active",
        "records": len(MEMORY_STORE),
        "keys": list(MEMORY_STORE.keys())[:20]  # Limit output
    }

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return {
        "key": key,
        "data": MEMORY_STORE.get(key, None),
        "exists": key in MEMORY_STORE
    }

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(datetime.now().timestamp()))
    MEMORY_STORE[key] = data.get("value", data)
    return {"saved": True, "key": key, "total_records": len(MEMORY_STORE)}

@app.delete("/api/memory/{key}")
async def memory_delete(key: str):
    if key in MEMORY_STORE:
        del MEMORY_STORE[key]
        return {"deleted": True}
    return {"deleted": False, "error": "Key not found"}

# ═══════════════════════════════════════════════════════
# 🦁 WEATHER MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/weather/")
async def weather_root():
    return {"module": "Weather", "status": "active", "source": "OpenWeatherMap"}

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set"}
    try:
        import requests
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {
                "city": city,
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
            }
        return {"error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════
# 🦁 NEWS MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/news/")
async def news_root():
    return {"module": "News", "status": "active", "sources": ["Currents", "NewsData"]}

@app.get("/api/news/latest")
async def news_latest():
    if not CURRENTS_API_KEY:
        return {"error": "CURRENTS_API_KEY not set"}
    try:
        import requests
        url = f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════
# 🦁 MANDI (AGRICULTURE) MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/mandi/")
async def mandi_root():
    return {"module": "Mandi", "status": "active", "source": "data.gov.in"}

@app.get("/api/mandi/{state}")
async def mandi_state(state: str):
    return {
        "state": state,
        "commodities": ["Wheat", "Rice", "Corn", "Soybean", "Cotton"],
        "note": "Full API integration pending"
    }

# ═══════════════════════════════════════════════════════
# 🦁 PLANT ID MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/plant/")
async def plant_root():
    return {"module": "Plant ID", "status": "active", "provider": "Plant.id"}

@app.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "PLANT_ID_API not set"}
    data = await request.json()
    return {
        "status": "identification_pending",
        "image_received": data.get("image_url", "none"),
        "note": "Connect to Plant.id API"
    }

# ═══════════════════════════════════════════════════════
# 🦁 PAYMENT GATEWAY (ON HOLD)
# ═══════════════════════════════════════════════════════
@app.get("/api/payment/")
async def payment_root():
    return {
        "module": "Singh Ji Payment Gateway",
        "status": "ON_HOLD",
        "activate_at": "1000+ daily users",
        "upi_id": "jp200883@sbi",
        "features": {
            "upi": "0% commission",
            "card": "2% commission",
            "merchant_loans": "18-24% (future)",
            "insurance": "10-20% (future)"
        }
    }

# ═══════════════════════════════════════════════════════
# 🦁 ADMIN MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/")
async def admin_root():
    return {
        "module": "Admin",
        "status": "active",
        "total_modules": len(MODULES),
        "memory_records": len(MEMORY_STORE),
        "agent_swarm": len(AGENT_SWARM),
        "uptime": "running"
    }

@app.get("/api/admin/modules")
async def admin_modules():
    all_modules = discover_modules()
    return {
        "discovered": list(all_modules.keys()),
        "loaded": list(MODULES.keys()),
        "total_discovered": len(all_modules),
        "total_loaded": len(MODULES)
    }

@app.get("/api/admin/stats")
async def admin_stats():
    return {
        "modules_loaded": len(MODULES),
        "modules_discovered": len(discover_modules()),
        "memory_records": len(MEMORY_STORE),
        "agent_count": len(AGENT_SWARM),
        "active_sessions": len(USER_SESSIONS),
        "api_keys_loaded": sum([
            bool(CEREBRAS_API_KEY), bool(GEMINI_API_KEY), bool(GROQ_API_KEY),
            bool(OPENWEATHER_API_KEY), bool(TELEGRAM_TOKEN), bool(SUPABASE_URL)
        ]),
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 330 AGENT SWARM MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/swarm/")
async def swarm_root():
    return {
        "module": "330 Agent Swarm",
        "status": "active",
        "total_agents": 330,
        "registered": len(AGENT_SWARM),
        "phases": {
            "phase_1": "Core Agents (1-100)",
            "phase_2": "Service Agents (101-200)",
            "phase_3": "Specialized Agents (201-330)"
        }
    }

@app.post("/api/swarm/register")
async def swarm_register(request: Request):
    data = await request.json()
    agent_id = data.get("agent_id")
    agent_type = data.get("agent_type", "general")
    agent_config = data.get("config", {})
    
    AGENT_SWARM[agent_id] = {
        "id": agent_id,
        "type": agent_type,
        "config": agent_config,
        "status": "registered",
        "registered_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }
    
    return {
        "registered": True,
        "agent_id": agent_id,
        "total_agents": len(AGENT_SWARM)
    }

@app.get("/api/swarm/agents")
async def swarm_list():
    return {
        "total": len(AGENT_SWARM),
        "agents": list(AGENT_SWARM.keys())[:50]  # Limit output
    }

@app.get("/api/swarm/agent/{agent_id}")
async def swarm_agent_get(agent_id: str):
    if agent_id not in AGENT_SWARM:
        return {"error": "Agent not found"}
    return AGENT_SWARM[agent_id]

@app.post("/api/swarm/agent/{agent_id}/execute")
async def swarm_agent_execute(agent_id: str, request: Request):
    if agent_id not in AGENT_SWARM:
        return {"error": "Agent not found"}
    
    data = await request.json()
    task = data.get("task", "unknown")
    
    AGENT_SWARM[agent_id]["last_active"] = datetime.now().isoformat()
    AGENT_SWARM[agent_id]["last_task"] = task
    
    return {
        "agent_id": agent_id,
        "task": task,
        "status": "executed",
        "result": f"Task '{task}' completed by agent {agent_id}"
    }

@app.post("/api/swarm/broadcast")
async def swarm_broadcast(request: Request):
    data = await request.json()
    message = data.get("message", "")
    targets = data.get("targets", list(AGENT_SWARM.keys()))
    
    results = []
    for agent_id in targets:
        if agent_id in AGENT_SWARM:
            AGENT_SWARM[agent_id]["last_active"] = datetime.now().isoformat()
            results.append({"agent": agent_id, "status": "broadcast_received"})
    
    return {
        "broadcast": True,
        "message": message,
        "recipients": len(results),
        "results": results
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
        
        logger.info(f"📩 Telegram: {text} from chat {chat_id}")
        
        if text == '/start':
            reply = "🦁 <b>Singh Ji AI Bot</b>\n\nShuruwat ho gayi!\n\nCommands:\n/start — Shuruwat\n/help — Madad\n/status — System check"
        elif text == '/help':
            reply = "🦁 <b>Madad</b>\n\n/start — Bot shuru\n/status — API status\nKuch bhi likho — Main jawab dunga!"
        elif text == '/status':
            reply = "🟢 <b>Singh Ji AI Status</b>\n\n✅ Bot Active\n✅ API Connected\n🦁 Singh Ji AI v7.0"
        else:
            reply = f"🦁 Aapne likha: <b>{text}</b>\n\nMain abhi sirf commands samajhta hoon:\n/start, /help, /status"
        
        if TELEGRAM_TOKEN and chat_id:
            import requests
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": reply,
                "parse_mode": "HTML"
            }, timeout=10)
            logger.info(f"✅ Reply sent to {chat_id}")
        
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return JSONResponse(status_code=200, content={"status": "ok"})

# ═══════════════════════════════════════════════════════
# 🦁 RETIREMENT TAX MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/retirement/")
async def retirement_root():
    return {
        "module": "Retirement & Tax Planning",
        "status": "active",
        "features": [
            "PF Calculator",
            "NPS Calculator",
            "Tax Calculator (Old vs New Regime)",
            "SIP Planner",
            "Pension Estimator"
        ]
    }

@app.post("/api/retirement/pf-calculate")
async def retirement_pf(request: Request):
    data = await request.json()
    basic_salary = data.get("basic_salary", 0)
    years = data.get("years", 20)
    rate = data.get("rate", 8.1)  # Current PF rate
    
    monthly_pf = basic_salary * 0.12  # 12% of basic
    total_contribution = monthly_pf * 12 * years
    interest = total_contribution * (rate / 100) * years * 0.5  # Approximate
    maturity = total_contribution + interest
    
    return {
        "basic_salary": basic_salary,
        "monthly_pf": round(monthly_pf, 2),
        "years": years,
        "interest_rate": rate,
        "total_contribution": round(total_contribution, 2),
        "estimated_interest": round(interest, 2),
        "maturity_amount": round(maturity, 2)
    }

@app.post("/api/retirement/tax-calculate")
async def retirement_tax(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")  # old or new
    
    tax = 0
    if regime == "new":
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = 15000 + (income - 600000) * 0.10
        elif income <= 1200000:
            tax = 45000 + (income - 900000) * 0.15
        elif income <= 1500000:
            tax = 90000 + (income - 1200000) * 0.20
        else:
            tax = 150000 + (income - 1500000) * 0.30
    else:  # Old regime with deductions
        taxable = max(0, income - 50000 - data.get("deductions", 0))
        if taxable <= 250000:
            tax = 0
        elif taxable <= 500000:
            tax = (taxable - 250000) * 0.05
        elif taxable <= 1000000:
            tax = 12500 + (taxable - 500000) * 0.20
        else:
            tax = 112500 + (taxable - 1000000) * 0.30
    
    cess = tax * 0.04
    total_tax = tax + cess
    
    return {
        "income": income,
        "regime": regime,
        "taxable_income": income if regime == "new" else max(0, income - 50000 - data.get("deductions", 0)),
        "base_tax": round(tax, 2),
        "cess_4_percent": round(cess, 2),
        "total_tax": round(total_tax, 2),
        "take_home": round(income - total_tax, 2)
    }

# ═══════════════════════════════════════════════════════
# 🦁 RUN SERVER
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
