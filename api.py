# api.py
"""
Singh Ji AI Ultra v7.0 - Main API
Direct file loading - NO package imports
"""
import os
import sys
import json
import logging
import importlib.util
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== PATH SETUP ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'core', 'modules')
CONFIG_DIR = os.path.join(BASE_DIR, 'core', 'config')

logger.info(f"📁 Base dir: {BASE_DIR}")
logger.info(f"📁 Modules dir: {MODULES_DIR}")
logger.info(f"📁 Modules dir exists: {os.path.exists(MODULES_DIR)}")

# List files in modules dir if exists
if os.path.exists(MODULES_DIR):
    files = os.listdir(MODULES_DIR)
    logger.info(f"📁 Files in modules: {files}")
else:
    logger.error(f"❌ Modules directory NOT FOUND!")
    # Create it
    os.makedirs(MODULES_DIR, exist_ok=True)
    logger.info(f"📁 Created modules directory")

# ========== LOAD CONFIG ==========
def load_config():
    """Load settings from core/config/settings.py"""
    try:
        settings_path = os.path.join(CONFIG_DIR, 'settings.py')
        if not os.path.exists(settings_path):
            logger.warning(f"⚠️ settings.py not found at {settings_path}")
            return None
            
        spec = importlib.util.spec_from_file_location("settings", settings_path)
        settings_mod = importlib.util.module_from_spec(spec)
        sys.modules["settings"] = settings_mod
        spec.loader.exec_module(settings_mod)
        
        if hasattr(settings_mod, 'get_settings'):
            logger.info("✅ Config loaded with get_settings")
            return settings_mod.get_settings
        else:
            logger.warning("⚠️ get_settings not found in settings.py")
            return None
            
    except Exception as e:
        logger.error(f"❌ Config load failed: {e}")
        return None

get_settings_func = load_config()

def get_settings():
    if get_settings_func:
        return get_settings_func()
    return {"app_name": "Singh Ji AI Ultra", "version": "7.0.0"}

# ========== DYNAMIC MODULE LOADER ==========
MODULES_LOADED = []

