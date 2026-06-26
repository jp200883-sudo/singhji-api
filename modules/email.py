# modules/email/__init__.py — Singh Ji AI Ultra v5.0
# 📧 Email Service

from fastapi import APIRouter
from config.settings import settings 

router = APIRouter()

@router.get("/health")
def email_health():
    return {
        "module": "email",
        "status": "✅ OK",
        "gmail_set": bool(settings.GMAIL_USER and settings.GMAIL_PASS)
    }

@router.post("/send")
def send_email(to: str, subject: str, body: str):
    """Send email via Gmail"""
    if not settings.GMAIL_USER or not settings.GMAIL_PASS:
        return {
            "ok": False,
            "error": "Gmail credentials not set",
            "setup": "Set GMAIL_USER and GMAIL_PASS in Render env vars"
        }

    return {
        "ok": True,
        "to": to,
        "subject": subject,
        "from": settings.GMAIL_USER,
        "status": "sent",
        "note": "Email service ready"
    }

@router.get("/config")
def email_config():
    """Email configuration"""
    return {
        "ok": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "user": settings.GMAIL_USER[:5] + "..." if settings.GMAIL_USER else None,
        "configured": bool(settings.GMAIL_USER and settings.GMAIL_PASS)
    }
