# telegram/commands.py
import os
import logging
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from core.config import (
    GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY,
    AVAILABLE_KEYS, OPENWEATHER_API_KEY, ADMIN_USER_ID
)

# Mandi — DATAGOVINDIA_API_KEY इस्तेमाल करता है (MANDI_API_KEY की ज़रूरत नहीं)
DATA_GOV_API_KEY = os.environ.get("DATAGOVINDIA_API_KEY", "")
MANDI_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Variety-wise Daily Market Prices
MANDI_BASE_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE_ID}"

# Supabase config — direct env (not exported from core.config)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
from core.memory import _memory_save, _memory_get
from core.swarm import SMART_SWARM
from core.scheduler import USER_PREFERENCES, MASTER_SCHEDULER
from utils.helpers import _normalize_state, _calculate_tax
from tg_bot.helpers import send_message

logger = logging.getLogger(__name__)

# ==========================================
# HTTP CLIENT - GLOBAL
# ==========================================
HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client
    logger.info("✅ Telegram commands HTTP client set")

# ==========================================
# KYC STATE MANAGEMENT (in-memory session)
# ==========================================
KYC_SESSIONS = {}  # user_id -> {"step": "aadhaar", "data": {...}}

# ==========================================
# SUPABASE HELPERS
# ==========================================
async def _get_kyc_status(telegram_id: str) -> str:
    try:
        url = f"{SUPABASE_URL}/rest/v1/kyc_records?telegram_id=eq.{telegram_id}&select=status"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        resp = await HTTP_CLIENT.get(url, headers=headers, timeout=10)
        data = resp.json()
        return data[0].get("status", "none") if data else "none"
    except Exception as e:
        logger.error(f"KYC status check failed: {e}")
    return "none"

async def _init_kyc_session(telegram_id: str):
    try:
        url = f"{SUPABASE_URL}/rest/v1/kyc_records"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        payload = {"telegram_id": telegram_id, "status": "in_progress", "started_at": "now()"}
        resp = await HTTP_CLIENT.post(url, json=payload, headers=headers, timeout=10)
        return resp.status in [200, 201]
    except Exception as e:
        logger.error(f"KYC init failed: {e}")
    return False

async def _save_kyc_data(telegram_id: str, data: dict) -> bool:
    try:
        url = f"{SUPABASE_URL}/rest/v1/kyc_records"
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
        resp = await HTTP_CLIENT.post(url, json=payload, headers=headers, timeout=10)
        return resp.status in [200, 201]
    except Exception as e:
        logger.error(f"KYC save failed: {e}")
    return False

async def _get_agent_data(telegram_id: str) -> dict:
    try:
        url = f"{SUPABASE_URL}/rest/v1/agents?telegram_id=eq.{telegram_id}&select=*"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        resp = await HTTP_CLIENT.get(url, headers=headers, timeout=10)
        data = resp.json()
        return data[0] if data else None
    except Exception as e:
        logger.error(f"Agent fetch failed: {e}")
    return None

