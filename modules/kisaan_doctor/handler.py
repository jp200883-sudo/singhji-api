import os
import requests
from fastapi import APIRouter, Request

router = APIRouter()

PLANT_ID_API = os.getenv("PLANT_ID_API", "")
PLANT_ID_URL = "https://api.plant.id/v2/health_assessment"

@router.post("/diagnose")
async def diagnose_plant(request: Request):
    data = await request.json()
    photo_url = data.get("photo_url")

    if not photo_url:
        return {"error": "photo_url zaroori hai"}

    try:
        response = requests.post(
            PLANT_ID_URL,
            headers={"Api-Key": PLANT_ID_API, "Content-Type": "application/json"},
            json={
                "images": [photo_url],
                "modifiers": ["crops_fast", "similar_images"],
                "disease_details": ["cause", "common_names", "treatment"]
            },
            timeout=15
        )
        # DEBUG MODE — asli response dekhne ke liye
        return {
            "debug_status_code": response.status_code,
            "debug_url_used": PLANT_ID_URL,
            "debug_key_present": bool(PLANT_ID_API),
            "debug_response_text": response.text[:800]
        }

    except Exception as e:
        return {"error": str(e)}
