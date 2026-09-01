
import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

logger = logging.getLogger("SinghJi.Scheduler")

# ═════════════════════════════════════════════════════════════════
# SAFE CONFIG IMPORTS
# ═════════════════════════════════════════════════════════════════

try:
    from core.config import (
        OPENWEATHER_API_KEY, MANDI_API_KEY, MANDI_BASE_URL,
        ADMIN_USER_ID, TELEGRAM_BOT_TOKEN, APP_URL
    )
except ImportError:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
    MANDI_BASE_URL = os.getenv("MANDI_BASE_URL", "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070")
    ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    APP_URL = os.getenv("APP_URL", "")

DATAGOVINDIA_API_KEY = os.getenv("DATAGOVINDIA_API_KEY", "")

# ═════════════════════════════════════════════════════════════════
# HTTP CLIENT
# ═════════════════════════════════════════════════════════════════

_http_client: Optional[httpx.AsyncClient] = None

async def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client


# ═════════════════════════════════════════════════════════════════
# SMART PING SYSTEM — 5 MIN BEFORE EACH SCHEDULED JOB
# ═════════════════════════════════════════════════════════════════

async def _smart_ping():
    """Ping ONLY when called — no automatic interval"""
    if not APP_URL:
        logger.debug("APP_URL not set — skip smart ping")
        return
    try:
        client = await _get_http_client()
        resp = await client.get(f"{APP_URL}/ping", timeout=10)
        if resp.status_code == 200:
            logger.info(f"Smart Ping OK — {datetime.now().strftime('%H:%M:%S')}")
        else:
            logger.warning(f"Smart Ping returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Smart Ping failed: {e}")

def _schedule_smart_ping(scheduler: AsyncIOScheduler, target_hour: int, target_minute: int, job_name: str):
    """
    Schedule a ping exactly 5 minutes before the target job
    Example: target 6:00 AM → ping at 5:55 AM
    """
    ping_minute = target_minute - 5
    ping_hour = target_hour
    if ping_minute < 0:
        ping_minute += 60
        ping_hour -= 1
        if ping_hour < 0:
            ping_hour += 24
    
    ping_time = f"{ping_hour:02d}:{ping_minute:02d}"
    job_id = f"smart_ping_{job_name}"
    
    scheduler.add_job(
        _smart_ping,
        CronTrigger(hour=ping_hour, minute=ping_minute),
        id=job_id,
        name=f"Smart Ping {ping_time} for {job_name}",
        replace_existing=True,
        misfire_grace_time=300
    )
    logger.info(f"Smart Ping scheduled: {ping_time} → {job_name} ({target_hour:02d}:{target_minute:02d})")


# ═════════════════════════════════════════════════════════════════
# AAJ KA VICHAR
# ═════════════════════════════════════════════════════════════════

_FALLBACK_VICHAR = [
    "Apni takdeer ke nirmaata tum khud ho.",
    "Sapne woh hain jo neend uda dein.",
    "Mehnat itni khamoshi se karo ki safalta shor macha de.",
    "Har subah ek nayi shuruaat hai.",
    "Dar ke aage hi jeet hai.",
]

_VICHAR_CACHE: Dict[str, str] = {}

async def _fetch_fresh_vichar_from_ai() -> str:
    try:
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            return ""
        today = datetime.now().strftime("%d %b %Y")
        prompt = (
            f"Aaj {today} hai. Ek shaktishaali, prernaadayak Hindi sukti do "
            f"jo vyapaar, safalta, mehnat, ya jeevan par ho. "
            f"Sirf quote do — koi intro, outro, ya explanation mat do. "
            f"Maximum 150 characters. Hindi mein ho."
        )
        client = await _get_http_client()
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200, "temperature": 0.9},
            timeout=15.0
        )
        data = resp.json()
        quote = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip().strip('"').strip("'")
        if quote and len(quote) > 10:
            logger.info(f"Fresh vichar: {quote[:60]}...")
            return quote
        return ""
    except Exception as e:
        logger.warning(f"AI vichar fail: {e}")
        return ""

