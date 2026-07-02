"""
📰 Singh Ji AI Ultra v7.0 — News/Currents Module
NewsAPI + GNews fallback (Free tiers)
"""
import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        keywords = params.get("keywords", "India").strip()
        num = min(int(params.get("num", 5)), 10)  # Max 10
        country = params.get("country", "in").strip().lower()
        lang = params.get("lang", "hi").strip().lower()
        
        articles = []
        source_used = None
        
        # Try 1: NewsAPI (100 requests/day free)
        newsapi_key = os.getenv("NEWS_API_KEY")
        if newsapi_key and not articles:
            try:
                url = (
                    f"https://newsapi.org/v2/everything?"
                    f"q={keywords}&pageSize={num}&language={lang}&"
                    f"sortBy=publishedAt&apiKey={newsapi_key}"
                )
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if data.get("status") == "ok" and data.get("articles"):
                    for a in data["articles"]:
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("url", ""),
                            "image": a.get("urlToImage", ""),
                            "published": a.get("publishedAt", ""),
                            "source": a.get("source", {}).get("name", "NewsAPI")
                        })
                    source_used = "newsapi.org"
            except Exception as e:
                logger.error(f"NewsAPI failed: {e}")
        
        # Try 2: GNews (100 requests/day free)
        gnews_key = os.getenv("GNEWS_API_KEY")
        if gnews_key and not articles:
            try:
                url = (
                    f"https://gnews.io/api/v4/search?"
                    f"q={keywords}&max={num}&lang={lang}&country={country}&"
                    f"apikey={gnews_key}"
                )
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if data.get("articles"):
                    for a in data["articles"]:
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("url", ""),
                            "image": a.get("image", ""),
                            "published": a.get("publishedAt", ""),
                            "source": a.get("source", {}).get("name", "GNews")
                        })
                    source_used = "gnews.io"
            except Exception as e:
                logger.error(f"GNews failed: {e}")
        
        # Try 3: NewsData.io (200 requests/day free)
        newsdata_key = os.getenv("NEWSDATA_API_KEY")
        if newsdata_key and not articles:
            try:
                url = (
                    f"https://newsdata.io/api/1/news?"
                    f"apikey={newsdata_key}&q={keywords}&"
                    f"language={lang}&country={country}&size={num}"
                )
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if data.get("results"):
                    for a in data["results"]:
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("link", ""),
                            "image": a.get("image_url", ""),
                            "published": a.get("pubDate", ""),
                            "source": a.get("source_id", "NewsData")
                        })
                    source_used = "newsdata.io"
            except Exception as e:
                logger.error(f"NewsData failed: {e}")
        
        # Fallback: Mock data if all APIs fail
        if not articles:
            articles = [
                {
                    "title": f"Latest news about {keywords}",
                    "description": "News API temporarily unavailable. Please check your API keys in Render environment variables.",
                    "url": "https://news.google.com",
                    "image": "",
                    "published": "",
                    "source": "Fallback"
                }
            ]
            source_used = "fallback (no API keys configured)"
        
        # TTS
        tts = f"समाचार अपडेट। {keywords} से जुड़ी {len(articles)} खबरें मिलीं।"
        if articles:
            tts += f" पहली खबर: {articles[0]['title'][:80]}..."
        
        return JSONResponse(content={
            "success": True,
            "keywords": keywords,
            "count": len(articles),
            "source": source_used,
            "articles": articles,
            "tts": tts,
            "usage": "/api/currents_api?keywords=India&num=5&country=in&lang=hi"
        })
        
    except Exception as e:
        logger.error(f"Currents error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "tts": "समाचार लाने में त्रुटि हुई। कृपया पुनः प्रयास करें।"
        })
