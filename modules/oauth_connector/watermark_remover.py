"""
Singh Ji AI - Video Aggregator Module
Watermark Remover - WaveSpeed AI + Fallback Pipeline
Removes watermarks from Seedance, Kling, Hailuo, Luma, Pika, Veo videos
"""
import os
import aiohttp
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class WatermarkType(Enum):
    """Types of watermarks by platform"""
    SEEDANCE_CORNER = "seedance_corner"      # "AI Generated" badge corner
    KLING_OVERLAY = "kling_overlay"          # Semi-transparent overlay
    HAILUO_BADGE = "hailuo_badge"            # Fixed badge
    LUMA_WATERMARK = "luma_watermark"         # Bottom corner
    PIKA_LOGO = "pika_logo"                    # Pika logo
    VEO_BADGE = "veo_badge"                    # Google Veo badge
    GENERIC_TEXT = "generic_text"              # Generic text watermark
    GENERIC_LOGO = "generic_logo"              # Generic logo watermark


@dataclass
class WatermarkRemovalResult:
    """Result of watermark removal"""
    success: bool
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    method_used: str = "unknown"
    credits_used: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    quality_score: float = 0.0  # 0-1, AI-assessed quality


class WatermarkRemover:
    """
    Smart watermark remover with multiple backends:
    1. WaveSpeed AI API (primary) - $0.01/sec, best quality
    2. SorryWatermark API (fallback) - free tier available
    3. Manual mask pipeline (ultimate fallback) - FFmpeg + OpenCV
    """

    # Platform-specific watermark detection configs
    WATERMARK_CONFIGS = {
        "seedance": {
            "type": WatermarkType.SEEDANCE_CORNER,
            "position": "bottom_right",
            "size_ratio": 0.08,  # 8% of frame
            "opacity": 1.0,
            "color": "white"
        },
        "kling": {
            "type": WatermarkType.KLING_OVERLAY,
            "position": "bottom_center",
            "size_ratio": 0.05,
            "opacity": 0.5,
            "color": "semi_transparent"
        },
        "hailuo": {
            "type": WatermarkType.HAILUO_BADGE,
            "position": "bottom_right",
            "size_ratio": 0.06,
            "opacity": 1.0,
            "color": "white"
        },
        "luma": {
            "type": WatermarkType.LUMA_WATERMARK,
            "position": "bottom_right",
            "size_ratio": 0.07,
            "opacity": 0.8,
            "color": "white"
        },
        "pika": {
            "type": WatermarkType.PIKA_LOGO,
            "position": "bottom_left",
            "size_ratio": 0.06,
            "opacity": 1.0,
            "color": "colored"
        },
        "veo": {
            "type": WatermarkType.VEO_BADGE,
            "position": "bottom_right",
            "size_ratio": 0.05,
            "opacity": 0.7,
            "color": "white"
        }
    }

    def __init__(self, 
                 wavespeed_key: Optional[str] = None,
                 sorrywatermark_key: Optional[str] = None):
        self.wavespeed_key = wavespeed_key or os.getenv("WAVESPEED_API_KEY")
        self.sorrywatermark_key = sorrywatermark_key or os.getenv("SORRYWATERMARK_API_KEY")
        self.wavespeed_url = "https://api.wavespeed.ai/v1/watermark/remove"
        self.sorrywatermark_url = "https://api.sorrywatermark.com/v1/remove"

    async def remove_watermark(self, 
                                video_path: str,
                                platform: str,
                                output_path: str,
                                method: str = "auto") -> WatermarkRemovalResult:
        """
        Remove watermark from video

        Args:
            video_path: Input video file path
            platform: Source platform (seedance, kling, etc.)
            output_path: Where to save clean video
            method: "auto", "wavespeed", "sorrywatermark", "manual"
        """
        import time
        start_time = time.time()

        # Detect watermark config
        config = self.WATERMARK_CONFIGS.get(platform, {})

        # Try methods in priority order
        methods_to_try = self._get_method_priority(method)

        for method_name in methods_to_try:
            try:
                if method_name == "wavespeed" and self.wavespeed_key:
                    result = await self._wavespeed_remove(
                        video_path, platform, output_path
                    )
                    if result.success:
                        result.method_used = "wavespeed_ai"
                        result.processing_time = time.time() - start_time
                        return result

                elif method_name == "sorrywatermark" and self.sorrywatermark_key:
                    result = await self._sorrywatermark_remove(
                        video_path, platform, output_path
                    )
                    if result.success:
                        result.method_used = "sorrywatermark_ai"
                        result.processing_time = time.time() - start_time
                        return result

                elif method_name == "manual":
                    result = await self._manual_remove(
                        video_path, platform, output_path, config
                    )
                    if result.success:
                        result.method_used = "manual_opencv"
                        result.processing_time = time.time() - start_time
                        return result

            except Exception as e:
                print(f"Method {method_name} failed: {e}")
                continue

        return WatermarkRemovalResult(
            success=False,
            error="Sab methods fail ho gaye! Watermark remove nahi ho paya.",
            processing_time=time.time() - start_time
        )

    def _get_method_priority(self, method: str) -> List[str]:
        """Get method priority list"""
        if method == "auto":
            return ["wavespeed", "sorrywatermark", "manual"]
        elif method == "wavespeed":
            return ["wavespeed", "manual"]
        elif method == "sorrywatermark":
            return ["sorrywatermark", "manual"]
        elif method == "manual":
            return ["manual"]
        return ["wavespeed", "sorrywatermark", "manual"]

    async def _wavespeed_remove(self, video_path: str, 
                                 platform: str, 
                                 output_path: str) -> WatermarkRemovalResult:
        """Remove watermark using WaveSpeed AI API"""

        # WaveSpeed AI: $0.01/sec, temporal inpainting
        # Upload video, get job ID, poll for result

        async with aiohttp.ClientSession() as session:
            # Step 1: Upload video
            with open(video_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("video", f, filename="input.mp4")
                data.add_field("platform", platform)
                data.add_field("watermark_type", "auto_detect")

                async with session.post(
                    self.wavespeed_url + "/submit",
                    headers={"Authorization": f"Bearer {self.wavespeed_key}"},
                    data=data
                ) as resp:
                    job_data = await resp.json()
                    job_id = job_data.get("job_id")

            if not job_id:
                return WatermarkRemovalResult(
                    success=False,
                    error="WaveSpeed job submit fail"
                )

            # Step 2: Poll for completion
            max_attempts = 120  # 10 minutes max
            for _ in range(max_attempts):
                await asyncio.sleep(5)

                async with session.get(
                    f"{self.wavespeed_url}/status/{job_id}",
                    headers={"Authorization": f"Bearer {self.wavespeed_key}"}
                ) as resp:
                    status = await resp.json()

                    if status.get("status") == "completed":
                        # Download result
                        video_url = status.get("output_url")
                        async with session.get(video_url) as video_resp:
                            with open(output_path, "wb") as f:
                                f.write(await video_resp.read())

                        return WatermarkRemovalResult(
                            success=True,
                            output_path=output_path,
                            output_url=video_url,
                            credits_used=status.get("credits_used", 0),
                            quality_score=status.get("quality_score", 0.9)
                        )

                    elif status.get("status") == "failed":
                        return WatermarkRemovalResult(
                            success=False,
                            error=status.get("error", "WaveSpeed processing failed")
                        )

            return WatermarkRemovalResult(
                success=False,
                error="WaveSpeed timeout - 10 minutes mein complete nahi hua"
            )

    async def _sorrywatermark_remove(self, video_path: str,
                                        platform: str,
                                        output_path: str) -> WatermarkRemovalResult:
        """Remove watermark using SorryWatermark API"""

        async with aiohttp.ClientSession() as session:
            with open(video_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("video", f, filename="input.mp4")
                data.add_field("platform", platform)
                data.add_field("mode", "ai_reconstruction")  # AI inpainting mode

                async with session.post(
                    self.sorrywatermark_url,
                    headers={"Authorization": f"Bearer {self.sorrywatermark_key}"},
                    data=data
                ) as resp:
                    result = await resp.json()

                    if result.get("success"):
                        video_url = result.get("output_url")

                        # Download
                        async with session.get(video_url) as video_resp:
                            with open(output_path, "wb") as f:
                                f.write(await video_resp.read())

                        return WatermarkRemovalResult(
                            success=True,
                            output_path=output_path,
                            output_url=video_url,
                            credits_used=result.get("credits_used", 1)
                        )
                    else:
                        return WatermarkRemovalResult(
                            success=False,
                            error=result.get("error", "SorryWatermark failed")
                        )

    async def _manual_remove(self, video_path: str,
                              platform: str,
                              output_path: str,
                              config: Dict) -> WatermarkRemovalResult:
        """
        Manual watermark removal using FFmpeg + OpenCV
        Fallback method when AI APIs fail or not available
        """
        import subprocess
        import cv2
        import numpy as np

        try:
            # Method 1: Simple crop if watermark is at edge
            position = config.get("position", "bottom_right")

            if position in ["bottom_right", "bottom_left", "bottom_center"]:
                # Crop bottom portion
                crop_ratio = 0.92  # Keep 92% of height

                cmd = [
                    "ffmpeg", "-y", "-i", video_path,
                    "-vf", f"crop=iw:ih*{crop_ratio}:0:0",
                    "-c:a", "copy",
                    output_path
                ]
                subprocess.run(cmd, check=True, capture_output=True)

                return WatermarkRemovalResult(
                    success=True,
                    output_path=output_path,
                    method_used="manual_crop",
                    quality_score=0.7  # Some content lost
                )

            # Method 2: OpenCV inpainting for more complex cases
            # Extract frames, inpaint, reassemble
            temp_dir = f"{output_path}_temp"
            os.makedirs(temp_dir, exist_ok=True)

            # Extract frames
            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-vf", "fps=30",
                f"{temp_dir}/frame_%04d.png"
            ], check=True, capture_output=True)

            # Get video dimensions
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            # Create mask for watermark region
            mask = np.zeros((height, width), np.uint8)

            # Define watermark region based on position
            wm_height = int(height * config.get("size_ratio", 0.08))
            if position == "bottom_right":
                mask[height - wm_height:height, width//2:width] = 255
            elif position == "bottom_left":
                mask[height - wm_height:height, 0:width//2] = 255
            elif position == "bottom_center":
                mask[height - wm_height:height, width//4:3*width//4] = 255

            # Process each frame
            frames = sorted([f for f in os.listdir(temp_dir) if f.endswith(".png")])
            for frame_file in frames:
                frame = cv2.imread(f"{temp_dir}/{frame_file}")
                inpainted = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
                cv2.imwrite(f"{temp_dir}/{frame_file}", inpainted)

            # Reassemble video
            subprocess.run([
                "ffmpeg", "-y",
                "-i", video_path,  # Original for audio
                "-i", f"{temp_dir}/frame_%04d.png",
                "-vf", "fps=30",
                "-c:a", "copy",
                "-shortest",
                output_path
            ], check=True, capture_output=True)

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)

            return WatermarkRemovalResult(
                success=True,
                output_path=output_path,
                method_used="manual_inpainting",
                quality_score=0.6
            )

        except Exception as e:
            return WatermarkRemovalResult(
                success=False,
                error=f"Manual removal failed: {str(e)}"
            )

    async def batch_remove(self, 
                          videos: List[Dict],
                          output_dir: str) -> List[WatermarkRemovalResult]:
        """
        Batch remove watermarks from multiple videos

        Args:
            videos: List of {"path": str, "platform": str, "output_name": str}
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)

        tasks = []
        for video in videos:
            output_path = f"{output_dir}/{video['output_name']}"
            task = self.remove_watermark(
                video["path"],
                video["platform"],
                output_path
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r if not isinstance(r, Exception) else 
                WatermarkRemovalResult(success=False, error=str(r)) 
                for r in results]


# Quick standalone function for simple use
def remove_watermark_sync(video_path: str, 
                           platform: str, 
                           output_path: str) -> WatermarkRemovalResult:
    """Synchronous wrapper for watermark removal"""
    remover = WatermarkRemover()
    return asyncio.run(remover.remove_watermark(video_path, platform, output_path))
