# modules/currency/handler.py — Singh Ji AI Ultra v5.0
# Currency Exchange — INR to USD, EUR, GBP, etc.

from fastapi import APIRouter
import os
import requests

router = APIRouter()
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "")

@router.get("/")
def currency_root():
    return {"module": "currency", "status": "✅ Live", "base": "INR"}

@router.get("/rates")
def get_rates(base: str = "INR"):
    """Live currency rates"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url, timeout=10)
        data = response.json()

        return {
            "success": True,
            "base": data.get("base", base),
            "date": data.get("date"),
            "rates": {
                "USD": data["rates"].get("USD", 0),
                "EUR": data["rates"].get("EUR", 0),
                "GBP": data["rates"].get("GBP", 0),
                "JPY": data["rates"].get("JPY", 0),
                "AUD": data["rates"].get("AUD", 0),
                "CAD": data["rates"].get("CAD", 0),
                "SGD": data["rates"].get("SGD", 0),
                "AED": data["rates"].get("AED", 0),
                "SAR": data["rates"].get("SAR", 0),
                "CNY": data["rates"].get("CNY", 0)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/convert")
def convert(amount: float, from_currency: str = "INR", to_currency: str = "USD"):
    """Convert currency"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()
        rate = data["rates"].get(to_currency, 0)

        return {
            "success": True,
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "rate": rate,
            "converted": round(amount * rate, 2)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
