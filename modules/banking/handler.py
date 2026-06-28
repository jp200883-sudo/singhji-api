# modules/banking/banking_handler.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/details")
def banking_details():
    return {
        "status": "live",
        "module": "banking",
        "features": ["balance", "mini_statement", "fund_transfer", "upi"]
    }

# ✅ अगर main.py get_banking_data ढूंढ रहा हो तो ये भी add करो
def get_banking_data():
    return {
        "status": "live",
        "banks": ["SBI", "HDFC", "ICICI", "Axis"],
        "services": ["balance_check", "mini_statement", "fund_transfer"]
    }
