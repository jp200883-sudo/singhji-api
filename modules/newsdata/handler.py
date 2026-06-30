from fastapi import Request
import os
import httpx
from datetime import datetime

KEY = os.getenv("NEWSDATA_API_KEY")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        q = dict(request.query_params)
        return await get_news(q.get("category", "top"))
    if method == "POST":
        try:
            b = await request.json()
            return await get_news(b.get("category", "top"))
        except: return await get_news("top")
    return {"status": "error", "message": "Method not allowed"}

async def get_news(cat):
    if not KEY:
        return {"status": "success", "mock": True, "category": cat, "headlines": [{"title": "🦁 Singh Ji AI Launch!", "source": "Singh Ji"}, {"title": "PM Kisan: New payment", "source": "Agri"}], "timestamp": datetime.now().isoformat()}
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"https://newsdata.io/api/1/news?apikey={KEY}&country=in&language=hi,en&category={cat}", timeout=10)
            d = r.json()
            articles = [{"title": i.get("title"), "source": i.get("source_id")} for i in d.get("results", [])[:5]]
            return {"status": "success", "category": cat, "total": len(articles), "articles": articles, "timestamp": datetime.now().isoformat()}
    except Exception as e: return {"status": "error", "error": str(e)}
