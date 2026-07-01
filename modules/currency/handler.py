import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            base = params.get('base', 'USD').upper()
            target = params.get('target', 'INR').upper()
            amount = float(params.get('amount', 1))
        else:
            body = await request.json()
            base = body.get('base', 'USD').upper()
            target = body.get('target', 'INR').upper()
            amount = float(body.get('amount', 1))
        
        # Free exchangerate-api
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if resp.status_code == 200:
                rate = data['rates'].get(target)
                if not rate:
                    return JSONResponse(status_code=400, content={
                        "success": False, "error": f"Currency {target} not found", "data": None
                    })
                
                converted = round(amount * rate, 2)
                return JSONResponse(content={
                    "success": True, "error": None,
                    "data": {
                        "base": base,
                        "target": target,
                        "amount": amount,
                        "rate": rate,
                        "converted": converted,
                        "date": data.get('date', '')
                    }
                })
        except Exception as e:
            logger.error(f"Exchange rate API failed: {e}")
        
        return JSONResponse(status_code=503, content={
            "success": False, "error": "Currency API unavailable", "data": None
        })
        
    except requests.exceptions.Timeout:
        logger.error("Currency API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, "error": "Currency API timeout", "data": None
        })
    except Exception as e:
        logger.error(f"Currency crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
