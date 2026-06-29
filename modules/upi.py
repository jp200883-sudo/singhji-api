# core/modules/upi.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/upi", tags=["UPI"])

class UPIRequest(BaseModel):
    upi_id: str
    amount: float = 0
    note: str = ""

@router.get("/wall/qr")
def generate_qr(upi_id: str, amount: float = 0, note: str = ""):
    try:
        import qrcode
        import io
        import base64
        
        upi_url = f"upi://pay?pa={upi_id}&am={amount}&cu=INR&tn={note}"
        qr = qrcode.make(upi_url)
        
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "qr_base64": f"data:image/png;base64,{img_base64}"
        }
    except ImportError:
        return {
            "status": "error",
            "message": "qrcode module not installed. Run: pip install qrcode Pillow"
        }
