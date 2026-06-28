from fastapi import APIRouter
import os
import requests

router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")

@router.get("/")
def telegram_home():
    return {
        "module": "telegram_bot",
        "status": "✅ LIVE",
        "bot_token_set": bool(TELEGRAM_BOT_TOKEN),
        "webhook_url_set": bool(TELEGRAM_WEBHOOK_URL),
        "message": "Telegram bot ready — Singh Ji ka messenger!",
        "commands": ["/start", "/help", "/status", "/weather", "/news"]
    }

@router.get("/webhook")
def webhook_info():
    if not TELEGRAM_BOT_TOKEN:
        return {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN not set",
            "message": "Render env mein TELEGRAM_BOT_TOKEN daalo!"
        }
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        return {
            "ok": True,
            "webhook": data.get("result", {}),
            "bot_token_set": True,
            "message": "Webhook info aa gayi!"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Webhook fetch fail — token check karo!"
        }

@router.post("/webhook")
def set_webhook(request: dict):
    if not TELEGRAM_BOT_TOKEN:
        return {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN not set",
            "message": "Token daalo pehle!"
        }
    
    webhook_url = request.get("url", TELEGRAM_WEBHOOK_URL)
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        payload = {"url": webhook_url}
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        return {
            "ok": data.get("ok", False),
            "result": data.get("description", "Done"),
            "webhook_url": webhook_url,
            "message": "Webhook set ho gaya!"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Webhook set fail!"
        }

@router.get("/me")
def get_bot_info():
    if not TELEGRAM_BOT_TOKEN:
        return {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN not set",
            "message": "Token daalo pehle!"
        }
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        return {
            "ok": True,
            "bot": data.get("result", {}),
            "message": "Bot info aa gayi!"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Bot info fetch fail!"
        }

@router.post("/send")
def send_message(request: dict):
    if not TELEGRAM_BOT_TOKEN:
        return {
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN not set",
            "message": "Token daalo pehle!"
        }
    
    chat_id = request.get("chat_id", "")
    text = request.get("text", "Hello from Singh Ji AI!")
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        return {
            "ok": data.get("ok", False),
            "message_id": data.get("result", {}).get("message_id"),
            "chat_id": chat_id,
            "text": text,
            "message": "Message bhej diya!"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Message bhejne mein fail!"
        }
