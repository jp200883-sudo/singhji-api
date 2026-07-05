"""
📱 WHATSAPP ALERT — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

class WhatsAppAlert(BaseModel):
    to_number: str
    message: str
    media_url: Optional[str] = None
    location: Optional[str] = None

@router.post("/send")
async def send_whatsapp(alert: WhatsAppAlert):
    branded = f"""🦁 *Singh Ji AI Alert* 🛡️

{alert.message}

📍 Location: {alert.location or 'Unknown'}
⏰ Time: {datetime.utcnow().strftime('%d-%m-%Y %H:%M')} IST

_जहाँ Singh Ji की नज़र, वहाँ चोर की फजीहत_"""
    
    return {
        "status": "mock_sent",
        "to": alert.to_number,
        "message_preview": alert.message[:50] + "...",
        "note": "Set WHATSAPP_TOKEN env var for live sending",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/broadcast")
async def broadcast_whatsapp(numbers: List[str], message: str, location: Optional[str] = None):
    results = []
    for num in numbers:
        results.append({"number": num, "status": "mock_sent"})
    return {
        "total": len(numbers),
        "successful": len(numbers),
        "results": results
    }
