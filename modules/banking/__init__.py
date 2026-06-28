# modules/banking/__init__.py

from fastapi import APIRouter
from .banking_handler import router as banking_router  # अगर banking_handler.py है

router = APIRouter()

@router.get("/")
def home():
    return {
        "module": "banking",
        "status": "live",
        "message": "Singh Ji AI Ultra v5.0 🚀"
    }

# अगर banking_handler.py है तो include करो
router.include_router(banking_router, prefix="/banking")
