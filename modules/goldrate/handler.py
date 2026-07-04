#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Gold/Silver Rate Module
Fetches today's gold, silver, platinum rates for Indian cities
"""

import requests
import json
import os
import re
from datetime import datetime
from typing import Dict, List

# API Keys
METAL_PRICE_API_KEY = os.getenv("METAL_PRICE_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# Fallback data for demo
FALLBACK_RATES = {
    "gold_24k": 72500,
    "gold_22k": 66500,
    "gold_18k": 54400,
    "silver": 95000,
    "platinum": 32000,
    "unit": "per 10 grams",
    "currency": "INR",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "source": "Fallback Data"
}

# Major Indian cities
CITIES = [
    "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore",
    "Hyderabad", "Ahmedabad", "Pune", "Jaipur", "Lucknow",
    "Kanpur", "Nagpur", "Indore", "Patna", "Bhopal",
    "Ludhiana", "Agra", "Varanasi", "Allahabad", "Ranchi"
]

# City variations for search
CITY_ALIASES = {
    "delhi": ["delhi", "new delhi", "noida", "gurgaon", "faridabad", "ghaziabad"],
    "mumbai": ["mumbai", "thane", "navi mumbai", "pune"],
    "kolkata": ["kolkata", "howrah"],
    "chennai": ["chennai", "madras"],
    "bangalore": ["bangalore", "bengaluru"],
    "hyderabad": ["hyderabad", "secunderabad"],
    "kanpur": ["kanpur", "unnao"],
    "lucknow": ["lucknow", "barabanki"]
}


class GoldRateHandler:
    """Gold/Silver rate handler for Singh Ji AI Ultra"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 1800  # 30 minutes
        self.last_fetch = {}

    def _get_cached(self, key: str) -> Dict:
        if key in self.cache and key in self.last_fetch:
            if (datetime.now() - self.last_fetch[key]).seconds < self.cache_duration:
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data: Dict):
        self.cache[key] = data
        self.last_fetch[key] = datetime.now()

    def fetch_from_metalpriceapi(self) -> Dict:
        """Fetch from metalpriceapi.com"""
        if not METAL_PRICE_API_KEY:
            return {}
        try:
            url = f"https://metals-api.com/api/latest"
            params = {
                "access_key": METAL_PRICE_API_KEY,
                "base": "INR",
                "symbols": "XAU,XAG,XPT"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("success"):
                rates = data.get("rates", {})
                return {
                    "gold_24k": round(rates.get("XAU", 0) * 10, 2),  # per 10g
                    "silver": round(rates.get("XAG", 0) * 1000, 2),   # per kg
                    "platinum": round(rates.get("XPT", 0) * 10, 2),
                    "unit": "per 10 grams (gold/platinum), per kg (silver)",
                    "currency": "INR",
                    "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "source": "MetalPriceAPI"
                }
            return {}
        except Exception as e:
            print(f"[GoldRate] MetalPriceAPI Error: {e}")
            return {}

    def fetch_from_rapidapi(self) -> Dict:
        """Fetch from RapidAPI gold rate"""
        if not RAPIDAPI_KEY:
            return {}
        try:
            url = "https://gold-rate-india.p.rapidapi.com/api/get-gold-rate"
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "gold-rate-india.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                return {
                    "gold_22k": float(item.get("rate_22k", 0)),
                    "gold_24k": float(item.get("rate_24k", 0)),
                    "silver": float(item.get("silver_rate", 0)),
                    "unit": "per 10 grams",
                    "currency": "INR",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "RapidAPI"
                }
            return {}
        except Exception as e:
            print(f"[GoldRate] RapidAPI Error: {e}")
            return {}

    def get_rates(self, city: str = "India", purity: str = "all") -> Dict:
        """
        Get gold/silver rates

        Args:
            city: City name (Delhi, Mumbai, etc.) or "India" for national average
            purity: "24k", "22k", "18k", "silver", "platinum", or "all"

        Returns:
            Dict with rates data
        """
        cache_key = f"{city.lower()}_{purity}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Try APIs
        result = self.fetch_from_metalpriceapi()
        if not result:
            result = self.fetch_from_rapidapi()

        # Fallback
        if not result:
            result = FALLBACK_RATES.copy()
            result["city"] = city

        # Calculate purity rates if not present
        if "gold_24k" in result and "gold_22k" not in result:
            result["gold_22k"] = round(result["gold_24k"] * 0.916, 2)
        if "gold_24k" in result and "gold_18k" not in result:
            result["gold_18k"] = round(result["gold_24k"] * 0.75, 2)

        # City-specific adjustment (simulated)
        city_lower = city.lower()
        if city_lower != "india":
            # Small variation by city
            variation = hash(city_lower) % 500 - 250  # -250 to +250
            for key in ["gold_24k", "gold_22k", "gold_18k", "silver"]:
                if key in result:
                    result[key] = round(result[key] + variation, 2)
            result["city"] = city.title()
        else:
            result["city"] = "India (National Average)"

        # Filter by purity if requested
        if purity != "all":
            purity_key = f"gold_{purity}" if purity in ["24k", "22k", "18k"] else purity
            filtered = {k: v for k, v in result.items() if purity_key in k or k in ["unit", "currency", "date", "city", "source"]}
            result = filtered

        self._set_cache(cache_key, result)
        return result

    def compare_cities(self, cities: List[str] = None) -> Dict:
        """Compare gold rates across cities"""
        if cities is None:
            cities = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore"]

        comparison = []
        for city in cities:
            rates = self.get_rates(city, "24k")
            comparison.append({
                "city": city,
                "gold_24k": rates.get("gold_24k", 0),
                "gold_22k": rates.get("gold_22k", 0),
                "silver": rates.get("silver", 0)
            })

        # Sort by gold_24k price
        comparison.sort(key=lambda x: x["gold_24k"])

        return {
            "status": "success",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "comparison": comparison,
            "cheapest": comparison[0]["city"] if comparison else None,
            "costliest": comparison[-1]["city"] if comparison else None
        }

    def get_historical(self, days: int = 7) -> Dict:
        """Get historical gold rates (simulated)"""
        historical = []
        base_rate = FALLBACK_RATES["gold_24k"]

        for i in range(days):
            date = (datetime.now() - __import__("datetime").timedelta(days=i)).strftime("%Y-%m-%d")
            # Random variation
            variation = (hash(date) % 1000) - 500
            rate = round(base_rate + variation, 2)
            historical.append({
                "date": date,
                "gold_24k": rate,
                "gold_22k": round(rate * 0.916, 2),
                "silver": round(FALLBACK_RATES["silver"] + variation * 0.5, 2)
            })

        return {
            "status": "success",
            "days": days,
            "historical": historical,
            "trend": "up" if historical[0]["gold_24k"] > historical[-1]["gold_24k"] else "down"
        }

    def format_for_telegram(self, rates_data: Dict, language: str = "hi") -> str:
        """Format rates for Telegram"""
        city = rates_data.get("city", "India")
        date = rates_data.get("date", datetime.now().strftime("%Y-%m-%d"))

        if language == "hi":
            message = f"""🪙 *सोना-चांदी भाव* 🪙
━━━━━━━━━━━━━━━
📍 *{city}*
📅 *{date}*

💰 *सोना (24K):* ₹{rates_data.get('gold_24k', 'N/A'):,}
💰 *सोना (22K):* ₹{rates_data.get('gold_22k', 'N/A'):,}
💰 *सोना (18K):* ₹{rates_data.get('gold_18k', 'N/A'):,}

🥈 *चांदी:* ₹{rates_data.get('silver', 'N/A'):,}/kg

💎 *प्लैटिनम:* ₹{rates_data.get('platinum', 'N/A'):,}

📊 *यूनिट:* {rates_data.get('unit', 'per 10 grams')}

━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"""
        else:
            message = f"""🪙 *Gold & Silver Rates* 🪙
━━━━━━━━━━━━━━━
📍 *{city}*
📅 *{date}*

💰 *Gold (24K):* ₹{rates_data.get('gold_24k', 'N/A'):,}
💰 *Gold (22K):* ₹{rates_data.get('gold_22k', 'N/A'):,}
💰 *Gold (18K):* ₹{rates_data.get('gold_18k', 'N/A'):,}

🥈 *Silver:* ₹{rates_data.get('silver', 'N/A'):,}/kg

💎 *Platinum:* ₹{rates_data.get('platinum', 'N/A'):,}

📊 *Unit:* {rates_data.get('unit', 'per 10 grams')}

━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"""

        return message

    def format_comparison_telegram(self, comp_data: Dict, language: str = "hi") -> str:
        """Format city comparison for Telegram"""
        if language == "hi":
            message = f"🏙️ *शहरों में तुलना* 🏙️
