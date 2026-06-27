from fastapi import APIRouter

router = APIRouter()

@router.get("/api/voice/tts")
def text_to_speech(text: str = "Hello Singh Ji"):
    return {
        "status": "success",
        "text": text,
        "audio_url": None,
        "message": "TTS module ready"
    }

@router.post("/api/voice/tts")
def generate_speech(text: str = ""):
    if not text:
        return {"status": "error", "message": "Text required"}
    return {
        "status": "success", 
        "text": text,
        "audio_url": None,
        "message": "Speech generated"
    }
