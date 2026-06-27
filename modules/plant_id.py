from fastapi import APIRouter
import requests
import os
import base64

router = APIRouter()

@router.get("/")
def plant_home():
    return {"module": "plant_id", "status": "ok"}

@router.post("/identify")
def identify_plant(image_data: dict):
    PLANT_KEY = os.getenv("PLANT_ID_API")
    PLANT_URL = os.getenv("PLANT_ID_URL", "https://api.plant.id/v2/identify")
    
    if not PLANT_KEY:
        return {"error": "API key missing", "source": "config_error"}
    
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "api_key": PLANT_KEY,
            "images": [image_data.get("image", "")],
            "modifiers": ["similar_images"],
            "plant_details": ["common_names", "url", "wiki_description", "taxonomy"]
        }
        
        res = requests.post(PLANT_URL, json=data, headers=headers, timeout=30)
        result = res.json()
        
        if res.status_code != 200:
            return {"error": result.get("message", "Unknown error"), "source": "api_error"}
        
        return {
            "plant": result.get("suggestions", [{}])[0].get("plant_name", "Unknown"),
            "confidence": result.get("suggestions", [{}])[0].get("probability", 0),
            "details": result.get("suggestions", [{}])[0].get("plant_details", {}),
            "source": "plant.id"
        }
    except Exception as e:
        return {"error": str(e), "source": "exception"}
