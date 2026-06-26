# core/app.py — v5.0 (Fixed)
from flask import Flask, jsonify, request
from flask_cors import CORS
import importlib
import os
from datetime import datetime

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ✅ FIXED MODULES — paths match actual folder names!
MODULES = {
    'telegram': {'name': 'Telegram Bot', 'path': 'modules.telegram.handler'},
    'plant': {'name': 'Plant ID', 'path': 'modules.plant.handler'},
    'memory': {'name': 'Supabase Memory', 'path': 'modules.memory.handler'},
    'language': {'name': 'Language Hub', 'path': 'modules.language.handler'},
}

# 🐛 DEBUG ENDPOINT — MODULES ke baad, HOME se pehle
@app.route('/api/debug/<module>')
def debug_module(module):
    try:
        module_path = MODULES[module]['path']
        module_name, handler_name = module_path.rsplit('.', 1)
        
        mod = importlib.import_module(module_name)
        has_handler = hasattr(mod, handler_name)
        attrs = [a for a in dir(mod) if not a.startswith('_')]
        
        return jsonify({
            "module": module,
            "path": module_path,
            "imported": True,
            "has_handler": has_handler,
            "handler_name": handler_name,
            "available_attributes": attrs,
            "file_location": mod.__file__ if hasattr(mod, '__file__') else 'unknown'
        })
    except Exception as e:
        import traceback
        return jsonify({
            "module": module,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

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
