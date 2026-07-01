import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            lat = params.get('lat', '').strip()
            lon = params.get('lon', '').strip()
            city = params.get('city', '').strip()
            emergency_type = params.get('type', '').strip()
        else:
            body = await request.json()
            lat = str(body.get('lat', '')).strip()
            lon = str(body.get('lon', '')).strip()
            city = body.get('city', '').strip()
            emergency_type = body.get('type', '').strip()
        
        # Emergency services data
        emergency_data = {
            "police": "100",
            "ambulance": "108",
            "fire": "101",
            "women_helpline": "1091",
            "child_helpline": "1098",
            "disaster_mgmt": "1078",
            "blood_bank": "1910"
        }
        
        # Nearby hospitals using OpenStreetMap (free)
        hospitals = []
        if lat and lon:
            try:
                overpass_url = "https://overpass-api.de/api/interpreter"
                query = f"""
                [out:json];
                node["amenity"="hospital"](around:5000,{lat},{lon});
                out body 5;
                """
                resp = requests.post(overpass_url, data={"data": query}, timeout=10)
                data = resp.json()
                for elem in data.get('elements', [])[:5]:
                    hospitals.append({
                        "name": elem.get('tags', {}).get('name', 'Unknown Hospital'),
                        "lat": elem.get('lat'),
                        "lon": elem.get('lon'),
                        "phone": elem.get('tags', {}).get('phone', 'N/A')
                    })
            except Exception as e:
                logger.error(f"Hospital fetch failed: {e}")
        
        # Nearby police stations
        police_stations = []
        if lat and lon:
            try:
                overpass_url = "https://overpass-api.de/api/interpreter"
                query = f"""
                [out:json];
                node["amenity"="police"](around:5000,{lat},{lon});
                out body 5;
                """
                resp = requests.post(overpass_url, data={"data": query}, timeout=10)
                data = resp.json()
                for elem in data.get('elements', [])[:5]:
                    police_stations.append({
                        "name": elem.get('tags', {}).get('name', 'Unknown Police Station'),
                        "lat": elem.get('lat'),
                        "lon": elem.get('lon'),
                        "phone": elem.get('tags', {}).get('phone', 'N/A')
                    })
            except Exception as e:
                logger.error(f"Police fetch failed: {e}")
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "emergency_numbers": emergency_data,
                "location": {"city": city or "Unknown", "lat": lat, "lon": lon},
                "nearby_hospitals": hospitals,
                "nearby_police": police_stations,
                "message": "Emergency services data fetched successfully"
            }
        })
        
    except Exception as e:
        logger.error(f"Emergency crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
