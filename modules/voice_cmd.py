from fastapi import APIRouter

router = APIRouter()

@router.get("/api/voice/command")
def voice_command():
    return {
        "status": "success",
        "module": "voice_cmd",
        "message": "Voice command module ready"
    }

@router.post("/api/voice/command")
def process_command(command: str = ""):
    if not command:
        return {"status": "error", "message": "Command required"}
    return {
        "status": "success",
        "command": command,
        "action": "processing",
        "message": f"Command '{command}' received"
    }
