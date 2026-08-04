# api/payment.py
import os
import time
from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from core.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, AVAILABLE_KEYS

router = APIRouter()

@router.get("/")
async def payment_root():
    return {
        "module": "Payment Gateway",
        "status": "ACTIVE" if AVAILABLE_KEYS["RAZORPAY"] else "ON_HOLD",
        "upi_id": "jp200883@sbi",
    }

@router.post("/create-order")
async def payment_create_order(request: Request):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return {"error": "Razorpay keys missing"}
    data = await request.json()
    amount = data.get("amount", 0)
    currency = data.get("currency", "INR")
    receipt = data.get("receipt", f"order_{int(time.time())}")

    def _create_order_sync():
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.order.create({"amount": amount, "currency": currency, "receipt": receipt, "payment_capture": 1})

    try:
        order = await run_in_threadpool(_create_order_sync)
        return {"status": "success", "order": order}
    except Exception as e:
        return {"error": str(e)}
