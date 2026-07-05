"""
🎭 BEHAVIOR ANALYSIS — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class BehaviorAlert(BaseModel):
    location: str
    behavior_type: str
    person_id: Optional[str] = None
    confidence: float = 0.80
    video_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_behavior(alert: BehaviorAlert):
    return {
        "status": "alert_received",
        "agent": "behavior",
        "behavior_type": alert.behavior_type,
        "message": f"🎭 {alert.behavior_type.upper()} at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }
