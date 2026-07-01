import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

CURRENTS_API_KEY = os.environ.get('CURRENTS_API_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            keywords = params.get('keywords', '').strip()
            language = params.get('language', 'en').strip()
            country = params.get('country', '').strip()
            num = int(params.get('num', 5))
        else:
            body = await request.json()
            keywords = body.get('keywords', '').strip()
            language = body.get('language', 'en').strip()
            country = body.get('country', '').strip()
            num = int(body.get('num', 5))
        
        if not CURRENTS_API_KEY:
            return JSONResponse(status_code=503, content={
                "success": False, "error": "CURRENTS_API_KEY not configured", "data": None
            })
        
        url = "https://api.currentsapi.services/v1/latest-news"
        headers = {"Authorization": CURRENTS_API_KEY}
        params_api = {"language": language, "limit": num}
        
        if keywords:
            params_api["keywords"] = keywords
        if country:
            params_api["country"] = country
        
        resp = requests.get(url, headers=headers, params=params_api, timeout=15)
        data = resp.json()
        
        if resp.status_code == 200:
            articles = []
            for a in data.get('news', [])[:num]:
                articles.append({
                    "title": a.get('title', ''),
                    "description": a.get('description', '') or '',
                    "url": a.get('url', ''),
                    "author": a.get('author', ''),
                    "published": a.get('published', ''),
                    "image": a.get('image', ''),
                    "category": a.get('category', [])
                })
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "total": len(articles),
                    "keywords": keywords or "latest",
                    "articles": articles
                }
            })
        
        return JSONResponse(status_code=resp.status_code, content={
            "success": False, "error": data.get('message', 'Currents API error'), "data": None
        })
        
    except requests.exceptions.Timeout:
        logger.error("Currents API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "Currents API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"Currents crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
