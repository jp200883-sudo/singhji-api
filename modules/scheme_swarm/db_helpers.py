"""
Singh Ji AI — Scheme Swarm Database Helpers
Works with Supabase / PostgreSQL
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy import — will work if supabase is installed
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not installed. Using in-memory fallback.")


# ═══════════════════════════════════════════════════════
# IN-MEMORY FALLBACK (for testing without DB)
# ═══════════════════════════════════════════════════════

_in_memory_profiles: Dict[int, Dict] = {}
_in_memory_applications: List[Dict] = []


def _get_supabase_client():
    """Get Supabase client"""
    if not SUPABASE_AVAILABLE:
        return None

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        return None

    return create_client(url, key)


# ═══════════════════════════════════════════════════════
# PROFILE FUNCTIONS
# ═══════════════════════════════════════════════════════

async def get_scheme_profile(user_id: int) -> Optional[Dict]:
    """Fetch user's scheme profile from DB"""
    client = _get_supabase_client()

    if client:
        try:
            result = client.table("scheme_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"DB get profile error: {e}")
            # Fallback to memory
            return _in_memory_profiles.get(user_id)
    else:
        return _in_memory_profiles.get(user_id)


async def save_scheme_profile(user_id: int, profile: Dict) -> bool:
    """Save or update user's scheme profile"""
    client = _get_supabase_client()

    data = {
        "user_id": user_id,
        "age": profile.get("age"),
        "annual_income": profile.get("income"),
        "state": profile.get("state"),
        "occupation": profile.get("occupation"),
        "caste_category": profile.get("caste"),
        "family_members": profile.get("family_members"),
        "gender": profile.get("gender", "male"),
        "bpl_status": profile.get("bpl_status", False),
        "is_farmer": profile.get("occupation") == "farmer",
        "is_student": profile.get("occupation") == "student",
        "is_widow": profile.get("is_widow", False),
        "is_disabled": profile.get("is_disabled", False),
        "is_senior_citizen": profile.get("age", 0) >= 60,
        "updated_at": datetime.now().isoformat()
    }

    if client:
        try:
            # Upsert
            result = client.table("scheme_profiles")\
                .upsert(data, on_conflict="user_id")\
                .execute()
            return True
        except Exception as e:
            logger.error(f"DB save profile error: {e}")
            _in_memory_profiles[user_id] = data
            return True
    else:
        _in_memory_profiles[user_id] = data
        return True


async def update_scheme_profile(user_id: int, updates: Dict) -> bool:
    """Partial update of profile"""
    client = _get_supabase_client()

    updates["updated_at"] = datetime.now().isoformat()

    if client:
        try:
            result = client.table("scheme_profiles")\
                .update(updates)\
                .eq("user_id", user_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"DB update error: {e}")
            if user_id in _in_memory_profiles:
                _in_memory_profiles[user_id].update(updates)
            return True
    else:
        if user_id in _in_memory_profiles:
            _in_memory_profiles[user_id].update(updates)
        return True


# ═══════════════════════════════════════════════════════
# APPLICATION TRACKING
# ═══════════════════════════════════════════════════════

async def save_application(user_id: int, scheme_id: str, application_data: Dict) -> bool:
    """Save scheme application tracking"""
    client = _get_supabase_client()

    data = {
        "user_id": user_id,
        "scheme_id": scheme_id,
        "application_id": application_data.get("application_id"),
        "status": application_data.get("status", "applied"),
        "status_history": [{"status": "applied", "timestamp": datetime.now().isoformat()}],
        "documents_submitted": application_data.get("documents", []),
        "notes": application_data.get("notes", ""),
        "created_at": datetime.now().isoformat()
    }

    if client:
        try:
            result = client.table("scheme_applications")\
                .insert(data)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"DB save application error: {e}")
            _in_memory_applications.append(data)
            return True
    else:
        _in_memory_applications.append(data)
        return True


async def get_user_applications(user_id: int) -> List[Dict]:
    """Get all applications for a user"""
    client = _get_supabase_client()

    if client:
        try:
            result = client.table("scheme_applications")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"DB get applications error: {e}")
            return [a for a in _in_memory_applications if a.get("user_id") == user_id]
    else:
        return [a for a in _in_memory_applications if a.get("user_id") == user_id]


async def update_application_status(user_id: int, scheme_id: str, status: str, notes: str = "") -> bool:
    """Update application status"""
    client = _get_supabase_client()

    if client:
        try:
            # Get existing
            result = client.table("scheme_applications")\
                .select("status_history")\
                .eq("user_id", user_id)\
                .eq("scheme_id", scheme_id)\
                .execute()

            history = result.data[0].get("status_history", []) if result.data else []
            history.append({"status": status, "timestamp": datetime.now().isoformat(), "notes": notes})

            client.table("scheme_applications")\
                .update({
                    "status": status,
                    "status_history": history,
                    "last_checked": datetime.now().isoformat()
                })\
                .eq("user_id", user_id)\
                .eq("scheme_id", scheme_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"DB update status error: {e}")
            return False
    return False


# ═══════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════

async def save_notification(user_id: int, scheme_id: str, notif_type: str, message: str) -> bool:
    """Save notification log"""
    client = _get_supabase_client()

    data = {
        "user_id": user_id,
        "scheme_id": scheme_id,
        "type": notif_type,
        "message": message,
        "sent_at": datetime.now().isoformat(),
        "read": False
    }

    if client:
        try:
            client.table("scheme_notifications").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"DB notification error: {e}")
            return False
    return True


async def get_unread_notifications(user_id: int) -> List[Dict]:
    """Get unread notifications for user"""
    client = _get_supabase_client()

    if client:
        try:
            result = client.table("scheme_notifications")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("read", False)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"DB get notifications error: {e}")
            return []
    return []


# ═══════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════

async def get_module_stats() -> Dict[str, Any]:
    """Get Scheme Swarm module statistics"""
    client = _get_supabase_client()

    if client:
        try:
            profiles = client.table("scheme_profiles").select("count", count="exact").execute()
            applications = client.table("scheme_applications").select("count", count="exact").execute()

            return {
                "total_profiles": profiles.count if hasattr(profiles, 'count') else 0,
                "total_applications": applications.count if hasattr(applications, 'count') else 0,
                "in_memory_profiles": len(_in_memory_profiles)
            }
        except Exception as e:
            logger.error(f"DB stats error: {e}")

    return {
        "total_profiles": len(_in_memory_profiles),
        "total_applications": len(_in_memory_applications),
        "in_memory_profiles": len(_in_memory_profiles),
        "db_connected": SUPABASE_AVAILABLE and client is not None
    }
