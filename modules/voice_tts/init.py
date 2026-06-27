from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def voice_tts_root():
    return {"status": "voice_tts module active"}

@router.post("/speak")
async def voice_speak(text: str, lang: str = "hi"):
    return {
        "text": text,
        "lang": lang,
        "audio_url": f"https://singhji-api.onrender.com/api/voice_tts/audio?text={text}&lang={lang}"
    }
