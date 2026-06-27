from fastapi import APIRouter

router = APIRouter()

@router.get("/sos")
async def emergency_sos():
    return {
        "police": "100",
        "ambulance": "108",
        "fire": "101",
        "women_helpline": "1091"
    }

@router.get("/")
async def emergency_root():
    return {"status": "emergency module active"}
