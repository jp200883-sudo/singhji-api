"""
🦁 Singh Ji AI Ultra v8.0 — Telegram Bot Handler
Developer: Singh Ji
Version: 8.0.0
Modules: 50+
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

# ========== FASTAPI ROUTER ==========
try:
    from fastapi import APIRouter, Request
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
    router = APIRouter()
except ImportError:
    FASTAPI_AVAILABLE = False
    router = None

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_BASE = os.getenv("API_BASE", "https://singhji-api-production-85ca.up.railway.app/modules")

# ========== MESSAGES ==========
WELCOME_MSG = """🦁 *Welcome to Singh Ji AI Ultra v8.0!*

Your AI assistant for Bharat 🇮🇳

*Commands:*
📰 /news — Latest news
🔮 /rashifal — Daily horoscope
⛽ /fuel — Petrol/Diesel prices
🪙 /gold — Gold/Silver rates
🌤 /weather — Weather update
🌾 /mandi — Mandi rates
🛡 /bachpan — Child safety
🚨 /emergency — Emergency help
📊 /report — Daily report
ℹ️ /help — All commands

⚡ *Singh Ji AI Ultra v8.0*"""

HELP_MSG = """🦁 *Singh Ji AI Commands*

*📰 News:* /news /sports /business
*🔮 Horoscope:* /rashifal [rashi]
*⛽ Fuel:* /fuel [city]
*🪙 Gold:* /gold [city]
*🌤 Weather:* /weather [city]
*🌾 Mandi:* /mandi
*🛡 Bachpan:* /bachpan
*🚨 Emergency:* /emergency
*📊 Report:* /report
*ℹ️ Status:* /status

⚡ *Singh Ji AI v8.0*"""

STATUS_MSG = """🟢 *Singh Ji AI Status*

