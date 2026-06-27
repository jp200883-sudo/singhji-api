from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/")  # ← ADD THIS!
def ai_home():
    return {
        "module": "ai_chat",
        "status": "ok",
        "gemini_key_exists": bool(os.getenv("GEMINI_API_KEY")),
        "groq_key_exists": bool(os.getenv("GROQ_API_KEY")),
        "cerebras_key_exists": bool(os.getenv("CEREBRAS_API_KEY"))
    }

@router.post("/chat")  # ← Existing POST endpoint
def chat(request: dict):
    # ... AI logic ...
    pass
