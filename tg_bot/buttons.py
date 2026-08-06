# tg_bot/buttons.py
# Singh Ji AI Ultra — Telegram Inline Keyboard Buttons

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ==========================================
# MAIN MENU (2-column grid)
# ==========================================
MAIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🌤️ Weather", callback_data="btn_weather"),
     InlineKeyboardButton("📰 News", callback_data="btn_news")],

    [InlineKeyboardButton("🌾 Mandi Bhav", callback_data="btn_mandi"),
     InlineKeyboardButton("🥇 Gold Rate", callback_data="btn_gold")],

    [InlineKeyboardButton("⛽ Fuel Price", callback_data="btn_fuel"),
     InlineKeyboardButton("💰 Tax Calc", callback_data="btn_tax")],

    [InlineKeyboardButton("🔮 Horoscope", callback_data="btn_horoscope"),
     InlineKeyboardButton("💼 Rozgar/Jobs", callback_data="btn_rozgar")],

    [InlineKeyboardButton("💱 Currency", callback_data="btn_currency"),
     InlineKeyboardButton("🔍 Search", callback_data="btn_search")],

    [InlineKeyboardButton("🔤 Translate", callback_data="btn_translate"),
     InlineKeyboardButton("📋 Yojana", callback_data="btn_yojana")],

    [InlineKeyboardButton("📺 SinghJi TV", callback_data="btn_tv"),
     InlineKeyboardButton("🚨 Emergency", callback_data="btn_emergency")],

    [InlineKeyboardButton("💳 UPI Info", callback_data="btn_upi"),
     InlineKeyboardButton("🏛️ Govt Services", callback_data="btn_govt")],

    [InlineKeyboardButton("🛡️ Guard Agent", callback_data="btn_guard"),
     InlineKeyboardButton("📱 Social Agent", callback_data="btn_social")],

    [InlineKeyboardButton("🎤 Voice AI", callback_data="btn_voice"),
     InlineKeyboardButton("🌿 Plant Doctor", callback_data="btn_plant")],

    [InlineKeyboardButton("🤖 AI Chat", callback_data="btn_ai"),
     InlineKeyboardButton("📊 System Status", callback_data="btn_status")],

    # ✅ NEW: KYC + Agent buttons
    [InlineKeyboardButton("📋 KYC Portal", callback_data="btn_kyc"),
     InlineKeyboardButton("🤝 Agent Program", callback_data="btn_agent")],

    [InlineKeyboardButton("🏛️ Gram Panchayat", callback_data="btn_grampanchayat"),
     InlineKeyboardButton("💸 Withdraw", callback_data="btn_withdraw")],

    [InlineKeyboardButton("❓ Help / Commands", callback_data="btn_help")],
])

# ==========================================
# GOVT SERVICES SUBMENU
# ==========================================
GOVT_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🆔 Aadhaar Card", callback_data="govt_aadhaar"),
     InlineKeyboardButton("💳 PAN Card", callback_data="govt_pan")],

    [InlineKeyboardButton("🛂 Passport", callback_data="govt_passport"),
     InlineKeyboardButton("🗳️ Voter ID", callback_data="govt_voter")],

    [InlineKeyboardButton("🍚 Ration Card", callback_data="govt_ration"),
     InlineKeyboardButton("🚗 Driving License", callback_data="govt_dl")],

    [InlineKeyboardButton("🏥 Ayushman Bharat", callback_data="govt_ayushman"),
     InlineKeyboardButton("🌾 PM Kisan", callback_data="govt_pmkisan")],

    [InlineKeyboardButton("📋 KYC करें", callback_data="govt_kyc"),
     InlineKeyboardButton("🤝 Agent बनें", callback_data="govt_agent")],

    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="btn_back")],
])

# ==========================================
# KYC SUBMENU
# ==========================================
KYC_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚀 KYC शुरू करें", callback_data="kyc_start")],
    [InlineKeyboardButton("📊 मेरा KYC स्टेटस", callback_data="kyc_status")],
    [InlineKeyboardButton("❓ KYC क्या है?", callback_data="kyc_help")],
    [InlineKeyboardButton("⬅️ वापस", callback_data="btn_back")],
])

# ==========================================
# AGENT SUBMENU
# ==========================================
AGENT_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Agent बनें", callback_data="agent_register")],
    [InlineKeyboardButton("📊 Agent Dashboard", callback_data="agent_dashboard")],
    [InlineKeyboardButton("📎 मेरा Referral Link", callback_data="agent_referral")],
    [InlineKeyboardButton("💸 पैसे निकालें", callback_data="agent_withdraw")],
    [InlineKeyboardButton("⬅️ वापस", callback_data="btn_back")],
])

# ==========================================
# GRAM PANCHAYAT SUBMENU
# ==========================================
GP_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📜 जाति प्रमाण पत्र", callback_data="gp_caste")],
    [InlineKeyboardButton("🏠 निवास प्रमाण पत्र", callback_data="gp_residence")],
    [InlineKeyboardButton("💍 विवाह प्रमाण पत्र", callback_data="gp_marriage")],
    [InlineKeyboardButton("🌾 किसान पंजीकरण", callback_data="gp_farmer")],
    [InlineKeyboardButton("💧 पानी कनेक्शन", callback_data="gp_water")],
    [InlineKeyboardButton("⚡ बिजली कनेक्शन", callback_data="gp_electricity")],
    [InlineKeyboardButton("⬅️ वापस", callback_data="btn_back")],
])

# ==========================================  
# GOVT SERVICE DETAILS (for callback handler)
# ==========================================
GOVT_SERVICES = {
    "govt_aadhaar": {
        "title": "🆔 Aadhaar Card",
        "phone": "1947",
        "website": "uidai.gov.in",
        "info": "Aadhaar enrollment, update, and download services"
    },
    "govt_pan": {
        "title": "💳 PAN Card",
        "phone": "1800-180-1961",
        "website": "incometaxindia.gov.in",
        "info": "PAN application, correction, and status tracking"
    },
    "govt_passport": {
        "title": "🛂 Passport",
        "phone": "1800-258-1800",
        "website": "passportindia.gov.in",
        "info": "Passport application, renewal, and appointment booking"
    },
    "govt_voter": {
        "title": "🗳️ Voter ID",
        "phone": "1950",
        "website": "nvsp.in",
        "info": "Voter registration, correction, and EPIC download"
    },
    "govt_ration": {
        "title": "🍚 Ration Card",
        "phone": "1967",
        "website": "nfsa.gov.in",
        "info": "Ration card application and beneficiary status"
    },
    "govt_dl": {
        "title": "🚗 Driving License",
        "phone": "1800-180-2066",
        "website": "parivahan.gov.in",
        "info": "DL application, renewal, and test booking"
    },
    "govt_ayushman": {
        "title": "🏥 Ayushman Bharat",
        "phone": "14555",
        "website": "pmjay.gov.in",
        "info": "Health insurance card and hospital locator"
    },
    "govt_pmkisan": {
        "title": "🌾 PM Kisan Samman Nidhi",
        "phone": "155261",
        "website": "pmkisan.gov.in",
        "info": "Farmer registration and beneficiary status"
    },
}
