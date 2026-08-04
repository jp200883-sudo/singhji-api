import os

modules = [
    "weather", "news", "mandi", "plant_doctor", "gold", "fuel", "tax_calc",
    "currency", "govt_schemes", "rozgar", "pani_helpline", "sewer", "ai_chat",
    "ai_chat_v2", "voice_ai", "search_web", "translate", "singhji_tv", "video_gen",
    "horoscope", "yojana_match", "emergency", "upi_info", "guard_agent",
    "social_agent", "system_status", "help_commands", "analytics", "daily_report",
    "supreme_ai", "supabase_memory", "whatsapp", "meta_agent", "language_hub",
    "swarm_status", "trolley"
]

for module in modules:
    path = f"modules/{module}/handler.py"
    if not os.path.exists(path):
        os.makedirs(f"modules/{module}", exist_ok=True)
        with open(path, "w") as f:
            f.write(f'''from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def {module}_handler():
    return {{"status": "ok", "module": "{module}"}}
''')
        print(f"✅ {module} handler created")
