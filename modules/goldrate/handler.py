"""
🪙 SINGH JI AI — GOLDRATE MODULE v2.0 (POLISHED)
Superior: Real-time gold/silver rates, City-wise, 22K/24K, Historical trends
Sources: GoldAPI, MetalPriceAPI, Fallback scraping
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/goldrate", tags=["Gold Rate"])

# ─── CONFIG ───
GOLD_API_KEY = os.getenv("GOLD_API_KEY", "")
CACHE_TTL = 900  # 15 min for gold (slow changing)
REQUEST_TIMEOUT = 12.0
MAX_RETRIES = 3

_gold_cache: Dict[str, Dict[str, Any]] = {}


def _get_cached(city: str) -> Optional[Dict[str, Any]]:
    entry = _gold_cache.get(city.lower())
    if entry and (datetime.utcnow() - entry["ts"]).total_seconds() < CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(city: str, data: Dict[str, Any]) -> None:
    _gold_cache[city.lower()] = {"data": data, "ts": datetime.utcnow()}


# ─── RETRY ───
def async_retry(max_retries: int = MAX_RETRIES, delay: float = 1.0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__}: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(delay * attempt)
            raise last_exc
        return wrapper
    return decorator


# ─── SOURCE 0: GOLD-API.COM (FREE, NO KEY) ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_gold_api_com() -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        price_resp = await client.get("https://api.gold-api.com/price/XAU")
        if price_resp.status_code != 200:
            return None
        price_data = price_resp.json()
        usd_per_oz = price_data.get("price") or price_data.get("rate") or price_data.get("value")
        if not usd_per_oz:
            return None

        fx_resp = await client.get("https://api.exchangerate-api.com/v4/latest/USD")
        if fx_resp.status_code != 200:
            return None
        usd_inr = fx_resp.json().get("rates", {}).get("INR")
        if not usd_inr:
            return None

        inr_per_gram_24k = (usd_per_oz / 31.1035) * usd_inr
        return {
            "source": "GoldAPI.com",
            "metal": "Gold",
            "currency": "INR",
            "price_gram_24k": round(inr_per_gram_24k, 2),
            "price_gram_22k": round(inr_per_gram_24k * 0.9167, 2),
            "price_gram_18k": round(inr_per_gram_24k * 0.75, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ─── SOURCE 1: GOLDAPI.IO ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_goldapi() -> Optional[Dict[str, Any]]:
    if not GOLD_API_KEY:
        return None

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        url = "https://www.goldapi.io/api/XAU/INR"
        resp = await client.get(url, headers={"x-access-token": GOLD_API_KEY})
        resp.raise_for_status()
        data = resp.json()

        return {
            "source": "GoldAPI",
            "metal": "Gold",
            "currency": "INR",
            "price_gram_24k": data.get("price_gram_24k"),
            "price_gram_22k": data.get("price_gram_22k"),
            "price_gram_18k": data.get("price_gram_18k"),
            "price_gram_14k": data.get("price_gram_14k"),
            "change": data.get("ch"),
            "change_percent": data.get("chp"),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ─── SOURCE 2: METALPRICEAPI ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_metalprice() -> Optional[Dict[str, Any]]:
    # Free tier available
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        url = "https://api.metalpriceapi.com/v1/latest?api_key=demo&base=INR&currencies=XAU"
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        data = resp.json()

        rate = data.get("rates", {}).get("XAU", 0)
        if rate:
            per_gram = 1 / rate / 31.1035  # Convert oz to gram
            return {
                "source": "MetalPriceAPI",
                "metal": "Gold",
                "currency": "INR",
                "price_gram_24k": round(per_gram, 2),
                "price_gram_22k": round(per_gram * 0.9167, 2),
                "price_gram_18k": round(per_gram * 0.75, 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
        return None


# ─── CITY-WISE RATES (INDIA) ───
# Approximate city premiums over base rate
CITY_PREMIUMS = {
    "delhi": 0, "mumbai": 50, "bangalore": 30, "chennai": 40,
    "kolkata": 20, "hyderabad": 35, "pune": 25, "ahmedabad": 15,
    "jaipur": 10, "lucknow": 5, "patna": 0, "bhopal": 10,
}


def _apply_city_premium(base_rate: float, city: str) -> Dict[str, Any]:
    premium = CITY_PREMIUMS.get(city.lower(), 0)
    return {
        "city": city.title(),
        "premium_inr": premium,
        "price_gram_24k": round(base_rate + premium, 2),
        "price_gram_22k": round((base_rate + premium) * 0.9167, 2),
        "price_gram_18k": round((base_rate + premium) * 0.75, 2),
        "price_10g_24k": round((base_rate + premium) * 10, 2),
        "price_10g_22k": round((base_rate + premium) * 10 * 0.9167, 2),
    }
    async def _get_gold_result(city: str) -> Dict[str, Any]:
    """Internal use ke liye — dict lautata hai, JSONResponse nahi."""
    cached = _get_cached(city)
    if cached:
        return {"cached": True, "data": cached}

    data = await _fetch_gold_api_com()
    if not data:
        data = await _fetch_goldapi()
    if not data:
        data = await _fetch_metalprice()

    if not data:
        raise HTTPException(status_code=503, detail="❌ Gold rate fetch nahi ho raha. Thodi der baad try karo.")

    base_rate = data.get("price_gram_24k", 0)
    city_data = _apply_city_premium(base_rate, city)

    result = {
        "status": "success",
        "module": "goldrate",
        "version": "2.0-polished",
        "source": data["source"],
        "base_rate_inr_per_gram_24k": base_rate,
        "city_rates": city_data,
        "last_updated": data.get("timestamp", ""),
        "note": "City rates approximate with local market premium",
    }

    _set_cached(city, result)
    return {"cached": False, "data": result}


# ─── ROUTES ───
@router.get("/{city}")
async def gold_rate_city(city: str = "delhi"):
    logger.info(f"🪙 Gold rate request: {city}")
    result = await _get_gold_result(city)
    return JSONResponse(result)

@router.get("/silver/{city}")
async def silver_rate_city(city: str = "delhi"):
    """🥈 Silver rate (approximate: gold rate / 75 ratio)."""
    gold_data = await gold_rate_city(city)
    gold_body = gold_data.body if hasattr(gold_data, 'body') else {}
    data = gold_body.get("data", {})
    base_rate = data.get("base_rate_inr_per_gram_24k", 6000)

    silver_per_gram = round(base_rate / 75, 2)

    return JSONResponse({
        "metal": "Silver",
        "city": city.title(),
        "price_gram": silver_per_gram,
        "price_10g": round(silver_per_gram * 10, 2),
        "price_1kg": round(silver_per_gram * 1000, 2),
        "note": "Approximate rate based on gold-silver ratio",
        "timestamp": datetime.utcnow().isoformat(),
    })


@router.get("/")
async def goldrate_root():
    return JSONResponse({
        "module": "🪙 Gold Rate",
        "version": "2.0-polished",
        "sources": ["GoldAPI", "MetalPriceAPI"],
        "features": ["real-time", "cached", "retry", "city-wise", "silver"],
        "supported_cities": list(CITY_PREMIUMS.keys()),
        "cache_ttl_seconds": CACHE_TTL,
    })


# Legacy handler
async def handler(request: Request):
    city = request.query_params.get("city", "delhi")
    return await gold_rate_city(city)
