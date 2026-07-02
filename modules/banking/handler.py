import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ============================================================
# 🇮🇳 INDIA
# ============================================================
INDIA = {
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
        "uco": "09278792787",
        "central_bank": "09222250000",
        "bank_of_maharashtra": "1800-233-4526"
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
        "idbi": "1800-209-4324",
        "citi": "1860-210-2484",
        "kotak": "1860-266-2666",
        "yes_bank": "1800-1200",
        "indusind": "1860-500-5004"
    },
    "upi": {
        "title": "🇮🇳 UPI Information",
        "apps": ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay", "Cred", "Mobikwik"],
        "limits": {"daily": "₹1,00,000", "per_txn": "₹1,00,000"},
        "helpline": "1800-120-1740",
        "complaint": "cpc.npci.org.in"
    },
    "loans": {
        "title": "🇮🇳 Loans",
        "types": ["Personal", "Home", "Car", "Education", "Gold", "Business", "Agriculture", "Two-Wheeler"],
        "govt": [
            {"name": "MUDRA", "max": "₹10 Lakh", "site": "mudra.org.in"},
            {"name": "PM SVANidhi", "max": "₹10,000", "site": "pmsvanidhi.mohua.gov.in"},
            {"name": "Stand-Up India", "max": "₹1 Crore", "site": "standupmitra.in"},
            {"name": "PM KUSUM", "max": "₹1.5 Lakh", "site": "mnre.gov.in"}
        ]
    },
    "schemes": {
        "title": "🇮🇳 Govt Schemes",
        "list": [
            {"name": "Jan Dhan", "benefit": "Zero balance", "site": "pmjdy.gov.in"},
            {"name": "Sukanya Samriddhi", "benefit": "Girl child savings", "site": "nsiindia.gov.in"},
            {"name": "Atal Pension", "benefit": "Pension scheme", "site": "npscra.nsdl.co.in"},
            {"name": "PMJJBY", "benefit": "Life insurance ₹2L", "site": "jansuraksha.gov.in"},
            {"name": "PMSBY", "benefit": "Accident insurance ₹2L", "site": "jansuraksha.gov.in"},
            {"name": "APY", "benefit": "Pension ₹1000-5000/month", "site": "npscra.nsdl.co.in"}
        ]
    }
}

