# modules/supabase_memory/__init__.py — Singh Ji AI Ultra v5.0
# This file = handler.py (Render free tier fix)

from fastapi import APIRouter
import os
import json

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# In-memory fallback (until Supabase is connected)
MEMORY_STORE = {}

@router.get("/health")
def memory_health():
    return {
        "module": "supabase_memory",
        "status": "✅ OK",
        "supabase_url_set": bool(SUPABASE_URL),
        "supabase_key_set": bool(SUPABASE_KEY),
        "mode": "supabase" if SUPABASE_URL else "local_memory"
    }

@router.get("/info")
def memory_info():
    return {
        "module": "supabase_memory",
        "version": "1.0.0",
        "features": [
            "User memory storage",
            "Conversation history",
            "Preference tracking",
            "Cross-session persistence"
        ],
        "setup": "Set SUPABASE_URL and SUPABASE_KEY in Render Environment Variables"
    }

@router.post("/save")
async def save_memory(user_id: str, key: str, value: dict):
    """Save memory for a user"""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            data = {
                "user_id": user_id,
                "key": key,
                "value": json.dumps(value),
                "updated_at": "now()"
            }
            result = supabase.table("memories").upsert(data).execute()
            return {"ok": True, "supabase": True, "result": result.data}
        except Exception as e:
            # Fallback to local
            pass
    
    # Local memory fallback
    if user_id not in MEMORY_STORE:
        MEMORY_STORE[user_id] = {}
    MEMORY_STORE[user_id][key] = value
    return {
        "ok": True,
        "supabase": False,
        "mode": "local_memory",
        "user_id": user_id,
        "key": key,
        "value": value
    }

@router.get("/get")
async def get_memory(user_id: str, key: str = None):
    """Get memory for a user"""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            if key:
                result = supabase.table("memories").select("*").eq("user_id", user_id).eq("key", key).execute()
            else:
                result = supabase.table("memories").select("*").eq("user_id", user_id).execute()
            return {"ok": True, "supabase": True, "data": result.data}
        except Exception as e:
            pass
    
    # Local fallback
    user_mem = MEMORY_STORE.get(user_id, {})
    if key:
        return {
            "ok": True,
            "supabase": False,
            "mode": "local_memory",
            "user_id": user_id,
            "key": key,
            "value": user_mem.get(key)
        }
    return {
        "ok": True,
        "supabase": False,
        "mode": "local_memory",
        "user_id": user_id,
        "all_memory": user_mem
    }

@router.delete("/delete")
async def delete_memory(user_id: str, key: str = None):
    """Delete memory for a user"""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            query = supabase.table("memories").delete().eq("user_id", user_id)
            if key:
                query = query.eq("key", key)
            result = query.execute()
            return {"ok": True, "supabase": True, "deleted": result.data}
        except Exception as e:
            pass
    
    # Local fallback
    if user_id in MEMORY_STORE:
        if key:
            MEMORY_STORE[user_id].pop(key, None)
        else:
            MEMORY_STORE[user_id] = {}
    return {"ok": True, "supabase": False, "mode": "local_memory", "deleted": True}

@router.get("/list-users")
async def list_users():
    """List all users with memory (local mode only)"""
    return {
        "ok": True,
        "users": list(MEMORY_STORE.keys()),
        "count": len(MEMORY_STORE)
    }
