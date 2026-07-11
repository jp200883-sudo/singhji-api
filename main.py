from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ YEH ADD KARO!
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Singh Ji AI Ultra v8.0")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./singhji.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10} if "postgresql" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.on_event("startup")
async def startup():
    logger.info("🚀 Startup begin...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connected!")
    except Exception as e:
        logger.error(f"❌ Database failed: {e}")
        return
    
    try:
        from miniprogram.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Mini-Program tables created!")
    except Exception as e:
        logger.warning(f"⚠️ Tables error: {e}")
    
    try:
        from miniprogram.portal import router as miniprogram_router
        app.include_router(miniprogram_router)
        logger.info("✅ Mini-Program router loaded!")
    except Exception as e:
        logger.warning(f"⚠️ Router error: {e}")
    
    logger.info("🚀 Startup complete!")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "8.0", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {"message": "Singh Ji AI Ultra v8.0 🔥", "status": "live"}

# ═══════════════════════════════════════════════════════
# 🦁 ALL API KEYS
# ═══════════════════════════════════════════════════════
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
PLANT_ID_API = os.getenv("PLANT_ID_API")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "1008554401796459")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")

# ═══════════════════════════════════════════════════════
# 🦁 AVAILABLE KEYS MAP
# ═══════════════════════════════════════════════════════
AVAILABLE_KEYS = {
    "OPENWEATHER": bool(OPENWEATHER_API_KEY),
    "CURRENTS": bool(CURRENTS_API_KEY),
    "GROQ": bool(GROQ_API_KEY),
    "GEMINI": bool(GEMINI_API_KEY),
    "TELEGRAM": bool(TELEGRAM_TOKEN),
    "SUPABASE": bool(SUPABASE_URL and SUPABASE_SERVICE_KEY),
    "CEREBRAS": bool(CEREBRAS_API_KEY),
    "CF": bool(CF_API_TOKEN),
    "HUGGINGFACE": bool(HUGGINGFACE_TOKEN),
    "MANDI": bool(MANDI_API_KEY),
    "NEWSDATA": bool(NEWSDATA_API_KEY),
    "PLANT_ID": bool(PLANT_ID_API),
    "RAPIDAPI": bool(RAPIDAPI_KEY),
    "RAZORPAY": bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET),
    "TAVILY": bool(TAVILY_API_KEY),
    "TWILIO": bool(TWILIO_SID and TWILIO_TOKEN),
    "FACEBOOK": bool(FACEBOOK_ACCESS_TOKEN),
    "GMAIL": bool(GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET),
    "INSTAGRAM": bool(INSTAGRAM_ACCESS_TOKEN),
    "YOUTUBE": bool(YOUTUBE_API_KEY),
}

# ═══════════════════════════════════════════════════════
# 🦁 GLOBAL STORES
# ═══════════════════════════════════════════════════════
MODULES = {}
MEMORY_STORE = {}
AGENT_SWARM = {}
AGENT_QUEUE = []
SYSTEM_LOAD = {"active_agents": 0, "max_agents": 100, "phase": 0}
TRISHUL_MEMORY = {}

# ═══════════════════════════════════════════════════════
# 🦁 LIFESPAN (replaces deprecated @app.on_event)
# ═══════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    SYSTEM_LOAD["phase"] = 1
    logger.info("🦁 Singh Ji AI Ultra v8.0 Started!")
    logger.info(f"🦁 Available Keys: {AVAILABLE_KEYS}")
    logger.info(f"🦁 Mini-Program Available: {MINIPROGRAM_AVAILABLE}")
    yield
    logger.info("🦁 Singh Ji AI Ultra v8.0 Stopped!")

