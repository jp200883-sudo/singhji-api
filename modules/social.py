from fastapi import APIRouter
from core.config import settings

router = APIRouter()
@router.get("/")
def social_home():
    return {
        "module": "social",
        "status": "ok",
        "platforms": settings.SOCIAL_PLATFORMS
    }
@router.get("/platforms")
def social_platforms():
        "platforms": ["instagram", "facebook", "twitter", "whatsapp", "telegram"],
        "status": "active"
