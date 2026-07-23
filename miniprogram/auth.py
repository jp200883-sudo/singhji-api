"""
Singh Ji AI Ultra v8.0 — Mini-Program Auth Module
Developer: Singh Ji
Version: 1.0.0
"""

import os
import jwt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# JWT Config — hardcoded fallback nahi, sirf env variable se
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY env variable set nahi hai! "
        "Railway par ek strong random string set karo, warna auth insecure rahega."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 din


class AuthManager:
    """JWT Token management"""
    
    @staticmethod
    def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expire ho gaya!")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token!")
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()


class MiniAuth:
    """Mini-Program authentication"""

    @staticmethod
    async def authenticate(email: str, password: str) -> Optional[Dict]:
        """Supabase se developer record nikalkar password_hash match karo"""
        from .storage import storage

        record = storage.get_record("miniprogram_developers", "email", email)
        if not record:
            return None

        password_hash = AuthManager.hash_password(password)
        if not hmac_compare(record.get("password_hash", ""), password_hash):
            return None

        return {
            "id": record.get("id"),
            "email": record.get("email"),
            "name": record.get("full_name", "Developer"),
            "role": "developer"
        }


def hmac_compare(a: str, b: str) -> bool:
    """Constant-time string comparison (timing-attack se bachne ke liye)"""
    import hmac as _hmac
    return _hmac.compare_digest(a or "", b or "")


class DeveloperAuth:
    """Developer authentication helper"""

    @staticmethod
    async def register(email: str, password: str, name: str = "", supabase=None):
        """Register new developer — Supabase mein save karo"""
        from .storage import storage

        existing = storage.get_record("miniprogram_developers", "email", email)
        if existing:
            return {
                "status": "error",
                "message": "Ye email pehle se registered hai!"
            }

        dev_id = str(uuid.uuid4())
        record = storage.insert_record("miniprogram_developers", {
            "id": dev_id,
            "email": email,
            "password_hash": AuthManager.hash_password(password),
            "full_name": name or "Developer"
        })

        if not record:
            return {
                "status": "error",
                "message": "Registration fail ho gaya, dobara try karo."
            }

        return {
            "status": "success",
            "developer_id": dev_id,
            "email": email,
            "message": "Registration successful! Login karo."
        }

    @staticmethod
    async def login(email: str, password: str):
        """Login developer — password asli verify hota hai ab"""
        developer = await MiniAuth.authenticate(email, password)
        if not developer:
            raise ValueError("Email ya password galat hai!")

        token = AuthManager.create_token({
            "sub": developer["id"],
            "email": developer["email"],
            "role": developer["role"]
        })
        return {
            "token": token,
            "developer": {
                "email": developer["email"],
                "name": developer["name"]
            }
        }
    
    @staticmethod
    async def refresh_token(token: str):
        """Refresh JWT token"""
        payload = AuthManager.verify_token(token)
        new_token = AuthManager.create_token({
            "sub": payload["sub"],
            "email": payload.get("email"),
            "role": payload.get("role", "developer")
        })
        return {"token": new_token}


async def get_current_developer(token: str = None):
    """Get current developer from token"""
    if not token:
        raise ValueError("Token required!")
    
    payload = AuthManager.verify_token(token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "developer")
    }
