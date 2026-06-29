# core/modules/ai_chat.py
"""
Singh Ji AI Ultra v7.0 - AI Chat Module
"""
import os
import requests
from typing import Dict, Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def get_ai_response(message: str, model: str = "llama3-70b-8192", 
                   system_prompt: Optional[str] = None,
                   history: Optional[list] = None) -> Dict:
    """Get AI response using Groq"""
    try:
        if not GROQ_API_KEY:
            return {
                "success": False,
                "error": "GROQ_API_KEY not configured",
                "response": "❌ AI service unavailable. Configure GROQ_API_KEY in Render environment variables."
            }
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "response": data["choices"][0]["message"]["content"],
                "model": model,
                "usage": data.get("usage", {})
            }
        else:
            return {
                "success": False,
                "error": data.get("error", {}).get("message", "Unknown error"),
                "response": "❌ AI response failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "❌ Error connecting to AI service"
        }
