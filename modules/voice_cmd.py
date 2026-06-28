from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def voice_cmd_root():
    return {
        "ok": True,
        "module": "voice_cmd",
        "status": "✅ LIVE",
        "message": "Voice Command ready — Bol ke control karo!"
    }

@router.post("/command")
async def process_command(command: str = "hello singh ji"):
    # Simple command processing
    cmd_lower = command.lower()
    
    responses = {
        "hello": "Namaste! Main Singh Ji AI hoon.",
        "weather": "Mausam check karne ke liye /api/weather dekho!",
        "news": "Aaj ki khabar ke liye /api/news dekho!",
        "joke": "Ek Santa-Banta joke suno...",
        "time": "Abhi time check karo!",
        "singh ji": "Haan bhai, main hoon! Kya kaam hai?"
    }
    
    response = "Samajh nahi aaya bhai, dobara bolo!"
    for key, val in responses.items():
        if key in cmd_lower:
            response = val
            break
    
    return {
        "ok": True,
        "command": command,
        "response": response,
        "action": "processed",
        "message": "Command samajh liya!"
    }
