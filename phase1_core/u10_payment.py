"""🦁 U10: Payment — Razorpay/UPI/Card"""
class Payment:
    async def handle(self, action, request):
        return {"module": "U10", "razorpay": True, "upi": "jp200883@sbi", "methods": ["card", "upi", "netbanking"]}
