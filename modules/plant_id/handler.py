from flask import jsonify, request
import os
import requests

PLANT_ID_API_KEY = os.environ.get('PLANT_ID_API_KEY', '')
PLANT_ID_URL = "https://api.plant.id/v2/identify"

def handler(path, request_obj):
    method = request_obj.method
    
    if path == 'identify' and method == 'POST':
        data = request_obj.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({"error": "Image required"}), 400
        
        return identify_plant(image_base64)
    
    elif path == 'health' and method == 'POST':
        data = request_obj.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({"error": "Image required"}), 400
        
        return health_assessment(image_base64)
    
    else:
        return jsonify({"error": "Plant ID endpoint not found"}), 404


def identify_plant(image_base64):
    try:
        headers = {
            "Content-Type": "application/json",
            "Api-Key": PLANT_ID_API_KEY
        }
        
        payload = {
            "images": [image_base64],
            "modifiers": ["similar_images"],
            "plant_details": ["common_names", "url", "wiki_description", "taxonomy"]
        }
        
        res = requests.post(PLANT_ID_URL, json=payload, headers=headers, timeout=30)
        data = res.json()
        
        suggestions = data.get('suggestions', [])
        if suggestions:
            best = suggestions[0]
            return jsonify({
                "status": "success",
                "plant_name": best.get('plant_name', 'Unknown'),
                "probability": best.get('probability', 0),
                "common_names": best.get('plant_details', {}).get('common_names', []),
                "description": best.get('plant_details', {}).get('wiki_description', {}).get('value', 'No description'),
                "image_url": best.get('similar_images', [{}])[0].get('url', '')
            })
        
        return jsonify({"status": "no_match", "message": "Plant not identified"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def health_assessment(image_base64):
    try:
        headers = {
            "Content-Type": "application/json",
            "Api-Key": PLANT_ID_API_KEY
        }
        
        payload = {
            "images": [image_base64],
            "modifiers": ["similar_images"],
            "health_assessment": 1
        }
        
        res = requests.post(PLANT_ID_URL, json=payload, headers=headers, timeout=30)
        return jsonify(res.json())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
