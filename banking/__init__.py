# Banking module
from .handler import *

from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def banking_root():
    return {
        "ok": True,
        "module": "banking",
        "status": "✅ LIVE",
        "message": "Banking module ready!"
    }
