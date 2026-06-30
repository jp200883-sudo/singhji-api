from fastapi import Request
import os
import httpx

KEY = os.getenv("WHATSAPP_API_KEY")
PHONE = os.getenv("ADMIN_PHONE", "919XXXXXXXXX")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "whatsapp", "phone": PHONE}
    if method == "POST":
        try:
            b = await request.json()
            return await send_wa(b.get("phone", PHONE), b.get("message", "🦁 Alert!"))
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def send_wa(phone, msg):
    if not KEY: return {"status": "success", "mock": True, "phone": phone, "message": msg, "note": "🦁 Demo mode"}
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get("https://api.callmebot.com/whatsapp.php", params={"phone": phone, "text": msg, "apikey": KEY}, timeout=10)
            return {"status": "success", "sent": True, "response": r.text}
    except Exception as e: return {"status": "error", "error": str(e)}