async def _get_aaj_ka_vichar() -> str:
    today_str = datetime.now().strftime("%Y-%m-%d")
    if today_str in _VICHAR_CACHE:
        return _VICHAR_CACHE[today_str]
    fresh = await _fetch_fresh_vichar_from_ai()
    if fresh:
        _VICHAR_CACHE[today_str] = fresh
        return fresh
    day_of_year = datetime.now().timetuple().tm_yday
    fallback = _FALLBACK_VICHAR[day_of_year % len(_FALLBACK_VICHAR)]
    _VICHAR_CACHE[today_str] = fallback
    return fallback


# ═════════════════════════════════════════════════════════════════
# TELEGRAM BROADCAST
# ═════════════════════════════════════════════════════════════════

async def _send_telegram_message(chat_id: int, text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        client = await _get_http_client()
        resp = await client.post(url, json={
            "chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True
        })
        return resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"Telegram send fail: {e}")
        return False

async def _get_subscriber_chat_ids() -> List[int]:
    try:
        from core.supabase_client import get_supabase_client
        sb = get_supabase_client()
        resp = sb.table("telegram_subscribers").select("chat_id").eq("active", True).execute()
        return [row["chat_id"] for row in (resp.data or [])]
    except Exception as e:
        logger.error(f"Subscriber fetch fail: {e}")
        if ADMIN_USER_ID:
            try:
                return [int(ADMIN_USER_ID)]
            except:
                pass
        return []

async def _broadcast_message(text: str) -> Dict[str, Any]:
    chat_ids = await _get_subscriber_chat_ids()
    if not chat_ids:
        logger.warning("No subscribers")
        return {"sent": 0, "failed": 0, "total": 0}
    sent, failed = 0, 0
    for cid in chat_ids:
        if await _send_telegram_message(cid, text):
            sent += 1
        else:
            failed += 1
        await asyncio.sleep(0.1)
    logger.info(f"Broadcast: Sent {sent}, Failed {failed}")
    return {"sent": sent, "failed": failed, "total": len(chat_ids)}


# ═════════════════════════════════════════════════════════════════
# DATA FETCHERS
# ═════════════════════════════════════════════════════════════════

async def _fetch_news() -> str:
    try:
        from modules.news.handler import get_news_digest_text
        news_text = await get_news_digest_text(count=5, hindi_only=True)
        if not news_text or "khbar" in news_text.lower():
            return "TAZA KHABREIN\n\nAbhi khabrein uplabdh nahi hain."
        return f"TAZA KHABREIN\n\n{news_text}"
    except Exception as e:
        logger.error(f"News fetch fail: {e}")
        return "TAZA KHABREIN\n\nKhabrein lane mein truti hui."

async def _fetch_weather(city: str = "Kanpur") -> str:
    if not OPENWEATHER_API_KEY:
        return f"MAUSAM — {city}\n\nAPI key missing."
    try:
        client = await _get_http_client()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = await client.get(url, timeout=15)
        data = resp.json()
        if resp.status_code != 200:
            return f"MAUSAM — {city}\n\nSheher nahi mila."
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        desc = data["weather"][0]["description"].title()
        return f"MAUSAM — {city}\nTapman: {temp}C (Mehsoos: {feels}C)\nNami: {humidity}%\nHawa: {wind} m/s\n{desc}"
    except Exception as e:
        logger.error(f"Weather fail: {e}")
        return f"MAUSAM — {city}\n\nTruti hui."

async def _fetch_mandi(state: str = "Uttar Pradesh") -> str:
    if not MANDI_API_KEY:
        return "MANDI BHAV\n\nAPI key missing."
    try:
        client = await _get_http_client()
        params = {"api-key": MANDI_API_KEY, "format": "json", "limit": 10, "filters[state.keyword]": state}
        resp = await client.get(MANDI_BASE_URL, params=params, timeout=45)
        data = resp.json()
        if "error" in data:
            return f"MANDI BHAV — {state}\n\nAPI truti."
        records = data.get("records", [])
        if not records:
            return f"MANDI BHAV — {state}\n\nKoi data nahi."
        lines = [f"MANDI BHAV — {state}"]
        for i, r in enumerate(records[:5], 1):
            commodity = r.get("commodity", "Unknown")
            modal = r.get("modal_price", "N/A")
            min_p = r.get("min_price", "N/A")
            max_p = r.get("max_price", "N/A")
            market = r.get("market", "N/A")
            district = r.get("district", "N/A")
            lines.append(f"{i}. {commodity} — Rs{modal}/quintal (Rs{min_p}-Rs{max_p}) | {market}, {district}")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Mandi fail: {e}")
        return "MANDI BHAV\n\nTruti hui."

