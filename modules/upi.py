# modules/upi.py — Singh Ji AI Ultra v5.0
# SINGH JI UPI WALL — Apna UPI, Apna Control!

from fastapi import APIRouter
import os
import qrcode
import io
import base64
import uuid
from datetime import datetime
import pytz

router = APIRouter()
IST = pytz.timezone('Asia/Kolkata')

# 🔥 SINGH JI PRIMARY UPI
SINGHJI_UPI = os.getenv("UPI_ID", "jp200883@sbi")
SINGHJI_NAME = os.getenv("MERCHANT_NAME", "Singh Ji AI")

# Optional wallets (user choice)
OPTIONAL_WALLETS = {
    "paytm": {"name": "Paytm", "enabled": False},
    "phonepe": {"name": "PhonePe", "enabled": False},
    "gpay": {"name": "Google Pay", "enabled": False},
    "amazonpay": {"name": "Amazon Pay", "enabled": False}
}

USER_WALLETS = {}
TRANSACTIONS = []

@router.get("/")
def upi_wall():
    """🏛️ Singh Ji UPI Wall — Entry Point"""
    return {
        "module": "Singh Ji UPI Wall",
        "version": "5.0",
        "status": "✅ Live",
        "primary_upi": SINGHJI_UPI,
        "merchant": SINGHJI_NAME,
        "philosophy": "Apna UPI, Apna Control!",
        "features": {
            "primary": ["QR Scan", "UPI ID Direct", "Singh Ji Pay"],
            "optional": ["Paytm", "PhonePe", "GPay", "Amazon Pay"]
        }
    }

# ========== 🏛️ PRIMARY: SINGH JI UPI WALL ==========

@router.get("/wall/qr")
def wall_qr(amount: float = None, note: str = "Singh Ji AI"):
    """🎯 PRIMARY: Singh Ji QR Code — Sabse pehle yahi scan karo!"""
    
    upi_uri = f"upi://pay?pa={SINGHJI_UPI}&pn={SINGHJI_NAME}&tn={note}"
    if amount:
        upi_uri += f"&am={amount}"
    upi_uri += "&cu=INR"
    
    # Premium QR Design
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)
    
    # Singh Ji branded QR
    img = qr.make_image(fill_color="#FF6B00", back_color="#FFF8E7")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "success": True,
        "type": "PRIMARY",
        "method": "Singh Ji QR Wall",
        "upi_id": SINGHJI_UPI,
        "merchant": SINGHJI_NAME,
        "amount": amount,
        "note": note,
        "qr_code": f"data:image/png;base64,{img_str}",
        "scan_instruction": "Kisi bhi UPI app se scan karo — PhonePe, GPay, Paytm, BHIM sab chalenge!",
        "priority": 1
    }

@router.get("/wall/direct")
def wall_direct(amount: float, note: str = "Singh Ji Payment"):
    """🎯 PRIMARY: Direct UPI ID se pay — No app needed!"""
    
    txn_id = f"SJ{uuid.uuid4().hex[:10].upper()}"
    
    return {
        "success": True,
        "type": "PRIMARY",
        "method": "Direct UPI",
        "upi_id": SINGHJI_UPI,
        "merchant": SINGHJI_NAME,
        "amount": amount,
        "note": note,
        "txn_id": txn_id,
        "steps": [
            "1. Apne UPI app kholen",
            f"2. '{SINGHJI_UPI}' pe pay karein",
            f"3. Amount: ₹{amount}",
            f"4. Note: {note}",
            "5. Done! 🎉"
        ],
        "priority": 1
    }

@router.get("/wall/singhji-pay")
def singhji_pay(amount: float, user_upi: str, note: str = ""):
    """🦁 SINGH JI PAY — Apna payment system!"""
    
    txn_id = f"SJ{uuid.uuid4().hex[:12].upper()}"
    
    return {
        "success": True,
        "type": "PRIMARY",
        "method": "Singh Ji Pay",
        "txn_id": txn_id,
        "from": user_upi,
        "to": SINGHJI_UPI,
        "amount": amount,
        "note": note or "Singh Ji AI Payment",
        "status": "initiated",
        "message": "Payment initiated via Singh Ji Pay",
        "verify_url": f"/api/upi/verify?txn={txn_id}",
        "priority": 1
    }

# ========== ⚪ OPTIONAL: Third-Party Wallets ==========

