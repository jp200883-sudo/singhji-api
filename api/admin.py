# api/admin.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from core.swarm import SMART_SWARM
from core.scheduler import MASTER_SCHEDULER, USER_PREFERENCES
from core.memory import MEMORY_STORE
from core.config import AVAILABLE_KEYS
from utils.helpers import _check_admin_auth, MODULES

router = APIRouter()

@router.get("/")
async def admin_root(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return {
        "module": "Admin Panel",
        "total_modules": len(MODULES),
        "active_modules": [n for n, i in MODULES.items() if i["active"]],
        "agents": SMART_SWARM.get_status(),
        "apis": AVAILABLE_KEYS,
        "users": len(USER_PREFERENCES),
        "memory_ram": len(MEMORY_STORE),
        "scheduler": MASTER_SCHEDULER.get_status() if MASTER_SCHEDULER else {"running": False},
        "timestamp": datetime.now().isoformat()
    }

@router.post("/broadcast")
async def admin_broadcast(request: Request):
    if not _check_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    data = await request.json()
    message = data.get("message", "")
    if MASTER_SCHEDULER:
        await MASTER_SCHEDULER._broadcast_with_rate_limit(f"Admin Broadcast\n\n{message}")
        return {"broadcast": True, "sent_to": len(USER_PREFERENCES)}
    return {"error": "Scheduler not initialized"}
