from fastapi import APIRouter
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

# Render env se lo — baad mein daalna
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

@router.get("/")
async def email_root():
    configured = bool(SMTP_USER and SMTP_PASS)
    return {
        "ok": True,
        "module": "email",
        "status": "✅ LIVE" if configured else "⚠️ CONFIG PENDING",
        "smtp_user": SMTP_USER[:5] + "..." if SMTP_USER else "Not set",
        "configured": configured,
        "message": "Email ready — Gmail App Password daalo Render mein!" if not configured else "Email full ready!"
    }

@router.post("/send")
async def send_email(to: str, subject: str, body: str, from_name: str = "Singh Ji AI"):
    if not SMTP_USER or not SMTP_PASS:
        return {
            "ok": False,
            "error": "SMTP not configured",
            "message": "Render mein SMTP_USER aur SMTP_PASS daalo!"
        }
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{SMTP_USER}>"
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        return {
            "ok": True,
            "to": to,
            "subject": subject,
            "message": "Email bhej diya bhai! 📧"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Email fail — App Password check karo!"
        }
