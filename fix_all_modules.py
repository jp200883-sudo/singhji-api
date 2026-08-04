import os

# Aapke saare modules
modules = [
    "supreme_agent", "ai_chat", "weather", "mandi", "newsdata",
    "plant_id", "telegram_bot", "whatsapp", "trolley",
    "daily_report", "analytics", "upi", "news_scheduler",
    "voice_tts", "language"
]

print("🦁 Singh Ji AI - Sab Modules Theek Kar Raha Hun...")
print("="*50)

for module in modules:
    module_path = f"modules/{module}"
    os.makedirs(module_path, exist_ok=True)
    
    # ========== __init__.py ==========
    with open(f"{module_path}/__init__.py", "w") as f:
        f.write(f"""from .handler import router

__all__ = ['router']
""")
    
    # ========== handler.py ==========
    handler_content = f'''from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def {module}_handler():
    return {{"status": "ok", "module": "{module}"}}

# ========== Aapka actual logic yahan aayega ==========
# Jaise:
# @router.post("/action")
# async def action():
#     return {{"result": "done"}}
'''
    with open(f"{module_path}/handler.py", "w") as f:
        f.write(handler_content)
    
    print(f"✅ {module}")

print("="*50)
print("🎉 Sab modules theek ho gaye!")
