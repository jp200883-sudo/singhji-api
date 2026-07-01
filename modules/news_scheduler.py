# modules/news_scheduler.py

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def handler(request):
    """News Scheduler - API endpoint"""
    return {"status": "ok", "message": "News scheduler active"}

def fetch_and_store_news():
    """Background job - every hour"""
    try:
        # Lazy import - जब जरूरत हो तब
        from modules.newsdata.handler import get_india_news
        
        languages = ["en", "hi"]
        for lang in languages:
            try:
                news = get_india_news(language=lang)
                logger.info(f"✅ News fetched: {lang} - {len(news) if news else 0} items")
            except Exception as e:
                logger.error(f"❌ News fetch failed {lang}: {e}")
                # Crash नहीं होगा - log करके आगे बढ़ेगा
                
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")
        # Module missing हो तो भी crash नहीं

# APScheduler setup - safe
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_news, 'cron', hour='6-21', minute='0')
    scheduler.start()
    logger.info("✅ News scheduler started")
except Exception as e:
    logger.error(f"❌ Scheduler start failed: {e}")
