"""
🌤️ SINGH JI AI — WEATHER MODULE v2.0 (POLISHED)
Superior: Async, Cached, Retry, Rate-Limited, Multi-Source
Primary: Open-Meteo (Free, No API Key)
Fallback: OpenWeatherMap
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import lru_cache

import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weather", tags=["Weather"])

# ─── CONFIG ───
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CACHE_TTL_SECONDS = 300  # 5 min cache
REQUEST_TIMEOUT = 15.0
MAX_RETRIES = 3

# WMO Weather codes → Hinglish descriptions
WMO_CODES: Dict[int, str] = {
    0: "☀️ Saaf aasmaan", 1: "🌤️ Halki dhoop", 2: "⛅ Baadal", 3: "☁️ Ghaney baadal",
    45: "🌫️ Kohra", 48: "🌫️ Ghaney kohra",
    51: "🌦️ Halki boondaa-baanndi", 53: "🌧️ Boondaa-baanndi", 55: "🌧️ Tez boondaa-baanndi",
    56: "🌧️ Halki barfili boondaa-baanndi", 57: "🌧️ Tez barfili boondaa-baanndi",
    61: "🌧️ Halki baarish", 63: "🌧️ Baarish", 65: "🌧️ Tez baarish",
    66: "🌨️ Halki barfili baarish", 67: "🌨️ Tez barfili baarish",
    71: "🌨️ Halki barf", 73: "🌨️ Barf", 75: "🌨️ Tez barf",
    77: "🌨️ Barf ke daane",
    80: "🌧️ Halki boondaa-baanndi (tez)", 81: "🌧️ Boondaa-baanndi (tez)", 82: "🌧️ Tez boondaa-baanndi (tez)",
    85: "🌨️ Halki barf-baarish", 86: "🌨️ Tez barf-baarish",
    95: "⛈️ Gharjna", 96: "⛈️ Gharjna + aasmani bijli", 99: "⛈️ Tez gharjna + bijli",
}

# ─── IN-MEMORY CACHE ───
_weather_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(city: str, lang: str) -> str:
    return f"{city.lower().strip()}:{lang}"


def _get_cached(city: str, lang: str) -> Optional[Dict[str, Any]]:
    key = _cache_key(city, lang)
    entry = _weather_cache.get(key)
    if entry and (datetime.utcnow() - entry["ts"]).seconds < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cached(city: str, lang: str, data: Dict[str, Any]) -> None:
    _weather_cache[_cache_key(city, lang)] = {"data": data, "ts": datetime.utcnow()}


# ─── RETRY DECORATOR ───
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


# ─── OPEN-METEO (PRIMARY) ───
@async_retry(max_retries=3, delay=1.0)
async def _fetch_openmeteo(city: str, lang: str = "hi") -> Optional[Dict[str, Any]]:
    """Fetch weather from Open-Meteo (free, no API key)."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        # Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language={lang}"
        geo_resp = await client.get(geo_url)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return None

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        display_name = geo_data["results"][0].get("name", city)
        country = geo_data["results"][0].get("country", "")

        # Weather forecast
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"weather_code,wind_speed_10m,wind_direction_10m,pressure_msl"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
            f"&timezone=auto&forecast_days=3"
        )
        w_resp = await client.get(weather_url)
        w_resp.raise_for_status()
        w_data = w_resp.json()

        current = w_data.get("current", {})
        daily = w_data.get("daily", {})

        code = current.get("weather_code", 0)

        return {
            "source": "Open-Meteo",
            "city": display_name,
            "country": country,
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "pressure": current.get("pressure_msl"),
            "condition_code": code,
            "condition": WMO_CODES.get(code, "🌡️ Mausam"),
            "forecast": [
                {
                    "date": daily["time"][i],
                    "max": daily["temperature_2m_max"][i],
                    "min": daily["temperature_2m_min"][i],
                    "condition": WMO_CODES.get(daily["weather_code"][i], "🌡️ Mausam"),
                }
                for i in range(min(3, len(daily.get("time", []))))
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }


# ─── OPENWEATHERMAP (FALLBACK) ───
@async_retry(max_retries=2, delay=1.5)
async def _fetch_openweather(city: str) -> Optional[Dict[str, Any]]:
    """Fetch weather from OpenWeatherMap (requires API key)."""
    if not OPENWEATHER_API_KEY:
        return None

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        return {
            "source": "OpenWeatherMap",
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", ""),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "pressure": data.get("main", {}).get("pressure"),
            "condition": data.get("weather", [{}])[0].get("description", "Maasam"),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ─── MAIN HANDLER ───
@router.get("/{city}")
async def get_weather(city: str, lang: str = "hi"):
    """
    🌤️ Get weather for any city.

    - Cached for 5 minutes
    - Auto-fallback Open-Meteo → OpenWeatherMap
    - 3-day forecast included

    Example: /weather/Delhi?lang=hi
    """
    logger.info(f"🌤️ Weather request: {city}, lang={lang}")

    # Check cache
    cached = _get_cached(city, lang)
    if cached:
        logger.info(f"🌤️ Cache hit for {city}")
        return JSONResponse({"cached": True, "data": cached})

    # Try primary source
    data = await _fetch_openmeteo(city, lang)

    # Fallback
    if not data:
        logger.warning(f"🌤️ Open-Meteo failed for {city}, trying OpenWeatherMap")
        data = await _fetch_openweather(city)

    if not data:
        raise HTTPException(status_code=404, detail=f"❌ Mausam ka data nahi mila: {city}")

    # Cache and return
    _set_cached(city, lang, data)

    return JSONResponse({
        "status": "success",
        "module": "weather",
        "version": "2.0-polished",
        "cached": False,
        "data": data,
    })


@router.get("/")
async def weather_root():
    """Weather module info."""
    return JSONResponse({
        "module": "🌤️ Weather",
        "version": "2.0-polished",
        "sources": ["Open-Meteo (primary)", "OpenWeatherMap (fallback)"],
        "features": ["async", "cached", "retry", "forecast", "multi-source"],
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
    })


# Legacy handler for compatibility
async def handler(request: Request):
    """Legacy handler entry point."""
    city = request.query_params.get("city", "Delhi")
    lang = request.query_params.get("lang", "hi")
    return await get_weather(city, lang)
