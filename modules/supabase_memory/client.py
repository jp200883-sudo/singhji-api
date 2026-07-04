import os
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client: Optional[Client] = None
        self.admin_client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                if self.service_key:
                    self.admin_client = create_client(self.url, self.service_key)
                logger.info("✅ Supabase connected successfully")
            except Exception as e:
                logger.error(f"❌ Supabase connection failed: {e}")
        else:
            logger.warning("⚠️ Supabase credentials missing - using MongoDB fallback")
    
    def is_connected(self) -> bool:
        return self.client is not None
    
    # ========== USER MANAGEMENT ==========
    async def get_user(self, user_id: str) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            response = self.client.table('users').select('*').eq('id', user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    async def create_user(self, user_data: Dict) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            response = self.client.table('users').insert(user_data).execute()
            return response.data
        except Exception as e:
            logger.error(f"Create user error: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict) -> bool:
        if not self.client:
            return False
        try:
            self.client.table('users').update(updates).eq('id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return False
    
    # ========== CHAT HISTORY ==========
    async def save_chat(self, user_id: str, message: str, response: str, 
                        module: str = "general", metadata: Dict = None) -> bool:
        if not self.client:
            return False
        try:
            data = {
                "user_id": user_id,
                "message": message,
                "response": response,
                "module": module,
                "metadata": metadata or {},
                "created_at": "now()"
            }
            self.client.table('chat_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Save chat error: {e}")
            return False
    
    async def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        if not self.client:
            return []
        try:
            response = self.client.table('chat_history')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Get chat history error: {e}")
            return []
    
    # ========== MEMORY/CONTEXT ==========
    async def save_memory(self, user_id: str, key: str, value: Any, 
                          ttl_days: int = 30) -> bool:
        if not self.client:
            return False
        try:
            data = {
                "user_id": user_id,
                "key": key,
                "value": value,
                "expires_at": f"now() + interval '{ttl_days} days'"
            }
            self.client.table('user_memory').upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Save memory error: {e}")
            return False
    
    async def get_memory(self, user_id: str, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            # Clean expired memories first
            self.client.rpc('clean_expired_memories').execute()
            
            response = self.client.table('user_memory')\
                .select('value')\
                .eq('user_id', user_id)\
                .eq('key', key)\
                .single().execute()
            return response.data['value'] if response.data else None
        except Exception as e:
            logger.error(f"Get memory error: {e}")
            return None
    
    # ========== REAL-TIME SUBSCRIPTIONS ==========
    def subscribe_to_table(self, table: str, callback, event: str = "*"):
        if not self.client:
            return None
        return self.client.table(table).on(event, callback).subscribe()
    
    # ========== FILE STORAGE ==========
    async def upload_file(self, bucket: str, path: str, file_data: bytes, 
                          content_type: str = "application/octet-stream") -> Optional[str]:
        if not self.admin_client:
            return None
        try:
            response = self.admin_client.storage.from_(bucket).upload(
                path, file_data, {"content-type": content_type}
            )
            return response.get('path') if response else None
        except Exception as e:
            logger.error(f"Upload file error: {e}")
            return None
    
    async def get_public_url(self, bucket: str, path: str) -> str:
        if not self.client:
            return ""
        return self.client.storage.from_(bucket).get_public_url(path)
    
    # ========== BACKUP & EXPORT ==========
    async def export_table(self, table: str) -> List[Dict]:
        if not self.admin_client:
            return []
        try:
            response = self.admin_client.table(table).select('*').execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Export table error: {e}")
            return []
    
    # ========== ANALYTICS ==========
    async def log_event(self, event_type: str, event_data: Dict, 
                        user_id: str = None) -> bool:
        if not self.client:
            return False
        try:
            data = {
                "event_type": event_type,
                "event_data": event_data,
                "user_id": user_id,
                "ip_address": event_data.get('ip'),
                "user_agent": event_data.get('user_agent'),
                "created_at": "now()"
            }
            self.client.table('events').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Log event error: {e}")
            return False

# Singleton instance
supabase_manager = SupabaseManager()
