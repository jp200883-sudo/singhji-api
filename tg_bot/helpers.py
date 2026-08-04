# telegram/helpers.py
import json
import base64
import logging
import asyncio
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from core.config import TELEGRAM_TOKEN, GROQ_API_KEY
from core.memory import _memory_save

logger = logging.getLogger(__name__)

# ==========================================
# HTTP CLIENT - GLOBAL VARIABLE
# ==========================================
HTTP_CLIENT = None

def set_http_client(client):
    """HTTP client set karne ka function - bas itna hi kaam hai"""
    global HTTP_CLIENT
    HTTP_CLIENT = client
    logger.info("✅ Telegram helpers HTTP client set")
    # ⚠️ YAHAN KOI SELF-CALL NAHI HONA CHAHIYE

# ==========================================
# TELEGRAM API BASE URL
# ==========================================
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ==========================================
# SEND MESSAGE
# ==========================================
async def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    """Telegram par message bhejne ka function with auto-retry"""
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
            
            resp = await HTTP_CLIENT.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
            result = resp.json()
            
            if result.get("ok"):
                return result
            else:
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

# ==========================================
# VOICE MESSAGE HANDLER
# ==========================================
async def handle_voice(chat_id, user_id, message):
    """Voice message ko transcribe karke AI response bhejna"""
    try:
        voice = message.get("voice")
        if not voice:
            return {"error": "No voice message found"}
        
        file_id = voice["file_id"]
        logger.info(f"Processing voice message: {file_id}")
        
        # Step 1: Get file path from Telegram
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        
        if not file_data.get("ok"):
            await send_message(chat_id, "❌ Could not get voice file")
            return {"error": "Failed to get file"}
        
        file_path = file_data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        # Step 2: Download voice file
        audio_resp = await HTTP_CLIENT.get(file_url, timeout=30)
        if audio_resp.status_code != 200:
            await send_message(chat_id, "❌ Could not download voice file")
            return {"error": "Failed to download file"}
        
        audio_bytes = audio_resp.content
        
        # Step 3: Transcribe using Whisper
        await send_message(chat_id, "🎤 Transcribing your voice...")
        
        from api.ai import _transcribe_sync
        out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".ogg", None)
        
        if not out:
            await send_message(chat_id, "❌ Whisper model not available")
            return {"error": "Whisper unavailable"}
        
        transcript, detected_lang, lang_prob = out
        logger.info(f"Transcribed: {transcript[:100]}... (lang: {detected_lang}, prob: {lang_prob:.2f})")
        
        # Step 4: Send transcript
        transcript_msg = f"📝 Transcript:\n{transcript}"
        if len(transcript_msg) > 4000:
            transcript_msg = transcript_msg[:4000] + "..."
        await send_message(chat_id, transcript_msg)
        
        # Step 5: Get AI response
        if GROQ_API_KEY:
            await send_message(chat_id, "🤖 Getting AI response...")
            try:
                from api.ai import _call_groq
                ai_text = await _call_groq(transcript)
                
                ai_msg = f"🤖 AI Response:\n{ai_text}"
                if len(ai_msg) > 4000:
                    ai_msg = ai_msg[:4000] + "..."
                await send_message(chat_id, ai_msg)
                
                # Save to memory
                await _memory_save(
                    f"telegram_voice:{user_id}:{int(datetime.now().timestamp())}",
                    {"transcript": transcript, "response": ai_text, "language": detected_lang}
                )
            except Exception as e:
                logger.error(f"AI response error: {e}")
                await send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")
        else:
            await send_message(chat_id, "ℹ️ AI response not available (GROQ_API_KEY missing)")
        
        return {"status": "ok", "transcript": transcript}
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}", exc_info=True)
        await send_message(chat_id, f"❌ Voice error: {str(e)[:100]}")
        return {"error": str(e)}

# ==========================================
# PHOTO MESSAGE HANDLER
# ==========================================
async def handle_photo(chat_id, message):
    """Photo ko Plant Doctor se analyze karna"""
    try:
        photos = message.get("photo")
        if not photos:
            return {"error": "No photo found"}
        
        # Get highest quality photo (last one)
        file_id = photos[-1]["file_id"]
        logger.info(f"Processing photo: {file_id}")
        
        # Step 1: Get file path from Telegram
        file_resp = await HTTP_CLIENT.get(f"{TELEGRAM_API_BASE}/getFile?file_id={file_id}")
        file_data = file_resp.json()
        
        if not file_data.get("ok"):
            await send_message(chat_id, "❌ Could not get photo file")
            return {"error": "Failed to get file"}
        
        file_path = file_data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        # Step 2: Download photo
        img_resp = await HTTP_CLIENT.get(file_url, timeout=30)
        if img_resp.status_code != 200:
            await send_message(chat_id, "❌ Could not download photo")
            return {"error": "Failed to download file"}
        
        # Step 3: Convert to base64
        img_b64 = base64.b64encode(img_resp.content).decode("utf-8")
        
        # Step 4: Detect disease
        await send_message(chat_id, "🌿 Analyzing plant...")
        
        try:
            from modules.kisaan_doctor.handler import _detect_disease
            result = await _detect_disease(img_b64)
            
            if result is None:
                await send_message(chat_id, "❌ Plant ID API key not set")
                return {"error": "API key missing"}
            
            if result.get("is_healthy", False):
                health_pct = result.get("health_probability", 0) * 100
                await send_message(chat_id, f"✅ Plant looks healthy! ({health_pct:.0f}% confidence)")
            else:
                plant_text = "🌿 Disease Detection Result\n\n"
                diseases = result.get("diseases", [])
                if not diseases:
                    plant_text += "No diseases detected, but plant may not be healthy."
                else:
                    for d in diseases[:5]:  # Max 5 diseases
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

# ==========================================
# CHECK IF USER IS ADMIN
# ==========================================
def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    from core.config import ADMIN_USER_ID
    return user_id == ADMIN_USER_ID
