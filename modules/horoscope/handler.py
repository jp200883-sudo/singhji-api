#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Horoscope (Rashifal) Handler Module
Daily, Weekly, Monthly horoscope for all 12 zodiac signs
"""
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

RASHIS = {
    "hi": [
        {"name": "मेष", "symbol": "♈", "element": "अग्नि", "ruler": "मंगल"},
        {"name": "वृष", "symbol": "♉", "element": "पृथ्वी", "ruler": "शुक्र"},
        {"name": "मिथुन", "symbol": "♊", "element": "वायु", "ruler": "बुध"},
        {"name": "कर्क", "symbol": "♋", "element": "जल", "ruler": "चंद्र"},
        {"name": "सिंह", "symbol": "♌", "element": "अग्नि", "ruler": "सूर्य"},
        {"name": "कन्या", "symbol": "♍", "element": "पृथ्वी", "ruler": "बुध"},
        {"name": "तुला", "symbol": "♎", "element": "वायु", "ruler": "शुक्र"},
        {"name": "वृश्चिक", "symbol": "♏", "element": "जल", "ruler": "मंगल"},
        {"name": "धनु", "symbol": "♐", "element": "अग्नि", "ruler": "गुरु"},
        {"name": "मकर", "symbol": "♑", "element": "पृथ्वी", "ruler": "शनि"},
        {"name": "कुंभ", "symbol": "♒", "element": "वायु", "ruler": "शनि"},
        {"name": "मीन", "symbol": "♓", "element": "जल", "ruler": "गुरु"}
    ],
    "en": [
        {"name": "Aries", "symbol": "♈", "element": "Fire", "ruler": "Mars"},
        {"name": "Taurus", "symbol": "♉", "element": "Earth", "ruler": "Venus"},
        {"name": "Gemini", "symbol": "♊", "element": "Air", "ruler": "Mercury"},
        {"name": "Cancer", "symbol": "♋", "element": "Water", "ruler": "Moon"},
        {"name": "Leo", "symbol": "♌", "element": "Fire", "ruler": "Sun"},
        {"name": "Virgo", "symbol": "♍", "element": "Earth", "ruler": "Mercury"},
        {"name": "Libra", "symbol": "♎", "element": "Air", "ruler": "Venus"},
        {"name": "Scorpio", "symbol": "♏", "element": "Water", "ruler": "Mars"},
        {"name": "Sagittarius", "symbol": "♐", "element": "Fire", "ruler": "Jupiter"},
        {"name": "Capricorn", "symbol": "♑", "element": "Earth", "ruler": "Saturn"},
        {"name": "Aquarius", "symbol": "♒", "element": "Air", "ruler": "Saturn"},
        {"name": "Pisces", "symbol": "♓", "element": "Water", "ruler": "Jupiter"}
    ]
}

DATE_RANGES = [
    {"start": (3, 21), "end": (4, 19), "hi": "मेष", "en": "Aries"},
    {"start": (4, 20), "end": (5, 20), "hi": "वृष", "en": "Taurus"},
    {"start": (5, 21), "end": (6, 20), "hi": "मिथुन", "en": "Gemini"},
    {"start": (6, 21), "end": (7, 22), "hi": "कर्क", "en": "Cancer"},
    {"start": (7, 23), "end": (8, 22), "hi": "सिंह", "en": "Leo"},
    {"start": (8, 23), "end": (9, 22), "hi": "कन्या", "en": "Virgo"},
    {"start": (9, 23), "end": (10, 22), "hi": "तुला", "en": "Libra"},
    {"start": (10, 23), "end": (11, 21), "hi": "वृश्चिक", "en": "Scorpio"},
    {"start": (11, 22), "end": (12, 21), "hi": "धनु", "en": "Sagittarius"},
    {"start": (12, 22), "end": (1, 19), "hi": "मकर", "en": "Capricorn"},
    {"start": (1, 20), "end": (2, 18), "hi": "कुंभ", "en": "Aquarius"},
    {"start": (2, 19), "end": (3, 20), "hi": "मीन", "en": "Pisces"}
]

LUCKY_ELEMENTS = {
    "hi": {
        "numbers": ["3", "7", "9", "12", "21", "27", "33", "42", "51", "72"],
        "colors": ["लाल", "पीला", "हरा", "नीला", "सफेद", "गुलाबी", "बैंगनी", "नारंगी"],
        "directions": ["उत्तर", "दक्षिण", "पूर्व", "पश्चिम", "उत्तर-पूर्व", "दक्षिण-पश्चिम"],
        "gems": ["माणिक्य", "पुखराज", "हीरा", "मोती", "मूंगा", "पन्ना", "नीलम", "गोमेद", "लहसुनिया"]
    },
    "en": {
        "numbers": ["3", "7", "9", "12", "21", "27", "33", "42", "51", "72"],
        "colors": ["Red", "Yellow", "Green", "Blue", "White", "Pink", "Purple", "Orange"],
        "directions": ["North", "South", "East", "West", "Northeast", "Southwest"],
        "gems": ["Ruby", "Yellow Sapphire", "Diamond", "Pearl", "Coral", "Emerald", "Blue Sapphire", "Hessonite", "Cat's Eye"]
    }
}

SENTIMENTS = {
    "hi": ["शुभ", "अनुकूल", "मिश्रित", "उत्साहवर्धक", "शांतिपूर्ण", "ऊर्जावान"],
    "en": ["auspicious", "favorable", "mixed", "encouraging", "peaceful", "energetic"]
}

AREAS = {
    "hi": ["करियर", "पैसा", "परिवार", "स्वास्थ्य", "प्रेम", "व्यापार", "पढ़ाई", "यात्रा"],
    "en": ["career", "finance", "family", "health", "love", "business", "education", "travel"]
}

ADVICE = {
    "hi": ["धैर्य रखने", "सावधानी बरतने", "नए अवसर तलाशने", "पुराने रिश्तों को संभालने", "स्वास्थ्य का ध्यान रखने"],
    "en": ["patience", "caution", "seeking new opportunities", "maintaining old relationships", "taking care of health"]
}


class HoroscopeHandler:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600
        self.last_fetch = {}

    def get_rashi_by_date(self, day: int, month: int, language: str = "hi") -> str:
        for zodiac in DATE_RANGES:
            sm, sd = zodiac["start"]
            em, ed = zodiac["end"]
            if sm == em:
                if month == sm and sd <= day <= ed:
                    return zodiac[language]
            else:
                if (month == sm and day >= sd) or (month == em and day <= ed):
                    return zodiac[language]
        return "मेष" if language == "hi" else "Aries"

    def get_rashi_index(self, rashi_name: str, language: str = "hi") -> int:
        for i, rashi in enumerate(RASHIS[language]):
            if rashi["name"].lower() == rashi_name.lower():
                return i
        return 0

    def get_rashi_details(self, rashi_name: str, language: str = "hi") -> Dict:
        idx = self.get_rashi_index(rashi_name, language)
        rashi = RASHIS[language][idx]
        opposite_idx = (idx + 6) % 12
        opposite = RASHIS[language][opposite_idx]
        return {
            "name": rashi["name"],
            "symbol": rashi["symbol"],
            "element": rashi["element"],
            "ruler": rashi["ruler"],
            "opposite": opposite["name"],
            "index": idx + 1,
            "lucky_number": random.choice(LUCKY_ELEMENTS[language]["numbers"]),
            "lucky_color": random.choice(LUCKY_ELEMENTS[language]["colors"]),
            "lucky_direction": random.choice(LUCKY_ELEMENTS[language]["directions"]),
            "lucky_gem": random.choice(LUCKY_ELEMENTS[language]["gems"])
        }

    def _generate_prediction(self, rashi: str, period: str, language: str) -> Dict:
        random.seed(hash(f"{rashi}_{period}_{datetime.now().strftime('%Y%m%d')}"))
        sentiments = SENTIMENTS[language]
        areas_list = AREAS[language]
        advice_list = ADVICE[language]
        
        prediction = f"{rashi} के लिए आज का दिन {random.choice(sentiments)} रहेगा। {random.choice(areas_list)} में सफलता मिलेगी। {random.choice(advice_list)} की जरूरत है।"
        
        return {
            "prediction": prediction,
            "career": f"{random.choice(areas_list)}: {random.choice(sentiments)}",
            "love": f"प्रेम: {random.choice(sentiments)}" if language == "hi" else f"love: {random.choice(sentiments)}",
            "health": f"स्वास्थ्य: {random.choice(sentiments)}" if language == "hi" else f"health: {random.choice(sentiments)}",
            "finance": f"धन: {random.choice(sentiments)}" if language == "hi" else f"finance: {random.choice(sentiments)}",
            "lucky_number": random.choice(LUCKY_ELEMENTS[language]["numbers"]),
            "lucky_color": random.choice(LUCKY_ELEMENTS[language]["colors"]),
            "lucky_time": f"{random.randint(6, 11)}:{random.choice(['00', '15', '30', '45'])} {'AM' if language == 'en' else 'सुबह'}",
            "lucky_direction": random.choice(LUCKY_ELEMENTS[language]["directions"]),
            "advice": random.choice(advice_list)
        }

    def get_horoscope(self, rashi: str, period: str = "daily", language: str = "hi", date: str = None) -> Dict:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        rashi_details = self.get_rashi_details(rashi, language)
        fallback = self._generate_prediction(rashi, period, language)
        
        return {
            "rashi": rashi,
            "period": period,
            "language": language,
            "date": date,
            "source": "fallback",
            "prediction": fallback["prediction"],
            "career": fallback["career"],
            "love": fallback["love"],
            "health": fallback["health"],
            "finance": fallback["finance"],
            "lucky_number": fallback["lucky_number"],
            "lucky_color": fallback["lucky_color"],
            "lucky_time": fallback["lucky_time"],
            "lucky_direction": fallback["lucky_direction"],
            "advice": fallback["advice"],
            "details": rashi_details,
            "timestamp": datetime.now().isoformat()
        }

    def get_all_horoscopes(self, period: str = "daily", language: str = "hi") -> Dict:
        all_rashis = []
        for rashi in RASHIS[language]:
            horoscope = self.get_horoscope(rashi["name"], period, language)
            all_rashis.append({
                "rashi": rashi["name"],
                "symbol": rashi["symbol"],
                "prediction": horoscope.get("prediction", "")[:100] + "...",
                "lucky_number": horoscope.get("lucky_number", ""),
                "lucky_color": horoscope.get("lucky_color", "")
            })
        return {
            "status": "success",
            "period": period,
            "language": language,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "count": len(all_rashis),
            "rashis": all_rashis,
            "timestamp": datetime.now().isoformat()
        }

    def get_compatibility(self, rashi1: str, rashi2: str, language: str = "hi") -> Dict:
        idx1 = self.get_rashi_index(rashi1, language)
        idx2 = self.get_rashi_index(rashi2, language)
        diff = abs(idx1 - idx2)
        
        if diff == 0:
            score, level = 85, "अच्छी" if language == "hi" else "Good"
        elif diff == 6:
            score, level = 90, "बहुत अच्छी" if language == "hi" else "Excellent"
        elif diff in [3, 9]:
            score, level = 75, "मिश्रित" if language == "hi" else "Mixed"
        elif diff in [4, 8]:
            score, level = 80, "अनुकूल" if language == "hi" else "Favorable"
        else:
            score, level = random.randint(60, 95), "अच्छी" if language == "hi" else "Good"
        
        message = f"{rashi1} और {rashi2} की जोड़ी {score}% अनुकूल है।" if language == "hi" else f"{rashi1} and {rashi2} are {score}% compatible."
        
        return {
            "status": "success",
            "rashi1": rashi1,
            "rashi2": rashi2,
            "compatibility_score": score,
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

    def format_telegram(self, horoscope_data: Dict) -> str:
        language = horoscope_data.get("language", "hi")
        rashi = horoscope_data.get("rashi", "")
        details = horoscope_data.get("details", {})
        
        if language == "hi":
            return f"""🔮 *{details.get('symbol', '')} {rashi} राशिफल* 🔮