# ═══════════════════════════════════════════════════════
# 🦁 FASTAPI APP
# ═══════════════════════════════════════════════════════
app = FastAPI(
    title="Singh Ji AI Ultra v8.0",
    version="8.0.0",
    description="330 Agent Swarm | Railway Deploy | All Social APIs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════
# 🦁 HEALTH CHECK
# ═══════════════════════════════════════════════════════
@app.get("/")
@app.head("/")
async def root():
    return {
        "name": "Singh Ji AI Ultra v8.0",
        "version": "8.0.0",
        "status": "LIVE",
        "modules": len(MODULES),
        "agents_active": SYSTEM_LOAD["active_agents"],
        "available_keys": AVAILABLE_KEYS,
        "miniprogram": MINIPROGRAM_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
@app.head("/health")
async def health():
    return {"status": "ok", "service": "Singh Ji AI v8.0"}
# ═══════════════════════════════════════════════════════
# 🦁 CORE MODULES
# ═══════════════════════════════════════════════════════
@app.get("/api/status")
async def status():
    return {
        "name": "Singh Ji AI Ultra v8.0",
        "modules": len(MODULES),
        "agents": {"total": 330, "active": SYSTEM_LOAD["active_agents"], "phase": SYSTEM_LOAD["phase"]},
        "available_keys": AVAILABLE_KEYS,
        "miniprogram": MINIPROGRAM_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# ═══════════════════════════════════════════════════════
# 🦁 MEMORY MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/memory/")
async def memory_list():
    return {"status": "Memory Active", "records": len(MEMORY_STORE)}

@app.get("/api/memory/{key}")
async def memory_get(key: str):
    return {"key": key, "data": MEMORY_STORE.get(key), "exists": key in MEMORY_STORE}

@app.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(datetime.now().timestamp()))
    MEMORY_STORE[key] = data.get("value", data)
    return {"saved": True, "key": key}

# ═══════════════════════════════════════════════════════
# 🦁 WEATHER MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/weather/")
async def weather_root():
    return {"module": "Weather", "status": "active"}

@app.get("/api/weather/{city}")
async def weather_city(city: str):
    if OPENWEATHER_API_KEY:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if resp.status_code == 200:
                return {
                    "city": city, "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "desc": data["weather"][0]["description"]
                }
        except Exception as e:
            logger.warning(f"Weather error: {e}")
    return {"city": city, "temp": 32.0, "humidity": 65, "desc": "demo", "source": "DEMO"}

# ═══════════════════════════════════════════════════════
# 🦁 NEWS MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/news/")
async def news_root():
    return {"module": "News", "status": "active"}

@app.get("/api/news/latest")
async def news_latest():
    if CURRENTS_API_KEY:
        try:
            resp = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}", timeout=10)
            return resp.json()
        except Exception as e:
            logger.warning(f"News error: {e}")
    return {"status": "demo", "news": [{"title": "Singh Ji AI News", "description": "Add CURRENTS_API_KEY"}]}

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
    data = await request.json()
    return {"status": "pending", "image": data.get("image_url", "none")}

# ═══════════════════════════════════════════════════════
# 🦁 PAYMENT MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/payment/")
async def payment_root():
    return {"module": "Payment Gateway", "status": "ON_HOLD", "activate_at": "1000+ daily users", "upi_id": "jp200883@sbi"}

# ═══════════════════════════════════════════════════════
# 🦁 ADMIN MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/admin/")
async def admin_root():
    return {"module": "Admin", "modules": len(MODULES), "agents": SYSTEM_LOAD["active_agents"], "available_keys": AVAILABLE_KEYS}

@app.get("/api/admin/stats")
async def admin_stats():
    return {"modules": len(MODULES), "agents_active": SYSTEM_LOAD["active_agents"], "available_keys": AVAILABLE_KEYS, "timestamp": datetime.now().isoformat()}

# ═══════════════════════════════════════════════════════
# 🦁 FACEBOOK MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/facebook/")
async def facebook_root():
    return {"module": "Facebook", "status": "active" if FACEBOOK_ACCESS_TOKEN else "missing_token", "page_id": FACEBOOK_PAGE_ID}

@app.get("/api/facebook/status")
async def facebook_status():
    if not FACEBOOK_ACCESS_TOKEN:
        return {"status": "error", "error": "FACEBOOK_ACCESS_TOKEN not set"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=id,name,followers_count"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {"status": "connected", "token_valid": True, "page": {"id": data.get("id"), "name": data.get("name"), "followers": data.get("followers_count", 0)}}
        return {"status": "error", "error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/facebook/post")
async def facebook_post(request: Request):
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN not set"}
    data = await request.json()
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/feed"
        payload = {"access_token": FACEBOOK_ACCESS_TOKEN, "message": data.get("message", "")}
        if data.get("link"):
            payload["link"] = data["link"]
        resp = requests.post(url, data=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════
# 🦁 INSTAGRAM MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/instagram/")
async def instagram_root():
    return {"module": "Instagram", "status": "active" if INSTAGRAM_ACCESS_TOKEN else "missing_token"}

@app.get("/api/instagram/status")
async def instagram_status():
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"status": "error", "error": "INSTAGRAM_ACCESS_TOKEN not set"}
    try:
        url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}?access_token={INSTAGRAM_ACCESS_TOKEN}&fields=id,username,followers_count"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {"status": "connected", "account": {"id": data.get("id"), "username": data.get("username"), "followers": data.get("followers_count", 0)}}
        return {"status": "error", "error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/instagram/post")
async def instagram_post(request: Request):
    if not INSTAGRAM_ACCESS_TOKEN:
        return {"error": "INSTAGRAM_ACCESS_TOKEN not set"}
    data = await request.json()
    try:
        url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media"
        payload = {
            "access_token": INSTAGRAM_ACCESS_TOKEN,
            "caption": data.get("caption", ""),
            "image_url": data.get("image_url", "")
        }
        resp = requests.post(url, data=payload, timeout=10)
        result = resp.json()
        if "id" in result:
            publish_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media_publish"
            pub_resp = requests.post(publish_url, data={"access_token": INSTAGRAM_ACCESS_TOKEN, "creation_id": result["id"]}, timeout=10)
            return pub_resp.json()
        return result
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════
# 🦁 YOUTUBE MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/youtube/")
async def youtube_root():
    return {"module": "YouTube", "status": "active" if YOUTUBE_API_KEY else "missing_key"}

@app.get("/api/youtube/channel/{channel_id}")
async def youtube_channel(channel_id: str):
    if not YOUTUBE_API_KEY:
        return {"error": "YOUTUBE_API_KEY not set"}
    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/youtube/search")
async def youtube_search(q: str = "", max_results: int = 10):
    if not YOUTUBE_API_KEY:
        return {"error": "YOUTUBE_API_KEY not set"}
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={q}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════
# 🦁 GMAIL MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/gmail/")
async def gmail_root():
    return {"module": "Gmail", "status": "active" if GMAIL_CLIENT_ID else "missing_credentials"}

@app.get("/api/gmail/auth-url")
async def gmail_auth_url():
    if not GMAIL_CLIENT_ID:
        return {"error": "GMAIL_CLIENT_ID not set"}
    redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "https://singhji-ai.github.io/oauth/callback")
    scope = "https://www.googleapis.com/auth/gmail.send"
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GMAIL_CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&access_type=offline"
    return {"auth_url": url, "note": "Visit this URL to authorize Gmail access"}

