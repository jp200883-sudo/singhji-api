# tg_bot/helpers.py
import json
import base64
import logging
import asyncio
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from core.config import TELEGRAM_TOKEN, GROQ_API_KEY
from core.memory import _memory_save

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# HTTP CLIENT - GLOBAL
# ═══════════════════════════════════════════════════════════════
HTTP_CLIENT = None


def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client
    logger.info("✅ Telegram helpers HTTP client set")


# ═══════════════════════════════════════════════════════════════
# TELEGRAM API BASE
# ═══════════════════════════════════════════════════════════════
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ═══════════════════════════════════════════════════════════════
# SAFE AI IMPORTS — कोई भी नाम उपलब्ध हो, काम चलेगा
# ═══════════════════════════════════════════════════════════════
_ai_call = None


def _get_ai_callable():
    """कई नामों में से जो भी मिले, उसे लौटाता है।"""
    global _ai_call
    if _ai_call is not None:
        return _ai_call

    try:
        from api.ai import ask as _ai_call
        logger.info("✅ AI callable loaded: ask()")
        return _ai_call
    except ImportError:
        pass

    try:
        from api.ai import _call_groq as _ai_call
        logger.info("✅ AI callable loaded: _call_groq()")
        return _ai_call
    except ImportError:
        pass

    try:
        from api.ai import get_brain as _get_brain
        async def _brain_call(prompt, *a, **kw):
            brain = _get_brain()
            result = await brain.get_best_response(str(prompt))
            return result.get("response", "")
        _ai_call = _brain_call
        logger.info("✅ AI callable loaded: get_brain()")
        return _ai_call
    except ImportError:
        pass

    logger.error("❌ कोई भी AI callable api.ai में नहीं मिला")
    _ai_call = None
    return None


async def _ai_respond(transcript: str) -> str:
    """AI से जवाब लो — जो भी callable मिले उससे।"""
    fn = _get_ai_callable()
    if fn is None:
        raise RuntimeError("api.ai में कोई callable नहीं मिला")

    try:
        # पहले ask() style ट्राई करो (prompt + user_id)
        result = fn(transcript, "telegram_user")
        if asyncio.iscoroutine(result):
            result = await result
        return str(result)
    except TypeError:
        pass

    # fallback — सिर्फ prompt
    result = fn(transcript)
    if asyncio.iscoroutine(result):
        result = await result
    return str(result)


# ═══════════════════════════════════════════════════════════════
# SEND MESSAGE
# ═══════════════════════════════════════════════════════════════
async def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN missing")
        return {"error": "TELEGRAM_TOKEN missing"}

    if not HTTP_CLIENT:
        logger.error("HTTP_CLIENT not set")
        return {"error": "HTTP_CLIENT not set"}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            payload = {"chat_id": chat_id, "text": text}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)

            resp = await HTTP_CLIENT.post(
                f"{TELEGRAM_API_BASE}/sendMessage", json=payload
            )
            result = resp.json()

            if result.get("ok"):
                return result

            error_msg = result.get("description", "Unknown error")
            if "Too Many Requests" in error_msg and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Telegram send failed: {error_msg}")
            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Send error, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Telegram send exception: {e}")
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


