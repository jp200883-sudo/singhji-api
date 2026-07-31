"""
🦁 SINGH JI AI ULTRA v8.0 — NEWS MODULE
Polished: Async, Cached, Retry, Rate-Limited, Superior
"""

from .handler import router
from .handler import handler as legacy_handler

__all__ = ["router", "legacy_handler"]
