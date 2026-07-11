import os
import json
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🔱 TRISHUL: FORCE SUPABASE_SERVICE_KEY ONLY
# Public SUPABASE_KEY ko IGNORE karo
# ═══════════════════════════════════════════════════════
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# SIRF service_role key use karo - public/anon key nahi
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Agar service key nahi mili toh warning do, public key mat lo
if not SUPABASE_KEY:
    logger.warning("⚠️ Trishul: SUPABASE_SERVICE_KEY nahi mila! Supabase OFF.")

DATABASE_URL = os.getenv("DATABASE_URL", "")
POOLER_URL = os.getenv("POOLER_URL", "")

USE_SUPABASE = False
supabase = None

# Try Supabase client - SIRF service_role key se
try:
    from supabase import create_client
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        logger.info("🧠 Trishul: Supabase SERVICE_ROLE se connected!")
    else:
        logger.warning("⚠️ Trishul: Supabase URL ya SERVICE_KEY missing")
except Exception as e:
    logger.warning(f"⚠️ Trishul: Supabase client fail — {e}")

# Try Pooler
USE_POOLER = False
POOL_AVAILABLE = False
pool_conn = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POOL_AVAILABLE = True
except:
    pass

if DATABASE_URL and "pooler" in DATABASE_URL:
    USE_POOLER = True
    try:
        pool_conn = psycopg2.connect(DATABASE_URL)
        logger.info("🧠 Trishul: Pooler connected!")
    except Exception as e:
        logger.warning(f"⚠️ Trishul: Pooler fail — {e}")
        USE_POOLER = False

import sqlite3
SQLITE_DB = "trishul_memory.db"

class TrishulMemory:
    def __init__(self):
        self._init_sqlite()
        logger.info("🧠 Trishul Memory Engine Initialized!")

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

    def store(self, user_id, message, agent_id="general", metadata=None):
        meta_json = json.dumps(metadata) if metadata else "{}"
        if USE_SUPABASE and supabase:
            try:
                supabase.table("memories").insert({
                    "user_id": user_id, "agent_id": agent_id, "message": message,
                    "metadata": meta_json, "created_at": datetime.now().isoformat()
                }).execute()
                return True
            except Exception as e:
                logger.error(f"❌ Supabase store: {e}")
        if USE_POOLER and pool_conn:
            try:
                cursor = pool_conn.cursor()
                cursor.execute("INSERT INTO memories (user_id, agent_id, message, metadata) VALUES (%s, %s, %s, %s)",
                             (user_id, agent_id, message, meta_json))
                pool_conn.commit()
                return True
            except Exception as e:
                logger.error(f"❌ Pooler store: {e}")
        try:
            conn = sqlite3.connect(SQLITE_DB)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO memories (user_id, agent_id, message, metadata) VALUES (?, ?, ?, ?)",
                         (user_id, agent_id, message, meta_json))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ SQLite store: {e}")
            return False

    def recall(self, user_id, limit=10):
        if USE_SUPABASE and supabase:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase recall: {e}")
        if USE_POOLER and pool_conn:
            try:
                cursor = pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler recall: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def search(self, user_id, query, limit=5):
        if USE_SUPABASE and supabase:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).ilike("message", f"%{query}%").limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase search: {e}")
        if USE_POOLER and pool_conn:
            try:
                cursor = pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s AND message ILIKE %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, f"%{query}%", limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler search: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? AND message LIKE ? ORDER BY created_at DESC LIMIT ?",
                     (user_id, f"%{query}%", limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_agent_context(self, user_id, agent_id, limit=5):
        if USE_SUPABASE and supabase:
            try:
                resp = supabase.table("memories").select("*").eq("user_id", user_id).eq("agent_id", agent_id).order("created_at", desc=True).limit(limit).execute()
                return resp.data
            except Exception as e:
                logger.error(f"❌ Supabase context: {e}")
        if USE_POOLER and pool_conn:
            try:
                cursor = pool_conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM memories WHERE user_id = %s AND agent_id = %s ORDER BY created_at DESC LIMIT %s",
                             (user_id, agent_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Pooler context: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE user_id = ? AND agent_id = ? ORDER BY created_at DESC LIMIT ?",
                     (user_id, agent_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def forget_user(self, user_id):
        if USE_SUPABASE and supabase:
            try:
                supabase.table("memories").delete().eq("user_id", user_id).execute()
                return True
            except Exception as e:
                logger.error(f"❌ Supabase forget: {e}")
        if USE_POOLER and pool_conn:
            try:
                cursor = pool_conn.cursor()
                cursor.execute("DELETE FROM memories WHERE user_id = %s", (user_id,))
                pool_conn.commit()
                return True
            except Exception as e:
                logger.error(f"❌ Pooler forget: {e}")
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

trishul = TrishulMemory()
