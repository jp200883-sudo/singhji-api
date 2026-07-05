"""
👤 FACE RECOGNITION — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class FaceAlert(BaseModel):
    location: str
    person_name: Optional[str] = "Unknown"
    face_id: Optional[str] = None
    confidence: float = 0.88
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_face(alert: FaceAlert):
    return {
        "status": "alert_received",
        "agent": "face",
        "person_name": alert.person_name,
        "face_id": alert.face_id,
        "message": f"👤 Face: {alert.person_name} at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }
