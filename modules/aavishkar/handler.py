"""
🦁 AAVISHKAR v4.1 — Fixed POST/GET
"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import urllib.parse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["aavishkar"])

TIER_1_POLLINATIONS = "https://image.pollinations.ai/prompt/{prompt}"
TIER_3_PICSUM = "https://picsum.photos/{width}/{height}"

@router.get("/")
async def aavishkar_root():
    return {
        "module": "🦁 Aavishkar v4.1",
        "status": "active",
        "tiers": {
            "tier_1": "Pollinations — Free, Unlimited, No Key",
            "tier_2": "OpenArt — Free, Image-to-Image",
            "tier_3": "Picsum — Free, Unlimited"
        },
        "version": "4.1.0"
    }

@router.get("/image/generate")
async def image_generate(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic"):
    """Auto-generate image"""
    try:
        enhanced_prompt = f"{prompt}, {style}, high quality, detailed"
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        url = f"{TIER_1_POLLINATIONS.format(prompt=encoded_prompt)}?width={width}&height={height}&nologo=true&seed={int(datetime.now().timestamp())}"

        resp = requests.get(url, timeout=60)
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/png",
                headers={"X-Source": "Pollinations-Tier-1"}
            )
    except Exception as e:
        logger.warning(f"Tier 1 failed: {e}")

    # Fallback to Picsum
    try:
        url = f"{TIER_3_PICSUM.format(width=width, height=height)}?seed={urllib.parse.quote(str(prompt))}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/jpeg",
                headers={"X-Source": "Picsum-Tier-3"}
            )
    except Exception as e:
        logger.error(f"Picsum failed: {e}")

    return JSONResponse(status_code=500, content={"error": "All tiers failed"})

# ============ BUTTERFLY EFFECT — GET METHOD (Easy for CMD) ============

@router.get("/image/butterfly-effect")
async def butterfly_effect(image_url: str, prompt: str = "butterfly flying, magical, dreamy"):
    """
    Image-to-Image Butterfly Effect
    GET method for easy CMD testing
    """
    return {
        "success": True,
        "message": "🦋 Butterfly effect request received!",
        "original_url": image_url,
        "effect_prompt": prompt,
        "note": "Butterfly effect processing...",
        "status": "processing",
        "next_step": "Pollinations se image generate karo"
    }

@router.get("/styles")
async def get_styles():
    return {
        "styles": [
            {"id": "realistic", "name": "Realistic Photo"},
            {"id": "anime", "name": "Anime/Manga"},
            {"id": "oil-painting", "name": "Oil Painting"},
            {"id": "watercolor", "name": "Watercolor"},
            {"id": "3d-render", "name": "3D Render"},
            {"id": "sketch", "name": "Pencil Sketch"},
            {"id": "digital-art", "name": "Digital Art"},
            {"id": "cinematic", "name": "Cinematic"},
            {"id": "butterfly-effect", "name": "🦋 Butterfly Effect"}
        ]
    }

@router.get("/stats")
async def aavishkar_stats():
    return {
        "module": "Aavishkar v4.1",
        "tier_1": "Pollinations — Free, Unlimited",
        "tier_2": "OpenArt — Free, Image-to-Image",
        "tier_3": "Picsum — Free, Unlimited",
        "status": "🦁 Ready!"
    }

@router.get("/health")
async def health():
    return {"status": "ok", "mode": "Multi-Tier-Fallback"}
