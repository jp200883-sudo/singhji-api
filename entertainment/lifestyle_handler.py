"""
🍔 Singh Ji AI Ultra — Lifestyle Hub Handler
Phase 3: Food, Fitness, Shopping, Home, Fashion, Ayurveda, Pet, Vehicle
"""
from fastapi import APIRouter, Query, UploadFile, File
from typing import Optional, List
import random
import json

router = APIRouter(prefix="/lifestyle", tags=["Lifestyle"])

# ========== 🍕 FOOD & RECIPES ==========
INDIAN_RECIPES = {
    "paneer_tikka": {"name": "Paneer Tikka", "time": "30 min", "difficulty": "Easy", "calories": 280, "ingredients": ["Paneer", "Yogurt", "Spices", "Bell Pepper"], "steps": ["Marinate paneer", "Skewer veggies", "Grill 15 min"], "region": "North India", "diet": "Vegetarian"},
    "butter_chicken": {"name": "Butter Chicken", "time": "45 min", "difficulty": "Medium", "calories": 450, "ingredients": ["Chicken", "Tomato", "Cream", "Butter", "Spices"], "steps": ["Marinate chicken", "Cook gravy", "Simmer 20 min"], "region": "Punjab", "diet": "Non-Veg"},
    "dosa": {"name": "Masala Dosa", "time": "40 min", "difficulty": "Medium", "calories": 180, "ingredients": ["Rice Batter", "Potato", "Onion", "Mustard Seeds"], "steps": ["Ferment batter", "Make potato filling", "Spread & cook dosa"], "region": "South India", "diet": "Vegetarian"},
    "chole_bhature": {"name": "Chole Bhature", "time": "50 min", "difficulty": "Medium", "calories": 520, "ingredients": ["Chickpeas", "Flour", "Spices", "Oil"], "steps": ["Soak & boil chickpeas", "Make bhature dough", "Fry bhature"], "region": "Delhi", "diet": "Vegetarian"},
    "biryani": {"name": "Hyderabadi Biryani", "time": "90 min", "difficulty": "Hard", "calories": 600, "ingredients": ["Rice", "Chicken/Mutton", "Saffron", "Fried Onions"], "steps": ["Marinate meat", "Parboil rice", "Layer & dum cook"], "region": "Hyderabad", "diet": "Non-Veg"},
    "rajma_chawal": {"name": "Rajma Chawal", "time": "40 min", "difficulty": "Easy", "calories": 350, "ingredients": ["Kidney Beans", "Rice", "Tomato", "Onion"], "steps": ["Boil rajma", "Make masala gravy", "Serve with rice"], "region": "North India", "diet": "Vegetarian"},
    "pav_bhaji": {"name": "Pav Bhaji", "time": "25 min", "difficulty": "Easy", "calories": 320, "ingredients": ["Mixed Vegetables", "Pav Bread", "Butter", "Pav Bhaji Masala"], "steps": ["Boil & mash veggies", "Cook with masala", "Toast pav in butter"], "region": "Mumbai", "diet": "Vegetarian"},
    "dal_makhani": {"name": "Dal Makhani", "time": "60 min", "difficulty": "Medium", "calories": 380, "ingredients": ["Black Lentils", "Kidney Beans", "Cream", "Butter"], "steps": ["Soak lentils overnight", "Pressure cook", "Simmer with cream"], "region": "Punjab", "diet": "Vegetarian"},
}

DIET_PLANS = {
    "weight_loss": {"name": "Weight Loss", "daily_calories": 1500, "meals": {"breakfast": "Oats + Fruits", "lunch": "Grilled Chicken + Salad", "dinner": "Dal + Roti (1)", "snacks": "Nuts / Green Tea"}},
    "muscle_gain": {"name": "Muscle Gain", "daily_calories": 2800, "meals": {"breakfast": "Eggs + Banana + Peanut Butter", "lunch": "Rice + Chicken + Dal", "dinner": "Fish + Vegetables", "snacks": "Protein Shake + Dry Fruits"}},
    "diabetic": {"name": "Diabetic Friendly", "daily_calories": 1800, "meals": {"breakfast": "Besan Cheela", "lunch": "Brown Rice + Dal + Sabzi", "dinner": "Roti + Paneer + Salad", "snacks": "Sprouts / Buttermilk"}},
    "heart_healthy": {"name": "Heart Healthy", "daily_calories": 2000, "meals": {"breakfast": "Fruit Salad + Yogurt", "lunch": "Grilled Fish + Quinoa", "dinner": "Vegetable Soup + Roti", "snacks": "Almonds / Green Tea"}},
}

