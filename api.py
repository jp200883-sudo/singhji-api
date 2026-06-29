# api.py
"""
Singh Ji AI Ultra v7.0 - Main API
Render Deployment Ready
"""
import os
import sys
import json
import logging
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
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))
logger.info(f"📁 Base dir: {BASE_DIR}")

# ========== SAFE IMPORTS ==========
# Config
try:
    from core.config.settings import get_settings
    logger.info("✅ Config loaded")
except Exception as e:
    logger.error(f"❌ Config import failed: {e}")
    def get_settings():
        return {"app_name": "Singh Ji AI", "version": "7.0.0"}

# ========== MODULE LOADER ==========
MODULES_LOADED = []

def safe_import(module_name, module_path):
    """Safely import a module with fallback"""
    try:
        # Try direct import first
        module = __import__(module_path, fromlist=[module_name])
        MODULES_LOADED.append(module_name)
        logger.info(f"✅ {module_name} loaded")
        return module
    except ImportError as e:
        logger.warning(f"⚠️ {module_name} import failed: {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠️ {module_name} error: {e}")
        return None

# ========== LOAD ALL MODULES ==========
logger.info("🔄 Loading modules...")

# List of all modules to load
MODULE_LIST = [
    ("ai_chat", "core.modules.ai_chat"),
    ("weather", "core.modules.weather"),
    ("news", "core.modules.news"),
    ("translate", "core.modules.translate"),
    ("calculator", "core.modules.calculator"),
    ("unit_converter", "core.modules.unit_converter"),
    ("dictionary", "core.modules.dictionary"),
    ("jokes", "core.modules.jokes"),
    ("quotes", "core.modules.quotes"),
    ("horoscope", "core.modules.horoscope"),
    ("qr_code", "core.modules.qr_code"),
    ("youtube", "core.modules.youtube"),
    ("pdf_tools", "core.modules.pdf_tools"),
    ("password_gen", "core.modules.password_gen"),
    ("url_shortener", "core.modules.url_shortener"),
    ("text_to_speech", "core.modules.text_to_speech"),
    ("speech_to_text", "core.modules.speech_to_text"),
    ("code_runner", "core.modules.code_runner"),
    ("json_formatter", "core.modules.json_formatter"),
    ("base64_tools", "core.modules.base64_tools"),
    ("hash_gen", "core.modules.hash_gen"),
    ("ip_lookup", "core.modules.ip_lookup"),
    ("domain_checker", "core.modules.domain_checker"),
    ("email_validator_mod", "core.modules.email_validator"),
    ("phone_validator", "core.modules.phone_validator"),
    ("plant_id", "core.modules.plant_id"),
    ("upi", "core.modules.upi"),
    ("reminders", "core.modules.reminders"),
    ("notes", "core.modules.notes"),
    ("todo", "core.modules.todo"),
    ("image_gen", "core.modules.image_gen"),
    ("voice", "core.modules.voice"),
]

# Load each module
modules_dict = {}
for name, path in MODULE_LIST:
    mod = safe_import(name, path)
    modules_dict[name] = mod

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
    all_modules = [m[0] for m in MODULE_LIST]
    return {
        "loaded": MODULES_LOADED,
        "count": len(MODULES_LOADED),
        "total": 33,
        "missing": [m for m in all_modules if m not in MODULES_LOADED]
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
