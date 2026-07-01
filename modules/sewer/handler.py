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
        
        # Sewer/Sanitation info
        sewer_data = {
            "helplines": {
                "swachh_bharat": "1800-180-1818",
                "urban_sewer": "1800-111-555",
                "complaint": "1969"
            },
            "schemes": [
                {
                    "name": "Swachh Bharat Mission (Urban)",
                    "target": "Open defecation free cities",
                    "website": "https://swachhbharaturban.gov.in",
                    "progress": "4500+ cities declared ODF"
                },
                {
                    "name": "AMRUT 2.0",
                    "target": "Sewerage in 500 cities",
                    "website": "https://amrut.gov.in",
                    "progress": "In progress"
                },
                {
                    "name": "SBM 2.0",
                    "target": "Garbage free cities",
                    "website": "https://swachhbharaturban.gov.in",
                    "progress": "Ongoing"
                }
            ],
            "complaint_types": [
                "Sewer blockage",
                "Sewer overflow",
                "Manhole cover missing",
                "Bad smell",
                "Sewer line damage"
            ],
            "tips": [
                "Do not throw solid waste in sewer",
                "Report open manholes immediately",
                "Keep sewer covers closed",
                "Do not connect rainwater to sewer",
                "Regular maintenance prevents blockages"
            ]
        }
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "state": state or "All India",
                "city": city or "All",
                "sewer_info": sewer_data
            }
        })
        
    except Exception as e:
        logger.error(f"Sewer crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