📅 {comp_data.get('date')}

"
            for item in comp_data.get("comparison", []):
                message += f"📍 *{item['city']}*
"
                message += f"   24K: ₹{item['gold_24k']:,}
"
                message += f"   22K: ₹{item['gold_22k']:,}

"
            message += f"✅ सबसे सस्ता: {comp_data.get('cheapest')}
"
            message += f"❌ सबसे महंगा: {comp_data.get('costliest')}
"
        else:
            message = f"🏙️ *City Comparison* 🏙️
📅 {comp_data.get('date')}

"
            for item in comp_data.get("comparison", []):
                message += f"📍 *{item['city']}*
"
                message += f"   24K: ₹{item['gold_24k']:,}
"
                message += f"   22K: ₹{item['gold_22k']:,}

"
            message += f"✅ Cheapest: {comp_data.get('cheapest')}
"
            message += f"❌ Costliest: {comp_data.get('costliest')}
"

        message += "
⚡ *Singh Ji AI Ultra v7.0*"
        return message


# Singleton
goldrate_handler = GoldRateHandler()

# Convenience functions
def get_rates(city: str = "India", purity: str = "all") -> Dict:
    return goldrate_handler.get_rates(city, purity)

def compare_cities(cities: List[str] = None) -> Dict:
    return goldrate_handler.compare_cities(cities)