# ============================================================
# 🌏 ASIA-PACIFIC
# ============================================================
ASIA_PACIFIC = {
    "china": {
        "title": "🇨🇳 China Banks",
        "currency": "CNY (¥)",
        "banks": {
            "icbc": {"phone": "+86-95588", "site": "icbc.com.cn", "name": "Industrial & Commercial Bank"},
            "ccb": {"phone": "+86-95533", "site": "ccb.com", "name": "China Construction Bank"},
            "abc": {"phone": "+86-95599", "site": "abchina.com", "name": "Agricultural Bank"},
            "boc": {"phone": "+86-95566", "site": "boc.cn", "name": "Bank of China"},
            "bankcomm": {"phone": "+86-95559", "site": "bankcomm.com", "name": "Bank of Communications"},
            "cmb": {"phone": "+86-95555", "site": "cmbchina.com", "name": "China Merchants Bank"},
            "spdb": {"phone": "+86-95528", "site": "spdb.com.cn", "name": "Shanghai Pudong Development"},
            "citic": {"phone": "+86-95558", "site": "citicbank.com", "name": "CITIC Bank"}
        }
    },
    "japan": {
        "title": "🇯🇵 Japan Banks",
        "currency": "JPY (¥)",
        "banks": {
            "mufg": {"phone": "+81-3-3240-1111", "site": "bk.mufg.jp", "name": "Mitsubishi UFJ Financial"},
            "sumitomo": {"phone": "+81-3-5551-1411", "site": "smbc.co.jp", "name": "Sumitomo Mitsui Banking"},
            "mizuho": {"phone": "+81-3-3596-1111", "site": "mizuhobank.co.jp", "name": "Mizuho Bank"},
            "resona": {"phone": "+81-3-5832-2111", "site": "resonabank.co.jp", "name": "Resona Bank"}
        }
    },
    "south_korea": {
        "title": "🇰🇷 South Korea Banks",
        "currency": "KRW (₩)",
        "banks": {
            "shinhan": {"phone": "+82-2-1588-0360", "site": "shinhan.com", "name": "Shinhan Bank"},
            "kb": {"phone": "+82-2-1588-9999", "site": "kbstar.com", "name": "KB Kookmin Bank"},
            "woori": {"phone": "+82-2-1588-5000", "site": "wooribank.com", "name": "Woori Bank"},
            "hana": {"phone": "+82-2-1599-1111", "site": "hanabank.com", "name": "Hana Bank"},
            "ibk": {"phone": "+82-2-1588-2588", "site": "ibk.co.kr", "name": "Industrial Bank of Korea"}
        }
    },
    "thailand": {
        "title": "🇹🇭 Thailand Banks",
        "currency": "THB (฿)",
        "banks": {
            "bangkok_bank": {"phone": "+66-2-645-9000", "site": "bangkokbank.com", "name": "Bangkok Bank"},
            "kasikorn": {"phone": "+66-2-888-8888", "site": "kasikornbank.com", "name": "Kasikornbank"},
            "scb": {"phone": "+66-2-777-7777", "site": "scb.co.th", "name": "Siam Commercial Bank"},
            "krungthai": {"phone": "+66-2-111-1111", "site": "krungthai.com", "name": "Krungthai Bank"}
        }
    },
    "vietnam": {
        "title": "🇻🇳 Vietnam Banks",
        "currency": "VND (₫)",
        "banks": {
            "vietcombank": {"phone": "+84-24-3934-1839", "site": "vietcombank.com.vn", "name": "Vietcombank"},
            "bidv": {"phone": "+84-24-3825-1420", "site": "bidv.com.vn", "name": "BIDV"},
            "vietinbank": {"phone": "+84-24-3941-8868", "site": "vietinbank.vn", "name": "VietinBank"},
            "agribank": {"phone": "+84-24-3205-3205", "site": "agribank.com.vn", "name": "Agribank"}
        }
    },
    "indonesia": {
        "title": "🇮🇩 Indonesia Banks",
        "currency": "IDR (Rp)",
        "banks": {
            "bca": {"phone": "+62-21-2358-8000", "site": "bca.co.id", "name": "Bank Central Asia"},
            "mandiri": {"phone": "+62-21-5299-7777", "site": "bankmandiri.co.id", "name": "Bank Mandiri"},
            "bni": {"phone": "+62-21-251-1946", "site": "bni.co.id", "name": "Bank Negara Indonesia"},
            "bri": {"phone": "+62-21-575-1966", "site": "bri.co.id", "name": "Bank Rakyat Indonesia"}
        }
    },
    "malaysia": {
        "title": "🇲🇾 Malaysia Banks",
        "currency": "MYR (RM)",
        "banks": {
            "maybank": {"phone": "+60-3-2070-8833", "site": "maybank.com", "name": "Malayan Banking"},
            "cimb": {"phone": "+60-3-6204-7788", "site": "cimb.com", "name": "CIMB Bank"},
            "public_bank": {"phone": "+60-3-2176-6000", "site": "pbebank.com", "name": "Public Bank"},
            "rhb": {"phone": "+60-3-9286-8000", "site": "rhbgroup.com", "name": "RHB Bank"}
        }
    },
    "philippines": {
        "title": "🇵🇭 Philippines Banks",
        "currency": "PHP (₱)",
        "banks": {
            "bdo": {"phone": "+63-2-8840-7000", "site": "bdo.com.ph", "name": "BDO Unibank"},
            "metrobank": {"phone": "+63-2-8898-8000", "site": "metrobank.com.ph", "name": "Metropolitan Bank"},
            "bpi": {"phone": "+63-2-8891-0000", "site": "bpi.com.ph", "name": "Bank of the Philippine Islands"},
            "landbank": {"phone": "+63-2-8405-7000", "site": "landbank.com", "name": "Land Bank"}
        }
    },
    "bangladesh": {
        "title": "🇧🇩 Bangladesh Banks",
        "currency": "BDT (৳)",
        "banks": {
            "sonali": {"phone": "+880-2-955-1034", "site": "sonalibank.com.bd", "name": "Sonali Bank"},
            "janata": {"phone": "+880-2-955-9000", "site": "janatabank-bd.com", "name": "Janata Bank"},
            "brac": {"phone": "+880-2-5566-3000", "site": "bracbank.com", "name": "BRAC Bank"},
            "dbbl": {"phone": "+880-2-957-1622", "site": "dutchbanglabank.com", "name": "Dutch-Bangla Bank"}
        }
    },
    "pakistan": {
        "title": "🇵🇰 Pakistan Banks",
        "currency": "PKR (₨)",
        "banks": {
            "hbl": {"phone": "+92-21-111-111-425", "site": "hbl.com", "name": "Habib Bank"},
            "ubl": {"phone": "+92-42-111-825-888", "site": "ubldigital.com", "name": "United Bank"},
            "mcb": {"phone": "+92-42-111-000-622", "site": "mcb.com.pk", "name": "Muslim Commercial Bank"},
            "alfalah": {"phone": "+92-21-111-225-111", "site": "bankalfalah.com", "name": "Bank Alfalah"}
        }
    },
    "sri_lanka": {
        "title": "🇱🇰 Sri Lanka Banks",
        "currency": "LKR (Rs)",
        "banks": {
            "boc": {"phone": "+94-11-244-6790", "site": "bankofceylon.com", "name": "Bank of Ceylon"},
            "peoples": {"phone": "+94-11-248-1481", "site": "peoplesbank.lk", "name": "People's Bank"},
            "commercial": {"phone": "+94-11-235-0000", "site": "combank.net", "name": "Commercial Bank"},
            "hatton": {"phone": "+94-11-266-3000", "site": "hnb.net", "name": "Hatton National Bank"}
        }
    },
    "nepal": {
        "title": "🇳🇵 Nepal Banks",
        "currency": "NPR (Rs)",
        "banks": {
            "nabil": {"phone": "+977-1-444-4000", "site": "nabilbank.com", "name": "Nabil Bank"},
            "nic_asia": {"phone": "+977-1-444-5555", "site": "nicasiabank.com", "name": "NIC Asia Bank"},
            "everest": {"phone": "+977-1-444-0300", "site": "everestbankltd.com", "name": "Everest Bank"}
        }
    },
    "myanmar": {
        "title": "🇲🇲 Myanmar Banks",
        "currency": "MMK (K)",
        "banks": {
            "kbz": {"phone": "+95-1-380-380", "site": "kbzbank.com", "name": "Kanbawza Bank"},
            "aya": {"phone": "+95-1-231-7777", "site": "ayabank.com", "name": "AYA Bank"},
            "cb": {"phone": "+95-1-251-381", "site": "cbbank.com.mm", "name": "Co-operative Bank"}
        }
    },
    "cambodia": {
        "title": "🇰🇭 Cambodia Banks",
        "currency": "KHR (៛)",
        "banks": {
            "acleda": {"phone": "+855-23-426-888", "site": "acledabank.com.kh", "name": "ACLEDA Bank"},
            "canadia": {"phone": "+855-23-868-222", "site": "canadiabank.com.kh", "name": "Canadia Bank"}
        }
    }
}

