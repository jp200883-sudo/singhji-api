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
            keyword = params.get('keyword', '').strip()
            location = params.get('location', '').strip()
            category = params.get('category', '').strip()
        else:
            body = await request.json()
            keyword = body.get('keyword', '').strip()
            location = body.get('location', '').strip()
            category = body.get('category', '').strip()
        
        # Job portals and schemes
        job_data = {
            "portals": [
                {"name": "Naukri.com", "url": "https://www.naukri.com"},
                {"name": "Indeed India", "url": "https://in.indeed.com"},
                {"name": "LinkedIn Jobs", "url": "https://www.linkedin.com/jobs"},
                {"name": "Government Jobs", "url": "https://www.sarkariresult.com"},
                {"name": "Freshersworld", "url": "https://www.freshersworld.com"}
            ],
            "government_schemes": [
                {
                    "name": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
                    "description": "100 days guaranteed wage employment",
                    "website": "https://nrega.nic.in",
                    "helpline": "1800-110-707"
                },
                {
                    "name": "PM SVANidhi",
                    "description": "Street vendor loan scheme",
                    "website": "https://pmsvanidhi.mohua.gov.in",
                    "helpline": "1800-11-2222"
                },
                {
                    "name": "Skill India Mission",
                    "description": "Free skill training programs",
                    "website": "https://www.skillindia.gov.in",
                    "helpline": "1800-102-5100"
                },
                {
                    "name": "National Career Service (NCS)",
                    "description": "Job matching portal",
                    "website": "https://www.ncs.gov.in",
                    "helpline": "1800-425-1514"
                },
                {
                    "name": "Kaushal Bharat",
                    "description": "Skill development for youth",
                    "website": "https://kaushalbharat.gov.in",
                    "helpline": "011-2332-3456"
                }
            ],
            "apprenticeship": [
                {"name": "NAPS", "url": "https://naps.gov.in", "description": "National Apprenticeship Promotion Scheme"},
                {"name": "Bharat Skills", "url": "https://bharatskills.gov.in", "description": "Skill certification"}
            ]
        }
        
        # Filter by keyword if provided
        if keyword:
            keyword_lower = keyword.lower()
            filtered = {
                "portals": [p for p in job_data["portals"] if keyword_lower in p["name"].lower()],
                "government_schemes": [s for s in job_data["government_schemes"] if keyword_lower in s["name"].lower() or keyword_lower in s["description"].lower()],
                "apprenticeship": [a for a in job_data["apprenticeship"] if keyword_lower in a["name"].lower()]
            }
            job_data = filtered
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "search_keyword": keyword or "all",
                "location": location or "India",
                "category": category or "all",
                "results": job_data,
                "total_portals": len(job_data["portals"]),
                "total_schemes": len(job_data["government_schemes"]),
                "total_apprenticeship": len(job_data["apprenticeship"])
            }
        })
        
    except Exception as e:
        logger.error(f"Rozgar crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
