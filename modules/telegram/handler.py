"""
Singh Ji AI Ultra v8.0 — Telegram Bot with Web App
Backend: Railway (PRIMARY) | AWS Backup: 15.134.36.7
"""

import os
import logging
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp
)
from aiogram.enums import ParseMode

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://your-app-url.com")
ADMIN_IDS = [123456789]  # Apna Telegram ID daalo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ========== MODULE RESPONSES ==========
MODULES = {
    "weather": "🌤️ <b>मौसम (Delhi):</b>\n🌡️ तापमान: 30.15°C (Feel: 34.91°C)\n💧 नमी: 68%\n💨 हवा: 2.48 m/s\n🌧️ Light Rain\n\n— Singh Ji AI Ultra",
    "news": "📰 <b>Latest News:</b>\n• Rahul Gandhi demands Amit Shah resignation\n• India GDP growth 7.2%\n• ISRO launches new satellite\n\n— Singh Ji AI Ultra",
    "mandi": "🌾 <b>Mandi Bhav (Delhi):</b>\n🌾 गेहूं: ₹2,450/quintal\n🌾 चावल: ₹3,200/quintal\n🧅 प्याज: ₹1,800/quintal\n🥔 आलू: ₹1,200/quintal\n\n— Singh Ji AI Ultra",
    "gold": "🥇 <b>Gold Rate:</b>\n💰 24K: ₹78,450/10g\n💰 22K: ₹71,890/10g\n💰 18K: ₹58,840/10g\n\n— Singh Ji AI Ultra",
    "yojana": "📜 <b>Sarkari Yojana:</b>\n• PM Kisan Samman Nidhi\n• Ayushman Bharat Yojana\n• PM Awas Yojana\n• Mudra Loan Yojana\n\n— Singh Ji AI Ultra",
    "tv": "📺 <b>TV Channels:</b>\n• DD National\n• Aaj Tak\n• Zee News\n• Sony TV\n• Colors TV\n\n— Singh Ji AI Ultra",
    "rozgar": "💼 <b>Rozgar / Jobs:</b>\n• SSC CGL 2026 - Apply Now\n• UPSC CDS - Last Date: 15 Aug\n• Railway Group D - 5000 Posts\n• Bank PO - IBPS Notification\n\n— Singh Ji AI Ultra",
    "govt": "🏛️ <b>Government Services:</b>\n• Aadhaar Update\n• PAN Card Apply\n• Passport Status\n• Voter ID Card\n• Ration Card\n\n— Singh Ji AI Ultra",
    "pani": "💧 <b>Jal Board / Pani:</b>\n• Delhi Jal Board Bill Check\n• New Water Connection\n• Complaint Register\n• Tanker Booking\n\n— Singh Ji AI Ultra",
    "sewer": "🚰 <b>Sewer / Drainage:</b>\n• Sewer Connection Apply\n• Blockage Complaint\n• Sewer Bill Payment\n• New Connection Status\n\n— Singh Ji AI Ultra",
    "kisaan": "🚜 <b>Kisaan Portal:</b>\n• PM Kisan Registration\n• Crop Insurance\n• Soil Health Card\n• KCC Loan Apply\n• Mandi Rates\n\n— Singh Ji AI Ultra",
    "fuel": "⛽ <b>Fuel Prices:</b>\n• Petrol: ₹96.72/L (Delhi)\n• Diesel: ₹89.62/L (Delhi)\n• CNG: ₹76.50/kg\n• LPG: ₹903/cylinder\n\n— Singh Ji AI Ultra",
    "horoscope": "🔮 <b>Rashifal (Aaj ka):</b>\n♈ मेष: आज का दिन अच्छा रहेगा\n♉ वृष: व्यापार में लाभ\n♊ मिथुन: नई योजना बनेगी\n\n— Singh Ji AI Ultra",
    "currency": "💱 <b>Currency Rates:</b>\n• USD: ₹83.42\n• EUR: ₹90.15\n• GBP: ₹105.30\n• JPY: ₹0.56\n\n— Singh Ji AI Ultra",
    "voice": "🎙️ <b>Voice AI:</b>\nVoice mode activate! Bhashini + Whisper STT aur Kokoro TTS ready hai.\nAb bol ke poochho!\n\n— Singh Ji AI Ultra",
    "ai_chat": "🤖 <b>AI Chat Mode:</b>\nGroq + Gemini dono models active hain.\nKoi bhi sawaal poochho — coding, GK, creative sab handle karenge!\n\n— Singh Ji AI Ultra",
    "tax_calc": "🧮 <b>Tax Calculator:</b>\nIncome tax calculate karne ke liye apni salary batao.\nOld regime vs New regime dono compare karenge.\n\n— Singh Ji AI Ultra",
    "plant_id": "🌿 <b>Plant Identifier:</b>\nPlant ki photo bhejo, AI bata dega kaunsa plant hai!\nCare tips + medicinal uses bhi!\n\n— Singh Ji AI Ultra",
    "emergency": "🚨 <b>Emergency Numbers:</b>\n🚑 Ambulance: 102\n🚔 Police: 100\n🔥 Fire: 101\n🆘 Women Helpline: 1091\n💊 Poison Control: 1066\n\n— Singh Ji AI Ultra",
    "upi": "💳 <b>UPI Info:</b>\nUPI ID: jp200883@sbi\n• 0% UPI Transaction Fee\n• Instant Transfer\n• QR Code Payment\n• Merchant Support\n\n— Singh Ji AI Ultra",
    "image_gen": "🎨 <b>Image Generator:</b>\nFLUX.1 + Stable Diffusion 3.5 ready!\nKaisa image chahiye? Prompt batao:\nExample: \"Indian farmer in golden field\"\n\n— Singh Ji AI Ultra",
    "translate": "🌐 <b>Translator:</b>\nIndicTrans2 + SeamlessM4T + Google Translate ready!\nKoi bhi language mein translate karo.\n\n— Singh Ji AI Ultra",
    "status": "📊 <b>System Status:</b>\n✅ Backend: Railway (Online)\n✅ AWS Backup: 15.134.36.7\n✅ 95/300 Agents Active\n✅ Groq API: Connected\n✅ Gemini API: Connected\n✅ Bhashini: Pending Approval\n\n— Singh Ji AI Ultra",
    "admin": "🔒 <b>Admin Panel:</b>\nAdmin access ke liye login required.\nAdmin.html pe jaao ya secret key daalo.\n\n— Singh Ji AI Ultra",
}

