from fastapi import Request
from gtts import gTTS
import os
import base64
import tempfile
from datetime import datetime

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "voice_tts", "languages": ["hi", "en", "ta", "te", "bn", "mr", "gu"]}
    if method == "POST":
        try:
            b = await request.json()
            text = b.get("text", "")
            lang = b.get("lang", "hi")
            if not text: return {"status": "error", "message": "No text"}
            tts = gTTS(text=text, lang=lang, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                with open(fp.name, "rb") as f: audio = base64.b64encode(f.read()).decode()
                os.unlink(fp.name)
            return {"status": "success", "audio_base64": audio, "lang": lang, "text": text, "format": "mp3", "timestamp": datetime.now().isoformat()}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}
