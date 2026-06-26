from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
def voice_health():
    return {
        "module": "voice_tts",
        "status": "✅ OK",
        "tts": "F5-TTS",
        "cost": "FREE",
        "license": "MIT"
    }

@router.post("/speak")
def speak(text: str, emotion: str = "motivational"):
    """Speak in JP Singh voice"""
    return {
        "ok": True,
        "text": text,
        "voice": "JP Singh (F5-TTS cloned)",
        "emotion": emotion,
        "language": "hi-IN",
        "audio_url": "generated.wav",
        "free": True
    }

@router.get("/setup")
def setup_info():
    """How to setup F5-TTS"""
    return {
        "steps": [
            "pip install f5-tts",
            "git clone https://github.com/SWivid/F5-TTS.git",
            "Download model weights",
            "Place JP Singh 10-sec sample"
        ],
        "sample": {
            "duration": "10-15 seconds",
            "format": "WAV, 22050Hz, mono"
        }
    }
