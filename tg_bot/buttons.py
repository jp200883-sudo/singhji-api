# tg_bot/buttons.py
"""
Singh Ji AI Ultra v8.3 — Telegram Inline Keyboard Buttons
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# ==================== MAIN MENU BUTTONS ====================

def get_main_menu():
    """47 बटन वाला मुख्य मेन्यू"""
    keyboard = [
        # Row 1
        [
            InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat"),
            InlineKeyboardButton("🖼️ Image Gen", callback_data="image_gen"),
            InlineKeyboardButton("🎙️ Voice", callback_data="voice"),
        ],
        # Row 2
        [
            InlineKeyboardButton("📰 News", callback_data="news"),
            InlineKeyboardButton("🌦️ Weather", callback_data="weather"),
            InlineKeyboardButton("💰 Gold Rate", callback_data="gold"),
        ],
        # Row 3
        [
            InlineKeyboardButton("🚂 PNR Status", callback_data="pnr"),
            InlineKeyboardButton("🚆 Train Tracking", callback_data="train"),
            InlineKeyboardButton("🚌 Bus", callback_data="bus"),
        ],
        # Row 4
        [
            InlineKeyboardButton("🎓 Govt Schemes", callback_data="govt"),
            InlineKeyboardButton("💧 Pani / Water", callback_data="water"),
            InlineKeyboardButton("💼 Jobs / Rozgar", callback_data="jobs"),
        ],
        # Row 5
        [
            InlineKeyboardButton("🌾 Mandi Rates", callback_data="mandi"),
            InlineKeyboardButton("📹 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Music", callback_data="music"),
        ],
        # Row 6
        [
            InlineKeyboardButton("📱 Recharge", callback_data="recharge"),
            InlineKeyboardButton("💳 Balance", callback_data="balance"),
            InlineKeyboardButton("🏦 UPI Pay", callback_data="upi"),
        ],
        # Row 7
        [
            InlineKeyboardButton("🛒 Shop", callback_data="shop"),
            InlineKeyboardButton("🍔 Food", callback_data="food"),
            InlineKeyboardButton("🚕 Cab", callback_data="cab"),
        ],
        # Row 8
        [
            InlineKeyboardButton("🏥 Hospital", callback_data="hospital"),
            InlineKeyboardButton("💊 Medicine", callback_data="medicine"),
            InlineKeyboardButton("👨‍⚕️ Doctor", callback_data="doctor"),
        ],
        # Row 9
        [
            InlineKeyboardButton("📚 Education", callback_data="education"),
            InlineKeyboardButton("📝 Exam", callback_data="exam"),
            InlineKeyboardButton("🎓 Result", callback_data="result"),
        ],
        # Row 10
        [
            InlineKeyboardButton("🏠 Property", callback_data="property"),
            InlineKeyboardButton("🚗 Vehicle", callback_data="vehicle"),
            InlineKeyboardButton("🛡️ Insurance", callback_data="insurance"),
        ],
        # Row 11
        [
            InlineKeyboardButton("📊 Stocks", callback_data="stocks"),
            InlineKeyboardButton("💹 Crypto", callback_data="crypto"),
            InlineKeyboardButton("🏦 Bank", callback_data="bank"),
        ],
        # Row 12
        [
            InlineKeyboardButton("📞 Call", callback_data="call"),
            InlineKeyboardButton("📧 Email", callback_data="email"),
            InlineKeyboardButton("💬 WhatsApp", callback_data="whatsapp"),
        ],
        # Row 13
        [
            InlineKeyboardButton("📍 Location", callback_data="location"),
            InlineKeyboardButton("🗺️ Map", callback_data="map"),
            InlineKeyboardButton("🧭 Navigate", callback_data="navigate"),
        ],
        # Row 14
        [
            InlineKeyboardButton("🎬 Movies", callback_data="movies"),
            InlineKeyboardButton("📺 TV", callback_data="tv"),
            InlineKeyboardButton("🎮 Games", callback_data="games"),
        ],
        # Row 15
        [
            InlineKeyboardButton("📖 Dictionary", callback_data="dictionary"),
            InlineKeyboardButton("🌐 Translate", callback_data="translate"),
            InlineKeyboardButton("🔍 Search", callback_data="search"),
        ],
        # Row 16
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("👤 Profile", callback_data="profile"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button():
    """वापस बटन"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ])


