"""
🦁 Singh Ji AI — OAuth Connector Handler
Social Media OAuth Management
"""

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
import os
import json
import logging
from datetime import datetime, timedelta

# Import Config properly
from .config import Config, get_config, PlatformConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth")

# Token storage (in-memory, replace with Redis/Supabase for production)
_token_store = {}

def _get_stored_token(platform: str) -> dict:
    """Get stored token for platform"""
    return _token_store.get(platform, {})

def _store_token(platform: str, token_data: dict):
    """Store token for platform"""
    _token_store[platform] = {
        **token_data,
        "stored_at": datetime.now().isoformat(),
    }

# ═══════════════════════════════════════════════════════
# 🦁 ROUTES
# ═══════════════════════════════════════════════════════

@router.get("/")
async def oauth_root():
    """OAuth connector status"""
    config = get_config()
    enabled = config.get_enabled_platforms()
    return {
        "module": "OAuth Connector",
        "status": "active",
        "platforms_total": len(config.platforms),
        "platforms_enabled": len(enabled),
        "platforms": {k: {"name": v.name, "enabled": v.enabled} for k, v in config.platforms.items()},
    }

@router.get("/{platform}/auth-url")
async def oauth_auth_url(platform: str):
    """Get OAuth authorization URL for platform"""
    config = get_config()
    plat = config.get_platform(platform)

    if not plat:
        return JSONResponse({"error": f"Platform '{platform}' not found"}, status_code=404)

    if not plat.enabled:
        return JSONResponse({"error": f"Platform '{platform}' not enabled"}, status_code=400)

    client_id = os.getenv(plat.client_id_env, "")
    if not client_id:
        return JSONResponse({"error": f"Client ID not set for {platform}"}, status_code=500)

    scopes = "%20".join(plat.scopes)
    auth_url = f"{plat.auth_url}?client_id={client_id}&redirect_uri={plat.redirect_uri}&scope={scopes}&response_type=code&state=singhji_{platform}"

    return {
        "platform": platform,
        "auth_url": auth_url,
        "scopes": plat.scopes,
    }

@router.get("/{platform}/callback")
async def oauth_callback(platform: str, code: str = None, error: str = None, state: str = None):
    """OAuth callback handler"""
    if error:
        return JSONResponse({"error": error, "platform": platform}, status_code=400)

    if not code:
        return JSONResponse({"error": "Authorization code missing"}, status_code=400)

    config = get_config()
    plat = config.get_platform(platform)

    if not plat:
        return JSONResponse({"error": "Platform not found"}, status_code=404)

    # Store authorization code (exchange for token in production)
    _store_token(platform, {
        "code": code,
        "state": state,
        "platform": platform,
        "status": "authorized",
    })

    logger.info(f"✅ OAuth authorized for {platform}")

    return {
        "status": "success",
        "platform": platform,
        "message": f"{plat.name} authorized successfully",
        "code_received": bool(code),
    }

@router.get("/{platform}/status")
async def oauth_status(platform: str):
    """Check OAuth status for platform"""
    token = _get_stored_token(platform)
    config = get_config()
    plat = config.get_platform(platform)

    return {
        "platform": platform,
        "name": plat.name if plat else platform,
        "enabled": plat.enabled if plat else False,
        "authorized": bool(token.get("code")),
        "token_stored_at": token.get("stored_at"),
    }

@router.post("/{platform}/disconnect")
async def oauth_disconnect(platform: str):
    """Disconnect OAuth for platform"""
    if platform in _token_store:
        del _token_store[platform]
        logger.info(f"⛔ OAuth disconnected for {platform}")

    return {"status": "disconnected", "platform": platform}

@router.get("/status/all")
async def oauth_all_status():
    """Get status of all platforms"""
    config = get_config()
    result = {}

    for key, plat in config.platforms.items():
        token = _get_stored_token(key)
        result[key] = {
            "name": plat.name,
            "enabled": plat.enabled,
            "authorized": bool(token.get("code")),
            "client_id_set": bool(os.getenv(plat.client_id_env, "")),
        }

    return {"platforms": result, "total": len(result), "authorized": sum(1 for v in result.values() if v["authorized"])}

# ═══════════════════════════════════════════════════════
# 🦁 HANDLER (for auto-loader compatibility)
# ═══════════════════════════════════════════════════════

async def handler(request: Request):
    """Fallback handler for auto-loader"""
    return {"module": "OAuth Connector", "status": "active", "note": "Use /oauth/ routes"}
