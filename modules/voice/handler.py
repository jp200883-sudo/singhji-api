import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY', '')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'status').strip()
        else:
            body = await request.json()
            action = body.get('action', 'status').strip()
        
        if action == 'status':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "stt": "Deepgram" if DEEPGRAM_API_KEY else "Not configured",
                    "tts": "ElevenLabs" if ELEVENLABS_API_KEY else "Not configured",
                    "deepgram_status": "✅ Active" if DEEPGRAM_API_KEY else "❌ Add DEEPGRAM_API_KEY to env",
                    "elevenlabs_status": "✅ Active" if ELEVENLABS_API_KEY else "❌ Add ELEVENLABS_API_KEY to env",
                    "supported_languages": ["hi", "en", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa"]
                }
            })
        
        elif action == 'stt':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Speech-to-Text coming soon",
                    "provider": "Deepgram",
                    "status": "Ready" if DEEPGRAM_API_KEY else "API key missing",
                    "endpoint": "POST audio file"
                }
            })
        
        elif action == 'tts':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Text-to-Speech coming soon",
                    "provider": "ElevenLabs",
                    "status": "Ready" if ELEVENLABS_API_KEY else "API key missing",
                    "endpoint": "POST text"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["status", "stt", "tts"],
                "message": "Use ?action=status"
            }
        })
        
    except Exception as e:
        logger.error(f"Voice crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
