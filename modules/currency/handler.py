"""
═══════════════════════════════════════════════════════════════
  सिंह जी AI अल्ट्रा v8.0 — करेंसी कनवर्टर मॉड्यूल
  फाइल: modules/currency.py
  बनाया: 23 जुलाई 2026
  फीचर्स: मल्टी-API fallback, Supabase logging, रेट कैशिंग
═══════════════════════════════════════════════════════════════
"""

import httpx
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger("singhji.currency")

# ==== कॉन्फिगरेशन ====
CURRENCY_APIS = {
    "primary": "https://api.exchangerate-api.com/v4/latest/{base}",
    "fallback_1": "https://open.er-api.com/v6/latest/{base}",
    "fallback_2": "https://api.frankfurter.app/latest?from={base}&to={target}",
}

POPULAR_CURRENCIES = [
    "USD", "INR", "EUR", "GBP", "JPY", "AUD", "CAD", 
    "CHF", "CNY", "SGD", "AED", "SAR", "BDT", "PKR", "LKR"
]

# ==== डेटा क्लास ====
@dataclass
class CurrencyResponse:
    base: str
    target: str
    amount: float
    rate: float
    converted: float
    date: str
    source: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SinghJiCurrency:
    """
    सिंह जी करेंसी इंजन — मल्टी-API fallback के साथ
    """
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 मिनट
        self.supabase = None  # बाद में init होगा
        
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """कैश से डेटा निकालो"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["time"] < timedelta(seconds=self.cache_ttl):
                logger.info(f"💾 कैश हिट: {key}")
                return entry["data"]
            else:
                del self.cache[key]
        return None
    
    async def _save_to_cache(self, key: str, data: Dict):
        """कैश में सेव करो"""
        self.cache[key] = {
            "data": data,
            "time": datetime.now()
        }
        logger.info(f"💾 कैश सेव: {key}")
    
    async def _call_api(self, url: str, source: str, base: str, target: str) -> Optional[Dict]:
        """एक API कॉल करो"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                
            if resp.status_code != 200:
                logger.warning(f"⚠️ {source} fail: HTTP {resp.status_code}")
                return None
                
            data = resp.json()
            
            # API के हिसाब से rate निकालो
            if source == "primary" or source == "fallback_1":
                rate = data.get("rates", {}).get(target)
            elif source == "fallback_2":
                rate = data.get("rates", {}).get(target)
            else:
                rate = None
                
            if not rate:
                logger.warning(f"⚠️ {source} में {target} rate नहीं मिला")
                return None
                
            return {
                "rate": float(rate),
                "date": data.get("date", data.get("time_last_update_utc", datetime.now().strftime("%Y-%m-%d"))),
                "source": source
            }
            
        except httpx.TimeoutException:
            logger.error(f"⏱️ {source} timeout")
            return None
        except Exception as e:
            logger.error(f"💥 {source} error: {e}")
            return None
    
    async def convert(self, base: str, target: str, amount: float) -> CurrencyResponse:
        """
        करेंसी कनवर्ट करो — मल्टी-API fallback के साथ
        """
        base = base.upper()
        target = target.upper()
        
        # कैश चेक करो
        cache_key = f"{base}_{target}"
        cached = await self._get_from_cache(cache_key)
        if cached:
            rate = cached["rate"]
            return CurrencyResponse(
                base=base, target=target, amount=amount,
                rate=rate, converted=round(amount * rate, 2),
                date=cached["date"], source=f"{cached['source']} (cache)",
                timestamp=datetime.now().isoformat()
            )
        
        # API कॉल करो — fallback chain
        apis = [
            ("primary", CURRENCY_APIS["primary"].format(base=base)),
            ("fallback_1", CURRENCY_APIS["fallback_1"].format(base=base)),
            ("fallback_2", CURRENCY_APIS["fallback_2"].format(base=base, target=target)),
        ]
        
        result = None
        for source, url in apis:
            logger.info(f"🌐 {source} कॉल कर रहा हूँ: {base} → {target}")
            result = await self._call_api(url, source, base, target)
            if result:
                break
        
        if not result:
            raise Exception("सभी करेंसी APIs फेल हो गए")
        
        # कैश में सेव करो
        await self._save_to_cache(cache_key, result)
        
        converted = round(amount * result["rate"], 2)
        
        return CurrencyResponse(
            base=base, target=target, amount=amount,
            rate=result["rate"], converted=converted,
            date=result["date"], source=result["source"],
            timestamp=datetime.now().isoformat()
        )
    
    async def get_all_rates(self, base: str = "USD") -> Dict[str, Any]:
        """सभी करेंसी रेट्स निकालो"""
        base = base.upper()
        url = CURRENCY_APIS["primary"].format(base=base)
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
            data = resp.json()
            
            rates = data.get("rates", {})
            # सिर्फ popular currencies
            filtered = {k: v for k, v in rates.items() if k in POPULAR_CURRENCIES}
            
            return {
                "success": True,
                "base": base,
                "date": data.get("date", ""),
                "rates": filtered,
                "count": len(filtered)
            }
            
        except Exception as e:
            logger.error(f"💥 All rates error: {e}")
            raise


