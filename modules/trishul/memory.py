"""
🦁 TRISHUL MEMORY ENGINE v2.0
Singh Ji AI — Pooler Connection Support!
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# POOLER CONNECTION
DATABASE_URL = os.getenv("DATABASE_URL", "")
POOLER_URL = os.getenv("POOLER_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "") or os.getenv("SUPABASE_KEY", "")

USE_POOLER = False
connection_string = ""

if POOLER_URL:
    connection_string = POOLER_URL
    USE_POOLER = True
    logger.info("🧠 Trishul: Pooler URL mil gayi!")
elif DATABASE_URL and "pooler" in DATABASE_URL:
    connection_string = DATABASE_URL
    USE_POOLER = True
    logger.info("🧠 Trishul: DATABASE_URL mein Pooler hai!")
elif SUPABASE_URL and SUPABASE_KEY:
    USE_POOLER = False
    logger.info("🧠 Trishul: Direct Supabase try kar raha hoon...")
else:
    logger.warning("⚠️ Trishul: Koi connection nahi mila!")

USE_SUPABASE = False
supabase = None
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_KEY and not USE_POOLER:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        logger.info("🧠 Trishul: Supabase direct connected!")
except Exception as e:
    logger.warning(f"⚠️ Trishul: Supabase direct fail — {e}")

POOL_AVAILABLE = False
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POOL_AVAILABLE = True
except:
    pass

import sqlite3
SQLITE_DB = "trishul_memory.db"


class TrishulMemory:
    def __init__(self):
        self.pool_conn = None
        self._init_pooler()
        self._init_sqlite()
        logger.info("🧠 Trishul Memory Engine Initialized!")

    def _init_pooler(self):
        if not USE_POOLER or not POOL_AVAILABLE:
            return
        try:
            self.pool_conn = psycopg2.connect(connection_string)
            cursor = self.pool_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    agent_id TEXT DEFAULT 'general',
                    message TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON memories(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)')
            self.pool_conn.commit()
            logger.info("🧠 Trishul: Pooler table ready!")
        except Exception as e:
            logger.error(f"❌ Pooler init failed: {e}")
            self.pool_conn = None

    def _init_sqlite(self):
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                agent_id TEXT DEFAULT 'general',
                message TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON memories(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)')
        conn.commit()
        conn.close()

    def store(self, user_id: str, message: str, agent_id: str = "general", metadata: dict = None) -> bool:
        meta_json = json.dumps(metadata) if metadata else "{}"
        if self.pool_conn:
            try:
                cursor = self.pool_conn.cursor()
                cursor.execute("INSERT INTO memories (user_id, agent_id, message, metadata) VALUES (%s, %s, %s, %s)",
                             (user_id, agent_id, message, meta_json))
                self.pool_conn.commit()
                logger.info(f"🧠 Pooler stored: {user_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Pooler store failed: {e}")
        if USE_SUPABASE:
            try:
                supabase.table("memories").insert({
                    "user_id": user_id, "agent_id": agent_id, "message": message,
                    "metadata": meta_json, "created_at": datetime.now().isoformat()
                }).execute()
                logger.info(f"🧠 Supabase stored: {user_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Supabase store failed: {e}")
        try:
            conn = sqlite3.connect(SQLITE_DB)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO memories (user_id, agent_id, message, metadata) VALUES (?, ?, ?, ?)",
                         (user_id, agent_id, message, meta_json))
            conn.commit()
            conn.close()
            logger.info(f"🧠 SQLite stored: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ SQLite store failed: {e}")
            return False

    def recall(self, user_id: str, limit: int = 10) -> List[Dict]:
        if self.pool_conn:
            try:
                cursor = self.pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler recall failed: {e}")
        if USE_SUPABASE:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase recall failed: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def search(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        if self.pool_conn:
            try:
                cursor = self.pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s AND message ILIKE %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, f"%{query}%", limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler search failed: {e}")
        if USE_SUPABASE:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).ilike("message", f"%{query}%").limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase search failed: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? AND message LIKE ? ORDER BY created_at DESC LIMIT ?",
                     (user_id, f"%{query}%", limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_agent_context(self, user_id: str, agent_id: str, limit: int = 5) -> List[Dict]:
        if self.pool_conn:
            try:
                cursor = self.pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s AND agent_id = %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, agent_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler context failed: {e}")
        if USE_SUPABASE:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).eq("agent_id", agent_id).order("created_at", desc=True).limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase context failed: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? AND agent_id = ? ORDER BY created_at DESC LIMIT ?",
                     (user_id, agent_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def forget_user(self, user_id: str) -> bool:
        if self.pool_conn:
            try:
                cursor = self.pool_conn.cursor()
                cursor.execute("DELETE FROM memories WHERE user_id = %s", (user_id,))
                self.pool_conn.commit()
                logger.info(f"🧠 Pooler forgot: {user_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Pooler forget failed: {e}")
        if USE_SUPABASE:
            try:
                supabase.table("memories").delete().eq("user_id", user_id).execute()
                logger.info(f"🧠 Supabase forgot: {user_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Supabase forget failed: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"🧠 SQLite forgot: {user_id}")
        return True


trishul = TrishulMemory()
