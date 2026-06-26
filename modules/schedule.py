from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def schedule_home():
    return {
        "module": "schedule",
        "status": "ok",
        "daily_routine": settings.DAILY_SCHEDULE
    }

@router.get("/today")
def schedule_today():
    return {
        "schedule": settings.DAILY_SCHEDULE,
        "status": "active"
    }
