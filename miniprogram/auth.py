cat > miniprogram/auth.py << 'EOF'
"""🦁 Mini-Program Auth"""
import os, jwt, hashlib
from datetime import datetime, timedelta

class MiniAuth:
    SECRET_KEY = os.getenv("MINI_SECRET", "singhji_mini_2026")
    APPROVED_APPS = {}
    DEVELOPERS = {}
    
    @classmethod
    def register_developer(cls, name, email, business_type):
        dev_id = f"dev_{hashlib.md5(email.encode()).hexdigest()[:12]}"
        api_key = f"sk_{os.urandom(16).hex()}"
        cls.DEVELOPERS[dev_id] = {
            "id": dev_id, "name": name, "email": email,
            "business_type": business_type, "api_key": api_key,
            "registered_at": datetime.now().isoformat(), "apps": [], "status": "active"
        }
        return {"developer_id": dev_id, "api_key": api_key}
    
    @classmethod
    def submit_app(cls, developer_id, name, app_type, code, permissions):
        if developer_id not in cls.DEVELOPERS:
            return {"error": "Developer not found"}
        app_id = f"app_{os.urandom(8).hex()}"
        cls.APPROVED_APPS[app_id] = {
            "id": app_id, "developer_id": developer_id, "name": name,
            "type": app_type, "code": code, "permissions": permissions,
            "status": "pending_review", "submitted_at": datetime.now().isoformat()
        }
        cls.DEVELOPERS[developer_id]["apps"].append(app_id)
        return {"app_id": app_id, "status": "pending_review"}
    
    @classmethod
    def approve_app(cls, app_id):
        if app_id not in cls.APPROVED_APPS:
            return {"error": "App not found"}
        cls.APPROVED_APPS[app_id]["status"] = "approved"
        cls.APPROVED_APPS[app_id]["approved_at"] = datetime.now().isoformat()
        return {"status": "approved", "app_id": app_id}
    
    @classmethod
    def generate_token(cls, app_id, user_phone):
        if app_id not in cls.APPROVED_APPS:
            raise ValueError("App not approved")
        payload = {
            "app_id": app_id,
            "user_phone_hash": hashlib.sha256(user_phone.encode()).hexdigest()[:16],
            "permissions": cls.APPROVED_APPS[app_id]["permissions"],
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm="HS256")
    
    @classmethod
    def validate_token(cls, token):
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=["HS256"])
            return {"app_id": payload["app_id"], "user_id": payload["user_phone_hash"],
                    "permissions": payload["permissions"]}
        except:
            return None
EOF