def get_historical(days: int = 7) -> Dict:
    return goldrate_handler.get_historical(days)

def format_telegram(rates_data: Dict, language: str = "hi") -> str:
    return goldrate_handler.format_for_telegram(rates_data, language)

def format_comparison_telegram(comp_data: Dict, language: str = "hi") -> str:
    return goldrate_handler.format_comparison_telegram(comp_data, language)


# FastAPI handler for dynamic router
async def handler(request):
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)

        city = body.get("city") or params.get("city", "India")
        purity = body.get("purity") or params.get("purity", "all")
        action = body.get("action") or params.get("action", "get_rates")
        language = body.get("language") or params.get("language", "hi")

        if action == "get_rates":
            result = get_rates(city, purity)
        elif action == "compare":
            cities = (body.get("cities") or params.get("cities", "")).split(",")
            cities = [c.strip() for c in cities if c.strip()] or None
            result = compare_cities(cities)
        elif action == "historical":
            days = int(body.get("days") or params.get("days", 7))
            result = get_historical(days)
        elif action == "telegram":
            rates_data = get_rates(city, purity)
            result = {"status": "success", "message": format_telegram(rates_data, language)}
        else:
            result = get_rates(city, purity)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("🧪 Testing Gold Rate Handler...")
    result = get_rates("Delhi")
    print(f"Gold 24K Delhi: ₹{result.get('gold_24k')}")
    print(format_telegram(result, "hi"))
