"""
🦁 SINGH JI AI ULTRA — Phase 5: Life Essentials
Emergency SOS | Map Locator | Govt Schemes | Food | Taxi | Music | Games | Safety | Education
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

# ==================== 🚨 EMERGENCY SOS ====================
class EmergencySOS:
    EMERGENCY_NUMBERS = {
        "police": "100", "ambulance": "108", "fire": "101",
        "women_helpline": "1091", "child_helpline": "1098",
        "disaster": "1078", "blood_bank": "1910"
    }

    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {
            "trigger_sos": self.trigger_sos,
            "women_safety": self.women_safety,
            "elderly_care": self.elderly_care,
            "medical_emergency": self.medical_emergency,
            "fake_call": self.fake_call,
            "get_numbers": self.get_numbers,
        }
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def trigger_sos(self, request):
        location = request.get("location", {})
        contacts = request.get("contacts", [])
        return {
            "status": "SOS_TRIGGERED",
            "time": datetime.now().isoformat(),
            "actions": [
                {"type": "call", "to": contacts[0] if contacts else "100"},
                {"type": "sms", "to": contacts, "message": f"🚨 SOS! Location: {location}"},
                {"type": "gps_share", "location": location},
                {"type": "flash_sos", "pattern": "...---..."},
                {"type": "vibrate", "pattern": [500, 200, 500, 200, 500]}
            ],
            "message": "🚨 Help is on the way! Stay calm."
        }

    async def women_safety(self, request):
        return {
            "features": [
                {"name": "Fake Call", "trigger": "button", "action": "Simulate incoming call from 'Papa'"},
                {"name": "Live Location", "trigger": "auto", "action": "Share GPS with family every 5 min"},
                {"name": "Police Near Me", "trigger": "voice", "action": "Find nearest police station"},
                {"name": "Self Defense Tips", "trigger": "video", "action": "Show quick self-defense moves"},
                {"name": "I'm Safe", "trigger": "button", "action": "Notify family you reached safely"}
            ],
            "helpline": self.EMERGENCY_NUMBERS["women_helpline"]
        }

    async def elderly_care(self, request):
        return {
            "features": [
                {"name": "Medicine Reminder", "time": "08:00, 14:00, 20:00", "voice_alert": True},
                {"name": "Doctor Appointment", "alert": "1 day before", "auto_call": True},
                {"name": "Fall Detection", "trigger": "accelerometer", "auto_sos": True},
                {"name": "Daily Check-in", "time": "10:00", "missed_alert": "family"},
                {"name": "Emergency Contact", "trigger": "long_press", "auto_dial": True}
            ],
            "helpline": self.EMERGENCY_NUMBERS["ambulance"]
        }

    async def medical_emergency(self, request):
        return {
            "blood_group_display": True,
            "medical_history_share": True,
            "nearest_hospital": "GPS routed",
            "nearest_blood_bank": self.EMERGENCY_NUMBERS["blood_bank"],
            "auto_call_doctor": True,
            "first_aid_guide": "Voice instructions",
            "ambulance": self.EMERGENCY_NUMBERS["ambulance"]
        }

    async def fake_call(self, request):
        return {"incoming_call": True, "caller": request.get("caller", "Papa"), "use_case": "Women safety / Escape awkward situation"}

    async def get_numbers(self, request):
        return {"emergency_numbers": self.EMERGENCY_NUMBERS}

    async def _default(self, request):
        return {"error": "Unknown action"}


# ==================== 🗺️ MAP LOCATOR ====================
class MapLocator:
    SERVICE_TYPES = {
        "petrol": {"query": "petrol pump near me", "icon": "⛽"},
        "diesel": {"query": "diesel pump near me", "icon": "⛽"},
        "cng": {"query": "CNG station near me", "icon": "🔥"},
        "ev": {"query": "EV charging station near me", "icon": "⚡"},
        "toilet": {"query": "public toilet near me", "icon": "🚽"},
        "hospital": {"query": "hospital near me", "icon": "🏥"},
        "pharmacy": {"query": "pharmacy near me", "icon": "💊"},
        "atm": {"query": "ATM near me", "icon": "🏧"},
        "police": {"query": "police station near me", "icon": "👮"},
        "bank": {"query": "bank near me", "icon": "🏦"},
        "post": {"query": "post office near me", "icon": "📮"},
        "railway": {"query": "railway station near me", "icon": "🚂"},
        "bus": {"query": "bus stop near me", "icon": "🚌"},
        "food": {"query": "restaurant near me", "icon": "🍽️"}
    }

    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"find_nearby": self.find_nearby, "get_all_types": self.get_all_types}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def find_nearby(self, request):
        service_type = request.get("type", "petrol")
        lat = request.get("lat", 0)
        lng = request.get("lng", 0)
        service = self.SERVICE_TYPES.get(service_type, self.SERVICE_TYPES["petrol"])
        maps_url = f"https://www.google.com/maps/search/{service['query']}/@{lat},{lng},15z"
        return {"type": service_type, "icon": service["icon"], "maps_url": maps_url, "features": ["Live navigation", "Distance & ETA", "User ratings", "Open/Closed status", "Contact number"]}

    async def get_all_types(self, request):
        return {"services": self.SERVICE_TYPES}

    async def _default(self, request):
        return {"error": "Unknown action", "types": list(self.SERVICE_TYPES.keys())}


# ==================== 🏛️ GOVT SCHEMES ====================
class GovtSchemes:
    SCHEMES = {
        "pm_kisan": {"name": "PM-KISAN", "name_hi": "प्रधानमंत्री किसान सम्मान निधि", "benefit": "₹6000/year", "eligibility": "Small & marginal farmers", "documents": ["Aadhaar", "Land records", "Bank account"], "apply_link": "https://pmkisan.gov.in"},
        "ayushman_bharat": {"name": "Ayushman Bharat", "name_hi": "आयुष्मान भारत", "benefit": "₹5 lakh health insurance", "eligibility": "BPL families", "documents": ["Aadhaar", "Ration card", "Mobile"], "apply_link": "https://pmjay.gov.in"},
        "pm_awas": {"name": "PM Awas Yojana", "name_hi": "प्रधानमंत्री आवास योजना", "benefit": "Free pucca house + ₹2.5L subsidy", "eligibility": "Homeless", "documents": ["Aadhaar", "Income proof", "Land papers"], "apply_link": "https://pmaymis.gov.in"},
        "jan_dhan": {"name": "PM Jan Dhan Yojana", "name_hi": "प्रधानमंत्री जन धन योजना", "benefit": "Zero balance bank account + ₹1L insurance", "eligibility": "All Indian citizens", "documents": ["Aadhaar", "Photo"], "apply_link": "Bank branch / CSP"},
        "sukanya_samriddhi": {"name": "Sukanya Samriddhi", "name_hi": "सुकन्या समृद्धि योजना", "benefit": "Girl child savings @ 7.6% interest", "eligibility": "Girl child below 10 years", "documents": ["Girl's birth certificate", "Aadhaar", "Photo"], "apply_link": "Post office / Bank"},
        "atal_pension": {"name": "Atal Pension Yojana", "name_hi": "अटल पेंशन योजना", "benefit": "₹1000-5000/month pension after 60", "eligibility": "18-40 years", "documents": ["Aadhaar", "Bank account", "Mobile"], "apply_link": "Bank / Post office"},
        "mudra_loan": {"name": "MUDRA Loan", "name_hi": "मुद्रा लोन", "benefit": "Business loan up to ₹10L", "eligibility": "Small business owners", "documents": ["Aadhaar", "Business proof", "Bank statement"], "apply_link": "Bank / Mudra portal"},
        "ujjwala": {"name": "PM Ujjwala Yojana", "name_hi": "उज्ज्वला योजना", "benefit": "Free LPG connection + subsidy", "eligibility": "BPL women", "documents": ["Aadhaar", "BPL card", "Bank account"], "apply_link": "Gas agency / Online"},
        "saubhagya": {"name": "Saubhagya", "name_hi": "सौभाग्य योजना", "benefit": "Free electricity connection", "eligibility": "Rural unelectrified households", "documents": ["Aadhaar", "Address proof"], "apply_link": "DISCOM office"},
        "jal_jeevan": {"name": "Jal Jeevan Mission", "name_hi": "जल जीवन मिशन", "benefit": "Tap water to every household", "eligibility": "Rural households", "documents": ["Aadhaar", "Address proof"], "apply_link": "Gram Panchayat"}
    }

    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"get_all": self.get_all, "get_scheme": self.get_scheme, "check_eligibility": self.check_eligibility, "search": self.search}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def get_all(self, request):
        return {"total_schemes": len(self.SCHEMES), "schemes": self.SCHEMES}

    async def get_scheme(self, request):
        scheme_id = request.get("scheme_id", "pm_kisan")
        scheme = self.SCHEMES.get(scheme_id, {})
        return {"scheme": scheme} if scheme else {"error": "Scheme not found"}

    async def check_eligibility(self, request):
        scheme_id = request.get("scheme_id", "pm_kisan")
        scheme = self.SCHEMES.get(scheme_id, {})
        return {"scheme": scheme_id, "eligible": True, "message": f"Aap {scheme.get('name', '')} ke liye eligible ho sakte hain!", "next_step": "Documents collect karo aur apply karo!"}

    async def search(self, request):
        query = request.get("query", "").lower()
        results = [s for sid, s in self.SCHEMES.items() if query in sid or query in s.get("name", "").lower() or query in s.get("name_hi", "")]
        return {"query": query, "results": results}

    async def _default(self, request):
        return {"error": "Unknown action", "schemes": list(self.SCHEMES.keys())}


# ==================== 🍲 FOOD ORDER ====================
class FoodOrder:
    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"order_food": self.order_food, "get_recipe": self.get_recipe, "check_ration": self.check_ration}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def order_food(self, request):
        return {"platform": request.get("platform", "zomato"), "item": request.get("item", ""), "status": "redirecting", "payment": "UPI via Singh Ji AI"}

    async def get_recipe(self, request):
        return {"dish": request.get("dish", "Dal Roti"), "ingredients": ["Dal", "Roti", "Chawal", "Sabzi"], "steps": ["Step 1: Dal boil karo", "Step 2: Roti banayo", "Step 3: Serve karo"]}

    async def check_ration(self, request):
        return {"ration_card": request.get("ration_card", ""), "status": "Active", "entitlement": "5kg rice + 5kg wheat + 1kg dal/month"}

    async def _default(self, request):
        return {"error": "Unknown action"}


# ==================== 🚕 TAXI BOOKING ====================
class TaxiBooking:
    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"book_taxi": self.book_taxi, "book_auto": self.book_auto, "check_train": self.check_train, "find_stay": self.find_stay}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def book_taxi(self, request):
        return {"platform": "Ola/Uber", "from": request.get("from", ""), "to": request.get("to", ""), "fare_estimate": "₹150-200", "payment": "UPI"}

    async def book_auto(self, request):
        return {"type": "Auto Rickshaw", "meter_fare": "₹50 base + ₹15/km", "share_auto": "₹20/person"}

    async def check_train(self, request):
        return {"pnr": request.get("pnr", ""), "status": "Confirmed", "train_name": "Rajdhani Express", "platform": "5"}

    async def find_stay(self, request):
        return {"options": [{"type": "Budget Hotel", "price": "₹500-1000"}, {"type": "Dharamshala", "price": "Free-₹200"}, {"type": "Railway Retiring Room", "price": "₹100-300"}]}

    async def _default(self, request):
        return {"error": "Unknown action"}


# ==================== 🎵 MUSIC PLAYER ====================
class MusicPlayer:
    MOOD_PLAYLISTS = {
        "happy": {"songs": ["Kala Chashma", "Lungi Dance", "Badtameez Dil"], "genre": "Bollywood Dance"},
        "sad": {"songs": ["Channa Mereya", "Tum Hi Ho", "Agar Tum Saath Ho"], "genre": "Romantic Sad"},
        "energetic": {"songs": ["Jai Ho", "Sultan", "Dangal"], "genre": "Motivational"},
        "devotional": {"songs": ["Hanuman Chalisa", "Om Jai Jagdish", "Gurbani"], "genre": "Bhajan"},
        "sleep": {"songs": ["Raag Yaman", "Ocean Waves", "Rain Sounds"], "genre": "Relaxing"},
        "workout": {"songs": ["Zinda", "Brothers Anthem", "Sultan"], "genre": "Gym"},
        "focus": {"songs": ["Instrumental", "Lo-fi", "Classical"], "genre": "Study"},
        "romantic": {"songs": ["Tere Bina", "Pehla Nasha", "Tum Se Hi"], "genre": "Love"}
    }

    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"play_mood": self.play_mood, "play_devotional": self.play_devotional, "karaoke": self.karaoke}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def play_mood(self, request):
        mood = request.get("mood", "happy")
        playlist = self.MOOD_PLAYLISTS.get(mood, self.MOOD_PLAYLISTS["happy"])
        return {"mood": mood, "playlist": playlist["songs"], "genre": playlist["genre"], "source": "Jamendo / ccMixter (FREE)"}

    async def play_devotional(self, request):
        deity = request.get("deity", "hanuman")
        return {"type": "Devotional", "deity": deity, "songs": [f"{deity.title()} Chalisa", f"{deity.title()} Aarti"], "source": "FREE streaming"}

    async def karaoke(self, request):
        return {"song": request.get("song", "Kala Chashma"), "lyrics": "Displaying...", "instrumental": "Playing...", "score": "AI will rate!"}

    async def _default(self, request):
        return {"error": "Unknown action", "moods": list(self.MOOD_PLAYLISTS.keys())}


# ==================== 🎮 GAMES HUB ====================
class GamesHub:
    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"get_coding_games": self.get_coding_games, "get_desi_games": self.get_desi_games, "get_brain_games": self.get_brain_games, "parent_control": self.parent_control}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def get_coding_games(self, request):
        age = request.get("age", 10)
        if age < 8: return {"platform": "ScratchJr", "link": "https://scratchjr.org"}
        elif age < 12: return {"platform": "Scratch", "link": "https://scratch.mit.edu"}
        else: return {"platform": "Code.org", "link": "https://code.org"}

    async def get_desi_games(self, request):
        return {"games": [{"name": "Ludo", "players": "2-4"}, {"name": "Carrom", "players": "2-4"}, {"name": "Chess", "players": "2", "ai_opponent": True}, {"name": "Tambola", "players": "Unlimited"}]}

    async def get_brain_games(self, request):
        return {"games": [{"name": "Sudoku"}, {"name": "Crossword", "language": "Hindi/English"}, {"name": "Memory Match"}, {"name": "Math Quiz", "class": "1-12"}, {"name": "GK Quiz", "topic": "India Special"}]}

    async def parent_control(self, request):
        return {"features": [{"name": "Screen Time Limit", "setting": "1-3 hours/day"}, {"name": "Content Filter", "blocks": "Ads, Violence"}, {"name": "Progress Report"}, {"name": "Safe Mode"}]}

    async def _default(self, request):
        return {"error": "Unknown action"}


# ==================== 🛡️ GOOD TOUCH BAD TOUCH ====================
class GoodTouchBadTouch:
    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"get_lessons": self.get_lessons, "take_quiz": self.take_quiz, "trigger_help": self.trigger_help, "parent_dashboard": self.parent_dashboard}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def get_lessons(self, request):
        return {"lessons": [
            {"title": "Safe Touch vs Unsafe Touch", "title_hi": "सेफ टच बनाम अनसेफ टच", "type": "Animated Video", "key_points": ["Good touch feels safe", "Bad touch feels uncomfortable", "Say NO", "Tell parents"]},
            {"title": "My Body, My Rules", "title_hi": "मेरा शरीर, मेरे नियम", "type": "Interactive Story", "key_points": ["Private parts", "No one can touch", "Speak up"]},
            {"title": "NO-GO-TELL", "title_hi": "नहीं-जाओ-बताओ", "type": "Game", "key_points": ["NO to bad touch", "GO away", "TELL parents"]}
        ]}

    async def take_quiz(self, request):
        return {"quiz": [{"question": "If someone touches you and you feel uncomfortable?", "answer": "Say NO and tell parents"}], "badge": "Safety Champion"}

    async def trigger_help(self, request):
        return {"action": "Emergency SOS triggered", "child_helpline": "1098", "message": "Help is coming!", "auto_call": "Parents + Police"}

    async def parent_dashboard(self, request):
        return {"child_progress": "3/4 lessons completed", "safety_score": "85/100", "tips": "Aaj apne bachche se baat karo!"}

    async def _default(self, request):
        return {"error": "Unknown action"}


# ==================== 📚 EDUCATION GURU ====================
class EducationGuru:
    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {"kids_learning": self.kids_learning, "adult_skills": self.adult_skills, "elderly_digital": self.elderly_digital, "exam_prep": self.exam_prep, "skill_courses": self.skill_courses}
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def kids_learning(self, request):
        age = request.get("age", 8)
        return {"age_group": f"{age} years", "subjects": [{"name": "Hindi", "voice_first": True}, {"name": "English", "voice_first": True}, {"name": "Math", "voice_first": True}, {"name": "Science", "video": True}, {"name": "Moral Stories", "language": "Hindi"}], "platforms": ["Khan Academy Kids", "NCERT"]}

    async def adult_skills(self, request):
        return {"courses": [{"name": "Digital Literacy", "duration": "2 weeks"}, {"name": "Financial Literacy", "duration": "1 week"}, {"name": "Entrepreneurship", "duration": "4 weeks"}], "free_platforms": ["SWAYAM", "NPTEL", "Skill India"]}

    async def elderly_digital(self, request):
        return {"lessons": [{"topic": "Phone Chalana", "steps": ["On/Off", "Call karna", "Message padhna"]}, {"topic": "UPI Sikho", "steps": ["App install", "Account link", "Payment karna"]}, {"topic": "Video Call", "steps": ["WhatsApp kholo", "Contact select karo", "Video call dabaoo"]}], "voice_first": True, "large_font": True}

    async def exam_prep(self, request):
        exam = request.get("exam", "ssc")
        return {"exam": exam.upper(), "subjects": ["Math", "Reasoning", "English", "GK", "Current Affairs"], "mock_tests": "Daily free", "free_resources": ["YouTube", "Unacademy Free", "Testbook"]}

    async def skill_courses(self, request):
        return {"courses": [{"name": "Plumbing", "duration": "3 months", "certificate": "NSDC"}, {"name": "Electrician", "duration": "3 months", "certificate": "NSDC"}, {"name": "Tailoring", "duration": "2 months", "certificate": "NSDC"}, {"name": "Driving", "duration": "1 month", "certificate": "RTO"}], "government_free": True, "stipend": "₹500-1500/month"}

    async def _default(self, request):
        return {"error": "Unknown action"}