async def _fetch_gold_silver(city: str = "delhi") -> str:
    try:
        from modules.goldrate.handler import gold_rate_city
        resp = await gold_rate_city(city)
        body = json.loads(bytes(resp.body))
        d = body.get("data", {})
        cr = d.get("city_rates", {})
        lines = [f"SONA-CHAANDI — {cr.get('city', city.title())}"]
        g24 = cr.get("price_gram_24k", "N/A")
        g22 = cr.get("price_gram_22k", "N/A")
        if g24 != "N/A":
            lines.append(f"24K Sona (1g): Rs{g24}")
        if g22 != "N/A":
            lines.append(f"22K Sona (1g): Rs{g22}")
        try:
            silver = cr.get("price_silver_1kg", "N/A")
            if silver != "N/A":
                lines.append(f"Chaandi (1kg): Rs{silver}")
        except:
            pass
        updated = d.get("last_updated", "N/A")
        lines.append(f"Updated: {updated}")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Gold fail: {e}")
        return "SONA-CHAANDI\n\nTruti hui."

async def _fetch_fuel(city: str = "delhi") -> str:
    try:
        from modules.fuel.handler import fuel_price
        resp = await fuel_price(city)
        body = json.loads(bytes(resp.body))
        d = body.get("data", {})
        petrol = d.get("petrol", "N/A")
        diesel = d.get("diesel", "N/A")
        updated = d.get("last_updated", "N/A")
        city_name = d.get("city", city.title())
        return f"INDHAN BHAV — {city_name}\nPetrol: Rs{petrol}/L\nDiesel: Rs{diesel}/L\nUpdated: {updated}"
    except Exception as e:
        logger.error(f"Fuel fail: {e}")
        return "INDHAN BHAV\n\nTruti hui."

async def _fetch_horoscope(rashi: str = "Mesh") -> str:
    try:
        from modules.horoscope.handler import get_horoscope
        h = get_horoscope(rashi, "daily", "hi")
        prediction = h.get("prediction", "")
        lucky = h.get("lucky_number", "")
        lucky_color = h.get("lucky_color", "")
        lines = [f"RASHIFAL — {rashi}"]
        if prediction:
            lines.append(prediction[:300])
        if lucky:
            lines.append(f"Lucky Number: {lucky}")
        if lucky_color:
            lines.append(f"Lucky Rang: {lucky_color}")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Horoscope fail: {e}")
        return f"RASHIFAL — {rashi}\n\nTruti hui."

async def _fetch_rozgar() -> str:
    try:
        from modules.rozgar import handler as rozgar_module
        result = rozgar_module._search_keyword("government", "")
        result = rozgar_module._filter_by_country(result, "IN")
        lines = ["ROZGAR UPDATE"]
        count = 0
        for section, label in [("govt", "Sarkari"), ("regional", "Kshetriya")]:
            for entry in result.get(section, [])[:3]:
                name = entry.get("name", "")
                site = entry.get("site", "")
                if name:
                    lines.append(f"{label}: {name} — {site}")
                    count += 1
        if count == 0:
            lines.append("Aaj koi nayi bharti nahi.")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Rozgar fail: {e}")
        return "ROZGAR UPDATE\n\nTruti hui."


# ═════════════════════════════════════════════════════════════════
# DIGEST BUILDERS
# ═════════════════════════════════════════════════════════════════

