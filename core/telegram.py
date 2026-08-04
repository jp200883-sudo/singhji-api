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
