"""
Singh Ji AI - Luma Platform Connector
Luma API (Ray 3 family)
"""
import time
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class LumaConnector(BasePlatformConnector):
    """Luma AI connector"""
    
    PLATFORM_NAME = "luma"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        if not credentials.base_url:
            self.credentials.base_url = "https://api.lumalabs.ai"
    
    async def validate_credentials(self) -> bool:
        """Validate Luma API key"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/dream-machine/v1/models",
                headers=headers
            )
            return "models" in response
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check Luma credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/dream-machine/v1/credits",
                headers=headers
            )
            credits = response.get("credits_remaining", 0)
            self.credentials.credits_remaining = credits
            return credits, "active" if credits > 0 else "empty"
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video with Luma"""
        start_time = time.time()
        
        payload = {
            "prompt": request.prompt,
            "aspect_ratio": request.aspect_ratio
        }
        
        if request.image_url:
            payload["keyframes"] = {
                "frame0": {"type": "image", "url": request.image_url}
            }
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                "/dream-machine/v1/generations",
                headers=headers,
                json=payload
            )
            
            generation_id = response.get("id")
            
            return VideoGenerationResult(
                success=True,
                task_id=generation_id,
                generation_time=time.time() - start_time
            )
            
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """Check Luma generation status"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/dream-machine/v1/generations/{task_id}",
                headers=headers
            )
            
            state = response.get("state")
            
            if state == "completed":
                assets = response.get("assets", {})
                video_url = assets.get("video")
                
                return VideoGenerationResult(
                    success=True,
                    video_url=video_url,
                    task_id=task_id
                )
            elif state == "failed":
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
