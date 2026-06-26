# modules/voice/__init__.py — Singh Ji AI Ultra v5.0
# 🗣️ Voice / TTS

from fastapi import APIRouter
from config.settings import settings 

router = APIRouter()

@router.get("/health")
def voice_health():
    return {
        "module": "voice",
        "status": "✅ OK",
        "tts_enabled": settings.F5_TTS_ENABLED,
        "sample_set": bool(settings.JP_SINGH_SAMPLE)
    }

@router.get("/status")
def voice_status():
    """Voice system status"""
    return {
        "ok": True,
        "features": {
            "tts": settings.F5_TTS_ENABLED,
            "custom_voice": bool(settings.JP_SINGH_SAMPLE),
            "languages": ["hi", "en", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa"]
        },
        "note": "F5-TTS integration coming in v5.1"
    }

@router.get("/speak")
def speak(text: str = "नमस्ते, मैं सिंह जी एआई हूँ", lang: str = "hi"):
    """Text to Speech"""
    return {
        "ok": True,
        "text": text,
        "language": lang,
        "voice": "JP Singh (Demo)" if settings.JP_SINGH_SAMPLE else "Default",
        "audio_url": None,
        "note": "Full TTS in v5.1 — using browser TTS for now",
        "browser_tts": f"Use: speechSynthesis.speak(new SpeechSynthesisUtterance('{text}'))"
    }

@router.get("/jp_sample")
def jp_sample_info():
    """JP Singh voice sample info"""
    if not settings.JP_SINGH_SAMPLE:
        return {
            "ok": False,
            "error": "JP_SINGH_SAMPLE not set",
            "setup": "Set JP_SINGH_SAMPLE env var to audio file URL"
        }

    return {
        "ok": True,
        "sample_url": settings.JP_SINGH_SAMPLE[:50] + "...",
        "status": "Ready for voice cloning",
        "note": "F5-TTS will clone JP Singh's voice"
    }
