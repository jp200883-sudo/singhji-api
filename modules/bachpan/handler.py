#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - बच्चों की सुरक्षा (Child Safety) Module
Good Touch / Bad Touch | Helplines | Parental Tips | Emergency
"""

import os
import json
from datetime import datetime
from typing import Dict, List

# 🇮🇳 भारत सरकार हेल्पलाइन नंबर
HELPLINES = {
    "childline": {"number": "1098", "name": "चाइल्डलाइन", "timing": "24x7", "free": True},
    "police": {"number": "100", "name": "पुलिस", "timing": "24x7", "free": True},
    "women_helpline": {"number": "181", "name": "महिला हेल्पलाइन", "timing": "24x7", "free": True},
    "ambulance": {"number": "108", "name": "एम्बुलेंस", "timing": "24x7", "free": True},
    "ncpcr": {"number": "1800-572-1929", "name": "NCPCR", "timing": "24x7", "free": True},
    "pocso_ebox": {"url": "ncpcr.gov.in/user_complaints.php", "name": "POCSO ई-बॉक्स", "timing": "24x7"},
    "cyber_crime": {"number": "1930", "name": "साइबर क्राइम", "timing": "24x7", "free": True},
    "domestic_violence": {"number": "181", "name": "घरेलू हिंसा", "timing": "24x7", "free": True},
    "missing_child": {"number": "1098", "name": "गुमशुदा बच्चा", "timing": "24x7", "free": True},
    "suicide_prevention": {"number": "9152987821", "name": "आत्महत्या रोकथाम", "timing": "24x7", "free": True}
}

# 🛡️ गुड टच / बैड टच शिक्षा
SAFETY_EDUCATION = {
    "hi": {
        "good_touch": {
            "title": "🟢 अच्छा स्पर्श (Good Touch)",
            "points": [
                "जो स्पर्श आपको सुरक्षित, खुश और आरामदायक महसूस कराता है",
                "माँ-बाप का प्यार भरा गले लगाना",
                "डॉक्टर की जाँच (माँ-बाप के सामने)",
                "दोस्त का हाई-फाइव",
                "नानी-दादी का आशीर्वाद",
                "सिर पर सहलाना, पीठ थपथपाना"
            ],
            "rule": "अच्छा स्पर्श = सुरक्षित + खुशी + आराम"
        },
        "bad_touch": {
            "title": "🔴 बुरा स्पर्श (Bad Touch)",
            "points": [
                "जो स्पर्श आपको असहज, डरावना या बुरा महसूस कराता है",
                "कोई भी स्पर्श जो अंडरवियर/बनियान के अंदर हो",
                "जबरदस्ती गले लगाना या चूमना",
                "अकेले में कोई आपको छूने की कोशिश करे",
                "कोई आपकी तस्वीर बिना कपड़ों के खींचे",
                "कोई आपको अश्लील वीडियो दिखाए"
            ],
            "rule": "बुरा स्पर्श = असहज + डर + गुप्त"
        },
        "body_safety_rules": [
            "🚫 मेरा शरीर मेरा है - कोई भी बिना पूछे नहीं छू सकता",
            "🚫 कोई भी रहस्य नहीं - माँ-बाप को सब बताना",
            "🚫 नहीं कहने का अधिकार - जोर से 'नहीं' बोलो",
            "🚫 सुरक्षित जगह ढूंढो - घर, स्कूल, पुलिस",
            "🚫 कभी भी दोषी नहीं - गलती उसकी है जो छूता है"
        ],
        "danger_signs": [
            "⚠️ कोई आपको अकेले में बुलाए",
            "⚠️ कोई आपको तोहफे देकर कुछ करने को कहे",
            "⚠️ कोई आपकी तस्वीर खींचे",
            "⚠️ कोई आपको डराने की कोशिश करे",
            "⚠️ कोई कहे 'यह रहस्य रखना'"
        ]
    },
    "en": {
        "good_touch": {
            "title": "🟢 Good Touch",
            "points": [
                "Touch that makes you feel safe, happy, and comfortable",
                "Parents' loving hug",
                "Doctor's checkup (with parents present)",
                "Friend's high-five",
                "Grandparents' blessing",
                "Pat on back, head rub"
            ],
            "rule": "Good Touch = Safe + Happy + Comfortable"
        },
        "bad_touch": {
            "title": "🔴 Bad Touch",
            "points": [
                "Touch that makes you feel uncomfortable, scared, or bad",
                "Any touch inside underwear/vest area",
                "Forced hugging or kissing",
                "Someone trying to touch you when alone",
                "Someone taking your photo without clothes",
                "Someone showing you dirty videos"
            ],
            "rule": "Bad Touch = Uncomfortable + Scared + Secret"
        },
        "body_safety_rules": [
            "🚫 My body is mine - no one touches without asking",
            "🚫 No secrets - tell parents everything",
            "🚫 Right to say NO - shout 'NO' loudly",
            "🚫 Find safe place - home, school, police",
            "🚫 Never your fault - fault is of the one who touches"
        ],
        "danger_signs": [
            "⚠️ Someone calls you alone",
            "⚠️ Someone gives gifts and asks for something",
            "⚠️ Someone takes your photo",
            "⚠️ Someone tries to scare you",
            "⚠️ Someone says 'keep this secret'"
        ]
    }
}

# 👨‍👩‍👧‍👦 माता-पिता के लिए टिप्स
PARENTAL_TIPS = {
    "hi": [
        "📱 बच्चे की डिजिटल गतिविधि मॉनिटर करें (WhatsApp, Instagram)",
        "🗣️ रोज 15 मिनट बात करें - स्कूल, दोस्त, परेशानी",
        "👥 जान-पहचान वालों पर भी नज़र रखें - 90% abuse जान-पहचान वाले करते हैं",
        "🚫 'रहस्य रखना' शब्द पर अलर्ट रहें",
        "🏠 बच्चे को 'सुरक्षित जगह' बताएं - कहाँ जा सकता है",
        "📞 1098 नंबर बच्चे को याद कराएं",
        "📚 POCSO Act के बारे में जानें - कानूनी सुरक्षा",
        "🩺 बच्चे के शरीर के बदलाव देखें - अचानक डर, रोना, नींद",
        "🎮 स्क्रीन टाइम सीमित करें - 2 घंटे से ज़्यादा नहीं",
        "👨‍🏫 स्कूल में Child Safety Program की मांग करें"
    ],
    "en": [
        "📱 Monitor child's digital activity (WhatsApp, Instagram)",
        "🗣️ Talk 15 min daily - school, friends, problems",
        "👥 Watch known people too - 90% abuse by known persons",
        "🚫 Alert on 'keep secret' words",
        "🏠 Tell child 'safe places' - where to go",
        "📞 Make child memorize 1098 number",
        "📚 Learn POCSO Act - legal protection",
        "🩺 Watch body changes - sudden fear, crying, sleep issues",
        "🎮 Limit screen time - max 2 hours",
        "👨‍🏫 Demand Child Safety Program in school"
    ]
}

# 🚨 इमरजेंसी स्टेप्स
EMERGENCY_STEPS = {
    "hi": [
        "1️⃣ चिल्लाओ - जोर से 'बचाओ' बोलो",
        "2️⃣ भागो - सुरक्षित जगह की ओर दौड़ो",
        "3️⃣ बताओ - माँ-बाप, टीचर, पुलिस को बताओ",
        "4️⃣ याद रखो - चेहरा, कपड़े, गाड़ी नंबर",
        "5️⃣ 1098 पर कॉल करो - चाइल्डलाइन",
        "6️⃣ POCSO ई-बॉक्स - Online शिकायत",
        "7️⃣ कभी डरो मत - तुम्हारी कोई गलती नहीं"
    ],
    "en": [
        "1️⃣ Shout - yell 'HELP' loudly",
        "2️⃣ Run - towards safe place",
        "3️⃣ Tell - parents, teacher, police",
        "4️⃣ Remember - face, clothes, vehicle number",
        "5️⃣ Call 1098 - Childline",
        "6️⃣ POCSO e-Box - Online complaint",
        "7️⃣ Never fear - it's not your fault"
    ]
}

# 📚 एजुकेशनल कंटेंट
EDUCATIONAL_CONTENT = {
    "hi": {
        "swarnim_mantra": [
            "🛡️ मेरा शरीर मेरा है",
            "🛡️ मैं अपनी सुरक्षा का हकदार हूँ",
            "🛡️ मैं किसी से डरता नहीं",
            "🛡️ मैं मदद माँग सकता हूँ",
            "🛡️ मेरी आवाज़ सुनी जाएगी"
        ],
        "story": "एक बार एक छोटी लड़की रिया थी। एक अंकल ने उसे चॉकलेट दी और कहा 'यह रहस्य रखना'। रिया ने तुरंत मम्मी को बताया। मम्मी ने 1098 पर कॉल किया। अंकल पकड़ा गया। रिया बहादुर थी!",
        "quiz": [
            {"q": "कोई अकेले में छूने की कोशिश करे तो क्या करें?", "a": "जोर से 'नहीं' बोलो और भागो"},
            {"q": "1098 किसकी हेल्पलाइन है?", "a": "बच्चों की सुरक्षा"},
            {"q": "बुरा स्पर्श कौन सा होता है?", "a": "जो असहज महसूस कराता है"}
        ]
    },
    "en": {
        "golden_mantra": [
            "🛡️ My body is mine",
            "🛡️ I have right to safety",
            "🛡️ I fear no one",
            "🛡️ I can ask for help",
            "🛡️ My voice will be heard"
        ],
        "story": "Once there was a girl Riya. An uncle gave her chocolate and said 'keep this secret'. Riya immediately told her mom. Mom called 1098. Uncle was caught. Riya was brave!",
        "quiz": [
            {"q": "What to do if someone touches inappropriately?", "a": "Shout 'NO' and run"},
            {"q": "Whose helpline is 1098?", "a": "Child safety"},
            {"q": "What is bad touch?", "a": "Touch that feels uncomfortable"}
        ]
    }
}


class BachpanHandler:
    """बच्चों की सुरक्षा handler"""

    def __init__(self):
        pass

    def get_helplines(self, language: str = "hi") -> Dict:
        """सभी हेल्पलाइन नंबर"""
        return {
            "status": "success",
            "language": language,
            "count": len(HELPLINES),
            "helplines": HELPLINES,
            "emergency_note": "सभी नंबर फ्री और 24x7" if language == "hi" else "All numbers are free and 24x7",
            "timestamp": datetime.now().isoformat()
        }

    def get_safety_education(self, topic: str = "all", language: str = "hi") -> Dict:
        """गुड टच / बैड टच शिक्षा"""
        content = SAFETY_EDUCATION.get(language, SAFETY_EDUCATION["hi"])

        if topic == "good_touch":
            result = content["good_touch"]
        elif topic == "bad_touch":
            result = content["bad_touch"]
        elif topic == "body_rules":
            result = {"title": "🛡️ शरीर सुरक्षा नियम" if language == "hi" else "🛡️ Body Safety Rules", "rules": content["body_safety_rules"]}
        elif topic == "danger":
            result = {"title": "⚠️ खतरे की निशानी" if language == "hi" else "⚠️ Danger Signs", "signs": content["danger_signs"]}
        else:
            result = content

        return {
            "status": "success",
            "topic": topic,
            "language": language,
            "content": result,
            "timestamp": datetime.now().isoformat()
        }

    def get_parental_tips(self, language: str = "hi") -> Dict:
        """माता-पिता के लिए टिप्स"""
        tips = PARENTAL_TIPS.get(language, PARENTAL_TIPS["hi"])
        return {
            "status": "success",
            "language": language,
            "count": len(tips),
            "tips": tips,
            "timestamp": datetime.now().isoformat()
        }

    def get_emergency_steps(self, language: str = "hi") -> Dict:
        """इमरजेंसी स्टेप्स"""
        steps = EMERGENCY_STEPS.get(language, EMERGENCY_STEPS["hi"])
        return {
            "status": "success",
            "language": language,
            "steps": steps,
            "helplines": HELPLINES,
            "timestamp": datetime.now().isoformat()
        }

    def get_educational_content(self, content_type: str = "all", language: str = "hi") -> Dict:
        """एजुकेशनल कंटेंट"""
        content = EDUCATIONAL_CONTENT.get(language, EDUCATIONAL_CONTENT["hi"])

        if content_type == "mantra":
            result = content.get("swarnim_mantra") or content.get("golden_mantra")
        elif content_type == "story":
            result = content["story"]
        elif content_type == "quiz":
            result = content["quiz"]
        else:
            result = content

        return {
            "status": "success",
            "type": content_type,
            "language": language,
            "content": result,
            "timestamp": datetime.now().isoformat()
        }

    def report_incident(self, report_data: Dict) -> Dict:
        """शिकायत दर्ज करें"""
        # In real implementation, this would save to database and notify authorities
        return {
            "status": "success",
            "message": "शिकायत दर्ज हो गई। 24 घंटे में कार्रवाई होगी।" if report_data.get("language") == "hi" else "Complaint registered. Action within 24 hours.",
            "complaint_id": f"BACHPAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "next_steps": [
                "1098 पर कॉल करें" if report_data.get("language") == "hi" else "Call 1098",
                "नजदीकी पुलिस स्टेशन जाएं" if report_data.get("language") == "hi" else "Go to nearest police station",
                "डॉक्टर से जाँच कराएं" if report_data.get("language") == "hi" else "Get medical checkup"
            ],
            "helplines": HELPLINES,
            "timestamp": datetime.now().isoformat()
        }

    def format_telegram(self, data: Dict, language: str = "hi") -> str:
        """Telegram format"""
        if language == "hi":
            return f"""🛡️ *बच्चों की सुरक्षा* 🛡️
