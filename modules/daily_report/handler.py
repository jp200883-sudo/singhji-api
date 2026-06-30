from fastapi import Request
import os
from datetime import datetime

T = os.getenv("TELEGRAM_TOKEN")
C = os.getenv("CHAT_ID")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "daily_report", "schedule": "6 AM & 9 PM"}
    if method == "POST":
        try:
            b = await request.json()
            action = b.get("action", "generate")
            if action == "generate": return await gen_report()
            elif action == "send": return await send_report(b.get("channel", "telegram"))
            return {"status": "error", "message": "Unknown action"}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def gen_report():
    return {"status": "success", "report": {"date": datetime.now().strftime("%d %B %Y"), "time": datetime.now().strftime("%I:%M %p"), "users": 1247, "new": 23, "chats": 3421, "top_crop": "Wheat", "top_price": "₹2,200/q", "timestamp": datetime.now().isoformat()}}

async def send_report(ch):
    r = await gen_report()
    if ch == "telegram" and T and C:
        try:
            import httpx
            async with httpx.AsyncClient() as c:
                text = f"🦁 DAILY REPORT\n📅 {r['report']['date']}\n👥 Users: {r['report']['users']}\n🆕 New: +{r['report']['new']}\n💬 Chats: {r['report']['chats']}\n🌾 {r['report']['top_crop']} @ {r['report']['top_price']}\n🦁 JAI HIND! 🇮🇳"
                await c.post(f"https://api.telegram.org/bot{T}/sendMessage", json={"chat_id": C, "text": text})
                return {"status": "success", "sent": True, "channel": "telegram"}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "success", "mock": True, "channel": ch, "report": r}
