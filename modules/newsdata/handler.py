import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

NEWSDATA_API_KEY = os.environ.get('NEWSDATA_API_KEY', '')
CURRENTS_API_KEY = os.environ.get('CURRENTS_API_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            q = params.get('q', '').strip()
            country = params.get('country', 'in')
            category = params.get('category', '')
            num = int(params.get('num', 5))
        else:
            body = await request.json()
            q = body.get('q', '').strip()
            country = body.get('country', 'in')
            category = body.get('category', '')
            num = int(body.get('num', 5))
        
        # Try NewsData.io first
        if NEWSDATA_API_KEY:
            try:
                url = "https://newsdata.io/api/1/latest"
                params_api = {
                    "apikey": NEWSDATA_API_KEY,
                    "country": country,
                    "language": "hi,en",
                    "size": num
                }
                if q:
                    params_api["q"] = q
                if category:
                    params_api["category"] = category
                    
                resp = requests.get(url, params=params_api, timeout=15)
                data = resp.json()
                
                if resp.status_code == 200:
                    articles = []
                    for a in data.get('results', [])[:num]:
                        articles.append({
                            "title": a.get('title', ''),
                            "description": a.get('description', '') or '',
                            "url": a.get('link', ''),
                            "source": a.get('source_id', ''),
                            "published": a.get('pubDate', ''),
                            "image": a.get('image_url', '')
                        })
                    return JSONResponse(content={
                        "success": True, "error": None,
                        "data": {"query": q or "latest", "source": "newsdata", "articles": articles}
                    })
            except Exception as e:
                logger.error(f"NewsData failed: {e}")
        
        # Fallback to Currents API
        if CURRENTS_API_KEY:
            try:
                url = "https://api.currentsapi.services/v1/latest-news"
                headers = {"Authorization": CURRENTS_API_KEY}
                params_api = {"language": "en", "country": country}
                if q:
                    params_api["keywords"] = q
                    
                resp = requests.get(url, headers=headers, params=params_api, timeout=15)
                data = resp.json()
                
                if resp.status_code == 200:
                    articles = []
                    for a in data.get('news', [])[:num]:
                        articles.append({
                            "title": a.get('title', ''),
                            "description": a.get('description', '') or '',
                            "url": a.get('url', ''),
                            "source": a.get('author', ''),
                            "published": a.get('published', ''),
                            "image": a.get('image', '')
                        })
                    return JSONResponse(content={
                        "success": True, "error": None,
                        "data": {"query": q or "latest", "source": "currents", "articles": articles}
                    })
            except Exception as e:
                logger.error(f"Currents API failed: {e}")
        
        return JSONResponse(status_code=503, content={
            "success": False, "error": "No news API available", "data": None
        })
        
    except requests.exceptions.Timeout:
        logger.error("News API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "News API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"News crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
