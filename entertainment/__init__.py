# entertainment/__init__.py
# 🎬 Singh Ji AI Ultra v5.0 — Entertainment Hub
# केला मोड ON — केला नहीं होता भाई अकेला! 🍌

from .music_handler import router as music_router
from .video_handler import router as video_router
from .ramayan_handler import router as ramayan_router
from .gaming_handler import router as gaming_router

__all__ = [
    "music_router",
    "video_router", 
    "ramayan_router",
    "gaming_router"
]
