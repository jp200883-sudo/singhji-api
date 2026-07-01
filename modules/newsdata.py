# modules/newsdata/handler.py

import os
import logging

logger = logging.getLogger(__name__)
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

def get_india_news(language="en"):
    """Fetch India news from NewsData API"""
    try:
        import requests
        
        if not NEWSDATA_API_KEY:
            logger.warning("⚠️ NEWSDATA_API_KEY missing")
            return []
        
        url = "https://newsdata.io/api/1/news"
        params = {
            "apikey": NEWSDATA_API_KEY,
            "country": "in",
            "language": language,
            "category": "top"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "success":
            results = data.get("results", [])
            logger.info(f"✅ NewsData: {len(results)} articles ({language})")
            return results
        else:
            logger.error(f"❌ NewsData API error: {data.get('message', 'unknown')}")
            return []
            
    except Exception as e:
        logger.error(f"❌ get_india_news error: {e}")
        return []  # Empty return - crash नहीं होगा

async def handler(request):
    """API endpoint for news"""
    try:
        from fastapi.responses import JSONResponse
        news = get_india_news(language="en")
        return JSONResponse({"status": "ok", "count": len(news), "news": news[:5]})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
