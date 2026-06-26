from fastapi import APIRouter
from config.settings import settings

router = APIRouter()

@router.get("/")
def emergency_home():
    return {
        "module": "emergency",
        "status": "ok",
        "contacts": {
            "police": settings.POLICE,
            "ambulance": settings.AMBULANCE,
            "fire": settings.FIRE,
            "women_helpline": settings.WOMEN_HELPLINE,
            "child_helpline": settings.CHILD_HELPLINE
        }
    }

@router.get("/contacts")
def emergency_contacts():
    return {
        "emergency_numbers": {
            "police": "100",
            "ambulance": "108",
            "fire": "101",
            "women_helpline": "1091",
            "child_helpline": "1098"
        }
    }
