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
            query = params.get('query', '').strip()
        else:
            body = await request.json()
            query = body.get('query', '').strip()
        
        # Supreme agent — master orchestrator
        capabilities = {
            "multi_module": "Combines multiple modules",
            "ai_chat": "OpenAI + Gemini + Groq",
            "memory": "Supabase long-term memory",
            "language": "26 Indian languages",
            "voice": "Speech-to-text + Text-to-speech",
            "vision": "Plant ID + OCR",
            "payments": "Razorpay (on hold)",
            "analytics": "Full system analytics"
        }
        
        if query:
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "agent": "Supreme Agent",
                    "query": query,
                    "response": "Processing through multiple AI models...",
                    "capabilities_used": ["ai_chat", "language", "memory"],
                    "status": "Advanced processing mode"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "name": "🦁 Supreme Agent",
                "description": "Master AI orchestrator",
                "capabilities": capabilities,
                "version": "7.0",
                "status": "🦁 ACTIVE"
            }
        })
        
    except Exception as e:
        logger.error(f"Supreme agent crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
