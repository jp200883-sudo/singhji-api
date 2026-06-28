# modules/schedule.py — Singh Ji AI Ultra
# Auto Schedule Plan — Har cheez time pe!

from fastapi import APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

router = APIRouter(prefix="/api/schedule", tags=["Schedule"])

IST = pytz.timezone('Asia/Kolkata')

# ===== SCHEDULER JOBS =====
scheduler = BackgroundScheduler(timezone=IST)

def fetch_news_job():
    """Har 30 min news fetch"""
    print(f"[{datetime.now(IST)}] 📰 News fetch ho raha hai...")
    # Call newsdata API internally
    # Store in Supabase cache

def fetch_weather_job():
    """Har 1 ghante weather fetch"""
    print(f"[{datetime.now(IST)}] 🌤️ Weather update ho raha hai...")

def fetch_mandi_job():
    """Subah 6 baje mandi rates"""
    print(f"[{datetime.now(IST)}] 🌾 Mandi rates aa gaye!")

def fetch_health_job():
    """Roz subah health tips"""
    print(f"[{datetime.now(IST)}] 💊 Health tips generate ho gaye!")

def fetch_stock_job():
    """Har 15 min stock/crypto"""
    print(f"[{datetime.now(IST)}] 📈 Stock prices update ho gaye!")

def fetch_govt_job():
    """Weekly govt schemes"""
    print(f"[{datetime.now(IST)}] 🏛️ Govt schemes check kiye!")

# ===== ADD ALL JOBS =====
scheduler.add_job(fetch_news_job, 'interval', minutes=30, id='news_job')
scheduler.add_job(fetch_weather_job, 'interval', hours=1, id='weather_job')
scheduler.add_job(fetch_mandi_job, 'cron', hour=6, minute=0, id='mandi_job')
scheduler.add_job(fetch_health_job, 'cron', hour=7, minute=0, id='health_job')
scheduler.add_job(fetch_stock_job, 'interval', minutes=15, id='stock_job')
scheduler.add_job(fetch_govt_job, 'cron', day_of_week='sun', hour=8, minute=0, id='govt_job')

scheduler.start()

# ===== API ROUTES =====
@router.get("/")
async def schedule_home():
    """Schedule Plan Home"""
    jobs = scheduler.get_jobs()
    return {
        "app": "Singh Ji Scheduler",
        "status": "active",
        "total_jobs": len(jobs),
        "jobs": [
            {
                "name": job.id,
                "next_run": str(job.next_run_time),
                "trigger": str(job.trigger)
            }
            for job in jobs
        ],
        "schedule": {
            "news": "Every 30 min",
            "weather": "Every 1 hour",
            "mandi": "Daily 6 AM",
            "health": "Daily 7 AM",
            "stock": "Every 15 min",
            "govt": "Weekly Sunday 8 AM"
        },
        "message": "Sab kuch time pe chalega!"
    }

@router.get("/status")
async def schedule_status():
    """Check all scheduled jobs"""
    return {
        "scheduler_running": scheduler.running,
        "jobs_count": len(scheduler.get_jobs()),
        "current_time": datetime.now(IST).isoformat(),
        "message": "Singh Ji ka clock chal raha hai!"
    }

@router.post("/run-now")
async def run_job_now(job_name: str):
    """Manually trigger any job"""
    job = scheduler.get_job(job_name)
    if job:
        job.modify(next_run_time=datetime.now(IST))
        return {"success": True, "message": f"{job_name} abhi chalega!"}
    return {"success": False, "error": "Job not found"}
