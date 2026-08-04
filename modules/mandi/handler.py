from fastapi import APIRouter
from core.config import config
from core.cache import cache_get, cache_set
import httpx

router = APIRouter()

@router.get("/")
async def mandi_handler():
    return {
        "status": "ok",
        "module": "mandi",
        "message": "Mandi rates API - Use /api/v1/mandi/rates?state=up&crop=wheat"
    }

@router.get("/rates")
async def get_mandi_rates(state: str = None, crop: str = None):
    """Get mandi rates for a state and crop"""
    cache_key = f"mandi_{state}_{crop}"
    
    # Cache check
    cached = cache_get(cache_key)
    if cached:
        return {"status": "ok", "source": "cache", "data": cached}
    
    # API call
    try:
        base_url = config.get("MANDI_BASE_URL")
        params = {
            "api-key": config.get("MANDI_API_KEY"),
            "format": "json",
            "limit": 50
        }
        if state:
            params["filters[state]"] = state
        if crop:
            params["filters[commodity]"] = crop
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=10)
            data = response.json()
        
        # Cache save
        cache_set(cache_key, data, 21600)  # 6 hours TTL
        return {"status": "ok", "source": "api", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
