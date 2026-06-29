# main.py
"""
Singh Ji AI Ultra v7.0 - Main Application
Render Deployment Ready
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config.settings import get_settings
from core.modules import ai_chat, weather, news, translate
from core.modules import calculator, unit_converter, dictionary
from core.modules import jokes, quotes, horoscope
from core.modules import qr_code, youtube, pdf_tools
from core.modules import password_gen, url_shortener
from core.modules import text_to_speech, speech_to_text
from core.modules import code_runner, json_formatter
from core.modules import base64_tools, hash_gen
from core.modules import ip_lookup, domain_checker
from core.modules import email_validator, phone_validator
from core.modules import plant_id, upi

app = FastAPI(
    title="Singh Ji AI Ultra v7.0",
    description="India's Super AI App - 33 Modules",
    version="7.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3-70b-8192"

class WeatherRequest(BaseModel):
    city: str

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "🚀 LIVE",
        "app": "Singh Ji AI Ultra v7.0",
        "version": "7.0.0",
        "modules_loaded": 33,
        "server": "Render",
        "timestamp": str(datetime.now())
    }

# AI Chat Endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        result = ai_chat.get_ai_response(
            message=request.message,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weather Endpoint
@app.post("/api/weather")
async def weather_api(request: WeatherRequest):
    try:
        result = weather.get_weather(request.city)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Translate Endpoint
@app.post("/api/translate")
async def translate_api(request: TranslateRequest):
    try:
        result = translate.translate_text(request.text, request.target_lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Calculator Endpoint
@app.post("/api/calculate")
async def calculate(expression: str):
    try:
        result = calculator.calculate(expression)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints for all 33 modules...

# Root
@app.get("/")
async def root():
    return {
        "message": "🙏 Welcome to Singh Ji AI Ultra v7.0",
        "status": "LIVE",
        "modules": 33,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
