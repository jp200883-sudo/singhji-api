"""
🦁 TRISHUL MEMORY ENGINE v1.0
Singh Ji AI — Khud ka Memory System (No mem0!)
Supabase PostgreSQL se chalega
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Supabase ya Local SQLite — dono chalega!
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        logger.info("🧠 Trishul: Supabase connected!")
    else:
        USE_SUPABASE = False
        logger.warning("⚠️ Trishul: Supabase keys missing, using SQLite")
except:
    USE_SUPABASE = False
    logger.warning("⚠️ Trishul: Supabase not available, using SQLite")

# SQLite backup (agar Supabase na chale)
import sqlite3
SQLITE_DB = "trishul_memory.db"

class TrishulMemory:
    """
    त्रिशूल = 3 नोक:
    1. Short-term (session) — fast
    2. Long-term (user history) — save forever  
    3. Agent-specific (context) — smart replies
    """
    
    def __init__(self):
        self._init_sqlite()
        logger.info("🧠 Trishul Memory Engine Initialized!")
    
    def _init_sqlite(self):
        """SQLite table banayo"""
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                agent_id TEXT DEFAULT 'general',
                message TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user ON memories(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)
        ''')
        conn.commit()
        conn.close()
    
    def store(self, user_id: str, message: str, agent_id: str = "general", metadata: dict = None) -> bool:
        """बात याद रखो"""
        try:
            meta_json = json.dumps(metadata) if metadata else "{}"
            
            if USE_SUPABASE:
                # Supabase me save
                supabase.table("memories").insert({
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "message": message,
                    "metadata": meta_json,
                    "created_at": datetime.now().isoformat()
                }).execute()
            else:
                # SQLite me save
                conn = sqlite3.connect(SQLITE_DB)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memories (user_id, agent_id, message, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, agent_id, message, meta_json))
                conn.commit()
                conn.close()
            
            logger.info(f"🧠 Stored: {user_id} | {agent_id} | {message[:30]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Store failed: {e}")
            return False
    
    def recall(self, user_id: str, limit: int = 10) -> List[Dict]:
        """पुरानी बातें याद करो"""
        try:
            if USE_SUPABASE:
                response = supabase.table("memories")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .order("created_at", desc=True)\
                    .limit(limit)\
                    .execute()
                return response.data
            else:
                conn = sqlite3.connect(SQLITE_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM memories 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Recall failed: {e}")
            return []
    
    def search(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """खोजो"""
        try:
            if USE_SUPABASE:
                # Full text search (agar available ho)
                response = supabase.table("memories")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .ilike("message", f"%{query}%")\
                    .limit(limit)\
                    .execute()
                return response.data
            else:
                conn = sqlite3.connect(SQLITE_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM memories 
                    WHERE user_id = ? AND message LIKE ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, f"%{query}%", limit))
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def get_agent_context(self, user_id: str, agent_id: str, limit: int = 5) -> List[Dict]:
        """Agent ke liye context"""
        try:
            if USE_SUPABASE:
                response = supabase.table("memories")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .eq("agent_id", agent_id)\
                    .order("created_at", desc=True)\
                    .limit(limit)\
                    .execute()
                return response.data
            else:
                conn = sqlite3.connect(SQLITE_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM memories 
                    WHERE user_id = ? AND agent_id = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, agent_id, limit))
                rows = cursor.fetchall()
                conn.close()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Context failed: {e}")
            return []
    
    def forget_user(self, user_id: str) -> bool:
        """सब भूल जाओ"""
        try:
            if USE_SUPABASE:
                supabase.table("memories")\
                    .delete()\
                    .eq("user_id", user_id)\
                    .execute()
            else:
                conn = sqlite3.connect(SQLITE_DB)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memories WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
            
            logger.info(f"🧠 Forgot all: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Forget failed: {e}")
            return False
    
    def forget_all(self) -> bool:
        """Sab kuch bhul jao (danger!)"""
        try:
            if USE_SUPABASE:
                # Careful — delete all!
                pass  # Manual hi karna
            else:
                conn = sqlite3.connect(SQLITE_DB)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memories')
                conn.commit()
                conn.close()
            return True
        except:
            return False

# Global instance
trishul = TrishulMemory()
