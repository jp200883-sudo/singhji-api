"""
Singh Ji AI - Kling Platform Connector
Kling AI v2/v3 API
"""
import time
import hmac
import hashlib
import base64
from typing import Tuple
from .base import BasePlatformConnector, PlatformCredentials, VideoGenerationRequest, VideoGenerationResult


class KlingConnector(BasePlatformConnector):
    """Kling AI connector with JWT auth"""
    
    PLATFORM_NAME = "kling"
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        if not credentials.base_url:
            self.credentials.base_url = "https://api.klingai.com"
    
    def _generate_jwt(self) -> str:
        """Generate JWT token from access_key + secret_key"""
        import jwt
        import datetime
        
        payload = {
            "iss": self.credentials.access_key,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "iat": datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.credentials.secret_key, algorithm="HS256")
        return token
    
    def _get_headers(self) -> dict:
        """Kling uses JWT auth"""
        token = self._generate_jwt()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    async def validate_credentials(self) -> bool:
        """Validate by fetching user info"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/v1/user/info",
                headers=headers
            )
            return response.get("code") == 200
        except Exception:
            return False
    
    async def check_credits(self) -> Tuple[float, str]:
        """Check Kling credits"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                "/v1/user/balance",
                headers=headers
            )
            
            if response.get("code") == 200:
                data = response.get("data", {})
                credits = data.get("balance", 0)
                self.credentials.credits_remaining = credits
                return credits, "active" if credits > 0 else "empty"
            return 0, "error"
        except Exception as e:
            return 0, f"error: {str(e)}"
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video with Kling"""
        start_time = time.time()
        
        payload = {
            "model_name": "kling-v2-master",
            "prompt": request.prompt,
            "duration": str(request.duration),
            "aspect_ratio": request.aspect_ratio
        }
        
        if request.image_url:
            payload["image"] = request.image_url
        
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "POST",
                "/v1/videos/text2video",
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
        """Check Kling task status"""
        try:
            headers = self._get_headers()
            response = await self._make_request(
                "GET",
                f"/v1/videos/status/{task_id}",
                headers=headers
            )
            
            data = response.get("data", {})
            status = data.get("status")
            
            if status == "succeed":
                videos = data.get("task_result", {}).get("videos", [])
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
