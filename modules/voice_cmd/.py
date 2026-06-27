# core/modules/voice_cmd/voice_cmd.py
from fastapi import APIRouter
router = APIRouter()
@router.get("/api/voice/command")
def voice_command():
    return {"status": "voice command endpoint"}
