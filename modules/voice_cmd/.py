# core/modules/voice_cmd/voice_cmd.py
from fastapi import APIRouter
from . import router  # __init__ से router import

@router.get("/api/voice/command")
def voice_command():
    return {"status": "voice command endpoint"}
