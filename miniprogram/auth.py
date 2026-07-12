
"""
Singh Ji AI Ultra v8.0 — Mini-Program Auth Module
Developer: Singh Ji
Version: 1.0.0
"""

import jwt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# JWT Config
SECRET_KEY = "singhji-ultra-secret-key-v8"
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
        # Supabase ya local DB se check karo
        # Abhi demo ke liye simple check
        return {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": "Developer",
            "role": "developer"
        }


class DeveloperAuth:
    """Developer authentication helper"""
    
    @staticmethod
    async def register(email: str, password: str, name: str = "", supabase=None):
        """Register new developer"""
        dev_id = str(uuid.uuid4())
        return {
            "status": "success",
            "developer_id": dev_id,
            "email": email,
            "message": "Registration successful! Login karo."
        }
    
    @staticmethod
    async def login(email: str, password: str):
        """Login developer"""
        token = AuthManager.create_token({
            "sub": str(uuid.uuid4()),
            "email": email,
            "role": "developer"
        })
        return {
            "token": token,
            "developer": {
                "email": email,
                "name": "Developer"
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

