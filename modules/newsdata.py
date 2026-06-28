# modules/newsdata.py — Singh Ji AI Ultra v5.0
# NewsData.io API — India News + Hindi News

from fastapi import APIRouter
import os
import requests

# ⬇️ FIX: Add prefix and tags
router = APIRouter(prefix="/api/news", tags=["News"])

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

@router.get("/")
async def newsdata_root():
    """News API Home"""
    return {
        "module": "newsdata",
        "status": "✅ Live",
        "source": "NewsData.io",
        "endpoints": ["/india", "/hindi", "/english"],
        "message": "Aaj ki taaza khabar!"
    }

@router.get("/india")
async def get_india_news(query: str = "India", language: str = "hi"):
    """India news from NewsData.io"""
    if not NEWSDATA_API_KEY:
        return {
            "success": False,
            "error": "API Key not configured",
            "message": "Add NEWSDATA_API_KEY to Render env vars",
            "mock": True
        }

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": query,
        "language": language,
        "country": "in"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") == "success":
            return {
                "success": True,
                "total": len(data.get("results", [])),
                "articles": data.get("results", [])
            }
        return {"success": False, "error": data.get("message", "API error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/hindi")
async def get_hindi_news():
    return await get_india_news(query="India", language="hi")

@router.get("/english")
async def get_english_news():
    return await get_india_news(query="India", language="en")
