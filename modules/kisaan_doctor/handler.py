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
                "modifiers": ["health_only", "similar_images"],
                "disease_details": ["cause", "common_names", "treatment"]
            },
            timeout=15
        )
        result = response.json()

        if response.status_code != 200:
            return {"error": f"Plant.id error: {result.get('error') or response.text[:200]}"}

        health = result.get("health_assessment", {})
        if not health.get("is_healthy", True):
            diseases = health.get("diseases", [])
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
