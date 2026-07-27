from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .core import SOCIAL_AGENT, init_social_agent
import os

router = APIRouter(prefix="/api/social", tags=["Social Agent"])

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def _check_admin(request: Request):
    key = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    return key == ADMIN_API_KEY

@router.get("/")
async def social_status():
    if not SOCIAL_AGENT:
        return {"error": "Social agent not initialized"}
    return {
        "agent": "Singh Ji Social Agent v1.0",
        "status": "ACTIVE",
        **SOCIAL_AGENT.get_stats()
    }

@router.post("/generate")
async def generate_post(request: Request):
    """Manually trigger content generation"""
    if not SOCIAL_AGENT:
        return {"error": "Social agent not initialized"}
    data = await request.json()
    niche = data.get("niche")
    lang = data.get("lang", "hi")
    content = await SOCIAL_AGENT.generate_post_content(niche, lang)
    return {"generated": True, "content": content}

@router.post("/publish")
async def publish_now(request: Request):
    """Immediate publish to all platforms"""
    if not _check_admin(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    if not SOCIAL_AGENT:
        return {"error": "Social agent not initialized"}
    
    data = await request.json()
    platforms = data.get("platforms", ["facebook", "instagram"])
    niche = data.get("niche")
    
    result = await SOCIAL_AGENT.create_and_publish(platforms, niche)
    return result

@router.post("/queue")
async def queue_posts(request: Request):
    """Queue posts for today"""
    if not _check_admin(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    if not SOCIAL_AGENT:
        return {"error": "Social agent not initialized"}
    
    await SOCIAL_AGENT.schedule_daily_posts()
    return {"queued": True, "queue_size": len(SOCIAL_AGENT.content_queue)}

@router.get("/history")
async def post_history(limit: int = 10):
    if not SOCIAL_AGENT:
        return {"error": "Social agent not initialized"}
    return {
        "history": SOCIAL_AGENT.posted_history[-limit:],
        "total": len(SOCIAL_AGENT.posted_history)
    }
