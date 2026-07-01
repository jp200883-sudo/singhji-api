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
        
        # Meta agent routes queries to best module
        routing = {
            "weather": "/api/weather?city={city}",
            "news": "/api/newsdata?country=in",
            "search": "/api/search?q={query}",
            "mandi": "/api/mandi?commodity={commodity}",
            "govt": "/api/govt?service={service}",
            "emergency": "/api/emergency?lat={lat}&lon={lon}",
            "rozgar": "/api/rozgar?keyword={keyword}",
            "banking": "/api/banking?query={query}",
            "plant": "/api/plant_id",
            "pani": "/api/pani?state={state}",
            "sewer": "/api/sewer?city={city}",
            "currency": "/api/currency?base=USD&target=INR"
        }
        
        if query:
            query_lower = query.lower()
            matched = None
            for key, route in routing.items():
                if key in query_lower:
                    matched = {"module": key, "route": route, "query": query}
                    break
            
            if matched:
                return JSONResponse(content={
                    "success": True,
                    "error": None,
                    "data": {
                        "message": f"Route to: {matched['module']}",
                        "route": matched['route'],
                        "query": query,
                        "action": "Redirect to specific module"
                    }
                })
            
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "No specific module matched",
                    "query": query,
                    "suggestion": "Try: weather, news, search, mandi, govt, emergency, rozgar, banking, plant, pani, sewer, currency"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "name": "Meta Agent",
                "description": "Routes queries to best module",
                "available_routes": routing,
                "example": "?query=weather in Delhi"
            }
        })
        
    except Exception as e:
        logger.error(f"Meta agent crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
