import hashlib
import time
from datetime import datetime, timedelta
from core.database import SUPABASE_CLIENT
from core.config import CACHE_TTL

def _cache_key(prefix, *args):
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()

def _cache_get_sync(key):
    if SUPABASE_CLIENT:
        try:
            resp = SUPABASE_CLIENT.table("cache_store").select("*").eq("key", key).execute()
            if resp.data:
                entry = resp.data[0]
                if entry.get("expires_at") and datetime.now().isoformat() < entry["expires_at"]:
                    return entry["value"]
                SUPABASE_CLIENT.table("cache_store").delete().eq("key", key).execute()
        except Exception:
            pass
    return None

async def _cache_get(key):
    from fastapi.concurrency import run_in_threadpool
    return await run_in_threadpool(_cache_get_sync, key)

def _cache_set_sync(key, value, ttl=None):
    if not SUPABASE_CLIENT:
        return
    ttl = ttl or CACHE_TTL["default"]
    expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
    try:
        SUPABASE_CLIENT.table("cache_store").upsert({
            "key": key,
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now().isoformat()
        }).execute()
    except Exception:
        pass

async def _cache_set(key, value, ttl=None):
    from fastapi.concurrency import run_in_threadpool
    await run_in_threadpool(_cache_set_sync, key, value, ttl)
