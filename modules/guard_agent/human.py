"""
🚶 HUMAN DETECTION — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class HumanAlert(BaseModel):
    location: str
    person_count: int = 1
    behavior: Optional[str] = None
    confidence: float = 0.90
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_human(alert: HumanAlert):
    return {
        "status": "alert_received",
        "agent": "human",
        "person_count": alert.person_count,
        "behavior": alert.behavior,
        "message": f"🚶 {alert.person_count} person(s) at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }
