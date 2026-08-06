# tg_bot/callbacks.py
# Singh Ji AI Ultra — Button Click Handler
# Matches webhook.py signature: handle_callback(chat_id, user_id, query_data)

import logging
from tg_bot.buttons import GOVT_SERVICES, GOVT_KEYBOARD, KYC_KEYBOARD, AGENT_KEYBOARD, GP_KEYBOARD, MAIN_KEYBOARD
from tg_bot.helpers import send_message

logger = logging.getLogger(__name__)

async def handle_callback(chat_id: int, user_id: int, data: str):
    """Handle ALL inline button clicks — called from webhook.py"""

    # ==========================================
    # MAIN MENU BUTTONS
    # ==========================================
    if data == "btn_weather":
        await send_message(chat_id, "🌤️ Weather के लिए city name भेजें:\nExample: /weather Delhi")

    elif data == "btn_news":
        await send_message(chat_id, "📰 News लोड हो रही है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/news")

    elif data == "btn_mandi":
        await send_message(chat_id, "🌾 Mandi Bhav के लिए state name भेजें:\nExample: /mandi Punjab")

    elif data == "btn_gold":
        await send_message(chat_id, "🥇 Gold Rate लोड हो रहा है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/gold")

    elif data == "btn_fuel":
        await send_message(chat_id, "⛽ Fuel Price लोड हो रहा है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/fuel")

    elif data == "btn_tax":
        await send_message(chat_id, "💰 Tax Calc के लिए income भेजें:\nExample: /tax 500000")

    elif data == "btn_horoscope":
        await send_message(chat_id, "🔮 Horoscope के लिए राशि भेजें:\nExample: /horoscope मेष")

    elif data == "btn_rozgar":
        await send_message(chat_id, "💼 Jobs खोजने के लिए:\nExample: /rozgar software IN")

    elif data == "btn_currency":
        await send_message(chat_id, "💱 Currency Convert:\nExample: /currency USD INR 100")

    elif data == "btn_search":
        await send_message(chat_id, "🔍 Search के लिए query भेजें:\nExample: /search AI news")

    elif data == "btn_translate":
        await send_message(chat_id, "🔤 Translate:\nExample: /translate en Namaste")

    elif data == "btn_yojana":
        await send_message(chat_id, "📋 Yojana info जल्द आएगी! 🚀")

    elif data == "btn_tv":
        await send_message(chat_id, "📺 SinghJi TV जल्द लाइव होगा! 🎬")

    elif data == "btn_emergency":
        await send_message(chat_id, "🚨 Emergency Numbers:\n/police — 100\n/ambulance — 108\n/fire — 101\nWomen — 1091")

    elif data == "btn_upi":
        await send_message(chat_id, "💳 UPI Info लोड हो रहा है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/upi")

    elif data == "btn_govt":
        await send_message(chat_id, 
            "🏛️ *Govt Services*\n\n"
            "सरकारी सेवाओं की जानकारी:\n"
            "नंबर और वेबसाइट के साथ",
            reply_markup=GOVT_KEYBOARD
        )

    elif data == "btn_guard":
        await send_message(chat_id, "🛡️ Guard Agent activated! Security monitoring ON.")

    elif data == "btn_social":
        await send_message(chat_id, "📱 Social Agent — Facebook/Twitter posting ready!")

    elif data == "btn_voice":
        await send_message(chat_id, "🎤 Voice AI — Speak in Hindi/English!\n(Coming soon to Telegram)")

    elif data == "btn_plant":
        await send_message(chat_id, "🌿 Plant Doctor — पौधे की फोटो भेजें!\n(Coming soon)")

    elif data == "btn_ai":
        await send_message(chat_id, "🤖 AI Chat — सवाल पूछें!\nExample: /ai India ka capital kya hai?")

    elif data == "btn_status":
        await send_message(chat_id, "📊 Status लोड हो रहा है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/status")

    # ==========================================
    # ✅ NEW: KYC BUTTON
    # ==========================================
    elif data == "btn_kyc":
        await send_message(chat_id,
            "📋 *Singh Ji KYC Portal*\n\n"
            "KYC से मिलेगा:\n"
            "• ✅ ग्राम पंचायत सेवाएँ\n"
            "• 💰 Agent कमीशन\n"
            "• 🏦 डिजिटल पहचान पत्र\n"
            "• 📜 सरकारी योजनाओं की पहुँच\n\n"
            "⏱️ समय: 2 मिनट\n"
            "🔒 100% सुरक्षित",
            reply_markup=KYC_KEYBOARD
        )

    # ==========================================
    # ✅ NEW: AGENT BUTTON
    # ==========================================
    elif data == "btn_agent":
        await send_message(chat_id,
            "🤝 *Singh Ji Agent Program*\n\n"
            "Agent बनकर कमाएँ:\n"
            "• 💰 UPI पेमेंट पर 0.5%\n"
            "• 🏛️ GP सेवा शुल्क का 10%\n"
            "• 📱 नया यूज़र रेफरल: ₹10\n"
            "• 🎯 मंथली बोनस: ₹500+\n\n"
            "KYC ज़रूरी है!",
            reply_markup=AGENT_KEYBOARD
        )

    # ==========================================
    # ✅ NEW: GRAM PANCHAYAT BUTTON
    # ==========================================
    elif data == "btn_grampanchayat":
        await send_message(chat_id,
            "🏛️ *ग्राम पंचायत सेवाएँ*\n\n"
            "KYC वेरिफाइड यूज़र के लिए:\n"
            "सभी सेवाएँ डिजिटल!\n\n"
            "सेवा शुल्क: ₹20-₹50\n"
            "Agent कमीशन: 10%",
            reply_markup=GP_KEYBOARD
        )

    elif data == "btn_withdraw":
        await send_message(chat_id, "💸 Withdrawal के लिए:\n/withdraw <amount>\nExample: /withdraw 500")

    elif data == "btn_help":
        await send_message(chat_id, "📚 Help लोड हो रहा है...")
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/help")

    elif data == "btn_back":
        await send_message(chat_id,
            "🌅 *Singh Ji AI Ultra v8.4*\n\n"
            "अपनी सुविधा चुनें:",
            reply_markup=MAIN_KEYBOARD
        )

    # ==========================================
    # GOVT SERVICE DETAILS
    # ==========================================
    elif data.startswith("govt_"):
        service = GOVT_SERVICES.get(data)
        if service:
            text = (
                f"{service['title']}\n\n"
                f"☎️ Helpline: {service['phone']}\n"
                f"🌐 Website: {service['website']}\n\n"
                f"ℹ️ {service['info']}"
            )
            await send_message(chat_id, text)
        elif data == "govt_kyc":
            from tg_bot.commands import handle_command
            await handle_command(chat_id, user_id, "/kyc")
        elif data == "govt_agent":
            from tg_bot.commands import handle_command
            await handle_command(chat_id, user_id, "/agent")

    # ==========================================
    # KYC CALLBACKS
    # ==========================================
    elif data == "kyc_start":
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/kyc")

    elif data == "kyc_status":
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/mykyc")

    elif data == "kyc_help":
        await send_message(chat_id,
            "❓ *KYC मदद*\n\n"
            "1. KYC क्यों? → सरकारी सेवाएँ + Agent कमीशन\n"
            "2. सुरक्षित? → हाँ! Meri Pehchaan API\n"
            "3. समय? → 2 मिनट\n"
            "4. मदद: @SinghJiSupport"
        )

    # ==========================================
    # AGENT CALLBACKS
    # ==========================================
    elif data == "agent_register":
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/agent")

    elif data == "agent_dashboard":
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/agent")

    elif data == "agent_referral":
        from tg_bot.commands import handle_command
        await handle_command(chat_id, user_id, "/referral")

    elif data == "agent_withdraw":
        await send_message(chat_id, "💸 Withdrawal:\n/withdraw <amount>\nExample: /withdraw 500")

    # ==========================================
    # GRAM PANCHAYAT CALLBACKS
    # ==========================================
    elif data.startswith("gp_"):
        service_names = {
            "gp_caste": "📜 जाति प्रमाण पत्र",
            "gp_residence": "🏠 निवास प्रमाण पत्र",
            "gp_marriage": "💍 विवाह प्रमाण पत्र",
            "gp_farmer": "🌾 किसान पंजीकरण",
            "gp_water": "💧 पानी कनेक्शन",
            "gp_electricity": "⚡ बिजली कनेक्शन",
        }
        name = service_names.get(data, "सेवा")
        await send_message(chat_id,
            f"{name}\n\n"
            f"🚧 यह सेवा जल्द लाइव होगी!\n"
            f"KYC वेरिफाइड यूज़र के लिए उपलब्ध।\n\n"
            f"Status track करें: /mykyc"
        )

    else:
        logger.warning(f"Unknown callback: {data}")
        await send_message(chat_id, "⚠️ Unknown button. Type /help for commands.")

    return {"status": "ok"}
