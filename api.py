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

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ========== SAFE IMPORTS ==========
# Config
try:
    from core.config.settings import get_settings
    logger.info("✅ Config loaded")
except Exception as e:
    logger.error(f"❌ Config import failed: {e}")
    def get_settings():
        return {"app_name": "Singh Ji AI", "version": "7.0.0"}

# Modules - with fallback
MODULES_LOADED = []

def safe_import(module_name, import_path):
    """Safely import a module with fallback"""
    try:
        module = __import__(import_path, fromlist=[module_name])
        MODULES_LOADED.append(module_name)
        logger.info(f"✅ {module_name} loaded")
        return module
    except Exception as e:
        logger.warning(f"⚠️ {module_name} failed: {e}")
        return None

# Import all modules safely
ai_chat = safe_import("ai_chat", "core.modules.ai_chat")
weather = safe_import("weather", "core.modules.weather")
news = safe_import("news", "core.modules.news")
translate = safe_import("translate", "core.modules.translate")
calculator = safe_import("calculator", "core.modules.calculator")
unit_converter = safe_import("unit_converter", "core.modules.unit_converter")
dictionary = safe_import("dictionary", "core.modules.dictionary")
jokes = safe_import("jokes", "core.modules.jokes")
quotes = safe_import("quotes", "core.modules.quotes")
horoscope = safe_import("horoscope", "core.modules.horoscope")
qr_code = safe_import("qr_code", "core.modules.qr_code")
youtube = safe_import("youtube", "core.modules.youtube")
pdf_tools = safe_import("pdf_tools", "core.modules.pdf_tools")
password_gen = safe_import("password_gen", "core.modules.password_gen")
url_shortener = safe_import("url_shortener", "core.modules.url_shortener")
text_to_speech = safe_import("text_to_speech", "core.modules.text_to_speech")
speech_to_text = safe_import("speech_to_text", "core.modules.speech_to_text")
code_runner = safe_import("code_runner", "core.modules.code_runner")
json_formatter = safe_import("json_formatter", "core.modules.json_formatter")
base64_tools = safe_import("base64_tools", "core.modules.base64_tools")
hash_gen = safe_import("hash_gen", "core.modules.hash_gen")
ip_lookup = safe_import("ip_lookup", "core.modules.ip_lookup")
domain_checker = safe_import("domain_checker", "core.modules.domain_checker")
email_validator_mod = safe_import("email_validator", "core.modules.email_validator")
phone_validator = safe_import("phone_validator", "core.modules.phone_validator")
plant_id = safe_import("plant_id", "core.modules.plant_id")
upi = safe_import("upi", "core.modules.upi")
reminders = safe_import("reminders", "core.modules.reminders")
notes = safe_import("notes", "core.modules.notes")
todo = safe_import("todo", "core.modules.todo")
image_gen = safe_import("image_gen", "core.modules.image_gen")
voice = safe_import("voice", "core.modules.voice")

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
        "missing": [m for m in [
            "ai_chat", "weather", "news", "translate", "calculator",
            "unit_converter", "dictionary", "jokes", "quotes", "horoscope",
            "qr_code", "youtube", "pdf_tools", "password_gen", "url_shortener",
            "text_to_speech", "speech_to_text", "code_runner", "json_formatter",
            "base64_tools", "hash_gen", "ip_lookup", "domain_checker",
            "email_validator", "phone_validator", "plant_id", "upi",
            "reminders", "notes", "todo", "image_gen", "voice"
        ] if m not in MODULES_LOADED]
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not ai_chat:
        raise HTTPException(status_code=503, detail="AI Chat module not loaded")
    try:
        result = ai_chat.get_ai_response(message=request.message, model=request.model)
        return result
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weather")
async def weather_api(request: WeatherRequest):
    if not weather:
        raise HTTPException(status_code=503, detail="Weather module not loaded")
    try:
        result = weather.get_weather(request.city)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_api(request: TranslateRequest):
    if not translate:
        raise HTTPException(status_code=503, detail="Translate module not loaded")
    try:
        result = translate.translate_text(request.text, request.target_lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate")
async def calculate(request: CalculatorRequest):
    if not calculator:
        raise HTTPException(status_code=503, detail="Calculator module not loaded")
    try:
        result = calculator.calculate(request.expression)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/joke")
async def get_joke():
    if not jokes:
        raise HTTPException(status_code=503, detail="Jokes module not loaded")
    try:
        return jokes.get_joke()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quote")
async def get_quote():
    if not quotes:
        raise HTTPException(status_code=503, detail="Quotes module not loaded")
    try:
        return quotes.get_quote()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/qr")
async def generate_qr(text: str):
    if not qr_code:
        raise HTTPException(status_code=503, detail="QR module not loaded")
    try:
        return qr_code.generate_qr(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/password")
async def generate_password(length: int = 12):
    if not password_gen:
        raise HTTPException(status_code=503, detail="Password module not loaded")
    try:
        return password_gen.generate(length)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hash")
async def generate_hash(text: str, algorithm: str = "sha256"):
    if not hash_gen:
        raise HTTPException(status_code=503, detail="Hash module not loaded")
    try:
        return hash_gen.generate(text, algorithm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ip")
async def ip_lookup_api(ip: Optional[str] = None):
    if not ip_lookup:
        raise HTTPException(status_code=503, detail="IP Lookup module not loaded")
    try:
        return ip_lookup.lookup(ip)
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
