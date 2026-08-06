import os
from fastapi import APIRouter
from core.cache import cache_get, cache_set
import httpx

router = APIRouter()

DATA_GOV_API_KEY = os.environ.get("DATAGOVINDIA_API_KEY", "")
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Variety-wise Daily Market Prices
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"


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

    if not DATA_GOV_API_KEY:
        return {"status": "error", "message": "DATAGOVINDIA_API_KEY not set"}

    # API call
    try:
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": 50
        }
        if state:
            params["filters[state]"] = state
        if crop:
            params["filters[commodity]"] = crop

        async with httpx.AsyncClient() as client:
            response = await client.get(MANDI_BASE_URL, params=params, timeout=10)
            data = response.json()

        # Cache save
        cache_set(cache_key, data, 21600)  # 6 hours TTL
        return {"status": "ok", "source": "api", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
