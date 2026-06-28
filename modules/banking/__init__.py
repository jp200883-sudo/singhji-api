# modules/banking/__init__.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "module": "banking",
        "status": "live",
        "message": "Singh Ji AI Ultra v5.0 🚀"
    }

# ✅ banking_handler से router import करो
try:
    from .banking_handler import router as banking_router
    router.include_router(banking_router, prefix="/details")
except ImportError:
    pass
