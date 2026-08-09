# utils/helpers.py
import os
import base64
from core.config import STATE_MAP, AVAILABLE_KEYS

MAX_B64_BYTES = 10 * 1024 * 1024

def _normalize_state(state: str) -> str:
    key = state.strip().lower()
    return STATE_MAP.get(key, state.strip().title())

def _calculate_tax(income: float, regime: str = "new", deductions: float = 0):
    if regime == "new":
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = 15000 + (income - 600000) * 0.10
        elif income <= 1200000:
            tax = 45000 + (income - 900000) * 0.15
        elif income <= 1500000:
            tax = 90000 + (income - 1200000) * 0.20
        else:
            tax = 150000 + (income - 1500000) * 0.30
    else:
        taxable = max(0, income - 50000 - deductions)
        if taxable <= 250000:
            tax = 0
        elif taxable <= 500000:
            tax = (taxable - 250000) * 0.05
        elif taxable <= 1000000:
            tax = 12500 + (taxable - 500000) * 0.20
        else:
            tax = 112500 + (taxable - 1000000) * 0.30
    cess = tax * 0.04
    total_tax = tax + cess
    return {
        "income": income, "regime": regime,
        "tax": round(tax, 2), "cess": round(cess, 2),
        "total": round(total_tax, 2),
        "take_home": round(income - total_tax, 2)
    }

def _b64_too_big(b64_str: str) -> bool:
    return (len(b64_str) * 3 / 4) > MAX_B64_BYTES

def _check_admin_auth(request):
    from core.config import ADMIN_API_KEY
    if not ADMIN_API_KEY:
        return True
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return token == ADMIN_API_KEY
    provided = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    return provided == ADMIN_API_KEY

# ---- MODULES CONFIG ----
MODULES = {
    "memory": {"needs_key": None, "active": True},
    "weather": {"needs_key": "OPENWEATHER", "active": AVAILABLE_KEYS["OPENWEATHER"]},
    "news": {"needs_key": "CURRENTS", "active": AVAILABLE_KEYS["CURRENTS"]},
    "mandi": {"needs_key": "MANDI", "active": AVAILABLE_KEYS["MANDI"]},
    "plant_id": {"needs_key": "PLANT_ID", "active": AVAILABLE_KEYS["PLANT_ID"]},
    "payment": {"needs_key": "RAZORPAY", "active": AVAILABLE_KEYS["RAZORPAY"]},
    "admin": {"needs_key": None, "active": True},
    "facebook": {"needs_key": "FACEBOOK", "active": AVAILABLE_KEYS["FACEBOOK"]},
    "instagram": {"needs_key": "INSTAGRAM", "active": AVAILABLE_KEYS["INSTAGRAM"]},
    "youtube": {"needs_key": "YOUTUBE", "active": AVAILABLE_KEYS["YOUTUBE"]},
    "gmail": {"needs_key": "GMAIL", "active": AVAILABLE_KEYS["GMAIL"]},
    "swarm": {"needs_key": None, "active": True},
    "telegram_bot": {"needs_key": "TELEGRAM", "active": AVAILABLE_KEYS["TELEGRAM"]},
    "ai_chat": {"needs_key": "MULTI_AI", "active": AVAILABLE_KEYS["GROQ"] or AVAILABLE_KEYS["GEMINI"] or AVAILABLE_KEYS["CEREBRAS"]},
    "bhashini": {"needs_key": "BHASHINI", "active": AVAILABLE_KEYS["BHASHINI"]},
    "supabase_memory": {"needs_key": "SUPABASE", "active": AVAILABLE_KEYS["SUPABASE"]},
    "whatsapp": {"needs_key": None, "active": True},
    "telegram": {"needs_key": "TELEGRAM", "active": AVAILABLE_KEYS["TELEGRAM"]},
}

# ---- MAIN KEYBOARD ----
# NOTE: No emojis — clean text only for human-like feel
MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "Weather", "callback_data": "weather"}, {"text": "News", "callback_data": "news"}],
        [{"text": "Mandi Bhav", "callback_data": "mandi"}, {"text": "Gold Rate", "callback_data": "gold"}],
        [{"text": "Fuel Price", "callback_data": "fuel"}, {"text": "Tax Calc", "callback_data": "tax"}],
        [{"text": "Horoscope", "callback_data": "horoscope"}, {"text": "Rozgar/Jobs", "callback_data": "rozgar"}],
        [{"text": "Currency", "callback_data": "currency"}, {"text": "Search", "callback_data": "search"}],
        [{"text": "Translate", "callback_data": "translate"}, {"text": "Yojana", "callback_data": "yojana"}],
        [{"text": "SinghJi TV", "callback_data": "tv"}, {"text": "Emergency", "callback_data": "emergency"}],
        [{"text": "UPI Info", "callback_data": "upi"}, {"text": "Govt Services", "callback_data": "govt"}],
        [{"text": "KYC Portal", "callback_data": "kyc"}, {"text": "Agent Program", "callback_data": "agent"}],
        [{"text": "Gram Panchayat", "callback_data": "grampanchayat"}, {"text": "Withdraw", "callback_data": "withdraw"}],
        [{"text": "Guard Agent", "callback_data": "guard"}, {"text": "Social Agent", "callback_data": "social"}],
        [{"text": "Voice AI", "callback_data": "voice"}, {"text": "Plant Doctor", "callback_data": "plant"}],
        [{"text": "AI Chat", "callback_data": "ai_chat"}, {"text": "System Status", "callback_data": "status"}],
        [{"text": "Help / Commands", "callback_data": "help"}],
    ]
}
