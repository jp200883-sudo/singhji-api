"""
🦁 SINGH JI AI ULTRA v5.0 — Configuration
All settings in one place — FastAPI Version
"""

import os
from dotenv import load_dotenv
from fastapi import APIRouter
from core.config import settings

load_dotenv()
router = APIRouter()
load_dotenv() 
router = APIRouter()
# ... existing code ...
load_dotenv()

class Config:
    # App Info
    APP_NAME = "🦁 Singh Ji AI Ultra"
    VERSION = "5.0.0"
    TAGLINE = "भारत का ऑल-इन-वन सुपर ऐप — ज़ीरो फोन लोड, फुल ऑटोमेशन"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 10000))

    # CORS
    CORS_ORIGINS = ["*"]

    # ========== AI APIs ==========
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

    # ========== Weather ==========
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

    # ========== News ==========
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
    NEWSAPI_URL = "https://newsapi.org/v2"

    # ========== Search ==========
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    TAVILY_URL = os.getenv("TAVILY_URL", "https://api.tavily.com")

    # ========== Agriculture ==========
    MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")

    # ========== Plant ID ==========
    PLANT_ID_API = os.getenv("PLANT_ID_API", "")
    PLANT_ID_URL = os.getenv("PLANT_ID_URL", "")

    # ========== Telegram ==========
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://singhji-api.onrender.com/api/telegram/webhook")

    # ========== Supabase ==========
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    # ========== Payments ==========
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    UPI_ID = os.getenv("UPI_ID", "jp200883@sbi")

    # ========== Email ==========
    GMAIL_USER = os.getenv("GMAIL_USER", "")
    GMAIL_PASS = os.getenv("GMAIL_PASS", "")

    # ========== Emergency ==========
    EMERGENCY_CONTACTS = [
        os.getenv("EMERGENCY_CONTACT_1", ""),
        os.getenv("EMERGENCY_CONTACT_2", ""),
    ]
    POLICE = "100"
    AMBULANCE = "108"
    FIRE = "101"
    WOMEN_HELPLINE = "1091"
    CHILD_HELPLINE = "1098"

    # ========== Social Media ==========
    SOCIAL_PLATFORMS = ["instagram", "facebook", "twitter", "whatsapp", "telegram"]

    # ========== Voice ==========
    F5_TTS_ENABLED = True
    JP_SINGH_SAMPLE = os.getenv("JP_SINGH_SAMPLE", "")

    # ========== Daily Schedule ==========
    DAILY_SCHEDULE = {
        "06:00": "morning_routine",
        "08:00": "social_post_morning",
        "09:00": "music_morning",
        "10:00": "education_tip",
        "12:00": "news_digest",
        "14:00": "banking_tip",
        "15:00": "coming_soon_teaser",
        "16:00": "email_check",
        "18:00": "evening_summary",
        "20:00": "music_evening",
        "21:00": "jp_singh_thought",
        "22:00": "good_night"
    }

    # ========== Government Schemes ==========
    GOVT_SCHEMES = [
        {"id": "pm_kisan", "name": "PM-KISAN", "amount": "₹6,000/साल", "desc": "किसानों को हर साल 6000 रुपये"},
        {"id": "ayushman_bharat", "name": "Ayushman Bharat", "amount": "₹5 लाख", "desc": "5 लाख तक का मुफ्त इलाज"},
        {"id": "pm_awas", "name": "PM Awas Yojana", "amount": "₹2.5 लाख", "desc": "घर बनाने के लिए पैसे"},
        {"id": "jan_dhan", "name": "Jan Dhan Yojana", "amount": "₹0", "desc": "मुफ्त बैंक खाता"},
        {"id": "sukanya_samriddhi", "name": "Sukanya Samriddhi", "amount": "8.2% ब्याज", "desc": "बेटियों के लिए बचत"},
        {"id": "atal_pension", "name": "Atal Pension Yojana", "amount": "₹1,000-5,000/महीना", "desc": "पेंशन प्लान"},
        {"id": "mudra_loan", "name": "MUDRA Loan", "amount": "₹50,000-10 लाख", "desc": "बिजनेस लोन"},
        {"id": "standup_india", "name": "Stand Up India", "amount": "₹10 लाख-1 करोड़", "desc": "महिला/SC/ST लोन"},
        {"id": "ujjwala", "name": "Ujjwala Yojana", "amount": "₹0", "desc": "मुफ्त गैस कनेक्शन"},
        {"id": "saubhagya", "name": "Saubhagya", "amount": "₹0", "desc": "मुफ्त बिजली कनेक्शन"},
        {"id": "jal_jeevan", "name": "Jal Jeevan Mission", "amount": "₹0", "desc": "हर घर में नल का पानी"},
        {"id": "pm_shri_schools", "name": "PM SHRI Schools", "amount": "₹0", "desc": "अच्छी स्कूल सुविधा"},
        {"id": "skill_india", "name": "Skill India", "amount": "₹0", "desc": "फ्री ट्रेनिंग"},
        {"id": "digital_india", "name": "Digital India", "amount": "₹0", "desc": "डिजिटल सेवाएँ"},
    ]

    # ========== Languages ==========
    INDIAN_LANGUAGES = 22
    GLOBAL_LANGUAGES = 36
    TOTAL_LANGUAGES = 58

    # ========== Admin ==========
    ADMIN_KEY = os.getenv("ADMIN_KEY", "singhji-admin-2026")

    # ========== Bhashini ==========
    BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_URL = "https://bhashini-api.iitm.ac.in"

    # ========== RapidAPI ==========
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# Global instance
settings = Config()
