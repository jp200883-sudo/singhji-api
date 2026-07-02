"""
🌤️ Singh Ji AI Ultra v7.0 — Weather Module
OpenWeatherMap (your key) → Open-Meteo (free fallback)
"""
import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    95: "Thunderstorm", 96: "Thunderstorm with hail"
}

HINDI_CONDITIONS = {
    "Clear sky": "साफ आसमान", "Mainly clear": "मुख्य रूप से साफ",
    "Partly cloudy": "आंशिक बादल", "Overcast": "बादल छाए",
    "Foggy": "धुंध", "Light drizzle": "हल्की बूंदाबांदी",
    "Moderate rain": "मध्यम बारिश", "Heavy rain": "भारी बारिश",
    "Slight snow": "हल्की बर्फबारी", "Thunderstorm": "आंधी-तूफान"
}

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        city = params.get("city", "Delhi").strip()
        lang = params.get("lang", "hi").strip()
        
        weather_key = os.getenv("OPENWEATHER_API_KEY")
        result = None
        
        # Try 1: OpenWeatherMap (your key)
        if weather_key:
            try:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={weather_key}"
                geo_resp = requests.get(geo_url, timeout=10)
                geo_data = geo_resp.json()
                
                if geo_data and len(geo_data) > 0:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]
                    country = geo_data[0].get("country", "Unknown")
                    
                    w_url = (
                        f"https://api.openweathermap.org/data/2.5/weather?"
                        f"lat={lat}&lon={lon}&appid={weather_key}&units=metric"
                    )
                    w_resp = requests.get(w_url, timeout=10)
                    w_data = w_resp.json()
                    
                    if w_resp.status_code == 200:
                        condition = w_data["weather"][0]["main"]
                        result = {
                            "success": True,
                            "city": city,
                            "country": country,
                            "current": {
                                "temperature_c": w_data["main"]["temp"],
                                "feels_like_c": w_data["main"]["feels_like"],
                                "humidity_percent": w_data["main"]["humidity"],
                                "wind_speed_kmh": round(w_data["wind"]["speed"] * 3.6, 1),
                                "condition": condition,
                                "condition_hindi": HINDI_CONDITIONS.get(condition, condition),
                                "pressure": w_data["main"]["pressure"],
                                "visibility": w_data.get("visibility", 0)
                            },
                            "source": "openweathermap.org"
                        }
            except Exception as e:
                logger.error(f"OpenWeather failed: {e}")
        
        # Try 2: Open-Meteo (free, no key)
        if not result:
            try:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
                geo_resp = requests.get(geo_url, timeout=10)
                geo_data = geo_resp.json()
                
                if geo_data.get("results"):
                    loc = geo_data["results"][0]
                    lat, lon = loc["latitude"], loc["longitude"]
                    
                    w_url = (
                        f"https://api.open-meteo.com/v1/forecast?"
                        f"latitude={lat}&longitude={lon}"
                        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
                        f"&timezone=auto"
                    )
                    w_resp = requests.get(w_url, timeout=10)
                    w_data = w_resp.json()
                    
                    current = w_data.get("current", {})
                    code = current.get("weather_code", 0)
                    condition = WMO_CODES.get(code, "Unknown")
                    
                    result = {
                        "success": True,
                        "city": city,
                        "country": loc.get("country", "Unknown"),
                        "current": {
                            "temperature_c": current.get("temperature_2m"),
                            "feels_like_c": None,
                            "humidity_percent": current.get("relative_humidity_2m"),
                            "wind_speed_kmh": current.get("wind_speed_10m"),
                            "condition": condition,
                            "condition_hindi": HINDI_CONDITIONS.get(condition, condition),
                            "pressure": None,
                            "visibility": None
                        },
                        "source": "open-meteo.com (fallback)"
                    }
            except Exception as e:
                logger.error(f"Open-Meteo failed: {e}")
        
        if not result:
            return JSONResponse(status_code=503, content={
                "success": False,
                "error": "All weather APIs failed",
                "tts": "मौसम सेवा उपलब्ध नहीं।"
            })
        
        temp = result["current"]["temperature_c"]
        hindi = result["current"]["condition_hindi"]
        tts = f"मौसम अपडेट {city}। तापमान {temp} डिग्री सेल्सियस। {hindi}।"
        
        result["tts"] = tts
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "tts": "मौसम जानकारी में त्रुटि।"
        })
