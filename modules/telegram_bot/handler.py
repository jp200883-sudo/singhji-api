# modules/telegram_bot/handler.py

import os
import logging
import aiohttp
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def send_message(chat_id: int, text: str):
    """Send reply to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                result = await resp.json()
                logger.info(f"📤 Reply sent: {result.get('ok')}")
                return result
                
    except Exception as e:
        logger.error(f"❌ Send failed: {e}")
        return {"ok": False, "error": str(e)}

async def handler(request: Request):
    """Telegram Bot Handler"""
    try:
        data = await request.json()
        logger.info(f"📩 Telegram update: {data}")
        
        if "message" not in data:
            return JSONResponse({"status": "ok", "message": "No message"})
        
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Commands
        if text == "/start":
            reply = "🦁 <b>सिंह जी AI में आपका स्वागत है!</b>\n\nमैं आपका भारतीय सुपर ऐप असिस्टेंट हूँ।\n\nकैसे मदद करूँ?"
        elif text == "/help":
            reply = "🦁 <b>मदद</b>\n\n/start - शुरुआत\n/help - मदद\n/status - स्टेटस"
        else:
            reply = f"🦁 आपने लिखा: <b>{text}</b>\n\nमैं सिंह जी AI हूँ, जल्द और फीचर्स आ रहे हैं!"
        
        # Send reply
        await send_message(chat_id, reply)
        
        return JSONResponse({
            "status": "ok",
            "chat_id": chat_id,
            "reply": reply[:50]
        })
        
    except Exception as e:
        logger.error(f"❌ Bot handler error: {e}")
        return JSONResponse({"status": "error", "message": str(e)})
