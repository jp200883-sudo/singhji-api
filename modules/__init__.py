# modules/telegram_bot/__init__.py — Singh Ji AI Ultra v5.0
# This file = handler.py (Render free tier fix)
# Paste COMPLETE handler code here

from fastapi import APIRouter, Request
import os

router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://singhji-api.onrender.com/api/telegram/webhook")

@router.get("/health")
def telegram_health():
    return {
        "module": "telegram_bot",
        "status": "✅ OK",
        "bot_token_set": bool(TELEGRAM_BOT_TOKEN),
        "webhook_url": WEBHOOK_URL
    }

@router.get("/info")
def telegram_info():
    return {
        "module": "telegram_bot",
        "version": "1.0.0",
        "features": [
            "Webhook handler",
            "Message echo",
            "Command /start, /help",
            "Broadcast message"
        ],
        "setup": "Set TELEGRAM_BOT_TOKEN in Render Environment Variables"
    }

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive updates from Telegram"""
    try:
        data = await request.json()
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        # Simple echo + commands
        if text == "/start":
            reply = "🦁 Welcome to Singh Ji AI Ultra! Jai Hind! 🇮🇳"
        elif text == "/help":
            reply = "Commands: /start, /help, /status\nSend any message for AI response!"
        elif text == "/status":
            reply = "🦁 All systems operational! Singh Ji AI is LIVE."
        else:
            reply = f"🦁 Singh Ji AI received: {text}\n\nFull AI integration coming in v5.1!"
        
        # Log for now (async send can be added)
        return {"ok": True, "chat_id": chat_id, "reply": reply, "echo": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/send")
async def telegram_send_message(chat_id: str, message: str):
    """Send message to a chat (requires TELEGRAM_BOT_TOKEN)"""
    if not TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set in environment"}
    
    import aiohttp
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
