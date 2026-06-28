# modules/ai_chat.py — Singh Ji AI Ultra
import os
import requests
from fastapi import APIRouter

router = APIRouter()

GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")

def groq_chat(message: str):
    """Fastest — Llama 3"""
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are Singh Ji AI, India's super app assistant. Reply in Hindi-English mix (Hinglish). Be helpful, funny, and desi!"},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                       json=payload, headers=headers, timeout=15)
    return res.json()["choices"][0]["message"]["content"]

def gemini_chat(message: str):
    """Google Gemini fallback"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"You are Singh Ji AI. Reply in Hinglish. User: {message}"}]
        }]
    }
    res = requests.post(url, json=payload, timeout=15)
    return res.json()["candidates"][0]["content"]["parts"][0]["text"]

@router.post("/chat")
def chat(message: str, engine: str = "auto"):
    """
    AI Chat with auto-fallback:
    1. Groq (fastest)
    2. Gemini (Google)
    3. Cerebras (if needed)
    """
    if engine == "auto":
        engines = ["groq", "gemini"]
    else:
        engines = [engine]
    
    for eng in engines:
        try:
            if eng == "groq" and GROQ_KEY:
                reply = groq_chat(message)
                return {"reply": reply, "engine": "groq", "status": "success"}
            elif eng == "gemini" and GEMINI_KEY:
                reply = gemini_chat(message)
                return {"reply": reply, "engine": "gemini", "status": "success"}
        except Exception as e:
            continue
    
    return {
        "reply": "Arre bhai, thoda busy hoon! Thodi der me try karo! 🦁",
        "engine": "fallback",
        "status": "all_failed"
    }

@router.get("/engines")
def list_engines():
    """Available AI engines"""
    return {
        "engines": [
            {"name": "groq", "model": "llama3-8b", "status": "active" if GROQ_KEY else "missing_key"},
            {"name": "gemini", "model": "gemini-1.5-flash", "status": "active" if GEMINI_KEY else "missing_key"},
            {"name": "cerebras", "model": "llama3", "status": "active" if CEREBRAS_KEY else "missing_key"}
        ]
    }
