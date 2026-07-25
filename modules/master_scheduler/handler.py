"""
╔═══════════════════════════════════════════════════════════════╗
║         SINGH JI AI ULTRA - MASTER SCHEDULER                  ║
║         सारे शेड्यूल एक साथ                                  ║
╚═══════════════════════════════════════════════════════════════╝

Schedules Included:
  DAILY   → News Digest (7AM, 6PM), Weather+Fuel (7AM), Rozgar (6PM)
  WEEKLY  → Govt Schemes (Tue, Fri), Banking (1x), Social Media (3x)
  MONTHLY → Tenders (1-2x), Feature Updates (on launch)
  ON-DEMAND → Emergency, Child Safety, Govt Portals (24/7 commands)

Railway Sleep Fix: Self-ping every 10 min
State Tracking: SQLite (last_run, status, retry_count)
"""

import os
import sys
import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

# ─── Logging Setup ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scheduler.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("SinghJiScheduler")

# ─── SQLite State DB ─────────────────────────────────────────
DB_PATH = os.getenv("SCHEDULER_DB", "scheduler_state.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scheduler_state (
            job_name TEXT PRIMARY KEY,
            last_run TEXT,
            next_run TEXT,
            status TEXT DEFAULT 'pending',
            retry_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def update_job_state(job_name: str, status: str, next_run: Optional[str] = None):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO scheduler_state (job_name, last_run, status, next_run)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(job_name) DO UPDATE SET
                last_run=excluded.last_run,
                status=excluded.status,
                next_run=excluded.next_run,
                retry_count=retry_count+1
        """, (job_name, now, status, next_run))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB update fail for {job_name}: {e}")

# ─── Telegram Bot Placeholder ────────────────────────────────
# TODO: Apne telegram bot instance se replace karo
async def send_telegram_broadcast(message: str, chat_ids: list = None):
    """
    Yahan apna actual telegram bot.send_message() logic daalo.
    Abhi ke liye placeholder hai — isse replace karna mat bhoolna.
    """
    try:
        # import telegram_bot  # apna actual import
        # for cid in chat_ids or []:
        #     await telegram_bot.send_message(chat_id=cid, text=message)
        logger.info(f"[TELEGRAM] Would send: {message[:80]}...")
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False

# ─── News Aggregation Placeholder ────────────────────────────
async def fetch_and_summarize_news(category: str = "all") -> str:
    """
    TODO: Yahan apna actual news aggregation pipeline daalo:
    1. asyncio.gather se APIs se data pull
    2. Region filter (UP/Bihar)
    3. AI Cascade (Groq → Gemini) se summarize
    4. Hindi mein 3-4 bullet points
    """
    # Placeholder return
    return f"📰 {category.upper()} News Digest\n• Headline 1\n• Headline 2\n• Headline 3"

# ─── Weather + Fuel Placeholder ──────────────────────────────
async def fetch_weather_fuel() -> str:
    """TODO: Weather API + Fuel Price API se data fetch karo"""
    return "🌤️ Weather: Clear, 32°C\n⛽ Petrol: ₹96.50 | Diesel: ₹89.20"

# ─── Rozgar/Jobs Placeholder ─────────────────────────────────
async def fetch_rozgar_updates() -> str:
    """TODO: Rozgar APIs se fresh job listings fetch karo"""
    return "💼 Rozgar Updates\n• 50+ Govt Jobs Posted Today\n• Last Date: 30 July 2026"

# ─── Govt Schemes Placeholder ────────────────────────────────
async def fetch_govt_schemes() -> str:
    """TODO: Ration card, eligibility, new schemes"""
    return "🏛️ Govt Schemes Update\n• New PM Awas Yojana List\n• Ration Card Eligibility Check"

# ─── Banking Placeholder ─────────────────────────────────────
async def fetch_banking_updates() -> str:
    """TODO: RBI rates, new bank schemes"""
    return "🏦 Banking Weekly\n• FD Rates Updated\n• New Digital Loan Scheme"

# ─── Social Media Promo Placeholder ──────────────────────────
async def generate_social_content() -> str:
    """TODO: Auto-generate carousel/post content for IG/Twitter"""
    return "📱 Social Media Content Ready\n• 3 Carousel Slides Generated\n• Caption + Hashtags Ready"

# ─── Tenders Placeholder ─────────────────────────────────────
async def fetch_tender_info() -> str:
    """TODO: Govt tender portals se data"""
    return "📋 Tender Alert\n• New Road Construction Tender\n• Last Date: 15 Aug 2026"

# ═════════════════════════════════════════════════════════════
#                    JOB HANDLERS
# ═════════════════════════════════════════════════════════════

async def job_morning_digest():
    """7:00 AM — News + Weather + Fuel (Combined)"""
    logger.info("🌅 Running Morning Digest...")
    try:
        news = await fetch_and_summarize_news("all")
        weather = await fetch_weather_fuel()
        
        message = (
            f"🌅 *Singh Ji Morning Digest* — {datetime.now().strftime('%d %b, %A')}\n\n"
            f"{news}\n\n"
            f"{weather}\n\n"
            f"— Singh Ji AI Ultra"
        )
        await send_telegram_broadcast(message)
        update_job_state("morning_digest", "success", "Tomorrow 7:00 AM")
        logger.info("✅ Morning Digest sent")
    except Exception as e:
        logger.error(f"❌ Morning Digest failed: {e}")
        update_job_state("morning_digest", "failed")

async def job_evening_digest():
    """6:00 PM — News Update + Rozgar (Combined)"""
    logger.info("🌆 Running Evening Digest...")
    try:
        news = await fetch_and_summarize_news("all")
        rozgar = await fetch_rozgar_updates()
        
        message = (
            f"🌆 *Singh Ji Evening Digest* — {datetime.now().strftime('%d %b')}\n\n"
            f"{news}\n\n"
            f"{rozgar}\n\n"
            f"— Singh Ji AI Ultra"
        )
        await send_telegram_broadcast(message)
        update_job_state("evening_digest", "success", "Tomorrow 6:00 PM")
        logger.info("✅ Evening Digest sent")
    except Exception as e:
        logger.error(f"❌ Evening Digest failed: {e}")
        update_job_state("evening_digest", "failed")

async def job_govt_schemes():
    """Tuesday & Friday — Govt Schemes"""
    logger.info("🏛️ Running Govt Schemes Update...")
    try:
        content = await fetch_govt_schemes()
        message = f"🏛️ *Sarkari Yojana Update*\n\n{content}"
        await send_telegram_broadcast(message)
        update_job_state("govt_schemes", "success")
        logger.info("✅ Govt Schemes sent")
    except Exception as e:
        logger.error(f"❌ Govt Schemes failed: {e}")
        update_job_state("govt_schemes", "failed")

async def job_banking_weekly():
    """Weekly — Banking Updates"""
    logger.info("🏦 Running Banking Update...")
    try:
        content = await fetch_banking_updates()
        message = f"🏦 *Banking Weekly Update*\n\n{content}"
        await send_telegram_broadcast(message)
        update_job_state("banking_weekly", "success")
        logger.info("✅ Banking Update sent")
    except Exception as e:
        logger.error(f"❌ Banking Update failed: {e}")
        update_job_state("banking_weekly", "failed")

async def job_social_media_promo():
    """Weekly 3x — Social Media Content"""
    logger.info("📱 Running Social Media Promo...")
    try:
        content = await generate_social_content()
        message = f"📱 *Social Media Content Ready*\n\n{content}"
        await send_telegram_broadcast(message)
        update_job_state("social_promo", "success")
        logger.info("✅ Social Promo sent")
    except Exception as e:
        logger.error(f"❌ Social Promo failed: {e}")
        update_job_state("social_promo", "failed")

async def job_monthly_tenders():
    """Monthly — Govt Tenders"""
    logger.info("📋 Running Monthly Tenders...")
    try:
        content = await fetch_tender_info()
        message = f"📋 *Monthly Tender Alert*\n\n{content}"
        await send_telegram_broadcast(message)
        update_job_state("monthly_tenders", "success")
        logger.info("✅ Tenders sent")
    except Exception as e:
        logger.error(f"❌ Tenders failed: {e}")
        update_job_state("monthly_tenders", "failed")

# ─── Railway Sleep Prevention ────────────────────────────────
async def self_ping():
    """
    Railway free tier ko jagaye rakhta hai.
    Apne app ka health endpoint har 10 min mein ping karta hai.
    """
    app_url = os.getenv("APP_URL", "https://your-railway-url.railway.app")
    ping_url = f"{app_url}/health"
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(ping_url, timeout=10) as resp:
                if resp.status == 200:
                    logger.debug("Self-ping OK")
                else:
                    logger.warning(f"Self-ping returned {resp.status}")
    except Exception as e:
        logger.warning(f"Self-ping failed (Railway might be sleeping): {e}")

# ─── Scheduler Event Listeners ───────────────────────────────
def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} crashed: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} completed")

# ═════════════════════════════════════════════════════════════
#                    SCHEDULER SETUP
# ═════════════════════════════════════════════════════════════

class SinghJiMasterScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        init_db()
    
    def setup_jobs(self):
        """Sare jobs register karo — yahan se sab control hota hai"""
        
        # ─── DAILY ─────────────────────────────────────────────
        
        # 7:00 AM — Morning Digest (News + Weather + Fuel)
        self.scheduler.add_job(
            job_morning_digest,
            CronTrigger(hour=7, minute=0),
            id="morning_digest",
            name="Morning News + Weather + Fuel",
            replace_existing=True,
            misfire_grace_time=3600  # 1 hour late bhi chalega
        )
        
        # 6:00 PM — Evening Digest (News + Rozgar)
        self.scheduler.add_job(
            job_evening_digest,
            CronTrigger(hour=18, minute=0),
            id="evening_digest",
            name="Evening News + Rozgar",
            replace_existing=True,
            misfire_grace_time=3600
        )
        
        # ─── WEEKLY ────────────────────────────────────────────
        
        # Tuesday & Friday — Govt Schemes (3:00 PM)
        self.scheduler.add_job(
            job_govt_schemes,
            CronTrigger(day_of_week="tue,fri", hour=15, minute=0),
            id="govt_schemes",
            name="Govt Schemes Update",
            replace_existing=True
        )
        
        # Weekly — Banking (Monday 11:00 AM)
        self.scheduler.add_job(
            job_banking_weekly,
            CronTrigger(day_of_week="mon", hour=11, minute=0),
            id="banking_weekly",
            name="Banking Weekly Update",
            replace_existing=True
        )
        
        # Weekly 3x — Social Media Promo (Mon, Wed, Sat 10:00 AM)
        self.scheduler.add_job(
            job_social_media_promo,
            CronTrigger(day_of_week="mon,wed,sat", hour=10, minute=0),
            id="social_promo",
            name="Social Media Promo",
            replace_existing=True
        )
        
        # ─── MONTHLY ───────────────────────────────────────────
        
        # Monthly — Tenders (1st of month, 9:00 AM)
        self.scheduler.add_job(
            job_monthly_tenders,
            CronTrigger(day=1, hour=9, minute=0),
            id="monthly_tenders",
            name="Monthly Tender Alert",
            replace_existing=True
        )
        
        # ─── RAILWAY SLEEP FIX ─────────────────────────────────
        
        # Har 10 min mein self-ping
        self.scheduler.add_job(
            self_ping,
            "interval",
            minutes=10,
            id="self_ping",
            name="Railway Sleep Prevention",
            replace_existing=True
        )
        
        logger.info("✅ All jobs registered successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Scheduler ka current status"""
        jobs = self.scheduler.get_jobs()
        job_list = []
        for job in jobs:
            job_list.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": job_list,
            "timezone": "Asia/Kolkata"
        }
    
    async def start(self):
        """Scheduler start karo"""
        self.setup_jobs()
        self.scheduler.start()
        logger.info("🚀 Singh Ji Master Scheduler STARTED")
        
        # Startup pe ek baar status print karo
        status = self.get_status()
        for job in status["jobs"]:
            logger.info(f"  ⏰ {job['name']} → Next: {job['next_run']}")
    
    async def stop(self):
        """Scheduler band karo"""
        self.scheduler.shutdown()
        logger.info("🛑 Singh Ji Master Scheduler STOPPED")


# ═════════════════════════════════════════════════════════════
#              FASTAPI LIFESPAN INTEGRATION
# ═════════════════════════════════════════════════════════════

"""
TODO: Apne main.py mein yeh lifespan event daalna:

from contextlib import asynccontextmanager
from fastapi import FastAPI
from singhji_master_scheduler import SinghJiMasterScheduler

scheduler = SinghJiMasterScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await scheduler.start()
    yield
    # Shutdown
    await scheduler.stop()

app = FastAPI(lifespan=lifespan)

# Healthcheck endpoint (Railway ke liye zaroori)
@app.get("/health")
async def health():
    return {"status": "ok", "scheduler": scheduler.get_status()}
"""

# ─── Direct Run (for testing) ────────────────────────────────
if __name__ == "__main__":
    async def test_run():
        s = SinghJiMasterScheduler()
        await s.start()
        
        # 5 min chal ke dikhao test ke liye
        logger.info("Scheduler running for 5 minutes (test mode)...")
        await asyncio.sleep(300)
        await s.stop()
    
    asyncio.run(test_run())
