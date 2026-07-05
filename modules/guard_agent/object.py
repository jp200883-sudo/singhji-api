"""
⚠️ OBJECT DETECTION — Gun / Knife / Bomb — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ObjectAlert(BaseModel):
    location: str
    object_type: str
    confidence: float = 0.87
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_object(alert: ObjectAlert):
    priority = "CRITICAL" if alert.object_type in ["gun", "bomb"] else "WARNING"
    return {
        "status": "alert_received",
        "agent": "object",
        "priority": priority,
        "object_type": alert.object_type,
        "message": f"⚠️ {alert.object_type.upper()} at {alert.location}!",
        "timestamp": datetime.utcnow().isoformat()
    }
