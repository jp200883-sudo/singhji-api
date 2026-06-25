from flask import jsonify, request
import os
import requests
from datetime import datetime

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def handler(path, request_obj):
    method = request_obj.method

    # Save chat history
    if path == 'chat/save' and method == 'POST':
        data = request_obj.json
        return save_chat(data)

    # Get chat history
    elif path == 'chat/get' and method == 'GET':
        user_id = request_obj.args.get('user_id')
        return get_chat(user_id)

    # Save user data
    elif path == 'user/save' and method == 'POST':
        data = request_obj.json
        return save_user(data)

    # Get user data
    elif path == 'user/get' and method == 'GET':
        user_id = request_obj.args.get('user_id')
        return get_user(user_id)

    # Store memory
    elif path == 'memory/save' and method == 'POST':
        data = request_obj.json
        return save_memory(data)

    # Get memory
    elif path == 'memory/get' and method == 'GET':
        user_id = request_obj.args.get('user_id')
        return get_memory(user_id)

    else:
        return jsonify({"error": "Supabase endpoint not found"}), 404


def save_chat(data):
    try:
        payload = {
            "user_id": data.get('user_id'),
            "message": data.get('message'),
            "response": data.get('response'),
            "language": data.get('language', 'hi'),
            "timestamp": datetime.now().isoformat()
        }

        url = f"{SUPABASE_URL}/rest/v1/chat_history"
        res = requests.post(url, json=payload, headers=HEADERS, timeout=10)

        if res.status_code in [200, 201]:
            return jsonify({"status": "saved", "id": res.json()[0].get('id') if res.json() else None})
        return jsonify({"error": "Failed to save", "details": res.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_chat(user_id):
    try:
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        url = f"{SUPABASE_URL}/rest/v1/chat_history?user_id=eq.{user_id}&order=timestamp.desc&limit=50"
        res = requests.get(url, headers=HEADERS, timeout=10)

        return jsonify({"status": "success", "data": res.json()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def save_user(data):
    try:
        payload = {
            "user_id": data.get('user_id'),
            "name": data.get('name'),
            "phone": data.get('phone'),
            "language": data.get('language', 'hi'),
            "plan": data.get('plan', 'free'),
            "created_at": datetime.now().isoformat()
        }

        url = f"{SUPABASE_URL}/rest/v1/users"
        res = requests.post(url, json=payload, headers=HEADERS, timeout=10)

        if res.status_code in [200, 201]:
            return jsonify({"status": "saved", "user_id": data.get('user_id')})
        return jsonify({"error": "Failed to save", "details": res.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user(user_id):
    try:
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        url = f"{SUPABASE_URL}/rest/v1/users?user_id=eq.{user_id}"
        res = requests.get(url, headers=HEADERS, timeout=10)

        data = res.json()
        if data:
            return jsonify({"status": "found", "data": data[0]})
        return jsonify({"status": "not_found"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def save_memory(data):
    try:
        payload = {
            "user_id": data.get('user_id'),
            "key": data.get('key'),
            "value": data.get('value'),
            "timestamp": datetime.now().isoformat()
        }

        url = f"{SUPABASE_URL}/rest/v1/memory"
        res = requests.post(url, json=payload, headers=HEADERS, timeout=10)

        if res.status_code in [200, 201]:
            return jsonify({"status": "saved"})
        return jsonify({"error": "Failed to save"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_memory(user_id):
    try:
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        url = f"{SUPABASE_URL}/rest/v1/memory?user_id=eq.{user_id}"
        res = requests.get(url, headers=HEADERS, timeout=10)

        return jsonify({"status": "success", "data": res.json()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
