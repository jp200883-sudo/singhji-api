# modules/voice.py — Singh Ji AI Ultra v5.0
# Voice Recognition — Speech-to-Text, Commands, Assistant

from fastapi import APIRouter, UploadFile, File
import os
import requests

router = APIRouter()

ASSEMBLY_AI_KEY = os.getenv("ASSEMBLY_AI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

@router.get("/")
def voice_root():
    return {
        "module": "voice",
        "status": "✅ Live",
        "features": ["stt", "commands", "assistant"]
    }

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Speech to Text — Upload audio file"""
    
    if not ASSEMBLY_AI_KEY:
        return {
            "success": False,
            "error": "AssemblyAI key not configured",
            "fallback": "Use /voice/commands for text commands"
        }
    
    try:
        # Upload to AssemblyAI
        headers = {"authorization": ASSEMBLY_AI_KEY}
        upload_url = "https://api.assemblyai.com/v2/upload"
        
        audio_content = await audio.read()
        response = requests.post(upload_url, headers=headers, data=audio_content)
        upload_result = response.json()
        
        # Transcribe
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        json_data = {"audio_url": upload_result["upload_url"]}
        response = requests.post(transcript_url, headers=headers, json=json_data)
        transcript_result = response.json()
        
        return {
            "success": True,
            "text": transcript_result.get("text", ""),
            "confidence": transcript_result.get("confidence", 0),
            "language": transcript_result.get("language_code", "unknown")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/commands")
def voice_commands(command: str):
    """Process voice/text commands"""
    
    command = command.lower().strip()
    
    # Command mapping
    commands = {
        "weather": ["weather", "mausam", "मौसम"],
        "news": ["news", "samachar", "खबर", "samachar"],
        "time": ["time", "samay", "समय", "kitna baja"],
        "date": ["date", "tarikh", "तारीख"],
        "joke": ["joke", "chutkula", "चुटकुला"],
        "motivation": ["motivate", "prerak", "प्रेरणा"],
        "help": ["help", "madad", "मदद"]
    }
    
    detected = None
    for action, keywords in commands.items():
        if any(kw in command for kw in keywords):
            detected = action
            break
    
    responses = {
        "weather": {"action": "weather", "message": "Weather check karo /api/weather se", "icon": "🌤️"},
        "news": {"action": "news", "message": "Latest news /api/news/latest se", "icon": "📰"},
        "time": {"action": "time", "message": f"Abhi ka time: {__import__('datetime').datetime.now().strftime('%I:%M %p')}", "icon": "🕐"},
        "date": {"action": "date", "message": f"Aaj ki tarikh: {__import__('datetime').datetime.now().strftime('%d %B %Y')}", "icon": "📅"},
        "joke": {"action": "joke", "message": "Why did the computer go to doctor? Because it had a virus! 😄", "icon": "😂"},
        "motivation": {"action": "motivation", "message": "Aap best ho! Kuch bhi kar sakte ho! 🚀", "icon": "💪"},
        "help": {"action": "help", "message": "Main madad kar sakta hoon: news, weather, time, jokes, motivation", "icon": "❓"}
    }
    
    if detected:
        return {
            "success": True,
            "command": command,
            "detected": detected,
            "response": responses[detected]
        }
    
    return {
        "success": True,
        "command": command,
        "detected": "unknown",
        "response": {
            "action": "chat",
            "message": f"Main samajh gaya: '{command}'. Kuch aur batao!",
            "icon": "🤖"
        }
    }

@router.get("/languages")
def voice_languages():
    """Supported languages for voice"""
    return {
        "success": True,
        "languages": [
            {"code": "hi-IN", "name": "Hindi", "status": "✅"},
            {"code": "en-IN", "name": "English (India)", "status": "✅"},
            {"code": "bn-IN", "name": "Bengali", "status": "⏳"},
            {"code": "ta-IN", "name": "Tamil", "status": "⏳"},
            {"code": "te-IN", "name": "Telugu", "status": "⏳"},
            {"code": "mr-IN", "name": "Marathi", "status": "⏳"},
            {"code": "gu-IN", "name": "Gujarati", "status": "⏳"},
            {"code": "kn-IN", "name": "Kannada", "status": "⏳"},
            {"code": "ml-IN", "name": "Malayalam", "status": "⏳"},
            {"code": "pa-IN", "name": "Punjabi", "status": "⏳"}
        ],
        "note": "Bhashini integration pending for full 26 languages"
    }

@router.get("/assistant")
def voice_assistant(query: str):
    """Voice assistant — process natural language"""
    from modules import ai_chat
    
    try:
        # Use AI chat for response
        response = ai_chat.chat_with_ai(query)
        return {
            "success": True,
            "query": query,
            "response": response,
            "source": "ai_assistant"
        }
    except:
        # Fallback to command processor
        return voice_commands(query)
