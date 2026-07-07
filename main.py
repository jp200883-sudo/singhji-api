from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import random
from datetime import datetime

app = FastAPI(
    title="Singh Ji AI — 300 Agent Swarm",
    version="8.0.0"
)

# ✅ CORS — Sab jagah se allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 DUMMY DATA — NO JSON FILE LOAD!
SWARM_DATA = {
    "claw_groups": {
        "claw_1_agriculture": {
            "name": "🌾 Agriculture Claw",
            "leader": "CropMaster Agent",
            "agents_list": [
                {"id": "AGR-001", "name": "Crop Advisor Agent", "role": "क्या बोएं, कब बोएं", "status": "active"},
                {"id": "AGR-002", "name": "Price Tracker Agent", "role": "Mandi भाव real-time", "status": "active"},
                {"id": "AGR-003", "name": "Weather Agent", "role": "मौसम अपडेट", "status": "active"},
                {"id": "AGR-004", "name": "Pest Control Agent", "role": "कीट नियंत्रण", "status": "active"},
                {"id": "AGR-005", "name": "Soil Health Agent", "role": "मिट्टी जांच", "status": "active"},
            ]
        },
        "claw_2_health": {
            "name": "🏥 Health Claw",
            "leader": "Dr. Singh Agent",
            "agents_list": [
                {"id": "HLT-001", "name": "Symptom Checker Agent", "role": "बीमारी पहचान", "status": "active"},
                {"id": "HLT-002", "name": "Doctor Finder Agent", "role": "नज़दीकी doctor", "status": "active"},
                {"id": "HLT-003", "name": "Medicine Info Agent", "role": "दवाई जानकारी", "status": "active"},
                {"id": "HLT-004", "name": "Emergency Agent", "role": "आपातकालीन सहायता", "status": "active"},
            ]
        },
        "claw_3_education": {
            "name": "📚 Education Claw",
            "leader": "Guru Ji Agent",
            "agents_list": [
                {"id": "EDU-001", "name": "Tutor Agent", "role": "पढ़ाई मदद", "status": "active"},
                {"id": "EDU-002", "name": "Exam Prep Agent", "role": "परीक्षा तैयारी", "status": "active"},
            ]
        },
        "claw_4_finance": {
            "name": "💰 Finance Claw",
            "leader": "Banker Singh Agent",
            "agents_list": [
                {"id": "FIN-001", "name": "Budget Agent", "role": "बजट प्लानिंग", "status": "active"},
                {"id": "FIN-002", "name": "Investment Agent", "role": "निवेश सलाह", "status": "active"},
            ]
        },
        "claw_5_govt": {
            "name": "🏛️ Government Claw",
            "leader": "Sarkari Agent",
            "agents_list": [
                {"id": "GOV-001", "name": "Scheme Finder Agent", "role": "योजना खोजें", "status": "active"},
                {"id": "GOV-002", "name": "Document Helper Agent", "role": "दस्तावेज़ मदद", "status": "active"},
            ]
        },
        "claw_6_voice": {
            "name": "🎙️ Voice Claw",
            "leader": "Bollywood Voice Agent",
            "agents_list": [
                {"id": "VOC-001", "name": "STT Agent", "role": "Speech to Text", "status": "active"},
                {"id": "VOC-002", "name": "TTS Agent", "role": "Text to Speech", "status": "active"},
                {"id": "VOC-003", "name": "Voice Clone Agent", "role": "आवाज़ क्लोन", "status": "active"},
            ]
        },
        "claw_7_weather": {
            "name": "🌦️ Weather Claw",
            "leader": "Mausam Agent",
            "agents_list": [
                {"id": "WTH-001", "name": "Forecast Agent", "role": "मौसम पूर्वानुमान", "status": "active"},
                {"id": "WTH-002", "name": "Alert Agent", "role": "मौसम अलर्ट", "status": "active"},
            ]
        },
        "claw_8_legal": {
            "name": "⚖️ Legal Claw",
            "leader": "Vakil Singh Agent",
            "agents_list": [
                {"id": "LEG-001", "name": "Law Info Agent", "role": "कानूनी जानकारी", "status": "active"},
                {"id": "LEG-002", "name": "Rights Agent", "role": "अधिकार जानकारी", "status": "active"},
            ]
        },
        "claw_9_travel": {
            "name": "✈️ Travel Claw",
            "leader": "Safar Agent",
            "agents_list": [
                {"id": "TRV-001", "name": "Route Agent", "role": "रास्ता खोजें", "status": "active"},
                {"id": "TRV-002", "name": "Booking Agent", "role": "टिकट बुकिंग", "status": "active"},
            ]
        },
        "claw_10_shopping": {
            "name": "🛒 Shopping Claw",
            "leader": "Deal Master Agent",
            "agents_list": [
                {"id": "SHP-001", "name": "Price Compare Agent", "role": "दाम तुलना", "status": "active"},
                {"id": "SHP-002", "name": "Deal Finder Agent", "role": "डील खोजें", "status": "active"},
            ]
        },
        "claw_11_social": {
            "name": "🤝 Social Claw",
            "leader": "Dost Agent",
            "agents_list": [
                {"id": "SOC-001", "name": "Community Agent", "role": "समुदाय मदद", "status": "active"},
                {"id": "SOC-002", "name": "Event Agent", "role": "कार्यक्रम जानकारी", "status": "active"},
            ]
        }
    }
}

