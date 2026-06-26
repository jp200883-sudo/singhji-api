# modules/adminpanel/__init__.py — Singh Ji AI Ultra v5.0
# This file = handler.py (Render free tier fix)
# Admin Dashboard Backend

from fastapi import APIRouter
import os
import json

router = APIRouter()

ADMIN_KEY = os.getenv("ADMIN_KEY", "singhji-admin-2026")

@router.get("/health")
def admin_health():
    return {
        "module": "adminpanel",
        "status": "✅ OK",
        "version": "1.0.0",
        "features": [
            "Dashboard stats",
            "Module management",
            "User analytics",
            "System logs"
        ]
    }

@router.get("/stats")
def admin_stats():
    """System-wide statistics"""
    import psutil
    try:
        return {
            "ok": True,
            "app": "Singh Ji AI Ultra v5.0",
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else "N/A"
            },
            "modules": {
                "language": "✅ Active",
                "telegram_bot": "✅ Active",
                "plant_id": "✅ Active",
                "supabase_memory": "✅ Active",
                "adminpanel": "✅ Active"
            },
            "timestamp": str(__import__("datetime").datetime.now())
        }
    except:
        return {
            "ok": True,
            "app": "Singh Ji AI Ultra v5.0",
            "system": {"note": "psutil not available on Render free tier"},
            "modules": {
                "language": "✅ Active",
                "telegram_bot": "✅ Active",
                "plant_id": "✅ Active",
                "supabase_memory": "✅ Active",
                "adminpanel": "✅ Active"
            }
        }

@router.get("/modules")
def list_modules():
    """List all modules and their status"""
    return {
        "ok": True,
        "modules": [
            {"name": "language", "path": "modules.language", "prefix": "/api/language", "status": "✅"},
            {"name": "telegram_bot", "path": "modules.telegram_bot", "prefix": "/api/telegram", "status": "✅"},
            {"name": "plant_id", "path": "modules.plant_id", "prefix": "/api/plant", "status": "✅"},
            {"name": "supabase_memory", "path": "modules.supabase_memory", "prefix": "/api/memory", "status": "✅"},
            {"name": "adminpanel", "path": "modules.adminpanel", "prefix": "/api/admin", "status": "✅"}
        ]
    }

@router.get("/verify")
def verify_admin(key: str = ""):
    """Verify admin access key"""
    if key == ADMIN_KEY:
        return {"ok": True, "admin": True, "message": "🦁 Welcome, Admin!"}
    return {"ok": False, "admin": False, "message": "❌ Invalid admin key"}

@router.get("/config")
def get_config():
    """Get app configuration (safe values only)"""
    return {
        "ok": True,
        "app_name": "Singh Ji AI Ultra v5.0",
        "tagline": "भारत का ऑल-इन-वन सुपर ऐप",
        "version": "5.0.0",
        "language_count": 58,
        "indian_languages": 22,
        "global_languages": 36,
        "features": [
            "Language Hub (58 languages)",
            "Telegram Bot Integration",
            "Plant ID (AI Plant Recognition)",
            "Supabase Memory",
            "Admin Dashboard",
            "Bhashini Integration (Pending)"
        ]
    }
