# api.py (root level)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Singh Ji AI Ultra v7.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import modules from core.modules
modules_loaded = []
modules_failed = []

module_names = [
    "ai_chat", "currents_api", "email", "emergency", "govt",
    "karmachari", "mandi", "master_data", "meta_agent",
    "news_scheduler", "newsdata", "pani", "plant_id",
    "rozgar", "schedule", "search", "sewer", "singhji_agent",
    "singhji_tv", "social", "supabase_memory", "superior_agent",
    "upi", "voice", "voice_cmd", "voice_tts", "weather",
    # Folder modules with handler.py
    "adminpanel.handler", "banking.handler", "currency.handler",
    "entertainment.handler", "language.handler", "language_hub.handler",
    "railway.handler", "telegram_bot.handler"
]

for mod_name in module_names:
    try:
        mod = __import__(f"core.modules.{mod_name}", fromlist=["router"])
        if hasattr(mod, "router"):
            app.include_router(mod.router)
            modules_loaded.append(mod_name)
            print(f"✅ Loaded: {mod_name}")
    except Exception as e:
        modules_failed.append(f"{mod_name}: {str(e)}")
        print(f"❌ Failed: {mod_name}: {str(e)}")

print(f"\n🔥 Singh Ji AI Ultra v7.0 STARTED!")
print(f"✅ Loaded: {len(modules_loaded)} modules")
if modules_failed:
    print(f"❌ Failed: {modules_failed}")
print("👑 Singh Ji ka raj shuru!")

@app.get("/")
def root():
    return {
        "message": "👑 Singh Ji AI Ultra v7.0 - Bharat to the World!",
        "loaded": len(modules_loaded),
        "failed": len(modules_failed)
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "loaded": modules_loaded,
        "failed": modules_failed
    }
