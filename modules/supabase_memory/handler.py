# modules/supabase_memory/handler.py — FULL UPGRADE
import os
from typing import Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("आरंभ में Supabase जोड़ने में त्रुटि:", str(e))
        supabase = None
else:
    print("चेतावनी: SUPABASE_URL या SUPABASE_KEY व्यवस्था में मौजूद नहीं है")


def _ok(data=None):
    return {"success": True, "data": data}


def _fail(message, code=400):
    return {"success": False, "error": message, "code": code}


async def handler(request):
    if supabase is None:
        return _fail("Supabase जुड़ाव उपलब्ध नहीं है — env वैरिएबल जाँचें", 500)

    try:
        body = await request.json()
    except Exception:
        return _fail("अनुरोध का ढांचा गलत है (JSON नहीं मिला)", 400)

    action = body.get("action")
    if not action:
        return _fail("action क्षेत्र आवश्यक है", 400)

    try:
        if action == "save_user":
            payload = body.get("data")
            if not payload:
                return _fail("data क्षेत्र आवश्यक है", 400)
            result = supabase.table("users").insert(payload).execute()
            return _ok(result.data)

        elif action == "get_user":
            user_id = body.get("user_id")
            if not user_id:
                return _fail("user_id आवश्यक है", 400)
            result = supabase.table("users").select("*").eq("id", user_id).execute()
            return _ok(result.data)

        elif action == "save_chat":
            payload = body.get("data")
            if not payload:
                return _fail("data क्षेत्र आवश्यक है", 400)
            result = supabase.table("chats").insert(payload).execute()
            return _ok(result.data)

        elif action == "get_chat_history":
            user_id = body.get("user_id")
            if not user_id:
                return _fail("user_id आवश्यक है", 400)
            limit = int(body.get("limit", 50))
            result = (
                supabase.table("chats")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return _ok(result.data)

        elif action == "save_schedule":
            payload = body.get("data")
            if not payload:
                return _fail("data क्षेत्र आवश्यक है", 400)
            result = supabase.table("schedules").insert(payload).execute()
            return _ok(result.data)

        elif action == "get_schedule":
            user_id = body.get("user_id")
            if not user_id:
                return _fail("user_id आवश्यक है", 400)
            result = supabase.table("schedules").select("*").eq("user_id", user_id).execute()
            return _ok(result.data)

        elif action == "analytics":
            limit = int(body.get("limit", 100))
            result = supabase.table("analytics").select("*").limit(limit).execute()
            return _ok(result.data)

        elif action == "delete_user":
            user_id = body.get("user_id")
            if not user_id:
                return _fail("user_id आवश्यक है", 400)
            result = supabase.table("users").delete().eq("id", user_id).execute()
            return _ok(result.data)

        else:
            return _fail("अज्ञात action: " + str(action), 400)

    except Exception as e:
        return _fail("Supabase संचालन में त्रुटि: " + str(e), 500)
