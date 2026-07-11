"""
Singh Ji AI Ultra v8.0 — Telegram Bot Handler
Developer: Singh Ji
Version: 8.0.0
Modules: 15 (v7.0) + Mini-Program (v8.0)
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

# FastAPI imports (for webhook mode)
try:
    from fastapi import Request
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_BASE = os.getenv("API_BASE", "https://singhji-api.onrender.com/api")
MINI_PROGRAM_URL = os.getenv("MINI_PROGRAM_URL", "https://singhji.ai/mini")

# ========== MESSAGES v8.0 ==========
WELCOME_MSG = """🦁 *Welcome to Singh Ji AI Ultra v8.0!*

Your AI assistant for Bharat 🇮🇳

*📱 New in v8.0:*
🛠 /mini — Mini-Program Portal
🤖 AI Chat — Groq powered
🌐 26 Languages
🎙️ Voice Support

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
🛠 /mini — Mini-Program portal
ℹ️ /help — All commands

⚡ *Singh Ji AI Ultra v8.0*"""

HELP_MSG = """🦁 *Singh Ji AI Commands v8.0*

*📰 News:*
/news — India news
/sports — Sports news
/business — Business news

*🔮 Horoscope:*
/rashifal [rashi] — Daily horoscope

*⛽ Fuel:*
/fuel [city] — Fuel prices

*🪙 Gold:*
/gold [city] — Gold/Silver rates

*🌤 Weather:*
/weather [city] — Weather update

*🌾 Agriculture:*
/mandi — Mandi rates

*🛡 Child Safety:*
/bachpan — Safety tips

*🚨 Emergency:*
/emergency — Emergency numbers

*📊 Reports:*
/report — Daily report
/status — System status

*🛠 Mini-Program:*
/mini — Developer portal
/mini_register — Register
/mini_login — Login
/mini_create — Create app

⚡ *Singh Ji AI Ultra v8.0*"""

STATUS_MSG = """🟢 *Singh Ji AI Status v8.0*

✅ Bot Active
✅ API Connected
✅ Mini-Program Ready
🦁 Singh Ji AI v8.0
📡 Mode: {mode}"""

MINI_WELCOME = """📱 *Singh Ji Mini-Program Portal*

Create your own mini-apps!

*Commands:*
/mini_register — Developer register
/mini_login — Developer login
/mini_create — Naya app create karo
/mini_list — Apne apps dekho
/mini_status — App status check

*Features:*
🛠️ App Builder
🏖️ Sandbox Testing
💰 Payment Integration
📊 Analytics
🚀 App Store

Visit: {url}

⚡ *Singh Ji AI Ultra v8.0*"""

ERROR_MSG = "❓ Unknown command. Type /help for commands."


# ========== COMMAND MAP v7.0 + v8.0 ==========
COMMANDS = {
    # v7.0 Modules
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
}


# ========== TELEGRAM FUNCTIONS ==========

def send_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    """Send message to Telegram"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not set!")
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
        print(f"❌ send_message error: {e}")
        return False


