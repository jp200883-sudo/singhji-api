from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {"module": "currency", "status": "live", "message": "Singh Ji AI Ultra v5.0 🚀"}
