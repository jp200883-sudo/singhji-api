import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'status').strip()
            text = params.get('text', '').strip()
        else:
            body = await request.json()
            action = body.get('action', 'status').strip()
            text = body.get('text', '').strip()
        
        if action == 'status':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "provider": "ElevenLabs",
                    "status": "✅ Active" if ELEVENLABS_API_KEY else "❌ Add ELEVENLABS_API_KEY to env",
                    "voices": ["Rachel", "Adam", "Bella", "Antoni", "Elli"],
                    "languages": ["hi", "en", "bn", "te", "ta"],
                    "note": "High quality neural TTS"
                }
            })
        
        elif action == 'speak':
            if not text:
                return JSONResponse(status_code=400, content={
                    "success": False, "error": "Provide ?text=hello", "data": None
                })
            
            if not ELEVENLABS_API_KEY:
                return JSONResponse(status_code=503, content={
                    "success": False, "error": "ELEVENLABS_API_KEY not configured", "data": None
                })
            
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "TTS generation coming soon",
                    "text": text,
                    "provider": "ElevenLabs",
                    "status": "API ready, integration pending"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["status", "speak"],
                "message": "Use ?action=status or ?action=speak&text=hello"
            }
        })
        
    except Exception as e:
        logger.error(f"Voice TTS crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
