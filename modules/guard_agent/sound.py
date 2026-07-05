"""
🔊 SOUND DETECTION — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class SoundAlert(BaseModel):
    location: str
    sound_type: str
    decibel: Optional[float] = None
    confidence: float = 0.85
    audio_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

@router.post("/")
async def detect_sound(alert: SoundAlert):
    priority = "CRITICAL" if alert.sound_type in ["gunshot", "scream"] else \
               "WARNING" if alert.sound_type in ["glass_break", "alarm"] else "INFO"
    
    return {
        "status": "alert_received",
        "agent": "sound",
        "priority": priority,
        "sound_type": alert.sound_type,
        "decibel": alert.decibel,
        "message": f"🔊 {alert.sound_type.upper()} at {alert.location}!",
        "timestamp": datetime.utcnow().isoformat()
    }
