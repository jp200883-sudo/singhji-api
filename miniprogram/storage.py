"""
📦 Storage Module — Supabase connection for Mini-Program
"""
import os
import json
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

from .config import MiniProgramConfig


class StorageManager:
    """Supabase Storage Manager"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Supabase se connect karo"""
        if not MiniProgramConfig.is_storage_ready():
            print("⚠️ Supabase config missing — storage disabled")
            return
        
        try:
            self.client = create_client(
                MiniProgramConfig.SUPABASE_URL,
                MiniProgramConfig.SUPABASE_KEY
            )
            print("✅ Supabase connected!")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
    
    def is_connected(self) -> bool:
        """Check karo connected hai ya nahi"""
        return self.client is not None
    
    # 📁 Bucket Operations
    def create_bucket(self, bucket_name: str = None) -> bool:
        """Naya bucket banayo"""
        if not self.is_connected():
            return False
        
        bucket = bucket_name or MiniProgramConfig.SUPABASE_BUCKET
        try:
            self.client.storage.create_bucket(bucket, options={"public": True})
            return True
        except Exception as e:
            print(f"Bucket create error: {e}")
            return False
    
    def list_buckets(self) -> List[Dict]:
        """Sare buckets dikhayo"""
        if not self.is_connected():
            return []
        try:
            return self.client.storage.list_buckets()
        except Exception as e:
            print(f"List buckets error: {e}")
            return []
    
    # 📤 Upload
    def upload_file(self, file_path: str, file_data: bytes, 
                    bucket_name: str = None, content_type: str = None) -> Optional[str]:
        """File upload karo"""
        if not self.is_connected():
            return None
        
        bucket = bucket_name or MiniProgramConfig.SUPABASE_BUCKET
        try:
            result = self.client.storage.from_(bucket).upload(
                file_path, 
                file_data,
                file_options={"content-type": content_type or "application/octet-stream"}
            )
            # Public URL nikalo
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def upload_app_icon(self, app_id: str, image_data: bytes) -> Optional[str]:
        """App icon upload karo"""
        path = f"app-icons/{app_id}/icon.png"
        return self.upload_file(path, image_data, content_type="image/png")
    
    def upload_app_asset(self, app_id: str, file_name: str, file_data: bytes) -> Optional[str]:
        """App asset upload karo"""
        path = f"app-assets/{app_id}/{file_name}"
        return self.upload_file(path, file_data)
    
    # 📥 Download
    def download_file(self, file_path: str, bucket_name: str = None) -> Optional[bytes]:
        """File download karo"""
        if not self.is_connected():
            return None
        
        bucket = bucket_name or MiniProgramConfig.SUPABASE_BUCKET
        try:
            return self.client.storage.from_(bucket).download(file_path)
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    # 🗑️ Delete
    def delete_file(self, file_path: str, bucket_name: str = None) -> bool:
        """File delete karo"""
        if not self.is_connected():
            return False
        
        bucket = bucket_name or MiniProgramConfig.SUPABASE_BUCKET
        try:
            self.client.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    # 📊 Database Operations (Supabase PostgreSQL)
    def insert_record(self, table: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Record insert karo"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Insert error: {e}")
            return None
    
    def get_record(self, table: str, column: str, value: Any) -> Optional[Dict]:
        """Record nikalo"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table(table).select("*").eq(column, value).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Get error: {e}")
            return None
    
    def update_record(self, table: str, column: str, value: Any, 
                      data: Dict[str, Any]) -> Optional[Dict]:
        """Record update karo"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table(table).update(data).eq(column, value).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Update error: {e}")
            return None
    
    def delete_record(self, table: str, column: str, value: Any) -> bool:
        """Record delete karo"""
        if not self.is_connected():
            return False
        
        try:
            self.client.table(table).delete().eq(column, value).execute()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False


# Global instance
storage = StorageManager()
