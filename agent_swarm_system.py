"""
🦁 SINGH JI AI ULTRA v8.0 — SMART SARWAN AGENT SWARM
On-Demand Loading | Module-Based Activation | Auto-Scaling
"""

import os
import json
import asyncio
import time
import random
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# 🦁 MODULE → AGENT MAPPING (Kaunsa agent kis module se linked)
# ═══════════════════════════════════════════════════════
MODULE_AGENT_MAP = {
    # Agriculture Claw
    "mandi": ["AGR-002", "AGR-011", "AGR-027", "AGR-028"],
    "weather": ["AGR-003", "AGR-023", "AGR-029"],
    "plant_id": ["AGR-004", "AGR-024"],
    "pani": ["AGR-006", "AGR-026"],

    # Health Claw
    "bachpan": ["HLT-012"],
    "emergency": ["HLT-004", "HLT-029"],
    "horoscope": ["HLT-010"],

    # Finance Claw
    "banking": ["FIN-005", "FIN-006", "FIN-007"],
    "currency": ["FIN-016", "FIN-022"],
    "fuel": ["FIN-003"],
    "goldrate": ["FIN-002"],
    "payment": ["FIN-001", "FIN-019", "FIN-027"],
    "upi": ["FIN-001", "FIN-027"],
    "retirement_tax": ["FIN-013", "FIN-011"],

    # Education Claw
    "ai_chat": ["EDU-001", "EDU-003", "AI-001", "AI-005"],
    "language": ["EDU-007", "VCE-001", "VCE-002"],
    "language_hub": ["EDU-007", "VCE-001", "VCE-002", "VCE-028"],

    # Governance Claw
    "govt": ["GOV-001", "GOV-002", "GOV-003", "GOV-030"],
    "sewer": ["GOV-029"],

    # Transport Claw
    "trolley": ["TRP-001", "TRP-002", "TRP-003"],
    "fuel": ["TRP-004"],

    # Voice Claw
    "voice": ["VCE-001", "VCE-005", "VCE-006", "VCE-027"],
    "voice_cmd": ["VCE-021", "VCE-027"],
    "voice_tts": ["VCE-006", "VCE-007", "VCE-008", "VCE-009"],
    "whisper": ["VCE-005"],
    "bhashini": ["VCE-001", "VCE-002"],

    # Media Claw
    "facebook": ["MED-004", "MED-013"],
    "youtube": ["MED-001", "MED-005", "MED-013"],
    "instagram": ["MED-004", "MED-007"],
    "singhji_tv": ["MED-001", "MED-013"],
    "search": ["MED-003", "AI-009"],

    # Safety Claw
    "guard_agent": ["SFT-001", "SFT-003", "SFT-015"],
    "supreme_agent": ["SFT-030", "BOS-001", "AI-020"],

    # Boss Claw
    "admin": ["BOS-001", "BOS-004", "BOS-007"],
    "analytics": ["BOS-007", "BOS-008"],
    "daily_report": ["BOS-004"],
    "meta_agent": ["BOS-001", "AI-004"],

    # Core AI Claw
    "aavishkar": ["AI-001", "AI-003", "AI-005"],
    "aavishkar_ai": ["AI-001", "AI-003", "AI-005", "AI-011"],
    "trishul": ["AI-013", "AI-014", "AI-015"],
    "trishul_memory": ["AI-013", "AI-014"],
    "supabase_memory": ["AI-013"],

    # News
    "news": ["MED-003", "EDU-018"],
    "news_scheduler": ["MED-003", "BOS-009"],
    "newsdata": ["MED-003"],
    "currents_api": ["MED-003"],

    # Schedule
    "schedule": ["BOS-009", "EDU-029"],
    "news_scheduler": ["BOS-009", "MED-003"],

    # Rozgar
    "rozgar": ["EDU-004", "EDU-020", "EDU-022"],

    # Telegram
    "telegram_bot": ["BOS-009", "VCE-027"],

    # WhatsApp
    "whatsapp": ["BOS-009", "VCE-027"],

    # Memory
    "memory": ["AI-013", "AI-014"],

    # Init
    "init": ["BOS-001", "AI-020"],
}

# ═══════════════════════════════════════════════════════
# 🦁 API KEY → AGENT MAPPING (Key available = Related agents active)
# ═══════════════════════════════════════════════════════
KEY_AGENT_MAP = {
    "OPENWEATHER": ["AGR-003", "AGR-023", "AGR-029"],
    "CURRENTS": ["MED-003", "EDU-018"],
    "GROQ": ["AI-001", "AI-005", "AI-011", "EDU-001", "EDU-003"],
    "GEMINI": ["AI-003", "AI-012", "EDU-001"],
    "TELEGRAM": ["BOS-009", "VCE-027"],
    "SUPABASE": ["AI-013", "AI-014"],
    "CEREBRAS": ["AI-001", "AI-005"],
    "CF": ["VCE-001", "VCE-002", "EDU-007"],
    "HUGGINGFACE": ["AI-010", "AI-012", "VCE-003"],
    "MANDI": ["AGR-002", "AGR-011"],
    "NEWSDATA": ["MED-003", "EDU-018"],
    "PLANT_ID": ["AGR-004", "AGR-024"],
    "RAPIDAPI": ["FIN-008", "FIN-023", "TRP-001"],
    "RAZORPAY": ["FIN-001", "FIN-019", "FIN-027"],
    "TAVILY": ["MED-003", "AI-009"],
    "TWILIO": ["VCE-013", "VCE-027"],
    "FACEBOOK": ["MED-004", "MED-013"],
    "GMAIL": ["MED-004"],
    "INSTAGRAM": ["MED-004", "MED-007"],
    "YOUTUBE": ["MED-001", "MED-005", "MED-013"],
    "BHASHINI": ["VCE-001", "VCE-002", "EDU-007"],
}