# ============================================================
# 🌍 EUROPE
# ============================================================
EUROPE = {
    "uk": {
        "title": "🇬🇧 UK Banks",
        "currency": "GBP (£)",
        "banks": {
            "hsbc_uk": {"phone": "03457-404-404", "site": "hsbc.co.uk", "name": "HSBC UK"},
            "barclays": {"phone": "0345-734-5345", "site": "barclays.co.uk", "name": "Barclays"},
            "lloyds": {"phone": "0345-300-0000", "site": "lloydsbank.com", "name": "Lloyds Bank"},
            "natwest": {"phone": "03457-888-444", "site": "natwest.com", "name": "NatWest"},
            "santander_uk": {"phone": "0800-9-123-123", "site": "santander.co.uk", "name": "Santander UK"},
            "halifax": {"phone": "0345-720-3040", "site": "halifax.co.uk", "name": "Halifax"},
            "tsb": {"phone": "0345-975-8758", "site": "tsb.co.uk", "name": "TSB Bank"},
            "metro": {"phone": "0800-080-8500", "site": "metrobankonline.co.uk", "name": "Metro Bank"},
            "monzo": {"phone": "0800-802-1281", "site": "monzo.com", "name": "Monzo (Digital)"},
            "starling": {"phone": "0207-930-4450", "site": "starlingbank.com", "name": "Starling Bank (Digital)"}
        }
    },
    "germany": {
        "title": "🇩🇪 Germany Banks",
        "currency": "EUR (€)",
        "banks": {
            "deutsche": {"phone": "+49-69-910-38000", "site": "db.com", "name": "Deutsche Bank"},
            "commerzbank": {"phone": "+49-69-136-20000", "site": "commerzbank.com", "name": "Commerzbank"},
            "dzb": {"phone": "+49-69-7447-0", "site": "dzbank.de", "name": "DZ Bank"},
            "kfw": {"phone": "+49-69-7431-0", "site": "kfw.de", "name": "KfW Bankengruppe"},
            "ing": {"phone": "+49-69-9430-1000", "site": "ing.de", "name": "ING Germany"},
            "n26": {"phone": "+49-30-364-288-288", "site": "n26.com", "name": "N26 (Digital)"}
        }
    },
    "france": {
        "title": "🇫🇷 France Banks",
        "currency": "EUR (€)",
        "banks": {
            "bnp": {"phone": "+33-1-40-14-45-46", "site": "bnpparibas.com", "name": "BNP Paribas"},
            "societe_generale": {"phone": "+33-1-42-14-20-00", "site": "societegenerale.com", "name": "Société Générale"},
            "credit_agricole": {"phone": "+33-1-43-23-52-02", "site": "credit-agricole.com", "name": "Crédit Agricole"},
            "bpce": {"phone": "+33-1-58-40-41-42", "site": "groupebpce.fr", "name": "Groupe BPCE"},
            "lcl": {"phone": "+33-1-42-95-70-00", "site": "lcl.fr", "name": "LCL (Le Crédit Lyonnais)"}
        }
    },
    "switzerland": {
        "title": "🇨🇭 Switzerland Banks",
        "currency": "CHF (Fr)",
        "banks": {
            "ubs": {"phone": "+41-44-234-1111", "site": "ubs.com", "name": "UBS"},
            "credit_suisse": {"phone": "+41-44-333-8888", "site": "credit-suisse.com", "name": "Credit Suisse"},
            "zurich": {"phone": "+41-44-625-2121", "site": "zurichcantonalbank.ch", "name": "Zürcher Kantonalbank"},
            "raiffeisen": {"phone": "+41-848-880-888", "site": "raiffeisen.ch", "name": "Raiffeisen"}
        }
    },
    "netherlands": {
        "title": "🇳🇱 Netherlands Banks",
        "currency": "EUR (€)",
        "banks": {
            "ing_nl": {"phone": "+31-20-563-9111", "site": "ing.nl", "name": "ING Netherlands"},
            "rabobank": {"phone": "+31-30-216-0000", "site": "rabobank.nl", "name": "Rabobank"},
            "abn_amro": {"phone": "+31-20-343-2000", "site": "abnamro.nl", "name": "ABN AMRO"}
        }
    },
    "italy": {
        "title": "🇮🇹 Italy Banks",
        "currency": "EUR (€)",
        "banks": {
            "unicredit": {"phone": "+39-02-886-21", "site": "unicreditgroup.eu", "name": "UniCredit"},
            "intesa": {"phone": "+39-011-555-01", "site": "intesasanpaolo.com", "name": "Intesa Sanpaolo"},
            "monte_paschi": {"phone": "+39-0577-294-111", "site": "mps.it", "name": "Monte dei Paschi"}
        }
    },
    "spain": {
        "title": "🇪🇸 Spain Banks",
        "currency": "EUR (€)",
        "banks": {
            "santander_es": {"phone": "+34-915-121-000", "site": "santander.com", "name": "Banco Santander"},
            "bbva": {"phone": "+34-915-375-000", "site": "bbva.com", "name": "BBVA"},
            "caixabank": {"phone": "+34-932-201-000", "site": "caixabank.com", "name": "CaixaBank"},
            "sabadell": {"phone": "+34-935-459-000", "site": "bancosabadell.com", "name": "Banco Sabadell"}
        }
    },
    "russia": {
        "title": "🇷🇺 Russia Banks",
        "currency": "RUB (₽)",
        "banks": {
            "sberbank": {"phone": "+7-800-555-5550", "site": "sberbank.ru", "name": "Sberbank"},
            "vtb": {"phone": "+7-800-100-2424", "site": "vtb.ru", "name": "VTB Bank"},
            "gazprombank": {"phone": "+7-800-100-0711", "site": "gazprombank.ru", "name": "Gazprombank"},
            "alfa": {"phone": "+7-495-788-88-78", "site": "alfabank.ru", "name": "Alfa-Bank"},
            "tinkoff": {"phone": "+7-495-645-59-19", "site": "tinkoff.ru", "name": "Tinkoff (Digital)"}
        }
    },
    "sweden": {
        "title": "🇸🇪 Sweden Banks",
        "currency": "SEK (kr)",
        "banks": {
            "nordea": {"phone": "+46-771-224-488", "site": "nordea.se", "name": "Nordea"},
            "seb": {"phone": "+46-771-621-000", "site": "seb.se", "name": "SEB"},
            "swedbank": {"phone": "+46-771-221-122", "site": "swedbank.se", "name": "Swedbank"},
            "handelsbanken": {"phone": "+46-8-701-1000", "site": "handelsbanken.se", "name": "Handelsbanken"}
        }
    },
    "norway": {
        "title": "🇳🇴 Norway Banks",
        "currency": "NOK (kr)",
        "banks": {
            "dnb": {"phone": "+47-915-04800", "site": "dnb.no", "name": "DNB Bank"},
            "nordea_no": {"phone": "+47-232-06000", "site": "nordea.no", "name": "Nordea Norway"}
        }
    },
    "denmark": {
        "title": "🇩🇰 Denmark Banks",
        "currency": "DKK (kr)",
        "banks": {
            "danske": {"phone": "+45-33-44-00-00", "site": "danskebank.dk", "name": "Danske Bank"},
            "nordea_dk": {"phone": "+45-33-33-33-33", "site": "nordea.dk", "name": "Nordea Denmark"},
            "jyske": {"phone": "+45-89-89-89-89", "site": "jyskebank.dk", "name": "Jyske Bank"}
        }
    },
    "poland": {
        "title": "🇵🇱 Poland Banks",
        "currency": "PLN (zł)",
        "banks": {
            "pko": {"phone": "+48-800-302-302", "site": "pkobp.pl", "name": "PKO Bank Polski"},
            "pekao": {"phone": "+48-801-300-800", "site": "pekao.com.pl", "name": "Bank Pekao"},
            "ing_pl": {"phone": "+48-801-222-222", "site": "ing.pl", "name": "ING Poland"},
            "mBank": {"phone": "+48-801-300-800", "site": "mbank.pl", "name": "mBank (Digital)"}
        }
    },
    "turkey": {
        "title": "🇹🇷 Turkey Banks",
        "currency": "TRY (₺)",
        "banks": {
            "ziraat": {"phone": "+90-312-584-2000", "site": "ziraatbank.com.tr", "name": "Ziraat Bankası"},
            "isbank": {"phone": "+90-212-316-0000", "site": "isbank.com.tr", "name": "İş Bankası"},
            "garanti": {"phone": "+90-212-444-0001", "site": "garantibbva.com.tr", "name": "Garanti BBVA"},
            "akbank": {"phone": "+90-212-444-2525", "site": "akbank.com", "name": "Akbank"}
        }
    }
}

