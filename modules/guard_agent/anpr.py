"""
🚘 ANPR — Number Plate Recognition — Singh Ji AI Ultra
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


class ANPRAlert(BaseModel):
    location: str
    plate_number: str
    plate_image: Optional[str] = None
    confidence: float = 0.92
    camera_id: Optional[str] = "cam_001"


class WhitelistEntry(BaseModel):
    plate: str
    owner_name: Optional[str] = None
    note: Optional[str] = None


whitelist_db = []


@router.post("/")
async def detect_anpr(alert: ANPRAlert):
    try:
        plate = alert.plate_number.strip().upper()
        is_whitelisted = any(w["plate"] == plate for w in whitelist_db)

        return {
            "status": "alert_received",
            "agent": "anpr",
            "plate_number": plate,
            "location": alert.location,
            "camera_id": alert.camera_id,
            "confidence": alert.confidence,
            "whitelisted": is_whitelisted,
            "message": f"Plate: {plate} at {alert.location}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"ANPR detect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist")
async def add_whitelist(entry: WhitelistEntry):
    try:
        plate = entry.plate.strip().upper()
        if any(w["plate"] == plate for w in whitelist_db):
            return {"status": "already_exists", "plate": plate}

        whitelist_db.append({
            "plate": plate,
            "owner_name": entry.owner_name,
            "note": entry.note,
            "added_at": datetime.utcnow().isoformat()
        })
        return {"status": "added", "plate": plate}
    except Exception as e:
        logger.error(f"ANPR whitelist add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whitelist")
async def get_whitelist():
    return {"count": len(whitelist_db), "whitelist": whitelist_db}
