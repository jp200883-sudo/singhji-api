import time
from collections import defaultdict, deque

_rate_lock = None
_rate_buckets = None

def _init_rate_limit():
    global _rate_lock, _rate_buckets
    import threading
    _rate_lock = threading.Lock()
    _rate_buckets = defaultdict(deque)

def _client_ip(request):
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _rate_check(key: str, max_calls: int, window_seconds: int) -> bool:
    global _rate_buckets
    if _rate_buckets is None:
        _init_rate_limit()
    now = time.time()
    with _rate_lock:
        dq = _rate_buckets[key]
        while dq and dq[0] < now - window_seconds:
            dq.popleft()
        if len(dq) >= max_calls:
            return True
        dq.append(now)
        return False

def _is_rate_limited(request, bucket: str, max_calls: int, window_seconds: int) -> bool:
    ip = _client_ip(request)
    return _rate_check(f"{bucket}:{ip}", max_calls, window_seconds)
