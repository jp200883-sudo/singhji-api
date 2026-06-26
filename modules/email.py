from fastapi import APIRouter
from config.settings import settings

router = APIRouter()

@router.get("/")
def email_home():
    return {
        "module": "email",
        "status": "ok",
        "gmail_user": settings.GMAIL_USER
    }

@router.post("/send")
def email_send(to: str = "", subject: str = "", body: str = ""):
    return {
        "to": to,
        "subject": subject,
        "status": "mock_sent",
        "message": f"Email sent to {to}"
    }
