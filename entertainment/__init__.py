# modules/entertainment/__init__.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "module": "entertainment",
        "status": "live",
        "message": "Singh Ji AI Ultra v5.0 🚀"
    }

# ✅ gaming_handler से router import करो
try:
    from .gaming_handler import router as gaming_router
    router.include_router(gaming_router, prefix="/gaming")
except ImportError:
    pass
