# modules/karmachari.py — Singh Ji AI Ultra v6.0
# सरकारी कर्मचारी — Govt Employee Benefits

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def karmachari_root():
    return {
        "module": "karmachari",
        "status": "✅ Live",
        "for": "Government Employees"
    }

@router.get("/benefits")
def all_benefits():
    """सभी सरकारी लाभ"""
    return {
        "success": True,
        "statutory_benefits": {
            "epf": {"employer": "12%", "employee": "12%", "website": "https://epfindia.gov.in"},
            "esi": {"employer": "3.25%", "employee": "0.75%", "website": "https://www.esic.in"},
            "gratuity": {"eligibility": "1 year (fixed-term), 5 years (permanent)", "formula": "(Last Salary x 15 x Years) / 26"},
            "bonus": {"min": "8.33%", "max": "20%", "act": "Payment of Bonus Act"},
            "maternity": {"leave": "26 weeks", "for": "First 2 children"},
            "nps": {"voluntary": True, "tax_benefit": "10% of basic"}
        },
        "leave": {
            "annual": "15 days",
            "sick": "12 days",
            "casual": "6-7 days",
            "maternity": "26 weeks",
            "paternity": "2-3 weeks (voluntary)"
        }
    }

@router.get("/pension")
def pension_info():
    """पेंशन योजनाएं"""
    return {
        "success": True,
        "schemes": [
            {"name": "EPS-95", "for": "EPF members", "pension_age": "58 years"},
            {"name": "NPS", "for": "Govt employees (2004+)", "voluntary": True},
            {"name": "Old Age Pension", "for": "BPL seniors", "amount": "₹200-1000/month"}
        ]
    }

@router.get("/grievance")
def grievance():
    """शिकायत निवारण"""
    return {
        "success": True,
        "cpgrams": "https://pgportal.gov.in",
        "helpline": "1800-11-2233",
        "steps": [
            "1. Department level complaint",
            "2. Head of Department",
            "3. Chief Vigilance Officer",
            "4. CVC / CBI (if corruption)"
        ]
    }
