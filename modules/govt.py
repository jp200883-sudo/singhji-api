# modules/govt/__init__.py — Singh Ji AI Ultra v5.0
# 🏛️ Government Schemes

from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/health")
def govt_health():
    return {
        "module": "govt",
        "status": "✅ OK",
        "total_schemes": len(settings.GOVT_SCHEMES)
    }

@router.get("/schemes")
def list_schemes():
    """All government schemes"""
    return {
        "ok": True,
        "count": len(settings.GOVT_SCHEMES),
        "schemes": settings.GOVT_SCHEMES
    }

@router.get("/scheme/{scheme_id}")
def get_scheme(scheme_id: str):
    """Get specific scheme details"""
    for scheme in settings.GOVT_SCHEMES:
        if scheme["id"] == scheme_id:
            return {"ok": True, "scheme": scheme}
    return {"ok": False, "error": f"Scheme '{scheme_id}' not found"}

@router.get("/search")
def search_schemes(q: str = ""):
    """Search schemes"""
    results = [s for s in settings.GOVT_SCHEMES if q.lower() in s["name"].lower() or q.lower() in s["desc"].lower()]
    return {"ok": True, "query": q, "count": len(results), "schemes": results}

@router.get("/pm_kisan")
def pm_kisan():
    """PM-KISAN details"""
    return {
        "ok": True,
        "scheme": {
            "name": "PM-KISAN",
            "full_name": "Pradhan Mantri Kisan Samman Nidhi",
            "amount": "₹6,000 प्रति वर्ष",
            "installments": "3 किश्तें (₹2,000 हर 4 महीने)",
            "eligibility": "सभी किसान परिवार",
            "website": "pmkisan.gov.in",
            "helpline": "155261",
            "desc": "हर किसान को साल में 6000 रुपये सीधे बैंक खाते में"
        }
    }

@router.get("/ayushman")
def ayushman_bharat():
    """Ayushman Bharat details"""
    return {
        "ok": True,
        "scheme": {
            "name": "Ayushman Bharat",
            "full_name": "Pradhan Mantri Jan Arogya Yojana",
            "amount": "₹5 लाख प्रति परिवार",
            "eligibility": "गरीबी रेखा से नीचे के परिवार",
            "website": "pmjay.gov.in",
            "helpline": "14555",
            "desc": "5 लाख तक का मुफ्त इलाज हर साल"
        }
    }
