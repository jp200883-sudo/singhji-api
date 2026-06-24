from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import importlib
import os
import sys
from datetime import datetime

app = Flask(__name__, static_folder='frontend')
CORS(app)

# ⚡ MODULE REGISTRY
MODULES = {
    'u1': {'name': 'Proactive AI', 'path': 'modules.u1_proactive_ai.handler'},
    'u2': {'name': 'Gender Detection', 'path': 'modules.u2_gender_detection.handler'},
    'u3': {'name': 'Language Hub', 'path': 'modules.u3_language_hub.handler'},
    'u4': {'name': 'Auto Message', 'path': 'modules.u4_auto_message.handler'},
    'u5': {'name': 'Ramayan Speak', 'path': 'modules.u5_ramayan_speak.handler'},
    'u6': {'name': 'PWA Lite', 'path': 'modules.u6_pwa_lite.handler'},
    'u8': {'name': 'MADAD Button', 'path': 'modules.u8_madad_button.handler'},
    'u9': {'name': 'Singh Ji Haath', 'path': 'modules.u9_singh_ji_haath.handler'},
}

# 🏠 HOME — Frontend Serve (SIRF एक बार!)
@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

# 📊 STATUS — API Info (अलग route!)
@app.route('/api/status')
def status():
    return jsonify({
        "app": "Singh Ji AI Ultra v4.0",
        "status": "live",
        "mode": "KELA",
        "timestamp": datetime.now().isoformat(),
        "modules_loaded": len(MODULES),
        "modules": {k: v['name'] for k, v in MODULES.items()},
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "modules": "/api/<module>/<path:path>"
        }
    })

# 💓 HEALTH CHECK
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "app": "Singh Ji AI Ultra v4.0",
        "mode": "KELA",
        "timestamp": datetime.now().isoformat(),
        "modules_registered": len(MODULES)
    }), 200

# 🧩 LAZY MODULE ROUTER
@app.route('/api/<module>/<path:path>', methods=['GET', 'POST'])
def module_router(module, path):
    if module not in MODULES:
        return jsonify({"error": "Module not found", "available": list(MODULES.keys())}), 404
    try:
        module_path = MODULES[module]['path']
        module_name, handler_name = module_path.rsplit('.', 1)
        mod = importlib.import_module(module_name)
        handler = getattr(mod, handler_name)
        return handler(path, request)
    except Exception as e:
        return jsonify({"error": str(e), "module": module}), 500

# 🧩 MODULE INFO
@app.route('/api/<module>/info')
def module_info(module):
    if module not in MODULES:
        return jsonify({"error": "Module not found"}), 404
    return jsonify({
        "module": module,
        "name": MODULES[module]['name'],
        "status": "registered",
        "loaded": "lazy"
    })

# 📁 STATIC FILES
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

# 🚀 RUN
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
