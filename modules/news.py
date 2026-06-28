# modules/news.py — Singh Ji AI Ultra
import os
import requests
from fastapi import APIRouter

router = APIRouter()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

@router.get("/latest")
def latest_news(category: str = "general", country: str = "in"):
    """Latest news — RapidAPI"""
    if not RAPIDAPI_KEY:
        return {
            "status": "mock",
            "category": category,
            "headlines": [
                {"title": "🦁 Singh Ji AI Launch hone wala hai!", "source": "Singh Ji Times", "time": "Just now"},
                {"title": "Bharat ka sabse tez AI super app", "source": "Tech India", "time": "1 hour ago"}
            ]
        }
    
    try:
        url = "https://news-api14.p.rapidapi.com/v2/search/publishers"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "news-api14.p.rapidapi.com"
        }
        # Or use specific news endpoint
        url = "https://news-api14.p.rapidapi.com/top-headlines"
        querystring = {"country": country, "language": "en", "pageSize": 10, "category": category}
        
        res = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = res.json()
        
        articles = []
        for item in data.get("articles", [])[:5]:
            articles.append({
                "title": item.get("title", "No title"),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "image": item.get("urlToImage", ""),
                "source": item.get("source", {}).get("name", "Unknown"),
                "published": item.get("publishedAt", "Now")
            })
        
        return {"status": "live", "category": category, "count": len(articles), "news": articles}
    except Exception as e:
        return {"error": str(e), "fallback": "mock"}

@router.get("/headlines")
def headlines():
    """Quick headlines"""
    return latest_news(category="general")