def get_module_data(module_name: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Get data from any module via API"""
    try:
        url = f"{API_BASE}/{module_name}"
        if params:
            resp = requests.get(url, params=params, timeout=10)
        else:
            resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"❌ Module {module_name} error: {e}")
    return None


def ai_brain_reply(user_text: str) -> Optional[str]:
    """Get AI reply from Groq"""
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
        print(f"❌ AI brain error: {e}")
    return None


# ========== MINI-PROGRAM FUNCTIONS ==========

def mini_register(chat_id: int, args: List[str]):
    """Mini-Program developer register"""
    if len(args) < 2:
        send_message(chat_id, "📱 *Mini-Program Register*\n\nUsage:\n`/mini_register <email> <password>`")
        return

    email, password = args[0], args[1]
    try:
        resp = requests.post(
            f"{API_BASE}/mini/auth/register",
            data={"email": email, "password": password, "full_name": email.split("@")[0]},
            timeout=10
        )
        data = resp.json()
        if data.get("status") == "success":
            send_message(chat_id, f"✅ *Registration Successful!*\n\nDeveloper ID: `{data.get('developer_id')}`\n\nAb login karo: `/mini_login {email} {password}`")
        else:
            send_message(chat_id, f"❌ Registration failed: {data.get('message', 'Unknown error')}")
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")


def mini_login(chat_id: int, args: List[str]):
    """Mini-Program developer login"""
    if len(args) < 2:
        send_message(chat_id, "📱 *Mini-Program Login*\n\nUsage:\n`/mini_login <email> <password>`")
        return

    email, password = args[0], args[1]
    try:
        resp = requests.post(
            f"{API_BASE}/mini/auth/login",
            data={"email": email, "password": password},
            timeout=10
        )
        data = resp.json()
        if data.get("token"):
            token = data["token"]
            send_message(chat_id, f"🔑 *Login Successful!*\n\nToken: `{token[:20]}...`\n\nApp create karo: `/mini_create <app_name> <category> {token}`")
        else:
            send_message(chat_id, "❌ Login failed. Check credentials.")
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")


def mini_create(chat_id: int, args: List[str]):
    """Mini-Program app create"""
    if len(args) < 3:
        send_message(chat_id, "📱 *Create Mini-App*\n\nUsage:\n`/mini_create <name> <category> <token>`\n\nCategories: utilities, games, education, shopping, social")
        return

    name, category, token = args[0], args[1], args[2]
    try:
        resp = requests.post(
            f"{API_BASE}/mini/apps/create",
            data={"name": name, "category": category, "token": token},
            timeout=10
        )
        data = resp.json()
        if data.get("status") == "success":
            send_message(chat_id, f"🎉 *App Created!*\n\nApp ID: `{data.get('app_id')}`\nStatus: Pending review\n\n{data.get('message', '')}")
        else:
            send_message(chat_id, f"❌ Create failed: {data.get('message', 'Unknown error')}")
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")


def mini_list(chat_id: int, args: List[str]):
    """List developer apps"""
    if not args:
        send_message(chat_id, "📱 *List Apps*\n\nUsage:\n`/mini_list <token>`")
        return

    token = args[0]
    try:
        resp = requests.get(
            f"{API_BASE}/mini/apps/list",
            params={"token": token},
            timeout=10
        )
        data = resp.json()
        apps = data.get("apps", [])
        if apps:
            reply = "📱 *Your Mini-Apps*\n\n"
            for app in apps:
                reply += f"• `{app.get('id')}` — {app.get('name')} ({app.get('status')})\n"
            send_message(chat_id, reply)
        else:
            send_message(chat_id, "📭 No apps found. Create one: `/mini_create`")
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")


# ========== COMMAND HANDLER ==========

def handle_command(command: str, args: List[str], chat_id: int) -> Dict[str, Any]:
    """Handle any command and send reply"""

    # Basic commands
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

    # Mini-Program commands
    elif command == "mini":
        send_message(chat_id, MINI_WELCOME.format(url=MINI_PROGRAM_URL))
        return {"status": "ok"}

    elif command == "mini_register":
        mini_register(chat_id, args)
        return {"status": "ok"}

    elif command == "mini_login":
        mini_login(chat_id, args)
        return {"status": "ok"}

    elif command == "mini_create":
        mini_create(chat_id, args)
        return {"status": "ok"}

    elif command == "mini_list":
        mini_list(chat_id, args)
        return {"status": "ok"}

    # v7.0 Module commands
    if command in COMMANDS:
        cmd_info = COMMANDS[command]
        module = cmd_info["module"]
        params = cmd_info["params"].copy()

        # Update params with user args
        if args:
            if command in ["rashifal", "horoscope"]:
                params["rashi"] = args[0]
            elif command in ["fuel", "petrol"]:
                params["city"] = args[0]
            elif command in ["gold", "sone"]:
                params["city"] = args[0]
            elif command in ["weather", "mausam"]:
                params["city"] = args[0]

        # Call module API
        data = get_module_data(module, params)

        if data and data.get("success"):
            reply = format_module_response(module, data, params)
        else:
            reply = "❌ Data nahi mila. Try again later."

        send_message(chat_id, reply)
        return {"status": "ok"}

    # AI Chat for unknown commands
    ai_reply = ai_brain_reply(command + " " + " ".join(args))
    if ai_reply:
        reply = f"🦁 *Singh Ji AI:*\n\n{ai_reply}"
    else:
        reply = ERROR_MSG

    send_message(chat_id, reply)
    return {"status": "ok"}


def format_module_response(module: str, data: Dict, params: Dict) -> str:
    """Format module data for Telegram"""

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

    return "✅ Data received!"


# ========== FASTAPI WEBHOOK HANDLER ==========

if FASTAPI_AVAILABLE:
    async def webhook_handler(request: Request):
        """FastAPI webhook handler"""
        try:
            body = await request.json()
            message = body.get("message", {})
            text = message.get("text", "").strip()
            chat_id = message.get("chat", {}).get("id")

            if not chat_id or not text:
                return JSONResponse(status_code=200, content={"status": "ok"})

            # Parse command
            parts = text.strip().split()
            command = parts[0].lower().replace("/", "")
            args = parts[1:] if len(parts) > 1 else []

            # Handle command
            result = handle_command(command, args, chat_id)

            return JSONResponse(status_code=200, content=result)

        except Exception as e:
            print(f"❌ Webhook handler error: {e}")
            return JSONResponse(status_code=200, content={"status": "ok"})


# ========== POLLING MODE ==========

def polling_mode():
    """Run bot in polling mode (no webhook)"""
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

    # Delete webhook first
    if TELEGRAM_TOKEN:
        try:
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=10)
            print("✅ Webhook deleted for polling")
        except Exception as e:
            print(f"⚠️ Webhook delete: {e}")

    offset = get_offset() + 1
    print(f"🚀 Starting polling from offset {offset}")
    print("   Press Ctrl+C to stop\n")

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
                    print(f"📩 @{user}: {text[:50]}")

                    parts = text.strip().split()
                    command = parts[0].lower().replace("/", "")
                    args = parts[1:] if len(parts) > 1 else []

                    handle_command(command, args, chat_id)

                offset = update_id + 1
                save_offset(offset)

            if not updates:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Bot stopped. Bye!")
            break
        except Exception as e:
            print(f"❌ Polling error: {e}")
            time.sleep(5)


# ========== MAIN ENTRY ==========

if __name__ == "__main__":
    print("=" * 50)
    print("🦁 SINGH JI AI ULTRA v8.0 — TELEGRAM BOT")
    print("=" * 50)
    print(f"📡 Mode: Polling")
    print(f"🔗 API: {API_BASE}")
    print(f"🛠️ Mini-Program: {MINI_PROGRAM_URL}")
    print("=" * 50 + "\n")

    if not TELEGRAM_TOKEN:
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        print("   Set env var: export TELEGRAM_TOKEN='your_token'")
        sys.exit(1)

    polling_mode()
