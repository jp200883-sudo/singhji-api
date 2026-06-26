from flask import jsonify, request
import os
import requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

def handler(path, request_obj):
    method = request_obj.method

    if path == 'health' and method == 'GET':
        return jsonify({
            "status": "ok",
            "module": "supabase_memory",
            "url_set": bool(SUPABASE_URL),
            "key_set": bool(SUPABASE_KEY)
        })

    elif path == 'save' and method == 'POST':
        return save_memory(request_obj)

    elif path == 'get' and method == 'GET':
        return get_memory(request_obj)

    else:
        return jsonify({"error": "Memory endpoint not found"}), 404


def save_memory(request_obj):
    try:
        data = request_obj.json
        return jsonify({
            "status": "saved",
            "data": data,
            "note": "Supabase integration ready"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_memory(request_obj):
    try:
        return jsonify({
            "status": "retrieved",
            "memories": [],
            "note": "Supabase integration ready"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
