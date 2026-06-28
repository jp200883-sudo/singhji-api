from fastapi import APIRouter

# Sab handlers import karo
from .gaming_handler import get_gaming_content
from .lifestyle_handler import get_lifestyle_content
from .music_handler import get_music_content
from .ramayan_handler import get_ramayan_content
from .video_handler import get_video_content

router = APIRouter()

@router.get("/")
async def entertainment_root():
    return {
        "ok": True,
        "module": "entertainment",
        "status": "✅ LIVE",
        "categories": ["gaming", "lifestyle", "music", "ramayan", "video"],
        "message": "Entertainment module ready — Haso, gao, khelo, dekho!"
    }

@router.get("/gaming")
async def gaming():
    return get_gaming_content()

@router.get("/lifestyle")
async def lifestyle():
    return get_lifestyle_content()

@router.get("/music")
async def music():
    return get_music_content()

@router.get("/ramayan")
async def ramayan():
    return get_ramayan_content()

@router.get("/video")
async def video():
    return get_video_content()

@router.get("/joke")
async def joke():
    return {
        "ok": True,
        "joke": "Santa: Doctor sahab, main bhool jata hoon!\nDoctor: Kab se?\nSanta: Kaun se?",
        "message": "Santa-Banta special!"
    }

@router.get("/shayari")
async def shayari():
    return {
        "ok": True,
        "shayari": "दुनिया में सबसे बड़ा योद्धा वो है,\nजो अपने गुस्से पर काबू पा ले।",
        "message": "Singh Ji ki shayari!"
    }
