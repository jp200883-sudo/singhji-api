"""
Singh Ji AI - Pika Platform Connector
Pika Labs API
"""
import time
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class PikaConnector(BasePlatformConnector):
    """Pika Labs connector"""
    
    PLATFORM_NAME = "pika"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        if not credentials.base_url:
            self.credentials.base_url = "https://api.pika.art"
    
    async def validate_credentials(self) -> bool:
        """Validate Pika API key"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/v1/users/me",
                headers=headers
            )
            return "id" in response
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check Pika credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/v1/users/me",
                headers=headers
            )
            credits = response.get("credits", 0)
            self.credentials.credits_remaining = credits
            return credits, "active" if credits > 0 else "empty"
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video with Pika"""
        start_time = time.time()
        
        payload = {
            "prompt": request.prompt,
            "aspect_ratio": request.aspect_ratio,
            "frame_rate": 24,
            "motion_strength": 2
        }
        
        if request.image_url:
            payload["image_url"] = request.image_url
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                "/v1/generations",
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
        """Check Pika generation status"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/v1/generations/{task_id}",
                headers=headers
            )
            
            status = response.get("status")
            
            if status == "completed":
                return VideoGenerationResult(
                    success=True,
                    video_url=response.get("output_url"),
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
