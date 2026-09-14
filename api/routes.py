# api/routes.py
import time
import asyncio
import base64
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

from core.config import (
    AVAILABLE_KEYS,
    OPENWEATHER_API_KEY,
    PLANT_ID_API,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    CEREBRAS_API_KEY,
    BHASHINI_USER_ID,
    BHASHINI_ULCA_API_KEY,
    BHASHINI_INFERENCE_API_KEY,
)
from core.database import SUPABASE_CLIENT
from core.cache import _cache_key, _cache_get, _cache_set
from core.memory import _memory_save, _memory_get
from core.swarm import SMART_SWARM
from core.scheduler import MASTER_SCHEDULER, USER_PREFERENCES
from utils.helpers import _calculate_tax, _b64_too_big, _check_admin_auth, MODULES

router = APIRouter()
logger = logging.getLogger(__name__)

HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client


# ==========================================
# स्टेटस
# ==========================================
@router.get("/status")
async def status():
    active = [n for n, i in MODULES.items() if i["active"]]
    return {
        "name": "Singh Ji AI Ultra v8.3",
        "total_modules": len(MODULES),
        "active_count": len(active),
        "active_modules": active,
        "agents": SMART_SWARM.get_status(),
        "apis": AVAILABLE_KEYS,
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "subscribers": len(USER_PREFERENCES),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/api/status")
async def api_status():
    return await status()


@router.get("/api/check")
async def api_check():
    from core.config import (
        OPENWEATHER_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, TELEGRAM_TOKEN,
        SUPABASE_URL, SUPABASE_SERVICE_KEY,
    )

    tests = {
        "OPENWEATHER": (f"https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={OPENWEATHER_API_KEY or ''}", {}, "GET"),
        "GROQ": ("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {GROQ_API_KEY or ''}"}, "GET"),
        "GEMINI": (f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY or ''}", {}, "GET"),
        "TELEGRAM": (f"https://api.telegram.org/bot{TELEGRAM_TOKEN or ''}/getMe", {}, "GET"),
        "SUPABASE": (f"{SUPABASE_URL or ''}/rest/v1/", {"apikey": SUPABASE_SERVICE_KEY or "", "Authorization": f"Bearer {SUPABASE_SERVICE_KEY or ''}"}, "GET"),
    }

    async def _check_one(name, url, headers):
        if not AVAILABLE_KEYS.get(name):
            return name, {"status": "MISSING", "code": None}
        try:
            start = time.time()
            r = await HTTP_CLIENT.get(url, headers=headers, timeout=10)
            elapsed = round((time.time() - start) * 1000, 2)
            if r.status_code in [200, 401, 403]:
                return name, {"status": "LIVE", "code": r.status_code, "ms": elapsed}
            return name, {"status": "ERROR", "code": r.status_code, "ms": elapsed}
        except Exception as e:
            return name, {"status": "FAIL", "error": str(e)[:50]}

    outcomes = await asyncio.gather(*(_check_one(n, u, h) for n, (u, h, m) in tests.items()))
    results = dict(outcomes)
    live = sum(1 for v in results.values() if v["status"] == "LIVE")
    return {"timestamp": datetime.now().isoformat(), "summary": {"live": live, "total": len(results)}, "results": results}


# ==========================================
# मौसम
# ==========================================
@router.get("/api/weather/{city}")
async def weather_city(city: str):
    cache_key = _cache_key("weather", city)
    cached = await _cache_get(cache_key)
    if cached:
        cached["source"] = "CACHE"
        return cached
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY missing"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = await HTTP_CLIENT.get(url, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            result = {
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "desc": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "source": "OPENWEATHER_LIVE",
            }
            await _cache_set(cache_key, result, 1800)
            return result
        return {"error": data.get("message", "Unknown error"), "code": resp.status_code}
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return {"error": str(e)}


# ==========================================
# मेमोरी
# ==========================================
@router.get("/api/memory/{key}")
async def memory_get(key: str):
    return await _memory_get(key)


@router.post("/api/memory/")
async def memory_save(request: Request):
    data = await request.json()
    key = data.get("key", str(int(time.time())))
    value = data.get("value", data)
    return await _memory_save(key, value)


# ==========================================
# टैक्स
# ==========================================
@router.post("/api/retirement/tax-calculate")
async def tax_calculate(request: Request):
    data = await request.json()
    income = data.get("income", 0)
    regime = data.get("regime", "new")
    deductions = data.get("deductions", 0)
    return _calculate_tax(income, regime, deductions)


# ==========================================
# स्वार्म
# ==========================================
@router.get("/api/swarm/status")
async def swarm_status():
    return SMART_SWARM.get_status()


@router.post("/api/swarm/sync")
async def swarm_sync():
    result = SMART_SWARM.sync(MODULES, AVAILABLE_KEYS)
    return {"synced": True, **result}