@router.get("/food/recipes")
def get_recipes(category: Optional[str] = Query(None, description="Vegetarian / Non-Veg / All")):
    """🍕 सभी रेसिपी देखें — Browse All Recipes"""
    recipes = list(INDIAN_RECIPES.values())
    if category and category.lower() != "all":
        recipes = [r for r in recipes if r["diet"].lower() == category.lower()]
    return {"status": "success", "count": len(recipes), "recipes": recipes}

@router.get("/food/recipe/{recipe_id}")
def get_recipe_detail(recipe_id: str):
    """📖 एक रेसिपी की डिटेल — Recipe Detail"""
    recipe = INDIAN_RECIPES.get(recipe_id)
    if not recipe:
        return {"status": "error", "message": "Recipe not found"}
    return {"status": "success", "recipe": recipe}

@router.get("/food/search")
def search_recipes(query: str = Query(..., description="Recipe search query")):
    """🔍 रेसिपी खोजें — Search Recipes"""
    results = [r for r in INDIAN_RECIPES.values() if query.lower() in r["name"].lower() or query.lower() in r["region"].lower()]
    return {"status": "success", "query": query, "count": len(results), "recipes": results}

@router.get("/food/diet-plan/{plan_type}")
def get_diet_plan(plan_type: str):
    """🥗 डाइट प्लान — Get Diet Plan"""
    plan = DIET_PLANS.get(plan_type)
    if not plan:
        return {"status": "error", "message": "Plan not found", "available": list(DIET_PLANS.keys())}
    return {"status": "success", "plan": plan}

@router.get("/food/ai-chef")
def ai_chef(ingredients: str = Query(..., description="Comma separated ingredients")):
    """👨‍🍳 AI Chef — Recipe from available ingredients"""
    user_ing = [i.strip().lower() for i in ingredients.split(",")]
    matched = []
    for rid, recipe in INDIAN_RECIPES.items():
        match_count = sum(1 for ing in recipe["ingredients"] if any(ui in ing.lower() for ui in user_ing))
        if match_count >= 2:
            matched.append({"recipe_id": rid, "match_score": match_count, **recipe})
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return {"status": "success", "ingredients": user_ing, "suggestions": matched[:3]}

# ========== 🏋️ FITNESS & HEALTH ==========
WORKOUTS = {
    "beginner": {"name": "Beginner Full Body", "duration": "20 min", "exercises": ["Jumping Jacks (30 sec)", "Push-ups (10 reps)", "Squats (15 reps)", "Plank (20 sec)", "Lunges (10 each leg)"]},
    "intermediate": {"name": "Intermediate Strength", "duration": "40 min", "exercises": ["Burpees (15 reps)", "Pull-ups (8 reps)", "Deadlifts (12 reps)", "Bench Press (10 reps)", "Mountain Climbers (30 sec)"]},
    "advanced": {"name": "Advanced HIIT", "duration": "30 min", "exercises": ["Box Jumps (20 reps)", "Clean & Jerk (10 reps)", "Sprint Intervals (5 rounds)", "Battle Ropes (1 min)", "Tire Flips (10 reps)"]},
    "yoga": {"name": "Morning Yoga Flow", "duration": "25 min", "exercises": ["Surya Namaskar (5 rounds)", "Tadasana (1 min)", "Vrikshasana (30 sec each)", "Bhujangasana (30 sec)", "Shavasana (5 min)"]},
}

@router.get("/fitness/workouts")
def get_workouts(level: Optional[str] = Query(None, description="beginner / intermediate / advanced / yoga")):
    """🏋️ वर्कआउट प्लान — Workout Plans"""
    if level:
        w = WORKOUTS.get(level)
        return {"status": "success", "workout": w} if w else {"status": "error", "available": list(WORKOUTS.keys())}
    return {"status": "success", "workouts": WORKOUTS}

