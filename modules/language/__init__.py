from fastapi import APIRouter
import requests

router = APIRouter()

LANGUAGES = {
    "hi": {"name": "Hindi", "hello": "नमस्ते", "native": "हिन्दी", "region": "India"},
    "bn": {"name": "Bengali", "hello": "নমস্কার", "native": "বাংলা", "region": "India"},
    "te": {"name": "Telugu", "hello": "నమస్కారం", "native": "తెలుగు", "region": "India"},
    "mr": {"name": "Marathi", "hello": "नमस्कार", "native": "मराठी", "region": "India"},
    "ta": {"name": "Tamil", "hello": "வணக்கம்", "native": "தமிழ்", "region": "India"},
    "ur": {"name": "Urdu", "hello": "السلام علیکم", "native": "اردو", "region": "India"},
    "gu": {"name": "Gujarati", "hello": "નમસ્તે", "native": "ગુજરાતી", "region": "India"},
    "kn": {"name": "Kannada", "hello": "ನಮಸ್ಕಾರ", "native": "ಕನ್ನಡ", "region": "India"},
    "ml": {"name": "Malayalam", "hello": "നമസ്കാരം", "native": "മലയാളം", "region": "India"},
    "pa": {"name": "Punjabi", "hello": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "native": "ਪੰਜਾਬੀ", "region": "India"},
    "or": {"name": "Odia", "hello": "ନମସ୍କାର", "native": "ଓଡ଼ିଆ", "region": "India"},
    "as": {"name": "Assamese", "hello": "নমস্কাৰ", "native": "অসমীয়া", "region": "India"},
    "ne": {"name": "Nepali", "hello": "नमस्ते", "native": "नेपाली", "region": "India"},
    "si": {"name": "Sinhala", "hello": "ආයුබෝවන්", "native": "සිංහල", "region": "India"},
    "kok": {"name": "Konkani", "hello": "नमस्कार", "native": "कोंकणी", "region": "India"},
    "mni": {"name": "Manipuri", "hello": "ꯍꯦꯜꯂꯣ", "native": "মৈতৈলোন্", "region": "India"},
    "doi": {"name": "Dogri", "hello": "नमस्कार", "native": "डोगरी", "region": "India"},
    "sat": {"name": "Santali", "hello": "ᱡᱚᱦᱟᱨ", "native": "ᱥᱟᱱᱛᱟᱲᱤ", "region": "India"},
    "ks": {"name": "Kashmiri", "hello": "السلام علیکم", "native": "कॉशुर", "region": "India"},
    "sd": {"name": "Sindhi", "hello": "सलाम", "native": "سنڌي", "region": "India"},
    "brx": {"name": "Bodo", "hello": "नमस्कार", "native": "बड़ो", "region": "India"},
    "mai": {"name": "Maithili", "hello": "प्रणाम", "native": "मैथिली", "region": "India"},
    "en": {"name": "English", "hello": "Hello", "native": "English", "region": "Global"},
    "es": {"name": "Spanish", "hello": "Hola", "native": "Español", "region": "Global"},
    "fr": {"name": "French", "hello": "Bonjour", "native": "Français", "region": "Global"},
    "de": {"name": "German", "hello": "Hallo", "native": "Deutsch", "region": "Global"},
    "zh": {"name": "Chinese", "hello": "你好", "native": "中文", "region": "Global"},
    "ja": {"name": "Japanese", "hello": "こんにちは", "native": "日本語", "region": "Global"},
    "ko": {"name": "Korean", "hello": "안녕하세요", "native": "한국어", "region": "Global"},
    "ru": {"name": "Russian", "hello": "Привет", "native": "Русский", "region": "Global"},
    "ar": {"name": "Arabic", "hello": "مرحبا", "native": "العربية", "region": "Global"},
    "pt": {"name": "Portuguese", "hello": "Olá", "native": "Português", "region": "Global"},
    "it": {"name": "Italian", "hello": "Ciao", "native": "Italiano", "region": "Global"},
    "tr": {"name": "Turkish", "hello": "Merhaba", "native": "Türkçe", "region": "Global"},
    "vi": {"name": "Vietnamese", "hello": "Xin chào", "native": "Tiếng Việt", "region": "Global"},
    "th": {"name": "Thai", "hello": "สวัสดี", "native": "ไทย", "region": "Global"},
    "id": {"name": "Indonesian", "hello": "Halo", "native": "Bahasa Indonesia", "region": "Global"},
    "ms": {"name": "Malay", "hello": "Hai", "native": "Bahasa Melayu", "region": "Global"},
    "pl": {"name": "Polish", "hello": "Cześć", "native": "Polski", "region": "Global"},
    "nl": {"name": "Dutch", "hello": "Hallo", "native": "Nederlands", "region": "Global"},
    "sv": {"name": "Swedish", "hello": "Hej", "native": "Svenska", "region": "Global"},
    "el": {"name": "Greek", "hello": "Γειά σου", "native": "Ελληνικά", "region": "Global"},
    "cs": {"name": "Czech", "hello": "Ahoj", "native": "Čeština", "region": "Global"},
    "ro": {"name": "Romanian", "hello": "Salut", "native": "Română", "region": "Global"},
    "hu": {"name": "Hungarian", "hello": "Szia", "native": "Magyar", "region": "Global"},
    "he": {"name": "Hebrew", "hello": "שלום", "native": "עברית", "region": "Global"},
    "uk": {"name": "Ukrainian", "hello": "Привіт", "native": "Українська", "region": "Global"},
    "fa": {"name": "Persian", "hello": "سلام", "native": "فارسی", "region": "Global"},
    "my": {"name": "Burmese", "hello": "မင်္ဂလာပါ", "native": "မြန်မာဘာသာ", "region": "Global"},
    "km": {"name": "Khmer", "hello": "សួស្តី", "native": "ភាសាខ្មែរ", "region": "Global"},
    "la": {"name": "Latin", "hello": "Salve", "native": "Latina", "region": "Global"},
    "no": {"name": "Norwegian", "hello": "Hei", "native": "Norsk", "region": "Global"},
    "fi": {"name": "Finnish", "hello": "Hei", "native": "Suomi", "region": "Global"},
    "da": {"name": "Danish", "hello": "Hej", "native": "Dansk", "region": "Global"},
    "sr": {"name": "Serbian", "hello": "Здраво", "native": "Српски", "region": "Global"},
    "hr": {"name": "Croatian", "hello": "Bok", "native": "Hrvatski", "region": "Global"},
    "bg": {"name": "Bulgarian", "hello": "Здравейте", "native": "Български", "region": "Global"},
    "lt": {"name": "Lithuanian", "hello": "Labas", "native": "Lietuvių", "region": "Global"},
}

