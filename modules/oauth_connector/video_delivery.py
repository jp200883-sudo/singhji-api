"""
Singh Ji AI - Video Aggregator Module
Video Delivery - CDN Integration (Bunny Stream + Cloudflare R2)
Fast global video delivery with adaptive streaming
"""
import os
import aiohttp
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
import base64


@dataclass
class CDNConfig:
    """CDN configuration"""
    provider: str  # "bunny", "cloudflare_r2", "cloudflare_stream"
    api_key: str
    storage_zone: Optional[str] = None
    region: str = "ap-south-1"  # Default: India region
    custom_domain: Optional[str] = None


@dataclass
class VideoDeliveryResult:
    """Video delivery result"""
    success: bool
    video_url: Optional[str] = None
    cdn_url: Optional[str] = None
    streaming_url: Optional[str] = None  # HLS/DASH
    thumbnail_url: Optional[str] = None
    expiry: Optional[datetime] = None
    error: Optional[str] = None
    cdn_provider: str = "unknown"


class VideoDelivery:
    """
    Video Delivery Manager
    Supports: Bunny Stream, Cloudflare R2, Cloudflare Stream
    """

    def __init__(self, config: CDNConfig):
        self.config = config
        self.provider = config.provider

        # Bunny Stream config
        if self.provider == "bunny":
            self.bunny_base = "https://video.bunnycdn.com"
            self.bunny_storage = f"https://storage.bunnycdn.com/{config.storage_zone}"
            self.bunny_api_key = config.api_key

        # Cloudflare R2 config
        elif self.provider == "cloudflare_r2":
            self.r2_account_id = config.storage_zone  # Reusing field for account ID
            self.r2_access_key = config.api_key
            self.r2_secret_key = os.getenv("R2_SECRET_KEY")
            self.r2_bucket = os.getenv("R2_BUCKET", "singhji-videos")
            self.r2_endpoint = f"https://{self.r2_account_id}.r2.cloudflarestorage.com"

        # Cloudflare Stream config
        elif self.provider == "cloudflare_stream":
            self.cf_account_id = config.storage_zone
            self.cf_api_token = config.api_key
            self.cf_base = f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account_id}"

    async def upload_video(self, 
                          video_path: str,
                          video_name: Optional[str] = None,
                          metadata: Optional[Dict] = None) -> VideoDeliveryResult:
        """
        Upload video to CDN

        Args:
            video_path: Local video file path
            video_name: Custom name for the file
            metadata: Additional metadata (title, tags, etc.)
        """
        if not video_name:
            video_name = os.path.basename(video_path)

        if self.provider == "bunny":
            return await self._bunny_upload(video_path, video_name, metadata)
        elif self.provider == "cloudflare_r2":
            return await self._r2_upload(video_path, video_name, metadata)
        elif self.provider == "cloudflare_stream":
            return await self._cf_stream_upload(video_path, video_name, metadata)

        return VideoDeliveryResult(
            success=False,
            error=f"Unknown CDN provider: {self.provider}"
        )

    async def _bunny_upload(self, video_path: str, 
                            video_name: str,
                            metadata: Optional[Dict]) -> VideoDeliveryResult:
        """Upload to Bunny Stream"""

        async with aiohttp.ClientSession() as session:
            # Step 1: Create video object in Bunny
            create_payload = {
                "title": metadata.get("title", video_name) if metadata else video_name,
                "collectionId": metadata.get("collection_id", "") if metadata else ""
            }

            async with session.post(
                f"{self.bunny_base}/library/1/videos",
                headers={
                    "AccessKey": self.bunny_api_key,
                    "Content-Type": "application/json"
                },
                json=create_payload
            ) as resp:
                video_data = await resp.json()
                video_id = video_data.get("id")
                library_id = video_data.get("libraryId")

            if not video_id:
                return VideoDeliveryResult(
                    success=False,
                    error="Bunny video creation failed"
                )

            # Step 2: Upload video file
            with open(video_path, "rb") as f:
                async with session.put(
                    f"{self.bunny_base}/library/{library_id}/videos/{video_id}",
                    headers={
                        "AccessKey": self.bunny_api_key,
                        "Content-Type": "application/octet-stream"
                    },
                    data=f
                ) as upload_resp:
                    if upload_resp.status not in [200, 201]:
                        return VideoDeliveryResult(
                            success=False,
                            error=f"Bunny upload failed: {upload_resp.status}"
                        )

            # Step 3: Get CDN URLs
            cdn_url = f"https://video.bunnycdn.com/play/{library_id}/{video_id}"
            streaming_url = f"https://video.bunnycdn.com/play/{library_id}/{video_id}?quality=auto"

            return VideoDeliveryResult(
                success=True,
                video_url=cdn_url,
                cdn_url=cdn_url,
                streaming_url=streaming_url,
                thumbnail_url=f"https://video.bunnycdn.com/play/{library_id}/{video_id}?thumbnail=1",
                cdn_provider="bunny_stream"
            )

    async def _r2_upload(self, video_path: str,
                          video_name: str,
                          metadata: Optional[Dict]) -> VideoDeliveryResult:
        """Upload to Cloudflare R2 (S3-compatible)"""

        import boto3
        from botocore.config import Config

        s3 = boto3.client(
            "s3",
            endpoint_url=self.r2_endpoint,
            aws_access_key_id=self.r2_access_key,
            aws_secret_access_key=self.r2_secret_key,
            config=Config(signature_version="s3v4")
        )

        try:
            # Upload with metadata
            extra_args = {
                "ContentType": "video/mp4",
                "Metadata": metadata or {}
            }

            s3.upload_file(video_path, self.r2_bucket, video_name, ExtraArgs=extra_args)

            # Generate public URL (if bucket is public)
            # Or signed URL for private buckets
            cdn_url = f"https://{self.config.custom_domain or self.r2_account_id + '.r2.dev'}/{video_name}"

            return VideoDeliveryResult(
                success=True,
                video_url=cdn_url,
                cdn_url=cdn_url,
                cdn_provider="cloudflare_r2"
            )

        except Exception as e:
            return VideoDeliveryResult(
                success=False,
                error=f"R2 upload failed: {str(e)}"
            )

    async def _cf_stream_upload(self, video_path: str,
                                 video_name: str,
                                 metadata: Optional[Dict]) -> VideoDeliveryResult:
        """Upload to Cloudflare Stream"""

        async with aiohttp.ClientSession() as session:
            # Step 1: Get upload URL (direct creator upload)
            async with session.post(
                f"{self.cf_base}/stream?direct_user=true",
                headers={
                    "Authorization": f"Bearer {self.cf_api_token}"
                }
            ) as resp:
                upload_data = await resp.json()
                upload_url = upload_data.get("result", {}).get("uploadURL")

            if not upload_url:
                return VideoDeliveryResult(
                    success=False,
                    error="Cloudflare Stream upload URL generation failed"
                )

            # Step 2: Upload video
            with open(video_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("file", f, filename=video_name)

                async with session.post(
                    upload_url,
                    data=data
                ) as upload_resp:
                    stream_data = await upload_resp.json()
                    video_id = stream_data.get("result", {}).get("uid")

            if not video_id:
                return VideoDeliveryResult(
                    success=False,
                    error="Cloudflare Stream upload failed"
                )

            # Step 3: Get streaming URLs
            hls_url = f"https://customer-{self.cf_account_id}.cloudflarestream.com/{video_id}/manifest/video.m3u8"
            dash_url = f"https://customer-{self.cf_account_id}.cloudflarestream.com/{video_id}/manifest/video.mpd"

            return VideoDeliveryResult(
                success=True,
                video_url=f"https://watch.cloudflarestream.com/{video_id}",
                cdn_url=hls_url,
                streaming_url=hls_url,
                thumbnail_url=f"https://customer-{self.cf_account_id}.cloudflarestream.com/{video_id}/thumbnails/thumbnail.jpg",
                cdn_provider="cloudflare_stream"
            )

    async def get_signed_url(self, video_path: str, 
                              expiry_hours: int = 24) -> str:
        """
        Generate signed URL for private video access

        Args:
            video_path: Path/key of the video
            expiry_hours: URL expiry time in hours
        """
        if self.provider == "bunny":
            # Bunny signed URLs
            expiry = int((datetime.utcnow() + timedelta(hours=expiry_hours)).timestamp())
            token = hashlib.sha256(
                f"{self.bunny_api_key}{video_path}{expiry}".encode()
            ).hexdigest()
            return f"{video_path}?token={token}&expires={expiry}"

        elif self.provider == "cloudflare_r2":
            # R2 signed URLs via boto3
            import boto3
            from botocore.config import Config

            s3 = boto3.client(
                "s3",
                endpoint_url=self.r2_endpoint,
                aws_access_key_id=self.r2_access_key,
                aws_secret_access_key=self.r2_secret_key,
                config=Config(signature_version="s3v4")
            )

            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.r2_bucket, "Key": video_path},
                ExpiresIn=expiry_hours * 3600
            )
            return url

        return video_path  # Public URL for other providers

    async def delete_video(self, video_id: str) -> bool:
        """Delete video from CDN"""
        async with aiohttp.ClientSession() as session:
            if self.provider == "bunny":
                async with session.delete(
                    f"{self.bunny_base}/library/1/videos/{video_id}",
                    headers={"AccessKey": self.bunny_api_key}
                ) as resp:
                    return resp.status == 200

            elif self.provider == "cloudflare_stream":
                async with session.delete(
                    f"{self.cf_base}/stream/{video_id}",
                    headers={"Authorization": f"Bearer {self.cf_api_token}"}
                ) as resp:
                    return resp.status == 200

        return False


