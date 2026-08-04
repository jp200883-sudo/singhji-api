# api/ai.py
import os
import base64
import tempfile
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

from core.config import GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY, AVAILABLE_KEYS
from core.cache import _cache_key, _cache_get, _cache_set
from core.memory import _memory_save
from utils.helpers import _b64_too_big

router = APIRouter()
logger = logging.getLogger(__name__)

HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client

# ---- Whisper ----
_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            logger.info(f"Loading Whisper ({model_size})...")
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("Whisper loaded")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")
            return None
    return _whisper_model

def _transcribe_sync(audio_bytes: bytes, suffix: str, language=None):
    model = _get_whisper_model()
    if model is None:
        return None
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, info = model.transcribe(tmp.name, language=language)
        transcript = " ".join(seg.text.strip() for seg in segments)
    return transcript, info.language, info.language_probability

def _tts_sync(text: str, lang: str) -> bytes:
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    import io
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()

async def _call_groq(prompt: str, timeout=30):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")
    resp = await HTTP_CLIENT.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout
    )
    result = resp.json()
    if "choices" not in result:
        raise ValueError(f"Groq API error: {result}")
    return result["choices"][0]["message"]["content"]

# ---- AI CHAT ----
@router.post("/api/chat")
async def ai_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "groq")
    user_id = data.get("user_id", "anonymous")

    personal_kw = ["password", "otp", "secret", "aadhar", "pan", "bank", "cvv", "pin"]
    is_personal = any(kw in prompt.lower() for kw in personal_kw)

    cache_key = None
    if not is_personal:
        cache_key = _cache_key("ai_chat", model, prompt[:100])
        cached = await _cache_get(cache_key)
        if cached:
            cached["source"] = "CACHE"
            return cached

    if model in ["groq", "auto"] and GROQ_API_KEY:
        try:
            response_text = await _call_groq(prompt)
            result_data = {"status": "success", "model": "groq", "response": response_text, "source": "GROQ_LIVE"}
            if not is_personal:
                await _cache_set(cache_key, result_data, 3600)
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": response_text, "model": "groq"})
            return result_data
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if model in ["gemini", "auto"] and GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp = await HTTP_CLIENT.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            result_data = {"status": "success", "model": "gemini", "response": text, "source": "GEMINI_LIVE"}
            if not is_personal:
                await _cache_set(cache_key, result_data, 3600)
            await _memory_save(f"chat:{user_id}:{int(time.time())}", {"prompt": prompt, "response": text, "model": "gemini"})
            return result_data
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")

    return {"error": "All AI models failed or no API keys"}

# ---- WHISPER ----
@router.post("/api/whisper/transcribe")
async def whisper_transcribe(request: Request):
    data = await request.json()
    audio_b64 = data.get("audio_base64", "")
    language = data.get("language")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    if _b64_too_big(audio_b64):
        return JSONResponse(status_code=413, content={"error": "Audio too large (max 10MB)"})
    try:
        audio_bytes = base64.b64decode(audio_b64)
        out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".wav", language)
        if out is None:
            return {"error": "Whisper model not available"}
        transcript, detected_lang, lang_prob = out
        return {
            "status": "success",
            "transcript": transcript,
            "detected_language": detected_lang,
            "language_probability": round(lang_prob, 3),
            "source": "WHISPER_LOCAL"
        }
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return {"error": str(e)}

# ---- TTS ----
@router.post("/api/tts")
async def text_to_speech(request: Request):
    import time
    data = await request.json()
    text = data.get("text", "")
    lang = data.get("lang", "hi")
    if not text:
        return {"error": "text required"}
    try:
        audio_bytes = await run_in_threadpool(_tts_sync, text, lang)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"status": "success", "audio_base64": audio_b64, "lang": lang, "source": "GTTS_LIVE"}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {"error": str(e)}