# ═══════════════════════════════════════════════════════
# 🦁 SWARM MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/swarm/")
async def swarm_root():
    return {"module": "Sarwan 330", "total": 330, "active": SYSTEM_LOAD["active_agents"], "phase": SYSTEM_LOAD["phase"]}

@app.get("/api/swarm/agents")
async def swarm_list():
    return {"total": len(AGENT_SWARM), "active": SYSTEM_LOAD["active_agents"], "sample": list(AGENT_SWARM.keys())[:5]}

# ═══════════════════════════════════════════════════════
# 🦁 RETIREMENT & TAX
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
    return {"income": income, "regime": regime, "tax": round(tax, 2), "cess": round(cess, 2), "total": round(tax + cess, 2), "take_home": round(income - tax - cess, 2)}

# ═══════════════════════════════════════════════════════
# 🦁 TELEGRAM WEBHOOK
# ═══════════════════════════════════════════════════════
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        if text == "/status":
            reply = f"Singh Ji AI v8.0\nAgents: {SYSTEM_LOAD['active_agents']}/330"
        else:
            reply = "Singh Ji AI Bot\nCommands: /status"
        if TELEGRAM_TOKEN and chat_id:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}, timeout=10)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Telegram: {e}")
        return {"status": "ok"}

# ═══════════════════════════════════════════════════════
# 🦁 TRISHUL MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/trishul/")
async def trishul_root():
    return {"module": "Trishul Memory", "status": "active", "records": len(TRISHUL_MEMORY)}

