# modules/emergency.py — Singh Ji AI Ultra
from fastapi import APIRouter

router = APIRouter()

EMERGENCY_NUMBERS = {
    "police": "100",
    "ambulance": "108",
    "fire": "101",
    "women_helpline": "1091",
    "child_helpline": "1098",
    "disaster": "1078",
    "railway": "139",
    "cyber_crime": "1930"
}

@router.get("/numbers")
def emergency_numbers():
    """All emergency numbers"""
    return {
        "status": "ready",
        "country": "India",
        "numbers": EMERGENCY_NUMBERS,
        "message": "🚨 Emergency me dial karo!"
    }

@router.get("/number/{service}")
def get_number(service: str):
    """Specific emergency number"""
    number = EMERGENCY_NUMBERS.get(service.lower())
    if number:
        return {"service": service, "number": number, "dial": f"tel:{number}"}
    return {"error": "Service not found", "available": list(EMERGENCY_NUMBERS.keys())}

@router.post("/alert")
def send_alert(service: str, location: str, message: str = "Emergency!"):
    """Send emergency alert (mock — integrate real SMS later)"""
    number = EMERGENCY_NUMBERS.get(service.lower(), "100")
    return {
        "status": "alert_sent",
        "service": service,
        "number": number,
        "location": location,
        "message": message,
        "note": "Real SMS integration pending — use dial for now"
    }
