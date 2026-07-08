"""
🦁 TRISHUL MEMORY API
Singh Ji AI — Memory Endpoints (No mem0!)
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .memory import trishul
import logging

logger = logging.getLogger(__name__)
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
