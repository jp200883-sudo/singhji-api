cat > miniprogram/storage.py << 'EOF'
"""🦁 Mini-Program Storage — 10MB/user"""
import json
from datetime import datetime

class MiniStorage:
    MAX_MB = 10
    _storage = {}
    _usage = {}
    
    @classmethod
    def _ns(cls, app_id, user_id):
        return f"mini:{app_id}:{user_id}"
    
    @classmethod
    def put(cls, app_id, user_id, key, value):
        value_str = json.dumps(value)
        value_size = len(value_str.encode())
        ns = cls._ns(app_id, user_id)
        usage = cls._usage.get(ns, 0)
        if usage + value_size > cls.MAX_MB * 1024 * 1024:
            return {"error": "Storage quota exceeded (10MB)"}
        if ns not in cls._storage:
            cls._storage[ns] = {}
        old_size = len(json.dumps(cls._storage[ns].get(key, {})).encode())
        cls._usage[ns] = usage - old_size + value_size
        cls._storage[ns][key] = {"value": value, "timestamp": datetime.now().isoformat(), "size": value_size}
        return {"saved": True, "key": key, "size": value_size}
    
    @classmethod
    def get(cls, app_id, user_id, key):
        ns = cls._ns(app_id, user_id)
        data = cls._storage.get(ns, {}).get(key)
        if not data:
            return None
        return {"key": key, "value": data["value"], "timestamp": data["timestamp"], "size": data["size"]}
    
    @classmethod
    def delete(cls, app_id, user_id, key):
        ns = cls._ns(app_id, user_id)
        if ns in cls._storage and key in cls._storage[ns]:
            old_size = cls._storage[ns][key]["size"]
            del cls._storage[ns][key]
            cls._usage[ns] = max(0, cls._usage.get(ns, 0) - old_size)
            return {"deleted": True}
        return {"deleted": False, "error": "Key not found"}
EOF
