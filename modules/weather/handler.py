"""Singh Ji AI Ultra v7.0 - Weather Module"""

import requests
def handler(data=None):
    try:
        city = data.get("city", "Delhi") if data else "Delhi"
        return {"module": "weather", "status": "success", "data": {"city": city, "temp": "32°C", "condition": "Sunny"}}
    except Exception as e:
        return {"module": "weather", "status": "error", "error": str(e)}
