# core/config/settings.py
"""
Singh Ji AI Ultra v7.0 - Configuration Settings
"""
import os
from typing import Dict, List

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Weather
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# News
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Translation (Bhashini)
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")

# Image Generation
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# Plant ID
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# UPI / Payment
UPI_ID = os.getenv("UPI_ID", "jp200883@sbi")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

# App Config
APP_NAME = "Singh Ji AI Ultra v7.0"
APP_VERSION = "7.0.0"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# CORS
ALLOWED_ORIGINS = [
    "https://singhji-ai.github.io",
    "https://singhji-ai.github.io/singhji-ai",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"
]

# Default AI Model
DEFAULT_MODEL = "llama3-70b-8192"

# Available Models
AVAILABLE_MODELS = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "gemini-1.5-flash",
    "gpt-4o-mini"
]

# Languages Supported
SUPPORTED_LANGUAGES = [
    "en", "hi", "bn", "te", "mr", "ta", "ur", "gu", "kn", "ml",
    "pa", "or", "as", "ne", "si", "sd", "sa", "kok", "mni", "doi",
    "brx", "mai", "bho", "raj", "mag", "awa", "hne", "gbm", "kfr", "kru"
]

def get_settings() -> Dict:
    """
    Get all settings as dictionary
    """
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "debug": DEBUG,
        "default_model": DEFAULT_MODEL,
        "available_models": AVAILABLE_MODELS,
        "supported_languages": SUPPORTED_LANGUAGES,
        "allowed_origins": ALLOWED_ORIGINS,
        "upi_id": UPI_ID,
    }

def get_api_key(key_name: str) -> str:
    """
    Get specific API key
    """
    keys = {
        "groq": GROQ_API_KEY,
        "openai": OPENAI_API_KEY,
        "gemini": GEMINI_API_KEY,
        "anthropic": ANTHROPIC_API_KEY,
        "weather": OPENWEATHER_API_KEY,
        "news": NEWS_API_KEY,
        "bhashini": BHASHINI_API_KEY,
        "stability": STABILITY_API_KEY,
        "replicate": REPLICATE_API_TOKEN,
        "plant_id": PLANT_ID_API_KEY,
        "telegram": TELEGRAM_BOT_TOKEN,
        "supabase": SUPABASE_KEY,
        "razorpay_key": RAZORPAY_KEY_ID,
        "razorpay_secret": RAZORPAY_KEY_SECRET,
    }
    return keys.get(key_name.lower(), "")

def check_api_key(key_name: str) -> bool:
    """
    Check if API key is configured
    """
    return bool(get_api_key(key_name))

# Export all
__all__ = [
    'get_settings',
    'get_api_key',
    'check_api_key',
    'GROQ_API_KEY',
    'OPENAI_API_KEY',
    'GEMINI_API_KEY',
    'ANTHROPIC_API_KEY',
    'OPENWEATHER_API_KEY',
    'NEWS_API_KEY',
    'BHASHINI_API_KEY',
    'BHASHINI_USER_ID',
    'STABILITY_API_KEY',
    'REPLICATE_API_TOKEN',
    'PLANT_ID_API_KEY',
    'TELEGRAM_BOT_TOKEN',
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'UPI_ID',
    'RAZORPAY_KEY_ID',
    'RAZORPAY_KEY_SECRET',
    'APP_NAME',
    'APP_VERSION',
    'DEBUG',
    'ALLOWED_ORIGINS',
    'DEFAULT_MODEL',
    'AVAILABLE_MODELS',
    'SUPPORTED_LANGUAGES',
]
