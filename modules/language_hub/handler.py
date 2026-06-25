from flask import jsonify, request

# 50+ Languages Support
LANGUAGES = {
    'hi': {'name': 'हिन्दी', 'hello': 'नमस्ते', 'welcome': 'स्वागत है'},
    'en': {'name': 'English', 'hello': 'Hello', 'welcome': 'Welcome'},
    'bn': {'name': 'বাংলা', 'hello': 'নমস্কার', 'welcome': 'স্বাগতম'},
    'te': {'name': 'తెలుగు', 'hello': 'నమస్కారం', 'welcome': 'స్వాగతం'},
    'ta': {'name': 'தமிழ்', 'hello': 'வணக்கம்', 'welcome': 'வரவேற்கிறோம்'},
    'mr': {'name': 'मराठी', 'hello': 'नमस्कार', 'welcome': 'स्वागत आहे'},
    'gu': {'name': 'ગુજરાતી', 'hello': 'નમસ્તે', 'welcome': 'સ્વાગત છે'},
    'kn': {'name': 'ಕನ್ನಡ', 'hello': 'ನಮಸ್ಕಾರ', 'welcome': 'ಸ್ವಾಗತ'},
    'ml': {'name': 'മലയാളം', 'hello': 'നമസ്കാരം', 'welcome': 'സ്വാഗതം'},
    'pa': {'name': 'ਪੰਜਾਬੀ', 'hello': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ', 'welcome': 'ਜੀ ਆਇਆਂ ਨੂੰ'},
    'ur': {'name': 'اردو', 'hello': 'السلام علیکم', 'welcome': 'خوش آمدید'},
    'or': {'name': 'ଓଡ଼ିଆ', 'hello': 'ନମସ୍କାର', 'welcome': 'ସ୍ୱାଗତ'},
    'as': {'name': 'অসমীয়া', 'hello': 'নমস্কাৰ', 'welcome': 'স্বাগতম'},
    'ne': {'name': 'नेपाली', 'hello': 'नमस्ते', 'welcome': 'स्वागत छ'},
    'si': {'name': 'සිංහල', 'hello': 'ආයුබෝවන්', 'welcome': 'සාදරයෙන් පිළිගනිමු'},
    'zh': {'name': '中文', 'hello': '你好', 'welcome': '欢迎'},
    'ja': {'name': '日本語', 'hello': 'こんにちは', 'welcome': 'ようこそ'},
    'ko': {'name': '한국어', 'hello': '안녕하세요', 'welcome': '환영합니다'},
    'ar': {'name': 'العربية', 'hello': 'مرحبا', 'welcome': 'أهلا بك'},
    'fr': {'name': 'Français', 'hello': 'Bonjour', 'welcome': 'Bienvenue'},
    'de': {'name': 'Deutsch', 'hello': 'Hallo', 'welcome': 'Willkommen'},
    'es': {'name': 'Español', 'hello': 'Hola', 'welcome': 'Bienvenido'},
    'it': {'name': 'Italiano', 'hello': 'Ciao', 'welcome': 'Benvenuto'},
    'pt': {'name': 'Português', 'hello': 'Olá', 'welcome': 'Bem-vindo'},
    'ru': {'name': 'Русский', 'hello': 'Привет', 'welcome': 'Добро пожаловать'},
    'tr': {'name': 'Türkçe', 'hello': 'Merhaba', 'welcome': 'Hoş geldiniz'},
    'th': {'name': 'ไทย', 'hello': 'สวัสดี', 'welcome': 'ยินดีต้อนรับ'},
    'vi': {'name': 'Tiếng Việt', 'hello': 'Xin chào', 'welcome': 'Chào mừng'},
    'id': {'name': 'Bahasa Indonesia', 'hello': 'Halo', 'welcome': 'Selamat datang'},
    'ms': {'name': 'Bahasa Melayu', 'hello': 'Hai', 'welcome': 'Selamat datang'},
    'tl': {'name': 'Filipino', 'hello': 'Kamusta', 'welcome': 'Maligayang pagdating'},
    'pl': {'name': 'Polski', 'hello': 'Cześć', 'welcome': 'Witaj'},
    'uk': {'name': 'Українська', 'hello': 'Привіт', 'welcome': 'Ласкаво просимо'},
    'ro': {'name': 'Română', 'hello': 'Salut', 'welcome': 'Bun venit'},
    'nl': {'name': 'Nederlands', 'hello': 'Hallo', 'welcome': 'Welkom'},
    'sv': {'name': 'Svenska', 'hello': 'Hej', 'welcome': 'Välkommen'},
    'no': {'name': 'Norsk', 'hello': 'Hei', 'welcome': 'Velkommen'},
    'da': {'name': 'Dansk', 'hello': 'Hej', 'welcome': 'Velkommen'},
    'fi': {'name': 'Suomi', 'hello': 'Hei', 'welcome': 'Tervetuloa'},
    'cs': {'name': 'Čeština', 'hello': 'Ahoj', 'welcome': 'Vítejte'},
    'hu': {'name': 'Magyar', 'hello': 'Szia', 'welcome': 'Üdvözöljük'},
    'el': {'name': 'Ελληνικά', 'hello': 'Γεια σας', 'welcome': 'Καλώς ήρθατε'},
    'he': {'name': 'עברית', 'hello': 'שלום', 'welcome': 'ברוכים הבאים'},
    'fa': {'name': 'فارسی', 'hello': 'سلام', 'welcome': 'خوش آمدید'},
    'sw': {'name': 'Kiswahili', 'hello': 'Habari', 'welcome': 'Karibu'},
    'am': {'name': 'አማርኛ', 'hello': 'ሰላም', 'welcome': 'እንኳን ደህና መጡ'},
    'ha': {'name': 'Hausa', 'hello': 'Sannu', 'welcome': 'Barka da zuwa'},
    'yo': {'name': 'Yorùbá', 'hello': 'Báwo ni', 'welcome': 'Kaabo'},
    'ig': {'name': 'Igbo', 'hello': 'Nnọọ', 'welcome': 'Nnọọ'},
    'zu': {'name': 'isiZulu', 'hello': 'Sawubona', 'welcome': 'Siyakwamukela'},
}

def handler(path, request_obj):
    method = request_obj.method

    # Get all languages
    if path == 'list' and method == 'GET':
        return jsonify({
            "status": "success",
            "total": len(LANGUAGES),
            "languages": {k: v['name'] for k, v in LANGUAGES.items()}
        })

    # Get specific language
    elif path.startswith('get/') and method == 'GET':
        lang_code = path.split('/')[-1]
        return get_language(lang_code)

    # Translate simple text
    elif path == 'translate' and method == 'POST':
        data = request_obj.json
        return translate_text(data)

    # Detect language (basic)
    elif path == 'detect' and method == 'POST':
        data = request_obj.json
        return detect_language(data)

    else:
        return jsonify({"error": "Language endpoint not found"}), 404


def get_language(lang_code):
    if lang_code in LANGUAGES:
        return jsonify({
            "status": "found",
            "code": lang_code,
            "data": LANGUAGES[lang_code]
        })
    return jsonify({"status": "not_found", "code": lang_code}), 404


def translate_text(data):
    text = data.get('text', '')
    from_lang = data.get('from', 'en')
    to_lang = data.get('to', 'hi')

    # Simple mock translation (replace with real API later)
    if to_lang in LANGUAGES:
        greeting = LANGUAGES[to_lang]['hello']
        return jsonify({
            "status": "translated",
            "original": text,
            "translated": f"{greeting}! (Translated to {LANGUAGES[to_lang]['name']})",
            "from": from_lang,
            "to": to_lang
        })

    return jsonify({"error": "Language not supported"}), 400


def detect_language(data):
    text = data.get('text', '')

    # Basic detection by script
    if any('ऀ' <= c <= 'ॿ' for c in text):
        detected = 'hi'
    elif any('؀' <= c <= 'ۿ' for c in text):
        detected = 'ar'
    elif any('一' <= c <= '鿿' for c in text):
        detected = 'zh'
    elif any('぀' <= c <= 'ゟ' or '゠' <= c <= 'ヿ' for c in text):
        detected = 'ja'
    elif any('가' <= c <= '힯' for c in text):
        detected = 'ko'
    else:
        detected = 'en'

    return jsonify({
        "status": "detected",
        "language": detected,
        "name": LANGUAGES.get(detected, {}).get('name', 'Unknown')
    })