━━━━━━━━━━━━━━━
📅 *तारीख:* {horoscope_data.get('date', '')}

📝 *भविष्यवाणी:*
{horoscope_data.get('prediction', '')}

💼 *करियर:* {horoscope_data.get('career', 'अनुकूल')}
❤️ *प्रेम:* {horoscope_data.get('love', 'अच्छा')}
🏥 *स्वास्थ्य:* {horoscope_data.get('health', 'अच्छा')}
💰 *धन:* {horoscope_data.get('finance', 'लाभदायक')}

🍀 *भाग्यशाली:*
🔢 नंबर: {horoscope_data.get('lucky_number', '')}
🎨 रंग: {horoscope_data.get('lucky_color', '')}
⏰ समय: {horoscope_data.get('lucky_time', '')}
🧭 दिशा: {horoscope_data.get('lucky_direction', '')}

💡 *सलाह:* {horoscope_data.get('advice', '')}

━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"""
        else:
            return f"""🔮 *{details.get('symbol', '')} {rashi} Horoscope* 🔮
━━━━━━━━━━━━━━━
📅 *Date:* {horoscope_data.get('date', '')}

📝 *Prediction:*
{horoscope_data.get('prediction', '')}

💼 *Career:* {horoscope_data.get('career', 'Favorable')}
❤️ *Love:* {horoscope_data.get('love', 'Good')}
🏥 *Health:* {horoscope_data.get('health', 'Good')}
💰 *Finance:* {horoscope_data.get('finance', 'Profitable')}

