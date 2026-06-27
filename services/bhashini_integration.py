"""
🌐 Singh Ji AI Ultra — Bhashini 26 Language Integration
Bhashini: India's AI-driven language translation platform
API: https://bhashini.gov.in/
"""

import os
import requests
import json
from typing import Optional, Dict, List

# ─── CONFIG ─────────────────────────────────────────
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "YOUR_BHASHINI_KEY_HERE")
BHASHINI_BASE_URL = "https://api.bhashini.gov.in/v2"

# ─── 26 LANGUAGES SUPPORTED ─────────────────────────
SUPPORTED_LANGUAGES = {
    "hi": {"name": "Hindi", "script": "Devanagari", "flag": "🇮🇳"},
    "en": {"name": "English", "script": "Latin", "flag": "🇬🇧"},
    "pa": {"name": "Punjabi", "script": "Gurmukhi", "flag": "🦁"},
    "bn": {"name": "Bengali", "script": "Bengali", "flag": "🇧🇩"},
    "te": {"name": "Telugu", "script": "Telugu", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "script": "Tamil", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "script": "Devanagari", "flag": "🇮🇳"},
    "gu": {"name": "Gujarati", "script": "Gujarati", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "script": "Kannada", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam", "script": "Malayalam", "flag": "🇮🇳"},
    "ur": {"name": "Urdu", "script": "Perso-Arabic", "flag": "🇵🇰"},
    "or": {"name": "Odia", "script": "Odia", "flag": "🇮🇳"},
    "as": {"name": "Assamese", "script": "Bengali", "flag": "🇮🇳"},
    "ne": {"name": "Nepali", "script": "Devanagari", "flag": "🇳🇵"},
    "si": {"name": "Sinhala", "script": "Sinhala", "flag": "🇱🇰"},
    "my": {"name": "Burmese", "script": "Burmese", "flag": "🇲🇲"},
    "th": {"name": "Thai", "script": "Thai", "flag": "🇹🇭"},
    "vi": {"name": "Vietnamese", "script": "Latin", "flag": "🇻🇳"},
    "id": {"name": "Indonesian", "script": "Latin", "flag": "🇮🇩"},
    "ms": {"name": "Malay", "script": "Latin", "flag": "🇲🇾"},
    "zh": {"name": "Chinese", "script": "Han", "flag": "🇨🇳"},
    "ja": {"name": "Japanese", "script": "Japanese", "flag": "🇯🇵"},
    "ko": {"name": "Korean", "script": "Korean", "flag": "🇰🇷"},
    "ar": {"name": "Arabic", "script": "Arabic", "flag": "🇸🇦"},
    "fr": {"name": "French", "script": "Latin", "flag": "🇫🇷"},
    "es": {"name": "Spanish", "script": "Latin", "flag": "🇪🇸"},
}

class BhashiniTranslator:
    """Bhashini API wrapper for Singh Ji AI Ultra"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or BHASHINI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def translate(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """
        Translate text using Bhashini API

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'hi')
            target_lang: Target language code (e.g., 'hi', 'pa')

        Returns:
            Dict with translated text and metadata
        """
        if source_lang == target_lang:
            return {"success": True, "translation": text, "source": source_lang, "target": target_lang}

        # Bhashini API payload
        payload = {
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
            "input": text,
            "task": "translation"
        }

        try:
            response = requests.post(
                f"{BHASHINI_BASE_URL}/translate",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "translation": data.get("output", text),
                    "source": source_lang,
                    "target": target_lang,
                    "confidence": data.get("confidence", 0.95)
                }
            else:
                # Fallback: return original with note
                return {
                    "success": False,
                    "translation": text,
                    "source": source_lang,
                    "target": target_lang,
                    "error": f"API Error: {response.status_code}",
                    "note": "Bhashini key pending — using fallback"
                }

        except Exception as e:
            return {
                "success": False,
                "translation": text,
                "source": source_lang,
                "target": target_lang,
                "error": str(e),
                "note": "Bhashini key pending — using fallback"
            }

    def translate_bulk(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]:
        """Translate multiple texts"""
        return [self.translate(t, source_lang, target_lang) for t in texts]

    def detect_language(self, text: str) -> Dict:
        """Detect language of input text"""
        payload = {"input": text, "task": "langdetect"}
        try:
            response = requests.post(
                f"{BHASHINI_BASE_URL}/langdetect",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "language": data.get("language", "en"), "confidence": data.get("confidence", 0.9)}
            return {"success": False, "language": "en", "note": "Fallback to English"}
        except:
            return {"success": False, "language": "en", "note": "Fallback to English"}

    def get_supported_languages(self) -> List[Dict]:
        """Get list of all supported languages"""
        return [
            {"code": code, **info} 
            for code, info in SUPPORTED_LANGUAGES.items()
        ]


# ─── FASTAPI ENDPOINTS ──────────────────────────────
"""
Add these endpoints to your singhji-api main.py:

from bhashini_integration import BhashiniTranslator, SUPPORTED_LANGUAGES

translator = BhashiniTranslator()

@app.post("/api/translate")
async def api_translate(request: Request):
    data = await request.json()
    result = translator.translate(
        text=data.get("text", ""),
        source_lang=data.get("source", "en"),
        target_lang=data.get("target", "hi")
    )
    return result

@app.post("/api/detect-language")
async def api_detect_language(request: Request):
    data = await request.json()
    result = translator.detect_language(data.get("text", ""))
    return result

@app.get("/api/languages")
async def api_languages():
    return {"languages": translator.get_supported_languages(), "count": len(SUPPORTED_LANGUAGES)}
"""

# ─── USAGE EXAMPLE ──────────────────────────────────
if __name__ == "__main__":
    # Demo usage
    t = BhashiniTranslator()

    print("🌐 Singh Ji Bhashini Translator — 26 Languages")
    print("=" * 50)
    print(f"Total languages: {len(SUPPORTED_LANGUAGES)}")
    print()

    # Show all languages
    for code, info in SUPPORTED_LANGUAGES.items():
        print(f"  {info['flag']} {code.upper()}: {info['name']} ({info['script']})")

    print()
    print("📝 Translation Demo:")
    print("  EN → HI: 'Hello Singh Ji' → [Bhashini API pending]")
    print("  EN → PA: 'Hello Singh Ji' → [Bhashini API pending]")
    print()
    print("🍌 केला मोड ON — केला नहीं होता भाई अकेला!")
