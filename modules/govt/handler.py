import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

GOVT_DATA = {
    "aadhaar": {
        "title": "Aadhaar Card",
        "helpline": "1947",
        "website": "uidai.gov.in",
        "services": ["New Aadhaar", "Update", "Download", "Status Check"],
        "center_finder": "appointments.uidai.gov.in"
    },
    "pan": {
        "title": "PAN Card",
        "helpline": "1800-180-1961",
        "website": "incometaxindia.gov.in",
        "services": ["New PAN", "Correction", "Link with Aadhaar"]
    },
    "passport": {
        "title": "Passport",
        "helpline": "1800-258-1800",
        "website": "passportindia.gov.in",
        "services": ["New Passport", "Renewal", "Tatkal"]
    },
    "voter": {
        "title": "Voter ID",
        "helpline": "1950",
        "website": "nvsp.in",
        "services": ["New Voter ID", "Correction", "Check Status"]
    },
    "ration": {
        "title": "Ration Card",
        "helpline": "1967",
        "website": "nfsa.gov.in",
        "services": ["New Card", "Update", "Check Entitlement"]
    },
    "driving": {
        "title": "Driving License",
        "helpline": "1800-180-2066",
        "website": "parivahan.gov.in",
        "services": ["Learner's License", "Permanent License", "Renewal"]
    },
    "ayushman": {
        "title": "Ayushman Bharat",
        "helpline": "14555",
        "website": "pmjay.gov.in",
        "services": ["Card Download", "Hospital List", "Check Eligibility"]
    },
    "pmkisan": {
        "title": "PM Kisan Samman Nidhi",
        "helpline": "155261",
        "website": "pmkisan.gov.in",
        "services": ["Status Check", "Registration", "Beneficiary List"]
    }
}


async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            service = params.get("service", "").strip().lower()
        else:
            try:
                body = await request.json()
            except Exception:
                body = {}
            service = str(body.get("service", "")).strip().lower()

        if service and service in GOVT_DATA:
            return JSONResponse(content={
                "success": True,
                "service": service,
                "data": GOVT_DATA[service]
            })

        return JSONResponse(content={
            "success": True,
            "message": "Singh Ji AI - Government Services",
            "available_services": list(GOVT_DATA.keys()),
            "usage": "/api/govt?service=aadhaar",
            "all_data": GOVT_DATA
        })

    except Exception as e:
        logger.error(f"Govt error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
