from fastapi import Request
from datetime import datetime

PRICES = {"wheat": {"punjab": 2200, "up": 2150, "mp": 2100}, "rice": {"punjab": 3200, "up": 3100}, "corn": {"punjab": 1800, "up": 1750}}

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        q = dict(request.query_params)
        return await get_mandi(q.get("crop", "wheat"), q.get("state", "punjab"))
    if method == "POST":
        try:
            b = await request.json()
            return await get_mandi(b.get("crop", "wheat"), b.get("state", "punjab"))
        except: return await get_mandi("wheat", "punjab")
    return {"status": "error", "message": "Method not allowed"}

async def get_mandi(crop, state):
    c, s = crop.lower(), state.lower()
    if c in PRICES and s in PRICES[c]:
        return {"status": "success", "crop": c, "state": s, "price": PRICES[c][s], "unit": "₹/quintal", "trend": "⬆️ 2%", "timestamp": datetime.now().isoformat()}
    return {"status": "success", "crop": c, "state": s, "price": "N/A", "message": "🦁 Try: wheat, rice, corn", "timestamp": datetime.now().isoformat()}
