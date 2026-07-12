"""
🦁 Singh Ji AI — OAuth Connector Config
Social Media Platform Configuration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os

@dataclass
class PlatformConfig:
    """Individual platform configuration"""
    name: str
    auth_url: str
    token_url: str
    scopes: List[str]
    client_id_env: str
    client_secret_env: str
    redirect_uri: str = ""
    enabled: bool = False

@dataclass  
class Config:
    """Main OAuth configuration class"""

    # Platform configs
    platforms: Dict[str, PlatformConfig] = field(default_factory=dict)

    # Global settings
    auto_refresh: bool = True
    refresh_buffer_minutes: int = 5
    token_storage: str = "memory"  # memory, redis, supabase

    def __post_init__(self):
        """Initialize default platforms"""
        self.platforms = {
            "facebook": PlatformConfig(
                name="Facebook",
                auth_url="https://www.facebook.com/v25.0/dialog/oauth",
                token_url="https://graph.facebook.com/v25.0/oauth/access_token",
                scopes=["pages_manage_posts", "pages_read_engagement"],
                client_id_env="FACEBOOK_APP_ID",
                client_secret_env="FACEBOOK_APP_SECRET",
                redirect_uri=os.getenv("FACEBOOK_REDIRECT_URI", ""),
                enabled=bool(os.getenv("FACEBOOK_ACCESS_TOKEN")),
            ),
            "instagram": PlatformConfig(
                name="Instagram",
                auth_url="https://api.instagram.com/oauth/authorize",
                token_url="https://api.instagram.com/oauth/access_token",
                scopes=["instagram_basic", "instagram_content_publish"],
                client_id_env="INSTAGRAM_APP_ID",
                client_secret_env="INSTAGRAM_APP_SECRET",
                redirect_uri=os.getenv("INSTAGRAM_REDIRECT_URI", ""),
                enabled=bool(os.getenv("INSTAGRAM_ACCESS_TOKEN")),
            ),
            "youtube": PlatformConfig(
                name="YouTube",
                auth_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
                client_id_env="YOUTUBE_CLIENT_ID",
                client_secret_env="YOUTUBE_CLIENT_SECRET",
                redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI", ""),
                enabled=bool(os.getenv("YOUTUBE_API_KEY")),
            ),
            "twitter": PlatformConfig(
                name="Twitter/X",
                auth_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token",
                scopes=["tweet.read", "tweet.write", "users.read"],
                client_id_env="TWITTER_CLIENT_ID",
                client_secret_env="TWITTER_CLIENT_SECRET",
                redirect_uri=os.getenv("TWITTER_REDIRECT_URI", ""),
                enabled=bool(os.getenv("TWITTER_BEARER_TOKEN")),
            ),
            "linkedin": PlatformConfig(
                name="LinkedIn",
                auth_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                scopes=["r_liteprofile", "w_member_social"],
                client_id_env="LINKEDIN_CLIENT_ID",
                client_secret_env="LINKEDIN_CLIENT_SECRET",
                redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", ""),
                enabled=False,
            ),
        }

    def get_platform(self, name: str) -> Optional[PlatformConfig]:
        """Get platform config by name"""
        return self.platforms.get(name.lower())

    def get_enabled_platforms(self) -> Dict[str, PlatformConfig]:
        """Get only enabled platforms"""
        return {k: v for k, v in self.platforms.items() if v.enabled}

    def is_enabled(self, platform: str) -> bool:
        """Check if platform is enabled"""
        p = self.platforms.get(platform.lower())
        return p.enabled if p else False

# Singleton instance
_config_instance = None

def get_config() -> Config:
    """Get or create config singleton"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