async def build_morning_digest(
    weather_city: str = "Kanpur",
    mandi_state: str = "Uttar Pradesh",
    gold_city: str = "delhi",
    fuel_city: str = "delhi",
    rashi: str = "Mesh"
) -> str:
    today = datetime.now().strftime("%d %b %Y, %A")
    header = f"Singh Ji Morning Digest — {today}\n" + "=" * 30 + "\n\n"
    results = await asyncio.gather(
        _fetch_news(), _fetch_weather(weather_city), _fetch_gold_silver(gold_city),
        _fetch_fuel(fuel_city), _fetch_mandi(mandi_state), _fetch_horoscope(rashi),
        return_exceptions=True
    )
    sections = []
    names = ["News", "Weather", "Gold/Silver", "Fuel", "Mandi", "Horoscope"]
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            sections.append(f"{names[i]}: Truti hui")
        else:
            sections.append(r)
    separator = "\n\n" + "-" * 25 + "\n\n"
    body = separator.join(sections)
    footer = "\n\n" + "=" * 30 + "\nSingh Ji AI Ultra v11.0\nCommands: /news /weather /mandi /gold /fuel /horoscope"
    full = header + body + footer
    return full[:3990] + "\n\n... (truncated)" if len(full) > 4000 else full

async def build_evening_digest() -> str:
    today = datetime.now().strftime("%d %b %Y")
    header = f"Singh Ji Evening Digest — {today}\n" + "=" * 30 + "\n\n"
    results = await asyncio.gather(_fetch_news(), _fetch_rozgar(), return_exceptions=True)
    sections = []
    names = ["News", "Rozgar"]
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            sections.append(f"{names[i]}: Truti hui")
        else:
            sections.append(r)
    separator = "\n\n" + "-" * 25 + "\n\n"
    body = separator.join(sections)
    footer = "\n\n" + "=" * 30 + "\nSingh Ji AI Ultra v11.0\nShubh Ratri!"
    full = header + body + footer
    return full[:3990] + "\n\n... (truncated)" if len(full) > 4000 else full


# ═════════════════════════════════════════════════════════════════
# SCHEDULER JOBS
# ═════════════════════════════════════════════════════════════════

async def job_aaj_ka_vichar():
    logger.info("=== Aaj Ka Vichar START ===")
    try:
        today = datetime.now().strftime("%d %b %Y, %A")
        vichar = await _get_aaj_ka_vichar()
        message = f"Aaj Ka Vichar — {today}\n" + "=" * 30 + f"\n\n\"{vichar}\"\n\nSingh Ji AI Ultra v11.0\nPoora Digest 7 baje aayega..."
        result = await _broadcast_message(message)
        logger.info(f"Aaj Ka Vichar: {result['sent']}/{result['total']} users")
    except Exception as e:
        logger.error(f"Aaj Ka Vichar failed: {e}")

async def job_morning_digest():
    logger.info("=== Morning Digest START ===")
    try:
        message = await build_morning_digest()
        result = await _broadcast_message(message)
        logger.info(f"Morning Digest: {result['sent']}/{result['total']} users")
    except Exception as e:
        logger.error(f"Morning Digest failed: {e}")

async def job_evening_digest():
    logger.info("=== Evening Digest START ===")
    try:
        message = await build_evening_digest()
        result = await _broadcast_message(message)
        logger.info(f"Evening Digest: {result['sent']}/{result['total']} users")
    except Exception as e:
        logger.error(f"Evening Digest failed: {e}")

async def job_flood_watch():
    logger.info("=== Flood Watch START ===")
    # TODO: Implement actual flood monitoring
    pass


# ═════════════════════════════════════════════════════════════════
# SMART PING SCHEDULER CLASS
# ═════════════════════════════════════════════════════════════════

