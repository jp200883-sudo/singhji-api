import os
from datetime import datetime, timedelta
from supabase import create_client

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 7 din purani memory delete karo
MEMORY_RETENTION_DAYS = 7

async def handler(request):
    from fastapi import Request
    data = await request.json() if request.method == "POST" else {}
    action = data.get('action', 'status')
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    if action == 'store':
        # Memory store karo
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '')
        context = data.get('context', {})
        
        memory_data = {
            "user_id": user_id,
            "message": message,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=MEMORY_RETENTION_DAYS)).isoformat()
        }
        
        result = supabase.table('memories').insert(memory_data).execute()
        return {
            "status": "stored",
            "memory_id": result.data[0]['id'] if result.data else None,
            "expires_in": f"{MEMORY_RETENTION_DAYS} days",
            "timestamp": datetime.now().isoformat()
        }
    
    elif action == 'retrieve':
        # Memory retrieve karo (sirf 7 din ki)
        user_id = data.get('user_id', 'anonymous')
        cutoff_date = (datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)).isoformat()
        
        result = supabase.table('memories')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', cutoff_date)\
            .order('created_at', desc=True)\
            .execute()
        
        return {
            "status": "retrieved",
            "memories": result.data,
            "count": len(result.data),
            "retention": f"{MEMORY_RETENTION_DAYS} days",
            "timestamp": datetime.now().isoformat()
        }
    
    elif action == 'cleanup':
        # 7 din purani memory delete karo
        cutoff_date = (datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)).isoformat()
        
        result = supabase.table('memories')\
            .delete()\
            .lt('created_at', cutoff_date)\
            .execute()
        
        return {
            "status": "cleaned",
            "deleted_count": len(result.data) if result.data else 0,
            "older_than": f"{MEMORY_RETENTION_DAYS} days",
            "timestamp": datetime.now().isoformat()
        }
    
    elif action == 'auto_cleanup':
        # Auto cleanup schedule karo (har 24 ghante)
        # Ye Render ke background me chalega
        import asyncio
        asyncio.create_task(_auto_cleanup_loop(supabase))
        return {
            "status": "auto_cleanup_started",
            "interval": "24 hours",
            "retention": f"{MEMORY_RETENTION_DAYS} days",
            "timestamp": datetime.now().isoformat()
        }
    
    # Default status
    return {
        "module": "supabase_memory",
        "status": "active",
        "retention_policy": f"{MEMORY_RETENTION_DAYS} days",
        "supabase_connected": bool(SUPABASE_URL and SUPABASE_KEY),
        "actions": ["store", "retrieve", "cleanup", "auto_cleanup"],
        "note": "Memory auto-deletes after 7 days"
    }

async def _auto_cleanup_loop(supabase):
    """Har 24 ghante me purani memory delete karo"""
    while True:
        await asyncio.sleep(86400)  # 24 hours
        cutoff = (datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)).isoformat()
        try:
            result = supabase.table('memories').delete().lt('created_at', cutoff).execute()
            print(f"[AUTO_CLEANUP] Deleted {len(result.data)} old memories")
        except Exception as e:
            print(f"[AUTO_CLEANUP] Error: {e}")