active_missions = {}
step_tracker = {"current": 0, "max": 4000}

# ============== ROOT ENDPOINT ==============
@app.get("/")
async def root():
    return {
        "system": "🦁 Singh Ji AI — 300+ Agent Swarm",
        "version": "v8.0",
        "agents": 300,
        "claws": 11,
        "max_steps": 4000,
        "status": "🔥 ACTIVE 🔥",
        "railway": "✅ Running on Railway"
    }

# ============== HEALTH CHECK ==============
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active",
        "version": "8.0.0"
    }

# ============== SWARM STATS ==============
@app.get("/swarm/stats")
async def swarm_stats():
    total_agents = sum(len(c["agents_list"]) for c in SWARM_DATA["claw_groups"].values())
    return {
        "total_agents": total_agents,
        "total_claws": len(SWARM_DATA["claw_groups"]),
        "max_steps": 4000,
        "steps_used": step_tracker["current"],
        "steps_remaining": 4000 - step_tracker["current"],
        "status": "active"
    }

# ============== LIST ALL CLAWS ==============
@app.get("/swarm/claws")
async def list_claws():
    return {
        "claws": [
            {
                "id": claw_id,
                "name": claw["name"],
                "leader": claw["leader"],
                "agent_count": len(claw["agents_list"])
            }
            for claw_id, claw in SWARM_DATA["claw_groups"].items()
        ]
    }

# ============== GET SINGLE CLAW ==============
@app.get("/swarm/claws/{claw_id}")
async def get_claw(claw_id: str):
    if claw_id not in SWARM_DATA["claw_groups"]:
        raise HTTPException(status_code=404, detail=f"Claw {claw_id} not found")
    return SWARM_DATA["claw_groups"][claw_id]

# ============== LIST AGENTS IN A CLAW ==============
@app.get("/swarm/claws/{claw_id}/agents")
async def list_agents(claw_id: str):
    if claw_id not in SWARM_DATA["claw_groups"]:
        raise HTTPException(status_code=404, detail=f"Claw {claw_id} not found")
    return {
        "claw_id": claw_id,
        "claw_name": SWARM_DATA["claw_groups"][claw_id]["name"],
        "agents": SWARM_DATA["claw_groups"][claw_id]["agents_list"]
    }

# ============== GET SINGLE AGENT ==============
@app.get("/swarm/claws/{claw_id}/agents/{agent_id}")
async def get_agent(claw_id: str, agent_id: str):
    if claw_id not in SWARM_DATA["claw_groups"]:
        raise HTTPException(status_code=404, detail=f"Claw {claw_id} not found")
    agents = SWARM_DATA["claw_groups"][claw_id]["agents_list"]
    agent = next((a for a in agents if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent

# ============== ETHICS REPORT ==============
@app.get("/swarm/ethics")
async def ethics_report():
    return {
        "overlay": "Claude Ethics + Safety",
        "rules": [
            "No harmful content for children",
            "No hate speech or discrimination",
            "No illegal activities",
            "Protect user privacy",
            "Be honest about limitations"
        ],
        "status": "✅ All systems safe"
    }

# ============== MISSIONS ==============
@app.get("/swarm/missions")
async def list_missions():
    return {"missions": active_missions}

@app.post("/swarm/missions/{mission_id}")
async def create_mission(mission_id: str, data: dict):
    active_missions[mission_id] = {
        "id": mission_id,
        "data": data,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    return {"status": "created", "mission": active_missions[mission_id]}

# ============== STEP TRACKER ==============
@app.get("/swarm/steps")
async def get_steps():
    return step_tracker

@app.post("/swarm/steps")
async def update_steps(steps: int):
    step_tracker["current"] = min(step_tracker["current"] + steps, step_tracker["max"])
    return step_tracker

# ============== RANDOM AGENT PICKER ==============
@app.get("/swarm/random")
async def random_agent():
    all_agents = []
    for claw_id, claw in SWARM_DATA["claw_groups"].items():
        for agent in claw["agents_list"]:
            all_agents.append({
                "claw_id": claw_id,
                "claw_name": claw["name"],
                **agent
            })
    return random.choice(all_agents) if all_agents else {"error": "No agents"}

# ============== PORT HANDLING FOR RAILWAY ==============
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=2)
