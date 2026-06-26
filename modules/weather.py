from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def weather_home():
    return {"module": "weather", "status": "ok"}

@router.get("/{city}")
def weather_city(city: str):
    return {"city": city, "temp": "25°C", "condition": "Sunny", "source": "mock"}
