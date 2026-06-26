from fastapi import APIRouter

router = APIRouter()

COMMANDS = {
    "madad": {"module": "emergency", "action": "sos"},
    "khabar": {"module": "news", "action": "daily"},
    "gana": {"module": "music", "action": "play"},
    "khana": {"module": "food", "action": "order"},
    "taxi": {"module": "taxi", "action": "book"},
    "balance": {"module": "banking", "action": "check"},
    "yojana": {"module": "govt", "action": "schemes"},
}

@router.post("/listen")
def listen_command(text: str):
    """Listen to Hindi voice command"""
    text = text.lower()
    
    for keyword, command in COMMANDS.items():
        if keyword in text:
            return {
                "recognized": True,
                "keyword": keyword,
                "command": command,
                "response": f"🦁 '{keyword}' samajh gaya! {command['module']} chala raha hoon..."
            }
    
    return {
        "recognized": False,
        "text": text,
        "suggestion": "Bolo: 'madad', 'khabar', 'gana', 'khana', 'taxi'..."
    }

@router.get("/commands")
def list_commands():
    """All available commands"""
    return {
        "total": len(COMMANDS),
        "commands": COMMANDS
    }
