# modules/plant_id/__init__.py — Singh Ji AI Ultra v5.0
# This file = handler.py (Render free tier fix)

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import base64
import os

router = APIRouter()

PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY", "")
PLANT_ID_API_URL = "https://api.plant.id/v2/identify"

@router.get("/health")
def plant_health():
    return {
        "module": "plant_id",
        "status": "✅ OK",
        "api_key_set": bool(PLANT_ID_API_KEY),
        "provider": "Plant.id API v2"
    }

@router.get("/info")
def plant_info():
    return {
        "module": "plant_id",
        "version": "1.0.0",
        "features": [
            "Plant identification from image",
            "Disease detection",
            "Care suggestions",
            "Base64 image upload"
        ],
        "setup": "Set PLANT_ID_API_KEY in Render Environment Variables"
    }

@router.post("/identify")
async def identify_plant(file: UploadFile = File(...)):
    """Identify plant from uploaded image"""
    if not PLANT_ID_API_KEY:
        return {
            "ok": False,
            "error": "PLANT_ID_API_KEY not set",
            "fallback": "Please set PLANT_ID_API_KEY in Render Environment Variables",
            "demo_mode": True,
            "result": {
                "plant_name": "Demo: Tulsi (Holy Basil)",
                "scientific_name": "Ocimum tenuiflorum",
                "confidence": 0.95,
                "description": "Tulsi is a sacred plant in India, known for its medicinal properties.",
                "care": "Water daily, keep in sunlight, sacred to Hindu tradition 🙏"
            }
        }
    
    try:
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        import aiohttp
        payload = {
            "images": [f"data:image/jpeg;base64,{base64_image}"],
            "modifiers": ["crops_fast", "similar_images"],
            "plant_language": "en",
            "plant_details": ["common_names", "url", "wiki_description", "taxonomy", "synonyms"]
        }
        headers = {
            "Content-Type": "application/json",
            "Api-Key": PLANT_ID_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(PLANT_ID_API_URL, json=payload, headers=headers) as resp:
                result = await resp.json()
                return {
                    "ok": True,
                    "plant_id_result": result,
                    "image_name": file.filename
                }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "fallback": "Error during identification. Please try again."
        }

@router.post("/identify-base64")
async def identify_plant_base64(image_base64: str):
    """Identify plant from base64 string"""
    if not PLANT_ID_API_KEY:
        return {
            "ok": False,
            "error": "PLANT_ID_API_KEY not set",
            "demo_mode": True
        }
    
    try:
        import aiohttp
        payload = {
            "images": [image_base64 if image_base64.startswith("data:") else f"data:image/jpeg;base64,{image_base64}"],
            "modifiers": ["crops_fast"],
            "plant_details": ["common_names", "wiki_description"]
        }
        headers = {
            "Content-Type": "application/json",
            "Api-Key": PLANT_ID_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(PLANT_ID_API_URL, json=payload, headers=headers) as resp:
                return await resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