# ==========================================
# KYC FLOW HANDLER
# ==========================================
async def _handle_kyc_flow(chat_id: int, user_id: int, text: str):
    """Handle multi-step KYC via text messages"""
    session = KYC_SESSIONS.get(user_id, {})
    step = session.get("step", "start")
    data = session.get("data", {})

    if step == "start":
        if text.lower() in ["start", "yes", "haan", "हाँ"]:
            KYC_SESSIONS[user_id] = {"step": "aadhaar", "data": {}}
            await _init_kyc_session(str(user_id))
            await send_message(
                chat_id,
                "🚀 KYC शुरू!\n\n"
                "चरण 1/5: 🆔 *आधार नंबर*\n"
                "कृपया अपना 12 अंकों का आधार नंबर भेजें।\n"
                "(Example: 123456789012)"
            )
        else:
            await send_message(chat_id, "KYC रद्द कर दिया गया। /kyc से फिर से शुरू करें।")
            KYC_SESSIONS.pop(user_id, None)
        return {"status": "ok"}

    elif step == "aadhaar":
        clean = text.strip().replace(" ", "").replace("-", "")
        if len(clean) == 12 and clean.isdigit():
            data["aadhaar"] = clean
            KYC_SESSIONS[user_id] = {"step": "pan", "data": data}
            await send_message(
                chat_id,
                "✅ आधार रिकॉर्ड किया गया\n\n"
                "चरण 2/5: 💳 *PAN नंबर*\n"
                "कृपया PAN भेजें (Format: ABCDE1234F)"
            )
        else:
            await send_message(chat_id, "❌ गलत आधार! 12 अंकों का सही नंबर भेजें।")
        return {"status": "ok"}

    elif step == "pan":
        clean = text.strip().upper()
        if len(clean) == 10 and clean[:5].isalpha() and clean[5:9].isdigit() and clean[9].isalpha():
            data["pan"] = clean
            KYC_SESSIONS[user_id] = {"step": "address", "data": data}
            await send_message(
                chat_id,
                "✅ PAN रिकॉर्ड किया गया\n\n"
                "चरण 3/5: 🏠 *पता*\n"
                "कृपया पूरा पता भेजें:\n"
                "गाँव, तहसील, जिला, राज्य, पिनकोड"
            )
        else:
            await send_message(chat_id, "❌ गलत PAN! सही Format: ABCDE1234F")
        return {"status": "ok"}

    elif step == "address":
        data["address"] = text.strip()
        KYC_SESSIONS[user_id] = {"step": "gram_panchayat", "data": data}
        await send_message(
            chat_id,
            "✅ पता रिकॉर्ड किया गया\n\n"
            "चरण 4/5: 🏛️ *ग्राम पंचायत*\n"
            "कृपया अपनी ग्राम पंचायत का नाम भेजें।"
        )
        return {"status": "ok"}

    elif step == "gram_panchayat":
        data["gram_panchayat"] = text.strip()

        # Save to DB
        success = await _save_kyc_data(str(user_id), data)

        if success:
            aadhaar_masked = data.get("aadhaar", "")[:4] + "****" + data.get("aadhaar", "")[-4:]
            await send_message(
                chat_id,
                f"🎉 *KYC सफलतापूर्वक जमा!*\n\n"
                f"✅ विवरण:\n"
                f"• 🆔 आधार: {aadhaar_masked}\n"
                f"• 💳 PAN: {data.get('pan', 'N/A')}\n"
                f"• 🏠 पता: {data.get('address', 'N/A')[:30]}...\n"
                f"• 🏛️ ग्राम पंचायत: {data.get('gram_panchayat', 'N/A')}\n\n"
                f"⏳ वेरिफिकेशन: 24 घंटे में\n"
                f"📧 अपडेट Telegram पर मिलेगा\n\n"
                f"अब Agent बनें: /agent"
            )
        else:
            await send_message(chat_id, "❌ डेटा सेव करने में समस्या! /kyc से फिर से कोशिश करें।")

        KYC_SESSIONS.pop(user_id, None)
        return {"status": "ok"}

    return {"status": "ok"}

