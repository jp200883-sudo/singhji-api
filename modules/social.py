# modules/social/__init__.py — Singh Ji AI Ultra v5.0
# 📱 Social Media

from fastapi import APIRouter
from config.settings import settings 

router = APIRouter()

@router.get("/health")
def social_health():
    return {
        "module": "social",
        "status": "✅ OK",
        "platforms": settings.SOCIAL_PLATFORMS
    }

@router.get("/platforms")
def list_platforms():
    """All connected platforms"""
    return {
        "ok": True,
        "platforms": [
            {"name": "instagram", "connected": False, "url": "https://instagram.com/singhjiai"},
            {"name": "facebook", "connected": False, "url": "https://facebook.com/singhjiai"},
            {"name": "twitter", "connected": False, "url": "https://twitter.com/singhjiai"},
            {"name": "whatsapp", "connected": True, "url": "https://wa.me/"},
            {"name": "telegram", "connected": True, "url": "https://t.me/Singhjp_bot"},
        ]
    }

@router.post("/share")
def share_post(platform: str, message: str):
    """Share to social media"""
    if platform not in settings.SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Platform '{platform}' not supported"}

    return {
        "ok": True,
        "platform": platform,
        "message": message,
        "status": "shared",
        "note": "Auto-posting coming in v5.1"
    }

@router.get("/templates")
def post_templates():
    """Ready-made post templates"""
    return {
        "ok": True,
        "templates": [
            {"id": "morning", "text": "🌅 सुप्रभात! Singh Ji AI के साथ नया दिन शुरू करें। #SinghJiAI #India"},
            {"id": "motivation", "text": "🦁 'सबका भला, सबका साथ' — Singh Ji AI Ultra v5.0 #Motivation #India"},
            {"id": "tech", "text": "⚡ AI + India = Singh Ji AI Ultra 🚀 #AI #TechIndia #Innovation"},
            {"id": "kisan", "text": "🌾 किसान भाइयों के लिए मंडी भाव और मौसम अपडेट। #Kisan #Agriculture #India"},
            {"id": "govt", "text": "🏛️ सरकारी योजनाओं की जानकारी Singh Ji AI पर। #GovtSchemes #India"},
        ]
    }
