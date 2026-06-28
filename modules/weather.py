from fastapi import APIRouter
import os
import requests

router = APIRouter()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

@router.get("/")
def weather_home():
    return {
        "module": "weather",
        "status": "✅ LIVE",
        "api_configured": bool(WEATHER_API_KEY),
        "message": "Weather module ready — Mausam ka haal bataoonga!"
    }

@router.get("/{city}")
def get_weather(city: str):
    if not WEATHER_API_KEY:
        return {
            "ok": False,
            "error": "OPENWEATHER_API_KEY not set",
            "message": "Render env mein key daalo!"
        }
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        return {
            "ok": True,
            "city": city,
            "temperature": data.get("main", {}).get("temp", "N/A"),
            "condition": data.get("weather", [{}])[0].get("description", "N/A"),
            "humidity": data.get("main", {}).get("humidity", "N/A"),
            "message": f"{city} ka mausam: {data.get('weather', [{}])[0].get('description', 'N/A')}"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Weather fetch fail — baad mein try karo!"
        }
