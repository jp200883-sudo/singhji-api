import os
from dotenv import load_dotenv
from fastapi import APIRouter
from core.config import settings

load_dotenv()
router = APIRouter()
def govt_home():
    return {
        "module": "govt",
        "status": "ok",
        "schemes_count": len(settings.GOVT_SCHEMES)
    }
@router.get("/schemes")
def govt_schemes():
        "schemes": settings.GOVT_SCHEMES
