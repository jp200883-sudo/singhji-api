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
    "weather": ("🌤️ Weather", "Enter city name! (e.g., Delhi, Mumbai, Kanpur)"),
    "mandi": ("🌾 Mandi Bhav", "Enter state! (e.g., UP, Punjab, Haryana)"),
    "tax": ("💰 Tax Calc", "Enter annual income! (e.g., 500000)"),
    "gold": ("🥇 Gold Rate", "Enter city! (default: Delhi)"),
    "fuel": ("⛽ Fuel Price", "Enter city! (default: Delhi)"),
    "horoscope": ("🔮 Horoscope", "Enter your zodiac sign! (e.g., Aries, Leo, Taurus)"),
    "currency": ("💱 Currency", "Format: USD INR 100"),
    "rozgar": ("💼 Rozgar", "Enter keyword + country! (e.g., software IN)"),
    "search": ("🔍 Search", "What do you want to search?"),
    "translate": ("🔤 Language", "Format: hi Hello how are you?"),
    "yojana": ("📋 Yojana", "Format: 30 100000 farmer"),
    "tv": ("📺 SinghJi TV", "Enter category! (educational/news/health)"),
    "pnr": ("🚆 PNR Status", "Enter PNR number!"),
    "train": ("🚂 Train Tracking", "Enter train number!"),
    "plant": ("🌿 Plant ID", "Send plant photo or enter name!"),
    "kisaan": ("🌱 Kisaan Doctor", "Describe the problem! (e.g., wheat has insects)"),
    "ai": ("🤖 AI Chat", "What would you like to ask?"),
    "language": ("🔤 Language", "Format: hi Where is the temple?"),
    "bhashini": ("🗣️ Bhashini", "Enter text to translate!"),
    "visual": ("📸 Visual AI", "Send image or enter prompt!"),
    "trend": ("📈 Trend Analysis", "Enter topic! (e.g., crypto, stock)"),
    "autoaccount": ("🤖 Auto Account", "Enter account type!"),
    "monetize": ("💵 Auto Monetize", "Enter platform name!"),
    "govt": ("🏛️ Govt Schemes", "Enter scheme name or category!"),
    "sewer": ("🚰 Sewer", "Enter city and area!"),
    "aavishkar": ("🎯 Aavishkar", "Enter your idea or project details!"),
}


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def button_to_command(text: str) -> str:
    """Convert button text to command"""
    return BUTTON_COMMAND_MAP.get(text, text)


def is_input_button(command: str) -> tuple:
    """Check if button needs extra input"""
    cmd_clean = command.replace("/", "").lower()
    if cmd_clean in INPUT_BUTTONS:
        return True, INPUT_BUTTONS[cmd_clean][1]
    return False, ""


def get_input_prompt(command: str) -> str:
    """Get input prompt for a command"""
    cmd_clean = command.replace("/", "").lower()
    if cmd_clean in INPUT_BUTTONS:
        return INPUT_BUTTONS[cmd_clean][1]
    return "Please enter the required information:"


