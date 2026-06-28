# modules/currents_api.py — Singh Ji AI Ultra v5.0
# Currents API — World News (600/day free)

import os
import requests

CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")

def get_world_news(keywords=None, language="en"):
    """World news from Currents API"""
    if not CURRENTS_API_KEY:
        return {"success": False, "error": "API Key not configured"}

    url = "https://api.currentsapi.services/v1/latest-news"
    params = {
        "apiKey": CURRENTS_API_KEY,
        "language": language
    }
    if keywords:
        params["keywords"] = keywords

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") == "ok":
            return {
                "success": True,
                "total": len(data.get("news", [])),
                "articles": data.get("news", [])
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_news(query):
    url = "https://api.currentsapi.services/v1/search"
    params = {
        "apiKey": CURRENTS_API_KEY,
        "keywords": query,
        "language": "en"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            return {"success": True, "articles": data.get("news", [])}
        return {"success": False, "error": data.get("msg")}
    except Exception as e:
        return {"success": False, "error": str(e)}
