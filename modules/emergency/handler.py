import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

EMERGENCY_DATA = {
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


async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            type_ = params.get("type", "").strip().lower()
        else:
            try:
                body = await request.json()
            except Exception:
                body = {}
            type_ = str(body.get("type", "")).strip().lower()

        if type_ and type_ in EMERGENCY_DATA:
            return JSONResponse(content={
                "success": True,
                "type": type_,
                "data": EMERGENCY_DATA[type_]
            })

        return JSONResponse(content={
            "success": True,
            "message": "Singh Ji AI - Emergency Numbers",
            "universal": "112",
            "all_numbers": EMERGENCY_DATA,
            "usage": "/api/emergency?type=police"
        })

    except Exception as e:
        logger.error(f"Emergency error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
