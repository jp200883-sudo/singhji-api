# api/video.py
from fastapi import APIRouter
from core.config import SEEDANCE_API_KEY, KLING_API_KEY, HAILUO_API_KEY, LUMA_API_KEY, PIKA_API_KEY, VEO_API_KEY

router = APIRouter()

@router.post("/generate")
async def video_generate(prompt: str, duration: int = 5, aspect_ratio: str = "16:9"):
    # Placeholder – implement full video generation here
    return {
        "status": "placeholder",
        "message": "Video generation API key required (Seedance/Kling/Hailuo/Luma/Pika/Veo)",
        "available_keys": {
            "seedance": bool(SEEDANCE_API_KEY),
            "kling": bool(KLING_API_KEY),
            "hailuo": bool(HAILUO_API_KEY),
            "luma": bool(LUMA_API_KEY),
            "pika": bool(PIKA_API_KEY),
            "veo": bool(VEO_API_KEY),
        }
    }
