"""
Singh Ji AI - Veo Platform Connector
Google Veo 3.1 via OFOX unified API
"""
import time
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class VeoConnector(BasePlatformConnector):
    """Google Veo 3.1 connector via OFOX"""
    
    PLATFORM_NAME = "veo"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        if not credentials.base_url:
            self.credentials.base_url = "https://api.ofox.ai/v1"
    
    async def validate_credentials(self) -> bool:
        """Validate Veo API key"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/models",
                headers=headers
            )
            models = response.get("data", [])
            return any("veo" in str(m.get("id", "")).lower() for m in models)
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check OFOX credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/user/balance",
                headers=headers
            )
            credits = response.get("balance", 0)
            self.credentials.credits_remaining = credits
            return credits, "active" if credits > 0 else "empty"
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video with Veo 3.1"""
        start_time = time.time()
        
        # Veo uses OpenAI-compatible endpoint
        payload = {
            "model": "google/veo-3.1",
            "prompt": request.prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }
        
        if request.image_url:
            payload["image_url"] = request.image_url
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                "/video/generations",
                headers=headers,
                json=payload
            )
            
            task_id = response.get("id")
            
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
        """Check Veo generation status"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/video/generations/{task_id}",
                headers=headers
            )
            
            status = response.get("status")
            
            if status == "completed":
                return VideoGenerationResult(
                    success=True,
                    video_url=response.get("video_url"),
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
