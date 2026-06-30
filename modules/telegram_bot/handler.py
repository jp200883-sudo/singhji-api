from fastapi import Request
import os
import httpx

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "telegram_bot", "bot_status": "active" if TOKEN else "no_token"}
    if method == "POST":
        try:
            b = await request.json()
            if "update_id" in b: return await handle_webhook(b)
            return await send_msg(b.get("chat_id"), b.get("message", "Hello!"))
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def handle_webhook(u):
    msg = u.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    await send_msg(chat_id, f"🦁 Singh Ji: {text}\n(Full AI coming!)")
    return {"status": "ok", "update_id": u.get("update_id")}

async def send_msg(chat_id, text):
    if not TOKEN or not chat_id: return {"status": "error", "message": "Missing token/chat_id"}
    try:
        async with httpx.AsyncClient() as c:
            await c.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
            return {"status": "success", "sent": True}
    except Exception as e: return {"status": "error", "error": str(e)}
