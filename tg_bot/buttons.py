"""
📱 tg_bot/buttons.py — Singh Ji AI Ultra v8.3 | 2026
Complete Keyboard + Input Handler
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton

# ==========================================
# MAIN KEYBOARD — ALL MODULES (2026)
# ==========================================

def get_main_keyboard():
    """Complete keyboard with all modules"""
    keyboard = [
        # Row 1: Agriculture
        [KeyboardButton("🌾 Mandi Bhav"), KeyboardButton("🌱 Kisaan Doctor")],
        [KeyboardButton("🌿 Plant ID"), KeyboardButton("💧 Pani")],

        # Row 2: Finance
        [KeyboardButton("🥇 Gold Rate"), KeyboardButton("⛽ Fuel Price")],
        [KeyboardButton("💰 Tax Calc"), KeyboardButton("💱 Currency")],
        [KeyboardButton("🏦 Banking"), KeyboardButton("💳 UPI")],

        # Row 3: News & Info
        [KeyboardButton("📰 News"), KeyboardButton("📡 NewsData")],
        [KeyboardButton("📊 Currents"), KeyboardButton("📋 Daily Report")],
        [KeyboardButton("🔍 Search"), KeyboardButton("🌐 DDG Search")],

        # Row 4: AI & Language
        [KeyboardButton("🤖 AI Chat"), KeyboardButton("🔤 Language")],
        [KeyboardButton("🌍 Language Hub"), KeyboardButton("🗣️ Bhashini")],
        [KeyboardButton("🎙️ Voice"), KeyboardButton("🔊 Voice TTS")],

        # Row 5: Government
        [KeyboardButton("🏛️ Govt Schemes"), KeyboardButton("📜 Scheme Swarm")],
        [KeyboardButton("💼 Rozgar"), KeyboardButton("🚨 Emergency")],
        [KeyboardButton("🚰 Sewer"), KeyboardButton("🎯 Aavishkar")],
        [KeyboardButton("📋 Yojana")],

        # Row 6: Social & Media
        [KeyboardButton("📱 Social Agent"), KeyboardButton("💬 WhatsApp")],
        [KeyboardButton("📘 Facebook"), KeyboardButton("📺 SinghJi TV")],
        [KeyboardButton("🔐 OAuth"), KeyboardButton("🛒 Trolley")],

        # Row 7: System & Agents
        [KeyboardButton("📊 System Status"), KeyboardButton("📈 Analytics")],
        [KeyboardButton("👑 Supreme Agent"), KeyboardButton("🧠 Meta Agent")],
        [KeyboardButton("🛡️ Guard Agent"), KeyboardButton("⚡ Trishul")],

        # Row 8: Transport
        [KeyboardButton("🚆 PNR Status"), KeyboardButton("🚂 Train Tracking")],

        # Row 9: Other
        [KeyboardButton("🔮 Horoscope"), KeyboardButton("🌤️ Weather")],
        [KeyboardButton("🤖 Auto Account"), KeyboardButton("💵 Auto Monetize")],
        [KeyboardButton("📸 Visual AI"), KeyboardButton("📈 Trend Analysis")],

        # Row 10: Help
        [KeyboardButton("❓ Help / Commands")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==========================================
# BUTTON → COMMAND MAP
# ==========================================

BUTTON_COMMAND_MAP = {
    # Agriculture
    "🌾 Mandi Bhav": "/mandi",
    "🌱 Kisaan Doctor": "/kisaan",
    "🌿 Plant ID": "/plant",
    "💧 Pani": "/pani",

    # Finance
    "🥇 Gold Rate": "/gold",
    "⛽ Fuel Price": "/fuel",
    "💰 Tax Calc": "/tax",
    "💱 Currency": "/currency",
    "🏦 Banking": "/banking",
    "💳 UPI": "/upi",

    # News & Info
    "📰 News": "/news",
    "📡 NewsData": "/newsdata",
    "📊 Currents": "/currents",
    "📋 Daily Report": "/dailyreport",
    "🔍 Search": "/search",
    "🌐 DDG Search": "/ddg",

    # AI & Language
    "🤖 AI Chat": "/ai",
    "🔤 Language": "/language",
    "🌍 Language Hub": "/langhub",
    "🗣️ Bhashini": "/bhashini",
    "🎙️ Voice": "/voice",
    "🔊 Voice TTS": "/voicetts",

    # Government
    "🏛️ Govt Schemes": "/govt",
    "📜 Scheme Swarm": "/schemes",
    "💼 Rozgar": "/rozgar",
    "🚨 Emergency": "/emergency",
    "🚰 Sewer": "/sewer",
    "🎯 Aavishkar": "/aavishkar",
    "📋 Yojana": "/yojana",

    # Social & Media
    "📱 Social Agent": "/social",
    "💬 WhatsApp": "/whatsapp",
    "📘 Facebook": "/facebook",
    "📺 SinghJi TV": "/singhjtv",
    "🔐 OAuth": "/oauth",
    "🛒 Trolley": "/trolley",

    # System & Agents
    "📊 System Status": "/status",
    "📈 Analytics": "/analytics",
    "👑 Supreme Agent": "/supreme",
    "🧠 Meta Agent": "/meta",
    "🛡️ Guard Agent": "/guard",
    "⚡ Trishul": "/trishul",

    # Transport
    "🚆 PNR Status": "/pnr",
    "🚂 Train Tracking": "/train",

    # Other
    "🔮 Horoscope": "/horoscope",
    "🌤️ Weather": "/weather",
    "🤖 Auto Account": "/autoaccount",
    "💵 Auto Monetize": "/monetize",
    "📸 Visual AI": "/visual",
    "📈 Trend Analysis": "/trend",

    # Help
    "❓ Help / Commands": "/help",
}


# ==========================================
# BUTTONS THAT NEED USER INPUT
# ==========================================
INPUT_BUTTONS = {
    "weather": ("🌤️ Weather", "City batao! (jaise: Delhi, Mumbai, Kanpur)"),
    "mandi": ("🌾 Mandi Bhav", "State batao! (jaise: UP, Punjab, Haryana)"),
    "tax": ("💰 Tax Calc", "Annual income batao! (jaise: 500000)"),
    "gold": ("🥇 Gold Rate", "City batao! (default: Delhi)"),
    "fuel": ("⛽ Fuel Price", "City batao! (default: Delhi)"),
    "horoscope": ("🔮 Horoscope", "Rashi batao! (jaise: मेष, सिंह, तुला)"),
    "currency": ("💱 Currency", "Format: USD INR 100"),
    "rozgar": ("💼 Rozgar", "Keyword + Country batao! (jaise: software IN)"),
    "search": ("🔍 Search", "Kya search karna hai?"),
    "translate": ("🔤 Translate", "Format: en Namaste kaise ho"),
    "yojana": ("📋 Yojana", "Format: 30 100000 farmer"),
    "tv": ("📺 SinghJi TV", "Category batao! (educational/news/health)"),
    "pnr": ("🚆 PNR Status", "PNR number batao!"),
    "train": ("🚂 Train Tracking", "Train number batao!"),
    "plant": ("🌿 Plant ID", "Plant ki photo bhejo ya naam batao!"),
    "kisaan": ("🌱 Kisaan Doctor", "Problem batao! (jaise: gehu mein keeda)"),
    "ai": ("🤖 AI Chat", "Kya puchna hai?"),
    "language": ("🔤 Language", "Format: en Namaste kaise ho"),
    "bhashini": ("🗣️ Bhashini", "Text batao jo translate karna hai!"),
    "visual": ("📸 Visual AI", "Image bhejo ya prompt batao!"),
    "trend": ("📈 Trend Analysis", "Topic batao! (jaise: crypto, stock)"),
    "autoaccount": ("🤖 Auto Account", "Account type batao!"),
    "monetize": ("💵 Auto Monetize", "Platform batao!"),
}


def button_to_command(text: str) -> str:
    """Button text ko command mein convert kare"""
    return BUTTON_COMMAND_MAP.get(text, text)


def is_input_button(command: str) -> tuple:
    """Check kare ki button ko extra input chahiye ya nahi"""
    cmd_clean = command.replace("/", "").lower()
    if cmd_clean in INPUT_BUTTONS:
        return True, INPUT_BUTTONS[cmd_clean][1]
    return False, ""
