# modules/currents_api.py — Singh Ji AI Ultra v5.0 (FIXED)
# Currents API — World News + India News (600/day free)

import os
import httpx
from fastapi import APIRouter, Query

router = APIRouter()

CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")

# ========== SYNC FUNCTIONS (for internal use) ==========

def get_world_news(keywords=None, language="en"):
    """World news from Currents API (sync)"""
    if not CURRENTS_API_KEY:
        return {"success": False, "error": "API Key not configured"}

    url = "https://api.currentsapi.services/v1/latest-news"
    params = {"apiKey": CURRENTS_API_KEY, "language": language}
    if keywords:
        params["keywords"] = keywords

    try:
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            return {"success": True, "total": len(data.get("news", [])), "articles": data.get("news", [])}
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_news(query):
    """Search news (sync)"""
    url = "https://api.currentsapi.services/v1/search"
    params = {"apiKey": CURRENTS_API_KEY, "keywords": query, "language": "en"}
    try:
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            return {"success": True, "articles": data.get("news", [])}
        return {"success": False, "error": data.get("msg")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== FASTAPI ROUTES (for app.py) ==========

@router.get("/world")
async def currents_world_news(keywords: str = Query(None), language: str = Query("en")):
    """Get world news via Currents API"""
    result = get_world_news(keywords=keywords, language=language)
    return result

@router.get("/india")
async def get_india_news():
    """Get India news via Currents API — THIS FIXES THE ERROR!"""
    if not CURRENTS_API_KEY:
        return {"success": False, "error": "CURRENTS_API_KEY not configured"}
    
    url = "https://api.currentsapi.services/v1/latest-news"
    params = {
        "apiKey": CURRENTS_API_KEY,
        "country": "IN",
        "language": "en"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            data = response.json()
        
        if data.get("status") == "ok":
            return {
                "success": True,
                "source": "currents_api",
                "country": "IN",
                "total": len(data.get("news", [])),
                "articles": data.get("news", [])
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/search")
async def currents_search(query: str = Query(..., description="Search keywords")):
    """Search news via Currents API"""
    result = search_news(query)
    return result

@router.get("/")
async def currents_home():
    """Currents API home"""
    return {
        "module": "currents_api",
        "status": "active",
        "endpoints": {
            "world": "/api/currents/world",
            "india": "/api/currents/india",
            "search": "/api/currents/search"
        }
    }
