"""
💰 Payment Integration — Razorpay ready hai!
"""
import razorpay
import hmac
import hashlib
from typing import Optional, Dict, Any

from .config import MiniProgramConfig


class PaymentManager:
    """Razorpay Payment Manager"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Razorpay se connect karo"""
        if not MiniProgramConfig.is_payment_ready():
            print("⚠️ Razorpay config missing — payments disabled")
            return
        
        try:
            self.client = razorpay.Client(
                auth=(MiniProgramConfig.RAZORPAY_KEY_ID, MiniProgramConfig.RAZORPAY_KEY_SECRET)
            )
            print("✅ Razorpay connected!")
        except Exception as e:
            print(f"❌ Razorpay connection failed: {e}")
    
    def is_connected(self) -> bool:
        return self.client is not None
    
    def create_order(self, amount: float, currency: str = "INR", 
                     receipt: str = None, notes: Dict[str, Any] = None) -> Optional[Dict]:
        """Naya order banayo"""
        if not self.is_connected():
            return None
        
        try:
            order_data = {
                "amount": int(amount * 100),  # Paise mein convert karo
                "currency": currency,
                "receipt": receipt or f"singhji_{int(__import__('time').time())}",
                "notes": notes or {}
            }
            order = self.client.order.create(data=order_data)
            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "status": order["status"],
                "receipt": order["receipt"]
            }
        except Exception as e:
            print(f"Order create error: {e}")
            return None
    
    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Payment signature verify karo"""
        if not self.is_connected():
            return False
        
        try:
            params = f"{order_id}|{payment_id}"
            expected_signature = hmac.new(
                MiniProgramConfig.RAZORPAY_KEY_SECRET.encode(),
                params.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            print(f"Verify error: {e}")
            return False
    
    def verify_webhook(self, body: str, signature: str) -> bool:
        """Webhook signature verify karo"""
        if not MiniProgramConfig.RAZORPAY_WEBHOOK_SECRET:
            return False
        
        try:
            expected = hmac.new(
                MiniProgramConfig.RAZORPAY_WEBHOOK_SECRET.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            print(f"Webhook verify error: {e}")
            return False
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """Payment details nikalo"""
        if not self.is_connected():
            return None
        
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            print(f"Fetch error: {e}")
            return None
    
    def refund_payment(self, payment_id: str, amount: float = None) -> Optional[Dict]:
        """Payment refund karo"""
        if not self.is_connected():
            return None
        
        try:
            refund_data = {}
            if amount:
                refund_data["amount"] = int(amount * 100)
            return self.client.payment.refund(payment_id, refund_data)
        except Exception as e:
            print(f"Refund error: {e}")
            return None
    
    def create_subscription(self, plan_id: str, customer_id: str = None,
                            total_count: int = 12, notes: Dict = None) -> Optional[Dict]:
        """Subscription banayo"""
        if not self.is_connected():
            return None
        
        try:
            sub_data = {
                "plan_id": plan_id,
                "total_count": total_count,
                "notes": notes or {}
            }
            if customer_id:
                sub_data["customer_id"] = customer_id
            return self.client.subscription.create(data=sub_data)
        except Exception as e:
            print(f"Subscription error: {e}")
            return None


# Global instance
payment = PaymentManager()