# ============================================================
# 🌎 AMERICAS
# ============================================================
AMERICAS = {
    "usa": {
        "title": "🇺🇸 USA Banks",
        "currency": "USD ($)",
        "banks": {
            "chase": {"phone": "1-800-935-9935", "site": "chase.com", "name": "JPMorgan Chase"},
            "bank_of_america": {"phone": "1-800-432-1000", "site": "bankofamerica.com", "name": "Bank of America"},
            "wells_fargo": {"phone": "1-800-869-3557", "site": "wellsfargo.com", "name": "Wells Fargo"},
            "citi": {"phone": "1-800-374-9700", "site": "citi.com", "name": "Citibank"},
            "usbank": {"phone": "1-800-872-2657", "site": "usbank.com", "name": "U.S. Bank"},
            "pnc": {"phone": "1-888-762-2265", "site": "pnc.com", "name": "PNC Bank"},
            "capital_one": {"phone": "1-877-383-4802", "site": "capitalone.com", "name": "Capital One"},
            "td_bank": {"phone": "1-888-751-9000", "site": "tdbank.com", "name": "TD Bank"},
            "truist": {"phone": "1-800-226-5228", "site": "truist.com", "name": "Truist"},
            "goldman": {"phone": "1-212-902-1000", "site": "goldmansachs.com", "name": "Goldman Sachs"},
            "morgan_stanley": {"phone": "1-888-454-3965", "site": "morganstanley.com", "name": "Morgan Stanley"},
            "ally": {"phone": "1-877-247-2559", "site": "ally.com", "name": "Ally Bank (Digital)"},
            "chime": {"phone": "1-844-244-6363", "site": "chime.com", "name": "Chime (Digital)"}
        }
    },
    "canada": {
        "title": "🇨🇦 Canada Banks",
        "currency": "CAD ($)",
        "banks": {
            "rbc": {"phone": "1-800-769-2511", "site": "rbcroyalbank.com", "name": "Royal Bank of Canada"},
            "td_canada": {"phone": "1-866-222-3456", "site": "td.com", "name": "TD Canada Trust"},
            "scotiabank": {"phone": "1-800-472-6842", "site": "scotiabank.com", "name": "Scotiabank"},
            "bmo": {"phone": "1-877-225-5266", "site": "bmo.com", "name": "Bank of Montreal"},
            "cibc": {"phone": "1-800-465-2422", "site": "cibc.com", "name": "CIBC"},
            "nbc": {"phone": "1-888-835-6281", "site": "nbc.ca", "name": "National Bank of Canada"},
            "tangerine": {"phone": "1-888-826-4374", "site": "tangerine.ca", "name": "Tangerine (Digital)"}
        }
    },
    "brazil": {
        "title": "🇧🇷 Brazil Banks",
        "currency": "BRL (R$)",
        "banks": {
            "itau": {"phone": "+55-11-4004-4828", "site": "itau.com.br", "name": "Itaú Unibanco"},
            "bradesco": {"phone": "+55-11-4004-0001", "site": "bradesco.com.br", "name": "Banco Bradesco"},
            "santander_br": {"phone": "+55-11-4004-3535", "site": "santander.com.br", "name": "Santander Brasil"},
            "bb": {"phone": "+55-800-729-0722", "site": "bb.com.br", "name": "Banco do Brasil"},
            "caixa": {"phone": "+55-800-726-0101", "site": "caixa.gov.br", "name": "Caixa Econômica Federal"},
            "nubank": {"phone": "+55-11-4003-4070", "site": "nubank.com.br", "name": "Nubank (Digital)"}
        }
    },
    "mexico": {
        "title": "🇲🇽 Mexico Banks",
        "currency": "MXN ($)",
        "banks": {
            "bbva_mx": {"phone": "+52-55-5226-2663", "site": "bbva.mx", "name": "BBVA México"},
            "santander_mx": {"phone": "+52-55-5169-4300", "site": "santander.com.mx", "name": "Santander México"},
            "banamex": {"phone": "+52-55-1226-3990", "site": "banamex.com", "name": "Citibanamex"},
            "banorte": {"phone": "+52-81-8152-4000", "site": "banorte.com", "name": "Banorte"}
        }
    },
    "argentina": {
        "title": "🇦🇷 Argentina Banks",
        "currency": "ARS ($)",
        "banks": {
            "galicia": {"phone": "+54-11-4343-0000", "site": "bancogalicia.com", "name": "Banco Galicia"},
            "santander_ar": {"phone": "+54-11-4343-0000", "site": "santander.com.ar", "name": "Santander Río"},
            "macro": {"phone": "+54-11-5222-2000", "site": "macro.com.ar", "name": "Banco Macro"}
        }
    },
    "chile": {
        "title": "🇨🇱 Chile Banks",
        "currency": "CLP ($)",
        "banks": {
            "bch": {"phone": "+56-2-2654-2000", "site": "bancochile.cl", "name": "Banco de Chile"},
            "santander_cl": {"phone": "+56-2-2654-2000", "site": "santander.cl", "name": "Banco Santander Chile"},
            "bci": {"phone": "+56-2-2654-2000", "site": "bci.cl", "name": "BCI"}
        }
    },
    "colombia": {
        "title": "🇨🇴 Colombia Banks",
        "currency": "COP ($)",
        "banks": {
            "bancolombia": {"phone": "+57-1-343-0000", "site": "grupobancolombia.com", "name": "Bancolombia"},
            "davivienda": {"phone": "+57-1-338-3838", "site": "davivienda.com", "name": "Davivienda"},
            "bbva_co": {"phone": "+57-1-401-0000", "site": "bbva.com.co", "name": "BBVA Colombia"}
        }
    }
}

