import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ============================================================
# 🇮🇳 INDIA BANKS
# ============================================================
INDIAN_BANKS = {
    "balance_check": {
        "title": "🇮🇳 Balance Check - Missed Call",
        "sbi": "09223766666",
        "hdfc": "1800-270-3333",
        "icici": "9594612612",
        "pnb": "1800-180-2223",
        "bob": "8468001111",
        "canara": "09015483483",
        "union": "09223008486",
        "axis": "1800-419-5959",
        "bank_of_india": "09015135135",
        "idbi": "09212993399",
        "indian_bank": "09289592895",
        "uco": "09278792787"
    },
    "customer_care": {
        "title": "🇮🇳 Customer Care",
        "sbi": "1800-1234",
        "hdfc": "1800-202-6161",
        "icici": "1860-120-7777",
        "pnb": "1800-180-2222",
        "bob": "1800-5700",
        "canara": "1800-1030",
        "union": "1800-208-2244",
        "axis": "1860-419-5555",
        "hsbc": "1800-267-3456",
        "idbi": "1800-209-4324"
    },
    "upi": {
        "title": "🇮🇳 UPI Information",
        "apps": ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay"],
        "limits": {"daily": "₹1,00,000", "per_txn": "₹1,00,000"},
        "helpline": "1800-120-1740"
    },
    "loans": {
        "title": "🇮🇳 Loans",
        "types": ["Personal", "Home", "Car", "Education", "Gold", "Business"],
        "govt": [
            {"name": "MUDRA", "max": "₹10 Lakh", "site": "mudra.org.in"},
            {"name": "PM SVANidhi", "max": "₹10,000", "site": "pmsvanidhi.mohua.gov.in"},
            {"name": "Stand-Up India", "max": "₹1 Crore", "site": "standupmitra.in"}
        ]
    },
    "schemes": {
        "title": "🇮🇳 Govt Schemes",
        "list": [
            {"name": "Jan Dhan", "benefit": "Zero balance", "site": "pmjdy.gov.in"},
            {"name": "Sukanya Samriddhi", "benefit": "Girl child savings", "site": "nsiindia.gov.in"},
            {"name": "Atal Pension", "benefit": "Pension scheme", "site": "npscra.nsdl.co.in"},
            {"name": "PMJJBY", "benefit": "Life insurance ₹2L", "site": "jansuraksha.gov.in"},
            {"name": "PMSBY", "benefit": "Accident insurance ₹2L", "site": "jansuraksha.gov.in"}
        ]
    }
}

