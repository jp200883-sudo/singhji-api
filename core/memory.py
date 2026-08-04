from core.database import SUPABASE_CLIENT
from core.config import MAX_MEMORY_SIZE
from datetime import datetime

MEMORY_STORE = {}

def _check_memory_limit():
    if len(MEMORY_STORE) > MAX_MEMORY_SIZE:
        keys_to_remove = list(MEMORY_STORE.keys())[:int(MAX_MEMORY_SIZE * 0.2)]
        for k in keys_to_remove:
            del MEMORY_STORE[k]

def _memory_save_sync(key, value, table="memory_store"):
    if SUPABASE_CLIENT:
        try:
            SUPABASE_CLIENT.table(table).upsert({
                "key": key,
                "value": value,
                "updated_at": datetime.now().isoformat()
            }).execute()
            return {"saved": True, "store": "supabase", "key": key}
        except Exception:
            pass
    _check_memory_limit()
    MEMORY_STORE[key] = value
    return {"saved": True, "store": "ram", "key": key}

async def _memory_save(key, value, table="memory_store"):
    from fastapi.concurrency import run_in_threadpool
    return await run_in_threadpool(_memory_save_sync, key, value, table)

def _memory_get_sync(key, table="memory_store"):
    if SUPABASE_CLIENT:
        try:
            resp = SUPABASE_CLIENT.table(table).select("*").eq("key", key).execute()
            if resp.data:
                return {"key": key, "data": resp.data[0]["value"], "exists": True, "store": "supabase"}
        except Exception:
            pass
    if key in MEMORY_STORE:
        return {"key": key, "data": MEMORY_STORE[key], "exists": True, "store": "ram"}
    return {"key": key, "data": None, "exists": False}

async def _memory_get(key, table="memory_store"):
    from fastapi.concurrency import run_in_threadpool
    return await run_in_threadpool(_memory_get_sync, key, table)
