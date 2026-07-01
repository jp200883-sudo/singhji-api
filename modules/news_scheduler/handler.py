import os
from datetime import datetime
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
        
        # News scheduler config
        scheduler = {
            "status": "active",
            "intervals": {
                "morning_digest": "08:00 AM",
                "noon_update": "12:00 PM",
                "evening_digest": "06:00 PM",
                "night_summary": "10:00 PM"
            },
            "categories": ["national", "international", "sports", "technology", "agriculture"],
            "languages": ["hi", "en"],
            "delivery": {
                "telegram": True,
                "whatsapp": False,
                "email": False
            }
        }
        
        if action == 'schedule':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "News scheduler is active",
                    "next_update": "Coming soon",
                    "config": scheduler
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": scheduler
        })
        
    except Exception as e:
        logger.error(f"News scheduler crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
