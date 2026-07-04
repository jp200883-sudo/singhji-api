# modules/supabase_memory/handler.py — FULL UPGRADE

import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def handler(request):
    body = await request.json()
    action = body.get("action")
    
    if action == "save_user":
        # User data save
        data = supabase.table("users").insert(body["data"]).execute()
        return {"success": True, "data": data}
    
    elif action == "get_user":
        # User data fetch
        data = supabase.table("users").select("*").eq("id", body["user_id"]).execute()
        return {"success": True, "data": data}
    
    elif action == "save_chat":
        # Chat history
        data = supabase.table("chats").insert(body["data"]).execute()
        return {"success": True}
    
    elif action == "get_chat_history":
        # Chat history fetch
        data = supabase.table("chats").select("*").eq("user_id", body["user_id"]).execute()
        return {"success": True, "data": data}
    
    elif action == "save_schedule":
        # Schedule preferences
        data = supabase.table("schedules").insert(body["data"]).execute()
        return {"success": True}
    
    elif action == "get_schedule":
        # User schedule
        data = supabase.table("schedules").select("*").eq("user_id", body["user_id"]).execute()
        return {"success": True, "data": data}
    
    elif action == "analytics":
        # Usage analytics
        data = supabase.table("analytics").select("*").execute()
        return {"success": True, "data": data}
