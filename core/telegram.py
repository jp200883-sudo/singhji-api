import json
import base64
import logging
from core.config import TELEGRAM_TOKEN, APP_URL

logger = logging.getLogger(__name__)
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def _telegram_send_message(http_client, chat_id, text, reply_markup=None, parse_mode=None):
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
            resp = await http_client.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
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

async def _ensure_correct_webhook(http_client):
    if not TELEGRAM_TOKEN or not APP_URL:
        return
    correct_url = f"{APP_URL}/telegram/webhook"
    try:
        resp = await http_client.get(
            f"{TELEGRAM_API_BASE}/setWebhook",
            params={"url": correct_url},
            timeout=10
        )
        result = resp.json()
        if result.get("ok"):
            logger.info(f"Webhook set to: {correct_url}")
        else:
            logger.error(f"Webhook set failed: {result}")
    except Exception as e:
        logger.error(f"Webhook set error: {e}")