# ============================================================
# 🌍 MIDDLE EAST & AFRICA
# ============================================================
MEA = {
    "uae": {
        "title": "🇦🇪 UAE Banks",
        "currency": "AED (د.إ)",
        "banks": {
            "emirates_nbd": {"phone": "600-54-0000", "site": "emiratesnbd.com", "name": "Emirates NBD"},
            "adcb": {"phone": "600-50-2030", "site": "adcb.com", "name": "ADCB"},
            "fab": {"phone": "600-52-5500", "site": "bankfab.com", "name": "First Abu Dhabi Bank"},
            "dubai_islamic": {"phone": "111-786-DIB", "site": "dubaiislamicbank.com", "name": "Dubai Islamic Bank"},
            "mashreq": {"phone": "04-424-4444", "site": "mashreqbank.com", "name": "Mashreq Bank"},
            "rakbank": {"phone": "600-54-4049", "site": "rakbank.ae", "name": "RAKBANK"}
        }
    },
    "saudi": {
        "title": "🇸🇦 Saudi Arabia Banks",
        "currency": "SAR (﷼)",
        "banks": {
            "alrajhi": {"phone": "920-003-344", "site": "alrajhibank.com.sa", "name": "Al Rajhi Bank"},
            "nbc": {"phone": "800-124-4040", "site": "bankalbilad.com", "name": "National Commercial Bank"},
            "riyad_bank": {"phone": "920-002-470", "site": "riyadbank.com", "name": "Riyad Bank"},
            "samba": {"phone": "800-124-2121", "site": "sambabank.com", "name": "Samba Financial"},
            "anb": {"phone": "920-001-928", "site": "anb.com.sa", "name": "Arab National Bank"}
        }
    },
    "qatar": {
        "title": "🇶🇦 Qatar Banks",
        "currency": "QAR (﷼)",
        "banks": {
            "qnb": {"phone": "+974-4440-7777", "site": "qnb.com", "name": "Qatar National Bank"},
            "cbq": {"phone": "+974-4449-4449", "site": "cbq.qa", "name": "Commercial Bank of Qatar"},
            "doha_bank": {"phone": "+974-4445-6000", "site": "dohabank.com.qa", "name": "Doha Bank"}
        }
    },
    "kuwait": {
        "title": "🇰🇼 Kuwait Banks",
        "currency": "KWD (د.ك)",
        "banks": {
            "nbk": {"phone": "+965-180-1801", "site": "nbk.com", "name": "National Bank of Kuwait"},
            "cbk": {"phone": "+965-188-2888", "site": "cbk.com", "name": "Commercial Bank of Kuwait"},
            "gbk": {"phone": "+965-2299-0000", "site": "gbk.com.kw", "name": "Gulf Bank"}
        }
    },
    "bahrain": {
        "title": "🇧🇭 Bahrain Banks",
        "currency": "BHD (د.ب)",
        "banks": {
            "ahli_united": {"phone": "+973-1721-5555", "site": "ahliunited.com", "name": "Ahli United Bank"},
            "bbk": {"phone": "+973-1721-5555", "site": "bbkonline.com", "name": "Bank of Bahrain & Kuwait"}
        }
    },
    "israel": {
        "title": "🇮🇱 Israel Banks",
        "currency": "ILS (₪)",
        "banks": {
            "hapoalim": {"phone": "+972-3-567-3333", "site": "bankhapoalim.co.il", "name": "Bank Hapoalim"},
            "leumi": {"phone": "+972-1-700-700-700", "site": "bankleumi.co.il", "name": "Bank Leumi"},
            "discount": {"phone": "+972-3-514-4111", "site": "discountbank.co.il", "name": "Israel Discount Bank"}
        }
    },
    "south_africa": {
        "title": "🇿🇦 South Africa Banks",
        "currency": "ZAR (R)",
        "banks": {
            "standard_bank": {"phone": "+27-11-636-9111", "site": "standardbank.co.za", "name": "Standard Bank"},
            "absa": {"phone": "+27-11-350-4000", "site": "absa.co.za", "name": "Absa"},
            "fnb": {"phone": "+27-11-369-1000", "site": "fnb.co.za", "name": "First National Bank"},
            "nedbank": {"phone": "+27-11-294-4444", "site": "nedbank.co.za", "name": "Nedbank"},
            "capitec": {"phone": "+27-21-941-1377", "site": "capitecbank.co.za", "name": "Capitec Bank"}
        }
    },
    "nigeria": {
        "title": "🇳🇬 Nigeria Banks",
        "currency": "NGN (₦)",
        "banks": {
            "gtbank": {"phone": "+234-700-482-666-328", "site": "gtbank.com", "name": "Guaranty Trust Bank"},
            "zenith": {"phone": "+234-700-936-4000", "site": "zenithbank.com", "name": "Zenith Bank"},
            "access": {"phone": "+234-1-271-2005", "site": "accessbankplc.com", "name": "Access Bank"},
            "uba": {"phone": "+234-1-280-8822", "site": "ubagroup.com", "name": "United Bank for Africa"},
            "first_bank": {"phone": "+234-1-448-5500", "site": "firstbanknigeria.com", "name": "First Bank of Nigeria"}
        }
    },
    "egypt": {
        "title": "🇪🇬 Egypt Banks",
        "currency": "EGP (E£)",
        "banks": {
            "nbe": {"phone": "+20-2-2390-0011", "site": "nbe.com.eg", "name": "National Bank of Egypt"},
            "cbe": {"phone": "+20-2-2595-5000", "site": "cbe.org.eg", "name": "Central Bank of Egypt"},
            "qnb_eg": {"phone": "+20-2-3535-1000", "site": "qnb.com.eg", "name": "QNB Al Ahli"}
        }
    },
    "kenya": {
        "title": "🇰🇪 Kenya Banks",
        "currency": "KES (KSh)",
        "banks": {
            "kcb": {"phone": "+254-711-087-000", "site": "kcbbankgroup.com", "name": "KCB Bank"},
            "equity": {"phone": "+254-763-000-000", "site": "equitybankgroup.com", "name": "Equity Bank"},
            "coop": {"phone": "+254-703-027-000", "site": "co-opbank.co.ke", "name": "Co-operative Bank"},
            "absa_ke": {"phone": "+254-732-130-120", "site": "absabank.co.ke", "name": "Absa Bank Kenya"}
        }
    },
    "ghana": {
        "title": "🇬🇭 Ghana Banks",
        "currency": "GHS (₵)",
        "banks": {
            "ecobank": {"phone": "+233-30-266-2000", "site": "ecobank.com", "name": "Ecobank Ghana"},
            "gcb": {"phone": "+233-30-266-8411", "site": "gcbbank.com.gh", "name": "GCB Bank"},
            "stanbic": {"phone": "+233-30-275-5000", "site": "stanbic.com.gh", "name": "Stanbic Bank Ghana"}
        }
    },
    "morocco": {
        "title": "🇲🇦 Morocco Banks",
        "currency": "MAD (د.م.)",
        "banks": {
            "attijariwafa": {"phone": "+212-537-212-212", "site": "attijariwafabank.com", "name": "Attijariwafa Bank"},
            "bmce": {"phone": "+212-537-212-212", "site": "bmcebank.ma", "name": "BMCE Bank"}
        }
    },
    "ethiopia": {
        "title": "🇪🇹 Ethiopia Banks",
        "currency": "ETB (Br)",
        "banks": {
            "cbe_et": {"phone": "+251-11-551-0000", "site": "combanketh.et", "name": "Commercial Bank of Ethiopia"},
            "dashen": {"phone": "+251-11-466-6611", "site": "dashenbanksc.com", "name": "Dashen Bank"}
        }
    }
}