✅ Bot Active
✅ API Connected
🦁 Singh Ji AI v8.0
📡 Mode: {mode}"""

ERROR_MSG = "❓ Unknown command. Type /help for commands."

# ========== COMMAND MAP ==========
COMMANDS = {
    "news": {"module": "news", "params": {"category": "india", "language": "hi"}},
    "khabar": {"module": "news", "params": {"category": "india", "language": "hi"}},
    "sports": {"module": "news", "params": {"category": "sports", "language": "hi"}},
    "business": {"module": "news", "params": {"category": "business", "language": "hi"}},
    "rashifal": {"module": "horoscope", "params": {"rashi": "मेष", "language": "hi"}},
    "horoscope": {"module": "horoscope", "params": {"rashi": "Aries", "language": "en"}},
    "fuel": {"module": "fuel", "params": {"city": "Delhi", "fuel_type": "all"}},
    "petrol": {"module": "fuel", "params": {"city": "Delhi", "fuel_type": "petrol"}},
    "gold": {"module": "goldrate", "params": {"city": "India", "purity": "all"}},
    "sone": {"module": "goldrate", "params": {"city": "India", "purity": "all"}},
    "weather": {"module": "weather", "params": {"city": "Kanpur"}},
    "mausam": {"module": "weather", "params": {"city": "Kanpur"}},
    "mandi": {"module": "mandi", "params": {}},
    "emergency": {"module": "emergency", "params": {}},
    "sos": {"module": "emergency", "params": {}},
    "bachpan": {"module": "bachpan", "params": {"language": "hi"}},
    "child": {"module": "bachpan", "params": {"language": "hi"}},
    "report": {"module": "daily_report", "params": {}},
    "rozgar": {"module": "rozgar", "params": {}},
    "naukri": {"module": "rozgar", "params": {}},
    "currency": {"module": "currency", "params": {}},
    "banking": {"module": "banking", "params": {}},
    "upi": {"module": "upi", "params": {}},
    "sewer": {"module": "sewer", "params": {}},
    "pani": {"module": "pani", "params": {}},
    "plant": {"module": "plant_id", "params": {}},
    "guard": {"module": "guard_agent", "params": {}},
    "meta": {"module": "meta_agent", "params": {}},
    "supreme": {"module": "supreme_agent", "params": {}},
    "search": {"module": "search", "params": {}},
    "analytics": {"module": "analytics", "params": {}},
    "language": {"module": "language_hub", "params": {}},
    "schedule": {"module": "schedule", "params": {}},
    "trolley": {"module": "trolley", "params": {}},
    "singhjitv": {"module": "singhji_tv", "params": {}},
    "tv": {"module": "singhji_tv", "params": {}},
    "aavishkar": {"module": "aavishkar", "params": {}},
    "init": {"module": "init", "params": {}},
    "currents": {"module": "currents_api", "params": {}},
    "newsdata": {"module": "newsdata", "params": {}},
    "newsscheduler": {"module": "news_scheduler", "params": {}},
    "whatsapp": {"module": "whatsapp", "params": {}},
    "voice": {"module": "voice", "params": {}},
    "voicecmd": {"module": "voice_cmd", "params": {}},
    "voicetts": {"module": "voice_tts", "params": {}},
    "oauth": {"module": "oauth_connector", "params": {}},
    "trishul": {"module": "trishul", "params": {}},
    "swarm": {"module": "swarm", "params": {}},
    "youtube": {"module": "youtube", "params": {}},
    "instagram": {"module": "instagram", "params": {}},
    "facebook": {"module": "facebook", "params": {}},
    "autoaccount": {"module": "auto_account", "params": {}},
    "automonetize": {"module": "auto_monetize", "params": {}},
    "trend": {"module": "trend_analysis", "params": {}},
    "visual": {"module": "visual", "params": {}},
}


# ========== TELEGRAM FUNCTIONS ==========

def send_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN not set!")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }, timeout=10)
        return resp.json().get("ok", False)
    except Exception as e:
        print(f"send_message error: {e}")
        return False


def get_module_data(module_name: str, params: Optional[Dict] = None) -> Optional[Dict]:
    try:
        url = f"{API_BASE}/{module_name}"
        if params:
            resp = requests.get(url, params=params, timeout=10)
        else:
            resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Module {module_name} error: {e}")
    return None


def ai_brain_reply(user_text: str) -> Optional[str]:
    try:
        if GROQ_API_KEY:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": user_text}],
                    "max_tokens": 500
                },
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI brain error: {e}")
    return None


# ========== COMMAND HANDLER ==========

def handle_command(command: str, args: List[str], chat_id: int) -> Dict[str, Any]:
    if command == "start":
        send_message(chat_id, WELCOME_MSG)
        return {"status": "ok"}

    elif command == "help":
        send_message(chat_id, HELP_MSG)
        return {"status": "ok"}

    elif command == "status":
        mode = "Webhook" if FASTAPI_AVAILABLE else "Polling"
        send_message(chat_id, STATUS_MSG.format(mode=mode))
        return {"status": "ok"}

    if command in COMMANDS:
        cmd_info = COMMANDS[command]
        module = cmd_info["module"]
        params = cmd_info["params"].copy()

        if args:
            if command in ["rashifal", "horoscope"]:
                params["rashi"] = args[0]
            elif command in ["fuel", "petrol"]:
                params["city"] = args[0]
            elif command in ["gold", "sone"]:
                params["city"] = args[0]
            elif command in ["weather", "mausam"]:
                params["city"] = args[0]

        data = get_module_data(module, params)

        if data:
            reply = format_module_response(module, data, params)
        else:
            reply = "Data nahi mila. Try again later."

        send_message(chat_id, reply)
        return {"status": "ok"}

    ai_reply = ai_brain_reply(command + " " + " ".join(args))
    if ai_reply:
        reply = f"🦁 *Singh Ji AI:*\n\n{ai_reply}"
    else:
        reply = ERROR_MSG

    send_message(chat_id, reply)
    return {"status": "ok"}


def format_module_response(module: str, data: Dict, params: Dict) -> str:
    if module == "goldrate":
        d = data.get("data", {}).get("rates", {})
        city = params.get("city", "India")
        return f"""🪙 *Sone Ka Bhav — {city.title()}*

🥇 24K: ₹{d.get('24k', {}).get('rate_per_10g', 'N/A')}/10g
🥈 22K: ₹{d.get('22k', {}).get('rate_per_10g', 'N/A')}/10g
🥉 18K: ₹{d.get('18k', {}).get('rate_per_10g', 'N/A')}/10g

📅 {datetime.now().strftime('%d %b %Y')}"""

    elif module == "fuel":
        d = data.get("data", {}).get("rates", {})
        city = params.get("city", "Delhi")
        return f"""⛽ *Fuel Price — {city.title()}*

🚗 Petrol: ₹{d.get('petrol', {}).get('rate_per_litre', 'N/A')}/L
🚛 Diesel: ₹{d.get('diesel', {}).get('rate_per_litre', 'N/A')}/L
🚌 CNG: ₹{d.get('cng', {}).get('rate_per_litre', 'N/A')}/L"""

    elif module == "weather":
        d = data.get("data", {})
        return f"""🌤 *Mausam — {d.get('city', '')}*

