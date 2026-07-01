import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            state = params.get('state', '').strip()
            city = params.get('city', '').strip()
        else:
            body = await request.json()
            state = body.get('state', '').strip()
            city = body.get('city', '').strip()
        
        # Water supply info
        water_data = {
            "helplines": {
                "national": "1800-180-1818",
                "jal_jeevan": "1800-111-555",
                "cpheeo": "011-2306-1532"
            },
            "schemes": [
                {
                    "name": "Jal Jeevan Mission",
                    "target": "Har Ghar Jal by 2024",
                    "website": "https://jaljeevanmission.gov.in",
                    "progress": "12+ crore connections"
                },
                {
                    "name": "AMRUT 2.0",
                    "target": "Water supply in 500 cities",
                    "website": "https://amrut.gov.in",
                    "progress": "In progress"
                },
                {
                    "name": "Swajal Scheme",
                    "target": "Clean water in rural areas",
                    "website": "https://jaljeevanmission.gov.in",
                    "progress": "Ongoing"
                }
            ],
            "tips": [
                "Report water leakage immediately",
                "Check water quality monthly",
                "Install rainwater harvesting",
                "Use water meter to track usage",
                "Report illegal borewells"
            ],
            "complaint_portals": [
                {"name": "Jal Jeevan Portal", "url": "https://jaljeevanmission.gov.in"},
                {"name": "State Water Board", "url": "Contact local office"},
                {"name": "Municipal Corporation", "url": "Local MC office"}
            ]
        }
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "state": state or "All India",
                "city": city or "All",
                "water_info": water_data
            }
        })
        
    except Exception as e:
        logger.error(f"Pani crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
