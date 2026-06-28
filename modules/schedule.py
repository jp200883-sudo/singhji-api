from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/")
def schedule_home():
    return {
        "module": "schedule",
        "status": "✅ LIVE",
        "message": "Schedule module ready — Singh Ji ka calendar!"
    }

@router.get("/today")
def today_schedule():
    return {
        "ok": True,
        "date": "today",
        "events": [
            {"time": "09:00", "task": "Singh Ji ka hukum sunna"},
            {"time": "12:00", "task": "Kela break 🍌"},
            {"time": "18:00", "task": "API check karna"}
        ],
        "message": "Aaj ka schedule!"
    }

@router.post("/add")
def add_event(request: dict):
    return {
        "ok": True,
        "event": request.get("event", "Unknown"),
        "time": request.get("time", "Now"),
        "message": "Event add ho gaya!"
    }