class AgentStatus(Enum):
    OFFLINE = "offline"
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    PAUSED = "paused"

class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass
class Agent:
    id: str
    name: str
    role: str
    claw: str
    claw_name: str
    status: AgentStatus = AgentStatus.OFFLINE
    linked_modules: List[str] = field(default_factory=list)
    required_keys: List[str] = field(default_factory=list)
    last_active: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_task: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "claw": self.claw, "claw_name": self.claw_name,
            "status": self.status.value, "linked_modules": self.linked_modules,
            "required_keys": self.required_keys,
            "last_active": self.last_active, "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed, "current_task": self.current_task,
        }

class SmartSarwanSwarm:
    """
    🦁 SMART AGENT SWARM — On-Demand Loading

    Features:
    - Module active hone pe related agents load
    - API key available = related agents activate
    - Lazy loading — pehle se sab load nahi
    - Auto-scale based on traffic
    - Memory efficient
    """

    def __init__(self, config_path: str = "singhji_310_agent_swarm.json"):
        self.all_agents: Dict[str, Agent] = {}  # Sab 330 agents (metadata only)
        self.active_agents: Dict[str, Agent] = {}  # Currently loaded agents
        self.config_path = config_path
        self.module_status: Dict[str, bool] = {}  # Kaunsa module active hai
        self.key_status: Dict[str, bool] = {}  # Kaunsi key available hai
        self.swarm_mode = False
        self.max_parallel = 20  # Reduced for memory efficiency
        self._load_threshold = 10  # Agents ka minimum batch size

        self.stats = {
            "total_registered": 0,
            "currently_loaded": 0,
            "active_running": 0,
            "peak_loaded": 0,
            "memory_saved": 0,  # Estimated
        }

    def register_all_agents(self):
        """Sirf metadata load karega — 330 agents ki info, memory mein nahi"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = self._get_default_config()

        for claw_key, claw_data in config.get("claw_groups", {}).items():
            for agent_data in claw_data.get("agents_list", []):
                agent_id = agent_data["id"]

                # Find linked modules
                linked = []
                for mod, agents in MODULE_AGENT_MAP.items():
                    if agent_id in agents:
                        linked.append(mod)

                # Find required keys
                required = []
                for key, agents in KEY_AGENT_MAP.items():
                    if agent_id in agents:
                        required.append(key)

                agent = Agent(
                    id=agent_id,
                    name=agent_data["name"],
                    role=agent_data["role"],
                    claw=claw_key,
                    claw_name=claw_data.get("name", claw_key),
                    status=AgentStatus.OFFLINE,
                    linked_modules=linked,
                    required_keys=required,
                )
                self.all_agents[agent_id] = agent

        self.stats["total_registered"] = len(self.all_agents)
        logger.info(f"🦁 {len(self.all_agents)} agents REGISTERED (metadata only, 0 memory)")
        return len(self.all_agents)

    def sync_with_modules(self, modules_status: Dict[str, dict], available_keys: Dict[str, bool]):
        """
        Main.py se call hoga — jab modules load hote hain
        modules_status: {"weather": {"active": True, "needs_key": "OPENWEATHER"}, ...}
        """
        self.module_status = {name: info.get("active", False) for name, info in modules_status.items()}
        self.key_status = available_keys

        # Decide kaunse agents load karne hain
        agents_to_load = set()
        agents_to_unload = set()

        for agent_id, agent in self.all_agents.items():
            should_load = self._should_agent_load(agent)
            is_loaded = agent_id in self.active_agents

            if should_load and not is_loaded:
                agents_to_load.add(agent_id)
            elif not should_load and is_loaded:
                agents_to_unload.add(agent_id)

        # Load agents
        for agent_id in agents_to_load:
            self._load_agent(agent_id)

        # Unload agents
        for agent_id in agents_to_unload:
            self._unload_agent(agent_id)

        logger.info(f"🐝 Sync complete: +{len(agents_to_load)} loaded, -{len(agents_to_unload)} unloaded")
        logger.info(f"🐝 Active agents: {len(self.active_agents)}/{len(self.all_agents)}")
        return {
            "loaded": len(agents_to_load),
            "unloaded": len(agents_to_unload),
            "active": len(self.active_agents),
            "total": len(self.all_agents),
        }

    def _should_agent_load(self, agent: Agent) -> bool:
        """Decide karna: agent load hona chahiye ya nahi"""
        # 1. Agar koi linked module active hai → LOAD
        for mod in agent.linked_modules:
            if self.module_status.get(mod, False):
                # Check if module needs key and key is available
                return True

        # 2. Agar required key available hai → LOAD
        for key in agent.required_keys:
            if self.key_status.get(key, False):
                return True

        # 3. Boss agents hamesha load (critical)
        if agent.claw == "claw_10_boss":
            return True

        # 4. Core AI agents hamesha load
        if agent.claw == "claw_11_core_ai":
            return True

        return False

    def _load_agent(self, agent_id: str):
        """Agent ko memory mein load karega"""
        if agent_id in self.active_agents:
            return

        agent = self.all_agents[agent_id]
        agent.status = AgentStatus.IDLE
        agent.last_active = datetime.now().isoformat()
        self.active_agents[agent_id] = agent

        self.stats["currently_loaded"] = len(self.active_agents)
        if len(self.active_agents) > self.stats["peak_loaded"]:
            self.stats["peak_loaded"] = len(self.active_agents)

        logger.debug(f"✅ Loaded agent {agent_id} ({agent.name})")

    def _unload_agent(self, agent_id: str):
        """Agent ko memory se unload karega"""
        if agent_id not in self.active_agents:
            return

        agent = self.active_agents[agent_id]
        agent.status = AgentStatus.OFFLINE
        agent.current_task = None
        del self.active_agents[agent_id]

        self.stats["currently_loaded"] = len(self.active_agents)
        logger.debug(f"⛔ Unloaded agent {agent_id}")

    def on_request(self, module_name: str, task_type: str = None) -> List[Agent]:
        """
        Jab user request aaye — tab related agents load ho
        Returns: List of available agents for this request
        """
        # Find agents linked to this module
        linked_agent_ids = MODULE_AGENT_MAP.get(module_name, [])

        available = []
        for agent_id in linked_agent_ids:
            # Load if not already loaded
            if agent_id not in self.active_agents:
                self._load_agent(agent_id)

            agent = self.active_agents.get(agent_id)
            if agent and agent.status in [AgentStatus.IDLE, AgentStatus.ACTIVE]:
                available.append(agent)

        # If no specific agents, use Core AI
        if not available:
            for agent_id in ["AI-020", "AI-004", "AI-001"]:
                if agent_id not in self.active_agents:
                    self._load_agent(agent_id)
                agent = self.active_agents.get(agent_id)
                if agent and agent.status in [AgentStatus.IDLE, AgentStatus.ACTIVE]:
                    available.append(agent)

        return available

    def get_status(self) -> Dict[str, Any]:
        """Full system status"""
        claw_stats = {}
        for agent in self.active_agents.values():
            if agent.claw not in claw_stats:
                claw_stats[agent.claw] = {"name": agent.claw_name, "total": 0, "active": 0, "idle": 0, "busy": 0}
            claw_stats[agent.claw]["total"] += 1
            if agent.status == AgentStatus.ACTIVE:
                claw_stats[agent.claw]["active"] += 1
            elif agent.status == AgentStatus.IDLE:
                claw_stats[agent.claw]["idle"] += 1
            elif agent.status == AgentStatus.BUSY:
                claw_stats[agent.claw]["busy"] += 1

        # Calculate memory saved
        unloaded = len(self.all_agents) - len(self.active_agents)
        memory_saved_mb = unloaded * 0.5  # Estimate: 0.5MB per agent

        return {
            "system": "Singh Ji AI Ultra v8.0 — Smart Swarm",
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total_registered": len(self.all_agents),
                "currently_loaded": len(self.active_agents),
                "active_running": sum(1 for a in self.active_agents.values() if a.status == AgentStatus.ACTIVE),
                "idle": sum(1 for a in self.active_agents.values() if a.status == AgentStatus.IDLE),
                "busy": sum(1 for a in self.active_agents.values() if a.status == AgentStatus.BUSY),
                "peak_loaded": self.stats["peak_loaded"],
                "memory_saved_mb": round(memory_saved_mb, 1),
            },
            "modules": self.module_status,
            "keys": self.key_status,
            "claws": claw_stats,
            "swarm_mode": self.swarm_mode,
        }

    def get_all_agents(self, status_filter: str = None) -> List[Dict]:
        """Currently loaded agents return karega"""
        agents = self.active_agents.values()
        if status_filter:
            agents = [a for a in agents if a.status.value == status_filter]
        return [a.to_dict() for a in agents]

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Agent detail — load if not loaded"""
        if agent_id not in self.active_agents and agent_id in self.all_agents:
            self._load_agent(agent_id)
        agent = self.active_agents.get(agent_id)
        return agent.to_dict() if agent else None

    def _get_default_config(self):
        """Default config agar JSON nahi mile"""
        return {"claw_groups": {}}

# ═══════════════════════════════════════════════════════
# 🦁 GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════
SMART_SWARM = SmartSarwanSwarm()
