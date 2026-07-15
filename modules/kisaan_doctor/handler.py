import os
import requests
from fastapi import APIRouter, Request

router = APIRouter()

PLANT_ID_API = os.getenv("PLANT_ID_API", "")
PLANT_ID_URL = os.getenv("PLANT_ID_URL", "https://api.plant.id/v2/health_assessment")

@router.post("/diagnose")
async def diagnose_plant(request: Request):
    data = await request.json()
    photo_url = data.get("photo_url")
    user_lang = data.get("lang", "hi")

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
        result = response.json()

        if not result.get("health_assessment", {}).get("is_healthy", True):
            diseases = result["health_assessment"].get("diseases", [])
            if diseases:
                top = diseases[0]
                treatment = top.get("disease_details", {}).get("treatment", {})
                return {
                    "healthy": False,
                    "disease_name": top.get("name"),
                    "confidence": round(top.get("probability", 0) * 100, 1),
                    "treatment_chemical": treatment.get("chemical", []),
                    "treatment_biological": treatment.get("biological", []),
                    "treatment_prevention": treatment.get("prevention", [])
                }

        return {"healthy": True, "message": "Paudha swasth hai"}

    except Exception as e:
        return {"error": str(e)}
