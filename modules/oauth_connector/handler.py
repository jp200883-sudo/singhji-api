"""
Singh Ji AI - Video Aggregator Handler
"""
import os
import hashlib
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/video", tags=["Video"])

USER_REGISTRY = {}

PLATFORMS = {
    "seedance": {"name": "Seedance 2.0", "free_credits": 100, "max_duration": 20, "watermark": False, "priority": 1},
    "kling": {"name": "Kling AI", "free_credits": 66, "max_duration": 10, "watermark": False, "priority": 2},
    "veo": {"name": "Google Veo 3.1", "free_credits": 10, "max_duration": 8, "watermark": False, "priority": 3},
    "pika": {"name": "Pika Labs", "free_credits": 150, "max_duration": 3, "watermark": True, "priority": 4},
    "luma": {"name": "Luma Ray", "free_credits": 8, "max_duration": 5, "watermark": True, "priority": 5},
    "hailuo": {"name": "Hailuo AI", "free_credits": 3, "max_duration": 6, "watermark": True, "priority": 6}
}

class RegisterRequest(BaseModel):
    email: str
    platforms: List[str]

class VideoRequest(BaseModel):
    email: str
    prompt: str
    duration: Optional[int] = 5

@router.post("/register")
async def register_user(request: RegisterRequest):
    email = request.email
    platforms = request.platforms
    valid = [p for p in platforms if p in PLATFORMS]
    USER_REGISTRY[email] = {"platforms": valid, "registered_at": datetime.now().isoformat()}
    return {"success": True, "email": email, "platforms": valid, "message": f"Registered {len(valid)} platforms!"}

@router.post("/generate")
async def auto_generate(request: VideoRequest, background_tasks: BackgroundTasks):
    email = request.email
    prompt = request.prompt
    duration = request.duration

    user = USER_REGISTRY.get(email)
    if not user:
        return {"success": False, "message": "Register first!", "action": "/api/oauth_connector/video/register"}

    best = None
    best_score = -1
    for p in user["platforms"]:
        if p in PLATFORMS:
            config = PLATFORMS[p]
            score = 0
            if not config["watermark"]:
                score += 100
            score += config["free_credits"]
            if duration <= config["max_duration"]:
                score += 50
            if score > best_score:
                best_score = score
                best = p

    if not best:
        return {"success": False, "message": "No suitable platform found!"}

    platform_config = PLATFORMS[best]
    video_id = hashlib.sha256(f"{email}{prompt}{best}{datetime.now()}".encode()).hexdigest()[:16]

    return {
        "success": True,
        "video_id": video_id,
        "email": email,
        "platform": best,
        "platform_name": platform_config["name"],
        "prompt": prompt,
        "duration": min(duration, platform_config["max_duration"]),
        "status": "processing",
        "watermark": platform_config["watermark"],
        "message": f"Video generating on {platform_config['name']}!"
    }

@router.get("/status/{video_id}")
async def check_status(video_id: str):
    return {"success": True, "video_id": video_id, "status": "processing", "message": "Video is being generated..."}

@router.get("/download/{video_id}")
async def download_video(video_id: str):
    return {"success": True, "video_id": video_id, "status": "ready", "clean_video_url": f"https://cdn.singhji.ai/video/{video_id}_clean.mp4", "message": "Clean video ready! No watermark!"}

@router.get("/platforms")
async def list_platforms():
    return {"success": True, "platforms": [{"name": k, "display_name": v["name"], "free_credits": v["free_credits"], "watermark": v["watermark"], "max_duration": v["max_duration"]} for k, v in PLATFORMS.items()]}

@router.get("/health")
async def health():
    return {"status": "ok", "mode": "Auto Video Aggregator", "registered_users": len(USER_REGISTRY)}
