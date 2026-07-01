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
            service = params.get('service', '').strip().lower()
            state = params.get('state', '').strip()
        else:
            body = await request.json()
            service = body.get('service', '').strip().lower()
            state = body.get('state', '').strip()
        
        # Government services database
        govt_services = {
            "aadhaar": {
                "name": "Aadhaar Card",
                "website": "https://uidai.gov.in",
                "helpline": "1947",
                "status_check": "https://resident.uidai.gov.in/verify"
            },
            "pan": {
                "name": "PAN Card",
                "website": "https://www.incometax.gov.in",
                "helpline": "1800-180-1961",
                "status_check": "https://www.incometax.gov.in/iec/foportal/"
            },
            "passport": {
                "name": "Passport",
                "website": "https://www.passportindia.gov.in",
                "helpline": "1800-258-1800",
                "status_check": "https://www.passportindia.gov.in/AppOnlineProject/statusTracker"
            },
            "driving_license": {
                "name": "Driving License",
                "website": "https://parivahan.gov.in",
                "helpline": "1800-180-1849",
                "status_check": "https://parivahan.gov.in/rcdlstatus/"
            },
            "voter_id": {
                "name": "Voter ID",
                "website": "https://www.nvsp.in",
                "helpline": "1950",
                "status_check": "https://www.nvsp.in/Forms/TrackStatus"
            },
            "ration_card": {
                "name": "Ration Card",
                "website": "https://nfsa.gov.in",
                "helpline": "1967",
                "status_check": "https://nfsa.gov.in/State-wise-PDS-Portal"
            },
            "ayushman": {
                "name": "Ayushman Bharat",
                "website": "https://pmjay.gov.in",
                "helpline": "14555",
                "status_check": "https://pmjay.gov.in/beneficiary-search"
            },
            "ujjwala": {
                "name": "PM Ujjwala Yojana",
                "website": "https://pmuy.gov.in",
                "helpline": "1906",
                "status_check": "https://pmuy.gov.in/ujjwala2/"
            },
            "kisan": {
                "name": "PM Kisan Samman Nidhi",
                "website": "https://pmkisan.gov.in",
                "helpline": "155261",
                "status_check": "https://pmkisan.gov.in/BeneficiaryStatus.aspx"
            },
            "mudra": {
                "name": "MUDRA Loan",
                "website": "https://www.mudra.org.in",
                "helpline": "1800-180-1111",
                "status_check": "https://www.mudra.org.in/"
            }
        }
        
        if service and service in govt_services:
            result = govt_services[service]
            result["service_name"] = service
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": result
            })
        
        # Return all services if no specific service requested
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "total_services": len(govt_services),
                "services": list(govt_services.keys()),
                "message": "Available government services"
            }
        })
        
    except Exception as e:
        logger.error(f"Govt crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
