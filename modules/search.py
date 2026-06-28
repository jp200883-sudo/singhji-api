# modules/search.py — Singh Ji AI Ultra v5.0
# Web Search — Google Custom Search + DuckDuckGo fallback

from fastapi import APIRouter
import os
import requests
import urllib.parse

router = APIRouter()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX = os.getenv("GOOGLE_CX", "")  # Custom Search Engine ID

@router.get("/")
def search_root():
    return {"module": "search", "status": "✅ Live", "engines": ["google", "duckduckgo"]}

@router.get("/web")
def web_search(query: str, limit: int = 5):
    """Web search — Google first, DuckDuckGo fallback"""
    
    # Try Google Custom Search
    if GOOGLE_API_KEY and GOOGLE_CX:
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CX,
                "q": query,
                "num": min(limit, 10)
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "items" in data:
                results = []
                for item in data["items"]:
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "source": "google"
                    })
                return {
                    "success": True,
                    "query": query,
                    "engine": "google",
                    "total": len(results),
                    "results": results
                }
        except Exception as e:
            pass
    
    # Fallback: DuckDuckGo Instant Answer
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        headers = {"User-Agent": "SinghJiAI/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        results = []
        
        # Abstract/Definition
        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", query),
                "link": data.get("AbstractURL", ""),
                "snippet": data.get("AbstractText"),
                "source": "duckduckgo"
            })
        
        # Related Topics
        for topic in data.get("RelatedTopics", [])[:limit-1]:
            if "Text" in topic:
                results.append({
                    "title": topic.get("Text", "")[:50],
                    "link": topic.get("FirstURL", ""),
                    "snippet": topic.get("Text", ""),
                    "source": "duckduckgo"
                })
        
        return {
            "success": True,
            "query": query,
            "engine": "duckduckgo",
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Search failed. Check API keys."
        }

@router.get("/news")
def search_news(query: str = "India", limit: int = 5):
    """News search using NewsData.io (if available)"""
    from modules import newsdata
    
    try:
        result = newsdata.get_india_news(query=query, language="en")
        if result.get("success"):
            articles = result.get("articles", [])[:limit]
            return {
                "success": True,
                "query": query,
                "total": len(articles),
                "results": articles
            }
    except:
        pass
    
    return {"success": False, "message": "News search unavailable"}

@router.get("/images")
def search_images(query: str, limit: int = 5):
    """Image search — placeholder for future"""
    return {
        "success": True,
        "message": "Image search coming soon",
        "query": query,
        "suggestion": "Use /web search for image links"
    }
