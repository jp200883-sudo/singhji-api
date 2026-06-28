# modules/language/__init__.py — Singh Ji AI Ultra v5.0
# Language — Translation, Detection

from fastapi import APIRouter
import os
import requests

router = APIRouter()

@router.get("/")
def language_root():
    return {
        "module": "language",
        "status": "✅ Live",
        "supported": ["hi", "en", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa"]
    }

@router.get("/translate")
def translate(text: str, from_lang: str = "auto", to_lang: str = "hi"):
    """Simple translation — Bhashini integration pending"""
    # Placeholder — Replace with Bhashini API when approved
    translations = {
        "hello": {"hi": "नमस्ते", "bn": "হ্যালো", "ta": "வணக்கம்", "te": "హలో"},
        "thank you": {"hi": "धन्यवाद", "bn": "ধন্যবাদ", "ta": "நன்றி", "te": "ధన్యవాదాలు"},
        "how are you": {"hi": "आप कैसे हैं", "bn": "আপনি কেমন আছেন", "ta": "நீங்கள் எப்படி இருக்கிறீர்கள்"}
    }

    lower_text = text.lower().strip()
    if lower_text in translations and to_lang in translations[lower_text]:
        return {
            "success": True,
            "original": text,
            "translated": translations[lower_text][to_lang],
            "from": from_lang,
            "to": to_lang
        }

    return {
        "success": True,
        "original": text,
        "translated": text,
        "note": "Bhashini integration pending for full translation"
    }

@router.get("/detect")
def detect_language(text: str):
    """Detect language"""
    # Simple detection
    hindi_chars = set('अआइईउऊएऐओऔंःािीुूेैोौ्कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')

    for char in text:
        if char in hindi_chars:
            return {"success": True, "language": "hi", "confidence": 0.9}

    return {"success": True, "language": "en", "confidence": 0.8}
