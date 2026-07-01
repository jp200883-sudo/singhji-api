import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'info').strip()
        else:
            body = await request.json()
            action = body.get('action', 'info').strip()
        
        if action == 'info':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "name": "🦁 Singh Ji AI Ultra v7.0",
                    "version": "7.0.0",
                    "description": "India's Super App for every citizen",
                    "features": [
                        "AI Chat (OpenAI + Gemini + Groq)",
                        "Weather (OpenWeather)",
                        "News (NewsData + Currents)",
                        "Search (Tavily + SerpAPI)",
                        "Currency Exchange",
                        "Mandi Rates",
                        "Government Schemes",
                        "Emergency Services",
                        "Jobs & Rozgar",
                        "Banking Info",
                        "Plant ID",
                        "Water & Sewer Info",
                        "Analytics",
                        "Daily Reports",
                        "Schedule",
                        "SinghJi TV",
                        "Telegram Bot",
                        "26 Languages"
                    ],
                    "total_modules": 32,
                    "status": "🦁 LIVE"
                }
            })
        
        elif action == 'health':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "modules_loaded": 25
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["info", "health"],
                "message": "Use ?action=info or ?action=health"
            }
        })
        
    except Exception as e:
        logger.error(f"Init crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
