# modules/govt.py — Singh Ji AI Ultra v5.0
# Govt Schemes, Yojana, PAN, Aadhaar, Voter ID info

from fastapi import APIRouter
import os
import requests

router = APIRouter()

GOVT_API_KEY = os.getenv("GOVT_API_KEY", "")

@router.get("/")
def govt_root():
    return {"module": "govt", "status": "✅ Live", "services": ["schemes", "pan", "aadhaar", "voter"]}

@router.get("/schemes")
def get_govt_schemes(category: str = "all"):
    """India Govt Schemes — PM Yojana, State Schemes"""
    
    schemes_db = {
        "pm_kisan": {
            "name": "PM Kisan Samman Nidhi",
            "amount": "₹6,000/year",
            "eligibility": "Small & marginal farmers",
            "website": "https://pmkisan.gov.in",
            "toll_free": "155261"
        },
        "ayushman": {
            "name": "Ayushman Bharat Yojana",
            "amount": "₹5 lakh health cover",
            "eligibility": "BPL families",
            "website": "https://pmjay.gov.in",
            "toll_free": "14555"
        },
        "ujjwala": {
            "name": "PM Ujjwala Yojana",
            "amount": "Free LPG connection",
            "eligibility": "BPL women",
            "website": "https://pmuy.gov.in",
            "toll_free": "1906"
        },
        "awas": {
            "name": "PM Awas Yojana",
            "amount": "₹2.67 lakh subsidy",
            "eligibility": "EWS/LIG/MIG",
            "website": "https://pmaymis.gov.in",
            "toll_free": "1800-11-6163"
        },
        "mudra": {
            "name": "MUDRA Loan",
            "amount": "Up to ₹10 lakh",
            "eligibility": "Small business/startup",
            "website": "https://mudra.org.in",
            "toll_free": "1800-180-2230"
        },
        "skill_india": {
            "name": "Skill India Mission",
            "amount": "Free training + stipend",
            "eligibility": "Youth 18-35 years",
            "website": "https://skillindia.gov.in",
            "toll_free": "1800-123-9626"
        }
    }
    
    if category == "all":
        return {"success": True, "total": len(schemes_db), "schemes": schemes_db}
    
    if category in schemes_db:
        return {"success": True, "scheme": schemes_db[category]}
    
    return {"success": False, "error": "Scheme not found", "available": list(schemes_db.keys())}

@router.get("/pan/verify")
def verify_pan(pan_number: str):
    """PAN Card verification format check"""
    import re
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    if re.match(pan_pattern, pan_number.upper()):
        return {
            "success": True,
            "valid": True,
            "pan": pan_number.upper(),
            "message": "PAN format is valid"
        }
    return {
        "success": False,
        "valid": False,
        "message": "Invalid PAN format. Format: ABCDE1234F"
    }

@router.get("/aadhaar/verify")
def verify_aadhaar(aadhaar_number: str):
    """Aadhaar number format check"""
    import re
    aadhaar_pattern = r'^\d{12}$'
    
    cleaned = aadhaar_number.replace(" ", "").replace("-", "")
    
    if re.match(aadhaar_pattern, cleaned):
        return {
            "success": True,
            "valid": True,
            "aadhaar": "XXXX-XXXX-" + cleaned[-4:],
            "message": "Aadhaar format is valid"
        }
    return {
        "success": False,
        "valid": False,
        "message": "Invalid Aadhaar. Must be 12 digits"
    }

@router.get("/voter/search")
def search_voter(name: str = None, epic: str = None):
    """Voter ID search info"""
    return {
        "success": True,
        "message": "Voter search",
        "portal": "https://electoralsearch.in",
        "nvsp": "https://nvsp.in",
        "toll_free": "1950",
        "search_by": {"name": name, "epic": epic}
    }

@router.get("/passport/status")
def passport_status(file_number: str):
    """Passport application status check link"""
    return {
        "success": True,
        "portal": "https://passportindia.gov.in",
        "track_url": f"https://passportindia.gov.in/AppOnlineProject/statusTracker/trackStatusInpNew",
        "file_number": file_number,
        "toll_free": "1800-258-1800"
    }

@router.get("/ration/search")
def ration_search(state: str):
    """Ration card search by state"""
    state_portals = {
        "up": "https://fcs.up.gov.in",
        "bihar": "https://epds.bihar.gov.in",
        "mp": "https:// ration.mp.gov.in",
        "rajasthan": "https://food.rajasthan.gov.in",
        "maharashtra": "https://mahafood.gov.in",
        "gujarat": "https://dfpd.gujarat.gov.in",
        "delhi": "https://food.delhigovt.nic.in"
    }
    
    return {
        "success": True,
        "state": state,
        "portal": state_portals.get(state.lower(), "https://nfsa.gov.in"),
        "national_portal": "https://nfsa.gov.in",
        "toll_free": "1967"
    }