@router.get("/fitness/bmi")
def calculate_bmi(weight: float = Query(..., description="Weight in kg"), height: float = Query(..., description="Height in cm")):
    """📊 BMI कैलकुलेटर — BMI Calculator"""
    h_m = height / 100
    bmi = round(weight / (h_m ** 2), 1)
    if bmi < 18.5: category = "Underweight — खाओ पियो मौज करो!"
    elif bmi < 25: category = "Normal — बढ़िया!"
    elif bmi < 30: category = "Overweight — थोड़ा कम खाओ!"
    else: category = "Obese — Gym जाओ अभी!"
    return {"status": "success", "bmi": bmi, "category": category, "tip": f"Target weight: {round(22.5 * h_m**2, 1)} kg"}

@router.get("/fitness/calories")
def calorie_tracker(food_items: str = Query(..., description="Comma separated food items")):
    """🔥 कैलोरी ट्रैकर — Calorie Tracker"""
    CAL_DB = {"roti": 80, "rice": 130, "dal": 120, "paneer": 265, "chicken": 239, "egg": 155, "dosa": 180, "idli": 60, "samosa": 260, "pizza": 266}
    items = [i.strip().lower() for i in food_items.split(",")]
    total = 0
    breakdown = []
    for item in items:
        cal = CAL_DB.get(item, random.randint(50, 300))
        total += cal
        breakdown.append({"item": item.title(), "calories": cal})
    return {"status": "success", "total_calories": total, "breakdown": breakdown, "burn_tip": f"Burn this: {round(total/10)} min running or {round(total/8)} min cycling"}

