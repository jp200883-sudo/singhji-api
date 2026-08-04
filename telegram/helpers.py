# telegram/helpers.py
import json
import base64
import logging
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from core.config import TELEGRAM_TOKEN, GROQ_API_KEY
from core.memory import _memory_save

logger = logging.getLogger(__name__)

HTTP_CLIENT = None
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client

# ==========================================
# SEND MESSAGE
# ==========================================
async def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    if not TELEGRAM_TOKEN:
        return {"error": "TELEGRAM_TOKEN missing"}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            payload = {"chat_id": chat_id, "text": text}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            resp = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
            result = resp.json()
            if result.get("ok"):
                return result
            else:
                error_msg = result.get("description", "Unknown error")
                if "Too Many Requests" in error_msg and attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error(f"Telegram send failed: {error_msg}")
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(2 ** attempt)
                continue
            logger.error(f"Telegram send exception: {e}")
            return {"error": str(e)}
    return {"error": "Max retries exceeded"}

# ==========================================
# VOICE MESSAGE HANDLER
# ==========================================
async def handle_voice(chat_id, user_id, message):
    voice = message["voice"]
    file_id = voice["file_id"]
    try:
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        if file_data.get("ok"):
            file_path = file_data["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            audio_resp = await HTTP_CLIENT.get(file_url, timeout=15)
            audio_bytes = audio_resp.content

            from api.ai import _transcribe_sync
            out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".ogg", None)
            if out:
                transcript, _, _ = out
                await send_message(chat_id, f"Transcript:\n{transcript}")
                if GROQ_API_KEY:
                    from api.ai import _call_groq
                    ai_text = await _call_groq(transcript)
                    await send_message(chat_id, f"AI Response:\n{ai_text[:4000]}")
                    await _memory_save(f"telegram_voice:{user_id}:{int(datetime.now().timestamp())}", 
                                       {"transcript": transcript, "response": ai_text})
            else:
                await send_message(chat_id, "Whisper model not available")
        else:
            await send_message(chat_id, "Could not download voice file")
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await send_message(chat_id, f"Voice error: {str(e)[:100]}")
    return {"status": "ok"}

# ==========================================
# PHOTO MESSAGE HANDLER
# ==========================================
async def handle_photo(chat_id, message):
    try:
        photos = message["photo"]
        file_id = photos[-1]["file_id"]
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        if file_data.get("ok"):
            file_path = file_data["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            img_resp = await HTTP_CLIENT.get(file_url, timeout=15)
            img_b64 = base64.b64encode(img_resp.content).decode("utf-8")
            await send_message(chat_id, "Analyzing plant...")

            from modules.kisaan_doctor.handler import _detect_disease
            result = await _detect_disease(img_b64)
            if result is None:
                await send_message(chat_id, "Plant ID API key not set")
            elif result.get("is_healthy", False):
                await send_message(chat_id, f"✅ Plant looks healthy! ({result.get('health_probability', 0):.0%})")
            else:
                plant_text = "🌿 Disease Detection Result\n\n"
                for d in result.get("diseases", []):
                    plant_text += f"🔴 {d['name']} ({d.get('probability', 0):.0%})\n{d.get('description', '')[:200]}\n\n"
                await send_message(chat_id, plant_text[:4000])
        else:
            await send_message(chat_id, "Could not download photo")
    except Exception as e:
        logger.error(f"Plant detect error: {e}")
        await send_message(chat_id, f"Plant detection error: {str(e)[:100]}")
    return {"status": "ok"}
