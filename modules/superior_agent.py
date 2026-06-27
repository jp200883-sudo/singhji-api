# modules/superior_agent.py — Singh Ji AI Ultra v5.0
# 🦁 SUPERIOR AGENT — CEO, सब Agents को manage करेगा

from fastapi import APIRouter

router = APIRouter()

# ===== ALL AGENTS REGISTRY (Phase 1) =====
AGENTS = {
    # Core System
    "emergency": "/api/emergency",
    "language": "/api/language",
    "plant": "/api/plant",
    "memory": "/api/memory",
    "ai_chat": "/api/ai",
    "weather": "/api/weather",
    "mandi": "/api/mandi",
    "news": "/api/news",
    "email": "/api/email",
    "schedule": "/api/schedule",
    "telegram": "/api/telegram",
    "voice": "/api/voice",
    "voice_cmd": "/api/voice-cmd",
    "search": "/api/search",
    "social": "/api/social",
    "govt": "/api/govt",
    "upi": "/api/upi",
    
    # Phase 1: New
    "master_data": "/api/master-data",
    "meta_agent": "/api/meta",
    "singhji_agent": "/api/singhji",
}

@router.get("/")
def superior_root():
    return {
        "agent": "🦁 Superior Manager",
        "status": "LIVE",
        "reports_to": "🤴 Singh Ji Agent",
        "total_agents": len(AGENTS),
        "agents": list(AGENTS.keys()),
        "message": "सब Agents मेरे अंडर में!"
    }

@router.get("/health")
def check_all():
    return {
        "superior": "✅ LIVE",
        "reports_to": "Singh Ji Agent",
        "agents": AGENTS,
        "message": "सब Agents मेरे अंडर में!"
    }

@router.get("/agent/{name}")
def get_agent(name: str):
    """Kisi bhi agent ka detail"""
    if name in AGENTS:
        return {
            "name": name,
            "endpoint": AGENTS[name],
            "status": "active"
        }
    return {"error": "Agent not found", "available": list(AGENTS.keys())}
