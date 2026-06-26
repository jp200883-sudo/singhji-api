from fastapi import APIRouter
from core.config import settings

router = APIRouter()

@router.get("/")
def govt_home():
    return {
        "module": "govt",
        "status": "ok",
        "schemes_count": len(settings.GOVT_SCHEMES)
    }

@router.get("/schemes")
def govt_schemes():
    return {
        "schemes": settings.GOVT_SCHEMES
    }
