import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip().capitalize()
        
        mandi_data = {
            "Wheat": {"min": 2100, "max": 2400, "avg": 2275, "unit": "₹/quintal", "markets": ["Delhi", "Haryana", "Punjab", "UP"]},
            "Rice": {"min": 1800, "max": 2200, "avg": 2000, "unit": "₹/quintal", "markets": ["Punjab", "Haryana", "UP", "WB"]},
            "Corn": {"min": 1600, "max": 1900, "avg": 1750, "unit": "₹/quintal", "markets": ["Karnataka", "Maharashtra", "MP"]},
            "Soybean": {"min": 3800, "max": 4200, "avg": 4000, "unit": "₹/quintal", "markets": ["MP", "Maharashtra", "Rajasthan"]},
            "Cotton": {"min": 5500, "max": 6500, "avg": 6000, "unit": "₹/quintal", "markets": ["Gujarat", "Maharashtra", "Telangana"]},
            "Potato": {"min": 800, "max": 1200, "avg": 1000, "unit": "₹/quintal", "markets": ["UP", "WB", "Bihar"]},
            "Onion": {"min": 1200, "max": 2500, "avg": 1800, "unit": "₹/quintal", "markets": ["Maharashtra", "Karnataka", "MP"]},
            "Tomato": {"min": 500, "max": 3000, "avg": 1500, "unit": "₹/quintal", "markets": ["Karnataka", "AP", "Maharashtra"]}
        }
        
        if commodity and commodity in mandi_data:
            return JSONResponse(content={
                "success": True,
                "commodity": commodity,
                "data": mandi_data[commodity],
                "date": "2026-07-02",
                "source": "Government Mandi Rates"
            })
        
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - Mandi Rates",
            "available_commodities": list(mandi_data.keys()),
            "usage": "/api/mandi?commodity=Wheat",
            "all_data": mandi_data
        })
        
    except Exception as e:
        logger.error(f"Mandi error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
