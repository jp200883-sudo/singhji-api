# modules/news_scheduler.py — Singh Ji AI Ultra v5.0
# Auto-News Bot — 6AM to 9PM

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

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
