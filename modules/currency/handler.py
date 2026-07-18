import httpx
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    method = request.method
    if method == "GET":
        params = dict(request.query_params)
    else:
        params = await request.json()

    base = str(params.get('base', 'USD')).upper()
    target = str(params.get('target', 'INR')).upper()

    try:
        amount = float(params.get('amount', 1))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={
            "success": False, "error": "amount एक संख्या होनी चाहिए", "data": None
        })

    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
        data = resp.json()

        if resp.status_code != 200:
            return JSONResponse(status_code=503, content={
                "success": False, "error": "Currency API unavailable", "data": None
            })

        rate = data.get('rates', {}).get(target)
        if not rate:
            return JSONResponse(status_code=400, content={
                "success": False, "error": f"Currency {target} not found", "data": None
            })

        converted = round(amount * rate, 2)
        return JSONResponse(content={
            "success": True, "error": None,
            "data": {
                "base": base, "target": target, "amount": amount,
                "rate": rate, "converted": converted,
                "date": data.get('date', '')
            }
        })

    except httpx.TimeoutException:
        logger.error("Currency API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "Currency API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"Currency crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
