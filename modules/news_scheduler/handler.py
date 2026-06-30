from fastapi import Request
from datetime import datetime

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "news_scheduler", "schedule": "Every 3 hours"}
    if method == "POST":
        try:
            b = await request.json()
            action = b.get("action", "status")
            if action == "fetch": return {"status": "success", "fetched": 10, "timestamp": datetime.now().isoformat()}
            elif action == "broadcast": return {"status": "success", "channels": ["telegram", "whatsapp"], "recipients": 1247}
            return {"status": "success", "next": "In 3 hours"}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}
