from flask import jsonify, request
import os
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def handler(path, request_obj):
    method = request_obj.method
    
    if path == 'webhook' and method == 'POST':
        data = request_obj.json
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        reply = f"🦁 Singh Ji AI: Aapne likha - {text}\n\nMain abhi sirf basic hu, jald full power aaunga!"
        send_message(chat_id, reply)
        
        return jsonify({"status": "ok"})
    
    elif path == 'send' and method == 'POST':
        data = request_obj.json
        chat_id = data.get('chat_id')
        text = data.get('text')
        return send_message(chat_id, text)
    
    elif path == 'set-webhook' and method == 'POST':
        data = request_obj.json
        url = data.get('url')
        return set_webhook(url)
    
    elif path == 'info' and method == 'GET':
        return get_bot_info()
    
    else:
        return jsonify({"error": "Telegram endpoint not found"}), 404


def send_message(chat_id, text):
    try:
        url = f"{API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        res = requests.post(url, json=payload, timeout=10)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def set_webhook(url):
    try:
        webhook_url = f"{API_URL}/setWebhook"
        payload = {"url": url}
        res = requests.post(webhook_url, json=payload, timeout=10)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_bot_info():
    try:
        url = f"{API_URL}/getMe"
        res = requests.get(url, timeout=10)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
