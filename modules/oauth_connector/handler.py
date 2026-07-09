"""
Singh Ji AI - OAuth Connector Handler
Video Generation + Delivery + Watermark Removal
"""
import os
import asyncio
import aiohttp
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .config import PLATFORM_CONFIGS, get_platform_config, get_all_platforms
from .base import BaseConnector
from .router import VideoRouter
from .video_delivery import VideoDelivery
from .watermark_remover import WatermarkRemover

router = APIRouter(prefix="/video", tags=["Video Generation & Delivery"])

# ============ PYDANTIC MODELS ============

class VideoRequest(BaseModel):
    prompt: str
    platform: Optional[str] = None  # None = auto-select
    image_url: Optional[str] = None
    duration: Optional[int] = 5
    negative_prompt: Optional[str] = ""
    aspect_ratio: Optional[str] = "16:9"

class VideoResponse(BaseModel):
    success: bool
    video_id: str
    platform: str
    status: str
    estimated_time: int
    credits_used: int
    message: str

class DeliveryRequest(BaseModel):
    video_url: str
    remove_watermark: bool = False
    quality: Optional[str] = "1080p"

class DeliveryResponse(BaseModel):
    success: bool
    stream_url: Optional[str] = None
    download_url: Optional[str] = None
    platform: str
    quality: str
    watermark_removed: bool
    expires_at: str

# ============ INITIALIZE ============

video_router = VideoRouter()
video_delivery = VideoDelivery()
watermark_remover = WatermarkRemover()

# ============ API ENDPOINTS ============

@router.get("/platforms")
async def list_platforms():
    """📺 Sab video platforms ka status"""
    platforms = []
    for name, config in PLATFORM_CONFIGS.items():
        platforms.append({
            "name": name,
            "display_name": config.display_name,
            "free_credits": config.free_credits,
            "max_duration": config.max_duration,
            "supports_image_to_video": config.supports_image_to_video,
            "supports_audio_sync": config.supports_audio_sync,
            "watermark_on_free": config.watermark_on_free,
            "status": "available"
        })
    return {
        "success": True,
        "platforms": platforms,
        "total": len(platforms),
        "message": "✅ 6 platforms ready!"
    }

@router.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """🎬 Video generate karo — Auto platform select ya manual"""
    
    # Auto-select best platform
    if not request.platform:
        platform_name = await video_router.get_best_platform(
            image_to_video=request.image_url is not None,
            duration=request.duration
        )
    else:
        platform_name = request.platform
    
    config = get_platform_config(platform_name)
    if not config:
        raise HTTPException(status_code=400, detail=f"❌ Platform '{platform_name}' not found!")
    
    # Check credits
    if config.free_credits <= 0:
        raise HTTPException(status_code=402, detail=f"⚠️ {config.display_name} credits khatam!")
    
    # Generate video_id
    video_id = hashlib.sha256(
        f"{request.prompt}{platform_name}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]
    
    # Background mein generate karo
    background_tasks.add_task(
        _generate_video_task,
        video_id=video_id,
        platform=platform_name,
        prompt=request.prompt,
        image_url=request.image_url,
        duration=min(request.duration, config.max_duration),
        negative_prompt=request.negative_prompt,
        aspect_ratio=request.aspect_ratio
    )
    
    return VideoResponse(
        success=True,
        video_id=video_id,
        platform=platform_name,
        status="processing",
        estimated_time=config.max_duration * 3,  # Approximate
        credits_used=1,
        message=f"🎬 {config.display_name} pe video ban raha hai! ID: {video_id}"
    )

@router.get("/status/{video_id}")
async def check_status(video_id: str):
    """⏳ Video generation status check karo"""
    # Supabase/memory se status fetch karo
    status = await video_delivery.get_status(video_id)
    return status

@router.post("/deliver", response_model=DeliveryResponse)
async def deliver_video(request: DeliveryRequest):
    """📦 Video deliver karo — CDN + Watermark removal"""
    
    # Route to best CDN
    route = await video_delivery.route_video(request.video_url)
    
    if not route["success"]:
        raise HTTPException(status_code=503, detail=route["error"])
    
    # Watermark removal if requested
    watermark_removed = False
    if request.remove_watermark:
        result = await watermark_remover.remove_watermark(
            request.video_url,
            method="auto"
        )
        watermark_removed = result.get("success", False)
    
    # Generate clean URLs
    stream_url = f"{route['cdn_url']}/stream/{hashlib.md5(request.video_url.encode()).hexdigest()}"
    download_url = f"{route['cdn_url']}/download/{hashlib.md5(request.video_url.encode()).hexdigest()}"
    
    return DeliveryResponse(
        success=True,
        stream_url=stream_url,
        download_url=download_url,
        platform=route["platform"],
        quality=request.quality,
        watermark_removed=watermark_removed,
        expires_at=(datetime.now().isoformat())
    )

@router.post("/batch")
async def batch_generate(requests: List[VideoRequest]):
    """🔄 Multiple videos ek saath generate karo"""
    tasks = []
    for req in requests:
        # Har request ko alag platform pe bhejo
        tasks.append(generate_video(req, BackgroundTasks()))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {
        "success": True,
        "total": len(results),
        "results": results,
        "message": "🚀 Batch processing complete!"
    }

@router.post("/watermark/remove")
async def remove_watermark_endpoint(video_url: str, method: str = "auto"):
    """💧 Watermark hatao — Auto-detect + AI removal"""
    result = await watermark_remover.remove_watermark(video_url, method=method)
    return result

# ============ BACKGROUND TASKS ============

async def _generate_video_task(video_id: str, platform: str, prompt: str, 
                               image_url: Optional[str], duration: int,
                               negative_prompt: str, aspect_ratio: str):
    """Background mein video generate karo"""
    try:
        connector = BaseConnector(platform)
        result = await connector.generate(
            prompt=prompt,
            image_url=image_url,
            duration=duration,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio
        )
        
        # Status update karo
        await video_delivery.update_status(video_id, "completed", result)
        
    except Exception as e:
        await video_delivery.update_status(video_id, "failed", {"error": str(e)})

# ============ HEALTH CHECK ============

@router.get("/health")
async def health_check():
    """🏥 Video system health check"""
    health = {
        "router": "ok",
        "delivery": "ok",
        "watermark_remover": "ok",
        "platforms": {}
    }
    
    for name in PLATFORM_CONFIGS.keys():
        try:
            # Quick ping
            connector = BaseConnector(name)
            status = await connector.health_check()
            health["platforms"][name] = "ok" if status else "degraded"
        except:
            health["platforms"][name] = "offline"
    
    return health
