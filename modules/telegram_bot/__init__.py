from flask import jsonify, request
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

def handler(path, request_obj):
    method = request_obj.method

    if path == 'health' and method == 'GET':
        return jsonify({
            "status": "ok",
            "module": "telegram_bot",
            "token_set": bool(TELEGRAM_BOT_TOKEN)
        })

    elif path == 'webhook' and method == 'POST':
        return handle_webhook(request_obj)

    elif path == 'send' and method == 'POST':
        return send_message(request_obj)

    else:
        return jsonify({"error": "Telegram endpoint not found"}), 404


def handle_webhook(request_obj):
    try:
        data = request_obj.json
        return jsonify({
            "status": "webhook_received",
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_message(request_obj):
    try:
        data = request_obj.json
        chat_id = data.get('chat_id', '')
        text = data.get('text', '')

        if not TELEGRAM_BOT_TOKEN:
            return jsonify({
                "status": "fallback",
                "message": "Telegram token not set"
            })

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }

        res = requests.post(url, json=payload, timeout=10)

        return jsonify({
            "status": "sent",
            "telegram_response": res.json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