# ==========================================
# प्लांट ID
# ==========================================
@router.post("/api/plant/identify")
async def plant_identify(request: Request):
    if not PLANT_ID_API:
        return {"error": "PLANT_ID_API missing"}
    data = await request.json()
    image_b64 = data.get("image_base64", "")
    if not image_b64:
        return {"error": "image_base64 required"}
    if _b64_too_big(image_b64):
        return JSONResponse(status_code=413, content={"error": "Image too large (max 10MB)"})
    try:
        resp = await HTTP_CLIENT.post(
            "https://api.plant.id/v3/identification",
            params={"details": "url,common_names,description"},
            headers={"Api-Key": PLANT_ID_API, "Content-Type": "application/json"},
            json={"images": [image_b64]},
            timeout=30,
        )
        result = resp.json()
        suggestions = result.get("result", {}).get("classification", {}).get("suggestions", [])
        top = suggestions[0] if suggestions else None
        return {
            "status": "success",
            "is_plant": result.get("result", {}).get("is_plant", {}).get("binary"),
            "top_match": {
                "name": top.get("name"),
                "probability": top.get("probability"),
                "common_names": top.get("details", {}).get("common_names"),
            } if top else None,
            "all_suggestions": suggestions[:5],
            "source": "PLANT.ID_LIVE",
        }
    except Exception as e:
        logger.error(f"Plant identification error: {e}")
        return {"error": str(e)}


# ==========================================
# भाषिणी — ASR / अनुवाद / TTS
# ==========================================
BHASHINI_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"


def _bhashini_ulca_headers():
    return {
        "userID": BHASHINI_USER_ID,
        "ulcaApiKey": BHASHINI_ULCA_API_KEY,
        "Content-Type": "application/json",
    }


def _bhashini_inference_headers():
    return {
        "Authorization": BHASHINI_INFERENCE_API_KEY,
        "Content-Type": "application/json",
    }


async def _bhashini_call(payload, timeout=60):
    """पहले ULCA, फेल होने पर Inference।"""
    if BHASHINI_USER_ID and BHASHINI_ULCA_API_KEY:
        try:
            resp = await HTTP_CLIENT.post(
                BHASHINI_URL,
                headers=_bhashini_ulca_headers(),
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 200:
                return resp.json(), "ULCA"
        except Exception as e:
            logger.warning(f"Bhashini ULCA failed: {e}")

    if BHASHINI_INFERENCE_API_KEY:
        try:
            resp = await HTTP_CLIENT.post(
                BHASHINI_URL,
                headers=_bhashini_inference_headers(),
                json=payload,
                timeout=timeout,
            )
            return resp.json(), "INFERENCE"
        except Exception as e:
            logger.error(f"Bhashini inference failed: {e}")
            return {"error": str(e)}, "INFERENCE_FAILED"

    return {"error": "Bhashini credentials missing"}, "NONE"


@router.get("/api/bhashini/status")
async def bhashini_status():
    return {
        "ulca_configured": bool(BHASHINI_USER_ID and BHASHINI_ULCA_API_KEY),
        "inference_configured": bool(BHASHINI_INFERENCE_API_KEY),
        "user_id_set": bool(BHASHINI_USER_ID),
        "ulca_key_set": bool(BHASHINI_ULCA_API_KEY),
        "inference_key_set": bool(BHASHINI_INFERENCE_API_KEY),
    }


@router.post("/api/bhashini/translate")
async def bhashini_translate(request: Request):
    data = await request.json()
    text = (data.get("text") or "").strip()
    source = data.get("source", "en")
    target = data.get("target", "hi")
    if not text:
        return {"error": "text required"}

    payload = {
        "pipelineTasks": [{
            "taskType": "translation",
            "config": {"language": {"sourceLanguage": source, "targetLanguage": target}},
        }],
        "inputData": {"input": [{"source": text}]},
    }

    body, mode = await _bhashini_call(payload, timeout=45)
    if "error" in body and not body.get("pipelineResponse"):
        return JSONResponse(status_code=400, content=body)

    out = body.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("target")
    return {
        "status": "success",
        "mode": mode,
        "source_lang": source,
        "target_lang": target,
        "input": text,
        "output": out,
        "source": "BHASHINI_LIVE",
    }


@router.post("/api/bhashini/asr")
async def bhashini_asr(request: Request):
    data = await request.json()
    audio_b64 = data.get("audio_base64", "")
    lang = data.get("language", "hi")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    if _b64_too_big(audio_b64):
        return JSONResponse(status_code=413, content={"error": "Audio too large"})

    payload = {
        "pipelineTasks": [{
            "taskType": "asr",
            "config": {
                "language": {"sourceLanguage": lang},
                "audioFormat": "wav",
                "samplingRate": 16000,
            },
        }],
        "inputData": {"audio": [{"audioContent": audio_b64}]},
    }

    body, mode = await _bhashini_call(payload, timeout=60)
    text = body.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source")
    return {"status": "success", "mode": mode, "text": text, "lang": lang}


@router.post("/api/bhashini/tts")
async def bhashini_tts(request: Request):
    data = await request.json()
    text = (data.get("text") or "").strip()
    lang = data.get("language", "hi")
    gender = data.get("gender", "female")
    if not text:
        return {"error": "text required"}

    payload = {
        "pipelineTasks": [{
            "taskType": "tts",
            "config": {
                "language": {"sourceLanguage": lang},
                "gender": gender,
                "samplingRate": 8000,
            },
        }],
        "inputData": {"input": [{"source": text}]},
    }

    body, mode = await _bhashini_call(payload, timeout=60)
    audio_b64 = body.get("pipelineResponse", [{}])[0].get("audio", [{}])[0].get("audioContent")
    if not audio_b64:
        return {"error": "No audio returned", "raw": body, "mode": mode}
    return {"status": "success", "mode": mode, "audio_base64": audio_b64, "format": "wav"}
