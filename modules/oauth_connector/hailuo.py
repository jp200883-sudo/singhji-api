"""
Singh Ji AI - Hailuo Platform Connector
Hailuo AI (MiniMax) API
"""
import time
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class HailuoConnector(BasePlatformConnector):
    """Hailuo AI connector"""
    
    PLATFORM_NAME = "hailuo"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        if not credentials.base_url:
            self.credentials.base_url = "https://api.hailuo.ai/v1"
    
    async def validate_credentials(self) -> bool:
        """Validate Hailuo API key"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/user/info",
                headers=headers
            )
            return response.get("code") == 0
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check Hailuo credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/user/balance",
                headers=headers
            )
            
            if response.get("code") == 0:
                data = response.get("data", {})
                credits = data.get("balance", 0)
                self.credentials.credits_remaining = credits
                return credits, "active" if credits > 0 else "empty"
            return 0, "error"
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video with Hailuo"""
        start_time = time.time()
        
        payload = {
            "model": "hailuo-video",
            "prompt": request.prompt,
            "duration": request.duration
        }
        
        if request.image_url:
            payload["image_url"] = request.image_url
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                "/videos/generations",
                headers=headers,
                json=payload
            )
            
            task_id = response.get("data", {}).get("task_id")
            
            return VideoGenerationResult(
                success=True,
                task_id=task_id,
                generation_time=time.time() - start_time
            )
            
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """Check Hailuo task status"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/videos/status/{task_id}",
                headers=headers
            )
            
            data = response.get("data", {})
            status = data.get("status")
            
            if status == "success":
                videos = data.get("videos", [])
                video_url = videos[0].get("url") if videos else None
                
                return VideoGenerationResult(
                    success=True,
                    video_url=video_url,
                    task_id=task_id
                )
            elif status == "failed":
                return VideoGenerationResult(
                    success=False,
                    task_id=task_id,
                    error_message="Generation failed"
                )
            else:
                return VideoGenerationResult(
                    success=False,
                    task_id=task_id,
                    error_message="processing"
                )
                
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
