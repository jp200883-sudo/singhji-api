"""
Singh Ji AI Video Aggregator - OAuth Connector Base
Abstract base class for all platform connectors
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import asyncio


@dataclass
class PlatformCredentials:
    """User's platform credentials"""
    platform: str
    api_key: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = False
    credits_remaining: float = 0.0
    rate_limit_remaining: int = 0


@dataclass
class VideoGenerationRequest:
    """Video generation request"""
    prompt: str
    duration: int = 5  # seconds
    aspect_ratio: str = "16:9"
    resolution: str = "1080p"
    image_url: Optional[str] = None  # For image-to-video
    audio_url: Optional[str] = None  # For audio sync


@dataclass
class VideoGenerationResult:
    """Video generation result"""
    success: bool
    video_url: Optional[str] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    credits_used: float = 0.0
    generation_time: float = 0.0


class BasePlatformConnector(ABC):
    """Abstract base class for all video platform connectors"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate if credentials are working"""
        pass
    
    @abstractmethod
    async def check_credits(self) -> Tuple[float, str]:
        """Check remaining credits. Returns (credits, status)"""
        pass
    
    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video from request"""
        pass
    
    @abstractmethod
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """Check status of async video generation task"""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Get auth headers - override per platform"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.credentials.api_key}"
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        if not self.session:
            raise RuntimeError("Connector not initialized. Use 'async with'")
        
        url = f"{self.credentials.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                if response.status == 401:
                    raise AuthError("Invalid credentials")
                
                data = await response.json()
                return data
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Network error: {str(e)}")


class AuthError(Exception):
    pass

class RateLimitError(Exception):
    pass

class InsufficientCreditsError(Exception):
    pass
