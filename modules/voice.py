from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def voice_home():
    return {
        "module": "voice",
        "status": "ok"
    }

@router.post("/speak")
def voice_speak(text: str = ""):
    return {
        "text": text,
        "status": "mock_spoken",
        "message": f"Speaking: {text}"
    }
