"""
Singh Ji AI - Video Aggregator Handler
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
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult
from .router import SmartVideoRouter
video_router = SmartVideoRouter({})
from .video_delivery import VideoDelivery
from .watermark_remover import WatermarkRemover

# ============ PLATFORM CONNECTOR MAP ============
CONNECTOR_MAP = {}

try:
    from .seedance import SeedanceConnector
    CONNECTOR_MAP["seedance"] = SeedanceConnector
except ImportError:
    pass

try:
    from .kling import KlingConnector
    CONNECTOR_MAP["kling"] = KlingConnector
except ImportError:
    pass

try:
    from .hailuo import HailuoConnector
    CONNECTOR_MAP["hailuo"] = HailuoConnector
except ImportError:
    pass

try:
    from .luma import LumaConnector
    CONNECTOR_MAP["luma"] = LumaConnector
except ImportError:
    pass

try:
    from .pika import PikaConnector
    CONNECTOR_MAP["pika"] = PikaConnector
except ImportError:
    pass

try:
    from .veo import VeoConnector
    CONNECTOR_MAP["veo"] = VeoConnector
except ImportError:
    pass

router = APIRouter(prefix="/video", tags=["Video Generation & Delivery"])

# ============ PYDANTIC MODELS ============

class VideoRequest(BaseModel):
    prompt: str
    platform: Optional[str] = None
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

video_router = SmartVideoRouter({})
video_delivery = VideoDelivery()
watermark_remover = WatermarkRemover()

# ============ HELPER FUNCTIONS ============

def get_connector(platform: str, api_key: Optional[str] = None):
    connector_class = CONNECTOR_MAP.get(platform)
    if not connector_class:
        raise HTTPException(status_code=400, detail=f"❌ Platform '{platform}' ka connector nahi mila!")
    
    config = get_platform_config(platform)
    if not config:
        raise HTTPException(status_code=400, detail=f"❌ Platform '{platform}' ka config nahi mila!")
    
    credentials = PlatformCredentials(
        platform=platform,
        api_key=api_key or os.getenv(f"{platform.upper()}_API_KEY", ""),
        base_url=config.base_url,
        is_active=True
    )
    
    return connector_class(credentials)

# ============ API ENDPOINTS ============

@router.get("/platforms")
async def list_platforms():
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
            "connector_available": name in CONNECTOR_MAP,
            "status": "available"
        })
    return {
        "success": True,
        "platforms": platforms,
        "total": len(platforms),
        "connectors_ready": len(CONNECTOR_MAP),
        "message": f"✅ {len(platforms)} platforms ready! {len(CONNECTOR_MAP)} connectors active!"
    }

@router.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    if not request.platform:
        platform_name = "seedance"
    else:
        platform_name = request.platform
    
    config = get_platform_config(platform_name)
    if not config:
        raise HTTPException(status_code=400, detail=f"❌ Platform '{platform_name}' not found!")
    
    if config.free_credits <= 0:
        raise HTTPException(status_code=402, detail=f"⚠️ {config.display_name} credits khatam!")
    
    if platform_name not in CONNECTOR_MAP:
        raise HTTPException(status_code=503, detail=f"🔧 {config.display_name} connector abhi ready nahi hai!")
    
    video_id = hashlib.sha256(
        f"{request.prompt}{platform_name}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]
    
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
        estimated_time=config.max_duration * 3,
        credits_used=1,
        message=f"🎬 {config.display_name} pe video ban raha hai! ID: {video_id}"
    )

@router.get("/status/{video_id}")
async def check_status(video_id: str):
    status = await video_delivery.get_status(video_id)
    return status

@router.post("/deliver", response_model=DeliveryResponse)
async def deliver_video(request: DeliveryRequest):
    route = await video_delivery.route_video(request.video_url)
    
    if not route["success"]:
        raise HTTPException(status_code=503, detail=route["error"])
    
    watermark_removed = False
    if request.remove_watermark:
        result = await watermark_remover.remove_watermark(
            request.video_url,
            method="auto"
        )
        watermark_removed = result.get("success", False)
    
    video_hash = hashlib.md5(request.video_url.encode()).hexdigest()
    stream_url = f"{route['cdn_url']}/stream/{video_hash}"
    download_url = f"{route['cdn_url']}/download/{video_hash}"
    
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
    results = []
    for req in requests:
        try:
            result = await generate_video(req, BackgroundTasks())
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    return {
        "success": True,
        "total": len(results),
        "results": results,
        "message": "🚀 Batch processing complete!"
    }

@router.post("/watermark/remove")
async def remove_watermark_endpoint(video_url: str, method: str = "auto"):
    result = await watermark_remover.remove_watermark(video_url, method=method)
    return result

# ============ BACKGROUND TASKS ============

async def _generate_video_task(video_id: str, platform: str, prompt: str, 
                               image_url: Optional[str], duration: int,
                               negative_prompt: str, aspect_ratio: str):
    try:
        api_key = os.getenv(f"{platform.upper()}_API_KEY", "")
        connector = get_connector(platform, api_key)
        
        request = VideoGenerationRequest(
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            image_url=image_url
        )
        
        async with connector:
            result = await connector.generate_video(request)
        
        await video_delivery.update_status(video_id, "completed", {
            "video_url": result.video_url,
            "task_id": result.task_id,
            "credits_used": result.credits_used,
            "generation_time": result.generation_time
        })
        
    except Exception as e:
        await video_delivery.update_status(video_id, "failed", {"error": str(e)})

# ============ HEALTH CHECK ============

@router.get("/health")
async def health_check():
    health = {
        "router": "ok",
        "delivery": "ok",
        "watermark_remover": "ok",
        "platforms": {}
    }
    
    for name in PLATFORM_CONFIGS.keys():
        try:
            if name in CONNECTOR_MAP:
                api_key = os.getenv(f"{name.upper()}_API_KEY", "")
                connector = get_connector(name, api_key)
                async with connector:
                    status = await connector.validate_credentials()
                health["platforms"][name] = "ok" if status else "degraded"
            else:
                health["platforms"][name] = "no_connector"
        except Exception as e:
            health["platforms"][name] = f"offline: {str(e)}"
    
    return health