# ============================================================
# 🌏 OCEANIA
# ============================================================
OCEANIA = {
    "australia": {
        "title": "🇦🇺 Australia Banks",
        "currency": "AUD ($)",
        "banks": {
            "commonwealth": {"phone": "13-2221", "site": "commbank.com.au", "name": "Commonwealth Bank"},
            "westpac": {"phone": "132-032", "site": "westpac.com.au", "name": "Westpac"},
            "anz": {"phone": "13-13-14", "site": "anz.com.au", "name": "ANZ"},
            "nab": {"phone": "13-22-65", "site": "nab.com.au", "name": "National Australia Bank"},
            "macquarie": {"phone": "1300-363-330", "site": "macquarie.com.au", "name": "Macquarie Bank"},
            "ing_au": {"phone": "133-464", "site": "ing.com.au", "name": "ING Australia"},
            "up": {"phone": "1300-864-595", "site": "up.com.au", "name": "Up Bank (Digital)"}
        }
    },
    "new_zealand": {
        "title": "🇳🇿 New Zealand Banks",
        "currency": "NZD ($)",
        "banks": {
            "anz_nz": {"phone": "0800-269-296", "site": "anz.co.nz", "name": "ANZ New Zealand"},
            "asb": {"phone": "0800-803-804", "site": "asb.co.nz", "name": "ASB Bank"},
            "bnz": {"phone": "0800-275-269", "site": "bnz.co.nz", "name": "Bank of New Zealand"},
            "westpac_nz": {"phone": "0800-400-600", "site": "westpac.co.nz", "name": "Westpac NZ"},
            "kiwibank": {"phone": "0800-501-501", "site": "kiwibank.co.nz", "name": "Kiwibank"}
        }
    },
    "fiji": {
        "title": "🇫🇯 Fiji Banks",
        "currency": "FJD ($)",
        "banks": {
            "anb": {"phone": "+679-321-4300", "site": "anbfiji.com", "name": "Australia & New Zealand Banking"},
            "bsp": {"phone": "+679-321-4300", "site": "bsp.com.fj", "name": "Bank of South Pacific"}
        }
    }
}

