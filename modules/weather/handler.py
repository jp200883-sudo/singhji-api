"""
🌤️ Singh Ji AI Ultra v7.0 — Weather Module
Open-Meteo API (No API Key Required, Free Forever)
"""
import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Weather condition codes mapping (WMO)
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        city = params.get("city", "Delhi").strip()
        lang = params.get("lang", "hi").strip()
        
        # Step 1: Geocoding — City to Lat/Lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language={lang}"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": f"City '{city}' not found",
                "tts": f"शहर {city} नहीं मिला। कृपया सही नाम डालें।"
            })
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        country = location.get("country", "Unknown")
        timezone = location.get("timezone", "auto")
        
        # Step 2: Weather Data
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,"
            f"precipitation_sum,weather_code"
            f"&timezone={timezone}&forecast_days=3"
        )
        
        w_resp = requests.get(weather_url, timeout=10)
        w_data = w_resp.json()
        
        current = w_data.get("current", {})
        daily = w_data.get("daily", {})
        
        weather_code = current.get("weather_code", 0)
        condition = WMO_CODES.get(weather_code, "Unknown")
        
        # Hindi condition mapping
        HINDI_CONDITIONS = {
            "Clear sky": "साफ आसमान",
            "Mainly clear": "मुख्य रूप से साफ",
            "Partly cloudy": "आंशिक रूप से बादल",
            "Overcast": "बादल छाए हुए",
            "Foggy": "धुंध",
            "Light drizzle": "हल्की बूंदाबांदी",
            "Moderate rain": "मध्यम बारिश",
            "Heavy rain": "भारी बारिश",
            "Slight snow": "हल्की बर्फबारी",
            "Thunderstorm": "आंधी-तूफान"
        }
        hindi_condition = HINDI_CONDITIONS.get(condition, condition)
        
        # Build response
        result = {
            "success": True,
            "city": city,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "feels_like_c": current.get("apparent_temperature"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "precipitation_mm": current.get("precipitation"),
                "is_day": current.get("is_day") == 1,
                "condition": condition,
                "condition_hindi": hindi_condition,
                "weather_code": weather_code
            },
            "forecast": [],
            "source": "open-meteo.com (Free, No API Key)"
        }
        
        # Build 3-day forecast
        if daily:
            for i in range(min(3, len(daily.get("time", [])))):
                day_code = daily.get("weather_code", [0])[i]
                result["forecast"].append({
                    "date": daily["time"][i],
                    "temp_max_c": daily.get("temperature_2m_max", [])[i],
                    "temp_min_c": daily.get("temperature_2m_min", [])[i],
                    "precipitation_mm": daily.get("precipitation_sum", [])[i],
                    "condition": WMO_CODES.get(day_code, "Unknown"),
                    "sunrise": daily.get("sunrise", [])[i] if daily.get("sunrise") else None,
                    "sunset": daily.get("sunset", [])[i] if daily.get("sunset") else None
                })
        
        # TTS Message
        temp = result["current"]["temperature_c"]
        tts = f"मौसम अपडेट {city}। तापमान {temp} डिग्री सेल्सियस। {hindi_condition}।"
        if result["forecast"]:
            tts += f" कल अधिकतम तापमान {result['forecast'][0]['temp_max_c']} डिग्री।"
        
        result["tts"] = tts
        
        return JSONResponse(content=result)
        
    except requests.exceptions.Timeout:
        logger.error("Weather API timeout")
        return JSONResponse(status_code=504, content={
            "success": False,
            "error": "Weather API timeout",
            "tts": "मौसम सेवा में देरी हो रही है। कृपया बाद में प्रयास करें।"
        })
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "tts": "मौसम जानकारी में त्रुटि हुई। कृपया पुनः प्रयास करें।"
        })
