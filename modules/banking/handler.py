import os
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            query = params.get('query', '').strip().lower()
            bank = params.get('bank', '').strip()
        else:
            body = await request.json()
            query = body.get('query', '').strip().lower()
            bank = body.get('bank', '').strip()
        
        # Banking info database
        banking_data = {
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
        
        if query and query in banking_data:
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": banking_data[query]
            })
        
        # Return all if no specific query
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "available_queries": list(banking_data.keys()),
                "message": "Use ?query=balance_check / customer_care / upi / loans / schemes",
                "all_data": banking_data
            }
        })
        
    except Exception as e:
        logger.error(f"Banking crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