class MultiCDNRouter:
    """
    Smart CDN Router - Auto-select best CDN based on:
    - User location (India = Bunny/Cloudflare)
    - Video type (shorts = Bunny, long = Cloudflare Stream)
    - Cost optimization
    """

    def __init__(self, configs: Dict[str, CDNConfig]):
        self.configs = configs
        self.providers = {}
        for name, config in configs.items():
            self.providers[name] = VideoDelivery(config)

    async def upload_to_best(self, 
                              video_path: str,
                              video_name: str,
                              user_location: str = "IN",
                              video_type: str = "standard") -> VideoDeliveryResult:
        """
        Auto-select best CDN and upload

        Priority:
        1. India users → Bunny Stream (cheapest, closest edge)
        2. Global users → Cloudflare Stream (best streaming)
        3. Backup → Cloudflare R2 (S3-compatible, free egress)
        """

        # Select provider based on rules
        if user_location == "IN" and "bunny" in self.providers:
            provider = self.providers["bunny"]
        elif video_type == "live_stream" and "cloudflare_stream" in self.providers:
            provider = self.providers["cloudflare_stream"]
        elif "bunny" in self.providers:
            provider = self.providers["bunny"]
        elif "cloudflare_r2" in self.providers:
            provider = self.providers["cloudflare_r2"]
        else:
            provider = list(self.providers.values())[0]

        return await provider.upload_video(video_path, video_name)

    async def get_mirror_urls(self, video_path: str) -> Dict[str, str]:
        """Get URLs from all CDNs for redundancy"""
        urls = {}
        for name, provider in self.providers.items():
            result = await provider.get_signed_url(video_path)
            urls[name] = result
        return urls


