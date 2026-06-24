"""
🗣️ SINGH JI AI — Hindi Voice Commands
Bolo → AI Samjhe → Kaam Kare
"""

import asyncio
from typing import Dict, Any

class VoiceCommands:
    """Hindi voice command parser"""

    COMMANDS = {
        # Emergency
        "madad": {"module": "emergency", "action": "trigger_sos"},
        "bachao": {"module": "emergency", "action": "trigger_sos"},
        "emergency": {"module": "emergency", "action": "trigger_sos"},

        # Govt
        "yojana": {"module": "govt", "action": "get_all"},
        "scheme": {"module": "govt", "action": "get_all"},
        "pension": {"module": "govt", "action": "get_scheme", "scheme_id": "atal_pension"},
        "kisan": {"module": "govt", "action": "get_scheme", "scheme_id": "pm_kisan"},

        # Food
        "khana": {"module": "food", "action": "order_food"},
        "bhukh": {"module": "food", "action": "order_food"},
        "recipe": {"module": "food", "action": "get_recipe"},

        # Taxi
        "taxi": {"module": "taxi", "action": "book_taxi"},
        "auto": {"module": "taxi", "action": "book_auto"},
        "gaadi": {"module": "taxi", "action": "book_taxi"},
        "train": {"module": "taxi", "action": "check_train"},

        # Music
        "gana": {"module": "music", "action": "play_mood"},
        "gaana": {"module": "music", "action": "play_mood"},
        "music": {"module": "music", "action": "play_mood"},
        "bhajan": {"module": "music", "action": "play_devotional", "deity": "hanuman"},

        # Maps
        "petrol": {"module": "map", "action": "find_nearby", "type": "petrol"},
        "toilet": {"module": "map", "action": "find_nearby", "type": "toilet"},
        "hospital": {"module": "map", "action": "find_nearby", "type": "hospital"},
        "atm": {"module": "map", "action": "find_nearby", "type": "atm"},

        # Banking
        "balance": {"module": "banking", "action": "check_balance"},
        "paisa": {"module": "banking", "action": "check_balance"},
        "upi": {"module": "banking", "action": "send_money"},

        # News
        "khabar": {"module": "news", "action": "get_daily"},
        "news": {"module": "news", "action": "get_daily"},
        "samachar": {"module": "news", "action": "get_daily"},

        # Education
        "padho": {"module": "education", "action": "kids_learning"},
        "sikho": {"module": "education", "action": "adult_skills"},
        "exam": {"module": "education", "action": "exam_prep"},

        # Games
        "game": {"module": "games", "action": "get_desi_games"},
        "khelo": {"module": "games", "action": "get_desi_games"},

        # Safety
        "safety": {"module": "safety", "action": "get_lessons"},
        "bacho": {"module": "safety", "action": "get_lessons"},
    }

    async def handle(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {
            "parse_command": self.parse_command,
            "get_all_commands": self.get_all_commands,
        }
        handler = handlers.get(action, self._default)
        return await handler(request)

    async def parse_command(self, request):
        text = request.get("text", "").lower()

        for keyword, command in self.COMMANDS.items():
            if keyword in text:
                return {
                    "recognized": True,
                    "command": command,
                    "keyword": keyword,
                    "original_text": text,
                    "response": f"🦁 Singh Ji: '{keyword}' samajh gaya! Ab {command['module']} module chala raha hoon..."
                }

        return {
            "recognized": False,
            "original_text": text,
            "suggestion": "Kripya saaf boliye: 'madad', 'khana', 'taxi', 'gana', 'khabar'...",
            "available_commands": list(self.COMMANDS.keys())[:20]
        }

    async def get_all_commands(self, request):
        return {
            "total_commands": len(self.COMMANDS),
            "commands": self.COMMANDS
        }

    async def _default(self, request):
        return {"error": "Unknown action"}