@router.post("/optional/enable")
def enable_optional_wallet(wallet_type: str):
    """⚪ OPTIONAL: User chahe toh enable kare — Force nahi!"""
    
    wallet_type = wallet_type.lower()
    
    if wallet_type not in OPTIONAL_WALLETS:
        return {
            "success": False,
            "message": "Wallet type not supported",
            "available": list(OPTIONAL_WALLETS.keys())
        }
    
    OPTIONAL_WALLETS[wallet_type]["enabled"] = True
    
    return {
        "success": True,
        "message": f"{OPTIONAL_WALLETS[wallet_type]['name']} enabled",
        "type": "OPTIONAL",
        "warning": "Yeh optional hai — Singh Ji UPI Wall primary hai!",
        "priority": 2
    }

@router.get("/optional/pay")
def optional_pay(wallet_type: str, amount: float, note: str = ""):
    """⚪ OPTIONAL: Third-party app se pay — Agar user chahe!"""
    
    wallet_type = wallet_type.lower()
    
    if not OPTIONAL_WALLETS.get(wallet_type, {}).get("enabled"):
        return {
            "success": False,
            "message": f"{wallet_type} enabled nahi hai!",
            "instruction": f"Pehle /optional/enable?wallet_type={wallet_type} call karo",
            "primary_alternative": f"/wall/qr?amount={amount}"
        }
    
    upi_uri = f"upi://pay?pa={SINGHJI_UPI}&pn={SINGHJI_NAME}&am={amount}&cu=INR&tn={note}"
    
    intents = {
        "paytm": f"paytmmp://upi/pay?pa={SINGHJI_UPI}&am={amount}&cu=INR",
        "phonepe": f"phonepe://pay?pa={SINGHJI_UPI}&am={amount}&cu=INR",
        "gpay": f"tez://upi/pay?pa={SINGHJI_UPI}&am={amount}&cu=INR",
        "amazonpay": f"amazonpay://upi/pay?pa={SINGHJI_UPI}&am={amount}&cu=INR"
    }
    
    return {
        "success": True,
        "type": "OPTIONAL",
        "method": wallet_type,
        "amount": amount,
        "intent_url": intents.get(wallet_type),
        "warning": "Yeh optional method hai",
        "primary_recommended": f"/wall/qr?amount={amount}",
        "priority": 2
    }

# ========== 👤 USER WALLETS (Apna UPI Wall) ==========

@router.post("/user/wallet/add")
def add_user_upi(user_id: str, upi_id: str, name: str = ""):
    """User apna UPI Wall banaye — Apna UPI, Apna Control!"""
    
    if "@" not in upi_id:
        return {"success": False, "error": "Invalid UPI ID"}
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = {
            "primary": None,
            "wallets": []
        }
    
    wallet = {
        "id": f"UW{uuid.uuid4().hex[:6].upper()}",
        "upi_id": upi_id,
        "name": name or "My UPI",
        "added_at": datetime.now(IST).isoformat(),
        "type": "user_primary"
    }
    
    USER_WALLETS[user_id]["primary"] = wallet
    USER_WALLETS[user_id]["wallets"].append(wallet)
    
    return {
        "success": True,
        "message": "Apna UPI Wall ban gaya! 🎉",
        "wallet": wallet,
        "tip": "Ab aap bhi payment receive kar sakte hain!"
    }

@router.get("/user/wallet")
def get_user_wall(user_id: str):
    """User ka apna UPI Wall dekho"""
    
    wall = USER_WALLETS.get(user_id, {"primary": None, "wallets": []})
    
    return {
        "success": True,
        "user_id": user_id,
        "my_upi_wall": wall,
        "can_receive": wall["primary"] is not None,
        "can_pay": True,
        "message": "Apna UPI Wall — Apna Control!" if wall["primary"] else "UPI Wall setup karo!"
    }

# ========== 📊 TRANSACTIONS ==========

@router.post("/txn/record")
def record_txn(user_id: str, amount: float, status: str = "success"):
    """Transaction record"""
    txn = {
        "id": f"SJ{uuid.uuid4().hex[:10].upper()}",
        "user_id": user_id,
        "amount": amount,
        "status": status,
        "timestamp": datetime.now(IST).isoformat()
    }
    TRANSACTIONS.append(txn)
    return {"success": True, "txn": txn}

@router.get("/txn/history")
def txn_history(user_id: str):
    """User ki history"""
    txns = [t for t in TRANSACTIONS if t["user_id"] == user_id]
    return {
        "success": True,
        "total": len(txns),
        "txns": txns
    }

# ========== ✅ VERIFY ==========

@router.get("/verify")
def verify_vpa(vpa: str):
    """UPI ID check"""
    if "@" not in vpa:
        return {"success": False, "valid": False}
    
    return {
        "success": True,
        "vpa": vpa,
        "valid": True,
        "message": "Valid UPI ID"
    }
