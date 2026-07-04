#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Horoscope (Rashifal) Handler Module
Daily, Weekly, Monthly horoscope for all 12 zodiac signs
Supports Hindi and English with AI-generated predictions
"""

import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# 12 Zodiac Signs - Hindi & English
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

# Date ranges for zodiac signs
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

# Lucky elements
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

# Prediction templates (fallback when AI not available)
PREDICTION_TEMPLATES = {
    "hi": {
        "daily": [
            "आज का दिन आपके लिए {sentiment} रहेगा। {area} में सफलता मिलेगी।",
            "{area} में नए अवसर आएंगे। आपकी मेहनत रंग लाएगी।",
            "आज आपको {advice} की जरूरत है। धैर्य रखें।",
            "{area} में कोई बड़ी खुशखबरी मिल सकती है। तैयार रहें।",
            "आज का दिन {sentiment} है। {area} में सावधानी बरतें।"
        ],
        "weekly": [
            "इस सप्ताह {area} में अच्छे परिणाम मिलेंगे।",
            "सप्ताह की शुरुआत {sentiment} रहेगी। अंत में लाभ होगा।",
            "{area} में नई शुरुआत के लिए अच्छा समय है।"
        ],
        "monthly": [
            "इस महीने {area} में बड़ी प्रगति होगी।",
            "महीने का पहला आधा {sentiment} रहेगा।",
            "{area} में निवेश का अच्छा समय है।"
        ]
    },
    "en": {
        "daily": [
            "Today will be a {sentiment} day for you. Success in {area}.",
            "New opportunities in {area} await you. Your hard work will pay off.",
            "You need to {advice} today. Stay patient.",
            "Good news may come in {area}. Stay prepared.",
            "Today is a {sentiment} day. Be cautious in {area}."
        ],
        "weekly": [
            "This week brings good results in {area}.",
            "The week starts {sentiment}. Profits by the end.",
            "Good time for new beginnings in {area}."
        ],
        "monthly": [
            "This month brings significant progress in {area}.",
            "The first half of the month will be {sentiment}.",
            "Good time for investment in {area}."
        ]
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
    """Horoscope handler for Singh Ji AI Ultra"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache for daily
        self.last_fetch = {}

    def _get_cache_key(self, rashi: str, period: str, date_str: str, language: str) -> str:
        return f"{rashi}_{period}_{date_str}_{language}"

    def _get_cached(self, key: str) -> Optional[Dict]:
        if key in self.cache and key in self.last_fetch:
            if datetime.now() - self.last_fetch[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data: Dict):
        self.cache[key] = data
        self.last_fetch[key] = datetime.now()

    def get_rashi_by_date(self, day: int, month: int, language: str = "hi") -> str:
        """Get zodiac sign by birth date"""
        for zodiac in DATE_RANGES:
            start_month, start_day = zodiac["start"]
            end_month, end_day = zodiac["end"]

            if start_month == end_month:  # Same month
                if month == start_month and start_day <= day <= end_day:
                    return zodiac[language]
            else:  # Crosses year boundary (Capricorn/Aquarius)
                if (month == start_month and day >= start_day) or                    (month == end_month and day <= end_day):
                    return zodiac[language]
        return "मेष" if language == "hi" else "Aries"

    def get_rashi_index(self, rashi_name: str, language: str = "hi") -> int:
        """Get index of rashi by name"""
        for i, rashi in enumerate(RASHIS[language]):
            if rashi["name"].lower() == rashi_name.lower():
                return i
        return 0  # Default to first

    def get_rashi_details(self, rashi_name: str, language: str = "hi") -> Dict:
        """Get full details of a zodiac sign"""
        idx = self.get_rashi_index(rashi_name, language)
        rashi = RASHIS[language][idx]

        # Get opposite sign
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

    def _generate_ai_prediction(self, rashi: str, period: str, language: str) -> Optional[str]:
        """Generate prediction using Groq AI"""
        if not GROQ_API_KEY:
            return None

        try:
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            if language == "hi":
                prompt = f"""आप एक प्रसिद्ध ज्योतिषी हैं। {rashi} राशि के लिए आज ({datetime.now().strftime('%d %B %Y')}) का राशिफल हिंदी में लिखिए।

शामिल करें:
1. दैनिक भविष्यवाणी (2-3 वाक्य)
2. करियर/व्यापार
3. प्रेम/रिश्ते
4. स्वास्थ्य
5. आज का लकी नंबर, रंग और समय
6. एक सलाह

सकारात्मक और प्रेरणादायक रहिए। सिर्फ हिंदी में जवाब दीजिए।"""
            else:
                prompt = f"""You are a famous astrologer. Write today's ({datetime.now().strftime('%d %B %Y')}) horoscope for {rashi} zodiac sign.

Include:
1. Daily prediction (2-3 sentences)
2. Career/Business
3. Love/Relationships
4. Health
5. Lucky number, color and time
6. One advice

Be positive and inspiring."""

            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are an expert astrologer. Provide accurate and positive horoscope readings."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            response = requests.post(groq_url, headers=headers, json=data, timeout=15)
            result = response.json()

            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            return None

        except Exception as e:
            print(f"[HoroscopeHandler] AI Error: {e}")
            return None

    def _generate_fallback_prediction(self, rashi: str, period: str, language: str) -> Dict:
        """Generate fallback prediction when AI unavailable"""
        random.seed(hash(f"{rashi}_{period}_{datetime.now().strftime('%Y%m%d')}"))

        templates = PREDICTION_TEMPLATES[language][period]
        sentiments = SENTIMENTS[language]
        areas = AREAS[language]
        advice = ADVICE[language]

        predictions = []
        for _ in range(3):
            template = random.choice(templates)
            prediction = template.format(
                sentiment=random.choice(sentiments),
                area=random.choice(areas),
                advice=random.choice(advice)
            )
            predictions.append(prediction)

        return {
            "prediction": " ".join(predictions),
            "career": f"{random.choice(areas)}: {random.choice(sentiments)}",
            "love": f"{random.choice(['प्रेम', 'रिश्ते', 'परिवार'] if language == 'hi' else ['love', 'relationships', 'family'])}: {random.choice(sentiments)}",
            "health": f"{random.choice(['स्वास्थ्य', 'तंदुरुस्ती'] if language == 'hi' else ['health', 'fitness'])}: {random.choice(sentiments)}",
            "finance": f"{random.choice(['पैसा', 'व्यापार'] if language == 'hi' else ['finance', 'business'])}: {random.choice(sentiments)}",
            "lucky_number": random.choice(LUCKY_ELEMENTS[language]["numbers"]),
            "lucky_color": random.choice(LUCKY_ELEMENTS[language]["colors"]),
            "lucky_time": f"{random.randint(6, 11)}:{random.choice(['00', '15', '30', '45'])} {'AM' if language == 'en' else 'सुबह'}" if random.random() > 0.5 else f"{random.randint(1, 8)}:{random.choice(['00', '15', '30', '45'])} {'PM' if language == 'en' else 'शाम'}",
            "lucky_direction": random.choice(LUCKY_ELEMENTS[language]["directions"]),
            "advice": random.choice(advice)
        }

    def get_horoscope(self, rashi: str, period: str = "daily", language: str = "hi", date: str = None) -> Dict:
        """
        Get horoscope for a zodiac sign

        Args:
            rashi: Zodiac sign name (e.g., "मेष", "Aries")
            period: "daily", "weekly", "monthly"
            language: "hi" or "en"
            date: Specific date (YYYY-MM-DD), default today

        Returns:
            Dict with horoscope data
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cache_key = self._get_cache_key(rashi, period, date, language)
        cached = self._get_cached(cache_key)

        if cached:
            return cached

        # Get rashi details
        rashi_details = self.get_rashi_details(rashi, language)

        # Try AI prediction first
        ai_prediction = self._generate_ai_prediction(rashi, period, language)

        if ai_prediction:
            # Parse AI response
            horoscope_data = {
                "rashi": rashi,
                "period": period,
                "language": language,
                "date": date,
                "source": "ai",
                "prediction": ai_prediction,
                "details": rashi_details,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Use fallback
            fallback = self._generate_fallback_prediction(rashi, period, language)
            horoscope_data = {
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

        self._set_cache(cache_key, horoscope_data)
        return horoscope_data

    def get_all_rashis(self, period: str = "daily", language: str = "hi") -> Dict:
        """Get horoscope for all 12 zodiac signs"""
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
        """Get compatibility between two zodiac signs"""
        idx1 = self.get_rashi_index(rashi1, language)
        idx2 = self.get_rashi_index(rashi2, language)

        # Calculate compatibility score
        diff = abs(idx1 - idx2)
        if diff == 0:
            score = 85  # Same sign
            level = "अच्छी" if language == "hi" else "Good"
        elif diff == 6:
            score = 90  # Opposite signs (attract)
            level = "बहुत अच्छी" if language == "hi" else "Excellent"
        elif diff in [3, 9]:
            score = 75  # Square aspect
            level = "मिश्रित" if language == "hi" else "Mixed"
        elif diff in [4, 8]:
            score = 80  # Trine aspect
            level = "अनुकूल" if language == "hi" else "Favorable"
        else:
            score = random.randint(60, 95)
            level = "अच्छी" if language == "hi" else "Good"

        if language == "hi":
            message = f"{rashi1} और {rashi2} की जोड़ी {score}% अनुकूल है। {level} संबंध बन सकता है।"
        else:
            message = f"{rashi1} and {rashi2} are {score}% compatible. {level} relationship possible."

        return {
            "status": "success",
            "rashi1": rashi1,
            "rashi2": rashi2,
            "compatibility_score": score,
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

    def format_for_telegram(self, horoscope_data: Dict) -> str:
        """Format horoscope for Telegram"""
        language = horoscope_data.get("language", "hi")
        rashi = horoscope_data.get("rashi", "")
        details = horoscope_data.get("details", {})

        if language == "hi":
            message = f"""🔮 *{details.get('symbol', '')} {rashi} राशिफल* 🔮
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
            message = f"""🔮 *{details.get('symbol', '')} {rashi} Horoscope* 🔮
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

        return message

    def format_all_for_telegram(self, all_data: Dict, language: str = "hi") -> str:
        """Format all 12 rashis for Telegram"""
        rashis = all_data.get("rashis", [])
        date = all_data.get("date", "")

        if language == "hi":
            message = f"📅 *आज का राशिफल — {date}* 📅

"
        else:
            message = f"📅 *Today's Horoscope — {date}* 📅

"

        for r in rashis:
            message += f"{r.get('symbol', '')} *{r.get('rashi', '')}*
"
            message += f"   📝 {r.get('prediction', '')}
"
            message += f"   🍀 {r.get('lucky_number', '')} | {r.get('lucky_color', '')}

"

        message += "⚡ *Singh Ji AI Ultra v7.0*"
        return message

    def format_for_web(self, horoscope_data: Dict) -> str:
        """Format horoscope for web display"""
        rashi = horoscope_data.get("rashi", "")
        details = horoscope_data.get("details", {})

        html = f"""
        <div class="horoscope-card">
            <div class="horoscope-header">
                <span class="horoscope-symbol">{details.get('symbol', '')}</span>
                <h2 class="horoscope-name">{rashi}</h2>
                <span class="horoscope-element">{details.get('element', '')}</span>
                <span class="horoscope-ruler">{details.get('ruler', '')}</span>
            </div>
            <div class="horoscope-date">{horoscope_data.get('date', '')}</div>
            <div class="horoscope-prediction">{horoscope_data.get('prediction', '')}</div>
            <div class="horoscope-sections">
                <div class="section">
                    <span class="section-icon">💼</span>
                    <span class="section-label">Career</span>
                    <span class="section-value">{horoscope_data.get('career', '')}</span>
                </div>
                <div class="section">
                    <span class="section-icon">❤️</span>
                    <span class="section-label">Love</span>
                    <span class="section-value">{horoscope_data.get('love', '')}</span>
                </div>
                <div class="section">
                    <span class="section-icon">🏥</span>
                    <span class="section-label">Health</span>
                    <span class="section-value">{horoscope_data.get('health', '')}</span>
                </div>
                <div class="section">
                    <span class="section-icon">💰</span>
                    <span class="section-label">Finance</span>
                    <span class="section-value">{horoscope_data.get('finance', '')}</span>
                </div>
            </div>
            <div class="horoscope-lucky">
                <div class="lucky-item">🔢 {horoscope_data.get('lucky_number', '')}</div>
                <div class="lucky-item">🎨 {horoscope_data.get('lucky_color', '')}</div>
                <div class="lucky-item">⏰ {horoscope_data.get('lucky_time', '')}</div>
                <div class="lucky-item">🧭 {horoscope_data.get('lucky_direction', '')}</div>
            </div>
            <div class="horoscope-advice">
                <strong>💡 Advice:</strong> {horoscope_data.get('advice', '')}
            </div>
        </div>
        """
        return html


# Singleton instance
horoscope_handler = HoroscopeHandler()

# Convenience functions
def get_horoscope(rashi: str, period: str = "daily", language: str = "hi", date: str = None) -> Dict:
    """Get horoscope for a zodiac sign"""
    return horoscope_handler.get_horoscope(rashi, period, language, date)

def get_all_horoscopes(period: str = "daily", language: str = "hi") -> Dict:
    """Get all 12 zodiac signs horoscopes"""
    return horoscope_handler.get_all_rashis(period, language)

def get_rashi_by_date(day: int, month: int, language: str = "hi") -> str:
    """Get zodiac sign by birth date"""
    return horoscope_handler.get_rashi_by_date(day, month, language)

def get_compatibility(rashi1: str, rashi2: str, language: str = "hi") -> Dict:
    """Get compatibility between two signs"""
    return horoscope_handler.get_compatibility(rashi1, rashi2, language)

def format_telegram(horoscope_data: Dict) -> str:
    """Format for Telegram"""
    return horoscope_handler.format_for_telegram(horoscope_data)

def format_all_telegram(all_data: Dict, language: str = "hi") -> str:
    """Format all rashis for Telegram"""
    return horoscope_handler.format_all_for_telegram(all_data, language)

def format_web(horoscope_data: Dict) -> str:
    """Format for web"""
    return horoscope_handler.format_for_web(horoscope_data)


if __name__ == "__main__":
    print("🧪 Testing Horoscope Handler...")
    result = get_horoscope("मेष", "daily", "hi")
    print(f"Rashi: {result['rashi']}")
    print(f"Prediction: {result['prediction'][:100]}...")
    print(f"\nTelegram Format:")
    print(format_telegram(result))