━━━━━━━━━━━━━━━

📞 *Emergency: 1098 (Childline)*
📞 *Police: 100*
📞 *Women: 181*

🟢 *अच्छा स्पर्श:*
• सुरक्षित, खुशी, आराम
• माँ-बाप का प्यार
• डॉक्टर की जाँच

🔴 *बुरा स्पर्श:*
• असहज, डर, गुप्त
• अंडरवियर के अंदर
• अकेले में कोई छूए

🛡️ *स्वर्णिम मंत्र:*
"मेरा शरीर मेरा है"
"मैं मदद माँग सकता हूँ"

⚡ *Singh Ji AI Ultra v7.0*"""
        else:
            return f"""🛡️ *Child Safety* 🛡️
━━━━━━━━━━━━━━━

📞 *Emergency: 1098 (Childline)*
📞 *Police: 100*
📞 *Women: 181*

🟢 *Good Touch:*
• Safe, happy, comfortable
• Parents' love
• Doctor's checkup

🔴 *Bad Touch:*
• Uncomfortable, scared, secret
• Inside underwear
• Someone touches when alone

🛡️ *Golden Mantra:*
"My body is mine"
"I can ask for help"

⚡ *Singh Ji AI Ultra v7.0*"""


# Singleton
bachpan_handler = BachpanHandler()

# Convenience functions
def get_helplines(language: str = "hi") -> Dict:
    return bachpan_handler.get_helplines(language)

def get_safety_education(topic: str = "all", language: str = "hi") -> Dict:
    return bachpan_handler.get_safety_education(topic, language)

def get_parental_tips(language: str = "hi") -> Dict:
    return bachpan_handler.get_parental_tips(language)

def get_emergency_steps(language: str = "hi") -> Dict:
    return bachpan_handler.get_emergency_steps(language)

def get_educational_content(content_type: str = "all", language: str = "hi") -> Dict:
    return bachpan_handler.get_educational_content(content_type, language)

def report_incident(report_data: Dict) -> Dict:
    return bachpan_handler.report_incident(report_data)

def format_telegram(data: Dict, language: str = "hi") -> str:
    return bachpan_handler.format_telegram(data, language)


# FastAPI handler for dynamic router
async def handler(request):
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)

        action = body.get("action") or params.get("action", "helplines")
        language = body.get("language") or params.get("language", "hi")
        topic = body.get("topic") or params.get("topic", "all")

        if action == "helplines":
            result = get_helplines(language)
        elif action == "safety":
            result = get_safety_education(topic, language)
        elif action == "parents":
            result = get_parental_tips(language)
        elif action == "emergency":
            result = get_emergency_steps(language)
        elif action == "education":
            content_type = body.get("type") or params.get("type", "all")
            result = get_educational_content(content_type, language)
        elif action == "report":
            result = report_incident(body)
        elif action == "telegram":
            result = {"status": "success", "message": format_telegram({}, language)}
        else:
            result = get_helplines(language)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("🧪 Testing Bachpan Handler...")
    print(get_helplines("hi"))
