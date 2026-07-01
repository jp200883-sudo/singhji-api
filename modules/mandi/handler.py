import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

MANDI_API_KEY = os.environ.get('MANDI_API_KEY', '')
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            commodity = params.get('commodity', '').strip()
            state = params.get('state', '').strip()
            market = params.get('market', '').strip()
        else:
            body = await request.json()
            commodity = body.get('commodity', '').strip()
            state = body.get('state', '').strip()
            market = body.get('market', '').strip()
        
        # Try data.gov.in mandi API
        if MANDI_API_KEY:
            try:
                url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
                params_api = {
                    "api-key": MANDI_API_KEY,
                    "format": "json",
                    "limit": 10
                }
                if commodity:
                    params_api["filters[commodity]"] = commodity
                if state:
                    params_api["filters[state]"] = state
                    
                resp = requests.get(url, params=params_api, timeout=15)
                data = resp.json()
                
                if resp.status_code == 200:
                    records = data.get('records', [])
                    results = []
                    for r in records:
                        results.append({
                            "state": r.get('state', ''),
                            "district": r.get('district', ''),
                            "market": r.get('market', ''),
                            "commodity": r.get('commodity', ''),
                            "variety": r.get('variety', ''),
                            "min_price": r.get('min_price', ''),
                            "max_price": r.get('max_price', ''),
                            "modal_price": r.get('modal_price', ''),
                            "date": r.get('arrival_date', '')
                        })
                    return JSONResponse(content={
                        "success": True, "error": None,
                        "data": {"commodity": commodity or "all", "records": results}
                    })
            except Exception as e:
                logger.error(f"Mandi API failed: {e}")
        
        # Fallback demo data
        demo_data = [
            {"commodity": "Wheat", "market": "Delhi", "min_price": 2100, "max_price": 2300, "modal_price": 2200},
            {"commodity": "Rice", "market": "Mumbai", "min_price": 3500, "max_price": 4000, "modal_price": 3750},
            {"commodity": "Onion", "market": "Nashik", "min_price": 800, "max_price": 1200, "modal_price": 1000}
        ]
        
        if commodity:
            demo_data = [d for d in demo_data if commodity.lower() in d['commodity'].lower()]
        
        return JSONResponse(content={
            "success": True, "error": None,
            "data": {"commodity": commodity or "all", "source": "demo", "records": demo_data}
        })
        
    except requests.exceptions.Timeout:
        logger.error("Mandi API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "Mandi API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"Mandi crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
