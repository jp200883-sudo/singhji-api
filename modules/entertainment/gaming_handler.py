# modules/entertainment/gaming_handler.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/gaming")
def gaming_home():
    return {
        "status": "live",
        "message": "Gaming Section - Singh Ji AI Ultra v5.0 🎮",
        "games": ["quiz", "puzzle", "trivia"]
    }

# ✅ ये function add करो — main.py इसको import कर रहा है!
def get_gaming_content():
    return {
        "status": "live",
        "content": "Gaming content loaded!",
        "games": ["quiz", "puzzle", "trivia", "word_game", "memory_challenge"]
    }
