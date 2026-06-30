from fastapi import Request
import os
from datetime import datetime

API = os.getenv("PLANT_ID_API")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "plant_id", "message": "🌱 Upload photo for disease detection"}
    if method == "POST":
        try:
            b = await request.json()
            if not b.get("image"):
                return {"status": "success", "mock": True, "disease": "Leaf Spot", "confidence": 85, "treatment": "Neem oil spray", "message": "🦁 Demo mode"}
            return {"status": "success", "message": "🦁 Real detection coming!"}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}