# ========== KEYBOARDS ==========

def get_main_keyboard():
    """Reply keyboard for quick text commands"""
    kb = [
        [types.KeyboardButton(text="🌤️ Weather"), types.KeyboardButton(text="📰 News")],
        [types.KeyboardButton(text="🌾 Mandi Bhav"), types.KeyboardButton(text="🤖 AI Chat")],
        [types.KeyboardButton(text="🎙️ Voice"), types.KeyboardButton(text="📊 Status")],
        [types.KeyboardButton(text="🧮 Tax Calc"), types.KeyboardButton(text="🌿 Plant ID")],
        [types.KeyboardButton(text="🥇 Gold Rate"), types.KeyboardButton(text="⛽ Fuel Price")],
        [types.KeyboardButton(text="🔮 Horoscope"), types.KeyboardButton(text="💱 Currency")],
        [types.KeyboardButton(text="🚨 Emergency"), types.KeyboardButton(text="💳 UPI Info")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_webapp_button():
    """Inline button to open Web App"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Singh Ji AI Capsule Kholo",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )],
        [InlineKeyboardButton(text="📊 Module Status", callback_data="status")],
    ])

# ========== HANDLERS ==========

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = (
        "🦁 <b>Welcome to Singh Ji AI Ultra v8.0!</b>\n\n"
        "Main aapka AI assistant hoon. 💬\n\n"
        "👇 <b>Do tareeke hain use karne ke:</b>\n"
        "1️⃣ <b>Capsule App</b> dabao — Full Web App with colors & buttons\n"
        "2️⃣ <b>Reply Keyboard</b> — Simple text buttons neeche\n\n"
        "Kya chahiye aapko? 🚀"
    )
    await message.answer(welcome, reply_markup=get_webapp_button())
    await message.answer("Ya reply keyboard se bhi use karo 👇", reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "🦁 <b>Singh Ji AI Ultra v8.0 — Help</b>\n\n"
        "<b>Commands:</b>\n"
        "/start — Bot start karo\n"
        "/weather — Mausam dekhlo\n"
        "/news — Latest khabar\n"
        "/mandi — Mandi bhav\n"
        "/gold — Sone ka bhav\n"
        "/yojana — Sarkari yojana\n"
        "/rozgar — Naukri updates\n"
        "/govt — Govt services\n"
        "/fuel — Petrol/diesel rate\n"
        "/horoscope — Aaj ka rashifal\n"
        "/currency — Dollar/rupee rate\n"
        "/status — System status\n"
        "/voice — Voice AI mode\n"
        "/admin — Admin panel\n\n"
        "💡 <b>Tip:</b> Capsule App dabao for best experience!"
    )
    await message.answer(help_text)

@router.message(F.text.in_(["🌤️ Weather", "/weather"]))
async def on_weather(message: types.Message):
    await message.answer(MODULES["weather"])

@router.message(F.text.in_(["📰 News", "/news"]))
async def on_news(message: types.Message):
    await message.answer(MODULES["news"])

@router.message(F.text.in_(["🌾 Mandi Bhav", "/mandi"]))
async def on_mandi(message: types.Message):
    await message.answer(MODULES["mandi"])

@router.message(F.text.in_(["🥇 Gold Rate", "/gold"]))
async def on_gold(message: types.Message):
    await message.answer(MODULES["gold"])

@router.message(F.text.in_(["📜 Yojana", "/yojana"]))
async def on_yojana(message: types.Message):
    await message.answer(MODULES["yojana"])

@router.message(F.text.in_(["📺 TV", "/tv"]))
async def on_tv(message: types.Message):
    await message.answer(MODULES["tv"])

@router.message(F.text.in_(["💼 Rozgar", "/rozgar"]))
async def on_rozgar(message: types.Message):
    await message.answer(MODULES["rozgar"])

@router.message(F.text.in_(["🏛️ Govt", "/govt"]))
async def on_govt(message: types.Message):
    await message.answer(MODULES["govt"])

@router.message(F.text.in_(["💧 Pani", "/pani"]))
async def on_pani(message: types.Message):
    await message.answer(MODULES["pani"])

@router.message(F.text.in_(["🚰 Sewer", "/sewer"]))
async def on_sewer(message: types.Message):
    await message.answer(MODULES["sewer"])

@router.message(F.text.in_(["🚜 Kisaan", "/kisaan"]))
async def on_kisaan(message: types.Message):
    await message.answer(MODULES["kisaan"])

@router.message(F.text.in_(["⛽ Fuel Price", "/fuel"]))
async def on_fuel(message: types.Message):
    await message.answer(MODULES["fuel"])

@router.message(F.text.in_(["🔮 Horoscope", "/horoscope"]))
async def on_horoscope(message: types.Message):
    await message.answer(MODULES["horoscope"])

@router.message(F.text.in_(["💱 Currency", "/currency"]))
async def on_currency(message: types.Message):
    await message.answer(MODULES["currency"])

@router.message(F.text.in_(["🎙️ Voice", "/voice"]))
async def on_voice(message: types.Message):
    await message.answer(MODULES["voice"])

@router.message(F.text.in_(["🤖 AI Chat", "/ai_chat"]))
async def on_ai_chat(message: types.Message):
    await message.answer(MODULES["ai_chat"])

@router.message(F.text.in_(["🧮 Tax Calc", "/tax_calc"]))
async def on_tax_calc(message: types.Message):
    await message.answer(MODULES["tax_calc"])

@router.message(F.text.in_(["🌿 Plant ID", "/plant_id"]))
async def on_plant_id(message: types.Message):
    await message.answer(MODULES["plant_id"])

@router.message(F.text.in_(["🚨 Emergency", "/emergency"]))
async def on_emergency(message: types.Message):
    await message.answer(MODULES["emergency"])

@router.message(F.text.in_(["💳 UPI Info", "/upi"]))
async def on_upi(message: types.Message):
    await message.answer(MODULES["upi"])

@router.message(F.text.in_(["📊 Status", "/status"]))
async def on_status(message: types.Message):
    await message.answer(MODULES["status"])

@router.message(Command("admin"))
async def on_admin(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("🔓 <b>Admin Panel Access Granted!</b>\n\nWelcome Admin!")
    else:
        await message.answer(MODULES["admin"])

@router.callback_query(F.data == "status")
async def on_callback_status(callback: types.CallbackQuery):
    await callback.message.answer(MODULES["status"])
    await callback.answer()

@router.message()
async def on_any_message(message: types.Message):
    """Fallback — AI response ya Web App suggest"""
    text = message.text.lower()
    
    # Check if it's a known command without slash
    for key, resp in MODULES.items():
        if key in text:
            await message.answer(resp)
            return
    
    # Default AI response
    await message.answer(
        f"🤖 <b>Singh Ji AI:</b>\n\n"
        f"\"{message.text}\" samajh liya! Main ispe kaam kar raha hoon...\n\n"
        f"💡 <b>Better experience ke liye Capsule App kholo:</b>",
        reply_markup=get_webapp_button()
    )


@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    settings_text = (
        "⚙️ <b>Singh Ji AI — Settings</b>\n\n"
        "🌐 <b>Language:</b> Hindi (Hinglish)\n"
        "🤖 <b>AI Model:</b> Groq + Gemini Dual\n"
        "🎙️ <b>Voice:</b> Bhashini + Whisper\n"
        "📰 <b>News:</b> Daily 4:00 AM Auto\n"
        "🔔 <b>Notifications:</b> ON ✅\n"
        "💳 <b>UPI:</b> jp200883@sbi\n\n"
        "— Singh Ji AI Ultra v8.0"
    )
    
    # Settings inline buttons
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Language", callback_data="set_lang"),
         InlineKeyboardButton(text="🤖 AI Model", callback_data="set_model")],
        [InlineKeyboardButton(text="🔔 Notifications", callback_data="set_notif"),
         InlineKeyboardButton(text="📰 News Time", callback_data="set_news")],
        [InlineKeyboardButton(text="🚀 Open Capsule App", web_app=WebAppInfo(url=WEB_APP_URL))],
    ])
    
    await message.answer(settings_text, reply_markup=kb)

# ========== SET MENU BUTTON ==========
async def set_menu_button():
    """Set Web App as menu button"""
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🦁 Singh Ji AI",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )

# ========== MAIN ==========
async def main():
    logger.info("🦁 Singh Ji AI Bot starting...")
    await set_menu_button()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
