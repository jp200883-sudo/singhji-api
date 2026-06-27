from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/")
def ai_home():
    return {
        "module": "ai_chat",
        "status": "ok",
        "gemini_key_exists": bool(os.getenv("GEMINI_API_KEY")),
        "groq_key_exists": bool(os.getenv("GROQ_API_KEY"))
    }

@router.post("/chat")
def chat(request: dict):
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_KEY = os.getenv("GROQ_API_KEY")
    
    # ... AI logic ...
    
    return {
        "response": "AI response here",
        "model": "gemini/groq",
        "source": "ai_chat"
    }
