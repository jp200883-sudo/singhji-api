"""
🚘 ANPR — Number Plate Recognition — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ANPRAlert(BaseModel):
    location: str
    plate_number: str
    plate_image: Optional[str] = None
    confidence: float = 0.92
    camera_id: Optional[str] = "cam_001"

whitelist_db = []

@router.post("/")
async def detect_anpr(alert: ANPRAlert):
    is_whitelisted = any(w["plate"] == alert.plate_number for w in whitelist_db)
    return {
        "status": "alert_received",
        "agent": "anpr",
        "plate_number": alert.plate_number,
        "whitelisted": is_whitelisted,
        "message": f"🚘 Plate: {alert.plate_number} at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }
