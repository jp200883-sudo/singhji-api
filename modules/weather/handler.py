import os
import requests
from flask import Blueprint, request, jsonify

weather_bp = Blueprint('weather', __name__)

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')

@weather_bp.route('/current', methods=['GET'])
def current_weather():
    city = request.args.get('city', '').strip()
    lat = request.args.get('lat', '').strip()
    lon = request.args.get('lon', '').strip()
    lang = request.args.get('lang', 'hi')
    
    if not OPENWEATHER_API_KEY:
        return jsonify({"success": False, "error": "OPENWEATHER_API_KEY not configured", "data": None}), 500
    
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    if lat and lon:
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
    elif city:
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
    else:
        return jsonify({"success": False, "error": "Provide ?city=Delhi OR ?lat=XX&lon=YY", "data": None}), 400
    
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        
        if resp.status_code != 200:
            return jsonify({"success": False, "error": data.get("message", "Weather API error"), "data": None}), resp.status_code
        
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
        return jsonify({"success": True, "error": None, "data": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": None}), 500

@weather_bp.route('/forecast', methods=['GET'])
def forecast():
    city = request.args.get('city', '').strip()
    lat = request.args.get('lat', '').strip()
    lon = request.args.get('lon', '').strip()
    lang = request.args.get('lang', 'hi')
    
    if not OPENWEATHER_API_KEY:
        return jsonify({"success": False, "error": "OPENWEATHER_API_KEY not configured", "data": None}), 500
    
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    
    if lat and lon:
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
    elif city:
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
    else:
        return jsonify({"success": False, "error": "Provide ?city=Delhi OR ?lat=XX&lon=YY", "data": None}), 400
    
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        
        if resp.status_code != 200:
            return jsonify({"success": False, "error": data.get("message", "Forecast API error"), "data": None}), resp.status_code
        
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
        
        return jsonify({
            "success": True,
            "error": None,
            "data": {"city": data["city"]["name"], "country": data["city"]["country"], "forecast": forecast_days}
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": None}), 500

@weather_bp.route('/air', methods=['GET'])
def air_quality():
    lat = request.args.get('lat', '').strip()
    lon = request.args.get('lon', '').strip()
    
    if not lat or not lon:
        return jsonify({"success": False, "error": "Provide ?lat=XX&lon=YY", "data": None}), 400
    
    if not OPENWEATHER_API_KEY:
        return jsonify({"success": False, "error": "OPENWEATHER_API_KEY not configured", "data": None}), 500
    
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    try:
        resp = requests.get(url, params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}, timeout=10)
        data = resp.json()
        
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        aqi = data["list"][0]["main"]["aqi"]
        
        return jsonify({
            "success": True,
            "error": None,
            "data": {"aqi": aqi, "aqi_label": aqi_labels.get(aqi, "Unknown"), "components": data["list"][0]["components"]}
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": None}), 500
