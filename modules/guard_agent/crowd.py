"""
👥 CROWD DENSITY — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class CrowdAlert(BaseModel):
    location: str
    person_count: int
    density_level: str = "normal"
    confidence: float = 0.85
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_crowd(alert: CrowdAlert):
    return {
        "status": "alert_received",
        "agent": "crowd",
        "person_count": alert.person_count,
        "density_level": alert.density_level,
        "message": f"👥 Crowd: {alert.person_count} people ({alert.density_level}) at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }
