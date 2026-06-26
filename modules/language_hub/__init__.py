from flask import jsonify, request
import os
import requests

# Bhashini API (Govt of India)
BHASHINI_API_KEY = os.environ.get('BHASHINI_API_KEY', '')
BHASHINI_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model"

# NLLB-200 (Meta) - via Hugging Face
NLLB_API_URL = "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M"
HF_TOKEN = os.environ.get('HUGGINGFACE_TOKEN', '')

# 50+ Languages
LANGUAGES = {
    'hi': {'name': 'हिन्दी', 'source': 'bhashini', 'hello': 'नमस्ते'},
    'bn': {'name': 'বাংলা', 'source': 'bhashini', 'hello': 'নমস্কার'},
    'te': {'name': 'తెలుగు', 'source': 'bhashini', 'hello': 'నమస్కారం'},
    'ta': {'name': 'தமிழ்', 'source': 'bhashini', 'hello': 'வணக்கம்'},
    'mr': {'name': 'मराठी', 'source': 'bhashini', 'hello': 'नमस्कार'},
    'gu': {'name': 'ગુજરાતી', 'source': 'bhashini', 'hello': 'નમસ્તે'},
    'kn': {'name': 'ಕನ್ನಡ', 'source': 'bhashini', 'hello': 'ನಮಸ್ಕಾರ'},
    'ml': {'name': 'മലയാളം', 'source': 'bhashini', 'hello': 'നമസ്കാരം'},
    'pa': {'name': 'ਪੰਜਾਬੀ', 'source': 'bhashini', 'hello': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ'},
    'ur': {'name': 'اردو', 'source': 'bhashini', 'hello': 'السلام علیکم'},
    'or': {'name': 'ଓଡ଼ିଆ', 'source': 'bhashini', 'hello': 'ନମସ୍କାର'},
    'as': {'name': 'অসমীয়া', 'source': 'bhashini', 'hello': 'নমস্কাৰ'},
    'ne': {'name': 'नेपाली', 'source': 'bhashini', 'hello': 'नमस्ते'},
    'si': {'name': 'සිංහල', 'source': 'bhashini', 'hello': 'ආයුබෝවන්'},
    'sd': {'name': 'سنڌي', 'source': 'bhashini', 'hello': 'سلام'},
    'sa': {'name': 'संस्कृत', 'source': 'bhashini', 'hello': 'नमो नमः'},
    'kok': {'name': 'कोंकणी', 'source': 'bhashini', 'hello': 'नमस्कार'},
    'mni': {'name': 'মৈতৈলোন্', 'source': 'bhashini', 'hello': 'খুরুমজরি'},
    'brx': {'name': 'बड़ो', 'source': 'bhashini', 'hello': 'नमसे'},
    'doi': {'name': 'डोगरी', 'source': 'bhashini', 'hello': 'नमस्कार'},
    'mai': {'name': 'मैथिली', 'source': 'bhashini', 'hello': 'नमस्कार'},
    'sat': {'name': 'ᱥᱟᱱᱛᱟᱲᱤ', 'source': 'bhashini', 'hello': 'ᱡᱚᱦᱟᱨ'},
    'en': {'name': 'English', 'source': 'nllb', 'hello': 'Hello'},
    'zh': {'name': '中文', 'source': 'nllb', 'hello': '你好'},
    'ja': {'name': '日本語', 'source': 'nllb', 'hello': 'こんにちは'},
    'ko': {'name': '한국어', 'source': 'nllb', 'hello': '안녕하세요'},
    'ar': {'name': 'العربية', 'source': 'nllb', 'hello': 'مرحبا'},
    'fr': {'name': 'Français', 'source': 'nllb', 'hello': 'Bonjour'},
    'de': {'name': 'Deutsch', 'source': 'nllb', 'hello': 'Hallo'},
    'es': {'name': 'Español', 'source': 'nllb', 'hello': 'Hola'},
    'it': {'name': 'Italiano', 'source': 'nllb', 'hello': 'Ciao'},
    'pt': {'name': 'Português', 'source': 'nllb', 'hello': 'Olá'},
    'ru': {'name': 'Русский', 'source': 'nllb', 'hello': 'Привет'},
    'tr': {'name': 'Türkçe', 'source': 'nllb', 'hello': 'Merhaba'},
    'th': {'name': 'ไทย', 'source': 'nllb', 'hello': 'สวัสดี'},
    'vi': {'name': 'Tiếng Việt', 'source': 'nllb', 'hello': 'Xin chào'},
    'id': {'name': 'Bahasa Indonesia', 'source': 'nllb', 'hello': 'Halo'},
    'ms': {'name': 'Bahasa Melayu', 'source': 'nllb', 'hello': 'Hai'},
    'tl': {'name': 'Filipino', 'source': 'nllb', 'hello': 'Kamusta'},
    'pl': {'name': 'Polski', 'source': 'nllb', 'hello': 'Cześć'},
    'uk': {'name': 'Українська', 'source': 'nllb', 'hello': 'Привіт'},
    'ro': {'name': 'Română', 'source': 'nllb', 'hello': 'Salut'},
    'nl': {'name': 'Nederlands', 'source': 'nllb', 'hello': 'Hallo'},
    'sv': {'name': 'Svenska', 'source': 'nllb', 'hello': 'Hej'},
    'no': {'name': 'Norsk', 'source': 'nllb', 'hello': 'Hei'},
    'da': {'name': 'Dansk', 'source': 'nllb', 'hello': 'Hej'},
    'fi': {'name': 'Suomi', 'source': 'nllb', 'hello': 'Hei'},
    'cs': {'name': 'Čeština', 'source': 'nllb', 'hello': 'Ahoj'},
    'hu': {'name': 'Magyar', 'source': 'nllb', 'hello': 'Szia'},
    'el': {'name': 'Ελληνικά', 'source': 'nllb', 'hello': 'Γεια σας'},
    'he': {'name': 'עברית', 'source': 'nllb', 'hello': 'שלום'},
    'fa': {'name': 'فارسی', 'source': 'nllb', 'hello': 'سلام'},
    'sw': {'name': 'Kiswahili', 'source': 'nllb', 'hello': 'Habari'},
    'am': {'name': 'አማርኛ', 'source': 'nllb', 'hello': 'ሰላም'},
    'ha': {'name': 'Hausa', 'source': 'nllb', 'hello': 'Sannu'},
    'yo': {'name': 'Yorùbá', 'source': 'nllb', 'hello': 'Báwo ni'},
    'ig': {'name': 'Igbo', 'source': 'nllb', 'hello': 'Nnọọ'},
    'zu': {'name': 'isiZulu', 'source': 'nllb', 'hello': 'Sawubona'},
}

def handler(path, request_obj):
    method = request_obj.method

    if path == 'list' and method == 'GET':
        return jsonify({
            "status": "success",
            "total": len(LANGUAGES),
            "indian": sum(1 for v in LANGUAGES.values() if v['source'] == 'bhashini'),
            "global": sum(1 for v in LANGUAGES.values() if v['source'] == 'nllb'),
            "languages": {k: {"name": v['name'], "source": v['source']} for k, v in LANGUAGES.items()}
        })

    elif path == 'translate' and method == 'POST':
        data = request_obj.json
        return translate(data)

    elif path == 'detect' and method == 'POST':
        data = request_obj.json
        return detect_language(data)

    elif path.startswith('hello/') and method == 'GET':
        lang_code = path.split('/')[-1]
        return get_hello(lang_code)

    else:
        return jsonify({"error": "Language endpoint not found"}), 404


def translate(data):
    text = data.get('text', '')
    from_lang = data.get('from', 'en')
    to_lang = data.get('to', 'hi')

    if to_lang not in LANGUAGES:
        return jsonify({"error": "Language not supported"}), 400

    source = LANGUAGES[to_lang]['source']

    if source == 'bhashini' and BHASHINI_API_KEY:
        return bhashini_translate(text, from_lang, to_lang)
    else:
        return nllb_translate(text, from_lang, to_lang)


def bhashini_translate(text, from_lang, to_lang):
    try:
        headers = {
            "Authorization": BHASHINI_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "input": [{"source": text}],
            "config": {
                "language": {
                    "sourceLanguage": from_lang,
                    "targetLanguage": to_lang
                }
            }
        }

        res = requests.post(f"{BHASHINI_URL}/compute", json=payload, headers=headers, timeout=10)
        data = res.json()

        if 'output' in data and len(data['output']) > 0:
            translated = data['output'][0].get('target', text)
            return jsonify({
                "status": "translated",
                "source": "bhashini",
                "original": text,
                "translated": translated,
                "from": from_lang,
                "to": to_lang
            })

        return nllb_translate(text, from_lang, to_lang)

    except Exception as e:
        return nllb_translate(text, from_lang, to_lang)


def nllb_translate(text, from_lang, to_lang):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

        payload = {
            "inputs": text,
            "parameters": {
                "src_lang": from_lang,
                "tgt_lang": to_lang
            }
        }

        res = requests.post(NLLB_API_URL, json=payload, headers=headers, timeout=15)
        data = res.json()

        if isinstance(data, list) and len(data) > 0:
            translated = data[0].get('translation_text', text)
        else:
            translated = text

        return jsonify({
            "status": "translated",
            "source": "nllb-200",
            "original": text,
            "translated": translated,
            "from": from_lang,
            "to": to_lang
        })

    except Exception as e:
        return jsonify({
            "status": "fallback",
            "source": "gemini-ready",
            "original": text,
            "translated": text,
            "note": "Translation service temporarily unavailable",
            "from": from_lang,
            "to": to_lang
        })


def detect_language(data):
    text = data.get('text', '')

    if any('\u0900' <= c <= '\u097F' for c in text):
        detected = 'hi'
    elif any('\u0980' <= c <= '\u09FF' for c in text):
        detected = 'bn'
    elif any('\u0C00' <= c <= '\u0C7F' for c in text):
        detected = 'te'
    elif any('\u0B80' <= c <= '\u0BFF' for c in text):
        detected = 'ta'
    elif any('\u0600' <= c <= '\u06FF' for c in text):
        detected = 'ur'
    elif any('\u4E00' <= c <= '\u9FFF' for c in text):
        detected = 'zh'
    elif any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' for c in text):
        detected = 'ja'
    elif any('\uAC00' <= c <= '\uD7AF' for c in text):
        detected = 'ko'
    elif any('\u0400' <= c <= '\u04FF' for c in text):
        detected = 'ru'
    else:
        detected = 'en'

    return jsonify({
        "status": "detected",
        "language": detected,
        "name": LANGUAGES.get(detected, {}).get('name', 'Unknown'),
        "source": LANGUAGES.get(detected, {}).get('source', 'nllb')
    })


def get_hello(lang_code):
    if lang_code in LANGUAGES:
        return jsonify({
            "status": "found",
            "code": lang_code,
            "hello": LANGUAGES[lang_code]['hello'],
            "name": LANGUAGES[lang_code]['name']
        })
    return jsonify({"status": "not_found"}), 404
