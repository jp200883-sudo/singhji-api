# modules/railway/__init__.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "module": "railway",
        "status": "live",
        "message": "Singh Ji AI Ultra v5.0 🚀"
    }

# ✅ railway_handler से router import करो
try:
    from .railway_handler import router as railway_router
    router.include_router(railway_router, prefix="/status")
except ImportError:
    pass
