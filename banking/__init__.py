from fastapi import APIRouter
from .handler import get_balance, get_upi_info, get_loan_info

router = APIRouter()

@router.get("/")
async def banking_root():
    return {
        "ok": True,
        "module": "banking",
        "status": "✅ LIVE",
        "services": ["Balance Check", "Mini Statement", "UPI", "Loan Info"],
        "message": "Banking module ready — Paisa ka hisaab rakho!"
    }

@router.get("/balance")
async def balance(account: str = "default"):
    return get_balance(account)

@router.get("/upi")
async def upi():
    return get_upi_info()

@router.get("/loan")
async def loan():
    return get_loan_info()
