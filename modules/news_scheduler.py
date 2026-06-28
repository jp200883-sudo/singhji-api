# modules/news_scheduler.py — FIXED

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from fastapi import APIRouter  # ⬅️ ADD THIS

IST = pytz.timezone('Asia/Kolkata')

# ⬅️ ADD THIS LINE
router = APIRouter(prefix="/api/news-scheduler", tags=["News Scheduler"])

# ===== SCHEDULER FUNCTIONS (same as before) =====
def fetch_and_store_news(category="india", language="hi"):
    """Har ghante news fetch + store + notify"""
    from modules import newsdata, currents_api, supabase_memory
    
    if category == "india":
        news = newsdata.get_india_news(language=language)
    elif category == "world":
        news = currents_api.get_world_news()
    else:
        news = {"success": False, "error": "Unknown category"}
    
    if news.get("success"):
        supabase_memory.store_news(
            category=category,
            language=language,
            articles=news["articles"],
            timestamp=datetime.now(IST).isoformat()
        )
        return True
    return False

# Scheduler
scheduler = BackgroundScheduler(timezone=IST)
scheduler.add_job(fetch_and_store_news, 'cron', hour='6-21', minute=0, args=["india", "hi"])
scheduler.add_job(fetch_and_store_news, 'cron', hour='6-21', minute=5, args=["world", "en"])
scheduler.start()

# ⬅️ ADD THESE ROUTES
@router.get("/")
async def news_scheduler_home():
    return {
        "app": "News Scheduler",
        "status": "active",
        "schedule": "Every hour 6AM-9PM",
        "timezone": "Asia/Kolkata",
        "jobs": 2,
        "message": "News auto-fetch chal raha hai!"
    }

@router.get("/status")
async def scheduler_status():
    return {
        "scheduler": "active",
        "next_run": "Check /api/news-scheduler/",
        "jobs": [
            {"name": "India News", "time": "Every hour :00", "category": "india"},
            {"name": "World News", "time": "Every hour :05", "category": "world"}
        ],
        "message": "6AM se 9PM tak har ghante news!"
    }