@app.post("/api/trishul/store")
async def trishul_store(request: Request):
    data = await request.json()
    key = data.get("key", str(datetime.now().timestamp()))
    TRISHUL_MEMORY[key] = {
        "value": data.get("value", data),
        "timestamp": datetime.now().isoformat(),
        "tags": data.get("tags", [])
    }
    return {"saved": True, "key": key, "total": len(TRISHUL_MEMORY)}

@app.get("/api/trishul/recall/{key}")
async def trishul_recall(key: str):
    return {"key": key, "data": TRISHUL_MEMORY.get(key), "exists": key in TRISHUL_MEMORY}

@app.get("/api/trishul/search")
async def trishul_search(q: str = ""):
    results = {k: v for k, v in TRISHUL_MEMORY.items() if q.lower() in str(v).lower()}
    return {"query": q, "results": results, "count": len(results)}

@app.delete("/api/trishul/delete/{key}")
async def trishul_delete(key: str):
    if key in TRISHUL_MEMORY:
        del TRISHUL_MEMORY[key]
        return {"deleted": True}
    return {"deleted": False, "error": "Key not found"}

# ═══════════════════════════════════════════════════════
# 🦁 AAVISHKAR MODULE
# ═══════════════════════════════════════════════════════
@app.get("/api/aavishkar/")
async def aavishkar_root():
    return {"module": "Aavishkar AI", "status": "active", "version": "4.1"}

