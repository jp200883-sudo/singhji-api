"""
🦁 AAVISHKAR v2.0 — Hybrid Image Generator
Tier 1: ZSky AI (Superior Quality, Unlimited, No Key)
Tier 2: Pollinations.ai (Good Quality, Unlimited, No Key)
Tier 3: Picsum (Placeholder, Instant, No Key)
"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import base64
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/aavishkar", tags=["aavishkar"])

# ═══════════════════════════════════════════════════════
# 🦁 HYBRID IMAGE APIS
# ═══════════════════════════════════════════════════════

TIER_1_ZSKY = "https://image.zsky.ai/api/v1/generate"  # Superior
TIER_2_POLLINATIONS = "https://image.pollinations.ai/prompt/{prompt}"  # Good
TIER_3_PICSUM = "https://picsum.photos/{width}/{height}"  # Placeholder

# ═══════════════════════════════════════════════════════
# 🦁 ROUTES
# ═══════════════════════════════════════════════════════

@router.get("/")
async def aavishkar_root():
    return {
        "module": "🦁 Aavishkar v2.0 — Hybrid Image AI",
        "status": "active",
        "tiers": {
            "tier_1": "ZSky AI — Superior Quality (Unlimited, No Key)",
            "tier_2": "Pollinations — Good Quality (Unlimited, No Key)",
            "tier_3": "Picsum — Placeholder (Instant, No Key)"
        },
        "features": [
            "Text → Image (3-Tier Hybrid)",
            "Hindi/English Prompts",
            "8 Art Styles",
            "Auto-Fallback",
            "Unlimited Free Generations"
        ],
        "version": "2.0.0"
    }

# ═══════════════════════════════════════════════════════
# 🖼️ TIER 1: ZSKY AI — Superior Quality
# ═══════════════════════════════════════════════════════

@router.get("/image/zsky")
async def image_zsky(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic"):
    """
    TIER 1: ZSky AI — Best quality, unlimited, no key
    """
    try:
        enhanced_prompt = f"{prompt}, {style}, high quality, detailed, 4k, masterpiece"
        
        # ZSky AI API call
        zsky_url = f"https://image.zsky.ai/api/v1/generate?prompt={requests.utils.quote(enhanced_prompt)}&width={width}&height={height}"
        
        resp = requests.get(zsky_url, timeout=60)
        
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/png",
                headers={"X-Source": "ZSky-AI-Tier-1"}
            )
        
    except Exception as e:
        logger.warning(f"ZSky failed: {e}")
    
    # Auto-fallback to Tier 2
    return await image_pollinations(prompt, width, height, style)

# ═══════════════════════════════════════════════════════
# 🖼️ TIER 2: POLLINATIONS — Good Quality
# ═══════════════════════════════════════════════════════

@router.get("/image/pollinations")
async def image_pollinations(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic"):
    """
    TIER 2: Pollinations.ai — Good quality, unlimited, no key
    """
    try:
        enhanced_prompt = f"{prompt}, {style}, high quality, detailed"
        
        pollinations_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced_prompt)}?width={width}&height={height}&nologo=true&seed={datetime.now().timestamp()}"
        
        resp = requests.get(pollinations_url, timeout=60)
        
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/png",
                headers={"X-Source": "Pollinations-Tier-2"}
            )
        
    except Exception as e:
        logger.warning(f"Pollinations failed: {e}")
    
    # Auto-fallback to Tier 3
    return await image_picsum(width, height, prompt)

# ═══════════════════════════════════════════════════════
# 🖼️ TIER 3: PICSUM — Placeholder
# ═══════════════════════════════════════════════════════

@router.get("/image/picsum")
async def image_picsum(width: int = 1024, height: int = 1024, seed: str = "singhji"):
    """
    TIER 3: Picsum — Instant placeholder, unlimited, no key
    """
    try:
        picsum_url = f"https://picsum.photos/seed/{requests.utils.quote(str(seed))}/{width}/{height}"
        
        resp = requests.get(picsum_url, timeout=10)
        
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/jpeg",
                headers={"X-Source": "Picsum-Tier-3"}
            )
        
    except Exception as e:
        logger.error(f"Picsum failed: {e}")
    
    return JSONResponse(
        status_code=500,
        content={"error": "All tiers failed", "trishul_status": "❌ Image generation unavailable"}
    )

# ═══════════════════════════════════════════════════════
# 🎯 SMART HYBRID — Auto Select Best Available
# ═══════════════════════════════════════════════════════

@router.get("/image/generate")
async def image_generate_smart(prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic", tier: int = 0):
    """
    SMART HYBRID: Auto-select best tier
    tier=0: Auto (ZSky → Pollinations → Picsum)
    tier=1: Force ZSky
    tier=2: Force Pollinations
    tier=3: Force Picsum
    """
    
    # Force tier selection
    if tier == 1:
        return await image_zsky(prompt, width, height, style)
    elif tier == 2:
        return await image_pollinations(prompt, width, height, style)
    elif tier == 3:
        return await image_picsum(width, height, prompt)
    
    # Auto mode: Try ZSky first
    try:
        enhanced_prompt = f"{prompt}, {style}, high quality, detailed, 4k, masterpiece"
        zsky_url = f"https://image.zsky.ai/api/v1/generate?prompt={requests.utils.quote(enhanced_prompt)}&width={width}&height={height}"
        
        resp = requests.get(zsky_url, timeout=30)
        
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/png",
                headers={"X-Source": "ZSky-AI-Tier-1", "X-Prompt": prompt}
            )
        
    except Exception as e:
        logger.warning(f"ZSky auto-fallback: {e}")
    
    # Fallback to Pollinations
    try:
        enhanced_prompt = f"{prompt}, {style}, high quality, detailed"
        pollinations_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced_prompt)}?width={width}&height={height}&nologo=true"
        
        resp = requests.get(pollinations_url, timeout=30)
        
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="image/png",
                headers={"X-Source": "Pollinations-Tier-2", "X-Prompt": prompt}
            )
        
    except Exception as e:
        logger.warning(f"Pollinations auto-fallback: {e}")
    
    # Final fallback to Picsum
    return await image_picsum(width, height, prompt)

# ═══════════════════════════════════════════════════════
# 🎨 STYLES
# ═══════════════════════════════════════════════════════

@router.get("/styles")
async def get_styles():
    return {
        "styles": [
            {"id": "realistic", "name": "Realistic Photo", "tier": "all"},
            {"id": "anime", "name": "Anime/Manga", "tier": "all"},
            {"id": "oil-painting", "name": "Oil Painting", "tier": "tier1-2"},
            {"id": "watercolor", "name": "Watercolor", "tier": "all"},
            {"id": "3d-render", "name": "3D Render", "tier": "tier1-2"},
            {"id": "sketch", "name": "Pencil Sketch", "tier": "all"},
            {"id": "digital-art", "name": "Digital Art", "tier": "all"},
            {"id": "cinematic", "name": "Cinematic", "tier": "tier1-2"},
            {"id": "fantasy", "name": "Fantasy Art", "tier": "tier1-2"},
            {"id": "portrait", "name": "Portrait", "tier": "all"}
        ],
        "trishul_status": "🎨 10 styles loaded!"
    }

# ═══════════════════════════════════════════════════════
# 📊 STATS
# ═══════════════════════════════════════════════════════

@router.get("/stats")
async def aavishkar_stats():
    return {
        "module": "Aavishkar v2.0",
        "tier_1": "ZSky AI — Unlimited, No Key",
        "tier_2": "Pollinations — Unlimited, No Key",
        "tier_3": "Picsum — Unlimited, No Key",
        "total_free_generations": "UNLIMITED",
        "trishul_status": "🦁 Aavishkar ready!"
    }