# ============================================================
# 🌍 INTERNATIONAL BANKS
# ============================================================
WORLD_BANKS = {
    "usa": {
        "title": "🇺🇸 USA Banks",
        "banks": {
            "chase": {"phone": "1-800-935-9935", "site": "chase.com"},
            "bank_of_america": {"phone": "1-800-432-1000", "site": "bankofamerica.com"},
            "wells_fargo": {"phone": "1-800-869-3557", "site": "wellsfargo.com"},
            "citi": {"phone": "1-800-374-9700", "site": "citi.com"},
            "usbank": {"phone": "1-800-872-2657", "site": "usbank.com"},
            "pnc": {"phone": "1-888-762-2265", "site": "pnc.com"},
            "capital_one": {"phone": "1-877-383-4802", "site": "capitalone.com"},
            "td_bank": {"phone": "1-888-751-9000", "site": "tdbank.com"}
        }
    },
    "uk": {
        "title": "🇬🇧 UK Banks",
        "banks": {
            "hsbc_uk": {"phone": "03457-404-404", "site": "hsbc.co.uk"},
            "barclays": {"phone": "0345-734-5345", "site": "barclays.co.uk"},
            "lloyds": {"phone": "0345-300-0000", "site": "lloydsbank.com"},
            "natwest": {"phone": "03457-888-444", "site": "natwest.com"},
            "santander_uk": {"phone": "0800-9-123-123", "site": "santander.co.uk"},
            "halifax": {"phone": "0345-720-3040", "site": "halifax.co.uk"}
        }
    },
    "uae": {
        "title": "🇦🇪 UAE Banks",
        "banks": {
            "emirates_nbd": {"phone": "600-54-0000", "site": "emiratesnbd.com"},
            "adcb": {"phone": "600-50-2030", "site": "adcb.com"},
            "fab": {"phone": "600-52-5500", "site": "bankfab.com"},
            "dubai_islamic": {"phone": "111-786-DIB", "site": "dubaiislamicbank.com"},
            "mashreq": {"phone": "04-424-4444", "site": "mashreqbank.com"}
        }
    },
    "canada": {
        "title": "🇨🇦 Canada Banks",
        "banks": {
            "rbc": {"phone": "1-800-769-2511", "site": "rbcroyalbank.com"},
            "td_canada": {"phone": "1-866-222-3456", "site": "td.com"},
            "scotiabank": {"phone": "1-800-472-6842", "site": "scotiabank.com"},
            "bmo": {"phone": "1-877-225-5266", "site": "bmo.com"},
            "cibc": {"phone": "1-800-465-2422", "site": "cibc.com"}
        }
    },
    "australia": {
        "title": "🇦🇺 Australia Banks",
        "banks": {
            "commonwealth": {"phone": "13-2221", "site": "commbank.com.au"},
            "westpac": {"phone": "132-032", "site": "westpac.com.au"},
            "anz": {"phone": "13-13-14", "site": "anz.com.au"},
            "nab": {"phone": "13-22-65", "site": "nab.com.au"}
        }
    },
    "singapore": {
        "title": "🇸🇬 Singapore Banks",
        "banks": {
            "dbs": {"phone": "1800-111-1111", "site": "dbs.com.sg"},
            "ocbc": {"phone": "1800-363-3333", "site": "ocbc.com"},
            "uob": {"phone": "1800-222-2121", "site": "uob.com.sg"},
            "standard_chartered": {"phone": "6747-7000", "site": "sc.com/sg"}
        }
    },
    "hong_kong": {
        "title": "🇭🇰 Hong Kong Banks",
        "banks": {
            "hsbc_hk": {"phone": "+852-3988-2388", "site": "hsbc.com.hk"},
            "hang_seng": {"phone": "+852-2822-0228", "site": "hangseng.com"},
            "boc_hk": {"phone": "+852-3988-2388", "site": "bochk.com"},
            "standard_chartered_hk": {"phone": "+852-2886-8868", "site": "sc.com/hk"}
        }
    },
    "saudi": {
        "title": "🇸🇦 Saudi Arabia Banks",
        "banks": {
            "alrajhi": {"phone": "920-003-344", "site": "alrajhibank.com.sa"},
            "nbc": {"phone": "800-124-4040", "site": "bankalbilad.com"},
            "riyad_bank": {"phone": "920-002-470", "site": "riyadbank.com"},
            "samba": {"phone": "800-124-2121", "site": "sambabank.com"}
        }
    },
    "nri": {
        "title": "🌐 NRI Helplines (From India)",
        "usa": "1855-205-5577",
        "uk": "0808-178-5040",
        "canada": "1855-436-0726",
        "uae": "8000-3570-3218",
        "singapore": "800-1206-355",
        "australia": "1800-153-861",
        "saudi": "800-850-0000",
        "qatar": "00-800-100-348"
    }
}

# ============================================================
# 🏦 HANDLER
# ============================================================
async def handler(request: Request):
    try:
        params = dict(request.query_params)
        query = params.get("query", "").strip().lower()
        bank = params.get("bank", "").strip().lower()
        country = params.get("country", "").strip().lower()
        
        # 🇮🇳 INDIAN QUERIES
        if query in INDIAN_BANKS:
            data = INDIAN_BANKS[query]
            
            if bank and query in ["balance_check", "customer_care"]:
                if bank in data:
                    return JSONResponse(content={
                        "success": True,
                        "country": "🇮🇳 India",
                        "bank": bank.upper(),
                        "data": data[bank]
                    })
            
            return JSONResponse(content={
                "success": True,
                "country": "🇮🇳 India",
                "data": data
            })
        
        # 🌍 INTERNATIONAL QUERIES
        if country in WORLD_BANKS:
            data = WORLD_BANKS[country]
            
            if bank and "banks" in data:
                if bank in data["banks"]:
                    return JSONResponse(content={
                        "success": True,
                        "country": data["title"],
                        "bank": bank.upper(),
                        "data": data["banks"][bank]
                    })
            
            return JSONResponse(content={
                "success": True,
                "country": data["title"],
                "data": data
            })
        
        # 🌐 ALL COUNTRIES LIST
        if query == "countries":
            return JSONResponse(content={
                "success": True,
                "message": "🌍 Available Countries",
                "india_queries": list(INDIAN_BANKS.keys()),
                "world_countries": list(WORLD_BANKS.keys()),
                "usage": {
                    "india": "/api/banking?query=balance_check&bank=sbi",
                    "world": "/api/banking?country=usa&bank=chase",
                    "nri": "/api/banking?country=nri"
                }
            })
        
        # DEFAULT - Show all
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - World Banking",
            "total_countries": len(WORLD_BANKS) + 1,
            "india_queries": list(INDIAN_BANKS.keys()),
            "world_countries": list(WORLD_BANKS.keys()),
            "examples": [
                "/api/banking?query=balance_check&bank=sbi",
                "/api/banking?country=usa&bank=chase",
                "/api/banking?country=uk",
                "/api/banking?country=uae&bank=fab",
                "/api/banking?country=nri",
                "/api/banking?query=schemes"
            ]
        })
        
    except Exception as e:
        logger.error(f"Banking error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
