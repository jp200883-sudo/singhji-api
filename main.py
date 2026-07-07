from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import random
from datetime import datetime

# SINGLE FastAPI app
app = FastAPI(
    title="Singh Ji AI — 300 Agent Swarm",
    version="8.0.0"
)

# CORS — ONCE only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy data
SWARM_DATA = {
    "claw_groups": {
        "claw_1_agriculture": {
            "name": "🌾 Agriculture Claw",
            "leader": "CropMaster Agent",
            "agents_list": [
                {"id": "AGR-001", "name": "Crop Advisor Agent", "role": "क्या बोएं, कब बोएं", "status": "active"},
                {"id": "AGR-002", "name": "Price Tracker Agent", "role": "Mandi भाव real-time", "status": "active"},
            ]
        },
        "claw_2_health": {
            "name": "🏥 Health Claw",
            "leader": "Dr. Singh Agent",
            "agents_list": [
                {"id": "HLT-001", "name": "Symptom Checker Agent", "role": "बीमारी पहचान", "status": "active"},
                {"id": "HLT-002", "name": "Doctor Finder Agent", "role": "नज़दीकी doctor", "status": "active"},
            ]
        }
    }
}

active_missions = {}
step_tracker = {"current": 0, "max": 4000}

@app.get("/")
async def root():
    return {
        "system": "🦁 Singh Ji AI — 300+ Agent Swarm",
        "version": "v8.0",
        "agents": 300,
        "claws": 11,
        "max_steps": 4000,
        "status": "🔥 ACTIVE 🔥"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
