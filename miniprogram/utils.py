"""
miniprogram/utils.py — Singh Ji AI Ultra v8.0
Common utilities for miniprogram portal module.
"""

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


# ─── APP ID / SECRET GENERATORS ──────────────────────────
def generate_app_id(prefix: str = "app") -> str:
    """Generate unique app ID for miniprogram"""
    timestamp = int(time.time())
    random_part = secrets.token_hex(4)
    return f"{prefix}_{timestamp}_{random_part}"

def generate_secret(length: int = 32) -> str:
    """Generate secure secret key"""
    return secrets.token_urlsafe(length)

def generate_nonce(length: int = 16) -> str:
    """Generate random nonce for API requests"""
    return secrets.token_hex(length // 2)

def generate_short_id(length: int = 8) -> str:
    """Generate short alphanumeric ID"""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(chars) for _ in range(length))

# ─── SIGNATURE UTILITIES ─────────────────────────────────
def generate_signature(payload: Dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook/API verification"""
    message = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

def verify_signature(payload: Dict, secret: str, signature: str) -> bool:
    """Verify HMAC-SHA256 signature"""
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(expected, signature)

# ─── RATE LIMIT HELPERS ──────────────────────────────────
def check_rate_limit(key: str, max_requests: int, window_seconds: int, store: Dict) -> bool:
    """Simple in-memory rate limit check"""
    now = time.time()
    if key not in store:
        store[key] = []
    # Clean old entries
    store[key] = [t for t in store[key] if now - t < window_seconds]
    if len(store[key]) >= max_requests:
        return False  # Rate limited
    store[key].append(now)
    return True  # OK

# ─── PHONE OTP HELPERS ───────────────────────────────────
def mask_phone(phone: str) -> str:
    """Mask phone number: 9876543210 → 98****3210"""
    if len(phone) >= 10:
        return phone[:2] + "****" + phone[-4:]
    return "****"

def format_phone(phone: str) -> str:
    """Format phone to +91 standard"""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    return digits

# ─── JSON HELPERS ────────────────────────────────────────
def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safe JSON parse with fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

def pretty_json(data: Any) -> str:
    """Pretty print JSON"""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)

# ─── ENVIRONMENT HELPERS ─────────────────────────────────
def get_env_int(key: str, default: int = 0) -> int:
    """Get integer from env var"""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from env var"""
    val = os.getenv(key, "").lower()
    return val in ("true", "1", "yes", "on") if val else default


# ─── APP CODE / INVITE CODE VALIDATORS ───────────────────
def validate_app_code(code: str) -> bool:
    """Validate miniprogram app registration code"""
    if not code or len(code) < 6:
        return False
    # Format: 6+ alphanumeric chars, no special chars
    return code.isalnum() and len(code) <= 20

def validate_invite_code(code: str) -> bool:
    """Validate invite/referral code"""
    if not code or len(code) < 4:
        return False
    return code.isalnum() and len(code) <= 16

def generate_invite_code(length: int = 8) -> str:
    """Generate random invite code"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # No confusing chars (0,O,I,1)
    return "".join(secrets.choice(chars) for _ in range(length))

# ─── UPI / PAYMENT VALIDATORS ────────────────────────────
def validate_upi_id(upi: str) -> bool:
    """Validate UPI ID format"""
    if not upi or "@" not in upi:
        return False
    parts = upi.split("@")
    return len(parts) == 2 and len(parts[0]) >= 3 and len(parts[1]) >= 3

def validate_ifsc(ifsc: str) -> bool:
    """Validate IFSC code (11 chars: 4 alpha + 0 + 6 alphanumeric)"""
    if len(ifsc) != 11:
        return False
    return (ifsc[:4].isalpha() and ifsc[4] == "0" and ifsc[5:].isalnum())

# ─── ID GENERATORS ─────────────────────────────────────
def generate_order_id(prefix: str = "ORD") -> str:
    """Generate unique order ID"""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand = secrets.token_hex(3).upper()
    return f"{prefix}{ts}{rand}"

def generate_transaction_id() -> str:
    """Generate unique transaction reference"""
    ts = int(time.time())
    rand = secrets.token_hex(4)
    return f"TXN{ts}{rand}"

# ─── STRING UTILITIES ──────────────────────────────────
def slugify(text: str) -> str:
    """Convert text to URL slug"""
    text = text.lower().strip()
    keep = "abcdefghijklmnopqrstuvwxyz0123456789-"
    return "".join(c if c in keep else "-" for c in text)[:50]

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate text with ellipsis"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix

# ─── NUMBER UTILITIES ────────────────────────────────────
def format_inr(amount: float) -> str:
    """Format amount in Indian Rupees: ₹1,23,456.00"""
    return f"₹{amount:,.2f}"

def format_number(num: int) -> str:
    """Format large numbers: 1,23,456"""
    s = str(num)
    if len(s) <= 3:
        return s
    # Indian numbering: 1,23,456
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.append(rest[-2:] if len(rest) >= 2 else rest)
        rest = rest[:-2]
    return ",".join(reversed(groups)) + "," + last3

# ─── EXPORT ──────────────────────────────────────────────
__all__ = [
    "success_response", "error_response",
    "create_jwt_token", "decode_jwt_token", "verify_jwt_from_request",
    "require_auth", "require_admin",
    "validate_phone", "validate_aadhaar", "validate_pan", "sanitize_input",
    "validate_app_code", "validate_invite_code", "generate_invite_code",
    "validate_upi_id", "validate_ifsc",
    "generate_api_key", "hash_password", "verify_password", "generate_otp",
    "generate_app_id", "generate_secret", "generate_nonce", "generate_short_id",
    "generate_order_id", "generate_transaction_id",
    "generate_signature", "verify_signature",
    "check_rate_limit", "mask_phone", "format_phone",
    "safe_json_loads", "pretty_json",
    "get_env_int", "get_env_bool",
    "get_client_ip", "get_user_agent",
    "paginate", "generate_cache_key",
    "format_datetime", "time_ago",
    "slugify", "truncate", "format_inr", "format_number",
    "log_api_call", "safe_filename", "format_bytes"
]
