import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

UPI_ID = os.environ.get('UPI_ID', 'jp200883@sbi')

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'info').strip()
        else:
            body = await request.json()
            action = body.get('action', 'info').strip()
        
        if action == 'info':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "upi_id": UPI_ID,
                    "apps": ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay", "Cred"],
                    "daily_limit": "₹1,00,000",
                    "per_transaction_limit": "₹1,00,000",
                    "note": "Payment gateway on hold until 1000+ daily users"
                }
            })
        
        elif action == 'qr':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "upi_id": UPI_ID,
                    "qr_text": f"upi://pay?pa={UPI_ID}&pn=SinghJiAI",
                    "message": "Scan this UPI QR code to pay",
                    "note": "Full QR generation coming soon"
                }
            })
        
        elif action == 'verify':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "UPI verification coming soon",
                    "status": "Pending Razorpay activation",
                    "current_phase": "FREE — all features free"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["info", "qr", "verify"],
                "message": "Use ?action=info or ?action=qr"
            }
        })
        
    except Exception as e:
        logger.error(f"UPI crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