@app.post("/api/aavishkar/generate")
async def aavishkar_generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "groq")

    if model == "groq" and GROQ_API_KEY:
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]},
                timeout=30)
            result = resp.json()
            return {"status": "success", "model": "groq", "response": result["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return {"status": "success", "model": "gemini", "response": text}
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")

    return {"status": "demo", "response": f"Singh Ji AI Demo Response for: {prompt[:50]}...", "note": "Add GROQ_API_KEY or GEMINI_API_KEY"}

@app.post("/api/aavishkar/translate")
async def aavishkar_translate(request: Request):
    data = await request.json()
    text = data.get("text", "")
    target_lang = data.get("target", "hi")
    return {"original": text, "translated": f"[{target_lang}] {text}", "status": "demo"}

@app.post("/api/aavishkar/summarize")
async def aavishkar_summarize(request: Request):
    data = await request.json()
    text = data.get("text", "")
    return {"summary": text[:200] + "..." if len(text) > 200 else text, "original_length": len(text)}

# ═══════════════════════════════════════════════════════
# 🦁 MINI-PROGRAM ROUTES
# ═══════════════════════════════════════════════════════
@app.post("/api/miniprogram/register")
async def mp_register(request: Request):
    data = await request.json()
    return MiniAuth.register_developer(data.get("name"), data.get("email"), data.get("business_type", "general"))

@app.post("/api/miniprogram/submit")
async def mp_submit(request: Request):
    data = await request.json()
    return MiniAuth.submit_app(data.get("developer_id"), data.get("name"), data.get("type"), data.get("code"), data.get("permissions", []))

@app.get("/api/miniprogram/status/{app_id}")
async def mp_status(app_id: str):
    app = MiniAuth.APPROVED_APPS.get(app_id)
    return {"app_id": app_id, "status": app["status"]} if app else {"error": "App not found"}

@app.post("/api/miniprogram/auth")
async def mp_auth(request: Request):
    data = await request.json()
    try:
        token = MiniAuth.generate_token(data.get("app_id"), data.get("phone"))
        return {"token": token, "expires_in": 86400}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/miniprogram/payment")
async def mp_payment(request: Request):
    data = await request.json()
    user = MiniAuth.validate_token(data.get("token"))
    if not user:
        return {"error": "Invalid token"}
    return MiniPayment.process(data.get("amount", 0), user["user_id"], data.get("merchant_id"), data.get("method", "upi"), {"app_id": user["app_id"]})

@app.post("/api/miniprogram/storage/put")
async def mp_storage_put(request: Request):
    data = await request.json()
    user = MiniAuth.validate_token(data.get("token"))
    if not user:
        return {"error": "Invalid token"}
    return MiniStorage.put(user["app_id"], user["user_id"], data.get("key"), data.get("value"))

@app.get("/api/miniprogram/storage/get")
async def mp_storage_get(key: str, token: str):
    user = MiniAuth.validate_token(token)
    if not user:
        return {"error": "Invalid token"}
    return MiniStorage.get(user["app_id"], user["user_id"], key)

@app.get("/api/miniprogram/developer/{developer_id}/dashboard")
async def mp_dashboard(developer_id: str):
    return DeveloperPortal.get_dashboard(developer_id)

@app.get("/api/miniprogram/admin/apps")
async def mp_admin_apps(status: str = None):
    return {"apps": DeveloperPortal.get_all_apps(status)}

@app.post("/api/miniprogram/admin/approve/{app_id}")
async def mp_admin_approve(app_id: str):
    return MiniAuth.approve_app(app_id)

# ═══════════════════════════════════════════════════════
# 🦁 API STATUS CHECK
# ═══════════════════════════════════════════════════════
@app.get("/api/check")
async def api_check():
    tests = {
        "OPENWEATHER": ("https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=" + str(OPENWEATHER_API_KEY or ""), {}, "GET"),
        "GROQ": ("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {GROQ_API_KEY or ''}"}, "GET"),
        "GEMINI": ("https://generativelanguage.googleapis.com/v1beta/models?key=" + str(GEMINI_API_KEY or ""), {}, "GET"),
        "TELEGRAM": (f"https://api.telegram.org/bot{TELEGRAM_TOKEN or ''}/getMe", {}, "GET"),
        "SUPABASE": (f"{SUPABASE_URL or ''}/rest/v1/", {"apikey": SUPABASE_SERVICE_KEY or "", "Authorization": f"Bearer {SUPABASE_SERVICE_KEY or ''}"}, "GET"),
        "FACEBOOK": (f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN or ''}", {}, "GET"),
    }

    results = {}
    live_count = 0
    dead_count = 0

    for name, (url, headers, method) in tests.items():
        if not AVAILABLE_KEYS.get(name):
            results[name] = {"status": "MISSING", "code": None, "ms": None}
            dead_count += 1
            continue

        try:
            start = time.time()
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=5)
            else:
                r = requests.post(url, headers=headers, timeout=5)
            elapsed = round((time.time() - start) * 1000, 2)

            if r.status_code == 200:
                results[name] = {"status": "LIVE", "code": 200, "ms": elapsed}
                live_count += 1
            else:
                results[name] = {"status": "ERROR", "code": r.status_code, "ms": elapsed, "detail": r.text[:100]}
                dead_count += 1
        except Exception as e:
            results[name] = {"status": "FAIL", "error": str(e)[:50], "ms": None}
            dead_count += 1

    return {
        "timestamp": datetime.now().isoformat(),
        "version": "8.0.0",
        "summary": {"live": live_count, "dead": dead_count, "total": live_count + dead_count},
        "results": results
    }

# ═══════════════════════════════════════════════════════
# 🦁 RUN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
