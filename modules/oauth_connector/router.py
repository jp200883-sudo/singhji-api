"""
Singh Ji AI - Smart Video Router
Auto-switch between platforms based on credits & availability
"""
import asyncio
from typing import List, Optional, Dict
from dataclasses import dataclass
from .base import (
    BasePlatformConnector, PlatformCredentials, 
    VideoGenerationRequest, VideoGenerationResult
)
from .seedance import SeedanceConnector
from .kling import KlingConnector
from .hailuo import HailuoConnector
from .luma import LumaConnector
from .pika import PikaConnector
from .veo import VeoConnector


@dataclass
class PlatformPriority:
    """Platform with priority score"""
    name: str
    connector: BasePlatformConnector
    priority: int  # Lower = higher priority
    credits: float


class SmartVideoRouter:
    """
    Smart Router - Auto-switch between video platforms
    Priority: Seedance → Kling → Hailuo → Luma → Pika → Veo
    """
    
    PLATFORM_MAP = {
        "seedance": SeedanceConnector,
        "kling": KlingConnector,
        "hailuo": HailuoConnector,
        "luma": LumaConnector,
        "pika": PikaConnector,
        "veo": VeoConnector
    }
    
    DEFAULT_PRIORITY = ["seedance", "kling", "hailuo", "luma", "pika", "veo"]
    
    def __init__(self, user_credentials: Dict[str, PlatformCredentials]):
        """
        Initialize router with user's platform credentials
        
        Args:
            user_credentials: Dict of platform_name -> PlatformCredentials
        """
        self.user_credentials = user_credentials
        self.connectors: Dict[str, BasePlatformConnector] = {}
        self.platform_status: Dict[str, dict] = {}
    
    async def initialize(self):
        """Initialize all connectors and check status"""
        tasks = []
        
        for platform_name, creds in self.user_credentials.items():
            if platform_name in self.PLATFORM_MAP:
                connector_class = self.PLATFORM_MAP[platform_name]
                connector = connector_class(creds)
                self.connectors[platform_name] = connector
                tasks.append(self._check_platform(connector))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_platform(self, connector: BasePlatformConnector):
        """Check platform health and credits"""
        async with connector:
            is_valid = await connector.validate_credentials()
            if is_valid:
                credits, status = await connector.check_credits()
                self.platform_status[connector.PLATFORM_NAME] = {
                    "valid": True,
                    "credits": credits,
                    "status": status
                }
                connector.credentials.is_active = True
            else:
                self.platform_status[connector.PLATFORM_NAME] = {
                    "valid": False,
                    "credits": 0,
                    "status": "invalid_credentials"
                }
    
    def get_available_platforms(self) -> List[PlatformPriority]:
        """Get list of platforms sorted by priority with credits"""
        available = []
        
        for platform_name in self.DEFAULT_PRIORITY:
            if platform_name in self.connectors:
                connector = self.connectors[platform_name]
                status = self.platform_status.get(platform_name, {})
                
                if status.get("valid") and status.get("credits", 0) > 0:
                    priority = self.DEFAULT_PRIORITY.index(platform_name)
                    available.append(PlatformPriority(
                        name=platform_name,
                        connector=connector,
                        priority=priority,
                        credits=status["credits"]
                    ))
        
        # Sort by priority (lower index = higher priority)
        available.sort(key=lambda x: x.priority)
        return available
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """
        Generate video using best available platform
        
        Tries platforms in priority order until one succeeds
        """
        available = self.get_available_platforms()
        
        if not available:
            return VideoGenerationResult(
                success=False,
                error_message="Koi bhi platform available nahi hai! Sab credits khatam ya credentials invalid."
            )
        
        last_error = None
        
        for platform in available:
            try:
                async with platform.connector as conn:
                    # Check credits again (real-time)
                    credits, _ = await conn.check_credits()
                    if credits <= 0:
                        continue
                    
                    # Submit generation
                    result = await conn.generate_video(request)
                    
                    if result.success:
                        # Poll for completion
                        max_attempts = 60  # 5 minutes max
                        for _ in range(max_attempts):
                            await asyncio.sleep(5)
                            status = await conn.check_task_status(result.task_id)
                            
                            if status.success:
                                return VideoGenerationResult(
                                    success=True,
                                    video_url=status.video_url,
                                    task_id=status.task_id,
                                    credits_used=status.credits_used,
                                    generation_time=status.generation_time
                                )
                            elif status.error_message != "processing":
                                # Real error
                                last_error = status.error_message
                                break
                        
                        if result.video_url:
                            return result
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        return VideoGenerationResult(
            success=False,
            error_message=f"Sab platforms fail ho gaye! Last error: {last_error}"
        )
    
    def get_status_summary(self) -> Dict:
        """Get summary of all platform statuses"""
        return {
            "total_platforms": len(self.connectors),
            "available_platforms": len(self.get_available_platforms()),
            "platforms": self.platform_status,
            "priority_order": self.DEFAULT_PRIORITY
        }
