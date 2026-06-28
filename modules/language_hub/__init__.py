# modules/language_hub/__init__.py — Singh Ji AI Ultra v5.0
# Language Hub — 26 Languages Support

from fastapi import APIRouter

router = APIRouter()

LANGUAGES = {
    "hi": {"name": "Hindi", "native": "हिन्दी", "status": "✅"},
    "en": {"name": "English", "native": "English", "status": "✅"},
    "bn": {"name": "Bengali", "native": "বাংলা", "status": "⏳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "status": "⏳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "status": "⏳"},
    "mr": {"name": "Marathi", "native": "मराठी", "status": "⏳"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "status": "⏳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "status": "⏳"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "status": "⏳"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "status": "⏳"},
    "ur": {"name": "Urdu", "native": "اردو", "status": "⏳"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "status": "⏳"},
    "as": {"name": "Assamese", "native": "অসমীয়া", "status": "⏳"},
    "ne": {"name": "Nepali", "native": "नेपाली", "status": "⏳"},
    "si": {"name": "Sinhala", "native": "සිංහල", "status": "⏳"},
    "sd": {"name": "Sindhi", "native": "سنڌي", "status": "⏳"},
    "sa": {"name": "Sanskrit", "native": "संस्कृतम्", "status": "⏳"},
    "kok": {"name": "Konkani", "native": "कोंकणी", "status": "⏳"},
    "mni": {"name": "Manipuri", "native": "মৈতৈলোন্", "status": "⏳"},
    "doi": {"name": "Dogri", "native": "डोगरी", "status": "⏳"},
    "sat": {"name": "Santali", "native": "ᱥᱟᱱᱛᱟᱲᱤ", "status": "⏳"},
    "brx": {"name": "Bodo", "native": "बड़ो", "status": "⏳"},
    "mai": {"name": "Maithili", "native": "मैथिली", "status": "⏳"},
    "ks": {"name": "Kashmiri", "native": "कॉशुर", "status": "⏳"},
    "gom": {"name": "Goan Konkani", "native": "गोंयची कोंकणी", "status": "⏳"},
    "bho": {"name": "Bhojpuri", "native": "भोजपुरी", "status": "⏳"}
}

@router.get("/")
def language_hub_root():
    return {
        "module": "language_hub",
        "status": "✅ Live",
        "total_languages": len(LANGUAGES),
        "active": 2,
        "pending": 24
    }

@router.get("/list")
def list_languages():
    return {"success": True, "languages": LANGUAGES}

@router.get("/status")
def language_status(code: str):
    lang = LANGUAGES.get(code.lower())
    if lang:
        return {"success": True, "language": lang}
    return {"success": False, "error": "Language not found"}
