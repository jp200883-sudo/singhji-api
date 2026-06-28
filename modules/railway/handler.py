from fastapi import APIRouter

router = APIRouter()

DUMMY_TRAINS = [
    {"train_no": "12301", "name": "Rajdhani Express", "from": "NDLS", "to": "HWH", "departure": "16:55", "arrival": "10:00", "status": "On Time"},
    {"train_no": "12002", "name": "Shatabdi Express", "from": "NDLS", "to": "BPL", "departure": "06:00", "arrival": "14:05", "status": "On Time"},
    {"train_no": "12951", "name": "Mumbai Rajdhani", "from": "MMCT", "to": "NDLS", "departure": "17:00", "arrival": "08:35", "status": "Delayed 15 min"},
    {"train_no": "12259", "name": "Duronto Express", "from": "SDAH", "to": "BKN", "departure": "12:30", "arrival": "10:15", "status": "On Time"},
    {"train_no": "22413", "name": "Garib Rath", "from": "NZM", "to": "KCVL", "departure": "10:00", "arrival": "18:00", "status": "On Time"},
]

@router.get("/status")
def railway_status():
    return {
        "status": "live",
        "module": "railway",
        "message": "Singh Ji AI Ultra v5.0 🚂",
        "trains": DUMMY_TRAINS,
        "services": ["pnr_status", "train_schedule", "seat_availability", "fare_enquiry"]
    }

@router.get("/pnr/{pnr_no}")
def pnr_status(pnr_no: str):
    return {
        "pnr": pnr_no,
        "status": "Confirmed",
        "train": "Rajdhani Express (12301)",
        "passengers": [{"name": "Passenger 1", "status": "CNF", "berth": "B1-12"}],
        "chart_prepared": False
    }

def get_railway_data():
    return {
        "status": "live",
        "content": "Railway data loaded!",
        "trains": DUMMY_TRAINS,
        "services": ["pnr", "schedule", "availability", "fare"]
    }
