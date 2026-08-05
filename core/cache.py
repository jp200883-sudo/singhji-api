import time
from typing import Any, Optional

# ==========================================
# CACHE STORE – यही main में import होगा
# ==========================================
cache_store = {}

def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set cache with TTL"""
    cache_store[key] = {
        "value": value,
        "expiry": time.time() + ttl
    }

def cache_get(key: str) -> Optional[Any]:
    """Get cached value if not expired"""
    data = cache_store.get(key)
    if data and data["expiry"] > time.time():
        return data["value"]
    if key in cache_store:
        del cache_store[key]
    return None

def cache_clear() -> None:
    """Clear entire cache"""
    cache_store.clear()

def cache_delete(key: str) -> bool:
    """Delete specific cache key"""
    if key in cache_store:
        del cache_store[key]
        return True
    return False

def cache_stats() -> dict:
    """Get cache statistics"""
    total = len(cache_store)
    expired = sum(1 for v in cache_store.values() if v["expiry"] <= time.time())
    return {
        "total_keys": total,
        "expired_keys": expired,
        "active_keys": total - expired
    }
_cache_get = cache_get
_cache_set = cache_set
