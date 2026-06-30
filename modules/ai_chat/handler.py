from fastapi import Request
import os
import httpx
from datetime import datetime

GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "ai_chat", "models": ["groq", "gemini"]}
    if method == "POST":
        try:
            body = await request.json()
            msg = body.get("message", "")
            model = body.get("model", "groq")
            if not msg: return {"status": "error", "message": "No message"}
            if model == "groq" and GROQ_KEY: return await call_groq(msg)
            elif model == "gemini" and GEMINI_KEY: return await call_gemini(msg)
            return {"status": "success", "model": "local", "reply": f"🦁 Singh Ji: {msg}", "timestamp": datetime.now().isoformat()}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}

async def call_groq(msg):
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": msg}], "temperature": 0.7, "max_tokens": 1024}, timeout=30)
            d = r.json()
            return {"status": "success", "model": "groq", "reply": d["choices"][0]["message"]["content"], "timestamp": datetime.now().isoformat()}
    except Exception as e: return {"status": "error", "model": "groq", "error": str(e)}

async def call_gemini(msg):
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-pro")
        return {"status": "success", "model": "gemini", "reply": model.generate_content(msg).text, "timestamp": datetime.now().isoformat()}
    except Exception as e: return {"status": "error", "model": "gemini", "error": str(e)}
