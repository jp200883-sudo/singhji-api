import os
import json
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
import supabase

logger = logging.getLogger(__name__)

class BackupSystem:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.backup_retention_days = 7
        self.tables_to_backup = ['users', 'chat_history', 'user_memory', 'events']
        self.webhook_url = os.getenv("BACKUP_ALERT_WEBHOOK")  # Telegram/Discord
        
    async def create_daily_backup(self) -> Dict:
        """Create full database backup"""
        backup_results = []
        total_records = 0
        
        try:
            # Create admin client
            admin_client = supabase.create_client(self.supabase_url, self.service_key)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"daily_{timestamp}"
            
            for table in self.tables_to_backup:
                try:
                    # Export data
                    response = admin_client.table(table).select('*').execute()
                    data = response.data or []
                    
                    # Calculate checksum
                    json_data = json.dumps(data, sort_keys=True, default=str)
                    checksum = hashlib.sha256(json_data.encode()).hexdigest()
                    
                    # Store in backup bucket
                    file_path = f"backups/{backup_id}/{table}.json"
                    admin_client.storage.from_('backups').upload(
                        file_path, 
                        json_data.encode(),
                        {"content-type": "application/json"}
                    )
                    
                    record_count = len(data)
                    total_records += record_count
                    
                    backup_results.append({
                        "table": table,
                        "records": record_count,
                        "checksum": checksum,
                        "status": "success"
                    })
                    
                    logger.info(f"✅ Backed up {table}: {record_count} records")
                    
                except Exception as e:
                    backup_results.append({
                        "table": table,
                        "records": 0,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"❌ Backup failed for {table}: {e}")
            
            # Log backup to database
            overall_status = "completed" if all(
                r["status"] == "success" for r in backup_results
            ) else "partial"
            
            backup_log = {
                "backup_type": "daily",
                "record_count": total_records,
                "file_path": f"backups/{backup_id}/",
                "status": overall_status,
                "completed_at": datetime.now().isoformat()
            }
            
            admin_client.table('backups').insert(backup_log).execute()
            
            # Clean old backups
            await self._clean_old_backups(admin_client)
            
            return {
                "backup_id": backup_id,
                "status": overall_status,
                "tables": backup_results,
                "total_records": total_records,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Daily backup failed: {e}")
            await self._create_alert("failed_backup", "critical", f"Backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def check_backup_health(self) -> Dict:
        """Check if backup exists for today"""
        try:
            admin_client = supabase.create_client(self.supabase_url, self.service_key)
            
            today = datetime.now().date()
            start_of_day = datetime.combine(today, datetime.min.time()).isoformat()
            
            response = admin_client.table('backups')\
                .select('*')\
                .eq('backup_type', 'daily')\
                .gte('created_at', start_of_day)\
                .execute()
            
            backups_today = response.data or []
            
            if not backups_today:
                await self._create_alert(
                    "missing_backup", 
                    "critical", 
                    f"No backup found for {today}"
                )
                return {"healthy": False, "message": "No backup today"}
            
            latest = backups_today[0]
            return {
                "healthy": True,
                "last_backup": latest['created_at'],
                "records": latest['record_count'],
                "status": latest['status']
            }
            
        except Exception as e:
            logger.error(f"Backup health check failed: {e}")
            return {"healthy": False, "error": str(e)}
    
    async def _clean_old_backups(self, client, days: int = 7):
        """Remove backups older than retention period"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get old backup records
            response = client.table('backups')\
                .select('file_path')\
                .lt('created_at', cutoff)\
                .execute()
            
            old_backups = response.data or []
            
            for backup in old_backups:
                try:
                    # Delete from storage (best effort)
                    path = backup['file_path']
                    # List and delete files in path
                    files = client.storage.from_('backups').list(path)
                    for file in files:
                        client.storage.from_('backups').remove([f"{path}{file['name']}"])
                except Exception as e:
                    logger.warning(f"Could not delete old backup files: {e}")
            
            # Delete old records
            client.table('backups')\
                .delete()\
                .lt('created_at', cutoff)\
                .execute()
            
            logger.info(f"🧹 Cleaned backups older than {days} days")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    async def _create_alert(self, alert_type: str, severity: str, message: str):
        """Create alert and send notification"""
        try:
            client = supabase.create_client(self.supabase_url, self.service_key)
            
            # Save to database
            client.table('backup_alerts').insert({
                "alert_type": alert_type,
                "severity": severity,
                "message": message
            }).execute()
            
            # Send webhook notification (Telegram/Discord)
            if self.webhook_url:
                async with aiohttp.ClientSession() as session:
                    await session.post(self.webhook_url, json={
                        "text": f"🚨 Singh Ji AI Backup Alert\nType: {alert_type}\nSeverity: {severity}\nMessage: {message}"
                    })
                    
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def restore_table(self, table: str, backup_date: str = None) -> bool:
        """Restore table from backup"""
        try:
            client = supabase.create_client(self.supabase_url, self.service_key)
            
            # Find latest backup if date not specified
            if not backup_date:
                response = client.table('backups')\
                    .select('file_path')\
                    .eq('backup_type', 'daily')\
                    .order('created_at', desc=True)\
                    .limit(1)\
                    .execute()
                
                if not response.data:
                    logger.error("No backups found")
                    return False
                    
                backup_path = response.data[0]['file_path']
            else:
                backup_path = f"backups/daily_{backup_date}/"
            
            # Download backup file
            file_path = f"{backup_path}{table}.json"
            file_data = client.storage.from_('backups').download(file_path)
            data = json.loads(file_data)
            
            # Truncate and restore (use service role to bypass RLS)
            # WARNING: Be careful with this in production!
            client.table(table).delete().neq('id', 'dummy').execute()
            
            if data:
                client.table(table).insert(data).execute()
            
            logger.info(f"✅ Restored {table} with {len(data)} records")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

# Scheduler for daily backups
backup_system = BackupSystem()

async def run_daily_backup():
    """Called by cron/scheduler"""
    result = await backup_system.create_daily_backup()
    health = await backup_system.check_backup_health()
    return {"backup": result, "health": health}
