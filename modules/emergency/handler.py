import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        type_ = params.get("type", "").strip().lower()
        
        emergency_data = {
            "police": {"number": "100", "alt": "112", "info": "Police helpline - 24x7"},
            "ambulance": {"number": "108", "alt": "102", "info": "Ambulance - Free service"},
            "fire": {"number": "101", "alt": "112", "info": "Fire brigade - 24x7"},
            "women": {"number": "1091", "alt": "181", "info": "Women helpline"},
            "child": {"number": "1098", "alt": "", "info": "Child helpline - Childline"},
            "disaster": {"number": "1078", "alt": "011-26701728", "info": "NDMA disaster helpline"},
            "cyber": {"number": "1930", "alt": "", "info": "Cyber crime helpline"},
            "railway": {"number": "139", "alt": "", "info": "Railway helpline"},
            "sos": {"number": "112", "alt": "", "info": "Universal emergency number"}
        }
        
        if type_ and type_ in emergency_data:
            return JSONResponse(content={
                "success": True,
                "type": type_,
                "data": emergency_data[type_]
            })
        
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - Emergency Numbers",
            "universal": "112",
            "all_numbers": emergency_data,
            "usage": "/api/emergency?type=police"
        })
        
    except Exception as e:
        logger.error(f"Emergency error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
