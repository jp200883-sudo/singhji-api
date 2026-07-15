import os
import logging
import requests
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"


async def handler(request: Request):
    try:
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip()
        state = params.get("state", "").strip()
        limit = int(params.get("limit", 20))

        if not MANDI_API_KEY:
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": "MANDI_API_KEY missing"
            })

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
        data = resp.json()
        records = data.get("records", [])

        if not records:
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": "Is filter ke liye data nahi mila",
                "hint": "commodity ya state ka naam check karo"
            })

        return JSONResponse(content={
            "success": True,
            "commodity": commodity or "all",
            "state": state or "all",
            "count": len(records),
            "records": records,
            "source": "AGMARKNET_LIVE"
        })

    except Exception as e:
        logger.error(f"Mandi error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
