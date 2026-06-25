# core/app.py — v5.0 Update
from flask import Flask, jsonify, request
from flask_cors import CORS
import importlib
import os
from datetime import datetime

app = Flask(__name__)

# ✅ CORS v5.0
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ⚡ MODULE REGISTRY (U3 हटा दिया)
MODULES = {
    'u1': {'name': 'Proactive AI', 'path': 'modules.u1_proactive_ai.handler'},
    'u2': {'name': 'Gender Detection', 'path': 'modules.u2_gender_detection.handler'},
    'u4': {'name': 'Auto Message', 'path': 'modules.u4_auto_message.handler'},
    'u5': {'name': 'Ramayan Speak', 'path': 'modules.u5_ramayan_speak.handler'},
    'u6': {'name': 'PWA Lite', 'path': 'modules.u6_pwa_lite.handler'},
    'u8': {'name': 'MADAD Button', 'path': 'modules.u8_madad_button.handler'},
    'u9': {'name': 'Singh Ji Haath', 'path': 'modules.u9_singh_ji_haath.handler'},
    'admin': {'name': 'Admin Panel', 'path': 'modules.admin_panel.handler'},
    'telegram': {'name': 'Telegram Bot', 'path': 'modules.telegram_bot.handler'},
    'plant': {'name': 'Plant ID', 'path': 'modules.plant_id.handler'},
    'memory': {'name': 'Supabase Memory', 'path': 'modules.supabase_memory.handler'},
    'language': {'name': 'Language Hub', 'path': 'modules.language_hub.handler'},
}

# 🏠 HOME
@app.route('/')
def home():
    return jsonify({
        "app": "Singh Ji AI Ultra v5.0",
        "status": "live",
        "phase": 4,
        "message": "🦁 Singh Ji AI Ultra v5.0 is live!"
    })

# 💓 HEALTH
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "app": "Singh Ji AI Ultra v5.0",
        "phase": 4,
        "timestamp": datetime.now().isoformat(),
        "modules": len(MODULES),
        "bhashini": "active" if os.environ.get('BHASHINI_API_KEY') else "pending"
    }), 200

# 📊 STATUS
@app.route('/api/status')
def status():
    return jsonify({
        "app": "Singh Ji AI Ultra v5.0",
        "phase": 4,
        "modules": {k: v['name'] for k, v in MODULES.items()},
        "total_modules": len(MODULES)
    })

# 🧩 MODULE ROUTER
@app.route('/api/<module>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def module_router(module, path):
    if module not in MODULES:
        return jsonify({"error": "Module not found", "available": list(MODULES.keys())}), 404
    try:
        module_path = MODULES[module]['path']
        module_name, handler_name = module_path.rsplit('.', 1)
        mod = importlib.import_module(module_name)
        handler = getattr(mod, handler_name)
        return handler(path, request)
    except ModuleNotFoundError as e:
        return jsonify({"error": f"Module not loaded: {str(e)}", "module": module}), 500
    except Exception as e:
        return jsonify({"error": str(e), "module": module}), 500

# 🚀 RUN
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
