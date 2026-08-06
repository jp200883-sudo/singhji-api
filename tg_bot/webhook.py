# telegram/webhook.py
import logging
from datetime import datetime
from fastapi import APIRouter, Request

from core.config import GROQ_API_KEY, TELEGRAM_TOKEN
from core.memory import _memory_save
from core.rate_limit import _rate_check
from core.scheduler import USER_PREFERENCES
from tg_bot.helpers import send_message, handle_voice, handle_photo, set_http_client as set_helper_http_client
from tg_bot.commands import handle_command, set_http_client as set_cmd_http_client
from tg_bot.buttons import handle_button
logger = logging.getLogger(__name__)
router = APIRouter()

HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client
    # सभी sub-modules में HTTP_CLIENT सेट करें
    set_helper_http_client(client)
    set_cmd_http_client(client)

# ==========================================
# TELEGRAM WEBHOOK
# ==========================================
@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        # ---- CALLBACK QUERY (Button Press) ----
        if "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["message"]["chat"]["id"]
            user_id = callback["from"]["id"]
            query_data = callback["data"]
           return await handle_button(chat_id, user_id, query_data)
        # ---- MESSAGE ----
        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_id = message["from"]["id"]

        # ---- Register New User ----
        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {"language": "hi", "location": None}
            await _memory_save(f"user_pref:{user_id}", USER_PREFERENCES[user_id], table="user_memory")
            logger.info(f"New user registered: {user_id}")

        # ---- Pending Input (from button) ----
        pending = USER_PREFERENCES.get(user_id, {}).pop("waiting_for", None)
        if pending and text and not text.startswith("/"):
            pending_map = {
                "weather": "/weather ",
                "mandi": "/mandi ",
                "tax": "/tax ",
                "gold": "/gold ",
                "fuel": "/fuel ",
                "horoscope": "/horoscope ",
                "currency": "/currency ",
                "rozgar": "/rozgar ",
                "search": "/search ",
                "translate": "/translate ",
                "yojana": "/yojana ",
                "tv": "/tv ",
                # ✅ NEW: KYC + Agent pending inputs
                "kyc_aadhaar": "",
                "kyc_pan": "",
                "kyc_address": "",
                "kyc_gram_panchayat": "",
                "agent_phone": "",
                "withdraw_amount": "",
            }
            if pending in pending_map:
                text = pending_map[pending] + text.strip()

        # ---- Scheme Profile Wizard ----
        if text and not text.startswith("/"):
            from tg_bot.scheme_flow import handle_scheme_step
            if await handle_scheme_step(chat_id, user_id, text):
                return {"status": "ok"}

        # ---- Rate Limit ----
        if _rate_check(f"tg_user:{user_id}", 10, 60):
            await send_message(chat_id, "⏳ Please slow down! Try again in 1 minute.")
            return {"status": "ok"}

        # ---- Voice Message ----
        if "voice" in message:
            return await handle_voice(chat_id, user_id, message)

        # ---- Photo Message ----
        if "photo" in message:
            return await handle_photo(chat_id, message)

        # ---- Command ----
        if text.startswith("/"):
            return await handle_command(chat_id, user_id, text)

        # ---- Default: AI Chat ----
        if GROQ_API_KEY and text:
            try:
                from api.ai import _call_groq
                ai_response = await _call_groq(text)
                await send_message(chat_id, ai_response[:4000])
                await _memory_save(f"telegram_chat:{user_id}:{int(datetime.now().timestamp())}", 
                                   {"prompt": text, "response": ai_response})
            except Exception as e:
                await send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")
            return {"status": "ok"}

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
