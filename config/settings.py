"""
🦁 SINGH JI AI ULTRA — Configuration
All settings in one place
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App
    APP_NAME = "🦁 Singh Ji AI Ultra"
    VERSION = "5.0.0"
    DEBUG = os.getenv("FLASK_ENV") == "development"
    PORT = int(os.getenv("PORT", 5000))

    # CORS
    CORS_ORIGINS = ["*"]

    # APIs
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
    NEWSAPI_URL = "https://newsapi.org/v2"

    # Email
    GMAIL_USER = os.getenv("GMAIL_USER", "")
    GMAIL_PASS = os.getenv("GMAIL_PASS", "")

    # UPI
    UPI_ID = os.getenv("UPI_ID", "jp200883@sbi")

    # Emergency
    EMERGENCY_CONTACTS = [
        os.getenv("EMERGENCY_CONTACT_1", ""),
        os.getenv("EMERGENCY_CONTACT_2", ""),
    ]
    POLICE = "100"
    AMBULANCE = "108"
    FIRE = "101"
    WOMEN_HELPLINE = "1091"
    CHILD_HELPLINE = "1098"

    # Social Media
    SOCIAL_PLATFORMS = ["instagram", "facebook", "twitter", "whatsapp"]

    # Voice
    F5_TTS_ENABLED = True
    JP_SINGH_SAMPLE = os.getenv("JP_SINGH_SAMPLE", "")

    # Schedule
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

    # Government Schemes
    GOVT_SCHEMES = [
        "pm_kisan", "ayushman_bharat", "pm_awas", "jan_dhan",
        "sukanya_samriddhi", "atal_pension", "mudra_loan",
        "standup_india", "ujjwala", "saubhagya", "jal_jeevan",
        "pm_shri_schools", "skill_india", "digital_india"
    ]