# ==========================================
# COMMAND HANDLER
# ==========================================
async def handle_command(chat_id, user_id, text):
    """सारे Telegram commands को handle करता है"""

    # ---- KYC FLOW CHECK (top priority) ----
    if user_id in KYC_SESSIONS and not text.startswith("/"):
        return await _handle_kyc_flow(chat_id, user_id, text)

    # ---- START ----
    if text == "/start":
        from utils.helpers import MAIN_KEYBOARD
        welcome = (
            "🌅 Welcome to Singh Ji AI Ultra v8.3!\n\n"
            "I'm your AI assistant. Use the buttons below or /help"
        )
        await send_message(chat_id, welcome, MAIN_KEYBOARD)
        return {"status": "ok"}

    # ---- HELP ----
    if text == "/help":
        help_text = (
            "📚 Commands:\n\n"
            "🌤️ /weather city - Get weather\n"
            "📰 /news - Latest news\n"
            "🌾 /mandi state - Mandi prices\n"
            "💰 /tax income - Tax calculation\n"
            "📊 /status - System status\n"
            "🤖 /ai question - AI chat\n"
            "🥇 /gold city - Gold rates\n"
            "⛽ /fuel city - Fuel prices\n"
            "🔮 /horoscope rashi - Daily horoscope\n"
            "💱 /currency USD INR 100 - Currency convert\n"
            "🔤 /translate en text - Translate\n"
            "🚨 /emergency type - Emergency numbers\n"
            "💳 /upi - UPI information\n"
            "🔍 /search query - Web search\n"
            "💼 /rozgar keyword country - Jobs\n"
            "📋 /kyc - KYC registration\n"
            "🤝 /agent - Agent dashboard\n"
            "🏛️ /grampanchayat - GP Services\n"
            "📢 /broadcast message - Admin only"
        )
        await send_message(chat_id, help_text)
        return {"status": "ok"}

    # ---- STATUS ----
    if text == "/status":
        status = SMART_SWARM.get_status()
        api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
        status_text = (
            f"📊 Status\n\n"
            f"🤖 Agents: {status['currently_loaded']}/330\n"
            f"⚡ Active: {status['active_running']}\n"
            f"😴 Idle: {status['idle']}\n"
            f"🔌 APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
            f"👥 Users: {len(USER_PREFERENCES)}\n"
            f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        await send_message(chat_id, status_text)
        return {"status": "ok"}

    # ---- KYC ----
    if text == "/kyc":
        status = await _get_kyc_status(str(user_id))
        if status == "verified":
            await send_message(
                chat_id,
                "✅ आपका KYC पहले से ही वेरिफाइड है!\n\n"
                "🏛️ ग्राम पंचायत: /grampanchayat\n"
                "💰 Agent बनें: /agent"
            )
        elif status == "pending_verification":
            await send_message(chat_id, "⏳ आपका KYC वेरिफिकेशन पेंडिंग है। 24 घंटे में अपडेट मिलेगा।")
        elif status == "in_progress":
            await send_message(chat_id, "⏳ KYC जारी है। विवरण जमा करें।")
        else:
            await send_message(
                chat_id,
                "📋 *Singh Ji KYC Portal*\n\n"
                "इस KYC से आपको मिलेगा:\n"
                "• ✅ ग्राम पंचायत सेवाएँ\n"
                "• 💰 Agent कमीशन\n"
                "• 🏦 डिजिटल पहचान पत्र\n"
                "• 📜 सरकारी योजनाओं की पहुँच\n\n"
                "⏱️ समय: 2 मिनट\n"
                "🔒 100% सुरक्षित (Meri Pehchaan)\n\n"
                "KYC शुरू करने के लिए *START* लिखें।"
            )
            KYC_SESSIONS[user_id] = {"step": "start", "data": {}}
        return {"status": "ok"}

    # ---- MYKYC ----
    if text == "/mykyc":
        status = await _get_kyc_status(str(user_id))
        status_map = {
            "none": "❌ KYC नहीं हुआ — /kyc से शुरू करें",
            "in_progress": "⏳ KYC जारी — विवरण जमा करें",
            "pending_verification": "⏳ वेरिफिकेशन पेंडिंग — 24 घंटे में अपडेट",
            "verified": "✅ KYC वेरिफाइड — सभी सेवाएँ उपलब्ध",
            "rejected": "❌ KYC रिजेक्ट — /kyc से फिर से करें"
        }
        await send_message(
            chat_id,
            f"📋 *आपका KYC स्टेटस*\n\n"
            f"{status_map.get(status, '❓ अज्ञात')}\n\n"
            f"मदद: @SinghJiSupport"
        )
        return {"status": "ok"}

    # ---- AGENT ----
    if text == "/agent":
        kyc_status = await _get_kyc_status(str(user_id))
        if kyc_status != "verified":
            await send_message(
                chat_id,
                "❌ *Agent बनने के लिए KYC ज़रूरी है!*\n\n"
                "पहले KYC करें: /kyc\n"
                "फिर Agent: /agent"
            )
            return {"status": "ok"}

        agent = await _get_agent_data(str(user_id))
        if agent:
            earnings = agent.get("total_earnings", 0)
            referrals = agent.get("total_referrals", 0)
            level = agent.get("level", "Bronze")
            available = earnings - agent.get("total_withdrawn", 0)

            levels = {"Bronze": 1000, "Silver": 5000, "Gold": 20000, "Platinum": 100000}
            target = levels.get(level, 1000)
            progress = min(100, int((earnings / target) * 100)) if target > 0 else 0
            bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

            await send_message(
                chat_id,
                f"🏆 *Agent Dashboard*\n\n"
                f"👤 Level: *{level}*\n"
                f"📊 Progress: [{bar}] {progress}%\n\n"
                f"💰 Total Earnings: ₹{earnings}\n"
                f"💵 Available: ₹{available}\n"
                f"👥 Referrals: {referrals}\n"
                f"📅 This Month: ₹{agent.get('month_earnings', 0)}\n\n"
                f"📋 Commands:\n"
                f"/referral — रेफरल लिंक\n"
                f"/withdraw — पैसे निकालें (min ₹100)"
            )
        else:
            await send_message(
                chat_id,
                f"🤝 *Singh Ji Agent Program*\n\n"
                f"Agent बनकर कमाएँ:\n"
                f"• 💰 UPI पेमेंट पर 0.5%\n"
                f"• 🏛️ GP सेवा शुल्क का 10%\n"
                f"• 📱 नया यूज़र रेफरल: ₹10\n"
                f"• 🎯 मंथली बोनस: ₹500+ ट्रांज़ैक्शन\n\n"
                f"रजिस्टर करने के लिए *YES* लिखें।"
            )
            KYC_SESSIONS[user_id] = {"step": "agent_register", "data": {}}
        return {"status": "ok"}

    # ---- AGENT REGISTER FLOW ----
    if user_id in KYC_SESSIONS and KYC_SESSIONS[user_id].get("step") == "agent_register":
        if text.lower() in ["yes", "haan", "हाँ", "y"]:
            # Auto-register via API
            try:
                url = f"{os.getenv('APP_URL', '')}/api/agent/register"
                payload = {
                    "telegram_id": str(user_id),
                    "name": f"Agent_{user_id}",
                    "phone": "0000000000",
                    "gram_panchayat": "Unknown"
                }
                resp = await HTTP_CLIENT.post(url, json=payload, timeout=15)
                if resp.status_code in [200, 201]:
                    result = resp.json()
                    await send_message(
                        chat_id,
                        f"🎉 *Agent रजिस्ट्रेशन सफल!*\n\n"
                        f"🆔 Agent ID: {result['data']['agent_id']}\n"
                        f"🏆 Level: {result['data']['level']}\n"
                        f"💳 UPI: {result['data']['upi_id']}\n\n"
                        f"📎 Referral Link:\n"
                        f"{result['data']['referral_link']}"
                    )
                else:
                    await send_message(chat_id, "❌ रजिस्ट्रेशन फेल। बाद में कोशिश करें।")
            except Exception as e:
                logger.error(f"Agent register error: {e}")
                await send_message(chat_id, "❌ रजिस्ट्रेशन में समस्या। /agent से फिर से करें।")
        else:
            await send_message(chat_id, "Agent रजिस्ट्रेशन रद्द। /agent से फिर से शुरू करें।")
        KYC_SESSIONS.pop(user_id, None)
        return {"status": "ok"}

    # ---- GRAM PANCHAYAT ----
    if text == "/grampanchayat":
        kyc_status = await _get_kyc_status(str(user_id))
        if kyc_status != "verified":
            await send_message(
                chat_id,
                "❌ *ग्राम पंचायत सेवाओं के लिए KYC ज़रूरी है!*\n\n"
                "पहले KYC करें: /kyc"
            )
            return {"status": "ok"}

        gp_text = (
            "🏛️ *ग्राम पंचायत सेवाएँ*\n\n"
            "KYC वेरिफाइड यूज़र के लिए उपलब्ध:\n\n"
            "📜 जाति प्रमाण पत्र\n"
            "🏠 निवास प्रमाण पत्र\n"
            "💍 विवाह प्रमाण पत्र\n"
            "🌾 किसान पंजीकरण\n"
            "💧 पानी कनेक्शन\n"
            "⚡ बिजली कनेक्शन\n\n"
            "सेवा शुल्क: ₹20-₹50\n"
            "Agent कमीशन: 10% ऑटो-स्प्लिट\n\n"
            "जल्द ही उपलब्ध होगा! 🚀"
        )
        await send_message(chat_id, gp_text)
        return {"status": "ok"}

    # ---- REFERRAL ----
    if text == "/referral":
        agent = await _get_agent_data(str(user_id))
        if agent:
            link = f"https://t.me/SinghJiAIBot?start=ref_{agent.get('id', '')}"
            await send_message(
                chat_id,
                f"📎 *आपका Referral Link*\n\n"
                f"{link}\n\n"
                f"हर नए Agent पर: ₹10 बोनस!\n"
                f"Share करें और कमाएँ! 💰"
            )
        else:
            await send_message(chat_id, "❌ पहले Agent बनें: /agent")
        return {"status": "ok"}

    # ---- WITHDRAW ----
    if text.startswith("/withdraw"):
        parts = text.replace("/withdraw", "").strip().split()
        if not parts:
            await send_message(
                chat_id,
                "❌ Format: /withdraw <amount>\n"
                "Example: /withdraw 500"
            )
            return {"status": "ok"}

        try:
            amount = float(parts[0])
            agent = await _get_agent_data(str(user_id))
            if not agent:
                await send_message(chat_id, "❌ पहले Agent बनें: /agent")
                return {"status": "ok"}

            available = agent.get("total_earnings", 0) - agent.get("total_withdrawn", 0)
            if amount < 100:
                await send_message(chat_id, "❌ Minimum withdrawal: ₹100")
                return {"status": "ok"}
            if amount > available:
                await send_message(chat_id, f"❌ Insufficient balance. Available: ₹{available}")
                return {"status": "ok"}

            # Call API
            url = f"{os.getenv('APP_URL', '')}/api/agent/withdraw"
            payload = {
                "agent_telegram_id": str(user_id),
                "amount": amount,
                "upi_id": agent.get("upi_id")
            }
            resp = await HTTP_CLIENT.post(url, json=payload, timeout=15)
            if resp.status_code in [200, 201]:
                result = resp.json()
                await send_message(
                    chat_id,
                    f"💸 *Withdrawal Requested*\n\n"
                    f"Amount: ₹{amount}\n"
                    f"UPI: {agent.get('upi_id')}\n"
                    f"Status: {result['data']['status']}\n"
                    f"ID: {result['data']['withdrawal_id']}\n\n"
                    f"24 घंटे में UPI पर पैसे मिलेंगे! ✅"
                )
            else:
                await send_message(chat_id, "❌ Withdrawal fail. बाद में कोशिश करें।")
        except ValueError:
            await send_message(chat_id, "❌ Invalid amount. Example: /withdraw 500")
        except Exception as e:
            logger.error(f"Withdraw error: {e}")
            await send_message(chat_id, "❌ Withdrawal error. /withdraw <amount> से फिर से करें।")
        return {"status": "ok"}

    # ---- WEATHER ----
    if text.startswith("/weather "):
        city = text.replace("/weather ", "").strip()
        if not city:
            await send_message(chat_id, "❌ Please provide a city name. Example: /weather Delhi")
            return {"status": "ok"}

        if OPENWEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                resp = await HTTP_CLIENT.get(url, timeout=15)
                data = resp.json()
                if resp.status_code == 200:
                    weather_text = (
                        f"🌤️ Weather in {city}\n\n"
                        f"🌡️ Temp: {data['main']['temp']}°C\n"
                        f"💧 Humidity: {data['main']['humidity']}%\n"
                        f"🌬️ Wind: {data['wind']['speed']} m/s\n"
                        f"☁️ {data['weather'][0]['description'].title()}"
                    )
                    await send_message(chat_id, weather_text)
                else:
                    await send_message(chat_id, f"❌ City not found: {city}")
            except Exception as e:
                await send_message(chat_id, f"❌ Weather error: {str(e)[:100]}")
        else:
            await send_message(chat_id, "❌ Weather API key missing")
        return {"status": "ok"}

    # ---- NEWS ----
    if text == "/news":
        try:
            import modules.news.handler as news_module
            news_text = "📰 Latest News\n\n" + await news_module.get_news_digest_text(count=5)
            await send_message(chat_id, news_text)
        except Exception as e:
            await send_message(chat_id, f"❌ News error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- MANDI ----
    if text.startswith("/mandi"):
        raw_state = text.replace("/mandi", "").strip()
        if not raw_state:
            await send_message(chat_id, "❌ Please provide a state. Example: /mandi Punjab")
            return {"status": "ok"}

        state = _normalize_state(raw_state)
        if DATA_GOV_API_KEY:
            try:
                params = {
                    "api-key": DATA_GOV_API_KEY,
                    "format": "json",
                    "limit": 10,
                    "filters[state.keyword]": state
                }
                resp = await HTTP_CLIENT.get(MANDI_BASE_URL, params=params, timeout=45)
                data = resp.json()

                if "error" in data:
                    await send_message(chat_id, f"❌ Mandi API error: {data.get('error', 'Unknown')}")
                    return {"status": "ok"}

                records = data.get("records", [])
                if not records:
                    await send_message(chat_id, f"❌ {state} ke liye data nahi mila\n\nTry karo:\n/mandi Punjab\n/mandi Haryana\n/mandi UP")
                    return {"status": "ok"}

                mandi_text = f"🌾 Mandi Bhav — {state}\n\n"
                for i, record in enumerate(records[:5], 1):
                    commodity = record.get("commodity", "Unknown")
                    modal = record.get("modal_price", "N/A")
                    min_p = record.get("min_price", "N/A")
                    max_p = record.get("max_price", "N/A")
                    market = record.get("market", "N/A")
                    district = record.get("district", "N/A")
                    mandi_text += f"{i}. {commodity}\n"
                    mandi_text += f"   ₹{modal}/q (₹{min_p}-₹{max_p})\n"
                    mandi_text += f"   📍 {market}, {district}\n\n"
                await send_message(chat_id, mandi_text)
            except Exception as e:
                await send_message(chat_id, f"❌ Mandi error: {str(e)[:200]}")
        else:
            await send_message(chat_id, "❌ Mandi API key missing (DATAGOVINDIA_API_KEY)")
        return {"status": "ok"}

    # ---- TAX ----
    if text.startswith("/tax "):
        try:
            income = float(text.replace("/tax ", "").strip())
            r = _calculate_tax(income, "new")
            tax_text = (
                f"💰 Tax Calculation\n\n"
                f"Income: ₹{r['income']:,.0f}\n"
                f"Tax: ₹{r['tax']:,.2f}\n"
                f"Cess: ₹{r['cess']:,.2f}\n"
                f"Total Tax: ₹{r['total']:,.2f}\n"
                f"Take Home: ₹{r['take_home']:,.2f}"
            )
            await send_message(chat_id, tax_text)
        except ValueError:
            await send_message(chat_id, "❌ Invalid income. Example: /tax 500000")
        except Exception as e:
            await send_message(chat_id, f"❌ Tax error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- GOLD ----
    if text.startswith("/gold"):
        city = text.replace("/gold", "").strip() or "delhi"
        try:
            from modules.goldrate.handler import gold_rate_city
            resp = await gold_rate_city(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            cr = d.get("city_rates", {})
            gold_text = (
                f"🥇 Gold Rate - {cr.get('city', city.title())}\n\n"
                f"24K (1g): ₹{cr.get('price_gram_24k', 'N/A')}\n"
                f"22K (1g): ₹{cr.get('price_gram_22k', 'N/A')}\n"
                f"24K (10g): ₹{cr.get('price_10g_24k', 'N/A')}\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await send_message(chat_id, gold_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Gold error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- FUEL ----
    if text.startswith("/fuel"):
        city = text.replace("/fuel", "").strip() or "delhi"
        try:
            from modules.fuel.handler import fuel_price
            resp = await fuel_price(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            fuel_text = (
                f"⛽ Fuel Price - {d.get('city', city.title())}\n\n"
                f"Petrol: ₹{d.get('petrol', 'N/A')}/L\n"
                f"Diesel: ₹{d.get('diesel', 'N/A')}/L\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await send_message(chat_id, fuel_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Fuel error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- HOROSCOPE ----
    if text.startswith("/horoscope"):
        rashi = text.replace("/horoscope", "").strip() or "मेष"
        try:
            from modules.horoscope.handler import get_horoscope, format_telegram as _format_horoscope_telegram
            h = get_horoscope(rashi, "daily", "hi")
            horo_text = _format_horoscope_telegram(h)
            await send_message(chat_id, horo_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Horoscope error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- CURRENCY ----
    if text.startswith("/currency"):
        parts = text.replace("/currency", "").strip().split()
        try:
            from modules.currency.handler import singhji_currency
            if len(parts) == 1:
                try:
                    amount = float(parts[0])
                    base, target = "USD", "INR"
                except ValueError:
                    base, target, amount = parts[0].upper(), "INR", 1.0
            else:
                base = parts[0].upper() if len(parts) > 0 else "USD"
                target = parts[1].upper() if len(parts) > 1 else "INR"
                amount = float(parts[2]) if len(parts) > 2 else 1.0

            result = await singhji_currency.convert(base, target, amount)
            cur_text = (
                f"💱 Currency Convert\n\n"
                f"{amount} {base} = {result.converted} {target}\n"
                f"Rate: 1 {base} = {result.rate} {target}"
            )
            await send_message(chat_id, cur_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Currency error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- ROZGAR ----
    if text.startswith("/rozgar"):
        raw = text.replace("/rozgar", "").strip()
        try:
            from modules.rozgar import handler as rozgar_module
            parts = raw.split()
            known_countries = set(rozgar_module.PORTALS["regional"].keys())
            country = ""
            keyword_parts = []
            for p in parts:
                if p.upper() in known_countries and not country:
                    country = p.upper()
                else:
                    keyword_parts.append(p)
            keyword = " ".join(keyword_parts).strip().lower()
            search_term = rozgar_module.KEYWORD_MAP.get(keyword, keyword) if keyword else ""

            if keyword and country:
                result = rozgar_module._search_keyword(keyword, search_term)
                result = rozgar_module._filter_by_country(result, country)
            elif keyword:
                result = rozgar_module._search_keyword(keyword, search_term)
            elif country:
                result = rozgar_module._country_only(country)
            else:
                result = {"global": [], "regional": [], "govt": [], "categories": []}

            rozgar_text = "💼 Rozgar/Jobs\n\n"
            for section, label in [("govt", "🏛️ Government"), ("regional", "📍 Regional"), ("global", "🌐 Global")]:
                for entry in result.get(section, [])[:5]:
                    name = entry.get("name", "")
                    site = entry.get("site", "")
                    rozgar_text += f"{label}: {name} — {site}\n"

            if not any(result.get(s) for s in ("govt", "regional", "global")):
                rozgar_text += "No results found. Example: /rozgar software IN"
            await send_message(chat_id, rozgar_text[:4000])
        except Exception as e:
            await send_message(chat_id, f"❌ Rozgar error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- TRANSLATE ----
    if text.startswith("/translate "):
        parts = text.replace("/translate ", "").strip().split(" ", 1)
        try:
            from modules.language.handler import LanguageModule
            LANG_MODULE = LanguageModule()
            target_lang = parts[0].lower()
            to_translate = parts[1] if len(parts) > 1 else ""
            if not to_translate:
                await send_message(chat_id, "Format: /translate en Namaste kaise ho")
                return {"status": "ok"}

            result = await run_in_threadpool(LANG_MODULE.translate, to_translate, target_lang, "auto")
            if result.get("success"):
                await send_message(chat_id, f"🔤 Translation ({result.get('target_name', target_lang)})\n\n{result['translated']}")
            else:
                await send_message(chat_id, f"❌ Translate error: {result.get('error', 'unknown')[:100]}")
        except Exception as e:
            await send_message(chat_id, f"❌ Translate error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- SEARCH ----
    if text.startswith("/search"):
        query = text.replace("/search", "").strip()
        if not query:
            await send_message(chat_id, "❌ Please provide a search query. Example: /search AI news")
            return {"status": "ok"}

        try:
            import services.travily_search as travily_search_service
            results = await travily_search_service.search(query)
            search_text = f"🔍 Search: {query}\n\n"
            for i, r in enumerate(results[:5], 1):
                search_text += f"{i}. {r.get('title', 'No title')}\n   {r.get('url', '')}\n\n"
            if not results:
                search_text += "No results found"
            await send_message(chat_id, search_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Search error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- EMERGENCY ----
    if text.startswith("/emergency"):
        type_ = text.replace("/emergency", "").strip().lower()
        try:
            from modules.emergency.handler import EMERGENCY_DATA
            if type_ and type_ in EMERGENCY_DATA:
                v = EMERGENCY_DATA[type_]
                emg_text = f"🚨 {type_.title()}\n\nNumber: {v['number']}"
                if v.get("alt"):
                    emg_text += f"\nAlt: {v['alt']}"
                emg_text += f"\n{v.get('info', '')}"
            else:
                emg_text = "🚨 Emergency Numbers\n\n"
                for k, v in EMERGENCY_DATA.items():
                    emg_text += f"{k.title()}: {v['number']}"
                    if v.get("alt"):
                        emg_text += f" / {v['alt']}"
                    emg_text += "\n"
            await send_message(chat_id, emg_text)
        except Exception as e:
            await send_message(chat_id, f"Emergency error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- UPI ----
    if text == "/upi":
        upi_id = os.getenv("UPI_ID", "jp200883@sbi")
        upi_text = (
            f"💳 UPI Info\n\n"
            f"UPI ID: {upi_id}\n"
            f"Apps: PhonePe, Google Pay, Paytm, BHIM\n"
            f"Daily Limit: ₹1,00,000"
        )
        await send_message(chat_id, upi_text)
        return {"status": "ok"}

      # ---- AI CHAT ----
    if text.startswith("/ai "):
        prompt = text.replace("/ai ", "").strip()
        if not prompt:
            await send_message(chat_id, "❌ Please provide a question. Example: /ai India ka capital kya hai?")
            return {"status": "ok"}

        try:
            from api.ai import get_brain
            await send_message(chat_id, "🤔 Thinking...")
            brain = get_brain()
            result = await brain.get_best_response(prompt, str(user_id))

            if result.get("status") == "success":
                ai_response = result.get("response", "Bhai kuch gadbad ho gayi.")
                source = result.get("source", "UNKNOWN")
                human_score = result.get("human_score", 0)
                latency = result.get("latency_sec", 0)

                # Truncate if too long for Telegram
                ai_response = ai_response[:4000]

                reply_text = ai_response
                await send_message(chat_id, reply_text)

                # Save to memory with full metadata
                await _memory_save(
                    f"telegram_chat:{user_id}:{int(datetime.now().timestamp())}",
                    {
                        "prompt": prompt,
                        "response": ai_response,
                        "source": source,
                        "human_score": human_score,
                        "latency_sec": latency,
                        "all_scores": result.get("all_scores", {}),
                        "all_sources": result.get("all_sources", [])
                    }
                )
            else:
                error_msg = result.get("response", "Kuch gadbad ho gayi.")
                await send_message(chat_id, f"❌ AI Error: {error_msg}")

        except Exception as e:
            logger.error(f"AI chat error: {e}")
            await send_message(chat_id, f"❌ AI Error: {str(e)[:200]}")
        return {"status": "ok"}
    # ---- BROADCAST (Admin only) ----
    if text.startswith("/broadcast "):
        if user_id != ADMIN_USER_ID:
            await send_message(chat_id, "⛔ Admin only command")
            return {"status": "ok"}

        broadcast_text = text.replace("/broadcast ", "").strip()
        if not broadcast_text:
            await send_message(chat_id, "❌ Please provide a message. Example: /broadcast Hello everyone!")
            return {"status": "ok"}

        if MASTER_SCHEDULER:
            await MASTER_SCHEDULER._broadcast_with_rate_limit(f"📢 Broadcast\n\n{broadcast_text}")
            await send_message(chat_id, f"✅ Broadcast sent to {len(USER_PREFERENCES)} users")
        else:
            await send_message(chat_id, "❌ Scheduler not initialized")
        return {"status": "ok"}

    # ---- UNKNOWN COMMAND ----
    await send_message(chat_id, "❌ Unknown command. Type /help for available commands")
    return {"status": "ok"}