# ═══════════════════════════════════════════════════════════════
# VOICE HANDLER
# ═══════════════════════════════════════════════════════════════
async def handle_voice(chat_id, user_id, message):
    """Voice → transcribe → AI response"""
    try:
        voice = message.get("voice")
        if not voice:
            return {"error": "No voice message found"}

        file_id = voice["file_id"]
        logger.info(f"Processing voice message: {file_id}")

        # 1. Telegram से file path लो
        file_resp = await HTTP_CLIENT.get(
            f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}"
        )
        file_data = file_resp.json()

        if not file_data.get("ok"):
            await send_message(chat_id, "❌ Could not get voice file")
            return {"error": "Failed to get file"}

        file_path = file_data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

        # 2. Voice file download करो
        audio_resp = await HTTP_CLIENT.get(file_url, timeout=30)
        if audio_resp.status_code != 200:
            await send_message(chat_id, "❌ Could not download voice file")
            return {"error": "Failed to download file"}

        audio_bytes = audio_resp.content

        # 3. Whisper से transcribe करो — भाषा "hi" ज़बरदस्ती
        await send_message(chat_id, "🎤 Transcribing your voice...")

        try:
            from api.ai import _transcribe_sync
            out = await run_in_threadpool(
                _transcribe_sync, audio_bytes, ".ogg", "hi"    # ← "hi", None नहीं
            )
        except ImportError:
            await send_message(chat_id, "❌ Whisper module नहीं मिला")
            return {"error": "Whisper import failed"}

        if not out:
            await send_message(chat_id, "❌ Whisper model not available")
            return {"error": "Whisper unavailable"}

        transcript, detected_lang, lang_prob = out
        logger.info(
            f"Transcribed: {transcript[:100]}... "
            f"(lang: {detected_lang}, prob: {lang_prob:.2f})"
        )

        # 4. Transcript भेजो
        transcript_msg = f"📝 Transcript:\n{transcript}"
        if len(transcript_msg) > 4000:
            transcript_msg = transcript_msg[:4000] + "..."
        await send_message(chat_id, transcript_msg)

        # 5. AI जवाब लो
        await send_message(chat_id, "🤖 Getting AI response...")

        try:
            ai_text = await _ai_respond(transcript)

            ai_msg = f"🤖 AI Response:\n{ai_text}"
            if len(ai_msg) > 4000:
                ai_msg = ai_msg[:4000] + "..."
            await send_message(chat_id, ai_msg)

            await _memory_save(
                f"telegram_voice:{user_id}:{int(datetime.now().timestamp())}",
                {
                    "transcript": transcript,
                    "response": ai_text,
                    "language": detected_lang,
                },
            )
        except Exception as e:
            logger.error(f"AI response error: {e}", exc_info=True)
            await send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")

        return {"status": "ok", "transcript": transcript}

    except Exception as e:
        logger.error(f"Voice processing error: {e}", exc_info=True)
        await send_message(chat_id, f"❌ Voice error: {str(e)[:100]}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# PHOTO HANDLER
# ═══════════════════════════════════════════════════════════════
async def handle_photo(chat_id, message):
    """Photo → Plant Doctor से analyze"""
    try:
        photos = message.get("photo")
        if not photos:
            return {"error": "No photo found"}

        file_id = photos[-1]["file_id"]
        logger.info(f"Processing photo: {file_id}")

        file_resp = await HTTP_CLIENT.get(
            f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}"
        )
        file_data = file_resp.json()

        if not file_data.get("ok"):
            await send_message(chat_id, "❌ Could not get photo file")
            return {"error": "Failed to get file"}

        file_path = file_data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

        img_resp = await HTTP_CLIENT.get(file_url, timeout=30)
        if img_resp.status_code != 200:
            await send_message(chat_id, "❌ Could not download photo")
            return {"error": "Failed to download file"}

        img_b64 = base64.b64encode(img_resp.content).decode("utf-8")

        await send_message(chat_id, "🌿 Analyzing plant...")

        try:
            from modules.kisaan_doctor.handler import _detect_disease
            result = await _detect_disease(img_b64)

            if result is None:
                await send_message(chat_id, "❌ Plant ID API key not set")
                return {"error": "API key missing"}

            if result.get("is_healthy", False):
                health_pct = result.get("health_probability", 0) * 100
                await send_message(
                    chat_id, f"✅ Plant looks healthy! ({health_pct:.0f}% confidence)"
                )
            else:
                plant_text = "🌿 Disease Detection Result\n\n"
                diseases = result.get("diseases", [])
                if not diseases:
                    plant_text += "No diseases detected, but plant may not be healthy."
                else:
                    for d in diseases[:5]:
                        name = d.get("name", "Unknown")
                        prob = d.get("probability", 0) * 100
                        desc = d.get("description", "")[:200]
                        plant_text += f"🔴 {name} ({prob:.0f}%)\n{desc}\n\n"

                if len(plant_text) > 4000:
                    plant_text = plant_text[:4000] + "..."
                await send_message(chat_id, plant_text)

            return {"status": "ok", "result": result}

        except ImportError:
            await send_message(chat_id, "❌ Plant Doctor module not available")
            return {"error": "Module not found"}

    except Exception as e:
        logger.error(f"Photo processing error: {e}", exc_info=True)
        await send_message(chat_id, f"❌ Plant detection error: {str(e)[:100]}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# ADMIN CHECK
# ═══════════════════════════════════════════════════════════════
def is_admin(user_id: int) -> bool:
    from core.config import ADMIN_USER_ID
    return user_id == ADMIN_USER_ID
