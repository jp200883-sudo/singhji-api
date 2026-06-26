from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def voice_home():
    return {
        "module": "voice",
        "status": "ok",
        "f5_tts_enabled": settings.F5_TTS_ENABLED,
        "sample": settings.JP_SINGH_SAMPLE
    }

@router.post("/speak")
def voice_speak(text: str = ""):
    return {
        "text": text,
        "voice": "JP Singh Clone",
        "status": "mock_tts",
        "message": f"Speaking: {text}"
    }
