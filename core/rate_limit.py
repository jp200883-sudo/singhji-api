import time
from collections import defaultdict
from typing import Tuple
from fastapi import Request

# In-memory storage for rate limits (Strict & Global)
_strict_requests = defaultdict(list)
_global_requests = defaultdict(list)

def _init_rate_limit():
    """Initializes the rate limiter (optional cleanup)."""
    # Can be used to reset counters on startup if needed
    _strict_requests.clear()
    _global_requests.clear()

def _is_rate_limited(request: Request, limiter_type: str, limit: int, window_seconds: int) -> bool:
    """
    Checks if the request is rate limited.
    Returns True if request exceeds the limit, False otherwise.
    """
    # Identify user by IP or User ID (if available via headers)
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    
    # Pick the correct storage dict
    request_log = _strict_requests if limiter_type == "strict" else _global_requests
    
    now = time.time()
    # Cleanup expired entries for this IP
    request_log[client_ip] = [t for t in request_log[client_ip] if now - t < window_seconds]
    
    # Check if limit exceeded
    if len(request_log[client_ip]) >= limit:
        return True
    
    # Add current timestamp
    request_log[client_ip].append(now)
    return False
