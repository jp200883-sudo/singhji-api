"""
Singh Ji AI Ultra v4.0 — KELA Mode Core
Lightweight bootstrap, lazy module loading
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS   
import importlib
import os
from datetime import datetime

app = Flask(__name__,
    template_folder='../templates',
    static_folder='../static'
)
CORS(app)   

# ⚡ MODULE REGISTRY — Add U3-U6 here when ready
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
@app.route('/')
def home():
    return jsonify({
        "status": "Singh Ji AI Ultra v4.0 is LIVE!",
        "creator": "JP Singh Ji, Kanpur",
        "version": "4.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({
        "reply": f"Singh Ji ne sun liya: {message}",
        "status": "success"
    })
# 🏠 HOME — Welcome + Status
@app.route('/')
def home():
    return jsonify({
        "app": "Singh Ji AI Ultra v4.0",
        "status": "live",
        "mode": "KELA",
        "timestamp": datetime.now().isoformat(),
        "modules_loaded": len(MODULES),
        "modules": {k: v['name'] for k, v in MODULES.items()},
        "endpoints": {
            "health": "/api/health",
            "modules": "/api/<module>/<path:path>",
            "admin": "/admin"
        }
    })

# 💓 HEALTH CHECK — Render uses this
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "app": "Singh Ji AI Ultra v4.0",
        "mode": "KELA",
        "timestamp": datetime.now().isoformat(),
        "memory": "lightweight",
        "modules_registered": len(MODULES)
    }), 200

# 🧩 LAZY MODULE ROUTER — Load only when called!
@app.route('/api/<module>/<path:path>', methods=['GET', 'POST'])
def module_router(module, path):
    """KELA Mode: Module loads ONLY when API called"""
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

# 🧩 MODULE INFO — Check without loading
@app.route('/api/<module>/info')
def module_info(module):
    if module not in MODULES:
        return jsonify({"error": "Module not found"}), 404
    return jsonify({
        "module": module,
        "name": MODULES[module]['name'],
        "status": "registered",
        "loaded": module in sys.modules if 'sys' in dir() else "lazy"
    })

# 🎛️ ADMIN DASHBOARD
@app.route('/admin')
def admin():
    return render_template('admin.html')

# 🚀 RUN
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
