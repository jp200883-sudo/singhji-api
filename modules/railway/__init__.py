from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "module": "railway",
        "status": "live",
        "message": "Singh Ji AI Ultra v5.0 🚀",
        "features": ["pnr_status", "train_schedule", "seat_availability"]
    }
