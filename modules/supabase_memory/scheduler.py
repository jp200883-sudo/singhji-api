from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backup_system import run_daily_backup
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def setup_scheduler():
    # Daily backup at 2:00 AM IST (20:30 UTC)
    scheduler.add_job(
        run_daily_backup,
        'cron',
        hour=20,
        minute=30,
        id='daily_backup',
        replace_existing=True
    )
    
    # Backup health check every 6 hours
    scheduler.add_job(
        lambda: backup_system.check_backup_health(),
        'cron',
        hour='*/6',
        id='backup_health_check',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started - Daily backup: 2:00 AM IST")