# ==================== BUTTON CLICK HANDLER ====================

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    सभी inline button clicks को हैंडल करता है।
    webhook.py line 11 से import होता है।
    """
    query = update.callback_query
    await query.answer()  # Telegram को acknowledge करो

    data = query.data
    user = query.from_user
    chat_id = query.message.chat.id

    logger.info(f"Button clicked: {data} by user {user.id}")

    try:
        # Main menu वापस
        if data == "main_menu":
            await query.edit_message_text(
                text=f"🦁 *Singh Ji AI Ultra v8.3*\n\nस्वागत है {user.first_name}!\n\nनीचे से कोई विकल्प चुनें:",
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )
            return

        # AI Chat
        elif data == "ai_chat":
            await query.edit_message_text(
                text="🤖 *AI Chat*\n\nअपना सवाल टाइप करें या voice भेजें।\n\nउदाहरण:\n• 'भारत की राजधानी क्या है?'\n• 'Python में loop कैसे लगाते हैं?'",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Image Generation
        elif data == "image_gen":
            await query.edit_message_text(
                text="🖼️ *Image Generator*\n\nFLUX.1 / SD3.5\n\nFormat: `/image <prompt>`\n\nउदाहरण: `/image एक शेर जंगल में बैठा है`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Voice
        elif data == "voice":
            await query.edit_message_text(
                text="🎙️ *Voice AI*\n\n• Voice message भेजें → STT + Reply\n• `/voice <text>` → TTS\n• Voice Clone (जल्द आ रहा है)",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # News
        elif data == "news":
            from tg_bot.commands import handle_command
            # Fake update object बनाओ ताकि command handler reuse हो सके
            fake_update = update
            fake_update.message.text = "/news"
            await handle_command(fake_update, context)
            await query.message.reply_text(
                "📰 News भेज दी गई!",
                reply_markup=get_back_button()
            )

        # Weather
        elif data == "weather":
            await query.edit_message_text(
                text="🌦️ *Weather*\n\nFormat: `/weather <city>`\n\nउदाहरण: `/weather दिल्ली`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Gold Rate
        elif data == "gold":
            from tg_bot.commands import handle_command
            fake_update = update
            fake_update.message.text = "/gold"
            await handle_command(fake_update, context)
            await query.message.reply_text(
                "💰 Gold Rate भेज दिया गया!",
                reply_markup=get_back_button()
            )

        # PNR
        elif data == "pnr":
            await query.edit_message_text(
                text="🚂 *PNR Status*\n\nFormat: `/pnr <10-digit-number>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Train Tracking
        elif data == "train":
            await query.edit_message_text(
                text="🚆 *Train Tracking*\n\nFormat: `/train <train-number>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Govt Schemes
        elif data == "govt":
            await query.edit_message_text(
                text="🎓 *Sarkari Yojna*\n\nFormat: `/govt <state>`\n\nउदाहरण: `/govt उत्तर प्रदेश`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Water / Pani
        elif data == "water":
            await query.edit_message_text(
                text="💧 *Pani / Water Bill*\n\nFormat: `/water <consumer-id>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Jobs
        elif data == "jobs":
            await query.edit_message_text(
                text="💼 *Rozgar / Jobs*\n\nFormat: `/jobs <skill>`\n\nउदाहरण: `/jobs python developer`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Mandi Rates
        elif data == "mandi":
            from tg_bot.commands import handle_command
            fake_update = update
            fake_update.message.text = "/mandi"
            await handle_command(fake_update, context)
            await query.message.reply_text(
                "🌾 Mandi Rates भेज दिए गए!",
                reply_markup=get_back_button()
            )

        # Video
        elif data == "video":
            await query.edit_message_text(
                text="📹 *Video Aggregator*\n\nFormat: `/video <query>`\n\nAuto-switch between platforms, watermark-free.",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Music
        elif data == "music":
            await query.edit_message_text(
                text="🎵 *Music*\n\nFormat: `/music <song-name>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Recharge
        elif data == "recharge":
            await query.edit_message_text(
                text="📱 *Mobile Recharge*\n\nFormat: `/recharge <number> <amount>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Balance
        elif data == "balance":
            await query.edit_message_text(
                text="💳 *Balance Check*\n\nFormat: `/balance`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # UPI
        elif data == "upi":
            await query.edit_message_text(
                text="🏦 *UPI Payment*\n\nUPI ID: `jp200883@sbi`\n\nPayment Gateway: *ON HOLD* (1000+ users के बाद activate)",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Shop
        elif data == "shop":
            await query.edit_message_text(
                text="🛒 *Shop*\n\nFormat: `/shop <product>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Food
        elif data == "food":
            await query.edit_message_text(
                text="🍔 *Food Order*\n\nFormat: `/food <dish> <pincode>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Cab
        elif data == "cab":
            await query.edit_message_text(
                text="🚕 *Cab Booking*\n\nFormat: `/cab <from> <to>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Hospital
        elif data == "hospital":
            await query.edit_message_text(
                text="🏥 *Hospital Finder*\n\nFormat: `/hospital <city>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Medicine
        elif data == "medicine":
            await query.edit_message_text(
                text="💊 *Medicine Info*\n\nFormat: `/medicine <name>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Doctor
        elif data == "doctor":
            await query.edit_message_text(
                text="👨‍⚕️ *Doctor Appointment*\n\nFormat: `/doctor <speciality> <city>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Education
        elif data == "education":
            await query.edit_message_text(
                text="📚 *Education Portal*\n\nFormat: `/education <course>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Exam
        elif data == "exam":
            await query.edit_message_text(
                text="📝 *Exam Info*\n\nFormat: `/exam <exam-name>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Result
        elif data == "result":
            await query.edit_message_text(
                text="🎓 *Result Check*\n\nFormat: `/result <roll-number>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Property
        elif data == "property":
            await query.edit_message_text(
                text="🏠 *Property*\n\nFormat: `/property <city> <type>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Vehicle
        elif data == "vehicle":
            await query.edit_message_text(
                text="🚗 *Vehicle Info*\n\nFormat: `/vehicle <number>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Insurance
        elif data == "insurance":
            await query.edit_message_text(
                text="🛡️ *Insurance*\n\nFormat: `/insurance <type>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Stocks
        elif data == "stocks":
            await query.edit_message_text(
                text="📊 *Stock Market*\n\nFormat: `/stocks <symbol>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Crypto
        elif data == "crypto":
            await query.edit_message_text(
                text="💹 *Crypto*\n\nFormat: `/crypto <coin>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Bank
        elif data == "bank":
            await query.edit_message_text(
                text="🏦 *Bank Services*\n\nFormat: `/bank <service>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Call
        elif data == "call":
            await query.edit_message_text(
                text="📞 *Voice Call*\n\nVoice AI Agent जल्द आ रहा है!\n\nExotel integration pending.",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Email
        elif data == "email":
            await query.edit_message_text(
                text="📧 *Email Service*\n\nFormat: `/email <to> <subject>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # WhatsApp
        elif data == "whatsapp":
            await query.edit_message_text(
                text="💬 *WhatsApp*\n\nFormat: `/whatsapp <number> <message>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Location
        elif data == "location":
            await query.edit_message_text(
                text="📍 *Share Location*\n\nLocation भेजें → Nearby services मिलेंगी।",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Map
        elif data == "map":
            await query.edit_message_text(
                text="🗺️ *Map*\n\nFormat: `/map <place>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Navigate
        elif data == "navigate":
            await query.edit_message_text(
                text="🧭 *Navigation*\n\nFormat: `/navigate <from> <to>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Movies
        elif data == "movies":
            await query.edit_message_text(
                text="🎬 *Movies*\n\nFormat: `/movies <name>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # TV
        elif data == "tv":
            await query.edit_message_text(
                text="📺 *TV Guide*\n\nFormat: `/tv <channel>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Games
        elif data == "games":
            await query.edit_message_text(
                text="🎮 *Games*\n\nFormat: `/games <name>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Dictionary
        elif data == "dictionary":
            await query.edit_message_text(
                text="📖 *Dictionary*\n\nFormat: `/dict <word>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Translate
        elif data == "translate":
            await query.edit_message_text(
                text="🌐 *Translate*\n\nFormat: `/translate <text> <to-lang>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Search
        elif data == "search":
            await query.edit_message_text(
                text="🔍 *Web Search*\n\nFormat: `/search <query>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Settings
        elif data == "settings":
            await query.edit_message_text(
                text="⚙️ *Settings*\n\n• Language\n• Notifications\n• Theme\n\nFormat: `/settings`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Profile
        elif data == "profile":
            await query.edit_message_text(
                text=f"👤 *Profile*\n\nName: {user.first_name}\nID: `{user.id}`\nUsername: @{user.username or 'N/A'}",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Help
        elif data == "help":
            await query.edit_message_text(
                text="❓ *Help*\n\nसभी commands के लिए: /help\n\nSupport: @singhji_support",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Bus
        elif data == "bus":
            await query.edit_message_text(
                text="🚌 *Bus Tracking*\n\nFormat: `/bus <route>`",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

        # Unknown button fallback
        else:
            await query.edit_message_text(
                text=f"⚠️ Unknown button: `{data}`\n\nMain menu पर वापस जा रहे हैं...",
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )

    except Exception as e:
        logger.error(f"Button handler error for {data}: {e}")
        await query.edit_message_text(
            text=f"❌ Error: {str(e)}\n\nकृपया फिर से प्रयास करें।",
            reply_markup=get_back_button()
        )
