import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')

async def handler(request: Request):
    method = request.method
    
    if method == "GET":
        params = dict(request.query_params)
        city = params.get('city', '').strip()
        lat = params.get('lat', '').strip()
        lon = params.get('lon', '').strip()
        lang = params.get('lang', 'hi')
        endpoint = params.get('endpoint', 'current')
    else:
        body = await request.json()
        city = body.get('city', '').strip()
        lat = str(body.get('lat', '')).strip()
        lon = str(body.get('lon', '')).strip()
        lang = body.get('lang', 'hi')
        endpoint = body.get('endpoint', 'current')
    
    if not OPENWEATHER_API_KEY:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "OPENWEATHER_API_KEY not configured", "data": None}
        )
    
    if endpoint == 'air':
        if not lat or not lon:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Provide lat & lon for air quality", "data": None}
            )
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        try:
            resp = requests.get(url, params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}, timeout=10)
            data = resp.json()
            aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            aqi = data["list"][0]["main"]["aqi"]
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {"aqi": aqi, "aqi_label": aqi_labels.get(aqi, "Unknown"), "components": data["list"][0]["components"]}
            })
        except Exception as e:
            return JSONResponse(status_code=500, content={"success": False, "error": str(e), "data": None})
    
    elif endpoint == 'forecast':
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        if lat and lon:
            params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
        elif city:
            params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
        else:
            return JSONResponse(status_code=400, content={"success": False, "error": "Provide city OR lat+lon", "data": None})
        
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            data = resp.json()
            if resp.status_code != 200:
                return JSONResponse(status_code=resp.status_code, content={"success": False, "error": data.get("message", "Forecast API error"), "data": None})
            
            from collections import defaultdict
            daily = defaultdict(list)
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                daily[date].append(item)
            
            forecast_days = []
            for date, items in list(daily.items())[:5]:
                temps = [i["main"]["temp"] for i in items]
                forecast_days.append({
                    "date": date,
                    "temp_min": min(temps),
                    "temp_max": max(temps),
                    "humidity_avg": round(sum(i["main"]["humidity"] for i in items) / len(items)),
                    "weather_main": items[0]["weather"][0]["main"],
                    "weather_desc": items[0]["weather"][0]["description"],
                    "icon": f"https://openweathermap.org/img/wn/{items[0]['weather'][0]['icon']}@2x.png",
                    "entries_count": len(items)
                })
            
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {"city": data["city"]["name"], "country": data["city"]["country"], "forecast": forecast_days}
            })
        except Exception as e:
            return JSONResponse(status_code=500, content={"success": False, "error": str(e), "data": None})
    
    else:
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        if lat and lon:
            params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
        elif city:
            params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
        else:
            return JSONResponse(status_code=400, content={"success": False, "error": "Provide city OR lat+lon", "data": None})
        
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            data = resp.json()
            if resp.status_code != 200:
                return JSONResponse(status_code=resp.status_code, content={"success": False, "error": data.get("message", "Weather API error"), "data": None})
            
            result = {
                "success": True,
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": {
                    "current": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "min": data["main"]["temp_min"],
                    "max": data["main"]["temp_max"]
                },
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind": {"speed": data["wind"]["speed"], "deg": data["wind"].get("deg", 0)},
                "visibility": data.get("visibility", 0) / 1000,
                "weather": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
                },
                "sunrise": data["sys"].get("sunrise"),
                "sunset": data["sys"].get("sunset"),
                "timestamp": data.get("dt")
            }
            return JSONResponse(content={"success": True, "error": None, "data": result})
        except Exception as e:
            return JSONResponse(status_code=500, content={"success": False, "error": str(e), "data": None})