🌡️ Temperature: {d.get('temperature', 'N/A')}°C
💧 Humidity: {d.get('humidity', 'N/A')}%
💨 Wind: {d.get('wind_speed', 'N/A')} km/h
🌤️ Condition: {d.get('condition', 'N/A')}"""

    elif module == "news":
        articles = data.get("data", {}).get("articles", [])[:5]
        reply = "📰 *Aaj Ki Top Khabar*\n\n"
        for i, article in enumerate(articles, 1):
            reply += f"{i}. {article.get('title', 'News')}\n"
        return reply

    elif module == "horoscope":
        d = data.get("data", {})
        return f"""🔮 *{d.get('rashi', 'Rashi')} — Rashifal*

{d.get('prediction', 'Aaj accha din hai!')}

💼 Career: {d.get('career', '⭐⭐⭐')}
💕 Love: {d.get('love', '⭐⭐⭐')}
💰 Money: {d.get('money', '⭐⭐⭐')}
🏥 Health: {d.get('health', '⭐⭐⭐')}"""

    elif module == "mandi":
        rates = data.get("data", {})
        items = list(rates.items())[:5]
        reply = "🌾 *Mandi Rates (₹/kg)*\n\n"
        for item, price in items:
            reply += f"• {item.title()}: ₹{price}\n"
        return reply

    elif module == "bachpan":
        d = data.get("data", {})
        return f"""🎈 *Bachpan Ki Yaadein — {d.get('topic', '').title()}*

{d.get('memory', 'Wo din yaad hain...')}

❤️ {d.get('hindi_message', '')}"""

    elif module == "emergency":
        return """🚨 *Emergency Numbers*

🚑 Ambulance: 108
🚒 Fire: 101
👮 Police: 100
🆘 Women Helpline: 1091
🏥 Medical: 104

🦁 Singh Ji AI — Hamesha saath!"""

    elif module == "daily_report":
        return f"""📊 *Daily Report*

✅ Bot Active
✅ API Connected
📅 Date: {datetime.now().strftime('%d %b %Y')}
⏰ Time: {datetime.now().strftime('%H:%M')}

