"""
╔═══════════════════════════════════════════════════════════════╗
║         SINGH JI AI ULTRA - MASTER SCHEDULER                  ║
║         सारे शेड्यूल एक साथ                                  ║
╚═══════════════════════════════════════════════════════════════╝

बदलाव (इस पैच में):
  1. सभी placeholder fetch फ़ंक्शन असली मॉड्यूल से जोड़े गए
     (news.py → singhji_news, weather/rozgar → अपने असली इम्पोर्ट पाथ भरें)
  2. send_telegram_broadcast असली python-telegram-bot Bot इंस्टेंस
     से भेजता है, अब सिर्फ़ लॉग नहीं करता
  3. Supabase से active chat_id लिस्ट खींचता है (टेबल नाम अपने हिसाब
     से बदलें — नीचे CHAT_ID_TABLE / CHAT_ID_COLUMN में मार्क किया है)
"""

import os
import sys
import asyncio
import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from telegram import Bot
from telegram.error import TelegramError

# ─── असली मॉड्यूल इम्पोर्ट — अपने प्रोजेक्ट की सही पाथ के हिसाब से जाँच लें ───
from modules.news import singhji_news          # modules/news.py में मौजूद सिंगलटन

# TODO: अगर weather और rozgar मॉड्यूल का फ़ंक्शन नाम/पाथ अलग है तो यहाँ बदलें
try:
    from modules.weather import get_weather_and_fuel   # expected: async def get_weather_and_fuel(city: str) -> dict
except ImportError:
    get_weather_and_fuel = None
    logging.getLogger("SinghJiScheduler").warning(
        "⚠️ modules.weather.get_weather_and_fuel नहीं मिला — weather digest fallback text इस्तेमाल होगा"
    )

try:
    from modules.rozgar import search_jobs              # expected: async def search_jobs(**filters) -> list[dict]
except ImportError:
    search_jobs = None
    logging.getLogger("SinghJiScheduler").warning(
        "⚠️ modules.rozgar.search_jobs नहीं मिला — rozgar digest fallback text इस्तेमाल होगा"
    )

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

# ─── Telegram Bot — असली इंस्टेंस ────────────────────────────
_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
_bot: Optional[Bot] = Bot(token=_bot_token) if _bot_token else None
if not _bot:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN env var missing — broadcast disabled रहेगा")

# TODO: अपने Supabase टेबल/कॉलम नाम के हिसाब से यह दो लाइन ठीक करें
CHAT_ID_TABLE = "telegram_subscribers"
CHAT_ID_COLUMN = "chat_id"

async def get_active_chat_ids() -> List[int]:
    """Supabase से broadcast के लिए active chat_id लिस्ट लाओ"""
    try:
        from core.supabase_client import get_supabase_client  # अपने असली helper से बदलें
        sb = get_supabase_client()
        resp = sb.table(CHAT_ID_TABLE).select(CHAT_ID_COLUMN).eq("active", True).execute()
        return [row[CHAT_ID_COLUMN] for row in (resp.data or [])]
    except Exception as e:
        logger.error(f"chat_id लिस्ट लाने में त्रुटि: {e}")
        return []

async def send_telegram_broadcast(message: str, chat_ids: Optional[List[int]] = None) -> bool:
    """असली Telegram broadcast — हर chat_id को अलग से भेजता है ताकि एक फेल होने पर बाकी न रुकें"""
    if not _bot:
        logger.warning(f"[TELEGRAM DISABLED] Would send: {message[:80]}...")
        return False

    ids = chat_ids if chat_ids is not None else await get_active_chat_ids()
    if not ids:
        logger.warning("कोई active chat_id नहीं मिला — broadcast स्किप हुआ")
        return False

    sent, failed = 0, 0
    for cid in ids:
        try:
            await _bot.send_message(chat_id=cid, text=message, parse_mode="Markdown")
            sent += 1
        except TelegramError as e:
            failed += 1
            logger.warning(f"chat_id {cid} को भेजने में त्रुटि: {e}")
        await asyncio.sleep(0.05)  # Telegram rate-limit से बचने के लिए

    logger.info(f"📤 Broadcast पूरा — भेजा: {sent}, फेल: {failed}")
    return sent > 0

# ─── News Aggregation — असली मॉड्यूल से ──────────────────────
async def fetch_and_summarize_news(category: str = "all") -> str:
    keywords = "" if category == "all" else category
    result = await singhji_news.get_news(keywords=keywords, num=4, country="in", lang="hi")
    if not result.articles:
        return "📰 आज कोई ताज़ा खबर उपलब्ध नहीं है।"
    lines = [f"📰 समाचार अपडेट ({result.source})"]
    for a in result.articles[:4]:
        title = a.get("title", "").strip()
        if title:
            lines.append(f"• {title}")
    return "\n".join(lines)

