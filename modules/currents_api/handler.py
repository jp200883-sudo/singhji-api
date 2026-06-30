"""Singh Ji AI Ultra v7.0 - Currents Api Module"""

import requests, os
API_KEY = os.getenv("CURRENTS_API_KEY", "")
def handler(data=None):
    try:
        url = f"https://api.currentsapi.services/v1/latest-news?apiKey={API_KEY}"
        r = requests.get(url, timeout=10)
        return {"module": "currents_api", "status": "success", "data": r.json().get("news", [])[:5]}
    except Exception as e:
        return {"module": "currents_api", "status": "error", "error": str(e)}
