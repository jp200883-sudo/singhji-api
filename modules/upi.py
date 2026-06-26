from fastapi import APIRouter
from core.config import settings

router = APIRouter()
@router.get("/")
def upi_home():
    return {
        "module": "upi",
        "status": "ok",
        "upi_id": settings.UPI_ID
    }
@router.get("/pay")
def upi_pay(amount: int = 0, note: str = ""):
        "upi_id": settings.UPI_ID,
        "amount": amount,
        "note": note,
        "status": "mock_payment",
        "message": f"₹{amount} payment to {settings.UPI_ID}"