def load_module_from_file(module_name, file_path):
    """Load a Python module directly from file path"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ File not found: {file_path}")
            return None
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.warning(f"⚠️ Cannot create spec for: {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        MODULES_LOADED.append(module_name)
        logger.info(f"✅ {module_name} loaded")
        return module
        
    except Exception as e:
        logger.warning(f"⚠️ {module_name} failed: {str(e)[:100]}")
        return None

# ========== LOAD ALL MODULES ==========
logger.info("🔄 Loading modules...")

MODULE_FILES = [
    "ai_chat.py", "weather.py", "news.py", "translate.py",
    "calculator.py", "unit_converter.py", "dictionary.py",
    "jokes.py", "quotes.py", "horoscope.py",
    "qr_code.py", "youtube.py", "pdf_tools.py",
    "password_gen.py", "url_shortener.py",
    "text_to_speech.py", "speech_to_text.py",
    "code_runner.py", "json_formatter.py",
    "base64_tools.py", "hash_gen.py",
    "ip_lookup.py", "domain_checker.py",
    "email_validator.py", "phone_validator.py",
    "plant_id.py", "upi.py",
    "reminders.py", "notes.py", "todo.py",
    "image_gen.py", "voice.py"
]

modules_dict = {}
for filename in MODULE_FILES:
    module_name = filename.replace('.py', '')
    file_path = os.path.join(MODULES_DIR, filename)
    mod = load_module_from_file(module_name, file_path)
    modules_dict[module_name] = mod

logger.info(f"🚀 Modules loaded: {len(MODULES_LOADED)}/33")

# ========== FASTAPI APP ==========
app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="India's Super AI App - 33 Modules",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODELS ==========
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3-70b-8192"

class WeatherRequest(BaseModel):
    city: str

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"

class CalculatorRequest(BaseModel):
    expression: str

# ========== ENDPOINTS ==========
@app.get("/")
async def root():
    return {
        "message": "🙏 Welcome to Singh Ji AI Ultra v7.0",
        "status": "LIVE",
        "modules_loaded": len(MODULES_LOADED),
        "total_modules": 33,
        "module_list": MODULES_LOADED,
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    settings = get_settings()
    return {
        "status": "🚀 LIVE",
        "app": settings.get("app_name", "Singh Ji AI"),
        "version": settings.get("version", "7.0.0"),
        "modules_loaded": len(MODULES_LOADED),
        "total_modules": 33,
        "module_list": MODULES_LOADED,
        "server": "Render",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/modules")
async def list_modules():
    return {
        "loaded": MODULES_LOADED,
        "count": len(MODULES_LOADED),
        "total": 33,
        "missing": [f.replace('.py', '') for f in MODULE_FILES if f.replace('.py', '') not in MODULES_LOADED]
    }

# ========== API ENDPOINTS ==========
@app.post("/api/chat")
async def chat(request: ChatRequest):
    mod = modules_dict.get("ai_chat")
    if not mod:
        raise HTTPException(status_code=503, detail="AI Chat module not loaded")
    try:
        result = mod.get_ai_response(message=request.message, model=request.model)
        return result
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weather")
async def weather_api(request: WeatherRequest):
    mod = modules_dict.get("weather")
    if not mod:
        raise HTTPException(status_code=503, detail="Weather module not loaded")
    try:
        result = mod.get_weather(request.city)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_api(request: TranslateRequest):
    mod = modules_dict.get("translate")
    if not mod:
        raise HTTPException(status_code=503, detail="Translate module not loaded")
    try:
        result = mod.translate_text(request.text, request.target_lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate")
async def calculate(request: CalculatorRequest):
    mod = modules_dict.get("calculator")
    if not mod:
        raise HTTPException(status_code=503, detail="Calculator module not loaded")
    try:
        result = mod.calculate(request.expression)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/joke")
async def get_joke():
    mod = modules_dict.get("jokes")
    if not mod:
        raise HTTPException(status_code=503, detail="Jokes module not loaded")
    try:
        return mod.get_joke()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quote")
async def get_quote():
    mod = modules_dict.get("quotes")
    if not mod:
        raise HTTPException(status_code=503, detail="Quotes module not loaded")
    try:
        return mod.get_quote()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/qr")
async def generate_qr(text: str):
    mod = modules_dict.get("qr_code")
    if not mod:
        raise HTTPException(status_code=503, detail="QR module not loaded")
    try:
        return mod.generate_qr(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/password")
async def generate_password(length: int = 12):
    mod = modules_dict.get("password_gen")
    if not mod:
        raise HTTPException(status_code=503, detail="Password module not loaded")
    try:
        return mod.generate(length)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hash")
async def generate_hash(text: str, algorithm: str = "sha256"):
    mod = modules_dict.get("hash_gen")
    if not mod:
        raise HTTPException(status_code=503, detail="Hash module not loaded")
    try:
        return mod.generate(text, algorithm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ip")
async def ip_lookup_api(ip: Optional[str] = None):
    mod = modules_dict.get("ip_lookup")
    if not mod:
        raise HTTPException(status_code=503, detail="IP Lookup module not loaded")
    try:
        return mod.lookup(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plant")
async def identify_plant(image_url: str):
    mod = modules_dict.get("plant_id")
    if not mod:
        raise HTTPException(status_code=503, detail="Plant ID module not loaded")
    try:
        return mod.identify_plant(image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upi")
async def get_upi_details():
    mod = modules_dict.get("upi")
    if not mod:
        raise HTTPException(status_code=503, detail="UPI module not loaded")
    try:
        return mod.get_upi_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== ERROR HANDLERS ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "status": "error"}
    )

# ========== STARTUP ==========
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Singh Ji AI Ultra v7.0 Started!")
    logger.info(f"📦 Modules: {len(MODULES_LOADED)}/33 loaded")
    logger.info(f"📋 Loaded: {MODULES_LOADED}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
