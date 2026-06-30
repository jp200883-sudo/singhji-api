from fastapi import Request
import os
import httpx
from datetime import datetime

API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        query = dict(request.query_params)
        return await get_weather(query.get("city", "Delhi"))
    if method == "POST":
        try:
            body = await request.json()
            return await get_weather(body.get("city", "Delhi"))
        except: return await get_weather("Delhi")
    return {"status": "error", "message": "Method not allowed"}

async def get_weather(city):
    if not API_KEY:
        return {"status": "success", "mock": True, "city": city, "temp": 32, "feels_like": 35, "humidity": 65, "description": "Sunny ☀️", "wind_speed": 12, "message": "🦁 Demo mode", "timestamp": datetime.now().isoformat()}
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=hi", timeout=10)
            d = r.json()
            if d.get("cod") != 200: return {"status": "error", "message": d.get("message", "Not found")}
            return {"status": "success", "city": d["name"], "country": d["sys"]["country"], "temp": d["main"]["temp"], "feels_like": d["main"]["feels_like"], "humidity": d["main"]["humidity"], "pressure": d["main"]["pressure"], "wind_speed": d["wind"]["speed"], "description": d["weather"][0]["description"], "icon": f"https://openweathermap.org/img/wn/{d['weather'][0]['icon']}@2x.png", "timestamp": datetime.now().isoformat()}
    except Exception as e: return {"status": "error", "error": str(e), "city": city}
