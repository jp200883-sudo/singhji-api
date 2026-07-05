"""
🔥 FIRE / SMOKE DETECTION — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class FireAlert(BaseModel):
    location: str
    alert_level: str = "warning"
    fire_type: Optional[str] = "smoke"
    confidence: float = 0.90
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_fire(alert: FireAlert):
    return {
        "status": "alert_received",
        "agent": "fire",
        "priority": "CRITICAL",
        "fire_type": alert.fire_type,
        "message": f"🔥 {alert.fire_type.upper()} at {alert.location}!",
        "timestamp": datetime.utcnow().isoformat()
    }
