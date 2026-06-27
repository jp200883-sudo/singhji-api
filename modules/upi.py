from fastapi import APIRouter

router = APIRouter()

@router.get("/verify/{upi_id}")
async def verify_upi(upi_id: str):
    return {"upi_id": upi_id, "verified": True, "bank": "SBI"}

@router.get("/")
async def upi_root():
    return {"status": "upi module active"}
