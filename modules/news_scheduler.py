from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

# India timezone
IST = pytz.timezone('Asia/Kolkata')

def fetch_and_store_news(category="india", language="hi"):
    """Har ghante news fetch + store + notify"""
    from modules import newsdata, currents_api, supabase_memory
    
    # News fetch
    if category == "india":
        news = newsdata.get_india_news(language=language)
    elif category == "world":
        news = currents_api.get_world_news()
    else:
        news = {"success": False, "error": "Unknown category"}
    
    if news.get("success"):
        # Supabase me store
        supabase_memory.store_news(
            category=category,
            language=language,
            articles=news["articles"],
            timestamp=datetime.now(IST).isoformat()
        )
        
        # Telegram notify
        notify_telegram(f"📰 {category.upper()} News Updated! {len(news['articles'])} articles.")
        
        return True
    
    return False

# Scheduler setup
scheduler = BackgroundScheduler(timezone=IST)

# 6 AM to 9 PM — every hour
scheduler.add_job(fetch_and_store_news, 'cron', hour='6-21', minute=0, args=["india", "hi"])
scheduler.add_job(fetch_and_store_news, 'cron', hour='6-21', minute=5, args=["world", "en"])

scheduler.start()
