from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def schedule_home():
    return {
        "module": "schedule",
        "status": "ok",
        "schedule": settings.DAILY_SCHEDULE
    }

@router.post("/add")
def schedule_add(task: str = "", time: str = ""):
    return {
        "task": task,
        "time": time,
        "status": "scheduled"
    }
