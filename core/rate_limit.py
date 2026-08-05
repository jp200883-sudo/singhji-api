import time
from collections import defaultdict
from typing import Tuple
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

# In-memory storage for rate limits
_strict_requests = defaultdict(list)
_global_requests = defaultdict(list)

def _init_rate_limit():
    """Initializes the rate limiter."""
    _strict_requests.clear()
    _global_requests.clear()

def _is_rate_limited(request: Request, limiter_type: str, limit: int, window_seconds: int) -> bool:
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    
    request_log = _strict_requests if limiter_type == "strict" else _global_requests
    
    now = time.time()
    request_log[client_ip] = [t for t in request_log[client_ip] if now - t < window_seconds]
    
    if len(request_log[client_ip]) >= limit:
        return True
    
    request_log[client_ip].append(now)
    return False

# ==========================================================
# 👇 ये दो फंक्शन जोड़े गए हैं ताकि __init__.py एरर न दे
# ==========================================================

async def rate_limit_middleware(request: Request, call_next):
    """
    This is the actual middleware that FastAPI calls.
    We simply pass the request to the next handler.
    The actual rate limiting is handled inside main.py explicitly 
    because your main.py has custom logic for strict vs global paths.
    """
    return await call_next(request)

def get_rate_limit_status() -> dict:
    """Returns the current status of rate limiters (for debugging/admin)."""
    return {
        "strict_ips": len(_strict_requests),
        "global_ips": len(_global_requests),
        "strict_total_requests": sum(len(v) for v in _strict_requests.values()),
        "global_total_requests": sum(len(v) for v in _global_requests.values())
    }
    # ==========================================================
# tg_bot/webhook.py जिस नाम से इस्तेमाल करता है
# ==========================================================
_key_requests = defaultdict(list)

def _rate_check(key: str, limit: int, window_seconds: int) -> bool:
    """
    सीधे किसी key (जैसे 'tg_user:123') के आधार पर rate-limit जाँचें।
    True = limit पार हो गई (रोकना है), False = ठीक है, आगे बढ़ने दें।
    """
    now = time.time()
    _key_requests[key] = [t for t in _key_requests[key] if now - t < window_seconds]

    if len(_key_requests[key]) >= limit:
        return True

    _key_requests[key].append(now)
    return False
