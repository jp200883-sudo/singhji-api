"""
═══════════════════════════════════════════════════════════════════
  🌅 सिंह जी AI अल्ट्रा v8.3 — UNIFIED MASTER SCHEDULER
  फाइल: core/scheduler_unified.py
  फीचर्स: Morning Digest (7 AM) + Evening Digest (6 PM) + 
           Keep Alive + Flood Watch + All Modules Integrated
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import asyncio
import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

# ─── Logging ─────────────────────────────────────────────────────
logger = logging.getLogger("SinghJi.Scheduler")

# ─── Config from core.config ─────────────────────────────────────
try:
    from core.config import (
        OPENWEATHER_API_KEY, MANDI_API_KEY, MANDI_BASE_URL,
        ADMIN_USER_ID, TELEGRAM_BOT_TOKEN
    )
except ImportError:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
    MANDI_BASE_URL = os.getenv("MANDI_BASE_URL", "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070")
    ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ─── HTTP Client ─────────────────────────────────────────────────
_http_client: Optional[httpx.AsyncClient] = None

async def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client

# ─── Key-saving Cache (weather + mandi ke liye) ───────────────────
_CACHE: Dict[str, tuple] = {}
_CACHE_TTL_SECONDS = 1800  # 30 minute — isi beech dobara wahi city/state maango to cache se milega

def _cache_get(key: str) -> Optional[str]:
    entry = _CACHE.get(key)
    if not entry:
        return None
    value, saved_at = entry
    if time.time() - saved_at > _CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value

def _cache_set(key: str, value: str) -> None:
    _CACHE[key] = (value, time.time())

# ─── Telegram Broadcast ──────────────────────────────────────────
async def _send_telegram_message(chat_id: int, text: str) -> bool:
    """Single message sender with rate limit safety"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN missing — message skipped")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        client = await _get_http_client()
        resp = await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
        data = resp.json()
        if data.get("ok"):
            return True
        logger.warning(f"Telegram API error: {data.get('description')}")
        return False
    except Exception as e:
        logger.error(f"Telegram send fail: {e}")
        return False

async def _get_subscriber_chat_ids() -> List[int]:
    """Supabase से active subscribers लाओ"""
    try:
        from core.supabase_client import get_supabase_client
        sb = get_supabase_client()
        resp = sb.table("telegram_subscribers").select("chat_id").eq("active", True).execute()
        return [row["chat_id"] for row in (resp.data or [])]
    except Exception as e:
        logger.error(f"Subscriber fetch fail: {e}")
        # Fallback: admin ko bhejo
        if ADMIN_USER_ID:
            try:
                return [int(ADMIN_USER_ID)]
            except:
                pass
        return []

async def _broadcast_message(text: str) -> Dict[str, Any]:
    """Sab subscribers ko message bhejo"""
    chat_ids = await _get_subscriber_chat_ids()
    if not chat_ids:
        logger.warning("No subscribers found — broadcast skipped")
        return {"sent": 0, "failed": 0, "total": 0}

    sent, failed = 0, 0
    for cid in chat_ids:
        if await _send_telegram_message(cid, text):
            sent += 1
        else:
            failed += 1
        await asyncio.sleep(0.1)  # Rate limit safety

    logger.info(f"📤 Broadcast complete — Sent: {sent}, Failed: {failed}")
    return {"sent": sent, "failed": failed, "total": len(chat_ids)}


# ═════════════════════════════════════════════════════════════════
#                    DATA FETCHERS (ALL MODULES)
# ═════════════════════════════════════════════════════════════════

async def _fetch_news() -> str:
    """📰 News digest fetch karo"""
    try:
        from modules.news.handler import get_news_digest_text
        news_text = await get_news_digest_text(count=5, hindi_only=True)
        if not news_text or news_text == "अभी कोई खबर उपलब्ध नहीं है।":
            return "📰 <b>ताज़ा खबरें</b>\n\nअभी खबरें उपलब्ध नहीं हैं।"
        return f"📰 <b>ताज़ा खबरें</b>\n\n{news_text}"
    except Exception as e:
        logger.error(f"News fetch fail: {e}")
        return "📰 <b>ताज़ा खबरें</b>\n\n❌ खबरें लाने में त्रुटि हुई।"


