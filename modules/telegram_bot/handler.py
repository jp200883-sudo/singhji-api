# telegram_bot/handler.py
import os
import json
import requests
import time
from typing import Dict, Any
from fastapi import Request
from fastapi.responses import JSONResponse

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else None

# ========== TELEGRAM BOT MODULE ==========
class TelegramBotModule:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.base_url = BOT_URL
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """Send message to Telegram chat"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            resp = requests.post(url, json=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            
            return {
                "success": result.get("ok", False),
                "message_id": result.get("result", {}).get("message_id"),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_photo(self, chat_id: str, photo_url: str, caption: str = "") -> Dict[str, Any]:
        """Send photo to Telegram chat"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML"
            }
            resp = requests.post(url, json=data, timeout=15)
            resp.raise_for_status()
            return {"success": True, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Set webhook for bot"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/setWebhook"
            data = {"url": webhook_url, "drop_pending_updates": True}
            resp = requests.post(url, json=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            return {
                "success": result.get("ok", False),
                "description": result.get("description", ""),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook info"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/getWebhookInfo"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            return {
                "success": result.get("ok", False),
                "info": result.get("result", {}),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_webhook(self) -> Dict[str, Any]:
        """Delete webhook"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/deleteWebhook"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            return {"success": True, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_updates(self, offset: int = None) -> Dict[str, Any]:
        """Get updates (for polling mode)"""
        if not self.token:
            return {"success": False, "error": "No Telegram token set"}
        
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"limit": 10}
            if offset:
                params["offset"] = offset
            
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            return {
                "success": result.get("ok", False),
                "updates": result.get("result", []),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "telegram_bot",
            "token_set": bool(self.token),
            "status": "✅ Ready" if self.token else "❌ No Token"
        }


# ========== RENDER HANDLER — FastAPI Compatible ==========
async def handler(request: Request):
    """FastAPI compatible handler — async def + JSONResponse"""
    
    if request.method == "GET":
        t = TelegramBotModule()
        
        # ✅ FastAPI mein query params
        action = request.query_params.get("action", "info")
        
        if action == "webhook_info":
            result = t.get_webhook_info()
        elif action == "delete_webhook":
            result = t.delete_webhook()
        elif action == "health":
            result = t.health_check()
        else:
            result = {
                "module": "telegram_bot",
                "status": "LIVE",
                "health": t.health_check()
            }
        
        # ✅ FastAPI JSONResponse
        return JSONResponse(content=result)
    
    elif request.method == "POST":
        try:
            # ✅ FastAPI mein: await request.json()
            body = await request.json()
            action = body.get("action", "send_message")
            
            t = TelegramBotModule()
            
            if action == "send_message":
                result = t.send_message(
                    body.get("chat_id"), 
                    body.get("text"), 
                    body.get("parse_mode", "HTML")
                )
            elif action == "send_photo":
                result = t.send_photo(
                    body.get("chat_id"), 
                    body.get("photo_url"), 
                    body.get("caption", "")
                )
            elif action == "set_webhook":
                result = t.set_webhook(body.get("webhook_url"))
            elif action == "get_updates":
                result = t.get_updates(body.get("offset"))
            else:
                result = {"error": "Unknown action"}
            
            # ✅ FastAPI JSONResponse
            return JSONResponse(content=result)
            
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
    
    return JSONResponse(status_code=405, content={"error": "Method not allowed"})


if __name__ == "__main__":
    t = TelegramBotModule()
    print("🦁 SINGH JI AI ULTRA v7.0 — Telegram Bot Module")
    print("Health:", t.health_check())
