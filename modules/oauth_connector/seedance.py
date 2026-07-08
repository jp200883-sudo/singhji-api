"""
Singh Ji AI - Seedance Platform Connector
ByteDance Seedance 2.0 via ModelsLab / CCAPI
"""
import time
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class SeedanceConnector(BasePlatformConnector):
    """Seedance 2.0 connector via ModelsLab or CCAPI"""
    
    PLATFORM_NAME = "seedance"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        # Default to ModelsLab, fallback to CCAPI
        if not credentials.base_url:
            self.credentials.base_url = "https://modelslab.com/api/v6"
    
    async def validate_credentials(self) -> bool:
        """Validate by checking available models"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET", 
                "/video/models",
                headers=headers
            )
            models = response.get("models", [])
            return any("seedance" in str(m).lower() for m in models)
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check remaining credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/user/balance",
                headers=headers
            )
            credits = response.get("balance", 0)
            status = "active" if credits > 0 else "empty"
            self.credentials.credits_remaining = credits
            return credits, status
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video using Seedance"""
        start_time = time.time()
        
        endpoint = "/video/text2video" if not request.image_url else "/video/image2video"
        
        payload = {
            "model": "bytedance/seedance-2.0",
            "prompt": request.prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "resolution": request.resolution
        }
        
        if request.image_url:
            payload["image_url"] = request.image_url
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                endpoint,
                headers=headers,
                json=payload
            )
            
            # Async task returned
            task_id = response.get("task_id") or response.get("id")
            
            return VideoGenerationResult(
                success=True,
                task_id=task_id,
                video_url=None,  # Will be populated after polling
                credits_used=response.get("credits_used", 0),
                generation_time=time.time() - start_time
            )
            
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """Poll for video generation completion"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/video/status/{task_id}",
                headers=headers
            )
            
            status = response.get("status", "unknown")
            
            if status == "completed":
                return VideoGenerationResult(
                    success=True,
                    video_url=response.get("video_url"),
                    task_id=task_id,
                    credits_used=response.get("credits_used", 0)
                )
            elif status == "failed":
                return VideoGenerationResult(
                    success=False,
                    task_id=task_id,
                    error_message=response.get("error", "Generation failed")
                )
            else:
                # Still processing
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
