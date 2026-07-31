import os
import requests
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"


# Synchronous version for thread pool execution
def _fetch_mandi_sync(commodity: str = "", state: str = "", limit: int = 20):
    """Synchronous function to fetch mandi data from API"""
    if not MANDI_API_KEY:
        raise ValueError("MANDI_API_KEY missing")
    
    api_params = {
        "api-key": MANDI_API_KEY,
        "format": "json",
        "limit": limit
    }
    
    if commodity:
        api_params["filters[commodity.keyword]"] = commodity.capitalize()
    if state:
        api_params["filters[state.keyword]"] = state
    
    resp = requests.get(MANDI_BASE_URL, params=api_params, timeout=15)
    resp.raise_for_status()  # Raise exception for bad status codes
    
    data = resp.json()
    records = data.get("records", [])
    
    if not records:
        return {
            "success": False,
            "error": "Is filter ke liye data nahi mila",
            "hint": "commodity ya state ka naam check karo",
            "commodity": commodity or "all",
            "state": state or "all",
            "count": 0,
            "records": []
        }
    
    return {
        "success": True,
        "commodity": commodity or "all",
        "state": state or "all",
        "count": len(records),
        "records": records,
        "source": "AGMARKNET_LIVE"
    }


async def handler(request: Request):
    """
    Mandi (Agricultural Market) API Handler
    
    Query Parameters:
    - commodity: (optional) Filter by commodity name
    - state: (optional) Filter by state name
    - limit: (optional) Number of records to return (default: 20, max: 100)
    
    Example: /api/mandi?commodity=wheat&state=uttar%20pradesh&limit=10
    """
    try:
        # Parse query parameters
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip()
        state = params.get("state", "").strip()
        
        # Limit validation
        try:
            limit = int(params.get("limit", 20))
            if limit < 1:
                limit = 1
            elif limit > 100:
                limit = 100  # API limit
        except ValueError:
            limit = 20
        
        # Validate API key is present
        if not MANDI_API_KEY:
            logger.error("MANDI_API_KEY environment variable not set")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "MANDI_API_KEY missing. Please set MANDI_API_KEY environment variable.",
                    "hint": "Get API key from https://data.gov.in/"
                }
            )
        
        # Validate at least one filter is provided
        if not commodity and not state:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "At least one filter required",
                    "hint": "Use commodity or state parameter (e.g., ?commodity=wheat or ?state=uttar%20pradesh)",
                    "available_examples": [
                        "?commodity=wheat",
                        "?state=uttar%20pradesh",
                        "?commodity=rice&state=punjab"
                    ]
                }
            )
        
        # Execute in thread pool to avoid blocking the async event loop
        result = await run_in_threadpool(
            _fetch_mandi_sync,
            commodity=commodity,
            state=state,
            limit=limit
        )
        
        # Return appropriate response
        if result.get("success"):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            # Data not found but API was accessible
            return JSONResponse(
                status_code=404,
                content=result
            )
            
    except requests.exceptions.Timeout:
        logger.error(f"Mandi API timeout: commodity={commodity}, state={state}")
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "error": "Mandi API timeout - server took too long to respond",
                "hint": "Try with more specific filters to reduce data size"
            }
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Mandi API connection error: commodity={commodity}, state={state}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Mandi API connection failed - please check network",
                "hint": "Try again later"
            }
        )
    except requests.exceptions.HTTPError as e:
        logger.error(f"Mandi API HTTP error: {e}")
        return JSONResponse(
            status_code=e.response.status_code if hasattr(e, 'response') else 500,
            content={
                "success": False,
                "error": f"API returned error: {str(e)}",
                "hint": "Check if filters are valid"
            }
        )
    except ValueError as e:
        logger.error(f"Mandi validation error: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Mandi unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(e) if os.getenv("DEBUG", "false").lower() == "true" else "Contact administrator"
            }
        )


# Alternative async version using httpx (if you want to use the global HTTP client)
async def handler_async_httpx(request: Request, http_client=None):
    """
    Alternative async version using httpx client.
    To use this, pass http_client from the main app.
    """
    try:
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip()
        state = params.get("state", "").strip()
        limit = int(params.get("limit", 20))
        
        if not MANDI_API_KEY:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "MANDI_API_KEY missing"}
            )
        
        # Validate filters
        if not commodity and not state:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "At least one filter required (commodity or state)"
                }
            )
        
        api_params = {
            "api-key": MANDI_API_KEY,
            "format": "json",
            "limit": min(limit, 100)
        }
        
        if commodity:
            api_params["filters[commodity.keyword]"] = commodity.capitalize()
        if state:
            api_params["filters[state.keyword]"] = state
        
        # Use the global HTTP client if provided, otherwise create a new one
        if http_client:
            resp = await http_client.get(MANDI_BASE_URL, params=api_params, timeout=15)
        else:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(MANDI_BASE_URL, params=api_params)
        
        data = resp.json()
        records = data.get("records", [])
        
        if not records:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "No data found for the given filters",
                    "hint": "Try different commodity or state"
                }
            )
        
        return JSONResponse(content={
            "success": True,
            "commodity": commodity or "all",
            "state": state or "all",
            "count": len(records),
            "records": records,
            "source": "AGMARKNET_LIVE"
        })
        
    except Exception as e:
        logger.error(f"Mandi error (httpx): {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# Cache wrapper for the handler (optional)
from functools import lru_cache
from datetime import datetime, timedelta

_cache = {}
_cache_expiry = {}

def _get_cached_mandi(commodity: str, state: str, limit: int):
    """Get cached mandi data with 6-hour TTL"""
    key = f"{commodity}:{state}:{limit}"
    now = datetime.now()
    
    if key in _cache and key in _cache_expiry:
        if now < _cache_expiry[key]:
            return _cache[key]
        else:
            # Cache expired
            del _cache[key]
            del _cache_expiry[key]
    
    return None

def _set_cached_mandi(commodity: str, state: str, limit: int, data):
    """Cache mandi data for 6 hours"""
    key = f"{commodity}:{state}:{limit}"
    _cache[key] = data
    _cache_expiry[key] = datetime.now() + timedelta(hours=6)


async def handler_with_cache(request: Request):
    """
    Mandi handler with built-in caching for 6 hours
    """
    try:
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip()
        state = params.get("state", "").strip()
        limit = int(params.get("limit", 20))
        
        # Check cache first
        cached_data = _get_cached_mandi(commodity, state, limit)
        if cached_data:
            cached_data["source"] = "CACHE"
            return JSONResponse(content=cached_data)
        
        # Fetch fresh data
        result = await handler(request)
        # If successful, cache it
        if result.status_code == 200:
            data = result.body
            import json
            data_dict = json.loads(data)
            _set_cached_mandi(commodity, state, limit, data_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Mandi cache handler error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
