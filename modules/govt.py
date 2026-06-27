from fastapi import APIRouter

router = APIRouter()

@router.get("/schemes")
async def govt_schemes():
    return {
        "schemes": [
            {"name": "PM Kisan", "url": "https://pmkisan.gov.in"},
            {"name": "Ayushman Bharat", "url": "https://abha.abdm.gov.in"}
        ]
    }

@router.get("/")
async def govt_root():
    return {"status": "govt module active"}
