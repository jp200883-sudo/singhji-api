

import os
import json
import time
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from functools import wraps

import jwt
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# ─── CONFIG ──────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("ADMIN_API_KEY", "dev-secret-change-me"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# ─── RESPONSE HELPERS ────────────────────────────────────
def success_response(data: Any = None, message: str = "Success", code: int = 200) -> Dict:
    """Standard success JSON response wrapper"""
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def error_response(message: str = "Error", code: int = 400, details: Any = None) -> Dict:
    """Standard error JSON response wrapper"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ─── JWT UTILITIES ───────────────────────────────────────
def create_jwt_token(payload: Dict, expiry_hours: Optional[int] = None) -> str:
    """Create JWT token with expiry"""
    exp = datetime.utcnow() + timedelta(hours=expiry_hours or JWT_EXPIRY_HOURS)
    token_payload = {**payload, "exp": exp, "iat": datetime.utcnow()}
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode and verify JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_jwt_from_request(request: Request) -> Optional[Dict]:
    """Extract and verify JWT from Authorization header"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return decode_jwt_token(auth[7:])
    return None

# ─── AUTH DECORATOR ──────────────────────────────────────
def require_auth(func):
    """Decorator to require valid JWT for API routes"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if request is None:
            for v in kwargs.values():
                if isinstance(v, Request):
                    request = v
                    break

        if request is None:
            raise HTTPException(status_code=500, detail="Request object not found")

        token_data = verify_jwt_from_request(request)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        request.state.user = token_data
        return await func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin role"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if request is None:
            for v in kwargs.values():
                if isinstance(v, Request):
                    request = v
                    break

        if request is None:
            raise HTTPException(status_code=500, detail="Request object not found")

        token_data = verify_jwt_from_request(request)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        if not token_data.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

        request.state.user = token_data
        return await func(*args, **kwargs)
    return wrapper

# ─── VALIDATION HELPERS ──────────────────────────────────
def validate_phone(phone: str) -> bool:
    """Validate Indian phone number"""
    return phone.isdigit() and len(phone) == 10 and phone[0] in "6789"

def validate_aadhaar(aadhaar: str) -> bool:
    """Validate Aadhaar number (12 digits)"""
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return False
    # Verhoeff checksum (simplified — production mein full algo use karna)
    return True

def validate_pan(pan: str) -> bool:
    """Validate PAN number format"""
    if len(pan) != 10:
        return False
    return (pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha())

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input — remove dangerous chars"""
    if not text:
        return ""
    # Remove control chars except newline/tab
    cleaned = "".join(c for c in text[:max_length] if c >= " " or c in "\n\t")
    return cleaned.strip()

# ─── CRYPTO / SECURITY ───────────────────────────────────
def generate_api_key(prefix: str = "sk") -> str:
    """Generate secure random API key"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def hash_password(password: str, salt: Optional[str] = None) -> Dict:
    """Hash password with salt using PBKDF2"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return {"hash": hashed.hex(), "salt": salt}

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against stored hash"""
    new_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(new_hash.hex(), hashed)

def generate_otp(length: int = 6) -> str:
    """Generate numeric OTP"""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))

# ─── REQUEST HELPERS ─────────────────────────────────────
def get_client_ip(request: Request) -> str:
    """Get real client IP from request"""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Get user agent string"""
    return request.headers.get("user-agent", "unknown")

# ─── PAGINATION ──────────────────────────────────────────
def paginate(items: list, page: int = 1, per_page: int = 20) -> Dict:
    """Simple pagination helper"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

# ─── CACHE KEY GENERATOR ─────────────────────────────────
def generate_cache_key(prefix: str, *args) -> str:
    """Generate consistent cache key"""
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return hashlib.md5(raw.encode()).hexdigest()

# ─── DATE/TIME UTILITIES ─────────────────────────────────
def format_datetime(dt: Optional[datetime] = None, fmt: str = "%d %b %Y, %I:%M %p") -> str:
    """Format datetime in Indian format"""
    return (dt or datetime.utcnow()).strftime(fmt)

def time_ago(timestamp: Union[str, datetime]) -> str:
    """Human readable time ago"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    diff = datetime.utcnow() - timestamp.replace(tzinfo=None)
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{seconds // 60} min ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    elif seconds < 604800:
        return f"{seconds // 86400} days ago"
    else:
        return timestamp.strftime("%d %b %Y")

# ─── LOGGING UTILITIES ───────────────────────────────────
def log_api_call(endpoint: str, method: str, status: int, duration_ms: float, user_id: Optional[str] = None):
    """Structured API call logging"""
    print(f"[API] {method} {endpoint} | {status} | {duration_ms:.2f}ms | user={user_id or 'anon'}")

# ─── FILE UTILITIES ──────────────────────────────────────
def safe_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
    return "".join(c if c in keep else "_" for c in filename)[:100]

def format_bytes(size: int) -> str:
    """Format bytes to human readable"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

# ─── EXPORT ──────────────────────────────────────────────
__all__ = [
    "success_response", "error_response",
    "create_jwt_token", "decode_jwt_token", "verify_jwt_from_request",
    "require_auth", "require_admin",
    "validate_phone", "validate_aadhaar", "validate_pan", "sanitize_input",
    "generate_api_key", "hash_password", "verify_password", "generate_otp",
    "get_client_ip", "get_user_agent",
    "paginate", "generate_cache_key",
    "format_datetime", "time_ago",
    "log_api_call", "safe_filename", "format_bytes"
]
