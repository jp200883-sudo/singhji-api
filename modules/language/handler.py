from fastapi import Request
from datetime import datetime

LANGS = {
    "hi": {"name": "Hindi", "welcome": "🦁 नमस्ते! मैं सिंह जी AI हूँ।"},
    "en": {"name": "English", "welcome": "🦁 Hello! I am Singh Ji AI."},
    "ta": {"name": "Tamil", "welcome": "🦁 வணக்கம்! நான் சிங் ஜி AI."},
    "te": {"name": "Telugu", "welcome": "🦁 నమస్తే! నేను సింగ్ జీ AI."},
    "bn": {"name": "Bengali", "welcome": "🦁 নমস্কার! আমি সিংহ জী AI."},
    "mr": {"name": "Marathi", "welcome": "🦁 नमस्कार! मी सिंह जी AI आहे."},
    "gu": {"name": "Gujarati", "welcome": "🦁 નમસ્તે! હું સિંહ જી AI છું."},
    "pa": {"name": "Punjabi", "welcome": "🦁 ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਸਿੰਘ ਜੀ AI ਹਾਂ."},
    "ur": {"name": "Urdu", "welcome": "🦁 السلام علیکم! میں سنگھ جی AI ہوں۔"}
}

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "language", "total": len(LANGS), "languages": {k: v["name"] for k, v in LANGS.items()}}
    if method == "POST":
        try:
            b = await request.json()
            action = b.get("action", "welcome")
            if action == "welcome":
                lang = b.get("lang", "hi")
                return {"status": "success", "lang": lang, "message": LANGS.get(lang, LANGS["hi"])["welcome"]}
            elif action == "detect":
                text = b.get("text", "")
                detected = "hi" if any(c in text for c in "अआइई") else "en"
                return {"status": "success", "detected": detected, "language": LANGS[detected]["name"]}
            return {"status": "success", "action": action}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}