@router.get("/")
async def language_root():
    return {
        "ok": True,
        "module": "language",
        "status": "✅ LIVE",
        "total_languages": len(LANGUAGES),
        "indian": 22,
        "global": 36,
        "message": "Language module ready — 58 languages supported!"
    }

@router.get("/health")
def language_health():
    return {"module": "language", "status": "✅ OK", "total_languages": len(LANGUAGES), "indian": 22, "global": 36}

@router.get("/list")
def list_languages():
    return {"ok": True, "count": len(LANGUAGES), "indian_count": 22, "global_count": 36, "languages": LANGUAGES}

@router.get("/hello/{code}")
def say_hello(code: str):
    lang = LANGUAGES.get(code.lower())
    if not lang:
        return {"ok": False, "error": f"Language code '{code}' not found", "available": list(LANGUAGES.keys())}
    return {"ok": True, "code": code, "language": lang["name"], "native": lang["native"], "hello": lang["hello"], "region": lang["region"]}

@router.post("/translate")
async def translate_text(text: str, target: str = "hi", source: str = "auto"):
    try:
        # Google Translate FREE API (temp until Bhashini)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl={target}&dt=t&q={text}"
        response = requests.get(url, timeout=10)
        data = response.json()
        translated = data[0][0][0] if data and data[0] else text
        
        return {
            "ok": True,
            "original": text,
            "translated": translated,
            "source_language": source,
            "target_language": target,
            "engine": "Google Translate (TEMP)",
            "mode": "real",
            "message": "Translation ho gaya!"
        }
    except Exception as e:
        # Fallback
        return {
            "ok": True,
            "original": text,
            "translated": text,
            "target_language": target,
            "engine": "fallback",
            "mode": "fallback",
            "error": str(e),
            "message": "Fallback mode — Bhashini integration pending"
        }
