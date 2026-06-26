from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def ai_chat_home():
    return {"module": "ai_chat", "status": "ok"}
