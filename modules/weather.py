from fastapi import APIRouter
import requests
import os

router = APIRouter()

@router.get("/{city}")
def weather_city(city: str):
    # ✅ SAHI variable name
    WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not WEATHER_KEY:
        return {"error": "API key missing", "source": "config_error", "expected": "OPENWEATHER_API_KEY"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
    
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        
        if res.status_code != 200:
            return {"error": data.get("message", "Unknown error"), "source": "api_error"}
        
        return {
            "city": city,
            "temp": f"{data['main']['temp']}°C",
            "condition": data["weather"][0]["main"],
            "humidity": f"{data['main']['humidity']}%",
            "source": "openweathermap"
        }
    except Exception as e:
        return {"error": str(e), "source": "exception"}
