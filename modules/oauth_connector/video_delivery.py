"""
Singh Ji AI - Video Delivery System
CDN Routing + Cache + Stream Optimization
"""
import os
import asyncio
import aiohttp
import hashlib
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

class VideoDelivery:
    """Video delivery with CDN + caching"""
    
    def __init__(self):
        self.cache = {}  # Memory cache
        self.max_cache = 50
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None
        
        # CDN endpoints
        self.cdn_map = {
            "seedance": "https://cdn.seedance.ai",
            "kling": "https://cdn.klingai.com",
            "hailuo": "https://cdn.hailuo.ai",
            "luma": "https://cdn.lumalabs.ai",
            "pika": "https://cdn.pika.art",
            "veo": "https://cdn.ofox.ai"
        }
    
    def _get_cache_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
    
    async def route_video(self, video_url: str) -> Dict[str, Any]:
        """🚀 Best CDN route select karo"""
        
        cache_key = self._get_cache_key(video_url)
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached["expires"] > datetime.now():
                return cached["data"]
        
        # Detect platform from URL
        platform = self._detect_platform(video_url)
        cdn_url = self.cdn_map.get(platform, "https://cdn.singhji.ai")
        
        result = {
            "success": True,
            "platform": platform,
            "cdn_url": cdn_url,
            "stream_url": f"{cdn_url}/stream/{cache_key}",
            "download_url": f"{cdn_url}/dl/{cache_key}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # Cache mein daalo
        self.cache[cache_key] = {
            "data": result,
            "expires": datetime.now() + timedelta(minutes=30)
        }
        
        # Cache cleanup
        if len(self.cache) > self.max_cache:
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k]["expires"])
            del self.cache[oldest]
        
        return result
    
    def _detect_platform(self, url: str) -> str:
        """URL se platform detect karo"""
        url_lower = url.lower()
        for platform in self.cdn_map.keys():
            if platform in url_lower:
                return platform
        return "generic"
    
    async def update_status(self, video_id: str, status: str, data: Dict[str, Any]):
        """📊 Video status update karo"""
        if self.supabase:
            try:
                self.supabase.table("video_jobs").upsert({
                    "video_id": video_id,
                    "status": status,
                    "data": json.dumps(data),
                    "updated_at": datetime.now().isoformat()
                }).execute()
            except Exception as e:
                print(f"❌ Supabase update error: {e}")
        
        # Memory mein bhi store karo
        self.cache[f"status_{video_id}"] = {
            "data": {"status": status, "data": data},
            "expires": datetime.now() + timedelta(hours=48)
        }
    
    async def get_status(self, video_id: str) -> Dict[str, Any]:
        """⏳ Video status fetch karo"""
        cache_key = f"status_{video_id}"
        
        # Memory cache check
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached["expires"] > datetime.now():
                return cached["data"]
        
        # Supabase se fetch karo
        if self.supabase:
            try:
                result = self.supabase.table("video_jobs").select("*").eq("video_id", video_id).execute()
                if result.data:
                    return {
                        "video_id": video_id,
                        "status": result.data[0]["status"],
                        "data": json.loads(result.data[0]["data"]),
                        "updated_at": result.data[0]["updated_at"]
                    }
            except Exception as e:
                print(f"❌ Supabase fetch error: {e}")
        
        return {
            "video_id": video_id,
            "status": "unknown",
            "message": "❌ Video ID not found!"
        }

# Singleton
video_delivery = VideoDelivery()