# ─── Weather + Fuel — असली मॉड्यूल से (उपलब्ध हो तो) ─────────
async def fetch_weather_fuel(city: str = "Kanpur") -> str:
    if get_weather_and_fuel is None:
        return "🌤️ मौसम/ईंधन मॉड्यूल अभी जुड़ा नहीं है (TODO)"
    try:
        data = await get_weather_and_fuel(city)
        return (
            f"🌤️ {city}: {data.get('condition', '—')}, {data.get('temp_c', '—')}°C\n"
            f"⛽ पेट्रोल: ₹{data.get('petrol', '—')} | डीज़ल: ₹{data.get('diesel', '—')}"
        )
    except Exception as e:
        logger.error(f"weather fetch fail: {e}")
        return "🌤️ मौसम/ईंधन जानकारी अभी उपलब्ध नहीं"

# ─── Rozgar/Jobs — असली मॉड्यूल से (उपलब्ध हो तो) ────────────
async def fetch_rozgar_updates() -> str:
    if search_jobs is None:
        return "💼 रोज़गार मॉड्यूल अभी जुड़ा नहीं है (TODO)"
    try:
        jobs = await search_jobs(country="in", limit=3)
        if not jobs:
            return "💼 आज कोई नई नौकरी लिस्टिंग नहीं मिली"
        lines = ["💼 रोज़गार अपडेट"]
        for j in jobs[:3]:
            lines.append(f"• {j.get('title', 'नौकरी')} — {j.get('company', '')}")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"rozgar fetch fail: {e}")
        return "💼 रोज़गार जानकारी अभी उपलब्ध नहीं"

# ─── बाकी मॉड्यूल अभी placeholder हैं — जैसे-जैसे बनें, ऊपर जैसे wire करें ───
async def fetch_govt_schemes() -> str:
    """TODO: sarkari_yojana मॉड्यूल से असली डेटा जोड़ें"""
    return "🏛️ सरकारी योजना अपडेट (मॉड्यूल जुड़ना बाकी है)"

async def fetch_banking_updates() -> str:
    """TODO: banking मॉड्यूल से असली डेटा जोड़ें"""
    return "🏦 बैंकिंग साप्ताहिक अपडेट (मॉड्यूल जुड़ना बाकी है)"

async def generate_social_content() -> str:
    """TODO: aavishkar/image_gen मॉड्यूल से असली कंटेंट जोड़ें"""
    return "📱 सोशल मीडिया कंटेंट तैयार (मॉड्यूल जुड़ना बाकी है)"

async def fetch_tender_info() -> str:
    """TODO: govt tender पोर्टल स्क्रैपर जोड़ें"""
    return "📋 टेंडर अलर्ट (मॉड्यूल जुड़ना बाकी है)"

# ═════════════════════════════════════════════════════════════
#                    JOB HANDLERS
# ═════════════════════════════════════════════════════════════

async def job_morning_digest():
    logger.info("🌅 Running Morning Digest...")
    try:
        news = await fetch_and_summarize_news("all")
        weather = await fetch_weather_fuel()
        message = (
            f"🌅 *Singh Ji Morning Digest* — {datetime.now().strftime('%d %b, %A')}\n\n"
            f"{news}\n\n{weather}\n\n— Singh Ji AI Ultra"
        )
        ok = await send_telegram_broadcast(message)
        update_job_state("morning_digest", "success" if ok else "no_recipients", "Tomorrow 7:00 AM")
        logger.info("✅ Morning Digest sent" if ok else "⚠️ Morning Digest: कोई recipient नहीं")
    except Exception as e:
        logger.error(f"❌ Morning Digest failed: {e}")
        update_job_state("morning_digest", "failed")

async def job_evening_digest():
    logger.info("🌆 Running Evening Digest...")
    try:
        news = await fetch_and_summarize_news("all")
        rozgar = await fetch_rozgar_updates()
        message = (
            f"🌆 *Singh Ji Evening Digest* — {datetime.now().strftime('%d %b')}\n\n"
            f"{news}\n\n{rozgar}\n\n— Singh Ji AI Ultra"
        )
        ok = await send_telegram_broadcast(message)
        update_job_state("evening_digest", "success" if ok else "no_recipients", "Tomorrow 6:00 PM")
        logger.info("✅ Evening Digest sent" if ok else "⚠️ Evening Digest: कोई recipient नहीं")
    except Exception as e:
        logger.error(f"❌ Evening Digest failed: {e}")
        update_job_state("evening_digest", "failed")

