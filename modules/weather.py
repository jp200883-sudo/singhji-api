# modules/weather.py — Singh Ji AI Ultra
import os
import requests
from fastapi import APIRouter

# ⬇️ ADD prefix and tags
router = APIRouter(prefix="/api/weather", tags=["Weather"])

API_KEY = os.getenv("OPENWEATHER_API_KEY")

@router.get("/")
async def weather_home():
    """Weather API Home"""
    return {
        "app": "Weather",
        "status": "active",
        "endpoints": ["/current", "/forecast"],
        "message": "Mausham ki jankari!"
    }

@router.get("/current")
async def current_weather(city: str = "Kanpur"):
    """Real-time weather — OpenWeather API"""
    if not API_KEY:
        return {
            "error": "OPENWEATHER_API_KEY not set",
            "mock": True,
            "city": city,
            "temp": 32,
            "condition": "Sunny ☀️",
            "message": "API key missing - showing demo data"
        }
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            "source": "openweather"
        }
    except Exception as e:
        return {"error": str(e), "city": city, "fallback": "mock"}

@router.get("/forecast")
async def forecast(city: str = "Kanpur", days: int = 3):
    """5-day forecast"""
    if not API_KEY:
        return {"error": "Key missing", "mock": True, "message": "Add OPENWEATHER_API_KEY to Render"}
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        # Filter to one per day
        daily = []
        seen = set()
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in seen and len(seen) < days:
                seen.add(date)
                daily.append({
                    "date": date,
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"]
                })
        
        return {"city": city, "forecast": daily, "source": "openweather"}
    except Exception as e:
        return {"error": str(e), "city": city}
