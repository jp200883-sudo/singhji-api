"""
🏦 Singh Ji AI Ultra — Banking Hub Handler
Phase 4: UPI, Bank Accounts, Loans, Insurance, Investments, Bill Pay, Credit Score, EMI Calculator
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import random
import hashlib
import time

router = APIRouter(prefix="/banking", tags=["Banking"])

# ========== 🏦 BANK ACCOUNTS ==========
BANKS = {
    "sbi": {"name": "State Bank of India", "hindi": "भारतीय स्टेट बैंक", "ifsc_prefix": "SBIN", "branches": 22000, "rating": 4.5},
    "hdfc": {"name": "HDFC Bank", "hindi": "एचडीएफसी बैंक", "ifsc_prefix": "HDFC", "branches": 6800, "rating": 4.7},
    "icici": {"name": "ICICI Bank", "hindi": "आईसीआईसीआई बैंक", "ifsc_prefix": "ICIC", "branches": 5200, "rating": 4.6},
    "pnb": {"name": "Punjab National Bank", "hindi": "पंजाब नेशनल बैंक", "ifsc_prefix": "PUNB", "branches": 10800, "rating": 4.3},
    "bob": {"name": "Bank of Baroda", "hindi": "बैंक ऑफ बड़ौदा", "ifsc_prefix": "BARB", "branches": 8200, "rating": 4.4},
    "axis": {"name": "Axis Bank", "hindi": "ऐक्सिस बैंक", "ifsc_prefix": "UTIB", "branches": 4800, "rating": 4.5},
    "canara": {"name": "Canara Bank", "hindi": "कैनरा बैंक", "ifsc_prefix": "CNRB", "branches": 9700, "rating": 4.2},
    "union": {"name": "Union Bank of India", "hindi": "यूनियन बैंक ऑफ इंडिया", "ifsc_prefix": "UBIN", "branches": 8500, "rating": 4.3},
}

@router.get("/banks")
def get_banks():
    """🏦 सभी बैंक — List All Banks"""
    return {"status": "success", "count": len(BANKS), "banks": BANKS}

@router.get("/banks/{bank_code}")
def get_bank_detail(bank_code: str):
    """📋 बैंक डिटेल — Bank Details"""
    bank = BANKS.get(bank_code.lower())
    if not bank:
        return {"status": "error", "message": "Bank not found"}
    return {"status": "success", "bank": bank}

@router.get("/banks/{bank_code}/branches/{city}")
def get_branches(bank_code: str, city: str):
    """📍 शाखाएं खोजें — Find Branches"""
    bank = BANKS.get(bank_code.lower())
    if not bank:
        return {"status": "error", "message": "Bank not found"}
    branches = [
        {"name": f"{bank['name']} Main Branch, {city.title()}", "ifsc": f"{bank['ifsc_prefix']}0000001", "address": f"Main Road, {city.title()}", "phone": f"+91-1800-{random.randint(1000000,9999999)}", "timings": "10 AM - 4 PM"},
        {"name": f"{bank['name']} City Center, {city.title()}", "ifsc": f"{bank['ifsc_prefix']}0000002", "address": f"City Center Mall, {city.title()}", "phone": f"+91-1800-{random.randint(1000000,9999999)}", "timings": "10 AM - 4 PM"},
        {"name": f"{bank['name']} Industrial Area, {city.title()}", "ifsc": f"{bank['ifsc_prefix']}0000003", "address": f"Industrial Area, {city.title()}", "phone": f"+91-1800-{random.randint(1000000,9999999)}", "timings": "10 AM - 4 PM"},
    ]
    return {"status": "success", "bank": bank['name'], "city": city.title(), "branches": branches}

# ========== 💸 UPI PAYMENTS ==========
@router.get("/upi/verify/{upi_id}")
def verify_upi(upi_id: str):
    """✅ UPI Verify — Verify UPI ID"""
    valid_suffixes = ["@okaxis", "@okhdfcbank", "@oksbi", "@okicici", "@paytm", "@ybl", "@apl"]
    is_valid = any(upi_id.endswith(s) for s in valid_suffixes)
    if not is_valid:
        return {"status": "error", "message": "Invalid UPI ID format", "valid_suffixes": valid_suffixes}
    # Simulate verification
    name = upi_id.split("@")[0].replace(".", " ").title()
    banks_map = {"@okaxis": "Axis Bank", "@okhdfcbank": "HDFC Bank", "@oksbi": "SBI", "@okicici": "ICICI Bank", "@paytm": "Paytm Payments Bank", "@ybl": "Yes Bank", "@apl": "Amazon Pay"}
    bank = next((banks_map[s] for s in valid_suffixes if upi_id.endswith(s)), "Unknown")
    return {"status": "success", "upi_id": upi_id, "name": name, "bank": bank, "verified": True, "daily_limit": 100000}

@router.post("/upi/send")
def send_money(upi_id: str = Query(...), amount: float = Query(...), pin: str = Query(...), note: str = Query("")):
    """💸 पैसे भेजो — Send Money via UPI"""
    if len(pin) != 4 or not pin.isdigit():
        return {"status": "error", "message": "Invalid UPI PIN (4 digits required)"}
    if amount <= 0 or amount > 100000:
        return {"status": "error", "message": "Amount must be between ₹1 and ₹1,00,000"}
    txn_id = f"SJ{int(time.time())}{random.randint(1000,9999)}"
    return {
        "status": "success",
        "txn_id": txn_id,
        "to": upi_id,
        "amount": amount,
        "note": note,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"₹{amount} successfully sent to {upi_id}"
    }

@router.get("/upi/history")
def upi_history(limit: int = Query(10, ge=1, le=50)):
    """📜 UPI History — Transaction History"""
    txns = []
    names = ["Rahul Sharma", "Priya Patel", "Amit Kumar", "Sneha Gupta", "Vikram Singh"]
    for i in range(limit):
        txns.append({
            "txn_id": f"SJ{int(time.time())-i*3600}{random.randint(1000,9999)}",
            "to": f"user{random.randint(1,999)}@{random.choice(['okaxis','oksbi','paytm'])}",
            "name": random.choice(names),
            "amount": random.choice([50, 100, 250, 500, 1000, 2000, 5000]),
            "type": random.choice(["sent", "received"]),
            "status": "success",
            "date": time.strftime("%Y-%m-%d", time.localtime(time.time()-i*86400)),
            "note": random.choice(["Lunch", "Rent", "Groceries", "Gift", ""])
        })
    return {"status": "success", "count": len(txns), "transactions": txns}

@router.get("/upi/qr/{upi_id}")
def generate_qr(upi_id: str, amount: Optional[float] = Query(None), note: str = Query("")):
    """📱 QR Code — Generate Payment QR"""
    qr_data = f"upi://pay?pa={upi_id}"
    if amount:
        qr_data += f"&am={amount}"
    if note:
        qr_data += f"&tn={note}"
    return {"status": "success", "upi_id": upi_id, "amount": amount, "qr_string": qr_data, "message": "Scan this QR to pay"}

# ========== 💰 LOANS ==========
LOAN_TYPES = {
    "personal": {"name": "Personal Loan", "hindi": "व्यक्तिगत ऋण", "rate": 10.5, "max_amount": 2000000, "tenure": "1-5 years", "processing": 2.0},
    "home": {"name": "Home Loan", "hindi": "होम लोन", "rate": 8.4, "max_amount": 50000000, "tenure": "5-30 years", "processing": 1.0},
    "car": {"name": "Car Loan", "hindi": "कार लोन", "rate": 9.0, "max_amount": 15000000, "tenure": "1-7 years", "processing": 1.5},
    "education": {"name": "Education Loan", "hindi": "शिक्षा ऋण", "rate": 8.5, "max_amount": 4000000, "tenure": "5-15 years", "processing": 0.5},
    "business": {"name": "Business Loan", "hindi": "व्यवसाय ऋण", "rate": 12.0, "max_amount": 50000000, "tenure": "1-10 years", "processing": 2.5},
    "gold": {"name": "Gold Loan", "hindi": "स्वर्ण ऋण", "rate": 7.5, "max_amount": 10000000, "tenure": "6 months - 3 years", "processing": 0.25},
}

@router.get("/loans/types")
def get_loan_types():
    """💰 लोन के प्रकार — Loan Types"""
    return {"status": "success", "loans": LOAN_TYPES}

@router.get("/loans/emi-calculator")
def emi_calculator(principal: float = Query(...), rate: float = Query(...), tenure_months: int = Query(...)):
    """📊 EMI Calculator — Calculate EMI"""
    r = rate / (12 * 100)  # Monthly rate
    emi = (principal * r * (1 + r)**tenure_months) / ((1 + r)**tenure_months - 1)
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    return {
        "status": "success",
        "principal": principal,
        "rate": rate,
        "tenure_months": tenure_months,
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "message": f"Monthly EMI: ₹{round(emi, 2)} for {tenure_months} months"
    }

@router.get("/loans/compare")
def compare_loans(amount: float = Query(500000), tenure: int = Query(60)):
    """🔍 लोन कंपेयर — Compare Loans"""
    results = []
    for code, loan in LOAN_TYPES.items():
        r = loan["rate"] / (12 * 100)
        emi = (amount * r * (1 + r)**tenure) / ((1 + r)**tenure - 1)
        total = emi * tenure
        interest = total - amount
        results.append({
            "type": code,
            "name": loan["name"],
            "hindi": loan["hindi"],
            "rate": loan["rate"],
            "emi": round(emi, 2),
            "total_interest": round(interest, 2),
            "total_payment": round(total, 2),
            "processing_fee": round(amount * loan["processing"] / 100, 2)
        })
    results.sort(key=lambda x: x["emi"])
    return {"status": "success", "amount": amount, "tenure_months": tenure, "best_option": results[0], "all_options": results}

@router.post("/loans/apply")
def apply_loan(loan_type: str = Query(...), amount: float = Query(...), tenure: int = Query(...), income: float = Query(...), pan: str = Query(...)):
    """📝 लोन अप्लाई — Apply for Loan"""
    loan = LOAN_TYPES.get(loan_type)
    if not loan:
        return {"status": "error", "message": "Invalid loan type", "available": list(LOAN_TYPES.keys())}
    if amount > loan["max_amount"]:
        return {"status": "error", "message": f"Max amount for {loan['name']} is ₹{loan['max_amount']:,}"}
    # Simple eligibility check
    eligible = income >= amount * 0.05  # Monthly income should be 5% of loan amount
    app_id = f"SJLOAN{random.randint(100000,999999)}"
    return {
        "status": "success",
        "application_id": app_id,
        "loan_type": loan["name"],
        "amount": amount,
        "tenure": tenure,
        "eligible": eligible,
        "message": "Application submitted!" if eligible else "Income proof required. Please upload salary slips.",
        "next_steps": ["Upload KYC documents", "Bank verification", "Loan approval (2-3 days)"] if eligible else ["Upload salary slips", "Re-apply with co-applicant"]
    }

# ========== 🛡️ INSURANCE ==========
INSURANCE_TYPES = {
    "health": {"name": "Health Insurance", "hindi": "स्वास्थ्य बीमा", "premium_per_lakh": 1200, "coverage": "Hospitalization, Pre-post expenses", "network_hospitals": 5000},
    "life": {"name": "Life Insurance", "hindi": "जीवन बीमा", "premium_per_lakh": 800, "coverage": "Death benefit, Maturity", "term": "10-40 years"},
    "vehicle": {"name": "Vehicle Insurance", "hindi": "वाहन बीमा", "premium_per_lakh": 3500, "coverage": "Accident, Theft, Third-party", "term": "1 year"},
    "home": {"name": "Home Insurance", "hindi": "घर बीमा", "premium_per_lakh": 500, "coverage": "Fire, Theft, Natural disasters", "term": "1-5 years"},
    "travel": {"name": "Travel Insurance", "hindi": "यात्रा बीमा", "premium_per_lakh": 200, "coverage": "Medical, Trip cancellation, Baggage", "term": "Per trip"},
}

@router.get("/insurance/types")
def get_insurance_types():
    """🛡️ बीमा प्रकार — Insurance Types"""
    return {"status": "success", "insurance": INSURANCE_TYPES}

@router.get("/insurance/premium")
def calculate_premium(insurance_type: str = Query(...), sum_assured: float = Query(...), age: int = Query(...)):
    """💰 Premium Calculator — Calculate Insurance Premium"""
    ins = INSURANCE_TYPES.get(insurance_type)
    if not ins:
        return {"status": "error", "message": "Invalid insurance type"}
    base_premium = (sum_assured / 100000) * ins["premium_per_lakh"]
    # Age factor
    age_factor = 1.0
    if age > 40: age_factor = 1.3
    if age > 50: age_factor = 1.8
    if age > 60: age_factor = 2.5
    final_premium = round(base_premium * age_factor, 2)
    return {
        "status": "success",
        "insurance_type": ins["name"],
        "sum_assured": sum_assured,
        "age": age,
        "base_premium": round(base_premium, 2),
        "age_factor": age_factor,
        "final_premium": final_premium,
        "monthly": round(final_premium / 12, 2),
        "coverage": ins["coverage"]
    }

# ========== 📈 INVESTMENTS ==========
INVESTMENT_OPTIONS = {
    "fd": {"name": "Fixed Deposit", "hindi": "सावधि जमा", "returns": 7.5, "risk": "Zero", "min_amount": 1000, "lock_in": "7 days - 10 years"},
    "rd": {"name": "Recurring Deposit", "hindi": "आवर्ती जमा", "returns": 7.0, "risk": "Zero", "min_amount": 100, "lock_in": "6 months - 10 years"},
    "ppf": {"name": "PPF", "hindi": "पब्लिक प्रोविडेंट फंड", "returns": 7.1, "risk": "Zero", "min_amount": 500, "lock_in": "15 years"},
    "nps": {"name": "NPS", "hindi": "नेशनल पेंशन स्कीम", "returns": 10.5, "risk": "Low", "min_amount": 500, "lock_in": "Till 60 years"},
    "mutual_fund": {"name": "Mutual Fund (SIP)", "hindi": "म्यूचुअल फंड", "returns": 12.0, "risk": "Medium", "min_amount": 500, "lock_in": "None"},
    "stocks": {"name": "Stocks", "hindi": "शेयर", "returns": 15.0, "risk": "High", "min_amount": 1, "lock_in": "None"},
    "gold": {"name": "Digital Gold", "hindi": "डिजिटल सोना", "returns": 8.5, "risk": "Low", "min_amount": 1, "lock_in": "None"},
    "crypto": {"name": "Crypto", "hindi": "क्रिप्टो", "returns": 25.0, "risk": "Very High", "min_amount": 100, "lock_in": "None"},
}

@router.get("/investments/options")
def get_investment_options():
    """📈 निवेश विकल्प — Investment Options"""
    return {"status": "success", "investments": INVESTMENT_OPTIONS}

@router.get("/investments/calculator")
def investment_calculator(investment_type: str = Query(...), amount: float = Query(...), years: int = Query(...), monthly: bool = Query(False)):
    """📊 Returns Calculator — Calculate Investment Returns"""
    inv = INVESTMENT_OPTIONS.get(investment_type)
    if not inv:
        return {"status": "error", "message": "Invalid investment type"}
    rate = inv["returns"] / 100
    if monthly:
        # SIP calculation
        n = years * 12
        r = rate / 12
        future_value = amount * (((1 + r)**n - 1) / r) * (1 + r)
        total_invested = amount * n
    else:
        # Lump sum
        future_value = amount * (1 + rate)**years
        total_invested = amount

    return {
        "status": "success",
        "investment": inv["name"],
        "hindi": inv["hindi"],
        "amount": amount,
        "years": years,
        "monthly": monthly,
        "total_invested": round(total_invested, 2),
        "future_value": round(future_value, 2),
        "returns": round(future_value - total_invested, 2),
        "returns_percent": round(((future_value - total_invested) / total_invested) * 100, 2),
        "risk": inv["risk"]
    }

@router.get("/investments/compare")
def compare_investments(amount: float = Query(100000), years: int = Query(10)):
    """🔍 निवेश तुलना — Compare Investments"""
    results = []
    for code, inv in INVESTMENT_OPTIONS.items():
        rate = inv["returns"] / 100
        if code in ["mutual_fund", "rd", "nps"]:
            # SIP style monthly
            n = years * 12
            r = rate / 12
            monthly_amt = amount / 12
            fv = monthly_amt * (((1 + r)**n - 1) / r) * (1 + r)
            invested = amount * years
        else:
            fv = amount * (1 + rate)**years
            invested = amount
        results.append({
            "type": code,
            "name": inv["name"],
            "hindi": inv["hindi"],
            "returns": inv["returns"],
            "risk": inv["risk"],
            "future_value": round(fv, 2),
            "profit": round(fv - invested, 2),
            "profit_percent": round(((fv - invested) / invested) * 100, 2)
        })
    results.sort(key=lambda x: x["future_value"], reverse=True)
    return {"status": "success", "amount": amount, "years": years, "best_option": results[0], "all_options": results}

# ========== 💳 CREDIT SCORE ==========
@router.get("/credit-score/check")
def check_credit_score(pan: str = Query(...)):
    """💳 क्रेडिट स्कोर — Check Credit Score"""
    if len(pan) != 10:
        return {"status": "error", "message": "Invalid PAN format (10 characters required)"}
    # Simulate score based on PAN hash
    hash_val = int(hashlib.md5(pan.encode()).hexdigest(), 16)
    score = 650 + (hash_val % 350)  # 650-999 range
    if score >= 750:
        rating = "Excellent — Best loan rates available!"
        color = "green"
    elif score >= 650:
        rating = "Good — Eligible for most loans"
        color = "yellow"
    elif score >= 550:
        rating = "Fair — Limited options, higher rates"
        color = "orange"
    else:
        rating = "Poor — Improve before applying"
        color = "red"
    return {
        "status": "success",
        "pan": pan[:5] + "*****",
        "credit_score": score,
        "rating": rating,
        "color": color,
        "factors": {
            "payment_history": random.randint(70, 100),
            "credit_utilization": random.randint(30, 80),
            "credit_age": random.randint(1, 20),
            "credit_mix": random.randint(60, 100),
            "recent_inquiries": random.randint(0, 5)
        },
        "tips": ["Pay EMIs on time", "Keep credit utilization below 30%", "Don't apply for multiple loans", "Check score monthly"]
    }

@router.get("/credit-score/improve")
def improve_credit_score(current_score: int = Query(...)):
    """📈 स्कोर बढ़ाओ — Improve Credit Score"""
    tips = []
    if current_score < 600:
        tips = ["Pay all dues on time", "Settle pending defaults", "Get a secured credit card", "Keep old accounts active"]
    elif current_score < 700:
        tips = ["Reduce credit utilization to 30%", "Pay full credit card bill", "Avoid new loan applications", "Check for errors in CIBIL report"]
    elif current_score < 800:
        tips = ["Maintain diverse credit mix", "Increase credit limit", "Keep old accounts open", "Monitor score regularly"]
    else:
        tips = ["You're doing great!", "Maintain current habits", "Negotiate better rates with banks", "Consider premium credit cards"]
    return {"status": "success", "current_score": current_score, "target_score": min(current_score + 100, 900), "tips": tips, "estimated_time": "3-6 months"}

# ========== 🧾 BILL PAYMENTS ==========
BILL_TYPES = {
    "electricity": {"name": "Electricity Bill", "hindi": "बिजली बिल", "providers": ["UPPCL", "Tata Power", "BSES", "MSEB", "Torrent Power"]},
    "water": {"name": "Water Bill", "hindi": "पानी का बिल", "providers": ["Jal Board", "MCG", "KMC", "NMC"]},
    "gas": {"name": "Gas Bill", "hindi": "गैस बिल", "providers": ["Indane", "Bharat Gas", "HP Gas"]},
    "broadband": {"name": "Broadband", "hindi": "ब्रॉडबैंड", "providers": ["JioFiber", "Airtel Xstream", "BSNL", "ACT"]},
    "mobile": {"name": "Mobile Recharge", "hindi": "मोबाइल रिचार्ज", "providers": ["Jio", "Airtel", "Vi", "BSNL"]},
    "dth": {"name": "DTH Recharge", "hindi": "डीटीएच रिचार्ज", "providers": ["Tata Play", "Dish TV", "Airtel DTH", "Sun Direct"]},
}

@router.get("/bills/types")
def get_bill_types():
    """🧾 बिल के प्रकार — Bill Types"""
    return {"status": "success", "bills": BILL_TYPES}

@router.get("/bills/fetch")
def fetch_bill(bill_type: str = Query(...), consumer_no: str = Query(...), provider: str = Query(...)):
    """📥 बिल देखो — Fetch Bill"""
    bill = BILL_TYPES.get(bill_type)
    if not bill:
        return {"status": "error", "message": "Invalid bill type"}
    amount = random.randint(200, 5000)
    due_date = time.strftime("%Y-%m-%d", time.localtime(time.time() + random.randint(5, 30) * 86400))
    return {
        "status": "success",
        "bill_type": bill["name"],
        "provider": provider,
        "consumer_no": consumer_no,
        "amount": amount,
        "due_date": due_date,
        "status": "unpaid" if random.random() > 0.3 else "paid",
        "late_fee": 50 if random.random() > 0.7 else 0
    }

@router.post("/bills/pay")
def pay_bill(bill_type: str = Query(...), consumer_no: str = Query(...), amount: float = Query(...), upi_id: str = Query(...)):
    """💳 बिल भरो — Pay Bill"""
    txn_id = f"SJBILL{int(time.time())}{random.randint(1000,9999)}"
    return {
        "status": "success",
        "txn_id": txn_id,
        "bill_type": bill_type,
        "consumer_no": consumer_no,
        "amount": amount,
        "paid_via": upi_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"₹{amount} paid successfully for {bill_type}"
    }

# ========== 🏦 BANKING HUB ROOT ==========
@router.get("/")
def banking_root():
    """🏦 Banking Hub Root"""
    return {
        "hub": "Banking Hub",
        "status": "🔥 LIVE",
        "modules": ["Bank Accounts", "UPI Payments", "Loans", "Insurance", "Investments", "Credit Score", "Bill Payments"],
        "endpoints": {
            "banks": "/banking/banks, /banking/banks/{code}, /banking/banks/{code}/branches/{city}",
            "upi": "/banking/upi/verify/{upi_id}, /banking/upi/send, /banking/upi/history, /banking/upi/qr/{upi_id}",
            "loans": "/banking/loans/types, /banking/loans/emi-calculator, /banking/loans/compare, /banking/loans/apply",
            "insurance": "/banking/insurance/types, /banking/insurance/premium",
            "investments": "/banking/investments/options, /banking/investments/calculator, /banking/investments/compare",
            "credit": "/banking/credit-score/check, /banking/credit-score/improve",
            "bills": "/banking/bills/types, /banking/bills/fetch, /banking/bills/pay"
        }
    }
