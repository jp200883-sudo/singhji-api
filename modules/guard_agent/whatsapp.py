"""
📱 WHATSAPP ALERT — Singh Ji AI Ultra
"""
import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")  # जैसे "whatsapp:+14155238886"


class WhatsAppAlert(BaseModel):
    to_number: str
    message: str
    media_url: Optional[str] = None
    location: Optional[str] = None


def _format_message(message: str, location: Optional[str] = None) -> str:
    return f"""🦁 *Singh Ji AI Alert* 🛡️
{message}
📍 Location: {location or 'Unknown'}
⏰ Time: {datetime.utcnow().strftime('%d-%m-%Y %H:%M')} IST
_जहाँ Singh Ji की नज़र, वहाँ चोर की फजीहत_"""


async def send_guard_whatsapp_alert(message: str, to_number: Optional[str] = None, location: Optional[str] = None) -> dict:
    """
    असली Twilio WhatsApp भेजें। to_number न दिया जाए तो
    GUARD_ALERT_WHATSAPP_NUMBERS env var (comma-separated) के सभी नंबरों पर भेजता है।
    """
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        return {"status": "error", "error": "Twilio env vars missing (TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN/TWILIO_WHATSAPP_FROM)"}

    numbers = [to_number] if to_number else [
        n.strip() for n in os.getenv("GUARD_ALERT_WHATSAPP_NUMBERS", "").split(",") if n.strip()
    ]
    if not numbers:
        return {"status": "error", "error": "No recipient number available"}

    body = _format_message(message, location)
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    results = []

    async with httpx.AsyncClient(timeout=15) as client:
        for num in numbers:
            to = num if num.startswith("whatsapp:") else f"whatsapp:{num}"
            try:
                resp = await client.post(
                    url,
                    data={"From": TWILIO_FROM, "To": to, "Body": body},
                    auth=(TWILIO_SID, TWILIO_TOKEN),
                )
                results.append({"number": num, "status": "sent" if resp.status_code == 201 else "failed", "code": resp.status_code})
            except Exception as e:
                results.append({"number": num, "status": "failed", "error": str(e)[:100]})

    return {"status": "sent", "results": results}


@router.post("/send")
async def send_whatsapp(alert: WhatsAppAlert):
    result = await send_guard_whatsapp_alert(alert.message, alert.to_number, alert.location)
    return {
        "status": result["status"],
        "to": alert.to_number,
        "message_preview": alert.message[:50] + "...",
        "detail": result,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/broadcast")
async def broadcast_whatsapp(numbers: List[str], message: str, location: Optional[str] = None):
    results = []
    for num in numbers:
        r = await send_guard_whatsapp_alert(message, num, location)
        results.append({"number": num, "status": r["status"]})
    return {
        "total": len(numbers),
        "successful": sum(1 for r in results if r["status"] == "sent"),
        "results": results
    }
