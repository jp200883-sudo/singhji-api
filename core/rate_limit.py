import time
import threading
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException

# ==========================================
# RATE LIMIT STORE
# ==========================================
RATE_LIMIT: Dict[str, List[float]] = {}

# ==========================================
# GENERIC KEYED RATE LIMIT (Telegram per-user, etc.)
# ==========================================
_rate_lock = threading.Lock()
_rate_buckets: Dict[str, List[float]] = defaultdict(list)


def _rate_check(key: str, max_calls: int, window_seconds: int) -> bool:
    """
    Generic keyed rate limiter — koi bhi custom key (jaise 'tg_user:12345')
    ke liye rate limit check karta hai. IP-based middleware se alag hai.
    Return: True agar limit cross ho gayi (rate-limited), False agar OK hai.
    """
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets[key]
        while bucket and bucket[0] < now - window_seconds:
            bucket.pop(0)
        if len(bucket) >= max_calls:
            return True
        bucket.append(now)
        return False

# Default limits (आप चाहें तो config से ले सकते हैं)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX = 30     # 30 requests per window

def rate_limit_middleware(request: Request) -> None:
    """
    Rate limit middleware - limits requests per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    window = RATE_LIMIT_WINDOW
    max_requests = RATE_LIMIT_MAX
    
    # Get or create IP entry
    if client_ip not in RATE_LIMIT:
        RATE_LIMIT[client_ip] = []
    
    # Clean old requests
    RATE_LIMIT[client_ip] = [
        t for t in RATE_LIMIT[client_ip] 
        if current_time - t < window
    ]
    
    # Check if over limit
    if len(RATE_LIMIT[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Limit: {max_requests} per {window} seconds"
        )
    
    # Add current request
    RATE_LIMIT[client_ip].append(current_time)

def get_rate_limit_status(ip: str) -> dict:
    """Get rate limit status for an IP"""
    if ip not in RATE_LIMIT:
        return {"requests": 0, "limit": RATE_LIMIT_MAX}
    
    current_time = time.time()
    window = RATE_LIMIT_WINDOW
    active_requests = [
        t for t in RATE_LIMIT[ip] 
        if current_time - t < window
    ]
    
    return {
        "requests": len(active_requests),
        "limit": RATE_LIMIT_MAX,
        "remaining": RATE_LIMIT_MAX - len(active_requests),
        "reset_in": int(window - (current_time - (active_requests[0] if active_requests else current_time)))
    }

def reset_rate_limit(ip: str = None) -> None:
    """Reset rate limit for specific IP or all"""
    if ip:
        RATE_LIMIT.pop(ip, None)
    else:
        RATE_LIMIT.clear()
