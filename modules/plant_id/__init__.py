from flask import jsonify, request
import os
import requests

PLANT_ID_API_KEY = os.environ.get('PLANT_ID_API_KEY', '')

def handler(path, request_obj):
    method = request_obj.method

    if path == 'health' and method == 'GET':
        return jsonify({
            "status": "ok",
            "module": "plant_id",
            "api_key_set": bool(PLANT_ID_API_KEY)
        })

    elif path == 'identify' and method == 'POST':
        return identify_plant(request_obj)

    else:
        return jsonify({"error": "Plant endpoint not found"}), 404


def identify_plant(request_obj):
    try:
        data = request_obj.json
        image_url = data.get('image_url', '')

        if not image_url:
            return jsonify({"error": "Image URL required"}), 400

        if not PLANT_ID_API_KEY:
            return jsonify({
                "status": "fallback",
                "message": "Plant.id API key not set",
                "note": "Add PLANT_ID_API_KEY to Render environment variables"
            })

        headers = {
            "Api-Key": PLANT_ID_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "images": [image_url],
            "modifiers": ["similar_images"],
            "plant_details": ["common_names", "url", "wiki_description", "taxonomy"]
        }

        res = requests.post(
            "https://api.plant.id/v2/identify",
            json=payload,
            headers=headers,
            timeout=15
        )

        result = res.json()

        return jsonify({
            "status": "identified",
            "plant": result.get('suggestions', [{}])[0].get('plant_name', 'Unknown'),
            "details": result.get('suggestions', [{}])[0].get('plant_details', {}),
            "similar_images": result.get('suggestions', [{}])[0].get('similar_images', [])
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "note": "Plant identification failed"
        }), 500
