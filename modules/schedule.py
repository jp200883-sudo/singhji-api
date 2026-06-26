# modules/schedule/__init__.py — Singh Ji AI Ultra v5.0
# 📅 Daily Schedule / Automation

from fastapi import APIRouter
from config.settings import settings 

router = APIRouter()

@router.get("/health")
def schedule_health():
    return {
        "module": "schedule",
        "status": "✅ OK",
        "total_tasks": len(settings.DAILY_SCHEDULE)
    }

@router.get("/daily")
def daily_schedule():
    """Full daily schedule"""
    return {
        "ok": True,
        "timezone": "IST (India)",
        "schedule": settings.DAILY_SCHEDULE
    }

@router.get("/now")
def current_task():
    """What should be running now"""
    from datetime import datetime
    import pytz

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    current_time = now.strftime("%H:%M")
    hour = now.hour

    # Find current or next task
    tasks = sorted(settings.DAILY_SCHEDULE.items())
    current_task = None
    next_task = None

    for i, (time_str, task) in enumerate(tasks):
        if time_str <= current_time:
            current_task = {"time": time_str, "task": task}
        if time_str > current_time and not next_task:
            next_task = {"time": time_str, "task": task}

    return {
        "ok": True,
        "current_time": current_time,
        "current_task": current_task,
        "next_task": next_task,
        "all_tasks": tasks
    }

@router.get("/task/{task_name}")
def get_task(task_name: str):
    """Get specific task details"""
    task_times = [t for t, n in settings.DAILY_SCHEDULE.items() if n == task_name]
    if task_times:
        return {
            "ok": True,
            "task": task_name,
            "scheduled_times": task_times,
            "description": get_task_description(task_name)
        }
    return {"ok": False, "error": f"Task '{task_name}' not found"}

def get_task_description(task_name: str):
    descriptions = {
        "morning_routine": "सुबह की शुरुआत — न्यूज़, मौसम, शेड्यूल",
        "social_post_morning": "सोशल मीडिया पोस्ट — सुबह का मैसेज",
        "music_morning": "सुबह का संगीत — मोटिवेशन",
        "education_tip": "रोज़ाना एक नई सीख",
        "news_digest": "दोपहर की खबरें",
        "banking_tip": "बैंकिंग और पैसों की सलाह",
        "coming_soon_teaser": "नया फीचर आने वाला है",
        "email_check": "इमेल चेक और जवाब",
        "evening_summary": "शाम का सारांश — आज क्या हुआ",
        "music_evening": "शाम का संगीत — आराम",
        "jp_singh_thought": "जेपी सिंह का विचार",
        "good_night": "रात्रि शुभ — कल मिलेंगे"
    }
    return descriptions.get(task_name, "Daily automated task")
