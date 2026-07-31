import os
import logging
import httpx
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ─── ये URL बिल्कुल सही है ──────────────────────────────────
MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"
# ──────────────────────────────────────────────────────────────

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        state = params.get("state", "").strip()
        commodity = params.get("commodity", "").strip()
        limit = min(int(params.get("limit", 20)), 100)

        # 1. API Key चेक
        if not MANDI_API_KEY:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "MANDI_API_KEY missing. कृपया Railway में डालें।"}
            )

        # 2. फ़िल्टर चेक
        if not state and not commodity:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "कम से कम state या commodity दें (जैसे: ?state=Uttar Pradesh)"}
            )

        # 3. API पैरामीटर – इसमें `api-key` QUERY PARAMETER है, HEADER नहीं!
        api_params = {
            "api-key": MANDI_API_KEY,   # <--- यही सही तरीका है
            "format": "json",
            "limit": limit
        }
        if state:
            api_params["filters[state.keyword]"] = state
        if commodity:
            api_params["filters[commodity.keyword]"] = commodity

        # 4. API कॉल – बिना किसी Authorization header के
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(MANDI_BASE_URL, params=api_params)

        # 5. रिस्पॉन्स चेक
        if resp.status_code != 200:
            return JSONResponse(
                status_code=resp.status_code,
                content={
                    "success": False,
                    "error": f"API Error {resp.status_code}",
                    "detail": resp.text[:200]
                }
            )

        data = resp.json()
        records = data.get("records", [])

        if not records:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"'{state or commodity}' पर कोई डेटा नहीं मिला",
                    "hint": "Uttar Pradesh, Punjab, Maharashtra, Haryana, Rajasthan आज़माएँ"
                }
            )

        # 6. सफल रिज़ल्ट
        return JSONResponse(content={
            "success": True,
            "state": state or "all",
            "commodity": commodity or "all",
            "count": len(records),
            "records": records,
            "source": "AGMARKNET_LIVE"
        })

    except httpx.TimeoutException:
        return JSONResponse(status_code=504, content={"success": False, "error": "API timeout – सर्वर ने जवाब नहीं दिया"})
    except Exception as e:
        logger.error(f"Mandi error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
