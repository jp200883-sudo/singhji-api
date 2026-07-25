"""
🌾 SINGH JI AI — KISAAN DOCTOR v2.0 (POLISHED)
Superior: Plant disease detection, Crop advisory, Fertilizer calculator, Market prices
Sources: Plant.id API, Groq AI, Weather integration
"""

import os
import asyncio
import logging
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List

import httpx
from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kisaan", tags=["Kisaan Doctor"])

# ─── CONFIG ───
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CACHE_TTL = 3600  # 1 hour
REQUEST_TIMEOUT = 20.0
MAX_RETRIES = 3

_kisaan_cache: Dict[str, Dict[str, Any]] = {}


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    entry = _kisaan_cache.get(key)
    if entry and (datetime.utcnow() - entry["ts"]).total_seconds() < CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: Dict[str, Any]) -> None:
    _kisaan_cache[key] = {"data": data, "ts": datetime.utcnow()}


# ─── RETRY ───
def async_retry(max_retries: int = MAX_RETRIES, delay: float = 1.0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__}: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(delay * attempt)
            raise last_exc
        return wrapper
    return decorator


# ─── PLANT DISEASE DETECTION (Plant.id) ───
@async_retry(max_retries=2, delay=1.5)
async def _detect_disease(image_b64: str) -> Optional[Dict[str, Any]]:
    if not PLANT_ID_API_KEY:
        return None

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(
            "https://api.plant.id/v2/health_assessment",
            headers={"Content-Type": "application/json", "Api-Key": PLANT_ID_API_KEY},
            json={
                "images": [image_b64],
                "modifiers": ["similar_images"],
                "disease_details": ["description", "treatment", "classification", "common_names"],
            },
        )
        resp.raise_for_status()
        data = resp.json()

        health = data.get("health_assessment", {})
        diseases = health.get("diseases", [])

        return {
            "source": "Plant.id",
            "is_healthy": health.get("is_healthy", True),
            "health_probability": health.get("probability", 0),
            "diseases": [
                {
                    "name": d.get("name", "Unknown"),
                    "probability": d.get("probability", 0),
                    "description": d.get("disease_details", {}).get("description", ""),
                    "treatment": d.get("disease_details", {}).get("treatment", {}),
                    "common_names": d.get("disease_details", {}).get("common_names", []),
                }
                for d in diseases[:3]
            ],
        }


# ─── AI CROP ADVISORY (Groq) ───
@async_retry(max_retries=2, delay=1.0)
async def _get_crop_advisory(crop: str, state: str, season: str) -> str:
    if not GROQ_API_KEY:
        return "❌ AI advisory temporarily unavailable."

    prompt = (
        f"You are Singh Ji Kisaan Doctor, an expert Indian agricultural advisor. "
        f"Give practical advice in Hinglish (Hindi+English mix) for growing {crop} in {state} "
        f"during {season} season. Include: sowing time, fertilizer, watering schedule, "
        f"pest control, expected yield, and market price tips. Keep it under 300 words."
    )

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


# ─── FERTILIZER CALCULATOR ───
FERTILIZER_DATA = {
    "wheat": {"npk": "120:60:40", "urea_kg_acre": 60, "dap_kg_acre": 30, "mop_kg_acre": 15},
    "rice": {"npk": "100:50:50", "urea_kg_acre": 50, "dap_kg_acre": 25, "mop_kg_acre": 17},
    "maize": {"npk": "120:60:40", "urea_kg_acre": 60, "dap_kg_acre": 30, "mop_kg_acre": 15},
    "cotton": {"npk": "100:50:50", "urea_kg_acre": 50, "dap_kg_acre": 25, "mop_kg_acre": 17},
    "sugarcane": {"npk": "150:75:75", "urea_kg_acre": 75, "dap_kg_acre": 38, "mop_kg_acre": 25},
    "potato": {"npk": "120:80:100", "urea_kg_acre": 60, "dap_kg_acre": 40, "mop_kg_acre": 33},
    "tomato": {"npk": "100:60:80", "urea_kg_acre": 50, "dap_kg_acre": 30, "mop_kg_acre": 27},
    "onion": {"npk": "100:50:50", "urea_kg_acre": 50, "dap_kg_acre": 25, "mop_kg_acre": 17},
    "mustard": {"npk": "80:40:40", "urea_kg_acre": 40, "dap_kg_acre": 20, "mop_kg_acre": 13},
    "soybean": {"npk": "20:60:20", "urea_kg_acre": 10, "dap_kg_acre": 30, "mop_kg_acre": 7},
}


