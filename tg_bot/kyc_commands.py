import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
import aiohttp
import os

logger = logging.getLogger(__name__)

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

KYC_STEPS = {
    "pending": "⏳ आपका KYC शुरू हुआ है। कृपया नीचे विवरण भरें।",
    "aadhaar": "🆔 आधार नंबर भेजें (12 अंकों का)",
    "pan": "💳 PAN नंबर भेजें (ABCDE1234F फॉर्मेट)",
    "photo": "📸 अपनी सेल्फी भेजें",
    "address": "🏠 पता भेजें (गाँव, तहसील, जिला, राज्य)",
    "gram_panchayat": "🏛️ अपनी ग्राम पंचायत का नाम भेजें",
    "done": "✅ KYC पूरा! अब आप सभी सरकारी सेवाओं का उपयोग कर सकते हैं।"
}

async def kyc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /kyc command"""
    user = update.effective_user
    telegram_id = str(user.id)

    # Check existing KYC status
    status = await get_kyc_status(telegram_id)

    if status == "verified":
        await update.message.reply_text(
            "✅ आपका KYC पहले से ही वेरिफाइड है!\n\n"
            "🏛️ ग्राम पंचायत सेवाओं के लिए /grampanchayat दबाएँ\n"
            "💰 Agent बनने के लिए /agent दबाएँ"
        )
        return

    if status == "pending":
        await update.message.reply_text(
            "⏳ आपका KYC प्रोसेसिंग में है...\n"
            "कृपया थोड़ी देर बाद फिर से चेक करें।"
        )
        return

    # Start new KYC
    keyboard = [
        [InlineKeyboardButton("🚀 KYC शुरू करें", callback_data="kyc_start")],
        [InlineKeyboardButton("❓ मदद चाहिए", callback_data="kyc_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🙏 नमस्ते {user.first_name}!\n\n"
        f"📋 *Singh Ji KYC Portal*\n\n"
        f"इस KYC से आपको मिलेगा:\n"
        f"• ✅ ग्राम पंचायत सेवाएँ\n"
        f"• 💰 Agent कमीशन\n"
        f"• 🏦 डिजिटल पहचान पत्र\n"
        f"• 📜 सरकारी योजनाओं की पहुँच\n\n"
        f"⏱️ समय: 2 मिनट\n"
        f"🔒 100% सुरक्षित (Meri Pehchaan)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def kyc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle KYC inline buttons"""
    query = update.callback_query
    await query.answer()

    if query.data == "kyc_start":
        # Initialize KYC session
        await init_kyc_session(str(query.from_user.id))

        keyboard = [
            [InlineKeyboardButton("📤 आधार अपलोड करें", callback_data="kyc_aadhaar")],
            [InlineKeyboardButton("⬅️ वापस", callback_data="kyc_back")]
        ]

        await query.edit_message_text(
            KYC_STEPS["pending"] + "\n\n"
            "चरण 1/5: 🆔 *आधार वेरिफिकेशन*\n\n"
            "कृपया अपना 12 अंकों का आधार नंबर भेजें।\n"
            "या 'Skip' लिखें (मैनुअल वेरिफिकेशन के लिए)।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        context.user_data["kyc_step"] = "aadhaar"

    elif query.data == "kyc_help":
        await query.edit_message_text(
            "❓ *KYC मदद केंद्र*\n\n"
            "1. KYC क्यों ज़रूरी है?\n"
            "   → सरकारी सेवाओं और Agent कमीशन के लिए\n\n"
            "2. क्या मेरा डेटा सुरक्षित है?\n"
            "   → हाँ! Meri Pehchaan API + Encryption\n\n"
            "3. KYC में कितना समय लगेगा?\n"
            "   → ऑटो: 2 मिनट | मैनुअल: 24 घंटे\n\n"
            "4. Contact: @SinghJiSupport",
            parse_mode="Markdown"
        )

async def handle_kyc_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages during KYC flow"""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    step = context.user_data.get("kyc_step", None)

    if not step:
        return  # Not in KYC flow

    if step == "aadhaar":
        if len(text) == 12 and text.isdigit():
            context.user_data["aadhaar"] = text
            context.user_data["kyc_step"] = "pan"

            await update.message.reply_text(
                "✅ आधार नंबर रिकॉर्ड किया गया\n\n"
                "चरण 2/5: 💳 *PAN नंबर*\n"
                "कृपया अपना PAN नंबर भेजें (जैसे: ABCDE1234F)"
            )
        else:
            await update.message.reply_text(
                "❌ गलत आधार नंबर! 12 अंकों का सही नंबर भेजें।"
            )

    elif step == "pan":
        if len(text) == 10 and text[:5].isalpha() and text[5:9].isdigit() and text[9].isalpha():
            context.user_data["pan"] = text.upper()
            context.user_data["kyc_step"] = "address"

            await update.message.reply_text(
                "✅ PAN नंबर रिकॉर्ड किया गया\n\n"
                "चरण 3/5: 🏠 *पता*\n"
                "कृपया अपना पूरा पता भेजें:\n"
                "फॉर्मेट: गाँव, तहसील, जिला, राज्य, पिनकोड"
            )
        else:
            await update.message.reply_text(
                "❌ गलत PAN फॉर्मेट! सही फॉर्मेट: ABCDE1234F"
            )

    elif step == "address":
        context.user_data["address"] = text
        context.user_data["kyc_step"] = "gram_panchayat"

        await update.message.reply_text(
            "✅ पता रिकॉर्ड किया गया\n\n"
            "चरण 4/5: 🏛️ *ग्राम पंचायत*\n"
            "कृपया अपनी ग्राम पंचायत का नाम भेजें।"
        )

    elif step == "gram_panchayat":
        context.user_data["gram_panchayat"] = text

        # Save to database
        success = await save_kyc_data(user_id, context.user_data)

        if success:
            await update.message.reply_text(
                "🎉 *KYC सफलतापूर्वक जमा!*\n\n"
                "✅ विवरण:\n"
                f"• 🆔 आधार: {context.user_data.get('aadhaar', 'N/A')[:4]}****{context.user_data.get('aadhaar', 'N/A')[-4:]}\n"
                f"• 💳 PAN: {context.user_data.get('pan', 'N/A')}\n"
                f"• 🏠 पता: {context.user_data.get('address', 'N/A')[:30]}...\n"
                f"• 🏛️ ग्राम पंचायत: {context.user_data.get('gram_panchayat', 'N/A')}\n\n"
                "⏳ वेरिफिकेशन: 24 घंटे में\n"
                "📧 स्टेटस अपडेट Telegram पर मिलेगा\n\n"
                "अब आप Agent रजिस्ट्रेशन कर सकते हैं: /agent",
                parse_mode="Markdown"
            )
            context.user_data.clear()
        else:
            await update.message.reply_text(
                "❌ डेटा सेव करने में समस्या! कृपया फिर से कोशिश करें: /kyc"
            )

async def get_kyc_status(telegram_id: str) -> str:
    """Fetch KYC status from Supabase"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            url = f"{SUPABASE_URL}/rest/v1/kyc_records?telegram_id=eq.{telegram_id}&select=status"
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data:
                    return data[0].get("status", "none")
    except Exception as e:
        logger.error(f"KYC status check failed: {e}")
    return "none"

async def init_kyc_session(telegram_id: str):
    """Initialize KYC session in database"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            payload = {
                "telegram_id": telegram_id,
                "status": "in_progress",
                "started_at": "now()"
            }
            url = f"{SUPABASE_URL}/rest/v1/kyc_records"
            async with session.post(url, json=payload, headers=headers) as resp:
                return resp.status in [200, 201]
    except Exception as e:
        logger.error(f"KYC init failed: {e}")
        return False

async def save_kyc_data(telegram_id: str, data: dict) -> bool:
    """Save completed KYC data"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "telegram_id": telegram_id,
                "aadhaar_hash": data.get("aadhaar", ""),
                "pan": data.get("pan", ""),
                "address": data.get("address", ""),
                "gram_panchayat": data.get("gram_panchayat", ""),
                "status": "pending_verification",
                "submitted_at": "now()"
            }
            url = f"{SUPABASE_URL}/rest/v1/kyc_records"
            async with session.post(url, json=payload, headers=headers) as resp:
                return resp.status in [200, 201]
    except Exception as e:
        logger.error(f"KYC save failed: {e}")
        return False

