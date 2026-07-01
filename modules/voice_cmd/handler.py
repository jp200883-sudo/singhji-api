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
            action = params.get('action', 'list').strip()
        else:
            body = await request.json()
            action = body.get('action', 'list').strip()
        
        commands = {
            "weather": {"voice": "Mausam kaisa hai", "action": "/api/weather?city={city}"},
            "news": {"voice": "Khabar sunao", "action": "/api/newsdata?country=in"},
            "search": {"voice": "Dhoondo", "action": "/api/search?q={query}"},
            "mandi": {"voice": "Mandi bhao", "action": "/api/mandi?commodity={commodity}"},
            "govt": {"voice": "Sarkari yojana", "action": "/api/govt?service={service}"},
            "emergency": {"voice": "Madhad chahiye", "action": "/api/emergency"},
            "rozgar": {"voice": "Naukri dhundo", "action": "/api/rozgar"},
            "banking": {"voice": "Bank jankari", "action": "/api/banking"},
            "plant": {"voice": "Paudhe ki pehchan", "action": "/api/plant_id"},
            "pani": {"voice": "Pani ki samasya", "action": "/api/pani"},
            "sewer": {"voice": "Sewer ki shikayat", "action": "/api/sewer"},
            "currency": {"voice": "Rate batao", "action": "/api/currency"}
        }
        
        if action == 'list':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "total_commands": len(commands),
                    "commands": commands,
                    "note": "Voice commands in Hindi/English",
                    "status": "Ready for STT integration"
                }
            })
        
        elif action == 'execute':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Voice command execution coming soon",
                    "status": "Pending Deepgram STT activation",
                    "flow": "Voice → STT → Command → Action → TTS Response"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["list", "execute"],
                "message": "Use ?action=list"
            }
        })
        
    except Exception as e:
        logger.error(f"Voice cmd crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