# ============================================================
# 🌐 NRI HELPLINES
# ============================================================
NRI = {
    "title": "🌐 NRI Helplines (From India)",
    "usa": "1855-205-5577",
    "uk": "0808-178-5040",
    "canada": "1855-436-0726",
    "uae": "8000-3570-3218",
    "singapore": "800-1206-355",
    "australia": "1800-153-861",
    "saudi": "800-850-0000",
    "qatar": "00-800-100-348",
    "kuwait": "00965-2205-2158",
    "bahrain": "00973-1617-5151",
    "oman": "00968-8007-8512",
    "south_africa": "0027-11-268-0051",
    "nigeria": "00234-1-277-4100",
    "kenya": "00254-20-222-9860"
}

# ============================================================
# 🏦 ALL REGIONS COMBINED
# ============================================================
ALL_REGIONS = {
    "india": INDIA,
    **ASIA_PACIFIC,
    **EUROPE,
    **AMERICAS,
    **MEA,
    **OCEANIA
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
        region = params.get("region", "").strip().lower()
        
        # 🇮🇳 INDIA QUERIES
        if query in INDIA:
            data = INDIA[query]
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
        
        # 🌍 COUNTRY SEARCH
        if country in ALL_REGIONS:
            data = ALL_REGIONS[country]
            if bank and "banks" in data:
                if bank in data["banks"]:
                    return JSONResponse(content={
                        "success": True,
                        "country": data["title"],
                        "currency": data.get("currency", ""),
                        "bank": bank.upper(),
                        "data": data["banks"][bank]
                    })
            return JSONResponse(content={
                "success": True,
                "country": data["title"],
                "currency": data.get("currency", ""),
                "data": data
            })
        
        # 🌐 NRI
        if country == "nri":
            return JSONResponse(content={
                "success": True,
                "data": NRI
            })
        
        # 🌍 REGION LIST
        if query == "regions":
            return JSONResponse(content={
                "success": True,
                "message": "🌍 World Banking Regions",
                "regions": {
                    "asia_pacific": list(ASIA_PACIFIC.keys()),
                    "europe": list(EUROPE.keys()),
                    "americas": list(AMERICAS.keys()),
                    "middle_east_africa": list(MEA.keys()),
                    "oceania": list(OCEANIA.keys())
                },
                "total_countries": len(ALL_REGIONS),
                "usage": "/api/banking?country=usa&bank=chase"
            })
        
        # 🌐 ALL COUNTRIES
        if query == "countries":
            return JSONResponse(content={
                "success": True,
                "message": "🌍 All Countries",
                "india_queries": list(INDIA.keys()),
                "world_countries": list(ALL_REGIONS.keys()),
                "total": len(ALL_REGIONS),
                "usage": "/api/banking?country=usa&bank=chase"
            })
        
        # DEFAULT
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - World Banking",
            "total_countries": len(ALL_REGIONS),
            "total_banks": sum(len(v.get("banks", {})) for v in ALL_REGIONS.values()),
            "regions": ["india", "asia_pacific", "europe", "americas", "middle_east_africa", "oceania"],
            "examples": [
                "/api/banking?query=balance_check&bank=sbi",
                "/api/banking?country=usa&bank=chase",
                "/api/banking?country=china&bank=icbc",
                "/api/banking?country=uk&bank=barclays",
                "/api/banking?country=uae&bank=fab",
                "/api/banking?country=nigeria&bank=gtbank",
                "/api/banking?country=south_africa&bank=absa",
                "/api/banking?country=brazil&bank=nubank",
                "/api/banking?country=japan&bank=mufg",
                "/api/banking?country=nri",
                "/api/banking?query=regions",
                "/api/banking?query=countries"
            ]
        })
        
    except Exception as e:
        logger.error(f"Banking error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e)
        })
