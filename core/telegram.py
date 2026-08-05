import httpx
from typing import Optional

# ==========================================
# TELEGRAM FUNCTIONS
# ==========================================

async def send_telegram_message(message: str, bot_token: str = None, chat_id: str = None, parse_mode: str = "Markdown") -> bool:
    """
    Send message to Telegram
    
    Args:
        message: Message text
        bot_token: Telegram bot token (optional, uses config if not provided)
        chat_id: Telegram chat ID (optional, uses config if not provided)
        parse_mode: Markdown, HTML, or None
    """
    # अगर token/chat_id नहीं दिया तो config से ले लो
    if not bot_token or not chat_id:
        try:
            from core.config import config
            bot_token = bot_token or config.get("TELEGRAM_TOKEN")
            chat_id = chat_id or config.get("TELEGRAM_CHAT_ID")
        except:
            print("⚠️ Telegram config not available")
            return False
    
    if not bot_token or not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message[:4096],  # Telegram limit
                    "parse_mode": parse_mode if parse_mode else None
                }
            )
            return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def format_telegram_message(module: str, status: str, detail: str = "", emoji: str = "🤖") -> str:
    """Format message for Telegram"""
    lines = [
        f"{emoji} *{module}*",
        f"Status: {status}"
    ]
    if detail:
        lines.append(f"Details: {detail}")
    return "\n".join(lines)

def format_error_telegram(module: str, error: str) -> str:
    """Format error message for Telegram"""
    return format_telegram_message(
        module=module,
        status="❌ Error",
        detail=error[:100],
        emoji="⚠️"
    )

# ==========================================
# SIMPLE SYNC VERSION (अगर async न चले तो)
# ==========================================

def send_telegram_message_sync(message: str, bot_token: str = None, chat_id: str = None) -> bool:
    """Sync version - uses requests instead of httpx"""
    import requests
    
    if not bot_token or not chat_id:
        try:
            from core.config import config
            bot_token = bot_token or config.get("TELEGRAM_TOKEN")
            chat_id = chat_id or config.get("TELEGRAM_CHAT_ID")
        except:
            return False
    
    if not bot_token or not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message[:4096]
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram sync error: {e}")
        return False
        # ==========================================
# WEBHOOK MANAGEMENT (main.py lifespan में इस्तेमाल होता है)
# ==========================================
async def _telegram_send_message(http_client, chat_id, message: str, parse_mode: str = None) -> bool:
    """Shared HTTP client से मैसेज भेजें (scheduler broadcast के लिए)"""
    from core.config import TELEGRAM_TOKEN
    if not TELEGRAM_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = await http_client.post(
            url,
            json={"chat_id": chat_id, "text": message[:4096], "parse_mode": parse_mode}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False


async def _check_webhook_config(http_client) -> dict:
    """Telegram से मौजूदा webhook जानकारी लाएँ (लॉगिंग के लिए)"""
    from core.config import TELEGRAM_TOKEN
    if not TELEGRAM_TOKEN:
        return {}
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    try:
        response = await http_client.get(url, timeout=10)
        data = response.json()
        print(f"📡 Current webhook: {data.get('result', {})}")
        return data.get("result", {})
    except Exception as e:
        print(f"Webhook check error: {e}")
        return {}


async def _ensure_correct_webhook(http_client) -> bool:
    """Webhook हमारे /telegram/webhook पते पर सेट है, यह पक्का करें"""
    from core.config import TELEGRAM_TOKEN, APP_URL
    if not TELEGRAM_TOKEN or not APP_URL:
        return False
    expected_url = f"{APP_URL}/telegram/webhook"
    info = await _check_webhook_config(http_client)
    if info.get("url", "") == expected_url:
        print("✅ Webhook already correct")
        return True
    set_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    try:
        response = await http_client.post(set_url, json={"url": expected_url})
        data = response.json()
        if data.get("ok"):
            print(f"✅ Webhook set to {expected_url}")
            return True
        print(f"❌ Webhook set failed: {data}")
        return False
    except Exception as e:
        print(f"Webhook set error: {e}")
        return False
