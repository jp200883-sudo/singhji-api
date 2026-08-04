# telegram/buttons.py
import logging
from datetime import datetime
from core.config import AVAILABLE_KEYS
from core.swarm import SMART_SWARM
from core.scheduler import USER_PREFERENCES
from tg_bot.helpers import send_message

logger = logging.getLogger(__name__)

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
}

# ==========================================
# INSTANT REPLY BUTTONS
# ==========================================
async def handle_button(chat_id, user_id, query_data):
    # ---- INPUT BUTTONS ----
    if query_data in INPUT_BUTTONS:
        label, prompt = INPUT_BUTTONS[query_data]
        USER_PREFERENCES.setdefault(user_id, {})["waiting_for"] = query_data
        await send_message(chat_id, f"{label}\n\n{prompt}")
        return {"status": "ok"}

    # ---- STATUS ----
    if query_data == "status":
        status = SMART_SWARM.get_status()
        api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
        text = (
            f"📊 Singh Ji AI Status\n\n"
            f"🤖 Agents: {status['currently_loaded']}/330\n"
            f"⚡ Active: {status['active_running']}\n"
            f"😴 Idle: {status['idle']}\n"
            f"🔌 APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
            f"👥 Users: {len(USER_PREFERENCES)}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
        await send_message(chat_id, text)
        return {"status": "ok"}

    # ---- NEWS ----
    if query_data == "news":
        try:
            import modules.news.handler as news_module
            text = "📰 Latest News\n\n" + await news_module.get_news_digest_text(count=5)
            await send_message(chat_id, text)
        except Exception as e:
            await send_message(chat_id, f"❌ News error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- EMERGENCY ----
    if query_data == "emergency":
        try:
            from modules.emergency.handler import EMERGENCY_DATA
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
    if query_data == "upi":
        upi_id = os.getenv("UPI_ID", "jp200883@sbi")
        await send_message(chat_id, f"💳 UPI Info\n\nUPI ID: {upi_id}\nApps: PhonePe, GPay, Paytm, BHIM")
        return {"status": "ok"}

    # ---- HELP ----
    if query_data == "help":
        help_text = (
            "📚 Singh Ji AI Commands\n\n"
            "🌤️ /weather Delhi\n"
            "📰 /news\n"
            "🌾 /mandi UP\n"
            "💰 /tax 500000\n"
            "🥇 /gold Delhi\n"
            "⛽ /fuel Delhi\n"
            "🔮 /horoscope मेष\n"
            "💱 /currency USD INR 100\n"
            "🔍 /search AI news\n"
            "🔤 /translate en Namaste\n"
            "🤖 /ai question\n"
            "📊 /status\n"
        )
        await send_message(chat_id, help_text)
        return {"status": "ok"}

    # ---- AI CHAT ----
    if query_data == "ai_chat":
        await send_message(chat_id, "🤖 AI Chat\n\nKuch bhi poochho! Main jawab dunga.")
        return {"status": "ok"}

    # ---- VOICE ----
    if query_data == "voice":
        await send_message(chat_id, "🎤 Voice AI\n\nVoice message bhejo! Main transcribe karunga.")
        return {"status": "ok"}

    # ---- PLANT DOCTOR ----
    if query_data == "plant":
        await send_message(chat_id, "🌿 Plant Doctor\n\nPlant ki photo bhejo! Disease detect karunga.")
        return {"status": "ok"}

    # ---- GOVT SCHEMES ----
    if query_data == "govt":
        govt_text = (
            "🏛️ Govt Services\n\n"
            "/govt aadhaar — Aadhaar services\n"
            "/govt pan — PAN card\n"
            "/govt passport — Passport\n"
            "/govt voter — Voter ID\n"
            "/govt ration — Ration card\n"
            "/govt driving — Driving license\n"
            "/govt ayushman — Ayushman Bharat\n"
            "/govt pmkisan — PM Kisan"
        )
        await send_message(chat_id, govt_text)
        return {"status": "ok"}

    # ---- GUARD AGENT ----
    if query_data == "guard":
        try:
            from modules.guard_agent.handler import singhji_guard
            g = singhji_guard
            guard_text = (
                f"🛡️ Guard Agent\n\n"
                f"📹 Cameras: {len(g.cameras_db)}\n"
                f"🚨 Alerts: {len(g.alerts_db)}\n"
                f"🔍 Detection: vehicle, human, sound, face, ANPR, fire, crowd"
            )
            await send_message(chat_id, guard_text)
        except Exception as e:
            await send_message(chat_id, f"🛡️ Guard Agent\n\nStatus: Loading...\n{str(e)[:80]}")
        return {"status": "ok"}

    # ---- SOCIAL AGENT ----
    if query_data == "social":
        try:
            from modules.social_agent import core as social_core
            s = social_core.SOCIAL_AGENT
            if s:
                cfg = s.get_stats()["platforms_configured"]
                live = ", ".join(p for p, v in cfg.items() if v) or "none"
                social_text = (
                    f"📱 Social Agent\n\n"
                    f"📤 Posts: {len(s.posted_history)}\n"
                    f"🟢 Live: {live}"
                )
            else:
                social_text = "📱 Social Agent\n\nStatus: Initializing..."
            await send_message(chat_id, social_text)
        except Exception as e:
            await send_message(chat_id, f"📱 Social Agent\n\nStatus: {str(e)[:80]}")
        return {"status": "ok"}

    # ---- DEFAULT ----
    await send_message(chat_id, f"✅ Command received: {query_data}")
    return {"status": "ok"}
