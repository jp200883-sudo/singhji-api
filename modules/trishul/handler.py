"""
🦁 TRISHUL MEMORY API
Singh Ji AI — Memory Endpoints (No mem0!)
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import importlib.util
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🦁 SEEDHA FILE-PATH SE memory.py LOAD KARO
# (relative import ".memory" isliye nahi use kiya kyunki
#  main.py dynamic loader se yeh module sys.path ke bahar
#  load hota hai — isse ModuleNotFoundError aata tha)
# ═══════════════════════════════════════════════════════
_here = os.path.dirname(os.path.abspath(__file__))
_mem_path = os.path.join(_here, "memory.py")
_spec = importlib.util.spec_from_file_location("trishul_memory_module", _mem_path)
_mem_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mem_module)
trishul = _mem_module.trishul

router = APIRouter()


@router.get("/")
async def memory_home():
    return {
        "system": "🧠 Trishul Memory",
        "version": "1.0.0",
        "status": "active",
        "engine": "Supabase/SQLite (Khud ka!)",
        "features": ["store", "recall", "search", "agent_context", "forget"]
    }


@router.post("/store")
async def store_memory(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        message = data.get("message", "")
        agent_id = data.get("agent_id", "general")
        metadata = data.get("metadata", {})

        success = trishul.store(user_id, message, agent_id, metadata)

        return {
            "status": "याद रखा!" if success else "फेल!",
            "user_id": user_id,
            "agent_id": agent_id
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/recall")
async def recall_memory(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        limit = data.get("limit", 10)

        memories = trishul.recall(user_id, limit)

        return {
            "user_id": user_id,
            "count": len(memories),
            "memories": memories
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/search")
async def search_memory(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        query = data.get("query", "")
        limit = data.get("limit", 5)

        results = trishul.search(user_id, query, limit)

        return {
            "user_id": user_id,
            "query": query,
            "results": results
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/agent-context")
async def agent_context(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        agent_id = data.get("agent_id", "general")

        context = trishul.get_agent_context(user_id, agent_id)

        return {
            "user_id": user_id,
            "agent_id": agent_id,
            "context": context
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/forget")
async def forget_memory(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")

        success = trishul.forget_user(user_id)

        return {
            "status": "भूल गया!" if success else "फेल!",
            "user_id": user_id
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ═══════════════════════════════════════════════════════
# 🦁 main.py ke load_module() ko handler bhi chahiye
# (agar router na mile to yeh fallback ban sake)
# ═══════════════════════════════════════════════════════
async def handler(request: Request):
    return await memory_home()
