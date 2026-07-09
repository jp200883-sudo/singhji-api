"""
🦁 Singh Ji AI - Simple Video Handler
No Supabase dependency - Demo mode
"""
import os
import hashlib
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/video", tags=["Video"])

# ============ MEMORY STORE (No Supabase) ============
VIDEO_JOBS = {}

# ============ MODELS ============
class VideoRequest(BaseModel):
    prompt: str
    platform: Optional[str] = "seedance"
    image_url: Optional[str] = None
    duration: Optional[int] = 5

class VideoResponse(BaseModel):
    success: bool
    video_id: str
    platform: str
    status: str
    estimated_time: int
    credits_used: int
    message: str

# ============ PLATFORMS ============
PLATFORMS = {
    "seedance": {"display_name": "Seedance 2.0", "free_credits": 100, "max_duration": 20},
    "kling": {"display_name": "Kling AI", "free_credits": 66, "max_duration": 10},
    "hailuo": {"display_name": "Hailuo AI", "free_credits": 3, "max_duration": 6},
    "luma": {"display_name": "Luma Ray", "free_credits": 8, "max_duration": 5},
    "pika": {"display_name": "Pika Labs", "free_credits": 150, "max_duration": 3},
    "veo": {"display_name": "Google Veo 3.1", "free_credits": 10, "max_duration": 8}
}

# ============ ENDPOINTS ============

@router.get("/platforms")
async def list_platforms():
    platforms = []
    for name, config in PLATFORMS.items():
        platforms.append({
            "name": name,
            "display_name": config["display_name"],
            "free_credits": config["free_credits"],
            "max_duration": config["max_duration"],
            "connector_available": True,
            "status": "available"
        })
    return {
        "success": True,
        "platforms": platforms,
        "total": len(platforms),
        "message": f"✅ {len(platforms)} platforms ready!"
    }

@router.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    platform_name = request.platform or "seedance"

    if platform_name not in PLATFORMS:
        raise HTTPException(status_code=400, detail=f"❌ Platform '{platform_name}' not found!")

    video_id = hashlib.sha256(
        f"{request.prompt}{platform_name}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    # Store in memory
    VIDEO_JOBS[video_id] = {
        "id": video_id,
        "platform": platform_name,
        "prompt": request.prompt,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "video_url": None
    }

    # Simulate processing
    background_tasks.add_task(_process_video, video_id)

    return VideoResponse(
        success=True,
        video_id=video_id,
        platform=platform_name,
        status="processing",
        estimated_time=60,
        credits_used=1,
        message=f"🎬 {PLATFORMS[platform_name]['display_name']} pe video ban raha hai! ID: {video_id}"
    )

@router.get("/status/{video_id}")
async def check_status(video_id: str):
    job = VIDEO_JOBS.get(video_id)
    if not job:
        return {"success": False, "error": "Video ID not found"}

    return {
        "success": True,
        "video_id": video_id,
        "status": job["status"],
        "platform": job["platform"],
        "progress": 100 if job["status"] == "completed" else 50,
        "video_url": job.get("video_url"),
        "message": "🎬 Video ready!" if job["status"] == "completed" else "🎬 Processing..."
    }

@router.get("/download/{video_id}")
async def download_video(video_id: str):
    job = VIDEO_JOBS.get(video_id)
    if not job:
        return {"success": False, "error": "Video ID not found"}

    if job["status"] == "completed" and job.get("video_url"):
        return {
            "success": True,
            "video_id": video_id,
            "download_url": job["video_url"],
            "status": "ready",
            "message": "🎬 Video ready! Download kar lo!"
        }

    return {
        "success": False,
        "video_id": video_id,
        "status": job["status"],
        "message": "🎬 Video abhi ban raha hai! Thoda wait karo...",
        "check_status_at": f"/api/oauth_connector/video/status/{video_id}",
        "estimated_time": 30
    }

@router.post("/deliver")
async def deliver_video(video_url: str, remove_watermark: bool = False):
    return {
        "success": True,
        "stream_url": video_url,
        "download_url": video_url,
        "platform": "cdn",
        "quality": "1080p",
        "watermark_removed": remove_watermark
    }

@router.post("/watermark/remove")
async def remove_watermark_endpoint(video_url: str, method: str = "auto"):
    return {
        "success": True,
        "original_url": video_url,
        "clean_url": video_url,
        "method": method,
        "message": "🎨 Watermark removed (demo mode)"
    }

# ============ BACKGROUND TASK ============
async def _process_video(video_id: str):
    """Simulate video processing"""
    await asyncio.sleep(30)  # 30 seconds processing
    if video_id in VIDEO_JOBS:
        VIDEO_JOBS[video_id]["status"] = "completed"
        VIDEO_JOBS[video_id]["video_url"] = f"https://example.com/video/{video_id}.mp4"
        print(f"✅ Video {video_id} completed!")

# ============ HEALTH ============
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "mode": "demo (no supabase)",
        "active_jobs": len(VIDEO_JOBS),
        "platforms": list(PLATFORMS.keys())
    }
