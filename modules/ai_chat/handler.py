# ai_chat/handler.py — FASTAPI VERSION
import os
import json
import requests
import time
import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse

# ========== CONFIG ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# ========== HYBRID AI FAILOVER ==========
class HybridAIChat:
    def __init__(self):
        self.engines = [
            {"name": "Groq", "func": self._call_groq, "key": GROQ_API_KEY},
            {"name": "Gemini", "func": self._call_gemini, "key": GEMINI_API_KEY},
            {"name": "Cerebras", "func": self._call_cerebras, "key": CEREBRAS_API_KEY},
            {"name": "HuggingFace", "func": self._call_huggingface, "key": HUGGINGFACE_TOKEN},
        ]
    
    def chat(self, message: str, system_prompt: str = "You are Singh Ji AI, a helpful Indian AI assistant.") -> dict:
        last_error = None
        for engine in self.engines:
            if not engine["key"]:
                continue
            try:
                print(f"🔄 Trying {engine['name']}...")
                response = engine["func"](message, system_prompt)
                return {
                    "success": True,
                    "engine": engine["name"],
                    "response": response,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            except Exception as e:
                print(f"❌ {engine['name']} failed: {str(e)}")
                last_error = e
                continue
        
        return {
            "success": False,
            "error": str(last_error),
            "message": "All AI engines failed. Please try again later.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _call_groq(self, message: str, system_prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    
    def _call_gemini(self, message: str, system_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser: {message}"}]
            }]
        }
        resp = requests.post(url, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    
    def _call_cerebras(self, message: str, system_prompt: str) -> str:
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3.1-70b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    
    def _call_huggingface(self, message: str, system_prompt: str) -> str:
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        prompt = f"<s>[INST] {system_prompt}\n\n{message} [/INST]"
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 2048, "temperature": 0.7}}
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").replace(prompt, "").strip()
        return "HuggingFace response error"
    
    def health_check(self) -> dict:
        status = {}
        for engine in self.engines:
            status[engine["name"]] = "✅ Ready" if engine["key"] else "❌ No Key"
        return status


# ========== FASTAPI HANDLER ==========
async def handler(request: Request):
    """
    FastAPI handler for ai_chat module
    Supports: GET (health), POST (chat)
    """
    if request.method == "GET":
        ai = HybridAIChat()
        return JSONResponse(content={
            "module": "ai_chat",
            "version": "7.0",
            "status": "LIVE",
            "engines": ai.health_check()
        })
    
    elif request.method == "POST":
        try:
            body = await request.json()
            message = body.get("message", "")
            system_prompt = body.get("system_prompt", "You are Singh Ji AI, a helpful Indian AI assistant.")
            
            if not message:
                return JSONResponse(status_code=400, content={"error": "Message required"})
            
            ai = HybridAIChat()
            
            # Run sync chat in executor (non-blocking)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, ai.chat, message, system_prompt)
            
            return JSONResponse(
                status_code=200 if result["success"] else 503,
                content=result
            )
            
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
    
    return JSONResponse(status_code=405, content={"error": "Method not allowed"})
