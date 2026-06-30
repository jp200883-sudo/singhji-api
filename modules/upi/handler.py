from fastapi import Request
import os
from datetime import datetime

UPI = os.getenv("UPI_ID", "jp200883@sbi")

async def handler(request: Request):
    method = request.method
    if method in ["GET", "HEAD"]:
        return {"status": "ok", "module": "upi", "upi_id": UPI}
    if method == "POST":
        try:
            b = await request.json()
            action = b.get("action", "generate")
            if action == "generate":
                amt = b.get("amount", 100)
                note = b.get("note", "Singh Ji Payment")
                url = f"upi://pay?pa={UPI}&pn=SinghJiAI&am={amt}&tn={note}"
                return {"status": "success", "upi_id": UPI, "amount": amt, "upi_url": url, "qr": url, "message": f"🦁 Pay ₹{amt} to {UPI}", "timestamp": datetime.now().isoformat()}
            elif action == "verify": return {"status": "success", "verified": True}
            return {"status": "error", "message": "Unknown action"}
        except Exception as e: return {"status": "error", "error": str(e)}
    return {"status": "error", "message": "Method not allowed"}
