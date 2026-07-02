"""
🌤️ Singh Ji AI Ultra v7.0 — Weather Module
Primary: Open-Meteo (Free, No API Key)
Fallback: OpenWeatherMap (if key works)
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
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

# Open-Meteo condition names → Hindi
HINDI_CONDITIONS = {
    "Clear sky": "साफ आसमान",
    "Mainly clear": "मुख्य रूप से साफ",
    "Partly cloudy": "आंशिक बादल",
    "Overcast": "बादल छाए हुए",
    "Foggy": "धुंध",
    "Depositing rime fog": "पाला जमी धुंध",
    "Light drizzle": "हल्की बूंदाबांदी",
    "Moderate drizzle": "मध्यम बूंदाबांदी",
    "Dense drizzle": "भारी बूंदाबांदी",
    "Light freezing drizzle": "हल्की जमने वाली बूंदाबांदी",
    "Dense freezing drizzle": "भारी जमने वाली बूंदाबांदी",
    "Slight rain": "हल्की बारिश",
    "Moderate rain": "मध्यम बारिश",
    "Heavy rain": "भारी बारिश",
    "Light freezing rain": "हल्की जमने वाली बारिश",
    "Heavy freezing rain": "भारी जमने वाली बारिश",
    "Slight snow": "हल्की बर्फबारी",
    "Moderate snow": "मध्यम बर्फबारी",
    "Heavy snow": "भारी बर्फबारी",
    "Snow grains": "बर्फ के कण",
    "Slight rain showers": "हल्की बौछारें",
    "Moderate rain showers": "मध्यम बौछारें",
    "Violent rain showers": "तीव्र बौछारें",
    "Slight snow showers": "हल्की बर्फ़ की बौछारें",
    "Heavy snow showers": "भारी बर्फ़ की बौछारें",
    "Thunderstorm": "आंधी-तूफान",
    "Thunderstorm with slight hail": "ओलों के साथ आंधी",
    "Thunderstorm with heavy hail": "भारी ओलों के साथ आंधी",

    # OpenWeatherMap condition names → Hindi (fallback source ke liye)
    "Clear": "साफ आसमान",
    "Clouds": "बादल छाए हुए",
    "Rain": "बारिश",
    "Drizzle": "बूंदाबांदी",
    "Snow": "बर्फबारी",
    "Mist": "धुंध",
    "Fog": "कोहरा",
    "Haze": "धुंधलापन",
    "Smoke": "धुआं",
    "Dust": "धूल",
    "Sand": "रेत",
    "Ash": "राख",
    "Squall": "तेज़ आंधी",
    "Tornado": "बवंडर"
}

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        city = params.get("city", "Delhi").strip()
        lang = params.get("lang", "hi").strip()
        
        # ============================================================
        # PRIMARY: Open-Meteo (Free, No API Key, Reliable)
        # ============================================================
        try:
            # Step 1: Geocoding
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
            
            # Step 2: Weather Data (Rich)
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
                f"is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m,"
                f"surface_pressure,cloud_cover,visibility"
                f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,"
                f"precipitation_sum,weather_code,precipitation_probability_max"
                f"&hourly=temperature_2m,weather_code,precipitation_probability"
                f"&timezone={timezone}&forecast_days=7"
            )
            
            w_resp = requests.get(weather_url, timeout=15)
            w_data = w_resp.json()
            
            current = w_data.get("current", {})
            daily = w_data.get("daily", {})
            hourly = w_data.get("hourly", {})
            
            weather_code = current.get("weather_code", 0)
            condition = WMO_CODES.get(weather_code, "Unknown")
            hindi_condition = HINDI_CONDITIONS.get(condition, condition)
            
            # Build 7-day forecast
            forecast = []
            if daily:
                for i in range(min(7, len(daily.get("time", [])))):
                    day_code = daily.get("weather_code", [0])[i]
                    day_condition = WMO_CODES.get(day_code, "Unknown")
                    forecast.append({
                        "date": daily["time"][i],
                        "temp_max_c": daily.get("temperature_2m_max", [])[i],
                        "temp_min_c": daily.get("temperature_2m_min", [])[i],
                        "precipitation_mm": daily.get("precipitation_sum", [])[i],
                        "precipitation_chance": daily.get("precipitation_probability_max", [])[i],
                        "condition": day_condition,
                        "condition_hindi": HINDI_CONDITIONS.get(day_condition, day_condition),
                        "sunrise": daily.get("sunrise", [])[i] if daily.get("sunrise") else None,
                        "sunset": daily.get("sunset", [])[i] if daily.get("sunset") else None
                    })
            
            # Hourly forecast (next 12 hours)
            hourly_forecast = []
            if hourly:
                for i in range(min(12, len(hourly.get("time", [])))):
                    hr_code = hourly.get("weather_code", [0])[i]
                    hourly_forecast.append({
                        "time": hourly["time"][i],
                        "temp_c": hourly.get("temperature_2m", [])[i],
                        "condition": WMO_CODES.get(hr_code, "Unknown"),
                        "precipitation_chance": hourly.get("precipitation_probability", [])[i]
                    })
            
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
                    "pressure_hpa": current.get("surface_pressure"),
                    "cloud_cover_percent": current.get("cloud_cover"),
                    "visibility_km": current.get("visibility"),
                    "is_day": current.get("is_day") == 1,
                    "condition": condition,
                    "condition_hindi": hindi_condition,
                    "weather_code": weather_code
                },
                "forecast": forecast,
                "hourly": hourly_forecast,
                "source": "open-meteo.com (Free, No API Key)",
                "note": "OpenWeatherMap key not working — using reliable Open-Meteo"
            }
            
            # TTS
            temp = result["current"]["temperature_c"]
            tts = f"मौसम अपडेट {city}। तापमान {temp} डिग्री सेल्सियस। {hindi_condition}।"
            if forecast:
                tts += f" आज अधिकतम {forecast[0]['temp_max_c']} डिग्री, न्यूनतम {forecast[0]['temp_min_c']} डिग्री।"
                if forecast[0].get("precipitation_chance", 0) > 50:
                    tts += f" बारिश की संभावना {forecast[0]['precipitation_chance']} प्रतिशत।"
            
            result["tts"] = tts
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Open-Meteo failed: {e}")
        
        # ============================================================
        # FALLBACK: OpenWeatherMap (if key ever works)
        # ============================================================
        weather_key = os.getenv("OPENWEATHER_API_KEY")
        if weather_key:
            try:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={weather_key}"
                geo_resp = requests.get(geo_url, timeout=10)
                geo_data = geo_resp.json()
                
                if geo_data and len(geo_data) > 0:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]
                    
                    w_url = (
                        f"https://api.openweathermap.org/data/2.5/weather?"
                        f"lat={lat}&lon={lon}&appid={weather_key}&units=metric"
                    )
                    w_resp = requests.get(w_url, timeout=10)
                    w_data = w_resp.json()
                    
                    if w_resp.status_code == 200:
                        condition = w_data["weather"][0]["main"]
                        hindi_condition = HINDI_CONDITIONS.get(condition, condition)
                        temp = w_data["main"]["temp"]
                        return JSONResponse(content={
                            "success": True,
                            "city": city,
                            "current": {
                                "temperature_c": temp,
                                "feels_like_c": w_data["main"]["feels_like"],
                                "humidity_percent": w_data["main"]["humidity"],
                                "wind_speed_kmh": round(w_data["wind"]["speed"] * 3.6, 1),
                                "condition": condition,
                                "condition_hindi": hindi_condition,
                                "pressure": w_data["main"].get("pressure"),
                                "visibility": w_data.get("visibility")
                            },
                            "source": "openweathermap.org",
                            "tts": f"मौसम अपडेट {city}। तापमान {temp} डिग्री सेल्सियस। {hindi_condition}।"
                        })
            except Exception as e:
                logger.error(f"OpenWeather fallback failed: {e}")
        
        # All failed
        return JSONResponse(status_code=503, content={
            "success": False,
            "error": "All weather services unavailable",
            "tts": "मौसम सेवा उपलब्ध नहीं। कृपया बाद में प्रयास करें।"
        })
        
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "tts": "मौसम जानकारी में त्रुटि हुई।"
        })
