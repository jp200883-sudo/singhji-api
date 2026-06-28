from fastapi import APIRouter
import os
import sys

# services folder ko path mein add karo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from services.travily_search import search_news  # ya jo function hai
    TAVILY_AVAILABLE = True
except:
    TAVILY_AVAILABLE = False

router = APIRouter()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = os.getenv("TAVILY_URL", "https://api.tavily.com/search")

@router.get("/")
def news_home():
    return {
        "module": "news",
        "status": "🔥 LIVE",
        "source": "Tavily AI Search",
        "tavily_service": "✅ Available" if TAVILY_AVAILABLE else "❌ Not Found",
        "tavily_key": "✅ SET" if TAVILY_API_KEY else "❌ MISSING",
        "message": "Singh Ji ka news engine ready!"
    }

@router.get("/latest")
def get_latest_news(topic: str = "India", max_results: int = 5):
    if not TAVILY_API_KEY:
        return {
            "ok": False,
            "error": "TAVILY_API_KEY not set",
            "message": "Render Dashboard → Environment → Key daalo!"
        }
    
    try:
        import requests
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": f"latest news {topic}",
            "search_depth": "basic",
            "topic": "news",
            "time_range": "day",
            "max_results": max_results
        }
        
        response = requests.post(TAVILY_URL, json=payload, headers=headers, timeout=15)
        data = response.json()
        
        if "results" not in data:
            return {"ok": False, "error": "No results", "raw": data}
        
        articles = []
        for item in data["results"]:
            articles.append({
                "title": item.get("title", "No title"),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:300] + "...",
                "published": item.get("published_date", "Recent"),
                "source": item.get("source", "Unknown")
            })
        
        return {
            "ok": True,
            "topic": topic,
            "total": len(articles),
            "articles": articles,
            "powered_by": "Tavily AI via services/travily_search.py",
            "singh_ji_message": f"🦁 {topic} ki taza khabar!"
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "News fetch fail — baad mein try karo!"
        }

@router.get("/india")
def india_news():
    return get_latest_news(topic="India")

@router.get("/tech")
def tech_news():
    return get_latest_news(topic="technology India")

@router.get("/sports")
def sports_news():
    return get_latest_news(topic="sports India")

@router.get("/business")
def business_news():
    return get_latest_news(topic="business India")

@router.get("/bollywood")
def bollywood_news():
    return get_latest_news(topic="Bollywood entertainment")
