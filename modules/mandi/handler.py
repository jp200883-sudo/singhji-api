import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Approx conversion rates to INR (per unit) — update periodically or wire to a live FX API
FX_TO_INR = {
    "USD": 85.5,
    "EUR": 92.0,
    "AUD": 56.0,
    "CAD": 62.5,
    "ARS": 0.09,   # Argentina peso (approx, very volatile)
    "RUB": 0.95,
    "UAH": 2.05,
    "CNY": 11.8,
    "BRL": 15.2,
    "INR": 1.0
}

def to_inr_per_quintal(price, currency, unit_kg=100):
    """Convert a price given in local currency per some kg-unit to INR per quintal (100kg)."""
    rate = FX_TO_INR.get(currency, 1.0)
    price_inr = price * rate
    # normalize to per-quintal (100kg)
    return round(price_inr * (100 / unit_kg), 2)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        commodity = params.get("commodity", "").strip().capitalize()
        scope = params.get("scope", "india").strip().lower()  # "india" | "global" | "all"

        # ---------------- India mandi data (existing) ----------------
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

        # ---------------- Global market data (country-wise, local currency + unit) ----------------
        # NOTE: These are static reference/demo values. For production, wire this to a live
        # commodity-exchange API (e.g. CBOT, MCX, Investing.com) instead of hardcoding.
        global_data = {
            "Wheat": [
                {"country": "USA",       "price": 210, "currency": "USD", "unit_kg": 1000},  # $/tonne
                {"country": "Russia",    "price": 14500, "currency": "RUB", "unit_kg": 1000},
                {"country": "Ukraine",   "price": 195, "currency": "USD", "unit_kg": 1000},
                {"country": "Australia", "price": 340, "currency": "AUD", "unit_kg": 1000},
                {"country": "Canada",    "price": 260, "currency": "CAD", "unit_kg": 1000},
                {"country": "Argentina", "price": 220000, "currency": "ARS", "unit_kg": 1000},
            ],
            "Rice": [
                {"country": "Thailand",  "price": 560, "currency": "USD", "unit_kg": 1000},
                {"country": "Vietnam",   "price": 520, "currency": "USD", "unit_kg": 1000},
                {"country": "USA",       "price": 640, "currency": "USD", "unit_kg": 1000},
            ],
            "Corn": [
                {"country": "USA",       "price": 175, "currency": "USD", "unit_kg": 1000},
                {"country": "Brazil",    "price": 850, "currency": "BRL", "unit_kg": 1000},
                {"country": "Argentina", "price": 180000, "currency": "ARS", "unit_kg": 1000},
            ],
            "Soybean": [
                {"country": "USA",       "price": 420, "currency": "USD", "unit_kg": 1000},
                {"country": "Brazil",    "price": 2100, "currency": "BRL", "unit_kg": 1000},
                {"country": "Argentina", "price": 400000, "currency": "ARS", "unit_kg": 1000},
            ],
            "Cotton": [
                {"country": "USA",  "price": 1500, "currency": "USD", "unit_kg": 1000},
                {"country": "China", "price": 14500, "currency": "CNY", "unit_kg": 1000},
            ],
        }

        def build_global_block(name):
            entries = global_data.get(name, [])
            enriched = []
            for e in entries:
                inr_val = to_inr_per_quintal(e["price"], e["currency"], e["unit_kg"])
                enriched.append({
                    "country": e["country"],
                    "local_price": e["price"],
                    "local_currency": e["currency"],
                    "price_inr_per_quintal": inr_val
                })
            return enriched

        # ---------------- Single commodity lookup ----------------
        if commodity:
            if commodity not in mandi_data and commodity not in global_data:
                return JSONResponse(status_code=404, content={
                    "success": False,
                    "error": f"'{commodity}' ke liye data available nahi hai",
                    "available_commodities": sorted(set(list(mandi_data.keys()) + list(global_data.keys())))
                })

            result = {
                "success": True,
                "commodity": commodity,
                "date": "2026-07-02",
                "source": "Government Mandi Rates + Global Exchange (demo data)"
            }

            if scope in ("india", "all") and commodity in mandi_data:
                result["india"] = mandi_data[commodity]

            if scope in ("global", "all") and commodity in global_data:
                result["global"] = build_global_block(commodity)

            return JSONResponse(content=result)

        # ---------------- No commodity specified -> show menu ----------------
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - Mandi Rates (India + Global)",
            "available_commodities": sorted(set(list(mandi_data.keys()) + list(global_data.keys()))),
            "usage": [
                "/api/mandi?commodity=Wheat              -> India rates",
                "/api/mandi?commodity=Wheat&scope=global  -> Global rates in INR",
                "/api/mandi?commodity=Wheat&scope=all     -> Dono"
            ]
        })

    except Exception as e:
        logger.error(f"Mandi error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
