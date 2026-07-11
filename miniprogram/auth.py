"""
🔐 Auth System — JWT + Developer Registration/Login
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import MiniProgramConfig
from .models import Developer

security = HTTPBearer()


class AuthManager:
    """JWT Token Manager"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Password hash karo"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Password verify karo"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """JWT token banao"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or MiniProgramConfig.JWT_ACCESS_TOKEN_EXPIRE)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, MiniProgramConfig.JWT_SECRET_KEY, algorithm=MiniProgramConfig.JWT_ALGORITHM)
    
    @staticmethod
    def create_access_token(developer_id: str, email: str) -> str:
        """Access token banao"""
        return AuthManager.create_token(
            {"sub": developer_id, "email": email, "type": "access"},
            MiniProgramConfig.JWT_ACCESS_TOKEN_EXPIRE
        )
    
    @staticmethod
    def create_refresh_token(developer_id: str, email: str) -> str:
        """Refresh token banao"""
        return AuthManager.create_token(
            {"sub": developer_id, "email": email, "type": "refresh"},
            MiniProgramConfig.JWT_REFRESH_TOKEN_EXPIRE
        )
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Token decode karo"""
        try:
            payload = jwt.decode(
                token, 
                MiniProgramConfig.JWT_SECRET_KEY, 
                algorithms=[MiniProgramConfig.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expire ho gaya hai!")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token!")
    
    @staticmethod
    async def get_current_developer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Current developer nikalo — API endpoints ke liye"""
        token = credentials.credentials
        payload = AuthManager.decode_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Access token chahiye!")
        
        return {
            "developer_id": payload.get("sub"),
            "email": payload.get("email")
        }


class DeveloperAuth:
    """Developer Registration & Login"""
    
    @staticmethod
    async def register(db, email: str, password: str, full_name: str, 
                       company_name: str = None, phone: str = None) -> Dict[str, Any]:
        """Naya developer register karo"""
        
        # Check karo email already exist toh nahi
        existing = db.query(Developer).filter(Developer.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered!")
        
        # Password hash karo
        password_hash = AuthManager.hash_password(password)
        
        # Developer banayo
        developer = Developer(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            company_name=company_name,
            phone=phone
        )
        
        db.add(developer)
        db.commit()
        db.refresh(developer)
        
        # Tokens banayo
        access_token = AuthManager.create_access_token(developer.id, developer.email)
        refresh_token = AuthManager.create_refresh_token(developer.id, developer.email)
        
        return {
            "success": True,
            "message": "Registration successful! 🎉",
            "developer": developer.to_dict(),
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
        }
    
    @staticmethod
    async def login(db, email: str, password: str) -> Dict[str, Any]:
        """Developer login karo"""
        
        developer = db.query(Developer).filter(Developer.email == email).first()
        if not developer:
            raise HTTPException(status_code=401, detail="Email ya password galat hai!")
        
        if not developer.is_active:
            raise HTTPException(status_code=403, detail="Account suspended hai!")
        
        if not AuthManager.verify_password(password, developer.password_hash):
            raise HTTPException(status_code=401, detail="Email ya password galat hai!")
        
        # Last login update karo
        developer.last_login = datetime.utcnow()
        db.commit()
        
        # Tokens banayo
        access_token = AuthManager.create_access_token(developer.id, developer.email)
        refresh_token = AuthManager.create_refresh_token(developer.id, developer.email)
        
        return {
            "success": True,
            "message": "Login successful! 🎉",
            "developer": developer.to_dict(),
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
        }
    
    @staticmethod
    async def refresh_token(token: str) -> Dict[str, Any]:
        """Token refresh karo"""
        payload = AuthManager.decode_token(token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Refresh token chahiye!")
        
        developer_id = payload.get("sub")
        email = payload.get("email")
        
        new_access = AuthManager.create_access_token(developer_id, email)
        
        return {
            "access_token": new_access,
            "token_type": "Bearer"
        }
