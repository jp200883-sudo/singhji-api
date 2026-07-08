"""
Singh Ji AI - Platform Configuration
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PlatformConfig:
    """Configuration for each video platform"""
    name: str
    display_name: str
    auth_type: str  # "api_key", "jwt", "oauth2"
    base_url: str
    docs_url: str
    free_credits: int
    max_duration: int  # seconds
    supports_image_to_video: bool
    supports_audio_sync: bool
    watermark_on_free: bool


PLATFORM_CONFIGS: Dict[str, PlatformConfig] = {
    "seedance": PlatformConfig(
        name="seedance",
        display_name="Seedance 2.0",
        auth_type="api_key",
        base_url="https://modelslab.com/api/v6",
        docs_url="https://docs.modelslab.com",
        free_credits=100,
        max_duration=20,
        supports_image_to_video=True,
        supports_audio_sync=True,
        watermark_on_free=False
    ),
    "kling": PlatformConfig(
        name="kling",
        display_name="Kling AI",
        auth_type="jwt",
        base_url="https://api.klingai.com",
        docs_url="https://docs.klingai.com",
        free_credits=66,
        max_duration=10,
        supports_image_to_video=True,
        supports_audio_sync=False,
        watermark_on_free=False
    ),
    "hailuo": PlatformConfig(
        name="hailuo",
        display_name="Hailuo AI",
        auth_type="api_key",
        base_url="https://api.hailuo.ai/v1",
        docs_url="https://docs.hailuo.ai",
        free_credits=3,
        max_duration=6,
        supports_image_to_video=True,
        supports_audio_sync=False,
        watermark_on_free=True
    ),
    "luma": PlatformConfig(
        name="luma",
        display_name="Luma Ray",
        auth_type="api_key",
        base_url="https://api.lumalabs.ai",
        docs_url="https://docs.lumalabs.ai",
        free_credits=8,
        max_duration=5,
        supports_image_to_video=True,
        supports_audio_sync=False,
        watermark_on_free=True
    ),
    "pika": PlatformConfig(
        name="pika",
        display_name="Pika Labs",
        auth_type="api_key",
        base_url="https://api.pika.art",
        docs_url="https://docs.pika.art",
        free_credits=150,
        max_duration=3,
        supports_image_to_video=True,
        supports_audio_sync=True,
        watermark_on_free=True
    ),
    "veo": PlatformConfig(
        name="veo",
        display_name="Google Veo 3.1",
        auth_type="api_key",
        base_url="https://api.ofox.ai/v1",
        docs_url="https://docs.ofox.ai",
        free_credits=10,
        max_duration=8,
        supports_image_to_video=True,
        supports_audio_sync=True,
        watermark_on_free=False
    )
}


def get_platform_config(platform_name: str) -> PlatformConfig:
    """Get config for a platform"""
    return PLATFORM_CONFIGS.get(platform_name)


def get_all_platforms() -> List[PlatformConfig]:
    """Get all platform configs"""
    return list(PLATFORM_CONFIGS.values())
