from fastapi import APIRouter
from core.config import settings

router = APIRouter()
@router.get("/")
def ai_chat_home():
    return {"module": "ai_chat", "status": "ok", "app": settings.APP_NAME}
@router.post("/chat")
def chat(message: str = ""):
    return {
        "reply": f"🦁 Singh Ji AI: '{message}' ka jawab...",
        "module": "ai_chat",
        "status": "active"
    }
