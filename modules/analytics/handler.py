from fastapi import Request
from datetime import datetime

events = []
users = {}

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        q = dict(request.query_params)
        if q.get("type") == "users": return await get_users()
        return await get_dashboard()
    if method == "POST":
        try:
            b = await request.json()
            if b.get("action") == "track": return await track(b)
            return await get_dashboard()
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def track(b):
    e = {"id": len(events)+1, "time": datetime.now().isoformat(), "user": b.get("user_id", "anon"), "action": b.get("event", "?"), "module": b.get("module", "?")}
    events.append(e)
    u = e["user"]
    if u not in users: users[u] = {"first": e["time"], "events": 0}
    users[u]["last"] = e["time"]
    users[u]["events"] += 1
    return {"status": "success", "tracked": True, "id": e["id"]}

async def get_dashboard():
    today = datetime.now().strftime("%Y-%m-%d")
    te = [e for e in events if e["time"].startswith(today)]
    return {"status": "success", "dashboard": {"users": len(users), "events": len(events), "today": len(te), "timestamp": datetime.now().isoformat()}}

async def get_users():
    return {"status": "success", "total": len(users), "users": [{"id": k, **v} for k, v in list(users.items())[:10]]}
