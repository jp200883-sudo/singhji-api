import os

# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "1008554401796459")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
PLANT_ID_API = os.getenv("PLANT_ID_API")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID")
BHASHINI_ULCA_API_KEY = os.getenv("BHASHINI_ULCA_API_KEY")
BHASHINI_INFERENCE_API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY")
KLING_API_KEY = os.getenv("KLING_API_KEY")
HAILUO_API_KEY = os.getenv("HAILUO_API_KEY")
LUMA_API_KEY = os.getenv("LUMA_API_KEY")
PIKA_API_KEY = os.getenv("PIKA_API_KEY")
VEO_API_KEY = os.getenv("VEO_API_KEY")
APP_URL = os.getenv("APP_URL", "").rstrip('/')

# ==========================================
# CONSTANTS
# ==========================================
MAX_B64_BYTES = 10 * 1024 * 1024
MAX_MEMORY_SIZE = 5000
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"

# Rate limits
RATE_LIMIT_GLOBAL = (int(os.getenv("RATE_LIMIT_GLOBAL_CALLS", 30)), int(os.getenv("RATE_LIMIT_GLOBAL_WINDOW", 60)))
RATE_LIMIT_STRICT = (int(os.getenv("RATE_LIMIT_STRICT_CALLS", 5)), int(os.getenv("RATE_LIMIT_STRICT_WINDOW", 60)))
RATE_LIMIT_TELEGRAM_USER = (int(os.getenv("RATE_LIMIT_TELEGRAM_CALLS", 10)), int(os.getenv("RATE_LIMIT_TELEGRAM_WINDOW", 60)))

CACHE_TTL = {
    "weather": int(os.getenv("CACHE_TTL_WEATHER", 1800)),
    "mandi": int(os.getenv("CACHE_TTL_MANDI", 21600)),
    "ai_chat": int(os.getenv("CACHE_TTL_AI", 3600)),
    "news": int(os.getenv("CACHE_TTL_NEWS", 900)),
    "default": int(os.getenv("CACHE_TTL_DEFAULT", 300))
}

# ==========================================
# AVAILABLE KEYS STATUS
# ==========================================
class Config:
    def __init__(self):
        self.ADMIN_API_KEY = ADMIN_API_KEY
        self.CEREBRAS_API_KEY = CEREBRAS_API_KEY
        self.GEMINI_API_KEY = GEMINI_API_KEY
        self.GROQ_API_KEY = GROQ_API_KEY
        self.OPENWEATHER_API_KEY = OPENWEATHER_API_KEY
        self.NEWSDATA_API_KEY = NEWSDATA_API_KEY
        self.MANDI_API_KEY = MANDI_API_KEY
        self.SUPABASE_URL = SUPABASE_URL
        self.SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY
        self.TELEGRAM_TOKEN = TELEGRAM_TOKEN
        self.FACEBOOK_ACCESS_TOKEN = FACEBOOK_ACCESS_TOKEN
        self.FACEBOOK_PAGE_ID = FACEBOOK_PAGE_ID
        self.MANDI_RESOURCE_ID = MANDI_RESOURCE_ID
        self.MANDI_BASE_URL = MANDI_BASE_URL
        self.CACHE_TTL = CACHE_TTL
        self.RATE_LIMIT_GLOBAL = RATE_LIMIT_GLOBAL
        self.RATE_LIMIT_STRICT = RATE_LIMIT_STRICT
        self.AVAILABLE_KEYS = AVAILABLE_KEYS
        self.STATE_MAP = STATE_MAP
        self.APP_URL = APP_URL
        self.DEBUG = True
        self.APP_VERSION = "8.0"

# ✅ यह लाइन सबसे ज़रूरी है – config object बनाओ
config = Config()

# ==========================================
# STATE MAP (for Mandi)
# ==========================================
STATE_MAP = {
    "up": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh", "uttarpradesh": "Uttar Pradesh",
    "mp": "Madhya Pradesh", "madhya pradesh": "Madhya Pradesh", "madhyapradesh": "Madhya Pradesh",
    "bihar": "Bihar", "rajasthan": "Rajasthan", "rajsthan": "Rajasthan",
    "punjab": "Punjab", "haryana": "Haryana",
    "maharashtra": "Maharashtra", "gujarat": "Gujarat",
    "wb": "West Bengal", "west bengal": "West Bengal", "westbengal": "West Bengal",
    "odisha": "Odisha", "orissa": "Odisha",
    "telangana": "Telangana", "andhra": "Andhra Pradesh", "andhra pradesh": "Andhra Pradesh",
    "karnataka": "Karnataka", "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
    "kerala": "Kerala", "jharkhand": "Jharkhand",
    "chhattisgarh": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
    "uttarakhand": "Uttarakhand", "uttranchal": "Uttarakhand",
    "himachal": "Himachal Pradesh", "himachal pradesh": "Himachal Pradesh",
    "assam": "Assam", "tripura": "Tripura", "meghalaya": "Meghalaya",
}
