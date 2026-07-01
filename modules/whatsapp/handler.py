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
            action = params.get('action', 'status').strip()
        else:
            body = await request.json()
            action = body.get('action', 'status').strip()
        
        if action == 'status':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "status": "🦁 WhatsApp Bot Ready",
                    "provider": "WhatsApp Business API",
                    "note": "Meta Business verification required for production",
                    "features": [
                        "Text messages",
                        "Image sharing",
                        "Quick replies",
                        "Broadcast messages"
                    ],
                    "setup_required": "WhatsApp Business Account + Meta approval"
                }
            })
        
        elif action == 'webhook':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "WhatsApp webhook endpoint",
                    "endpoint": "/api/whatsapp/webhook",
                    "method": "POST",
                    "status": "Ready for Meta integration"
                }
            })
        
        elif action == 'send':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Message sending coming soon",
                    "status": "Pending WhatsApp Business API activation",
                    "note": "Requires Meta Business verification"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["status", "webhook", "send"],
                "message": "Use ?action=status"
            }
        })
        
    except Exception as e:
        logger.error(f"WhatsApp crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