# ========== 🛒 SHOPPING DEALS ==========
DEALS = [
    {"id": 1, "title": "iPhone 16 Pro Max", "original": 159900, "discount": 139900, "platform": "Flipkart", "category": "Electronics", "url": "https://flipkart.com", "expires": "2 days"},
    {"id": 2, "title": "Noise Smartwatch", "original": 4999, "discount": 1999, "platform": "Amazon", "category": "Electronics", "url": "https://amazon.in", "expires": "Today"},
    {"id": 3, "title": "Nike Running Shoes", "original": 8999, "discount": 4499, "platform": "Myntra", "category": "Fashion", "url": "https://myntra.com", "expires": "3 days"},
    {"id": 4, "title": "LG 1.5 Ton AC", "original": 45990, "discount": 32990, "platform": "Flipkart", "category": "Home", "url": "https://flipkart.com", "expires": "5 days"},
    {"id": 5, "title": "Samsung 55" 4K TV", "original": 89990, "discount": 64990, "platform": "Amazon", "category": "Electronics", "url": "https://amazon.in", "expires": "1 day"},
    {"id": 6, "title": "Patanjali Honey 1kg", "original": 450, "discount": 320, "platform": "BigBasket", "category": "Grocery", "url": "https://bigbasket.com", "expires": "7 days"},
]

@router.get("/shopping/deals")
def get_deals(category: Optional[str] = Query(None), platform: Optional[str] = Query(None)):
    """🛒 टॉप डील्स — Top Shopping Deals"""
    deals = DEALS
    if category:
        deals = [d for d in deals if d["category"].lower() == category.lower()]
    if platform:
        deals = [d for d in deals if d["platform"].lower() == platform.lower()]
    return {"status": "success", "count": len(deals), "deals": deals}

@router.get("/shopping/compare")
def compare_prices(product: str = Query(..., description="Product name to compare")):
    """🔍 प्राइस कंपेयर — Price Comparison"""
    platforms = ["Amazon", "Flipkart", "Myntra", "Snapdeal", "Tata CLiQ"]
    base_price = random.randint(500, 50000)
    comparisons = []
    for p in platforms:
        discount = random.randint(5, 35)
        price = round(base_price * (1 - discount/100))
        comparisons.append({"platform": p, "price": price, "discount": f"{discount}%", "delivery": f"{random.randint(1,5)} days", "rating": round(random.uniform(3.5, 4.9), 1)})
    comparisons.sort(key=lambda x: x["price"])
    return {"status": "success", "product": product, "best_deal": comparisons[0], "all_prices": comparisons}

@router.get("/shopping/coupons")
def get_coupons(store: Optional[str] = Query(None)):
    """🎟️ कूपन कोड्स — Coupon Codes"""
    COUPONS = [
        {"code": "SINGH50", "store": "Myntra", "discount": "50% OFF", "min_order": 999, "expires": "30 June"},
        {"code": "JIFLAT200", "store": "Swiggy", "discount": "₹200 OFF", "min_order": 499, "expires": "Today"},
        {"code": "BIGSALE", "store": "Amazon", "discount": "10% OFF", "min_order": 500, "expires": "15 July"},
        {"code": "FRESH20", "store": "BigBasket", "discount": "20% OFF", "min_order": 799, "expires": "5 July"},
    ]
    if store:
        return {"status": "success", "coupons": [c for c in COUPONS if store.lower() in c["store"].lower()]}
    return {"status": "success", "coupons": COUPONS}

# ========== 🏠 HOME SERVICES ==========
HOME_SERVICES = [
    {"id": 1, "service": "Plumber", "hindi": "प्लंबर", "price": "₹299", "rating": 4.7, "time": "30 min", "icon": "🔧"},
    {"id": 2, "service": "Electrician", "hindi": "इलेक्ट्रीशियन", "price": "₹249", "rating": 4.8, "time": "20 min", "icon": "⚡"},
    {"id": 3, "service": "AC Repair", "hindi": "एसी रिपेयर", "price": "₹499", "rating": 4.6, "time": "1 hour", "icon": "❄️"},
    {"id": 4, "service": "Carpenter", "hindi": "कारपेंटर", "price": "₹399", "rating": 4.5, "time": "45 min", "icon": "🪚"},
    {"id": 5, "service": "House Cleaning", "hindi": "घर की सफाई", "price": "₹599", "rating": 4.9, "time": "2 hours", "icon": "🧹"},
    {"id": 6, "service": "Pest Control", "hindi": "कीट नियंत्रण", "price": "₹899", "rating": 4.4, "time": "1.5 hours", "icon": "🐜"},
    {"id": 7, "service": "Painter", "hindi": "पेंटर", "price": "₹15/sqft", "rating": 4.6, "time": "2 days", "icon": "🎨"},
    {"id": 8, "service": "RO Repair", "hindi": "RO रिपेयर", "price": "₹349", "rating": 4.7, "time": "40 min", "icon": "💧"},
]

@router.get("/home/services")
def get_home_services():
    """🏠 घर की सेवाएं — Home Services"""
    return {"status": "success", "count": len(HOME_SERVICES), "services": HOME_SERVICES}

@router.get("/home/book/{service_id}")
def book_service(service_id: int, name: str = Query(...), phone: str = Query(...), address: str = Query(...), date: str = Query(...)):
    """📅 सर्विस बुक करें — Book a Service"""
    service = next((s for s in HOME_SERVICES if s["id"] == service_id), None)
    if not service:
        return {"status": "error", "message": "Service not found"}
    booking_id = f"SJ{random.randint(10000, 99999)}"
    return {"status": "success", "booking_id": booking_id, "service": service, "customer": {"name": name, "phone": phone, "address": address, "date": date}, "message": f"Booking confirmed! {service['service']} will arrive on {date}"}

# ========== 💅 FASHION & BEAUTY ==========
FASHION_TRENDS = [
    {"trend": "Kurta with Jeans", "season": "All", "price_range": "₹800-2500", "occasion": "Casual", "image": "👔"},
    {"trend": "Saree with Belt", "season": "Festive", "price_range": "₹2000-8000", "occasion": "Wedding", "image": "🥻"},
    {"trend": "Oversized Hoodies", "season": "Winter", "price_range": "₹1200-4000", "occasion": "Streetwear", "image": "🧥"},
    {"trend": "Traditional Juttis", "season": "All", "price_range": "₹500-2000", "occasion": "Festive", "image": "👞"},
    {"trend": "Minimalist Jewelry", "season": "All", "price_range": "₹300-1500", "occasion": "Daily", "image": "💍"},
]

@router.get("/fashion/trends")
def get_fashion_trends():
    """💅 फैशन ट्रेंड्स — Fashion Trends"""
    return {"status": "success", "trends": FASHION_TRENDS}

@router.get("/fashion/ai-stylist")
def ai_stylist(occasion: str = Query(...), budget: str = Query(...), gender: str = Query("unisex")):
    """👗 AI स्टाइलिस्ट — AI Fashion Stylist"""
    outfits = {
        "wedding": {"men": "Sherwani + Mojari", "women": "Lehenga + Dupatta", "budget": "₹5000-20000"},
        "office": {"men": "Formal Shirt + Trousers", "women": "Kurti + Palazzo", "budget": "₹1500-5000"},
        "party": {"men": "Blazer + Jeans", "women": "Crop Top + Skirt", "budget": "₹2000-8000"},
        "daily": {"men": "T-shirt + Shorts", "women": "Kurta + Jeans", "budget": "₹500-2000"},
    }
    rec = outfits.get(occasion.lower(), {"men": "Casual Wear", "women": "Casual Wear", "budget": "₹1000-3000"})
    gender_key = "men" if gender.lower() in ["male", "men", "m"] else "women" if gender.lower() in ["female", "women", "f"] else "men"
    return {"status": "success", "occasion": occasion, "budget": budget, "recommendation": rec[gender_key], "estimated_price": rec["budget"], "tip": "Add accessories to complete the look!"}

# ========== 🌿 AYURVEDA & WELLNESS ==========
AYURVEDA_REMEDIES = [
    {"ailment": "Cold & Cough", "hindi": "सर्दी-खांसी", "remedy": "Tulsi + Ginger + Honey tea, 2x daily", "ingredients": ["Tulsi leaves", "Ginger", "Honey", "Warm water"], "dosha": "Kapha"},
    {"ailment": "Acidity", "hindi": "एसिडिटी", "remedy": "Saunf (fennel) water after meals", "ingredients": ["Saunf", "Warm water"], "dosha": "Pitta"},
    {"ailment": "Hair Fall", "hindi": "बाल झड़ना", "remedy": "Amla + Reetha + Shikakai powder wash", "ingredients": ["Amla powder", "Reetha", "Shikakai"], "dosha": "Vata"},
    {"ailment": "Insomnia", "hindi": "अनिद्रा", "remedy": "Warm milk + Ashwagandha before bed", "ingredients": ["Milk", "Ashwagandha powder"], "dosha": "Vata"},
    {"ailment": "Joint Pain", "hindi": "जोड़ों का दर्द", "remedy": "Turmeric + Ginger paste with warm mustard oil massage", "ingredients": ["Turmeric", "Ginger", "Mustard oil"], "dosha": "Vata"},
    {"ailment": "Stress", "hindi": "तनाव", "remedy": "Brahmi tea + Pranayama daily", "ingredients": ["Brahmi leaves", "Water"], "dosha": "All"},
]

@router.get("/ayurveda/remedies")
def get_remedies(ailment: Optional[str] = Query(None)):
    """🌿 आयुर्वेदिक नुस्खे — Ayurvedic Remedies"""
    if ailment:
        results = [r for r in AYURVEDA_REMEDIES if ailment.lower() in r["ailment"].lower() or ailment.lower() in r["hindi"]]
        return {"status": "success", "results": results}
    return {"status": "success", "remedies": AYURVEDA_REMEDIES}

@router.get("/ayurveda/dosha-quiz")
def dosha_quiz(answers: str = Query(..., description="v/p/k scores comma separated, e.g. 5,3,2")):
    """🧘 दोष टेस्ट — Dosha Quiz Result"""
    try:
        v, p, k = map(int, answers.split(","))
        scores = {"Vata": v, "Pitta": p, "Kapha": k}
        dominant = max(scores, key=scores.get)
        profiles = {
            "Vata": {"traits": "Creative, energetic, anxious", "diet": "Warm, cooked foods. Avoid cold/raw", "lifestyle": "Regular routine, oil massage, early sleep"},
            "Pitta": {"traits": "Sharp, determined, irritable", "diet": "Cool, sweet foods. Avoid spicy/sour", "lifestyle": "Meditation, nature walks, avoid heat"},
            "Kapha": {"traits": "Calm, loyal, sluggish", "diet": "Light, warm foods. Avoid heavy/oily", "lifestyle": "Exercise daily, wake early, stay active"},
        }
        return {"status": "success", "dominant_dosha": dominant, "profile": profiles[dominant], "all_scores": scores}
    except:
        return {"status": "error", "message": "Send answers as v,p,k (e.g. 5,3,2)"}

@router.get("/ayurveda/yoga")
def yoga_guide(level: str = Query("beginner", description="beginner/intermediate/advanced")):
    """🧘 योग गाइड — Yoga Guide"""
    YOGA = {
        "beginner": {"asanas": ["Tadasana", "Vrikshasana", "Balasana", "Shavasana"], "duration": "15 min", "focus": "Flexibility & Relaxation"},
        "intermediate": {"asanas": ["Surya Namaskar", "Trikonasana", "Bhujangasana", "Dhanurasana"], "duration": "30 min", "focus": "Strength & Balance"},
        "advanced": {"asanas": ["Shirshasana", "Sarvangasana", "Padmasana", "Mayurasana"], "duration": "45 min", "focus": "Mastery & Control"},
    }
    return {"status": "success", "level": level, "guide": YOGA.get(level, YOGA["beginner"])}

# ========== 🐾 PET CARE ==========
PET_SERVICES = [
    {"id": 1, "service": "Vet Consultation", "hindi": "पशु चिकित्सक", "price": "₹499", "type": "Health", "icon": "🩺"},
    {"id": 2, "service": "Pet Grooming", "hindi": "पालतू सौंदर्य", "price": "₹799", "type": "Grooming", "icon": "✂️"},
    {"id": 3, "service": "Dog Walking", "hindi": "कुत्ते को घुमाना", "price": "₹199/hr", "type": "Care", "icon": "🦮"},
    {"id": 4, "service": "Pet Boarding", "hindi": "पालतू बोर्डिंग", "price": "₹599/day", "type": "Boarding", "icon": "🏠"},
    {"id": 5, "service": "Pet Food Delivery", "hindi": "पालतू खाना", "price": "₹299+", "type": "Food", "icon": "🍖"},
]

@router.get("/pet/services")
def get_pet_services():
    """🐾 पालतू सेवाएं — Pet Services"""
    return {"status": "success", "services": PET_SERVICES}

@router.get("/pet/vet-finder")
def vet_finder(city: str = Query(..., description="Your city")):
    """🩺 वेट फाइंडर — Find a Vet"""
    vets = [
        {"name": f"Dr. Sharma Pet Clinic, {city}", "phone": "+91-98765-43210", "rating": 4.8, "specialty": "Dogs & Cats", "hours": "9 AM - 8 PM"},
        {"name": f"City Animal Hospital, {city}", "phone": "+91-98765-43211", "rating": 4.6, "specialty": "All Pets", "hours": "24x7"},
        {"name": f"Paws & Care, {city}", "phone": "+91-98765-43212", "rating": 4.9, "specialty": "Exotic Pets", "hours": "10 AM - 7 PM"},
    ]
    return {"status": "success", "city": city, "vets": vets}

# ========== 🚗 VEHICLE CARE ==========
VEHICLE_SERVICES = [
    {"id": 1, "service": "Car Service", "hindi": "कार सर्विस", "price": "₹2499", "duration": "4 hours", "icon": "🔧"},
    {"id": 2, "service": "Bike Service", "hindi": "बाइक सर्विस", "price": "₹899", "duration": "2 hours", "icon": "🏍️"},
    {"id": 3, "service": "Car Wash", "hindi": "कार धुलाई", "price": "₹399", "duration": "1 hour", "icon": "🚿"},
    {"id": 4, "service": "Tire Change", "hindi": "टायर बदलना", "price": "₹1500", "duration": "30 min", "icon": "🛞"},
    {"id": 5, "service": "Battery Check", "hindi": "बैटरी चेक", "price": "₹199", "duration": "15 min", "icon": "🔋"},
    {"id": 6, "service": "Insurance Renewal", "hindi": "बीमा नवीनीकरण", "price": "₹2500+", "duration": "Instant", "icon": "📋"},
]

FUEL_PRICES = {
    "Delhi": {"petrol": 96.72, "diesel": 89.62, "cng": 76.50},
    "Mumbai": {"petrol": 106.31, "diesel": 94.27, "cng": 80.00},
    "Chennai": {"petrol": 102.63, "diesel": 94.24, "cng": 78.50},
    "Kolkata": {"petrol": 106.03, "diesel": 92.76, "cng": 79.00},
    "Bangalore": {"petrol": 101.94, "diesel": 87.89, "cng": 77.00},
    "Kanpur": {"petrol": 96.50, "diesel": 89.30, "cng": 75.50},
    "Lucknow": {"petrol": 96.80, "diesel": 89.50, "cng": 76.00},
}

@router.get("/vehicle/services")
def get_vehicle_services():
    """🚗 वाहन सेवाएं — Vehicle Services"""
    return {"status": "success", "services": VEHICLE_SERVICES}

@router.get("/vehicle/fuel-price/{city}")
def fuel_price(city: str):
    ""️⛽ पेट्रोल-डीज़ल रेट — Fuel Prices"""
    prices = FUEL_PRICES.get(city.title())
    if not prices:
        return {"status": "error", "message": "City not found", "available_cities": list(FUEL_PRICES.keys())}
    return {"status": "success", "city": city.title(), "prices": prices, "updated": "Today 6 AM"}

@router.get("/vehicle/mechanic")
def find_mechanic(city: str = Query(...), vehicle_type: str = Query("car")):
    """🔧 मैकेनिक खोजें — Find Mechanic"""
    mechanics = [
        {"name": f"Singh Ji Motors, {city}", "phone": "+91-98765-55555", "rating": 4.9, "specialty": "All Cars", "available": "Now"},
        {"name": f"Speed Auto Care, {city}", "phone": "+91-98765-55556", "rating": 4.7, "specialty": "Luxury Cars", "available": "30 min"},
        {"name": f"Bharat Garage, {city}", "phone": "+91-98765-55557", "rating": 4.5, "specialty": "Bikes & Scooters", "available": "Now"},
    ]
    return {"status": "success", "city": city, "vehicle_type": vehicle_type, "mechanics": mechanics}

# ========== 🎯 LIFESTYLE HUB ROOT ==========
@router.get("/")
def lifestyle_root():
    """🍔 Lifestyle Hub Root"""
    return {
        "hub": "Lifestyle Hub",
        "status": "🔥 LIVE",
        "modules": ["Food & Recipes", "Fitness & Health", "Shopping Deals", "Home Services", "Fashion & Beauty", "Ayurveda & Wellness", "Pet Care", "Vehicle Care"],
        "endpoints": {
            "food": "/lifestyle/food/recipes, /lifestyle/food/search, /lifestyle/food/ai-chef, /lifestyle/food/diet-plan/{type}",
            "fitness": "/lifestyle/fitness/workouts, /lifestyle/fitness/bmi, /lifestyle/fitness/calories",
            "shopping": "/lifestyle/shopping/deals, /lifestyle/shopping/compare, /lifestyle/shopping/coupons",
            "home": "/lifestyle/home/services, /lifestyle/home/book/{id}",
            "fashion": "/lifestyle/fashion/trends, /lifestyle/fashion/ai-stylist",
            "ayurveda": "/lifestyle/ayurveda/remedies, /lifestyle/ayurveda/dosha-quiz, /lifestyle/ayurveda/yoga",
            "pet": "/lifestyle/pet/services, /lifestyle/pet/vet-finder",
            "vehicle": "/lifestyle/vehicle/services, /lifestyle/vehicle/fuel-price/{city}, /lifestyle/vehicle/mechanic"
    # ✅ main.py इसको import कर रहा है — ये add करो!
def get_lifestyle_content():
    return {
        "status": "live",
        "content": "Lifestyle content loaded!",
        "hub": "Lifestyle Hub",
        "modules": ["Food & Recipes", "Fitness & Health", "Shopping Deals", "Home Services", "Fashion & Beauty", "Ayurveda & Wellness", "Pet Care", "Vehicle Care"]
    }
