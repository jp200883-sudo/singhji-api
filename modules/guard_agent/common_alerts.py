"""
📋 ALERT HISTORY — Singh Ji AI Ultra
"""

from fastapi import APIRouter
from typing import Optional

router = APIRouter()

alerts_db = []

@router.get("/")
async def get_alerts(limit: int = 50, agent_type: Optional[str] = None):
    filtered = alerts_db
    if agent_type:
        filtered = [a for a in alerts_db if a.get("type") == agent_type]
    return {"total": len(filtered), "alerts": filtered[-limit:][::-1]}

@router.delete("/clear")
async def clear_alerts():
    global alerts_db
    count = len(alerts_db)
    alerts_db = []
    return {"status": "cleared", "deleted": count}
