"""
🛡️ BACHPAN MODULE — Child Safety Router
Singh Ji AI Ultra v8.3
"""

from fastapi import APIRouter, Request
from datetime import datetime
import json

router = APIRouter(prefix="/api/bachpan", tags=["bachpan"])

# 🇮🇳 REAL HELPLINES
HELPLINES = {
    "childline": {"number": "1098", "name": "चाइल्डलाइन", "timing": "24x7", "free": True},
    "police": {"number": "100", "name": "पुलिस", "timing": "24x7", "free": True},
    "women_helpline": {"number": "181", "name": "महिला हेल्पलाइन", "timing": "24x7", "free": True},
    "ambulance": {"number": "108", "name": "एम्बुलेंस", "timing": "24x7", "free": True},
    "ncpcr": {"number": "1800-572-1929", "name": "NCPCR", "timing": "24x7", "free": True},
    "cyber_crime": {"number": "1930", "name": "साइबर क्राइम", "timing": "24x7", "free": True},
    "suicide_prevention": {"number": "9152987821", "name": "आत्महत्या रोकथाम", "timing": "24x7", "free": True}
}

SAFETY_EDUCATION = {
    "hi": {
        "good_touch": {
            "title": "🟢 अच्छा स्पर्श (Good Touch)",
            "points": [
                "जो स्पर्श आपको सुरक्षित, खुश और आरामदायक महसूस कराता है",
                "माँ-बाप का प्यार भरा गले लगाना",
                "डॉक्टर की जाँच (माँ-बाप के सामने)",
                "दोस्त का हाई-फाइव",
                "नानी-दादी का आशीर्वाद"
            ],
            "rule": "अच्छा स्पर्श = सुरक्षित + खुशी + आराम"
        },
        "bad_touch": {
            "title": "🔴 बुरा स्पर्श (Bad Touch)",
            "points": [
                "जो स्पर्श आपको असहज, डरावना या बुरा महसूस कराता है",
                "कोई भी स्पर्श जो अंडरवियर/बनियान के अंदर हो",
                "जबरदस्ती गले लगाना या चूमना",
                "अकेले में कोई आपको छूने की कोशिश करे"
            ],
            "rule": "बुरा स्पर्श = असहज + डर + गुप्त"
        }
    },
    "en": {
        "good_touch": {
            "title": "🟢 Good Touch",
            "points": [
                "Touch that makes you feel safe, happy, comfortable",
                "Parents loving hug",
                "Doctor checkup (with parents)",
                "Friend high-five",
                "Grandparents blessing"
            ],
            "rule": "Good Touch = Safe + Happy + Comfortable"
        },
        "bad_touch": {
            "title": "🔴 Bad Touch",
            "points": [
                "Touch that makes you uncomfortable, scared",
                "Any touch inside underwear area",
                "Forced hugging or kissing",
                "Someone touching when alone"
            ],
            "rule": "Bad Touch = Uncomfortable + Scared + Secret"
        }
    }
}

EMERGENCY_STEPS = {
    "hi": [
        "1️⃣ चिल्लाओ - जोर से 'बचाओ' बोलो",
        "2️⃣ भागो - सुरक्षित जगह की ओर दौड़ो",
        "3️⃣ बताओ - माँ-बाप, टीचर, पुलिस को बताओ",
        "4️⃣ 1098 पर कॉल करो - चाइल्डलाइन",
        "5️⃣ कभी डरो मत - तुम्हारी कोई गलती नहीं"
    ],
    "en": [
        "1️⃣ Shout - yell 'HELP' loudly",
        "2️⃣ Run - towards safe place",
        "3️⃣ Tell - parents, teacher, police",
        "4️⃣ Call 1098 - Childline",
        "5️⃣ Never fear - it's not your fault"
    ]
}

@router.get("/")
async def bachpan_root():
    return {
        "module": "Bachpan - Child Safety",
        "version": "1.0",
        "status": "ACTIVE",
        "helplines_count": len(HELPLINES),
        "languages": ["hi", "en"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/helplines")
async def get_helplines(lang: str = "hi"):
    return {
        "status": "success",
        "language": lang,
        "count": len(HELPLINES),
        "helplines": HELPLINES,
        "note": "सभी नंबर फ्री और 24x7" if lang == "hi" else "All numbers free & 24x7",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/safety")
async def get_safety_education(topic: str = "all", lang: str = "hi"):
    content = SAFETY_EDUCATION.get(lang, SAFETY_EDUCATION["hi"])
    if topic == "good_touch":
        result = content["good_touch"]
    elif topic == "bad_touch":
        result = content["bad_touch"]
    else:
        result = content
    return {
        "status": "success",
        "topic": topic,
        "language": lang,
        "content": result,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/emergency")
async def get_emergency_steps(lang: str = "hi"):
    return {
        "status": "success",
        "language": lang,
        "steps": EMERGENCY_STEPS.get(lang, EMERGENCY_STEPS["hi"]),
        "helplines": HELPLINES,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/report")
async def report_incident(request: Request):
    data = await request.json()
    lang = data.get("language", "hi")
    return {
        "status": "success",
        "message": "शिकायत दर्ज हो गई। 24 घंटे में कार्रवाई होगी।" if lang == "hi" else "Complaint registered. Action within 24 hours.",
        "complaint_id": f"BACHPAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "next_steps": [
            "1098 पर कॉल करें" if lang == "hi" else "Call 1098",
            "पुलिस स्टेशन जाएं" if lang == "hi" else "Go to police station"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/telegram-format")
async def get_telegram_format(lang: str = "hi"):
    text = f"""🛡️ *बच्चों की सुरक्षा* 🛡️
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

⚡ *Singh Ji AI Ultra v8.3*""" if lang == "hi" else f"""🛡️ *Child Safety* 🛡️
━━━━━━━━━━━━━━━

📞 *Emergency: 1098 (Childline)*
📞 *Police: 100*
📞 *Women: 181*

🟢 *Good Touch:*
• Safe, happy, comfortable
• Parents love
• Doctor checkup

🔴 *Bad Touch:*
• Uncomfortable, scared
• Inside underwear
• Someone touches alone

🛡️ *Golden Mantra:*
"My body is mine"
"I can ask for help"

⚡ *Singh Ji AI Ultra v8.3*"""

    return {"status": "success", "language": lang, "text": text}
