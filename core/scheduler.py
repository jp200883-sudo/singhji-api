
import os
import sqlite3
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from core.config import OPENWEATHER_API_KEY, APP_URL
from core.database import SUPABASE_CLIENT
from utils.helpers import _normalize_state

logger = logging.getLogger(__name__)

MASTER_SCHEDULER = None
USER_PREFERENCES = {}

GOLD_API_KEY = os.getenv("GOLD_API_KEY", "")
SILVER_API_KEY = os.getenv("SILVER_API_KEY", "")

def _load_user_preferences_sync() -> Dict[int, Any]:
    loaded: Dict[int, Any] = {}
    if not SUPABASE_CLIENT:
        logger.warning("Supabase not connected")
        return loaded
    try:
        resp = SUPABASE_CLIENT.table("user_memory").select("*").execute()
        for row in (resp.data or []):
            key = row.get("key", "")
            if not key.startswith("user_pref:"):
                continue
            try:
                uid = int(key.split(":", 1)[1])
            except (IndexError, ValueError):
                continue
            loaded[uid] = row.get("value") or {"language": "hi", "location": None}
        logger.info(f"Loaded {len(loaded)} subscribers from Supabase")
    except Exception as e:
        logger.error(f"User preferences reload failed: {e}")
    return loaded

class SinghJiMasterScheduler:
    def __init__(self, http_client, telegram_send_func, api_keys, modules, user_preferences, admin_user_id=0):
        self.http = http_client
        self.send_tg = telegram_send_func
        self.keys = api_keys
        self.modules = modules
        self.users = user_preferences
        self.admin_uid = admin_user_id
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        self._init_db()

    def _init_db(self):
        db_path = os.getenv("SCHEDULER_DB", "scheduler_state.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
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

    def _update_state(self, job_name, status, next_run=None):
        try:
            db_path = os.getenv("SCHEDULER_DB", "scheduler_state.db")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            c = conn.cursor()
            now = datetime.now().isoformat()
            c.execute("""
                INSERT INTO scheduler_state (job_name, last_run, status, next_run)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(job_name) DO UPDATE SET
                    last_run=excluded.last_run,
                    status=excluded.status,
                    next_run=excluded.next_run,
                    retry_count=retry_count + CASE WHEN excluded.status='failed' THEN 1 ELSE 0 END
            """, (job_name, now, status, next_run))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB state update failed: {e}")

    def _job_listener(self, event):
        if event.exception:
            logger.error(f"Job {event.job_id} crashed: {event.exception}")
            self._update_state(event.job_id, "failed")
        else:
            logger.info(f"Job {event.job_id} completed successfully")
            self._update_state(event.job_id, "success")

    async def _broadcast_with_rate_limit(self, message, parse_mode="Markdown"):
        if not self.users:
            logger.warning("No users to broadcast to")
            return
        user_ids = list(self.users.keys())
        logger.info(f"Broadcasting to {len(user_ids)} users")
        batch_size = 20
        success_count = 0
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i+batch_size]
            tasks = []
            for uid in batch:
                tasks.append(self.send_tg(self.http, uid, message, parse_mode=parse_mode))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count += sum(1 for r in results if not isinstance(r, Exception))
            if i + batch_size < len(user_ids):
                await asyncio.sleep(1)
        logger.info(f"Broadcast sent to {success_count}/{len(user_ids)} users")

    # ==============================================================
    #  FETCH FUNCTIONS
    # ==============================================================
    async def _fetch_gold(self):
        try:
            url = "https://www.goldapi.io/api/XAU/INR"
            headers = {"x-access-token": GOLD_API_KEY} if GOLD_API_KEY else {}
            r = await self.http.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                price_gram_24k = data.get("price_gram_24k", 0)
                price_gram_22k = data.get("price_gram_22k", 0)
                return (
                    f"🥇 *Gold Rate (Kanpur)*\n\n"
                    f"24K (1g): ₹{price_gram_24k:.2f}\n"
                    f"22K (1g): ₹{price_gram_22k:.2f}\n"
                    f"24K (10g): ₹{price_gram_24k * 10:.2f}\n"
                    f"Updated: {datetime.now().strftime('%H:%M')}"
                )
        except Exception as e:
            logger.warning(f"Gold API failed: {e}")
        return f"🥇 *Gold Rate (Kanpur)*\n\n24K (1g): ₹7,650\n22K (1g): ₹7,015\n\n⚠️ Live API failed"

    async def _fetch_silver(self):
        try:
            url = "https://www.goldapi.io/api/XAG/INR"
            headers = {"x-access-token": SILVER_API_KEY} if SILVER_API_KEY else {}
            r = await self.http.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                price_gram = data.get("price_gram", 0)
                return (
                    f"🥈 *Silver Rate (Kanpur)*\n\n"
                    f"1g: ₹{price_gram:.2f}\n"
                    f"10g: ₹{price_gram * 10:.2f}\n"
                    f"1kg: ₹{price_gram * 1000:.2f}\n"
                    f"Updated: {datetime.now().strftime('%H:%M')}"
                )
        except Exception as e:
            logger.warning(f"Silver API failed: {e}")
        return f"🥈 *Silver Rate (Kanpur)*\n\n1g: ₹92.50\n10g: ₹925\n1kg: ₹92,500\n\n⚠️ Live API failed"

    async def _fetch_copper(self):
        try:
            url = "https://api.metals.live/v1/spot"
            r = await self.http.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                copper = data.get("copper", 0)
                return f"🔶 *Copper Rate*\n\nSpot: ${copper:.4f}/lb\nUpdated: {datetime.now().strftime('%H:%M')}"
        except Exception as e:
            logger.warning(f"Copper API failed: {e}")
        return f"🔶 *Copper Rate*\n\nSpot: $4.15/lb\n\n⚠️ Live API failed"

    async def _fetch_iron(self):
        try:
            url = "https://api.metals.live/v1/spot"
            r = await self.http.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                iron = data.get("iron", 0)
                return f"⚫ *Iron/Steel Rate*\n\nSpot: ${iron:.2f}/tonne\nUpdated: {datetime.now().strftime('%H:%M')}"
        except Exception as e:
            logger.warning(f"Iron API failed: {e}")
        return f"⚫ *Iron/Steel Rate*\n\nTMT Bars (10mm): ₹58,500/tonne\nMS Plates: ₹52,000/tonne\n\n⚠️ Live API failed"

    async def _fetch_aluminium(self):
        try:
            url = "https://api.metals.live/v1/spot"
            r = await self.http.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                aluminium = data.get("aluminium", 0)
                return f"🔷 *Aluminium Rate*\n\nSpot: ${aluminium:.4f}/lb\nUpdated: {datetime.now().strftime('%H:%M')}"
        except Exception as e:
            logger.warning(f"Aluminium API failed: {e}")
        return f"🔷 *Aluminium Rate*\n\nSpot: $1.05/lb\n\n⚠️ Live API failed"

    async def _fetch_fuel(self):
        try:
            url = "https://daily-petrol-diesel-lpg-cng-fuel-prices-in-india.p.rapidapi.com/v1/fuel-prices/today"
            headers = {
                "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),
                "X-RapidAPI-Host": "daily-petrol-diesel-lpg-cng-fuel-prices-in-india.p.rapidapi.com"
            }
            r = await self.http.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                up = data.get("Uttar Pradesh", {})
                petrol = up.get("petrol", "N/A")
                diesel = up.get("diesel", "N/A")
                cng = up.get("cng", "N/A")
                return (
                    f"⛽ *Fuel Rates (Kanpur, UP)*\n\n"
                    f"🛢️ Petrol: ₹{petrol}/L\n"
                    f"🛢️ Diesel: ₹{diesel}/L\n"
                    f"🔥 CNG: ₹{cng}/kg\n"
                    f"Updated: {datetime.now().strftime('%H:%M')}"
                )
        except Exception as e:
            logger.warning(f"Fuel API failed: {e}")
        return (
            f"⛽ *Fuel Rates (Kanpur, UP)*\n\n"
            f"🛢️ Petrol: ₹96.50/L\n"
            f"🛢️ Diesel: ₹89.75/L\n"
            f"🔥 CNG: ₹82.00/kg\n"
            f"\n⚠️ Live API failed"
        )

    async def _fetch_news(self, count=5):
        try:
            import modules.news.handler as news_module
            return await news_module.get_news_digest_text(count=count)
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")
            return f"News error: {str(e)[:150]}"

    async def _fetch_weather(self, city="Delhi"):
        if not OPENWEATHER_API_KEY:
            return "Weather API key missing"
        try:
            key = OPENWEATHER_API_KEY
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            r = await self.http.get(url, timeout=15)
            data = r.json()
            if r.status_code == 200:
                return (
                    f"Temp: {data['main']['temp']}°C (Feel: {data['main']['feels_like']}°C)\n"
                    f"Humidity: {data['main']['humidity']}%\n"
                    f"Wind: {data['wind']['speed']} m/s\n"
                    f"{data['weather'][0]['description'].title()}"
                )
            return f"Weather error: {data.get('message', 'Unknown')}"
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")
            return "Weather fetch failed"

    async def _fetch_mandi(self, state="Uttar Pradesh", limit=5):
        from core.config import DATAGOVINDIA_API_KEY
        if not DATAGOVINDIA_API_KEY:
            return "Mandi API key missing"
        try:
            normalized = _normalize_state(state)
            resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
            url = f"https://api.data.gov.in/resource/{resource_id}"
            params = {"api-key": DATAGOVINDIA_API_KEY, "format": "json", "limit": limit, "filters[state.keyword]": normalized}
            r = await self.http.get(url, params=params, timeout=45)
            data = r.json()
            if "error" in data:
                return f"Mandi API error: {data.get('error', 'Unknown')}"
            records = data.get("records", [])
            if not records:
                return f"{normalized} ke liye aaj mandi data available nahi hai"
            lines = [f"🌾 *Mandi Bhav — {normalized}*\n"]
            for rec in records[:limit]:
                commodity = rec.get("commodity", "?")
                market = rec.get("market", "?")
                district = rec.get("district", "")
                price = rec.get("modal_price", "?")
                min_p = rec.get("min_price", "?")
                max_p = rec.get("max_price", "?")
                date = rec.get("arrival_date", "")
                lines.append(f"*{commodity}* — ₹{price}/q")
                lines.append(f"📍 {market}, {district}")
                lines.append(f"Range: ₹{min_p} - ₹{max_p}")
                if date:
                    lines.append(f"📅 {date}")
                lines.append("")
            return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Mandi fetch failed: {e}")
            return f"Mandi error: {str(e)[:100]}"

    # ==============================================================
    #  JOBS
    # ==============================================================
    async def _job_morning_digest_555(self):
        logger.info("Morning Digest (5:55 AM) starting...")
        news = await self._fetch_news(5)
        weather = await self._fetch_weather("Delhi")
        mandi = await self._fetch_mandi("Uttar Pradesh", limit=5)
        msg = (
            f"🌅 *Good Morning!*\n"
            f"📅 {datetime.now().strftime('%d %b %Y, %A')}\n\n"
            f"📰 *News:*\n{news}\n\n"
            f"🌤️ *Weather (Delhi):*\n{weather}\n\n"
            f"🌾 *Mandi (UP):*\n{mandi}\n\n"
            f"— Singh Ji AI"
        )
        await self._broadcast_with_rate_limit(msg)
        self._update_state("morning_digest_555", "success", "Tomorrow 05:55 AM")
        logger.info("Morning Digest (5:55 AM) completed")

    async def _job_commodity_digest_655(self):
        logger.info("Commodity Digest (6:55 AM) starting...")
        gold = await self._fetch_gold()
        silver = await self._fetch_silver()
        copper = await self._fetch_copper()
        iron = await self._fetch_iron()
        aluminium = await self._fetch_aluminium()
        fuel = await self._fetch_fuel()
        msg = (
            f"📊 *Aaj Ke Bhav*\n"
            f"📅 {datetime.now().strftime('%d %b %Y')}\n\n"
            f"{gold}\n\n"
            f"{silver}\n\n"
            f"{copper}\n\n"
            f"{iron}\n\n"
            f"{aluminium}\n\n"
            f"{fuel}\n\n"
            f"— Singh Ji AI"
        )
        await self._broadcast_with_rate_limit(msg)
        self._update_state("commodity_digest_655", "success", "Tomorrow 06:55 AM")
        logger.info("Commodity Digest (6:55 AM) completed")

    async def _job_evening_digest(self):
        logger.info("Evening Digest (6:00 PM) starting...")
        news = await self._fetch_news(5)
        msg = (
            f"🌆 *Good Evening!*\n"
            f"📅 {datetime.now().strftime('%d %b %Y')}\n\n"
            f"📰 *News:*\n{news}\n\n"
            f"— Singh Ji AI"
        )
        await self._broadcast_with_rate_limit(msg)
        self._update_state("evening_digest", "success", "Tomorrow 06:00 PM")
        logger.info("Evening Digest (6:00 PM) completed")

    # ==============================================================
    #  KEEP ALIVE — 10 MIN BEFORE SCHEDULE
    # ==============================================================
    async def _self_ping(self):
        """Keep Render awake — every 10 min (before 5:55 AM & 6:55 AM)"""
        if not APP_URL:
            return
        try:
            r = await self.http.get(f"{APP_URL}/health", timeout=10)
            if r.status_code != 200:
                logger.warning(f"Self-ping status {r.status_code}")
            else:
                logger.info(f"Self-ping OK: {r.status_code}")
        except Exception as e:
            logger.warning(f"Self-ping failed: {e}")

    async def _pre_morning_ping(self):
        """Extra ping at 5:45 AM — 10 min before Morning Digest"""
        logger.info("Pre-morning ping at 5:45 AM...")
        await self._self_ping()
        logger.info("Pre-morning ping done — server awake for 5:55 AM digest")

    async def _pre_commodity_ping(self):
        """Extra ping at 6:45 AM — 10 min before Commodity Digest"""
        logger.info("Pre-commodity ping at 6:45 AM...")
        await self._self_ping()
        logger.info("Pre-commodity ping done — server awake for 6:55 AM digest")

    # ==============================================================
    #  SETUP ALL JOBS — v9.1
    # ==============================================================
    def setup(self):
        jobs = [
            # === MAIN DIGESTS ===
            {
                "id": "morning_digest_555",
                "func": self._job_morning_digest_555,
                "trigger": CronTrigger(hour=5, minute=55),
                "name": "Morning Digest (5:55 AM)",
                "misfire_grace_time": 3600
            },
            {
                "id": "commodity_digest_655",
                "func": self._job_commodity_digest_655,
                "trigger": CronTrigger(hour=6, minute=55),
                "name": "Commodity Digest (6:55 AM)",
                "misfire_grace_time": 3600
            },
            {
                "id": "evening_digest",
                "func": self._job_evening_digest,
                "trigger": CronTrigger(hour=18, minute=0),
                "name": "Evening Digest (6:00 PM)",
                "misfire_grace_time": 3600
            },
            # === KEEP ALIVE — 10 MIN BEFORE SCHEDULE ===
            {
                "id": "self_ping",
                "func": self._self_ping,
                "trigger": IntervalTrigger(minutes=10),  # ← 10 min (was 15)
                "name": "Keep Alive (10 min)",
                "misfire_grace_time": 60
            },
            {
                "id": "pre_morning_ping",
                "func": self._pre_morning_ping,
                "trigger": CronTrigger(hour=5, minute=45),  # ← 10 min before 5:55
                "name": "Pre-Morning Ping (5:45 AM)",
                "misfire_grace_time": 300
            },
            {
                "id": "pre_commodity_ping",
                "func": self._pre_commodity_ping,
                "trigger": CronTrigger(hour=6, minute=45),  # ← 10 min before 6:55
                "name": "Pre-Commodity Ping (6:45 AM)",
                "misfire_grace_time": 300
            },
        ]
        for job_config in jobs:
            self.scheduler.add_job(
                job_config["func"],
                job_config["trigger"],
                id=job_config["id"],
                name=job_config["name"],
                replace_existing=True,
                misfire_grace_time=job_config.get("misfire_grace_time", 60)
            )
        logger.info(f"{len(jobs)} jobs registered successfully")

    async def start(self):
        self.setup()
        self.scheduler.start()
        logger.info("✅ Master Scheduler v9.1 STARTED")
        for job in self.scheduler.get_jobs():
            nxt = str(job.next_run_time) if job.next_run_time else "N/A"
            logger.info(f"   📌 {job.name} -> {nxt}")

    async def stop(self):
        self.scheduler.shutdown()
        logger.info("🛑 Master Scheduler v9.1 STOPPED")

    def get_status(self):
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            })
        return {"running": self.scheduler.running, "total_jobs": len(jobs), "jobs": jobs}
