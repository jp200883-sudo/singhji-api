from fastapi import Request
from datetime import datetime

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "🦁 LIVE", "module": "supreme_agent", "role": "The One", "message": "🦁 Supreme Agent ready!"}
    if method == "POST":
        try:
            body = await request.json()
            action = body.get("action", "status")
            if action == "status": return {"status": "success", "supreme": True, "modules_controlled": 60}
            elif action == "override": return {"status": "success", "target": body.get("module"), "message": "🦁 Override!"}
            elif action == "broadcast": return {"status": "success", "message": body.get("message", "Jai Hind!"), "timestamp": datetime.now().isoformat()}
            return {"status": "success", "action": action}
        except: return {"status": "error", "message": "Invalid request"}
    return {"status": "error", "message": "Method not allowed"}
