# core/telegram.py
import json
import logging
from core.config import TELEGRAM_TOKEN, APP_URL

logger = logging.getLogger(__name__)
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ==========================================
# SEND MESSAGE FUNCTION
# ==========================================
async def _telegram_send_message(http_client, chat_id, text, reply_markup=None, parse_mode=None):
    """Telegram par message bhejne ka function"""
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

# ==========================================
# CHECK WEBHOOK CONFIG
# ==========================================
async def _check_webhook_config(http_client):
    """Check current webhook configuration"""
    if not TELEGRAM_TOKEN or not http_client:
        return
    
    try:
        resp = await http_client.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=10)
        info = resp.json().get("result", {})
        url = info.get("url", "")
        logger.info(f"🔍 Current webhook URL: {url or '(none)'}")
        
        correct_url = f"{APP_URL}/telegram/webhook"
        if url.rstrip("/") != correct_url:
            logger.warning(f"⚠️ Webhook points to {url} but should be {correct_url}")
            await _ensure_correct_webhook(http_client)
    except Exception as e:
        logger.warning(f"⚠️ Webhook check failed: {e}")

# ==========================================
# ENSURE CORRECT WEBHOOK
# ==========================================
async def _ensure_correct_webhook(http_client):
    """Set webhook to correct URL"""
    if not TELEGRAM_TOKEN or not http_client or not APP_URL:
        logger.warning("⚠️ Cannot set webhook: missing TELEGRAM_TOKEN or APP_URL")
        return
    
    correct_url = f"{APP_URL}/telegram/webhook"
    try:
        set_resp = await http_client.get(
            f"{TELEGRAM_API_BASE}/setWebhook",
            params={"url": correct_url},
            timeout=10
        )
        result = set_resp.json()
        if result.get("ok"):
            logger.info(f"✅ Webhook set to: {correct_url}")
        else:
            logger.error(f"❌ Webhook set failed: {result}")
    except Exception as e:
        logger.error(f"❌ Webhook set error: {e}")

# ==========================================
# DELETE WEBHOOK (Optional)
# ==========================================
async def _delete_webhook(http_client):
    """Delete webhook (for testing)"""
    if not TELEGRAM_TOKEN or not http_client:
        return
    
    try:
        resp = await http_client.get(f"{TELEGRAM_API_BASE}/deleteWebhook", timeout=10)
        result = resp.json()
        if result.get("ok"):
            logger.info("✅ Webhook deleted")
        else:
            logger.error(f"❌ Webhook delete failed: {result}")
    except Exception as e:
        logger.error(f"❌ Webhook delete error: {e}")

# ==========================================
# GET WEBHOOK INFO
# ==========================================
async def _get_webhook_info(http_client):
    """Get current webhook info"""
    if not TELEGRAM_TOKEN or not http_client:
        return None
    
    try:
        resp = await http_client.get(f"{TELEGRAM_API_BASE}/getWebhookInfo", timeout=10)
        return resp.json().get("result", {})
    except Exception as e:
        logger.error(f"❌ Get webhook info error: {e}")
        return None
