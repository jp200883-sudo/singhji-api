# File: modules/banking.py (direct file)
# YA
# File: modules/banking/handler.py (folder with __init__.py)

import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# 🏦 BANKING DATA — Static (no API needed)
BANKING_DATA = {
    "balance_check": {
        "title": "Balance Check Numbers",
        "methods": {
            "missed_call": {
                "sbi": "09223766666",
                "hdfc": "1800-270-3333",
                "icici": "9594612612",
                "pnb": "1800-180-2223",
                "bob": "8468001111",
                "canara": "09015483483",
                "union": "09223008486",
                "axis": "1800-419-5959"
            },
            "sms": {
                "sbi": "SMS 'BAL' to 09223766666",
                "hdfc": "SMS 'BAL' to 5676712"
            }
        }
    },
    "customer_care": {
        "title": "Customer Care Numbers",
        "numbers": {
            "sbi": "1800-1234",
            "hdfc": "1800-202-6161",
            "icici": "1860-120-7777",
            "pnb": "1800-180-2222",
            "bob": "1800-5700",
            "canara": "1800-1030",
            "union": "1800-208-2244",
            "axis": "1860-419-5555"
        }
    },
    "upi": {
        "title": "UPI Information",
        "apps": ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay"],
        "limits": {
            "daily_limit": "₹1,00,000",
            "per_transaction": "₹1,00,000"
        },
        "helpline": "1800-120-1740"
    },
    "loans": {
        "title": "Loan Information",
        "types": ["Personal Loan", "Home Loan", "Car Loan", "Education Loan", "Gold Loan", "Business Loan"],
        "government_schemes": [
            {"name": "MUDRA Loan", "max_amount": "₹10 Lakh", "website": "https://www.mudra.org.in"},
            {"name": "PM SVANidhi", "max_amount": "₹10,000", "website": "https://pmsvanidhi.mohua.gov.in"},
            {"name": "Stand-Up India", "max_amount": "₹1 Crore", "website": "https://www.standupmitra.in"}
        ]
    },
    "schemes": {
        "title": "Government Banking Schemes",
        "list": [
            {"name": "Jan Dhan Yojana", "benefit": "Zero balance account", "website": "https://pmjdy.gov.in"},
            {"name": "Sukanya Samriddhi", "benefit": "Girl child savings", "website": "https://www.nsiindia.gov.in"},
            {"name": "Atal Pension Yojana", "benefit": "Pension scheme", "website": "https://www.npscra.nsdl.co.in"},
            {"name": "PMJJBY", "benefit": "Life insurance ₹2 lakh", "website": "https://www.jansuraksha.gov.in"},
            {"name": "PMSBY", "benefit": "Accident insurance ₹2 lakh", "website": "https://www.jansuraksha.gov.in"}
        ]
    }
}

async def handler(request: Request):
    """
    🏦 Singh Ji AI — Banking Module
    Endpoint: /api/banking?query=balance_check
    """
    try:
        # Get params
        params = dict(request.query_params)
        query = params.get('query', '').strip().lower()
        bank = params.get('bank', '').strip().lower()
        
        # ✅ Specific query
        if query and query in BANKING_DATA:
            data = BANKING_DATA[query]
            
            # Filter by bank if provided
            if bank and query == "balance_check":
                missed_call = data.get("methods", {}).get("missed_call", {})
                if bank in missed_call:
                    return JSONResponse(content={
                        "success": True,
                        "error": None,
                        "data": {
                            "bank": bank.upper(),
                            "missed_call": missed_call[bank],
                            "sms": data.get("methods", {}).get("sms", {}).get(bank, "N/A")
                        }
                    })
            
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": data
            })
        
        # ✅ List all available queries
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "message": "🦁 Singh Ji AI Banking",
                "available_queries": list(BANKING_DATA.keys()),
                "usage": "/api/banking?query=balance_check&bank=sbi",
                "examples": [
                    "/api/banking?query=balance_check",
                    "/api/banking?query=customer_care",
                    "/api/banking?query=upi",
                    "/api/banking?query=loans",
                    "/api/banking?query=schemes"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Banking error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "data": None
        })