# ==== सिंगलटन इंस्टेंस ====
singhji_currency = SinghJiCurrency()


# ==== फास्टएपीआई राउटर ====
router = APIRouter(prefix="/currency", tags=["💰 करेंसी"])


@router.get("/convert")
async def currency_convert(
    base: str = "USD",
    target: str = "INR", 
    amount: float = 1.0
):
    """
    💰 करेंसी कनवर्ट करो
    
    Example: /currency/convert?base=USD&target=INR&amount=100
    """
    try:
        result = await singhji_currency.convert(base, target, amount)
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": result.to_dict(),
            "message": f"✅ {amount} {base.upper()} = {result.converted} {target.upper()}"
        })
        
    except Exception as e:
        logger.error(f"💥 Currency convert fail: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "data": None,
            "message": "❌ करेंसी कनवर्जन फेल हुआ, बाद में कोशिश करो"
        })


@router.get("/rates")
async def currency_rates(base: str = "USD"):
    """
    📊 सभी करेंसी रेट्स देखो
    
    Example: /currency/rates?base=USD
    """
    try:
        result = await singhji_currency.get_all_rates(base)
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "data": None
        })


@router.get("/popular")
async def popular_conversions():
    """
    🔥 लोकप्रिय कनवर्जन्स
    
    USD→INR, EUR→INR, GBP→INR, AED→INR
    """
    popular = [
        ("USD", "INR", 1),
        ("EUR", "INR", 1),
        ("GBP", "INR", 1),
        ("AED", "INR", 1),
        ("USD", "EUR", 1),
        ("INR", "USD", 100),
    ]
    
    results = []
    for b, t, a in popular:
        try:
            r = await singhji_currency.convert(b, t, a)
            results.append({
                "from": f"{a} {b}",
                "to": f"{r.converted} {t}",
                "rate": r.rate
            })
        except:
            pass
    
    return JSONResponse(content={
        "success": True,
        "data": results,
        "updated": datetime.now().strftime("%H:%M:%S")
    })


# ==== जेनेरिक हैंडलर (पुराने कोड के लिए compatible) ====
async def handler(request: Request):
    """
    पुराना handler — backward compatible
    """
    method = request.method
    if method == "GET":
        params = dict(request.query_params)
    else:
        params = await request.json()

    base = str(params.get('base', 'USD')).upper()
    target = str(params.get('target', 'INR')).upper()

    try:
        amount = float(params.get('amount', 1))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={
            "success": False, 
            "error": "amount एक संख्या होनी चाहिए", 
            "data": None
        })

    try:
        result = await singhji_currency.convert(base, target, amount)
        return JSONResponse(content={
            "success": True, 
            "error": None,
            "data": result.to_dict()
        })
        
    except httpx.TimeoutException:
        logger.error("Currency API timeout")
        return JSONResponse(status_code=504, content={
            "success": False, 
            "error": "Currency API timeout", 
            "data": None
        })
    except Exception as e:
        logger.error(f"Currency crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, 
            "error": str(e), 
            "data": None
        })
