# modules/entertainment/__init__.py — Singh Ji AI Ultra v5.0
# Entertainment — Jokes, Quotes, Facts

from fastapi import APIRouter
import random

router = APIRouter()

JOKES = [
    "Why did the computer go to doctor? Because it had a virus! 😄",
    "Why don't scientists trust atoms? Because they make up everything! 🤣",
    "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
    "What do you call a fake noodle? An impasta! 🍝",
    "Why did the math book look sad? Because it had too many problems! 📚"
]

QUOTES = [
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Success is not final, failure is not fatal.", "author": "Winston Churchill"},
    {"text": "Be the change you wish to see in the world.", "author": "Mahatma Gandhi"}
]

FACTS = [
    "India has the world's largest postal network with over 150,000 post offices! 📮",
    "The Taj Mahal took 22 years and 20,000 workers to build! 🕌",
    "India invented the number zero! 0️⃣",
    "The game of chess originated in India! ♟️",
    "India has 22 officially recognized languages! 🗣️"
]

@router.get("/")
def entertainment_root():
    return {"module": "entertainment", "status": "✅ Live"}

@router.get("/joke")
def get_joke():
    return {"success": True, "joke": random.choice(JOKES)}

@router.get("/quote")
def get_quote():
    return {"success": True, "quote": random.choice(QUOTES)}

@router.get("/fact")
def get_fact():
    return {"success": True, "fact": random.choice(FACTS)}

@router.get("/all")
def get_all():
    return {
        "success": True,
        "joke": random.choice(JOKES),
        "quote": random.choice(QUOTES),
        "fact": random.choice(FACTS)
    }