async def _fetch_weather(city: str = "Kanpur") -> str:
    """🌤️ Weather fetch karo (30 min cache — key bachane ke liye)"""
    cache_key = f"weather:{city.lower()}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if not OPENWEATHER_API_KEY:
        return f"🌤️ <b>मौसम — {city}</b>\n\n❌ Weather API key missing"
    try:
        client = await _get_http_client()
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        resp = await client.get(url, timeout=15)
        data = resp.json()
        if resp.status_code != 200:
            return f"🌤️ <b>मौसम — {city}</b>\n\n❌ शहर नहीं मिला"

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        desc = data["weather"][0]["description"].title()

        result = (
            f"🌤️ <b>मौसम — {city}</b>\n"
            f"🌡️ तापमान: {temp}°C (महसूस: {feels}°C)\n"
            f"💧 नमी: {humidity}%\n"
            f"🌬️ हवा: {wind} m/s\n"
            f"☁️ {desc}"
        )
        _cache_set(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Weather fetch fail: {e}")
        return f"🌤️ <b>मौसम — {city}</b>\n\n❌ त्रुटि: {str(e)[:80]}"


async def _fetch_mandi(state: str = "Uttar Pradesh") -> str:
    """🌾 Mandi rates fetch karo (30 min cache — key bachane ke liye)"""
    cache_key = f"mandi:{state.lower()}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if not MANDI_API_KEY:
        return "🌾 <b>मंडी भाव</b>\n\n❌ Mandi API key missing"
    try:
        client = await _get_http_client()
        params = {
            "api-key": MANDI_API_KEY,
            "format": "json",
            "limit": 10,
            "filters[state.keyword]": state
        }
        resp = await client.get(MANDI_BASE_URL, params=params, timeout=45)
        data = resp.json()

        if "error" in data:
            return f"🌾 <b>मंडी भाव — {state}</b>\n\n❌ API त्रुटि"

        records = data.get("records", [])
        if not records:
            return f"🌾 <b>मंडी भाव — {state}</b>\n\n❌ कोई डेटा नहीं मिला"

        lines = [f"🌾 <b>मंडी भाव — {state}</b>\n"]
        for i, r in enumerate(records[:5], 1):
            commodity = r.get("commodity", "Unknown")
            modal = r.get("modal_price", "N/A")
            min_p = r.get("min_price", "N/A")
            max_p = r.get("max_price", "N/A")
            market = r.get("market", "N/A")
            district = r.get("district", "N/A")
            lines.append(
                f"{i}. {commodity}\n"
                f"   ₹{modal}/क्विंटल (₹{min_p}-₹{max_p})\n"
                f"   📍 {market}, {district}"
            )
        result = "\n".join(lines)
        _cache_set(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Mandi fetch fail: {e}")
        return f"🌾 <b>मंडी भाव</b>\n\n❌ त्रुटि: {str(e)[:80]}"


async def _fetch_gold_silver(city: str = "delhi") -> str:
    """🥇 Gold + Silver + Copper rates"""
    try:
        from modules.goldrate.handler import gold_rate_city
        resp = await gold_rate_city(city)
        body = json.loads(bytes(resp.body))
        d = body.get("data", {})
        cr = d.get("city_rates", {})

        lines = [f"🥇 <b>सोना-चाँदी — {cr.get('city', city.title())}</b>\n"]

        g24 = cr.get("price_gram_24k", "N/A")
        g22 = cr.get("price_gram_22k", "N/A")
        g10_24 = cr.get("price_10g_24k", "N/A")
        g10_22 = cr.get("price_10g_22k", "N/A")

        if g24 != "N/A":
            lines.append(f"🟡 24K सोना (1g): ₹{g24}")
        if g22 != "N/A":
            lines.append(f"🟡 22K सोना (1g): ₹{g22}")
        if g10_24 != "N/A":
            lines.append(f"🟡 24K सोना (10g): ₹{g10_24}")
        if g10_22 != "N/A":
            lines.append(f"🟡 22K सोना (10g): ₹{g10_22}")

        try:
            silver = cr.get("price_silver_1kg", "N/A")
            if silver != "N/A":
                lines.append(f"⚪ चाँदी (1kg): ₹{silver}")
        except:
            pass

        try:
            copper = cr.get("price_copper_1kg", "N/A")
            if copper != "N/A":
                lines.append(f"🟤 ताँबा (1kg): ₹{copper}")
        except:
            pass

        updated = d.get("last_updated", "N/A")
        lines.append(f"\n🕐 अपडेटेड: {updated}")

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Gold fetch fail: {e}")
        return "🥇 <b>सोना-चाँदी</b>\n\n❌ दरें लाने में त्रुटि हुई।"


async def _fetch_fuel(city: str = "delhi") -> str:
    """⛽ Fuel prices"""
    try:
        from modules.fuel.handler import fuel_price
        resp = await fuel_price(city)
        body = json.loads(bytes(resp.body))
        d = body.get("data", {})

        petrol = d.get("petrol", "N/A")
        diesel = d.get("diesel", "N/A")
        updated = d.get("last_updated", "N/A")
        city_name = d.get("city", city.title())

        return (
            f"⛽ <b>ईंधन भाव — {city_name}</b>\n"
            f"🟢 पेट्रोल: ₹{petrol}/L\n"
            f"⚫ डीज़ल: ₹{diesel}/L\n"
            f"🕐 अपडेटेड: {updated}"
        )
    except Exception as e:
        logger.error(f"Fuel fetch fail: {e}")
        return "⛽ <b>ईंधन भाव</b>\n\n❌ भाव लाने में त्रुटि हुई।"


async def _fetch_horoscope(rashi: str = "मेष") -> str:
    """🔮 Horoscope"""
    try:
        from modules.horoscope.handler import get_horoscope
        h = get_horoscope(rashi, "daily", "hi")

        prediction = h.get("prediction", "")
        lucky = h.get("lucky_number", "")
        lucky_color = h.get("lucky_color", "")

        lines = [f"🔮 <b>राशिफल — {rashi}</b>\n"]
        if prediction:
            lines.append(prediction[:300])
        if lucky:
            lines.append(f"\n🍀 लकी नंबर: {lucky}")
        if lucky_color:
            lines.append(f"🎨 लकी रंग: {lucky_color}")

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Horoscope fetch fail: {e}")
        return f"🔮 <b>राशिफल — {rashi}</b>\n\n❌ राशिफल लाने में त्रुटि हुई।"


async def _fetch_rozgar() -> str:
    """💼 Rozgar/Jobs update"""
    try:
        from modules.rozgar import handler as rozgar_module
        result = rozgar_module._search_keyword("government", "")
        result = rozgar_module._filter_by_country(result, "IN")

        lines = ["💼 <b>रोज़गार अपडेट</b>\n"]
        count = 0
        for section, label in [("govt", "🏛️ सरकारी"), ("regional", "📍 क्षेत्रीय")]:
            for entry in result.get(section, [])[:3]:
                name = entry.get("name", "")
                site = entry.get("site", "")
                if name:
                    lines.append(f"{label}: {name} — {site}")
                    count += 1

        if count == 0:
            lines.append("आज कोई नई भर्ती नहीं मिली।")

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Rozgar fetch fail: {e}")
        return "💼 <b>रोज़गार अपडेट</b>\n\n❌ जानकारी लाने में त्रुटि हुई।"


# ═════════════════════════════════════════════════════════════════
#                    DIGEST BUILDERS
# ═════════════════════════════════════════════════════════════════

async def build_morning_digest(
    weather_city: str = "Kanpur",
    mandi_state: str = "Uttar Pradesh",
    gold_city: str = "delhi",
    fuel_city: str = "delhi",
    rashi: str = "मेष"
) -> str:
    """🌅 सुबह 7 बजे का complete digest"""

    today = datetime.now().strftime("%d %b %Y, %A")
    header = f"🌅 <b>सिंह जी मॉर्निंग डाइजेस्ट</b> — {today}\n"
    header += "═" * 30 + "\n\n"

    results = await asyncio.gather(
        _fetch_news(),
        _fetch_weather(weather_city),
        _fetch_gold_silver(gold_city),
        _fetch_fuel(fuel_city),
        _fetch_mandi(mandi_state),
        _fetch_horoscope(rashi),
        return_exceptions=True
    )

    sections = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            names = ["News", "Weather", "Gold/Silver", "Fuel", "Mandi", "Horoscope"]
            sections.append(f"❌ {names[i]}: त्रुटि हुई")
        else:
            sections.append(r)

    separator = "\n\n" + "─" * 25 + "\n\n"
    body = separator.join(sections)

    footer = (
        "\n\n" + "═" * 30 + "\n"
        "🤖 <i>सिंह जी AI अल्ट्रा v8.3</i>\n"
        "💬 कमांड्स: /news /weather /mandi /gold /fuel /horoscope"
    )

    full_message = header + body + footer
    if len(full_message) > 4000:
        full_message = full_message[:3990] + "\n\n... (truncated)"

    return full_message


async def build_evening_digest() -> str:
    """🌆 शाम 6 बजे का digest"""

    today = datetime.now().strftime("%d %b %Y")
    header = f"🌆 <b>सिंह जी इवनिंग डाइजेस्ट</b> — {today}\n"
    header += "═" * 30 + "\n\n"

    results = await asyncio.gather(
        _fetch_news(),
        _fetch_rozgar(),
        return_exceptions=True
    )

    sections = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            names = ["News", "Rozgar"]
            sections.append(f"❌ {names[i]}: त्रुटि हुई")
        else:
            sections.append(r)

    separator = "\n\n" + "─" * 25 + "\n\n"
    body = separator.join(sections)

    footer = (
        "\n\n" + "═" * 30 + "\n"
        "🤖 <i>सिंह जी AI अल्ट्रा v8.3</i>\n"
        "शुभ रात्रि! 🌙"
    )

    full_message = header + body + footer
    if len(full_message) > 4000:
        full_message = full_message[:3990] + "\n\n... (truncated)"

    return full_message


# ═════════════════════════════════════════════════════════════════
#                    SCHEDULER JOBS
# ═════════════════════════════════════════════════════════════════

async def job_morning_digest():
    logger.info("🌅 Morning Digest started...")
    try:
        message = await build_morning_digest()
        result = await _broadcast_message(message)
        logger.info(f"✅ Morning Digest sent to {result['sent']}/{result['total']} users")
    except Exception as e:
        logger.error(f"❌ Morning Digest failed: {e}")


async def job_evening_digest():
    logger.info("🌆 Evening Digest started...")
    try:
        message = await build_evening_digest()
        result = await _broadcast_message(message)
        logger.info(f"✅ Evening Digest sent to {result['sent']}/{result['total']} users")
    except Exception as e:
        logger.error(f"❌ Evening Digest failed: {e}")


async def job_keep_alive():
    app_url = os.getenv("APP_URL", "")
    if not app_url:
        logger.debug("APP_URL not set — skip keep-alive")
        return
    try:
        client = await _get_http_client()
        resp = await client.get(f"{app_url}/ping", timeout=10)
        if resp.status_code == 200:
            logger.debug("💓 Keep-alive ping OK")
        else:
            logger.warning(f"Keep-alive ping returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Keep-alive ping failed: {e}")


async def job_flood_watch():
    logger.info("🌊 Flood Watch check...")
    # TODO: Add actual flood alert logic using weather/meteorological APIs
    pass


# ═════════════════════════════════════════════════════════════════
#                    SCHEDULER CLASS
# ═════════════════════════════════════════════════════════════════

class UnifiedScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        self.scheduler.add_listener(
            lambda e: logger.error(f"Job {e.job_id} crashed: {e.exception}") if e.exception else logger.info(f"Job {e.job_id} done"),
            EVENT_JOB_ERROR | EVENT_JOB_EXECUTED
        )

    def setup_jobs(self):
        self.scheduler.add_job(
            job_morning_digest,
            CronTrigger(hour=7, minute=0),
            id="morning_digest",
            name="🌅 Morning Digest (News+Weather+Mandi+Gold+Fuel+Horoscope)",
            replace_existing=True,
            misfire_grace_time=3600
        )

        self.scheduler.add_job(
            job_evening_digest,
            CronTrigger(hour=18, minute=0),
            id="evening_digest",
            name="🌆 Evening Digest (News+Rozgar)",
            replace_existing=True,
            misfire_grace_time=3600
        )

        self.scheduler.add_job(
            job_keep_alive,
            "interval",
            minutes=10,
            id="keep_alive",
            name="💓 Railway Keep-Alive",
            replace_existing=True
        )

        self.scheduler.add_job(
            job_flood_watch,
            "interval",
            hours=1,
            id="flood_watch",
            name="🌊 Flood Watch",
            replace_existing=True
        )

        logger.info("✅ All 4 jobs registered successfully")

    def get_status(self) -> Dict[str, Any]:
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": j.id,
                    "name": j.name,
                    "next_run": str(j.next_run_time) if j.next_run_time else None,
                    "trigger": str(j.trigger)
                }
                for j in jobs
            ],
            "timezone": "Asia/Kolkata"
        }

    async def start(self):
        if self.scheduler.running:
            logger.info("Scheduler already running")
            return
        self.setup_jobs()
        self.scheduler.start()
        logger.info("🚀 Unified Scheduler STARTED")
        for j in self.get_status()["jobs"]:
            logger.info(f"  ⏰ {j['name']} → Next: {j['next_run']}")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            if _http_client and not _http_client.is_closed:
                await _http_client.aclose()
            logger.info("🛑 Unified Scheduler STOPPED")


# ═════════════════════════════════════════════════════════════════
#                    SINGLETON INSTANCE
# ═════════════════════════════════════════════════════════════════

MASTER_SCHEDULER = UnifiedScheduler()


# ─── Manual trigger helpers (for testing) ────────────────────────

async def trigger_morning_digest_now():
    logger.info("🧪 Manual trigger: Morning Digest")
    await job_morning_digest()

async def trigger_evening_digest_now():
    logger.info("🧪 Manual trigger: Evening Digest")
    await job_evening_digest()


if __name__ == "__main__":
    async def test():
        await MASTER_SCHEDULER.start()
        print("\nScheduler running. Press Ctrl+C to stop.\n")
        await asyncio.sleep(2)
        await trigger_morning_digest_now()
        while True:
            await asyncio.sleep(60)

    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        print("\nStopped.")
