# language/handler.py
import os
import json
import requests
import time
from typing import Dict, Any

# ========== CONFIG ==========
# Bhashini pending — using Google Translate free tier as fallback
# 7120 Jugaad = Google Translate API (free, no key needed for basic)

# ========== LANGUAGE MODULE ==========
class LanguageModule:
    def __init__(self):
        self.supported_languages = {
            "hi": "Hindi", "en": "English", "bn": "Bengali", "te": "Telugu",
            "mr": "Marathi", "ta": "Tamil", "ur": "Urdu", "gu": "Gujarati",
            "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi", "or": "Odia",
            "as": "Assamese", "ne": "Nepali", "sd": "Sindhi", "sa": "Sanskrit"
        }
        # Bhashini will replace this when approved
    
    def translate(self, text: str, target_lang: str = "hi", source_lang: str = "auto") -> Dict[str, Any]:
        """Translate text using free Google Translate API (7120 Jugaad)"""
        try:
            # Free Google Translate API (no key needed)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": source_lang,
                "tl": target_lang,
                "dt": "t",
                "q": text
            }
            
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            translated = ""
            if data and len(data) > 0 and data[0]:
                for sentence in data[0]:
                    if sentence and len(sentence) > 0:
                        translated += sentence[0]
            
            return {
                "success": True,
                "source": "Google Translate (Free)",
                "original": text,
                "translated": translated,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "target_name": self.supported_languages.get(target_lang, target_lang),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Translate failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original": text,
                "translated": text,  # Return original as fallback
                "note": "Translation failed - returned original text"
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "auto",
                "tl": "en",
                "dt": "t",
                "q": text
            }
            
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            detected = data[2] if len(data) > 2 else "unknown"
            
            return {
                "success": True,
                "detected_lang": detected,
                "language_name": self.supported_languages.get(detected, detected),
                "confidence": "high",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "detected_lang": "unknown"
            }
    
    def translate_bulk(self, texts: list, target_lang: str = "hi") -> Dict[str, Any]:
        """Translate multiple texts"""
        results = []
        for text in texts:
            result = self.translate(text, target_lang)
            results.append(result)
        
        return {
            "success": True,
            "translations": results,
            "count": len(results),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages"""
        return {
            "success": True,
            "languages": self.supported_languages,
            "count": len(self.supported_languages),
            "note": "Bhashini integration pending approval",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "language",
            "source": "Google Translate (Free) / Bhashini (Pending)",
            "status": "✅ Ready (Free Mode)"
        }


# ========== RENDER HANDLER ==========
def handler(request):
    if request.method == "GET":
        l = LanguageModule()
        params = request.args if hasattr(request, 'args') else {}
        action = params.get("action", "languages")
        
        if action == "languages":
            result = l.get_supported_languages()
        else:
            result = l.health_check()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result, ensure_ascii=False)
        }
    
    elif request.method == "POST":
        try:
            body = json.loads(request.body) if hasattr(request, 'body') else request.json()
            action = body.get("action", "translate")
            l = LanguageModule()
            
            if action == "translate":
                result = l.translate(
                    body.get("text", ""),
                    body.get("target_lang", "hi"),
                    body.get("source_lang", "auto")
                )
            elif action == "detect":
                result = l.detect_language(body.get("text", ""))
            elif action == "translate_bulk":
                result = l.translate_bulk(body.get("texts", []), body.get("target_lang", "hi"))
            else:
                result = {"error": "Unknown action"}
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result, ensure_ascii=False)
            }
            
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    
    return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}


if __name__ == "__main__":
    l = LanguageModule()
    print("🦁 SINGH JI AI ULTRA v7.0 — Language Module")
    print("Health:", l.health_check())
    print("\nTranslate (Hello → Hindi):")
    print(json.dumps(l.translate("Hello, how are you?", "hi"), indent=2, ensure_ascii=False))
    print("\nDetect Language:")
    print(json.dumps(l.detect_language("नमस्ते"), indent=2, ensure_ascii=False))
