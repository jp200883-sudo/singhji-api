from fastapi import APIRouter, Response
from gtts import gTTS
import os
import io

router = APIRouter()

@router.get("/")
async def voice_tts_root():
    return {
        "ok": True,
        "module": "voice_tts",
        "status": "✅ LIVE",
        "engine": "gTTS (Google Text-to-Speech)",
        "message": "Voice TTS ready — Bol bhai, suna dunga!"
    }

@router.get("/speak")
async def text_to_speech(text: str = "नमस्ते सिंह जी", lang: str = "hi"):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return Response(
            content=mp3_fp.read(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=singhji_tts.mp3"}
        )
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "gTTS failed — check logs"
        }

@router.get("/languages")
async def tts_languages():
    return {
        "ok": True,
        "languages": {
            "hi": "Hindi",
            "en": "English",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi"
        },
        "message": "10 languages supported!"
    }
