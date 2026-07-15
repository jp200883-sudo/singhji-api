# modules/sarkari_yojana/handler.py

from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/check-eligibility")
async def check_eligibility(request: Request):
    data = await request.json()

    age = data.get("age", 0)
    income = data.get("income", 0)
    occupation = data.get("occupation", "")
    land_size = data.get("land_size", 0)

    schemes = []

    if occupation == "farmer" and income < 200000:
        schemes.append({
            "name": "PM-KISAN",
            "amount": 6000,
            "frequency": "yearly",
            "link": "https://pmkisan.gov.in",
            "next_step": "Aadhaar aur bank passbook leke CSC center jao"
        })

    if income < 500000:
        schemes.append({
            "name": "Ayushman Bharat",
            "amount": 500000,
            "frequency": "cover per year",
            "link": "https://pmjay.gov.in",
            "next_step": "Ration card ya Aadhaar leke CSC center jao"
        })

    if occupation == "farmer":
        schemes.append({
            "name": "Kisan Credit Card",
            "amount": 300000,
            "frequency": "loan limit",
            "link": "https://kcc.gov.in",
            "next_step": "Bank branch jao, land documents saath le jao"
        })

    if age >= 60 and income < 300000:
        schemes.append({
            "name": "Old Age Pension (IGNOAPS)",
            "amount": 1000,
            "frequency": "monthly",
            "link": "https://nsap.nic.in",
            "next_step": "Gram panchayat/nagar palika office jao"
        })

    if not schemes:
        return {
            "eligible_count": 0,
            "message": "Filhaal koi scheme match nahi hui, details verify karo"
        }

    return {
        "eligible_count": len(schemes),
        "schemes": schemes
    }

