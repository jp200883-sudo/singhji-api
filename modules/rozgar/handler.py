import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        keyword = params.get("keyword", "").strip().lower()
        
        rozgar_data = {
            "portals": {
                "ncs": {"name": "National Career Service", "site": "ncs.gov.in", "type": "Government"},
                "indeed": {"name": "Indeed India", "site": "indeed.co.in", "type": "Private"},
                "naukri": {"name": "Naukri.com", "site": "naukri.com", "type": "Private"},
                "linkedin": {"name": "LinkedIn Jobs", "site": "linkedin.com/jobs", "type": "Private"},
                "monster": {"name": "Monster India", "site": "monsterindia.com", "type": "Private"},
                "shine": {"name": "Shine.com", "site": "shine.com", "type": "Private"}
            },
            "govt_schemes": {
                "mgnrega": {"name": "MGNREGA", "type": "Rural Jobs", "site": "nrega.nic.in"},
                "pmkvy": {"name": "PM Kaushal Vikas Yojana", "type": "Skill Training", "site": "pmkvyofficial.org"},
                "udyam": {"name": "Udyam Registration", "type": "MSME", "site": "udyamregistration.gov.in"},
                "startup_india": {"name": "Startup India", "type": "Entrepreneurship", "site": "startupindia.gov.in"}
            },
            "categories": [
                "Software", "Government", "Banking", "Teaching", "Medical",
                "Engineering", "Sales", "Marketing", "Data Entry", "Driver",
                "Security", "Cook", "Electrician", "Plumber", "Agriculture"
            ]
        }
        
        if keyword:
            matched = []
            for key, portal in rozgar_data["portals"].items():
                if keyword in portal["name"].lower() or keyword in key:
                    matched.append(portal)
            for key, scheme in rozgar_data["govt_schemes"].items():
                if keyword in scheme["name"].lower() or keyword in key:
                    matched.append(scheme)
            
            if matched:
                return JSONResponse(content={
                    "success": True,
                    "keyword": keyword,
                    "results": matched,
                    "total": len(matched)
                })
        
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - Rozgar/Jobs",
            "portals": rozgar_data["portals"],
            "govt_schemes": rozgar_data["govt_schemes"],
            "categories": rozgar_data["categories"],
            "usage": "/api/rozgar?keyword=software"
        })
        
    except Exception as e:
        logger.error(f"Rozgar error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
