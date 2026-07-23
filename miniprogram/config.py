"""
Mini-Program Config — सब settings यहाँ
"""
import os
from datetime import timedelta


class MiniProgramConfig:
    """Mini-Program के लिए सब config"""

    # 🔐 JWT Settings — hardcoded fallback nahi, sirf env variable se
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRE = timedelta(days=30)

    # 🔒 Admin Access — khali string default hatayi, warna admin_token=""
    # bhi match ho jata jab env variable set na ho
    ADMIN_SECRET = os.getenv("MINIPROGRAM_ADMIN_SECRET")

    # 👤 Developer Settings
    DEVELOPER_REGISTRATION_OPEN = True
    MAX_APPS_PER_DEVELOPER = 10
    APP_NAME_MAX_LENGTH = 50

    # 💰 Razorpay (already ready hai)
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

    # 📦 Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_BUCKET = "miniprogram-assets"

    # 🧪 Sandbox
    SANDBOX_TIMEOUT = 30  # seconds
    SANDBOX_MEMORY_LIMIT = 128  # MB
    SANDBOX_CPU_LIMIT = 1  # CPU cores
    SANDBOX_ALLOWED_MODULES = [
        "json", "math", "random", "datetime",
        "re", "string", "collections", "itertools",
        "statistics", "fractions", "decimal"
    ]

    # 🏗️ Portal
    PORTAL_API_PREFIX = "/api/v1/miniprogram"
    PORTAL_CORS_ORIGINS = ["*"]  # Production mein restrict karna

    # 📝 Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def is_payment_ready(cls):
        """Check karo Razorpay ready hai ya nahi"""
        return bool(cls.RAZORPAY_KEY_ID and cls.RAZORPAY_KEY_SECRET)

    @classmethod
    def is_storage_ready(cls):
        """Check karo Supabase ready hai ya nahi"""
        return bool(cls.SUPABASE_URL and cls.SUPABASE_KEY)

    @classmethod
    def is_admin_ready(cls):
        """Check karo ADMIN_SECRET set hai ya nahi"""
        return bool(cls.ADMIN_SECRET)
