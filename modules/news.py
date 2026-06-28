from fastapi import APIRouter
import os
import requests
import json

router = APIRouter()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = os.getenv("TAVILY_URL", "https://api.tavily.com/search")

@router.get("/")
def news_home():
    key_status = "✅ SET" if TAVILY_API_KEY else "❌ MISSING"
    url_status = "✅ SET" if TAVILY_URL else "❌ MISSING"
    
    return {
        "module": "news",
        "status": "🔥 LIVE",
        "source": "Tavily AI Search",
        "tavily_key": key_status,
        "tavily_url": url_status,
        "message": "Real news fetch ready — Singh Ji ka hukum do!"
    }

@router.get("/latest")
def get_latest_news(topic: str = "India", max_results: int = 5):
    """Tavily se real news fetch karo"""
    
    if not TAVILY_API_KEY:
        return {
            "ok": False,
            "error": "TAVILY_API_KEY not set",
            "message": "Render Dashboard → Environment → TAVILY_API_KEY add karo!"
        }
    
    try:
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
            return {
                "ok": False,
                "error": "No results from Tavily",
                "raw": data
            }
        
        # Clean format
        articles = []
        for item in data["results"]:
            articles.append({
                "title": item.get("title", "No title"),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:300] + "...",
                "published": item.get("published_date", "Recent"),
                "source": item.get("source", "Unknown"),
                "score": round(item.get("score", 0), 2)
            })
        
        return {
            "ok": True,
            "topic": topic,
            "total": len(articles),
            "articles": articles,
            "powered_by": "Tavily AI",
            "singh_ji_message": f"🦁 {topic} ki taza khabar aa gayi!"
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "News fetch fail — baad mein try karo bhai!"
        }

@router.get("/india")
def india_news():
    return get_latest_news(topic="India", max_results=5)

@router.get("/tech")
def tech_news():
    return get_latest_news(topic="technology India", max_results=5)

@router.get("/sports")
def sports_news():
    return get_latest_news(topic="sports India", max_results=5)

@router.get("/business")
def business_news():
    return get_latest_news(topic="business India", max_results=5)

@router.get("/entertainment")
def entertainment_news():
    return get_latest_news(topic="Bollywood entertainment India", max_results=5)

@router.get("/politics")
def politics_news():
    return get_latest_news(topic="Indian politics", max_results=5)

@router.get("/weather-news")
def weather_news():
    return get_latest_news(topic="weather India", max_results=5)
