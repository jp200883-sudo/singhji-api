# modules/supabase_memory.py — Singh Ji AI Ultra v5.0

from fastapi import APIRouter
from datetime import datetime
import os
import json
import pytz

router = APIRouter()

IST = pytz.timezone('Asia/Kolkata')

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

MEMORY_STORE = {}

# ====== EXISTING MEMORY FUNCTIONS (as-is) ======

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


# ====== NEW: NEWS CACHE FUNCTIONS (Auto-News Bot) ======

def store_news(category: str, language: str, articles: list, source: str = "auto-scheduler"):
    """News articles ko Supabase me store karo — Auto-News Bot ke liye"""
    timestamp = datetime.now(IST).isoformat()
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            
            data = {
                "category": category,
                "language": language,
                "articles": json.dumps(articles),
                "source": source,
                "timestamp": timestamp,
                "hour_slot": datetime.now(IST).hour
            }
            
            result = supabase.table("news_cache").insert(data).execute()
            return {"ok": True, "supabase": True, "stored": len(articles), "timestamp": timestamp}
        except Exception as e:
            pass
    
    # Local fallback
    cache_key = f"news_{category}_{language}_{datetime.now(IST).strftime('%Y%m%d_%H')}"
    if "news_cache" not in MEMORY_STORE:
        MEMORY_STORE["news_cache"] = {}
    MEMORY_STORE["news_cache"][cache_key] = {
        "category": category,
        "language": language,
        "articles": articles,
        "timestamp": timestamp,
        "source": source
    }
    return {"ok": True, "supabase": False, "mode": "local_memory", "stored": len(articles)}


def get_latest_news(category: str = "india", language: str = "hi", limit: int = 10):
    """Latest news from cache — Frontend ke liye"""
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            
            result = supabase.table("news_cache")\
                .select("*")\
                .eq("category", category)\
                .eq("language", language)\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            
            if result.data:
                # Parse JSON articles
                for item in result.data:
                    if isinstance(item.get("articles"), str):
                        item["articles"] = json.loads(item["articles"])
                return {"ok": True, "supabase": True, "data": result.data}
        except Exception as e:
            pass
    
    # Local fallback
    local_news = []
    for key, value in MEMORY_STORE.get("news_cache", {}).items():
        if value.get("category") == category and value.get("language") == language:
            local_news.append(value)
    
    local_news.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"ok": True, "supabase": False, "mode": "local_memory", "data": local_news[:limit]}


def get_news_by_hour(hour: int, category: str = "india"):
    """Specific hour ki news — Scheduler ke liye"""
    
    today = datetime.now(IST).strftime("%Y-%m-%d")
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            
            result = supabase.table("news_cache")\
                .select("*")\
                .eq("category", category)\
                .eq("hour_slot", hour)\
                .gte("timestamp", f"{today}T00:00:00")\
                .order("timestamp", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                for item in result.data:
                    if isinstance(item.get("articles"), str):
                        item["articles"] = json.loads(item["articles"])
                return {"ok": True, "data": result.data[0]}
        except Exception as e:
            pass
    
    return {"ok": False, "error": "No news found for this hour"}


def cleanup_old_news(days: int = 7):
    """Purani news delete karo — Storage bachao"""
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            
            cutoff = (datetime.now(IST) - __import__('datetime').timedelta(days=days)).isoformat()
            
            result = supabase.table("news_cache")\
                .delete()\
                .lt("timestamp", cutoff)\
                .execute()
            
            return {"ok": True, "deleted": len(result.data)}
        except Exception as e:
            pass
    
    return {"ok": True, "message": "Cleanup skipped (local mode)"}


# ====== API ROUTES FOR NEWS CACHE ======

@router.get("/news/latest")
async def api_latest_news(category: str = "india", language: str = "hi", limit: int = 10):
    """Frontend ke liye — Latest cached news"""
    return get_latest_news(category, language, limit)

@router.get("/news/hour")
async def api_news_by_hour(hour: int, category: str = "india"):
    """Specific hour ki news"""
    return get_news_by_hour(hour, category)

@router.post("/news/cleanup")
async def api_cleanup_news(days: int = 7):
    """Old news cleanup"""
    return cleanup_old_news(days)

@router.get("/news/stats")
async def api_news_stats():
    """News cache statistics"""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)
            
            total = supabase.table("news_cache").select("count", count="exact").execute()
            today = datetime.now(IST).strftime("%Y-%m-%d")
            today_count = supabase.table("news_cache")\
                .select("count", count="exact")\
                .gte("timestamp", f"{today}T00:00:00")\
                .execute()
            
            return {
                "ok": True,
                "total_cached": total.count,
                "today_cached": today_count.count,
                "categories": ["india", "world", "business", "sports"]
            }
        except Exception as e:
            pass
    
    local_count = len(MEMORY_STORE.get("news_cache", {}))
    return {"ok": True, "total_cached": local_count, "mode": "local_memory"}
