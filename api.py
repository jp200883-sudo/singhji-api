# app.py — Singh Ji AI Ultra v7.0 — Main Application
# Render-ready, CORS-enabled, module-routed
# Bharat to the World 🇮🇳

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ─── Add project root to path ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Import Module Loader ────────────────────────────────────────
from api import init_modules, get_handler, MODULES

# ─── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Flask App Setup ─────────────────────────────────────────────
app = Flask(__name__, template_folder='templates')

# ─── CORS Setup (CRITICAL for frontend) ────────────────────────────
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://singhji-ai.github.io",      # Your GitHub Pages
            "http://localhost:*",                  # Local dev
            "https://*.onrender.com",              # Render domains
            "*"                                    # TEMP: Allow all for testing
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
    }
})

# ─── Initialize Modules on Startup ───────────────────────────────
logger.info("🚀 Initializing Singh Ji AI Ultra v7.0...")
init_modules()
logger.info(f"✅ {len(MODULES)} modules active")

# ════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Root endpoint — API status."""
    return jsonify({
        "status": "🟢 LIVE",
        "name": "Singh Ji AI Ultra v7.0",
        "tagline": "Bharat to the World 🇮🇳",
        "modules_loaded": len(MODULES),
        "modules": list(MODULES.keys()),
        "timestamp": datetime.utcnow().isoformat(),
        "server": "Render"
    })


@app.route('/api/modules')
def list_modules():
    """List all loaded modules with metadata."""
    module_list = []
    for name, info in MODULES.items():
        module_list.append({
            "name": name,
            "type": info.get("type", "unknown"),
            "status": info.get("status", "unknown"),
            "has_handler": info.get("handler") is not None
        })
    
    return jsonify({
        "total": len(module_list),
        "modules": module_list
    })


@app.route('/api/<module_name>', methods=['GET', 'POST'])
def module_route(module_name):
    """
    Universal module router.
    Routes requests to the correct module handler.
    """
    # Check if module exists
    if module_name not in MODULES:
        return jsonify({
            "error": f"Module '{module_name}' not found",
            "available_modules": list(MODULES.keys())
        }), 404
    
    module_info = MODULES[module_name]
    handler = module_info.get("handler")
    
    if not handler:
        return jsonify({
            "error": f"Module '{module_name}' has no handler function"
        }), 500
    
    # Prepare request data
    request_data = {
        "method": request.method,
        "args": request.args.to_dict(),
        "json": request.get_json(silent=True) or {},
        "headers": dict(request.headers),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Call module handler
        response = handler(request_data)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Module '{module_name}' handler error: {e}")
        return jsonify({
            "error": f"Module '{module_name}' execution failed",
            "details": str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint for Render."""
    return jsonify({
        "status": "healthy",
        "modules": len(MODULES),
        "uptime": "active",
        "version": "v7.0"
    })


# ════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "available_routes": [
            "/",
            "/api/modules",
            "/api/<module_name>",
            "/api/health"
        ]
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
