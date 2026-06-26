from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def social_home():
    return {
        "module": "social",
        "status": "ok"
    }

@router.post("/post")
def social_post(message: str = ""):
    return {
        "message": message,
        "platforms": ["instagram", "facebook", "twitter", "whatsapp", "telegram"],
        "status": "mock_posted"
    }
