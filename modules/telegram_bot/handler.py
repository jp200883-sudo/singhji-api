# modules/telegram_bot/handler.py

import os
import json
import requests
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_BASE = "https://singhji-api.onrender.com/api"

# ========== YOUR COMMANDS (as-is) ==========
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
}

WELCOME_MSG = "🦁 *Welcome to Singh Ji AI Ultra v7.0!*\n\nYour AI assistant for Bharat 🇮🇳\n\n*Commands:*\n📰 /news - Latest news\n🔮 /rashifal - Daily horoscope\n⛽ /fuel - Petrol/Diesel prices\n🪙 /gold - Gold/Silver rates\n🌤 /weather - Weather update\n🌾 /mandi - Mandi rates\n🛡 /bachpan - Child safety\n🚨 /emergency - Emergency help\n📊 /report - Daily report\nℹ️ /help - All commands\n\n⚡ *Singh Ji AI Ultra v7.0*"

HELP_MSG = "🦁 *Singh Ji AI Commands*\n\n*📰 News:*\n/news - India news\n/sports - Sports news\n/business - Business news\n\n*🔮 Horoscope:*\n/rashifal [rashi] - Daily horoscope\n\n*⛽ Fuel:*\n/fuel [city] - Fuel prices\n\n*🪙 Gold:*\n/gold [city] - Gold/Silver rates\n\n*🌤 Weather:*\n/weather [city] - Weather update\n\n*🌾 Agriculture:*\n/mandi - Mandi rates\n\n*🛡 Child Safety:*\n/bachpan - Safety tips\n\n*🚨 Emergency:*\n/emergency - Emergency numbers\n\n*📊 Reports:*\n/report - Daily report\n/status - System status\n\n⚡ *Singh Ji AI Ultra v7.0*"

STATUS_MSG = "🟢 *Singh Ji AI Status*\n\n✅ Bot Active\n✅ API Connected\n🦁 Singh Ji AI v7.0"

ERROR_MSG = "❓ Unknown command. Type /help for commands."


# ========== TELEGRAM FUNCTIONS ==========

def send_message(chat_id, text, parse_mode="Markdown"):
    """Send message to Telegram"""
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }, timeout=10)
    except Exception as e:
        print(f"Send message failed: {e}")


def get_module_data(module_name, params=None):
    """Get data from any module via API"""
    try:
        url = f"{API_BASE}/{module_name}"
        if params:
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Module {module_name} error: {e}")
    return None


def ai_brain_reply(user_text):
    """Get AI reply from Groq"""
    try:
        if GROQ_API_KEY:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": user_text}],
                    "max_tokens": 500
                },
                timeout=15
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI brain error: {e}")
    return None


# ========== COMMAND HANDLER ==========

def handle_command(command, args, chat_id):
    """Handle any command and send reply to Telegram"""
    
    if command == "start":
        send_message(chat_id, WELCOME_MSG)
        return {"status": "ok"}
    
    elif command == "help":
        send_message(chat_id, HELP_MSG)
        return {"status": "ok"}
    
    elif command == "status":
        send_message(chat_id, STATUS_MSG)
        return {"status": "ok"}
    
    # Module commands
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
            # Format response based on module
            reply = format_module_response(module, data, params)
        else:
            reply = f"❌ Data nahi mila. Try again later."
        
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


def format_module_response(module, data, params):
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

🦁 Singh Ji AI v7.0"""
    
    return "✅ Data received!"


# ========== FASTAPI HANDLER ==========

async def handler(request: Request):
    """Main webhook handler"""
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
        print(f"Telegram handler error: {e}")
        return JSONResponse(status_code=200, content={"status": "ok"})
