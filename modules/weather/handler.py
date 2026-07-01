# weather/handler.py
import os
import json
import requests
import time
from typing import Dict, Any, Optional

# ========== CONFIG ==========
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ========== WEATHER MODULE ==========
class WeatherModule:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """Get current weather by city name"""
        if not self.api_key:
            return self._mock_weather(city)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                "success": True,
                "source": "OpenWeather",
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0) / 1000,
                "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ OpenWeather failed: {str(e)}")
            return self._mock_weather(city)
    
    def get_forecast(self, city: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """Get 5-day forecast by city name"""
        if not self.api_key:
            return self._mock_forecast(city, days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            # Group by day (API returns 3-hour intervals)
            daily = {}
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily:
                    daily[date] = {
                        "temps": [],
                        "weather": item["weather"][0]["main"],
                        "desc": item["weather"][0]["description"],
                        "icon": item["weather"][0]["icon"]
                    }
                daily[date]["temps"].append(item["main"]["temp"])
            
            # Build forecast list
            forecast_list = []
            for date, info in list(daily.items())[:days]:
                forecast_list.append({
                    "date": date,
                    "temp_avg": round(sum(info["temps"]) / len(info["temps"]), 1),
                    "temp_min": round(min(info["temps"]), 1),
                    "temp_max": round(max(info["temps"]), 1),
                    "weather": info["weather"],
                    "description": info["desc"],
                    "icon": f"https://openweathermap.org/img/wn/{info['icon']}@2x.png"
                })
            
            return {
                "success": True,
                "source": "OpenWeather",
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "forecast": forecast_list,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Forecast failed: {str(e)}")
            return self._mock_forecast(city, days)
    
    def get_by_coords(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get weather by GPS coordinates"""
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key & no coords fallback",
                "message": "API key missing"
            }
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units
            }
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                "success": True,
                "source": "OpenWeather",
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch weather by coordinates"
            }
    
    def _mock_weather(self, city: str) -> Dict[str, Any]:
        """Fallback mock data when API fails"""
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "city": city,
            "country": "IN",
            "temperature": 32.5,
            "feels_like": 35.0,
            "humidity": 65,
            "pressure": 1013,
            "weather": "Haze",
            "description": "haze",
            "wind_speed": 3.5,
            "visibility": 5.0,
            "icon": "https://openweathermap.org/img/wn/50d@2x.png",
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _mock_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """Fallback mock forecast"""
        import datetime
        forecast = []
        base_temp = 30
        for i in range(days):
            date = (datetime.datetime.now() + datetime.timedelta(days=i+1)).strftime("%Y-%m-%d")
            forecast.append({
                "date": date,
                "temp_avg": base_temp + (i % 3),
                "temp_min": base_temp - 2,
                "temp_max": base_temp + 4,
                "weather": "Clear" if i % 2 == 0 else "Clouds",
                "description": "clear sky" if i % 2 == 0 else "scattered clouds",
                "icon": "https://openweathermap.org/img/wn/01d@2x.png" if i % 2 == 0 else "https://openweathermap.org/img/wn/03d@2x.png"
            })
        
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "city": city,
            "country": "IN",
            "forecast": forecast,
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check module health"""
        return {
            "module": "weather",
            "api_key_set": bool(self.api_key),
            "status": "✅ Ready" if self.api_key else "⚠️ Mock Mode"
        }


# ========== RENDER HANDLER ==========
def handler(request):
    """
    Render.com handler for weather module
    GET: /weather?city=Delhi&forecast=true
    POST: {"city": "Mumbai", "type": "current"}
    """
    if request.method == "GET":
        params = request.args if hasattr(request, 'args') else {}
        city = params.get("city", "Delhi")
        forecast = params.get("forecast", "false").lower() == "true"
        units = params.get("units", "metric")
        
        weather = WeatherModule()
        
        if forecast:
            result = weather.get_forecast(city, days=5, units=units)
        else:
            result = weather.get_current(city, units=units)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result, ensure_ascii=False)
        }
    
    elif request.method == "POST":
        try:
            body = json.loads(request.body) if hasattr(request, 'body') else request.json()
            city = body.get("city", "Delhi")
            wtype = body.get("type", "current")
            lat = body.get("lat")
            lon = body.get("lon")
            units = body.get("units", "metric")
            days = body.get("days", 5)
            
            weather = WeatherModule()
            
            if lat and lon:
                result = weather.get_by_coords(lat, lon, units)
            elif wtype == "forecast":
                result = weather.get_forecast(city, days, units)
            else:
                result = weather.get_current(city, units)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result, ensure_ascii=False)
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    
    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method not allowed"})
    }


# ========== LOCAL TEST ==========
if __name__ == "__main__":
    w = WeatherModule()
    print("🦁 SINGH JI AI ULTRA v7.0 — Weather Module")
    print("Health:", w.health_check())
    print("\nCurrent Weather (Delhi):")
    print(json.dumps(w.get_current("Delhi"), indent=2, ensure_ascii=False))
    print("\nForecast (Delhi, 3 days):")
    print(json.dumps(w.get_forecast("Delhi", days=3), indent=2, ensure_ascii=False))