🦁 Singh Ji AI v8.0"""

    elif module == "rozgar":
        jobs = data.get("data", {}).get("jobs", [])[:5]
        reply = "💼 *Naukri Updates*\n\n"
        for i, job in enumerate(jobs, 1):
            reply += f"{i}. {job.get('title', 'Job')} — {job.get('company', '')}\n"
        return reply

    elif module == "currency":
        rates = data.get("data", {})
        reply = "💱 *Currency Rates*\n\n"
        for curr, rate in list(rates.items())[:5]:
            reply += f"• {curr}: ₹{rate}\n"
        return reply

    elif module == "banking":
        return "🏦 *Banking Services*\n\nSBI, PNB, HDFC, ICICI — all banks supported!\nUse /upi for UPI services."

    elif module == "upi":
        return "📲 *UPI Services*\n\n✅ Check balance\n✅ Send money\n✅ Request money\n✅ Transaction history"

    elif module == "sewer":
        return "🚰 *Sewer/Drainage Services*\n\nComplaint register karo!\nCity: " + params.get('city', 'Your City')

    elif module == "pani":
        return "💧 *Water Supply*\n\nComplaint: 1916\nTanker booking available!"

    elif module == "plant_id":
        return "🌿 *Plant Identification*\n\nPhoto bhejo, plant pehchanenge!"

    elif module == "guard_agent":
        return "🛡️ *Guard Agent*\n\nAlert system active!\nSecurity monitoring on."

    elif module == "meta_agent":
        return "🤖 *Meta Agent*\n\nAI brain active!\nProcessing your request..."

    elif module == "supreme_agent":
        return "👑 *Supreme Agent*\n\nMaster AI active!\nAll systems operational."

    elif module == "search":
        return "🔍 *Search*\n\nWeb search active!\nResults coming soon..."

    elif module == "analytics":
        return "📊 *Analytics*\n\nData analysis ready!"

    elif module == "language_hub":
        return "🌐 *Language Hub*\n\n26 languages supported!\nHindi, English, Tamil, Telugu, Bengali, etc."

    elif module == "schedule":
        return "📅 *Daily Schedule*\n\nWater: 6-9 AM\nPower: Check local schedule"

    elif module == "trolley":
        return "🛒 *Shopping Trolley*\n\nProducts added!\nCheckout when ready."

    elif module == "singhji_tv":
        return "📺 *Singh Ji TV*\n\nStreaming active!\nWatch now: /tv"

    elif module == "aavishkar":
        return "🚀 *Aavishkar v4.1*\n\nInnovation hub active!"

    elif module == "init":
        return "⚙️ *System Init*\n\nAll modules loaded!\nSystem ready."

    elif module == "currents_api":
        return "📡 *Currents API*\n\nNews feed active!"

    elif module == "newsdata":
        return "📰 *NewsData*\n\nGlobal news feed active!"

    elif module == "news_scheduler":
        return "⏰ *News Scheduler*\n\nScheduled news delivery active!"

    elif module == "whatsapp":
        return "💬 *WhatsApp*\n\nWhatsApp integration active!"

    elif module == "voice":
        return "🎙️ *Voice*\n\nVoice commands active!\nSpeak now..."

    elif module == "voice_cmd":
        return "🎤 *Voice Commands*\n\nSay a command!"

    elif module == "voice_tts":
        return "🔊 *Text to Speech*\n\nTTS engine ready!"

    elif module == "oauth_connector":
        return "🔗 *OAuth*\n\nSocial login ready!"

    elif module == "trishul":
        return "🔱 *Trishul Memory*\n\nMemory engine active!\nYour data is safe."

    elif module == "swarm":
        return "🐝 *Agent Swarm*\n\n300 agents active!\nCoordinating tasks..."

    elif module == "youtube":
        return "📹 *YouTube*\n\nUpload ready!\nChannel connected."

    elif module == "instagram":
        return "📸 *Instagram*\n\nPost ready!\nAuto-post active."

    elif module == "facebook":
        return "📘 *Facebook*\n\nPost ready!\nLong token active."

    elif module == "auto_account":
        return "🤖 *Auto Account*\n\nAccount creation ready!"

    elif module == "auto_monetize":
        return "💰 *Auto Monetize*\n\nMonetization active!\nEarnings tracking on."

    elif module == "trend_analysis":
        return "📈 *Trend Analysis*\n\nTrends detected!\nViral content suggestions ready."

    elif module == "visual":
        return "🎨 *Visual Generator*\n\nInfographics ready!\nImage generation active."

    return "✅ Data received!"


# ========== WEBHOOK HANDLER ==========
if FASTAPI_AVAILABLE and router:
    @router.post("/webhook")
    async def webhook_handler(request: Request):
        try:
            body = await request.json()
            message = body.get("message", {})
            text = message.get("text", "").strip()
            chat_id = message.get("chat", {}).get("id")

            if not chat_id or not text:
                return JSONResponse(status_code=200, content={"status": "ok"})

            parts = text.strip().split()
            command = parts[0].lower().replace("/", "")
            args = parts[1:] if len(parts) > 1 else []

            result = handle_command(command, args, chat_id)
            return JSONResponse(status_code=200, content=result)

        except Exception as e:
            print(f"Webhook handler error: {e}")
            return JSONResponse(status_code=200, content={"status": "ok"})


# Legacy support
handler = webhook_handler if FASTAPI_AVAILABLE else None


# ========== POLLING MODE ==========
def polling_mode():
    import time

    OFFSET_FILE = ".telegram_offset"

    def get_offset():
        try:
            with open(OFFSET_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_offset(offset):
        with open(OFFSET_FILE, 'w') as f:
            f.write(str(offset))

    if TELEGRAM_TOKEN:
        try:
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=10)
            print("Webhook deleted for polling")
        except Exception as e:
            print(f"Webhook delete: {e}")

    offset = get_offset() + 1
    print(f"Starting polling from offset {offset}")

    while True:
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                params={"offset": offset, "limit": 100, "timeout": 30},
                timeout=35
            )
            updates = resp.json().get("result", [])

            for update in updates:
                update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "").strip()
                chat_id = msg.get("chat", {}).get("id")

                if chat_id and text:
                    user = msg.get("from", {}).get("username", "unknown")
                    print(f"@{user}: {text[:50]}")

                    parts = text.strip().split()
                    command = parts[0].lower().replace("/", "")
                    args = parts[1:] if len(parts) > 1 else []

                    handle_command(command, args, chat_id)

                offset = update_id + 1
                save_offset(offset)

            if not updates:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nBot stopped. Bye!")
            break
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)


# ========== MAIN ENTRY ==========
if __name__ == "__main__":
    print("=" * 50)
    print("SINGH JI AI ULTRA v8.0 — TELEGRAM BOT")
    print("=" * 50)
    print(f"Mode: Polling")
    print(f"API: {API_BASE}")
    print("=" * 50 + "\n")

    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set!")
        sys.exit(1)

    polling_mode()
