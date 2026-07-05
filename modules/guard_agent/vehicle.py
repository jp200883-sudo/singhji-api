"""
🚗 VEHICLE DETECTION — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

router = APIRouter()

class VehicleAlert(BaseModel):
    location: str
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    confidence: float = 0.95
    image_url: Optional[str] = None
    camera_id: Optional[str] = "cam_001"

VEHICLE_TYPES = ["car", "bike", "truck", "bus", "auto", "van"]
COLORS = ["white", "black", "red", "blue", "silver", "grey", "green"]
whitelist_db = []

@router.post("/")
async def detect_vehicle(alert: VehicleAlert):
    if not alert.vehicle_type:
        alert.vehicle_type = random.choice(VEHICLE_TYPES)
    if not alert.color:
        alert.color = random.choice(COLORS)
    
    is_whitelisted = False
    if alert.vehicle_number:
        is_whitelisted = any(w["plate"] == alert.vehicle_number for w in whitelist_db)
    
    return {
        "status": "alert_received",
        "agent": "vehicle",
        "vehicle_number": alert.vehicle_number,
        "vehicle_type": alert.vehicle_type,
        "color": alert.color,
        "whitelisted": is_whitelisted,
        "message": f"🚗 {alert.vehicle_type.upper()} {alert.color} at {alert.location}",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/whitelist")
async def add_whitelist(plate_number: str, owner_name: str, vehicle_type: str = "car"):
    entry = {"plate": plate_number, "owner": owner_name, "type": vehicle_type, "added_at": datetime.utcnow().isoformat()}
    whitelist_db.append(entry)
    return {"status": "added", "entry": entry}

@router.get("/whitelist")
async def get_whitelist():
    return {"whitelist": whitelist_db, "total": len(whitelist_db)}
