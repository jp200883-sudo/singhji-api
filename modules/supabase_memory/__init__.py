# modules/supabase_memory.py — Singh Ji AI Ultra v5.0

from fastapi import APIRouter
import os
import json

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

MEMORY_STORE = {}

@router.get("/")
def memory_root():
    return {
        "module": "supabase_memory",
        "status": "✅ OK",
        "supabase_url_set": bool(SUPABASE_URL),
        "supabase_key_set": bool(SUPABASE_KEY),
        "mode": "supabase" if SUPABASE_URL else "local_memory"
    }

@router.get("/health")
def memory_health():
    return {
        "module": "supabase_memory",
        "status": "✅ OK",
        "supabase_url_set": bool(SUPABASE_URL),
        "supabase_key_set": bool(SUPABASE_KEY)
    }

@router.post("/save")
async def save_memory(user_id: str, key: str, value: dict):
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
            pass
    
    if user_id not in MEMORY_STORE:
        MEMORY_STORE[user_id] = {}
    MEMORY_STORE[user_id][key] = value
    return {"ok": True, "supabase": False, "mode": "local_memory", "user_id": user_id, "key": key}

@router.get("/get")
async def get_memory(user_id: str, key: str = None):
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
    
    user_mem = MEMORY_STORE.get(user_id, {})
    if key:
        return {"ok": True, "supabase": False, "mode": "local_memory", "value": user_mem.get(key)}
    return {"ok": True, "supabase": False, "mode": "local_memory", "all_memory": user_mem}

@router.delete("/delete")
async def delete_memory(user_id: str, key: str = None):
    if user_id in MEMORY_STORE:
        if key:
            MEMORY_STORE[user_id].pop(key, None)
        else:
            MEMORY_STORE[user_id] = {}
    return {"ok": True, "deleted": True}

@router.get("/list-users")
async def list_users():
    return {"ok": True, "users": list(MEMORY_STORE.keys()), "count": len(MEMORY_STORE)}