🍀 *Lucky:*
🔢 Number: {horoscope_data.get('lucky_number', '')}
🎨 Color: {horoscope_data.get('lucky_color', '')}
⏰ Time: {horoscope_data.get('lucky_time', '')}
🧭 Direction: {horoscope_data.get('lucky_direction', '')}

💡 *Advice:* {horoscope_data.get('advice', '')}

━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"""


# Singleton
horoscope_handler = HoroscopeHandler()

def get_horoscope(rashi: str, period: str = "daily", language: str = "hi", date: str = None) -> Dict:
    return horoscope_handler.get_horoscope(rashi, period, language, date)

def get_all_horoscopes(period: str = "daily", language: str = "hi") -> Dict:
    return horoscope_handler.get_all_horoscopes(period, language)

def get_rashi_by_date(day: int, month: int, language: str = "hi") -> str:
    return horoscope_handler.get_rashi_by_date(day, month, language)

def get_compatibility(rashi1: str, rashi2: str, language: str = "hi") -> Dict:
    return horoscope_handler.get_compatibility(rashi1, rashi2, language)

def format_telegram(horoscope_data: Dict) -> str:
    return horoscope_handler.format_telegram(horoscope_data)


# FastAPI handler for dynamic router
async def handler(request):
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)
        
        rashi = body.get("rashi") or params.get("rashi", "मेष")
        period = body.get("period") or params.get("period", "daily")
        language = body.get("language") or params.get("language", "hi")
        action = body.get("action") or params.get("action", "get_horoscope")
        
        if action == "get_horoscope":
            result = get_horoscope(rashi, period, language)
        elif action == "all":
            result = get_all_horoscopes(period, language)
        elif action == "by_date":
            day = int(body.get("day") or params.get("day", 1))
            month = int(body.get("month") or params.get("month", 1))
            result = {"status": "success", "rashi": get_rashi_by_date(day, month, language)}
        elif action == "compatibility":
            rashi1 = body.get("rashi1") or params.get("rashi1", "मेष")
            rashi2 = body.get("rashi2") or params.get("rashi2", "तुला")
            result = get_compatibility(rashi1, rashi2, language)
        elif action == "telegram":
            horoscope_data = get_horoscope(rashi, period, language)
            result = {"status": "success", "message": format_telegram(horoscope_data)}
        else:
            result = get_horoscope(rashi, period, language)
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