class SmartPingScheduler:
    """
    Smart Ping v11.0 — NO interval keep-alive
    Only pings 5 minutes BEFORE each scheduled job
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.scheduler.add_listener(
            lambda e: logger.error(f"Job {e.job_id} crashed: {e.exception}") if e.exception else logger.info(f"Job {e.job_id} done"),
            EVENT_JOB_ERROR | EVENT_JOB_EXECUTED
        )

    def setup_smart_pings(self):
        """
        Schedule smart pings for ALL jobs
        Each ping runs exactly 5 minutes before the target job
        """
        # Aaj Ka Vichar at 6:00 AM → Ping at 5:55 AM
        _schedule_smart_ping(self.scheduler, 6, 0, "aaj_ka_vichar")
        
        # Morning Digest at 7:00 AM → Ping at 6:55 AM
        _schedule_smart_ping(self.scheduler, 7, 0, "morning_digest")
        
        # Evening Digest at 6:00 PM → Ping at 5:55 PM
        _schedule_smart_ping(self.scheduler, 18, 0, "evening_digest")
        
        # Flood Watch every hour — NO smart ping (too frequent)
        # If you want smart ping for hourly jobs, tell me
        
        logger.info("Smart Pings scheduled for all digest jobs")

    def setup_jobs(self):
        # Main digest jobs
        self.scheduler.add_job(
            job_aaj_ka_vichar, 
            CronTrigger(hour=6, minute=0), 
            id="aaj_ka_vichar", 
            name="Aaj Ka Vichar 6AM", 
            replace_existing=True, 
            misfire_grace_time=1800
        )
        self.scheduler.add_job(
            job_morning_digest, 
            CronTrigger(hour=7, minute=0), 
            id="morning_digest", 
            name="Morning Digest 7AM", 
            replace_existing=True, 
            misfire_grace_time=3600
        )
        self.scheduler.add_job(
            job_evening_digest, 
            CronTrigger(hour=18, minute=0), 
            id="evening_digest", 
            name="Evening Digest 6PM", 
            replace_existing=True, 
            misfire_grace_time=3600
        )
        
        # Flood Watch — hourly, no smart ping needed (too frequent)
        self.scheduler.add_job(
            job_flood_watch, 
            "interval", 
            hours=1, 
            id="flood_watch", 
            name="Flood Watch 1hr", 
            replace_existing=True
        )
        
        # Setup smart pings for digest jobs
        self.setup_smart_pings()
        
        logger.info("All jobs registered (NO keep-alive interval)")

    def get_status(self) -> Dict[str, Any]:
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": j.id, 
                    "name": j.name, 
                    "next_run": str(j.next_run_time) if j.next_run_time else None
                } 
                for j in jobs
            ],
            "timezone": "Asia/Kolkata",
            "smart_ping_enabled": True,
            "keep_alive_removed": True
        }

    async def start(self):
        if self.scheduler.running:
            logger.info("Scheduler already running")
            return
        self.setup_jobs()
        self.scheduler.start()
        logger.info("=" * 50)
        logger.info("SMART PING SCHEDULER v11.0 STARTED")
        logger.info("Keep Alive REMOVED — only 5-min-before pings")
        logger.info("=" * 50)
        for j in self.get_status()["jobs"]:
            logger.info(f"  {j['name']} -> Next: {j['next_run']}")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            if _http_client and not _http_client.is_closed:
                await _http_client.aclose()
            logger.info("Smart Ping Scheduler STOPPED")


# ═════════════════════════════════════════════════════════════════
# SINGLETON + BACKWARD COMPATIBILITY
# ═════════════════════════════════════════════════════════════════

MASTER_SCHEDULER = SmartPingScheduler()
USER_PREFERENCES: Dict[int, Dict[str, Any]] = {}

def _load_user_preferences_sync():
    global USER_PREFERENCES
    try:
        from core.supabase_client import get_supabase_client
        sb = get_supabase_client()
        resp = sb.table("user_preferences").select("*").execute()
        for row in (resp.data or []):
            chat_id = row.get("chat_id")
            if chat_id:
                USER_PREFERENCES[int(chat_id)] = row
        logger.info(f"Loaded {len(USER_PREFERENCES)} preferences")
    except Exception as e:
        logger.warning(f"Preferences load fail: {e}")
        USER_PREFERENCES = {}

# Backward compatibility aliases
UnifiedScheduler = SmartPingScheduler
SinghJiMasterScheduler = SmartPingScheduler
