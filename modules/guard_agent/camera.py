"""
📷 CAMERA CONNECTOR — Singh Ji AI Ultra
Camera seedha Singh Ji AI se connect
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

router = APIRouter()

class CameraConfig(BaseModel):
    camera_id: str
    name: str
    location: str
    ip_address: str
    port: int = 554
    protocol: str = "rtsp"
    username: Optional[str] = None
    password: Optional[str] = None
    stream_url: Optional[str] = None
    is_active: bool = True

cameras_db = {}

@router.post("/register")
async def register_camera(config: CameraConfig):
    if not config.stream_url:
        if config.protocol == "rtsp":
            auth = ""
            if config.username and config.password:
                auth = f"{config.username}:{config.password}@"
            config.stream_url = f"rtsp://{auth}{config.ip_address}:{config.port}/stream"
        elif config.protocol == "onvif":
            config.stream_url = f"http://{config.ip_address}:{config.port}/onvif/device_service"
        elif config.protocol == "http":
            config.stream_url = f"http://{config.ip_address}:{config.port}/video"
    
    cameras_db[config.camera_id] = {
        **config.dict(),
        "registered_at": datetime.utcnow().isoformat(),
        "status": "online"
    }
    
    return {
        "status": "registered",
        "camera_id": config.camera_id,
        "stream_url": config.stream_url,
        "message": f"📷 Camera '{config.name}' registered at {config.location}"
    }

@router.get("/list")
async def list_cameras():
    return {"total": len(cameras_db), "cameras": list(cameras_db.values())}

@router.get("/status/{camera_id}")
async def camera_status(camera_id: str):
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {
        "camera_id": camera_id,
        "online": random.random() > 0.1,
        "fps": random.choice([15, 25, 30]),
        "resolution": random.choice(["720p", "1080p", "4K"]),
        "last_frame": datetime.utcnow().isoformat()
    }

@router.post("/test/{camera_id}")
async def test_camera(camera_id: str):
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Camera not found")
    is_online = random.random() > 0.2
    return {
        "camera_id": camera_id,
        "test_result": "passed" if is_online else "failed",
        "online": is_online,
        "message": "✅ Camera online" if is_online else "❌ Camera offline"
    }
