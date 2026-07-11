
"""🦁 Mini-Program Payment — 0% UPI, 2% Card"""
import uuid
from datetime import datetime

class MiniPayment:
    UPI_ID = "jp200883@sbi"
    RATES = {"upi": 0.0, "card": 0.02, "wallet": 0.01}
    TRANSACTIONS = {}
    BALANCES = {}
    
    @classmethod
    def process(cls, amount, from_user, to_merchant, method="upi", metadata=None):
        if method not in cls.RATES:
            return {"error": "Invalid method"}
        commission = amount * cls.RATES[method]
        merchant_amount = amount - commission
        txn_id = f"TXN_{uuid.uuid4().hex[:16].upper()}"
        cls.TRANSACTIONS[txn_id] = {
            "id": txn_id, "amount": amount, "method": method,
            "commission": commission, "merchant_amount": merchant_amount,
            "from_user": from_user, "to_merchant": to_merchant,
            "status": "completed", "upi_id": cls.UPI_ID,
            "timestamp": datetime.now().isoformat(), "metadata": metadata or {}
        }
        cls.BALANCES[to_merchant] = cls.BALANCES.get(to_merchant, 0) + merchant_amount
        return {"status": "success", "transaction_id": txn_id, "amount": amount,
                "method": method, "commission": commission, "merchant_amount": merchant_amount}
    
    @classmethod
    def get_balance(cls, merchant_id):
        return {"merchant_id": merchant_id, "balance": cls.BALANCES.get(merchant_id, 0), "currency": "INR"}
EOF
