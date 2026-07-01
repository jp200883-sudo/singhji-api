"""
🦁 SINGH JI AI MAIL SYSTEM
Auto-check | Spam Delete | Smart Reply | Public Service
"""
import os
import imaplib
import smtplib
import email
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ========== CONFIG ==========
EMAIL_HOST = os.getenv("EMAIL_HOST", "imap.gmail.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Singh Ji AI <noreply@singhji.ai>")

# Spam keywords (auto-delete)
SPAM_KEYWORDS = [
    "lottery", "winner", "prize", "free money", "click here",
    "urgent", "limited time", "act now", "congratulations",
    " Nigerian prince", "inheritance", "viagra", "crypto scam",
    "double your", "risk free", "act immediately", "call now",
    "credit card", "bank account", "verify now", "suspended"
]

# Auto-reply triggers
AUTO_REPLY_TRIGGERS = {
    "job": "🦁 Singh Ji Rozgar: नौकरी के लिए /api/rozgar पर जाएं या 'rozgar' टाइप करें।",
    "help": "🦁 Singh Ji AI: मदद के लिए 'help' लिखें या /api/status चेक करें।",
    "support": "🦁 Support: आपकी समस्या रिकॉर्ड हो गई। जल्द संपर्क करेंगे।",
    "contact": "🦁 Singh Ji AI: हमसे जुड़ने के लिए धन्यवाद! वेबसाइट: singhji-ai.github.io",
    "hello": "🦁 नमस्ते! मैं Singh Ji AI हूँ। कैसे मदद करूँ?",
    "hi": "🦁 नमस्ते! Singh Ji AI में आपका स्वागत है।",
    "thank": "🦁 आपका धन्यवाद! जय हिंद! 🇮🇳",
}

MODULES = {}

def is_spam(subject, body, sender):
    """AI Spam Detection"""
    text = f"{subject} {body} {sender}".lower()
    score = 0
    
    # Keyword check
    for keyword in SPAM_KEYWORDS:
        if keyword in text:
            score += 2
    
    # Suspicious sender
    suspicious = ["no-reply@", "noreply@", "marketing@", "promo@", "newsletter@"]
    for s in suspicious:
        if s in sender.lower():
            score += 1
    
    # All caps subject
    if subject.isupper() and len(subject) > 10:
        score += 1
    
    # Too many exclamation marks
    if text.count('!') > 3:
        score += 1
    
    return score >= 3

def get_auto_reply(subject, body):
    """Smart Auto-Reply"""
    text = f"{subject} {body}".lower()
    
    for trigger, reply in AUTO_REPLY_TRIGGERS.items():
        if trigger in text:
            return reply
    
    # Default reply for unknown
    if "?" in subject or "?" in body:
        return "🦁 Singh Ji AI: आपका सवाल मिल गया। जल्द जवाब देंगे। तब तक /api/status चेक करें।"
    
    return None

def send_email(to_email, subject, body, html=False):
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = f"🦁 {subject}"
        
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_HOST, 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        return {"status": "ok", "message": "Sent"}
    except Exception as e:
        logger.error(f"Send failed: {e}")
        return {"status": "error", "message": str(e)}

def check_and_process_emails():
    """Main AI Mail Engine"""
    if not EMAIL_USER or not EMAIL_PASS:
        return {"status": "error", "message": "Email not configured"}
    
    results = {
        "checked": 0,
        "spam_deleted": 0,
        "auto_replied": 0,
        "kept": 0,
        "errors": []
    }
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(EMAIL_HOST)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        # Search all unread emails
        _, search_data = mail.search(None, "UNSEEN")
        email_ids = search_data[0].split()
        
        results["checked"] = len(email_ids)
        
        for e_id in email_ids:
            try:
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract info
                subject = msg["subject"] or ""
                sender = msg["from"] or ""
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                
                # AI Decision
                if is_spam(subject, body, sender):
                    # DELETE SPAM
                    mail.store(e_id, "+FLAGS", "\\Deleted")
                    results["spam_deleted"] += 1
                    logger.info(f"🗑️ Spam deleted: {subject[:50]}")
                
                else:
                    auto_reply = get_auto_reply(subject, body)
                    if auto_reply:
                        # Send auto-reply
                        reply_to = email.utils.parseaddr(sender)[1]
                        send_email(reply_to, "Re: " + subject[:50], auto_reply)
                        results["auto_replied"] += 1
                        logger.info(f"🤖 Auto-replied: {subject[:50]}")
                    else:
                        results["kept"] += 1
                
            except Exception as e:
                results["errors"].append(str(e))
                logger.error(f"Email processing error: {e}")
        
        # Expunge deleted
        mail.expunge()
        mail.close()
        mail.logout()
        
        logger.info(f"🦁 Mail check: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Mail check failed: {e}")
        return {"status": "error", "message": str(e)}

# ========== API HANDLER ==========

async def handler(request: Request):
    """Singh Ji AI Mail API"""
    try:
        data = await request.json() if await request.body() else {}
        action = data.get("action", "status")
        
        if action == "check":
            # Manual check now
            result = check_and_process_emails()
            return JSONResponse({
                "status": "ok",
                "action": "mail_check",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        
        elif action == "send":
            # Send custom email
            result = send_email(
                data.get("to"),
                data.get("subject", "Singh Ji AI"),
                data.get("body", ""),
                data.get("html", False)
            )
            return JSONResponse(result)
        
        elif action == "test":
            # Test spam detection
            test_cases = [
                ("You won lottery!", "Click here to claim", "spam@test.com"),
                ("Job application", "I want to apply", "user@test.com"),
                ("Hello", "Hi there", "friend@test.com"),
            ]
            results = []
            for sub, body, sender in test_cases:
                results.append({
                    "subject": sub,
                    "is_spam": is_spam(sub, body, sender),
                    "auto_reply": get_auto_reply(sub, body)
                })
            return JSONResponse({"status": "ok", "tests": results})
        
        elif action == "config":
            # Show config (hide password)
            return JSONResponse({
                "status": "ok",
                "email_host": EMAIL_HOST,
                "email_user": EMAIL_USER,
                "spam_keywords_count": len(SPAM_KEYWORDS),
                "auto_reply_triggers": list(AUTO_REPLY_TRIGGERS.keys())
            })
        
        else:
            return JSONResponse({
                "status": "ok",
                "service": "🦁 Singh Ji AI Mail System",
                "features": [
                    "Auto spam detection & delete",
                    "Smart auto-reply",
                    "Manual mail check",
                    "Custom email send"
                ],
                "endpoints": {
                    "check": "POST /api/mailer {'action':'check'}",
                    "send": "POST /api/mailer {'action':'send', 'to':'...', 'subject':'...', 'body':'...'}",
                    "test": "POST /api/mailer {'action':'test'}",
                    "config": "POST /api/mailer {'action':'config'}"
                }
            })
            
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
