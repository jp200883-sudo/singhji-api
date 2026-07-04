#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Telegram Bot Handler
All module commands in one place
"""

import os
import json
from datetime import datetime
from typing import Dict

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# All module commands
COMMANDS = {
    "news": {"module": "news", "action": "telegram", "params": {"category": "india", "language": "hi"}},
    "khabar": {"module": "news", "action": "telegram", "params": {"category": "india", "language": "hi"}},
    "sports": {"module": "news", "action": "telegram", "params": {"category": "sports", "language": "hi"}},
    "business": {"module": "news", "action": "telegram", "params": {"category": "business", "language": "hi"}},
    "rashifal": {"module": "horoscope", "action": "telegram", "params": {"rashi": "मेष", "period": "daily", "language": "hi"}},
    "horoscope": {"module": "horoscope", "action": "telegram", "params": {"rashi": "Aries", "period": "daily", "language": "en"}},
    "fuel": {"module": "fuel", "action": "telegram", "params": {"city": "Delhi", "fuel_type": "all"}},
    "petrol": {"module": "fuel", "action": "telegram", "params": {"city": "Delhi", "fuel_type": "petrol"}},
    "gold": {"module": "goldrate", "action": "telegram", "params": {"city": "India", "purity": "all"}},
    "sone": {"module": "goldrate", "action": "telegram", "params": {"city": "India", "purity": "all"}},
    "weather": {"module": "weather", "action": "telegram", "params": {"city": "Kanpur"}},
    "mausam": {"module": "weather", "action": "telegram", "params": {"city": "Kanpur"}},
    "mandi": {"module": "mandi", "action": "telegram", "params": {}},
    "emergency": {"module": "emergency", "action": "telegram", "params": {}},
    "sos": {"module": "emergency", "action": "telegram", "params": {}},
    "bachpan": {"module": "bachpan", "action": "telegram", "params": {"language": "hi"}},
    "child": {"module": "bachpan", "action": "telegram", "params": {"language": "hi"}},
    "report": {"module": "daily_report", "action": "telegram", "params": {}},
    "status": {"module": "status", "action": "get", "params": {}},
    "help": {"module": "help", "action": "get", "params": {}},
    "start": {"module": "start", "action": "get", "params": {}},
}

# Single line messages only
WELCOME_MSG = "🦁 *Welcome to Singh Ji AI Ultra v7.0!*\n\nYour AI assistant for Bharat 🇮🇳\n\n*Commands:*\n📰 /news - Latest news\n🔮 /rashifal - Daily horoscope\n⛽ /fuel - Petrol/Diesel prices\n🪙 /gold - Gold/Silver rates\n🌤 /weather - Weather update\n🌾 /mandi - Mandi rates\n🛡 /bachpan - Child safety\n🚨 /emergency - Emergency help\n📊 /report - Daily report\nℹ️ /help - All commands\n\n⚡ *Singh Ji AI Ultra v7.0*"

HELP_MSG = "🦁 *Singh Ji AI Commands*\n\n*📰 News:*\n/news - India news\n/sports - Sports news\n/business - Business news\n\n*🔮 Horoscope:*\n/rashifal [rashi] - Daily horoscope\nExample: /rashifal मेष\n\n*⛽ Fuel:*\n/fuel [city] - Fuel prices\n/petrol [city] - Petrol only\n\n*🪙 Gold:*\n/gold [city] - Gold/Silver rates\n\n*🌤 Weather:*\n/weather [city] - Weather update\n\n*🌾 Agriculture:*\n/mandi - Mandi rates\n\n*🛡 Child Safety:*\n/bachpan - Safety tips\n/child - Helplines\n\n*🚨 Emergency:*\n/emergency - Emergency numbers\n/sos - Quick help\n\n*📊 Reports:*\n/report - Daily report\n/status - System status\n\n⚡ *Singh Ji AI Ultra v7.0*"

STATUS_MSG = "🟢 *Singh Ji AI Status*\n\n✅ Bot Active\n✅ API Connected\n🦁 Singh Ji AI v7.0"

ERROR_MSG = "❓ Unknown command. Type /help for commands."


class TelegramHandler:
    def __init__(self):
        pass

    def parse_command(self, text: str) -> Dict:
        if not text:
            return {"command": "", "args": []}
        parts = text.strip().split()
        command = parts[0].lower().replace("/", "")
        args = parts[1:] if len(parts) > 1 else []
        return {"command": command, "args": args}

    def get_response(self, command: str, args: list, user_id: str = "") -> str:
        if command == "start":
            return WELCOME_MSG
        elif command == "help":
            return HELP_MSG
        elif command == "status":
            return STATUS_MSG

        if command not in COMMANDS:
            return ERROR_MSG

        cmd_info = COMMANDS[command]
        module = cmd_info["module"]
        action = cmd_info["action"]
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

        return {
            "module": module,
            "action": action,
            "params": params,
            "user_id": user_id
        }


telegram_handler = TelegramHandler()

def parse_command(text: str) -> Dict:
    return telegram_handler.parse_command(text)

def get_response(command: str, args: list, user_id: str = "") -> str:
    return telegram_handler.get_response(command, args, user_id)


async def handler(request):
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)

        action = body.get("action") or params.get("action", "parse")
        text = body.get("text") or params.get("text", "")
        user_id = body.get("user_id") or params.get("user_id", "")

        if action == "parse":
            result = parse_command(text)
        elif action == "response":
            parsed = parse_command(text)
            result = get_response(parsed["command"], parsed["args"], user_id)
        else:
            result = {"status": "error", "message": "Unknown action"}

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("Testing Telegram Handler...")
    print(get_response("start", []))