async def job_govt_schemes():
    logger.info("🏛️ Running Govt Schemes Update...")
    try:
        content = await fetch_govt_schemes()
        ok = await send_telegram_broadcast(f"🏛️ *Sarkari Yojana Update*\n\n{content}")
        update_job_state("govt_schemes", "success" if ok else "no_recipients")
    except Exception as e:
        logger.error(f"❌ Govt Schemes failed: {e}")
        update_job_state("govt_schemes", "failed")

async def job_banking_weekly():
    logger.info("🏦 Running Banking Update...")
    try:
        content = await fetch_banking_updates()
        ok = await send_telegram_broadcast(f"🏦 *Banking Weekly Update*\n\n{content}")
        update_job_state("banking_weekly", "success" if ok else "no_recipients")
    except Exception as e:
        logger.error(f"❌ Banking Update failed: {e}")
        update_job_state("banking_weekly", "failed")

async def job_social_media_promo():
    logger.info("📱 Running Social Media Promo...")
    try:
        content = await generate_social_content()
        ok = await send_telegram_broadcast(f"📱 *Social Media Content Ready*\n\n{content}")
        update_job_state("social_promo", "success" if ok else "no_recipients")
    except Exception as e:
        logger.error(f"❌ Social Promo failed: {e}")
        update_job_state("social_promo", "failed")

async def job_monthly_tenders():
    logger.info("📋 Running Monthly Tenders...")
    try:
        content = await fetch_tender_info()
        ok = await send_telegram_broadcast(f"📋 *Monthly Tender Alert*\n\n{content}")
        update_job_state("monthly_tenders", "success" if ok else "no_recipients")
    except Exception as e:
        logger.error(f"❌ Tenders failed: {e}")
        update_job_state("monthly_tenders", "failed")

# ─── Railway Sleep Prevention ────────────────────────────────
async def self_ping():
    app_url = os.getenv("APP_URL", "https://your-railway-url.railway.app")
    ping_url = f"{app_url}/health"
    try:
        async with __import__("httpx").AsyncClient(timeout=10) as client:
            resp = await client.get(ping_url)
            if resp.status_code == 200:
                logger.debug("Self-ping OK")
            else:
                logger.warning(f"Self-ping returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Self-ping failed (Railway might be sleeping): {e}")

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
        self.scheduler.add_job(
            job_morning_digest, CronTrigger(hour=7, minute=0),
            id="morning_digest", name="Morning News + Weather + Fuel",
            replace_existing=True, misfire_grace_time=3600
        )
        self.scheduler.add_job(
            job_evening_digest, CronTrigger(hour=18, minute=0),
            id="evening_digest", name="Evening News + Rozgar",
            replace_existing=True, misfire_grace_time=3600
        )
        self.scheduler.add_job(
            job_govt_schemes, CronTrigger(day_of_week="tue,fri", hour=15, minute=0),
            id="govt_schemes", name="Govt Schemes Update", replace_existing=True
        )
        self.scheduler.add_job(
            job_banking_weekly, CronTrigger(day_of_week="mon", hour=11, minute=0),
            id="banking_weekly", name="Banking Weekly Update", replace_existing=True
        )
        self.scheduler.add_job(
            job_social_media_promo, CronTrigger(day_of_week="mon,wed,sat", hour=10, minute=0),
            id="social_promo", name="Social Media Promo", replace_existing=True
        )
        self.scheduler.add_job(
            job_monthly_tenders, CronTrigger(day=1, hour=9, minute=0),
            id="monthly_tenders", name="Monthly Tender Alert", replace_existing=True
        )
        self.scheduler.add_job(
            self_ping, "interval", minutes=10,
            id="self_ping", name="Railway Sleep Prevention", replace_existing=True
        )
        logger.info("✅ All jobs registered successfully")

    def get_status(self) -> Dict[str, Any]:
        jobs = self.scheduler.get_jobs()
        job_list = [{
            "id": job.id, "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger)
        } for job in jobs]
        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": job_list,
            "timezone": "Asia/Kolkata"
        }

    async def start(self):
        if self.scheduler.running:
            logger.info("Scheduler पहले से चल रहा है")
            return
        self.setup_jobs()
        self.scheduler.start()
        logger.info("🚀 Singh Ji Master Scheduler STARTED")
        for job in self.get_status()["jobs"]:
            logger.info(f"  ⏰ {job['name']} → Next: {job['next_run']}")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
        logger.info("🛑 Singh Ji Master Scheduler STOPPED")


# ═════════════════════════════════════════════════════════════
#   सिंगलटन — main.py और schedule control रूट दोनों यहीं से import करें
# ═════════════════════════════════════════════════════════════
scheduler = SinghJiMasterScheduler()


if __name__ == "__main__":
    async def test_run():
        await scheduler.start()
        logger.info("Scheduler 5 मिनट टेस्ट मोड में चल रहा है...")
        await asyncio.sleep(300)
        await scheduler.stop()

    asyncio.run(test_run())
