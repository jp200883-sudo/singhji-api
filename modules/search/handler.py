import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '') or os.environ.get('SERPAPI_API_KEY', '')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            query = params.get('q', '').strip()
            engine = params.get('engine', 'google')
            num = int(params.get('num', 5))
        else:
            body = await request.json()
            query = body.get('q', '').strip()
            engine = body.get('engine', 'google')
            num = int(body.get('num', 5))
        
        if not query:
            return JSONResponse(status_code=400, content={
                "success": False, "error": "Provide ?q=search_term", "data": None
            })
        
        # Try Tavily first (better for AI)
        if TAVILY_API_KEY:
            try:
                url = "https://api.tavily.com/search"
                resp = requests.post(url, json={
                    "api_key": TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": num
                }, timeout=15)
                data = resp.json()
                
                if resp.status_code == 200:
                    results = []
                    for r in data.get('results', []):
                        results.append({
                            "title": r.get('title', ''),
                            "url": r.get('url', ''),
                            "snippet": r.get('content', '')[:300]
                        })
                    return JSONResponse(content={
                        "success": True, "error": None,
                        "data": {"query": query, "source": "tavily", "results": results}
                    })
            except Exception as e:
                logger.error(f"Tavily failed: {e}")
        
        # Fallback to SerpAPI
        if SERPAPI_KEY:
            try:
                url = "https://serpapi.com/search"
                params_api = {
                    "q": query,
                    "engine": engine,
                    "api_key": SERPAPI_KEY,
                    "num": num
                }
                resp = requests.get(url, params=params_api, timeout=15)
                data = resp.json()
                
                if resp.status_code == 200:
                    organic = data.get('organic_results', [])
                    results = []
                    for r in organic[:num]:
                        results.append({
                            "title": r.get('title', ''),
                            "url": r.get('link', ''),
                            "snippet": r.get('snippet', '')
                        })
                    return JSONResponse(content={
                        "success": True, "error": None,
                        "data": {"query": query, "source": "serpapi", "results": results}
                    })
            except Exception as e:
                logger.error(f"SerpAPI failed: {e}")
        
        return JSONResponse(status_code=503, content={
            "success": False, "error": "No search API available", "data": None
        })
        
    except requests.exceptions.Timeout:
        logger.error("Search API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "Search API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"Search crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