# ========== DIRECT DOWNLOAD LINK GENERATOR ==========

class DownloadLinkGenerator:
    """
    Generate direct download links for users
    Supports: temporary signed URLs, permanent public links
    """

    def __init__(self, delivery: VideoDelivery):
        self.delivery = delivery

    async def generate_download_link(self, 
                                     video_path: str,
                                     expiry_hours: int = 24,
                                     max_downloads: Optional[int] = None) -> Dict:
        """
        Generate secure download link

        Returns:
            {
                "download_url": str,
                "expires_at": str,
                "max_downloads": int,
                "file_size": str,
                "format": str
            }
        """
        from datetime import datetime

        signed_url = await self.delivery.get_signed_url(video_path, expiry_hours)

        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)

        # Get file info
        file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
        size_mb = file_size / (1024 * 1024)

        return {
            "download_url": signed_url,
            "expires_at": expiry.isoformat(),
            "max_downloads": max_downloads or "unlimited",
            "file_size": f"{size_mb:.1f} MB",
            "format": "MP4 (H.264)"
        }

    async def generate_streaming_embed(self, 
                                        video_url: str,
                                        width: int = 640,
                                        height: int = 360) -> str:
        """Generate HTML embed code for video player"""

        return f"""
        <div class="singhji-video-player">
            <video width="{width}" height="{height}" controls preload="metadata">
                <source src="{video_url}" type="video/mp4">
                <source src="{video_url.replace('.mp4', '.m3u8')}" type="application/x-mpegURL">
                Your browser does not support the video tag.
            </video>
        </div>
        """
