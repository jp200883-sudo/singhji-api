"""
📰 Singh Ji AI Ultra v7.0 — News/Currents Module
Uses: CurrentsAPI → NewsData → Fallback
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
        num = min(int(params.get("num", 5)), 10)
        country = params.get("country", "in").strip().lower()
        lang = params.get("lang", "hi").strip().lower()
        
        articles = []
        source_used = None
        
        # Try 1: CurrentsAPI (your key)
        currents_key = os.getenv("CURRENTS_API_KEY")
        if currents_key and not articles:
            try:
                url = (
                    f"https://api.currentsapi.services/v1/search?"
                    f"keywords={keywords}&language={lang}&"
                    f"apiKey={currents_key}"
                )
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if data.get("status") == "ok" and data.get("news"):
                    for a in data["news"][:num]:
                        articles.append({
                            "title": a.get("title", ""),
                            "description": a.get("description", ""),
                            "url": a.get("url", ""),
                            "image": a.get("image", "") or a.get("image_url", ""),
                            "published": a.get("published", ""),
                            "source": a.get("author", "CurrentsAPI")
                        })
                    source_used = "currentsapi.services"
            except Exception as e:
                logger.error(f"CurrentsAPI failed: {e}")
        
        # Try 2: NewsData.io (your key)
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
        
        # Fallback
        if not articles:
            articles = [{
                "title": f"No news found for '{keywords}'",
                "description": "Try different keywords or check API quotas.",
                "url": "https://news.google.com",
                "image": "",
                "published": "",
                "source": "Fallback"
            }]
            source_used = "fallback"
        
        tts = f"समाचार अपडेट। {keywords} से जुड़ी {len(articles)} खबरें मिलीं।"
        if articles and articles[0].get("title"):
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
            "tts": "समाचार लाने में त्रुटि हुई।"
        })
