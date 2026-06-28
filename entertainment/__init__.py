# Entertainment module
from .gaming_handler import *
from .lifestyle_handler import *
from .music_handler import *
from .ramayan_handler import *
from .video_handler import *

from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def entertainment_root():
    return {
        "ok": True,
        "module": "entertainment",
        "status": "✅ LIVE",
        "message": "Entertainment module ready!"
    }