# Register handlers
def register_kyc_handlers(application):
    application.add_handler(CommandHandler("kyc", kyc_command))
    application.add_handler(CommandHandler("agent", agent_registration_cmd))
    application.add_handler(CommandHandler("grampanchayat", grampanchayat_cmd))
    application.add_handler(CommandHandler("mykyc", mykyc_status_cmd))

    # Callback handlers
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(kyc_callback, pattern="^kyc_"))

    # Message handler for KYC flow (add with lower priority)
    from telegram.ext import MessageHandler, filters
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kyc_message),
        group=1
    )

# ============ AGENT REGISTRATION ============

async def agent_registration_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /agent command — register as commission agent"""
    user = update.effective_user
    telegram_id = str(user.id)

    # Check KYC first
    kyc_status = await get_kyc_status(telegram_id)
    if kyc_status != "verified":
        await update.message.reply_text(
            "❌ *Agent बनने के लिए KYC ज़रूरी है!*\n\n"
            "पहले KYC करें: /kyc\n"
            "फिर Agent रजिस्ट्रेशन करें: /agent",
            parse_mode="Markdown"
        )
        return

    # Check if already agent
    agent = await get_agent_data(telegram_id)
    if agent:
        await show_agent_dashboard(update, agent)
        return

    # New agent registration
    keyboard = [
        [InlineKeyboardButton("✅ हाँ, Agent बनें", callback_data="agent_confirm")],
        [InlineKeyboardButton("❌ नहीं, बाद में", callback_data="agent_cancel")]
    ]

    await update.message.reply_text(
        f"🤝 *Singh Ji Agent Program*\n\n"
        f"नमस्ते {user.first_name}!\n\n"
        f"Agent बनकर आप कमा सकते हैं:\n"
        f"• 💰 हर UPI पेमेंट पर 0.5% कमीशन\n"
        f"• 🏛️ ग्राम पंचायत सेवा शुल्क का 10%\n"
        f"• 📱 नए यूज़र रेफरल: ₹10/यूज़र\n"
        f"• 🎯 मंथली बोनस: ₹500+ ट्रांज़ैक्शन पर\n\n"
        f"क्या आप Singh Ji Agent बनना चाहते हैं?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_agent_dashboard(update: Update, agent: dict):
    """Show agent earnings dashboard"""
    earnings = agent.get("total_earnings", 0)
    referrals = agent.get("total_referrals", 0)
    level = agent.get("level", "Bronze")

    levels = {
        "Bronze": {"next": "Silver", "target": 1000},
        "Silver": {"next": "Gold", "target": 5000},
        "Gold": {"next": "Platinum", "target": 20000},
        "Platinum": {"next": "Diamond", "target": 100000}
    }

    level_info = levels.get(level, levels["Bronze"])
    progress = min(100, int((earnings / level_info["target"]) * 100))

    bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

    await update.message.reply_text(
        f"🏆 *Agent Dashboard*\n\n"
        f"👤 Level: *{level}*\n"
        f"📊 Progress: [{bar}] {progress}%\n"
        f"🎯 Next: {level_info['next']} (₹{level_info['target']})\n\n"
        f"💰 Total Earnings: ₹{earnings}\n"
        f"👥 Referrals: {referrals}\n"
        f"📅 This Month: ₹{agent.get('month_earnings', 0)}\n\n"
        f"📋 Quick Actions:\n"
        f"/referral — अपना लिंक\n"
        f"/withdraw — पैसे निकालें\n"
        f"/mylevel — लेवल विवरण\n"
        f"/payments — ट्रांज़ैक्शन इतिहास",
        parse_mode="Markdown"
    )

async def grampanchayat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gram Panchayat services"""
    keyboard = [
        [InlineKeyboardButton("📜 जाति प्रमाण पत्र", callback_data="gp_caste")],
        [InlineKeyboardButton("🏠 निवास प्रमाण पत्र", callback_data="gp_residence")],
        [InlineKeyboardButton("💍 विवाह प्रमाण पत्र", callback_data="gp_marriage")],
        [InlineKeyboardButton("🌾 किसान पंजीकरण", callback_data="gp_farmer")],
        [InlineKeyboardButton("💧 पानी कनेक्शन", callback_data="gp_water")],
        [InlineKeyboardButton("⚡ बिजली कनेक्शन", callback_data="gp_electricity")]
    ]

    await update.message.reply_text(
        "🏛️ *ग्राम पंचायत सेवाएँ*\n\n"
        "KYC वेरिफाइड यूज़र के लिए उपलब्ध:\n"
        "सभी सेवाएँ डिजिटल — घर बैठे आवेदन!\n\n"
        "सेवा शुल्क: ₹20-₹50\n"
        "Agent कमीशन: 10% ऑटो-स्प्लिट",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def mykyc_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check my KYC status"""
    status = await get_kyc_status(str(update.effective_user.id))

    status_map = {
        "none": "❌ KYC नहीं हुआ — /kyc से शुरू करें",
        "in_progress": "⏳ KYC जारी — विवरण जमा करें",
        "pending_verification": "⏳ वेरिफिकेशन पेंडिंग — 24 घंटे में अपडेट",
        "verified": "✅ KYC वेरिफाइड — सभी सेवाएँ उपलब्ध",
        "rejected": "❌ KYC रिजेक्ट — /kyc से फिर से करें"
    }

    await update.message.reply_text(
        f"📋 *आपका KYC स्टेटस*\n\n"
        f"{status_map.get(status, '❓ अज्ञात')}\n\n"
        f"मदद: @SinghJiSupport",
        parse_mode="Markdown"
    )

async def get_agent_data(telegram_id: str) -> dict:
    """Fetch agent data from Supabase"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            url = f"{SUPABASE_URL}/rest/v1/agents?telegram_id=eq.{telegram_id}&select=*"
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data[0] if data else None
    except Exception as e:
        logger.error(f"Agent fetch failed: {e}")
    return None
