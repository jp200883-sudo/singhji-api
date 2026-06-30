from fastapi import Request
from datetime import datetime

carts = {}

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        q = dict(request.query_params)
        return await get_cart(q.get("user_id", "guest"))
    if method == "POST":
        try:
            b = await request.json()
            action = b.get("action", "view")
            uid = b.get("user_id", "guest")
            if action == "add": return await add_cart(uid, b)
            elif action == "remove": return await remove_cart(uid, b)
            elif action == "clear": return await clear_cart(uid)
            return await get_cart(uid)
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def get_cart(uid):
    cart = carts.get(uid, {"items": [], "total": 0})
    return {"status": "success", "user_id": uid, "cart": cart, "items": len(cart["items"]), "timestamp": datetime.now().isoformat()}

async def add_cart(uid, b):
    item = {"id": b.get("item_id"), "name": b.get("name", "Unknown"), "price": b.get("price", 0), "qty": b.get("quantity", 1)}
    if uid not in carts: carts[uid] = {"items": [], "total": 0}
    for e in carts[uid]["items"]:
        if e["id"] == item["id"]: e["qty"] += item["qty"]; break
    else: carts[uid]["items"].append(item)
    carts[uid]["total"] = sum(i["price"] * i["qty"] for i in carts[uid]["items"])
    return {"status": "success", "action": "added", "item": item, "total": carts[uid]["total"], "message": f"🛒 {item['name']} added!"}

async def remove_cart(uid, b):
    if uid in carts:
        carts[uid]["items"] = [i for i in carts[uid]["items"] if i["id"] != b.get("item_id")]
        carts[uid]["total"] = sum(i["price"] * i["qty"] for i in carts[uid]["items"])
    return {"status": "success", "action": "removed"}

async def clear_cart(uid):
    carts[uid] = {"items": [], "total": 0}
    return {"status": "success", "action": "cleared", "message": "🛒 Cart cleared!"}
