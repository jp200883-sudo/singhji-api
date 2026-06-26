# modules/emergency/__init__.py — Singh Ji AI Ultra v5.0
# 🚨 Emergency Services

from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/health")
def emergency_health():
    return {
        "module": "emergency",
        "status": "✅ OK",
        "services": ["Police", "Ambulance", "Fire", "Women Helpline", "Child Helpline"]
    }

@router.get("/numbers")
def emergency_numbers():
    """All emergency numbers"""
    return {
        "ok": True,
        "country": "India",
        "emergency_numbers": {
            "police": {"number": settings.POLICE, "name": "Police", "desc": "पुलिस"},
            "ambulance": {"number": settings.AMBULANCE, "name": "Ambulance", "desc": "एम्बुलेंस"},
            "fire": {"number": settings.FIRE, "name": "Fire Brigade", "desc": "फायर ब्रिगेड"},
            "women_helpline": {"number": settings.WOMEN_HELPLINE, "name": "Women Helpline", "desc": "महिला हेल्पलाइन"},
            "child_helpline": {"number": settings.CHILD_HELPLINE, "name": "Child Helpline", "desc": "बच्चों की हेल्पलाइन"},
        },
        "contacts": [c for c in settings.EMERGENCY_CONTACTS if c]
    }

@router.get("/police")
def police():
    return {"ok": True, "service": "Police", "number": settings.POLICE, "desc": "100 डायल करें"}

@router.get("/ambulance")
def ambulance():
    return {"ok": True, "service": "Ambulance", "number": settings.AMBULANCE, "desc": "108 डायल करें"}

@router.get("/fire")
def fire():
    return {"ok": True, "service": "Fire Brigade", "number": settings.FIRE, "desc": "101 डायल करें"}

@router.get("/women")
def women_helpline():
    return {"ok": True, "service": "Women Helpline", "number": settings.WOMEN_HELPLINE, "desc": "1091 डायल करें"}

@router.get("/child")
def child_helpline():
    return {"ok": True, "service": "Child Helpline", "number": settings.CHILD_HELPLINE, "desc": "1098 डायल करें"}
