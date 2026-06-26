from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def mandi_home():
    return {"module": "mandi", "status": "ok"}

@router.get("/rates")
def mandi_rates():
    return {
        "crops": [
            {"name": "गेहूं", "price": "₹2,100/quintal", "market": "Kanpur"},
            {"name": "चावल", "price": "₹3,500/quintal", "market": "Lucknow"},
            {"name": "आलू", "price": "₹1,200/quintal", "market": "Agra"},
            {"name": "प्याज", "price": "₹2,800/quintal", "market": "Nashik"},
            {"name": "सरसों", "price": "₹5,600/quintal", "market": "Jaipur"}
        ],
        "updated": "today",
        "source": "mock"
    }