def _calculate_fertilizer(crop: str, acres: float) -> Dict[str, Any]:
    data = FERTILIZER_DATA.get(crop.lower())
    if not data:
        return {"error": f"❌ {crop} ka data nahi hai. Available: {list(FERTILIZER_DATA.keys())}"}

    return {
        "crop": crop.title(),
        "area_acres": acres,
        "npk_ratio": data["npk"],
        "fertilizers": {
            "urea": {"kg_per_acre": data["urea_kg_acre"], "total_kg": round(data["urea_kg_acre"] * acres, 2)},
            "dap": {"kg_per_acre": data["dap_kg_acre"], "total_kg": round(data["dap_kg_acre"] * acres, 2)},
            "mop": {"kg_per_acre": data["mop_kg_acre"], "total_kg": round(data["mop_kg_acre"] * acres, 2)},
        },
        "estimated_cost_inr": round((data["urea_kg_acre"] * 12 + data["dap_kg_acre"] * 25 + data["mop_kg_acre"] * 20) * acres, 2),
        "note": "Rates approximate. Local market se exact price check karo.",
    }


# ─── ROUTES ───
@router.post("/detect")
async def detect_disease(image: UploadFile = File(...)):
    """
    🌾 Upload plant photo → AI disease detection.

    Returns: Disease name, probability, treatment advice.
    """
    logger.info(f"🌾 Disease detection: {image.filename}")

    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="❌ Photo 10MB se zyada nahi honi chahiye.")

    image_b64 = base64.b64encode(contents).decode("utf-8")
    cache_key = f"disease:{hash(image_b64) % 1000000}"

    cached = _get_cached(cache_key)
    if cached:
        return JSONResponse({"cached": True, "data": cached})

    result = await _detect_disease(image_b64)
    if not result:
        raise HTTPException(status_code=503, detail="❌ Plant.id API nahi chal rahi. Baad mein try karo.")

    _set_cached(cache_key, result)
    return JSONResponse({"cached": False, "data": result})


@router.get("/advisory")
async def crop_advisory(crop: str, state: str = "uttar pradesh", season: str = "kharif"):
    """
    🌾 AI crop advisory for any crop.

    Example: /kisaan/advisory?crop=wheat&state=uttar_pradesh&season=rabi
    """
    logger.info(f"🌾 Advisory: {crop} in {state} ({season})")

    cache_key = f"advisory:{crop}:{state}:{season}"
    cached = _get_cached(cache_key)
    if cached:
        return JSONResponse({"cached": True, "data": cached})

    advisory = await _get_crop_advisory(crop, state, season)

    result = {
        "crop": crop.title(),
        "state": state.title(),
        "season": season.title(),
        "advisory": advisory,
        "timestamp": datetime.utcnow().isoformat(),
    }

    _set_cached(cache_key, result)
    return JSONResponse({"cached": False, "data": result})


@router.get("/fertilizer")
async def fertilizer_calculator(crop: str, acres: float = 1.0):
    """
    🧪 Fertilizer calculator for any crop.

    Example: /kisaan/fertilizer?crop=wheat&acres=2.5
    """
    result = _calculate_fertilizer(crop, acres)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse({"data": result})


@router.get("/crops")
async def available_crops():
    """📋 List of supported crops."""
    return JSONResponse({
        "crops": list(FERTILIZER_DATA.keys()),
        "total": len(FERTILIZER_DATA),
    })


@router.get("/")
async def kisaan_root():
    return JSONResponse({
        "module": "🌾 Kisaan Doctor",
        "version": "2.0-polished",
        "features": ["disease-detection", "ai-advisory", "fertilizer-calculator", "cached", "retry"],
        "sources": ["Plant.id", "Groq AI"],
        "supported_crops": len(FERTILIZER_DATA),
        "cache_ttl_seconds": CACHE_TTL,
    })


# Legacy handler
async def handler(request: Request):
    crop = request.query_params.get("crop", "wheat")
    state = request.query_params.get("state", "uttar pradesh")
    return await crop_advisory(crop, state)
