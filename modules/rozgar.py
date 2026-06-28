# modules/rozgar.py — Singh Ji AI Ultra v6.0
# रोजगार — Jobs, Govt Jobs, NCS Portal

from fastapi import APIRouter
import requests
from datetime import datetime

router = APIRouter()

@router.get("/")
def rozgar_root():
    return {
        "module": "rozgar",
        "status": "✅ Live",
        "portals": ["NCS", "UPSC", "SSC", "State PSC", "Railway", "Banking"]
    }

@router.get("/govt-jobs")
def govt_jobs(category: str = "all"):
    """सरकारी नौकरियां — NCS Portal"""
    jobs = {
        "upsc": {"name": "UPSC Civil Services", "last_date": "2026-03-01", "vacancy": 1200},
        "ssc": {"name": "SSC CGL", "last_date": "2026-02-15", "vacancy": 7500},
        "railway": {"name": "RRB NTPC", "last_date": "2026-04-10", "vacancy": 35000},
        "banking": {"name": "IBPS PO", "last_date": "2026-03-20", "vacancy": 4500},
        "state": {"name": "UPPSC", "last_date": "2026-02-28", "vacancy": 500}
    }

    if category == "all":
        return {"success": True, "total": len(jobs), "jobs": jobs}

    if category in jobs:
        return {"success": True, "job": jobs[category]}

    return {"success": False, "error": "Category not found"}

@router.get("/ncs/search")
def ncs_search(keyword: str, location: str = ""):
    """NCS Portal search"""
    return {
        "success": True,
        "portal": "https://www.ncs.gov.in",
        "keyword": keyword,
        "location": location,
        "message": "NCS portal pe search karo",
        "helpline": "1800-102-0109"
    }

@router.get("/contract-jobs")
def contract_jobs():
    """संविदा नौकरियां — Contract Worker Benefits"""
    return {
        "success": True,
        "type": "Contract/Sanvida",
        "benefits_2026": [
            "Gratuity after 1 year (2025 reform)",
            "EPF if 20+ employees",
            "ESI if 10+ employees",
            "Equal pay for equal work",
            "Social security (new labour codes)"
        ],
        "portals": {
            "shramsuvidha": "https://shramsuvidha.gov.in",
            "epfo": "https://epfindia.gov.in",
            "esi": "https://www.esic.in"
        }
    }

@router.get("/skill-development")
def skill_dev():
    """Skill India — Kaushal Vikas"""
    return {
        "success": True,
        "schemes": [
            {"name": "PMKVY", "website": "https://pmkvyofficial.org", "toll_free": "1800-123-9626"},
            {"name": "NAPS", "website": "https://naps.gov.in", "toll_free": "011-23363733"},
            {"name": "DDU-GKY", "website": "https://ddugky.gov.in", "toll_free": "1800-274-0600"}
        ]
    }
