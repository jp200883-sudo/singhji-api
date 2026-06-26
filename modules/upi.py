# modules/upi/__init__.py — Singh Ji AI Ultra v5.0
# 💳 UPI / Payments

from fastapi import APIRouter
from config.settings import settings 

router = APIRouter()

@router.get("/health")
def upi_health():
    return {
        "module": "upi",
        "status": "✅ OK",
        "upi_id": settings.UPI_ID,
        "razorpay_set": bool(settings.RAZORPAY_KEY_ID)
    }

@router.get("/id")
def get_upi_id():
    """Get UPI ID for payments"""
    return {
        "ok": True,
        "upi_id": settings.UPI_ID,
        "name": "Singh Ji AI",
        "note": "Donation / Support",
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={settings.UPI_ID}&pn=SinghJiAI"
    }

@router.get("/donate")
def donate(amount: int = 100):
    """Donation link"""
    return {
        "ok": True,
        "amount": amount,
        "currency": "INR",
        "upi_id": settings.UPI_ID,
        "message": f"₹{amount} दान करने के लिए UPI ID: {settings.UPI_ID}",
        "methods": ["Google Pay", "PhonePe", "Paytm", "BHIM", "Any UPI App"]
    }

@router.get("/razorpay/config")
def razorpay_config():
    """Razorpay configuration"""
    if not settings.RAZORPAY_KEY_ID:
        return {"ok": False, "error": "Razorpay not configured"}

    return {
        "ok": True,
        "key_id": settings.RAZORPAY_KEY_ID[:10] + "...",
        "mode": "test" if "test" in settings.RAZORPAY_KEY_ID else "live"
    }
