from fastapi import APIRouter
import requests
import os

router = APIRouter()
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

@router.get("/")
def weather_home():
    return {"module": "weather", "status": "ok"}

@router.get("/{city}")
def weather_city(city: str):
    if not WEATHER_KEY:
        return {"error": "API key missing", "source": "config_error"}
    
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