def get_category_keyboard(category: str):
    """Get keyboard for specific category"""
    categories = {
        "agriculture": ["🌾 Mandi Bhav", "🌱 Kisaan Doctor", "🌿 Plant ID", "💧 Pani"],
        "finance": ["🥇 Gold Rate", "⛽ Fuel Price", "💰 Tax Calc", "💱 Currency"],
        "government": ["🏛️ Govt Schemes", "💼 Rozgar", "🚨 Emergency", "📋 Yojana"],
        "ai": ["🤖 AI Chat", "🔤 Language", "🌍 Language Hub", "🗣️ Bhashini"],
        "social": ["📱 Social Agent", "💬 WhatsApp", "📘 Facebook", "📺 SinghJi TV"],
        "system": ["📊 System Status", "📈 Analytics", "👑 Supreme Agent", "🧠 Meta Agent"],
    }
    
    buttons = categories.get(category.lower(), ["❓ Help / Commands"])
    keyboard = [[KeyboardButton(btn)] for btn in buttons]
    keyboard.append([KeyboardButton("🔙 Main Menu")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_paginated_keyboard(page: int = 0, per_page: int = 8):
    """Get paginated keyboard for many buttons"""
    all_buttons = list(BUTTON_COMMAND_MAP.keys())
    start = page * per_page
    end = start + per_page
    page_buttons = all_buttons[start:end]
    
    keyboard = [[KeyboardButton(btn)] for btn in page_buttons]
    
    # Add navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(KeyboardButton("⬅️ Previous"))
    if end < len(all_buttons):
        nav_row.append(KeyboardButton("➡️ Next"))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([KeyboardButton("❓ Help / Commands")])
    keyboard.append([KeyboardButton("🔙 Main Menu")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==========================================
# HELP TEXT
# ==========================================

HELP_TEXT = """
🌟 *Singh Ji AI Ultra v8.3 - Help* 🌟

📌 *Main Features:*
🌾 *Agriculture* - Mandi rates, Kisaan Doctor, Plant ID
💰 *Finance* - Gold rates, Tax, Currency exchange
🏛️ *Government* - Schemes, Jobs, Emergency
🤖 *AI* - Chat, Translation, Voice

💡 *Tips:*
• Press buttons or type commands
• Most features are free
• Available 24/7

❓ *Questions?* Type /help
"""


# ==========================================
# ERROR MESSAGES
# ==========================================

ERROR_MESSAGES = {
    "no_input": "⚠️ Please enter the required information!",
    "invalid": "❌ Invalid format! Please enter correctly.",
    "not_found": "🔍 Data not found! Please try again.",
    "server": "⏳ Server busy! Please try after some time.",
    "auth": "🔐 Login required! Please /login.",
    "timeout": "⌛ Timeout! Please try again.",
    "generic": "❌ Something went wrong! Please try again.",
}

# ==========================================
# MAIN MENU CATEGORY BUTTONS
# ==========================================

CATEGORY_MENU = [
    [KeyboardButton("🌾 Agriculture"), KeyboardButton("💰 Finance")],
    [KeyboardButton("🏛️ Government"), KeyboardButton("🤖 AI & Language")],
    [KeyboardButton("📱 Social"), KeyboardButton("📊 System")],
    [KeyboardButton("🚆 Transport"), KeyboardButton("🔮 Other")],
    [KeyboardButton("❓ Help / Commands")],
]

def get_category_menu():
    """Get category selection menu"""
    return ReplyKeyboardMarkup(CATEGORY_MENU, resize_keyboard=True)


# ==========================================
# INLINE KEYBOARD (Optional)
# ==========================================

def get_inline_keyboard():
    """Get inline keyboard for advanced features"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [
            InlineKeyboardButton("🌾 Mandi Bhav", callback_data="mandi"),
            InlineKeyboardButton("🌱 Kisaan Doctor", callback_data="kisaan"),
        ],
        [
            InlineKeyboardButton("🥇 Gold Rate", callback_data="gold"),
            InlineKeyboardButton("💰 Tax Calc", callback_data="tax"),
        ],
        [
            InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
            InlineKeyboardButton("📰 News", callback_data="news"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==========================================
# BOT HANDLER EXAMPLE (For reference)
# ==========================================

"""
# Usage in your bot handler:

def handle_message(update, context):
    text = update.message.text
    
    # Check if button was pressed
    if text in BUTTON_COMMAND_MAP:
        command = button_to_command(text)
        
        # Check if input required
        needs_input, prompt = is_input_button(command)
        if needs_input:
            context.user_data['pending_command'] = command
            update.message.reply_text(f"📝 {prompt}")
        else:
            # Execute command directly
            execute_command(update, context, command)
    
    # Check if main menu requested
    elif text == "🔙 Main Menu":
        update.message.reply_text(
            "📱 *Main Menu*",
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Handle user input or free text
        handle_free_text(update, context)
"""
