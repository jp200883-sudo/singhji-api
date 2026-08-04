# telegram/webhook.py
import logging
from datetime import datetime
from fastapi import APIRouter, Request

from core.config import GROQ_API_KEY
from core.memory import _memory_save
from core.rate_limit import _rate_check
from core.scheduler import USER_PREFERENCES
from telegram.helpers import send_message, handle_voice, handle_photo, set_http_client
from telegram.buttons import handle_button
from telegram.commands import handle_command, set_http_client as set_cmd_http_client

logger = logging.getLogger(__name__)
router = APIRouter()

HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client
    set_http_client(client)  # helpers
    set_cmd_http_client(client)  # commands

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
        chat_id =
