# modules/newsdata.py — Singh Ji AI Ultra v5.0
# NewsData.io API — India News + Hindi News

from fastapi import APIRouter
import os
import requests

router = APIRouter()

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

@router.get("/")
def newsdata_root():
    return {"module": "newsdata", "status": "✅ Live", "source": "NewsData.io"}

@router.get("/india")
def get_india_news(query: str = "India", language: str = "hi"):
    """India news from NewsData.io"""
    if not NEWSDATA_API_KEY:
        return {"success": False, "error": "API Key not configured"}

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
def get_hindi_news():
    return get_india_news(query="India", language="hi")

@router.get("/english")
def get_english_news():
    return get_india_news(query="India", language="en")
