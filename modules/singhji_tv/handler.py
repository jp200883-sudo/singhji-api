import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            category = params.get('category', '').strip()
        else:
            body = await request.json()
            category = body.get('category', '').strip()
        
        # Content database
        content = {
            "educational": [
                {"title": "Digital India Explained", "duration": "10 min", "topic": "Technology"},
                {"title": "PM Kisan Process", "duration": "5 min", "topic": "Agriculture"},
                {"title": "UPI Safety Tips", "duration": "3 min", "topic": "Banking"},
                {"title": "Aadhaar Update Guide", "duration": "7 min", "topic": "Government"}
            ],
            "news": [
                {"title": "Daily Headlines", "duration": "15 min", "source": "Multiple"},
                {"title": "Mandi Rates Update", "duration": "5 min", "source": "Agri Dept"},
                {"title": "Weather Forecast", "duration": "3 min", "source": "IMD"}
            ],
            "entertainment": [
                {"title": "Folk Music Collection", "duration": "30 min", "region": "All India"},
                {"title": "Regional Movies", "duration": "120 min", "region": "Multiple"}
            ],
            "health": [
                {"title": "Yoga for Beginners", "duration": "20 min", "instructor": "Certified"},
                {"title": "Healthy Cooking", "duration": "15 min", "type": "Vegetarian"},
                {"title": "First Aid Basics", "duration": "10 min", "type": "Emergency"}
            ]
        }
        
        if category and category in content:
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "category": category,
                    "videos": content[category]
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "categories": list(content.keys()),
                "all_content": content
            }
        })
        
    except Exception as e:
        logger.error(f"SinghJi TV crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
