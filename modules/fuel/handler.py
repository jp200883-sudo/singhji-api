#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Fuel Price Module
Petrol, Diesel, CNG, LPG rates for Indian cities
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# Fallback fuel rates (approximate)
FALLBACK_FUEL = {
    "petrol": 105.50,
    "diesel": 92.30,
    "cng": 82.00,
    "lpg": 950.00,
    "unit": "per litre (petrol/diesel/cng), per 14.2kg cylinder (lpg)",
    "currency": "INR",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "source": "Fallback Data"
}

# City-specific base rates (approximate)
CITY_BASE_RATES = {
    "delhi": {"petrol": 105.50, "diesel": 92.30, "cng": 82.00, "lpg": 950.00},
    "mumbai": {"petrol": 111.20, "diesel": 97.80, "cng": 85.00, "lpg": 980.00},
    "kolkata": {"petrol": 108.40, "diesel": 94.50, "cng": 83.50, "lpg": 965.00},
    "chennai": {"petrol": 109.80, "diesel": 95.20, "cng": 84.00, "lpg": 970.00},
    "bangalore": {"petrol": 110.10, "diesel": 95.80, "cng": 84.50, "lpg": 975.00},
    "hyderabad": {"petrol": 107.90, "diesel": 93.40, "cng": 83.00, "lpg": 960.00},
    "ahmedabad": {"petrol": 106.20, "diesel": 92.80, "cng": 81.50, "lpg": 955.00},
    "pune": {"petrol": 110.50, "diesel": 96.00, "cng": 84.80, "lpg": 978.00},
    "jaipur": {"petrol": 108.00, "diesel": 93.50, "cng": 82.50, "lpg": 958.00},
    "lucknow": {"petrol": 106.80, "diesel": 92.90, "cng": 82.20, "lpg": 952.00},
    "kanpur": {"petrol": 106.50, "diesel": 92.60, "cng": 82.10, "lpg": 951.00},
    "nagpur": {"petrol": 107.20, "diesel": 93.10, "cng": 82.80, "lpg": 956.00},
    "indore": {"petrol": 107.50, "diesel": 93.30, "cng": 82.90, "lpg": 957.00},
    "patna": {"petrol": 108.60, "diesel": 94.20, "cng": 83.20, "lpg": 962.00},
    "bhopal": {"petrol": 107.80, "diesel": 93.50, "cng": 82.70, "lpg": 955.00}
}

FUEL_TYPES = ["petrol", "diesel", "cng", "lpg"]
FUEL_NAMES_HI = {"petrol": "पेट्रोल", "diesel": "डीजल", "cng": "सीएनजी", "lpg": "एलपीजी"}


class FuelHandler:
    """Fuel price handler for Singh Ji AI Ultra"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 1800
        self.last_fetch = {}

    def _get_cached(self, key: str) -> Dict:
        if key in self.cache and key in self.last_fetch:
            if (datetime.now() - self.last_fetch[key]).seconds < self.cache_duration:
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data: Dict):
        self.cache[key] = data
        self.last_fetch[key] = datetime.now()

    def get_city_rates(self, city: str = "Delhi", fuel_type: str = "all") -> Dict:
        """
        Get fuel rates for a city

        Args:
            city: City name
            fuel_type: "petrol", "diesel", "cng", "lpg", or "all"
        """
        cache_key = f"{city.lower()}_{fuel_type}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Get base rates for city
        city_lower = city.lower()
        base_rates = CITY_BASE_RATES.get(city_lower, CITY_BASE_RATES["delhi"]).copy()

        # Add slight daily variation
        day_hash = hash(datetime.now().strftime("%Y%m%d")) % 20 - 10  # -10 to +10
        for key in base_rates:
            base_rates[key] = round(base_rates[key] + day_hash * 0.1, 2)

        result = {
            "city": city.title(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "currency": "INR",
            "unit": "per litre (petrol/diesel/cng), per 14.2kg cylinder (lpg)",
            "source": "Indian Oil Corporation (simulated)",
            "rates": base_rates
        }

        # Filter by fuel type
        if fuel_type != "all":
            if fuel_type in base_rates:
                result["rates"] = {fuel_type: base_rates[fuel_type]}
            else:
                result["rates"] = base_rates

        self._set_cache(cache_key, result)
        return result

    def compare_cities(self, cities: List[str] = None, fuel_type: str = "petrol") -> Dict:
        """Compare fuel prices across cities"""
        if cities is None:
            cities = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore"]

        comparison = []
        for city in cities:
            rates = self.get_city_rates(city, fuel_type)
            rate_value = rates.get("rates", {}).get(fuel_type, 0)
            comparison.append({
                "city": city,
                "rate": rate_value,
                "fuel_type": fuel_type
            })

        comparison.sort(key=lambda x: x["rate"])

        return {
            "status": "success",
            "fuel_type": fuel_type,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "comparison": comparison,
            "cheapest": comparison[0] if comparison else None,
            "costliest": comparison[-1] if comparison else None
        }

    def get_price_change(self, city: str = "Delhi", fuel_type: str = "petrol", days: int = 7) -> Dict:
        """Get price change over days"""
        changes = []
        base_rate = CITY_BASE_RATES.get(city.lower(), CITY_BASE_RATES["delhi"]).get(fuel_type, 0)

        for i in range(days):
            date = (datetime.now() - __import__("datetime").timedelta(days=i)).strftime("%Y-%m-%d")
            variation = (hash(date + city) % 40) - 20  # -20 to +20 paise
            rate = round(base_rate + variation * 0.01, 2)
            changes.append({
                "date": date,
                "rate": rate,
                "change": round(variation * 0.01, 2)
            })

        return {
            "status": "success",
            "city": city,
            "fuel_type": fuel_type,
            "days": days,
            "changes": changes,
            "trend": "up" if changes[0]["rate"] > changes[-1]["rate"] else "down"
        }

    def get_all_cities_summary(self, fuel_type: str = "petrol") -> Dict:
        """Get summary for all major cities"""
        all_cities = list(CITY_BASE_RATES.keys())
        summary = []

        for city in all_cities:
            rates = self.get_city_rates(city, fuel_type)
            summary.append({
                "city": city.title(),
                "rate": rates.get("rates", {}).get(fuel_type, 0)
            })

        summary.sort(key=lambda x: x["rate"])

        return {
            "status": "success",
            "fuel_type": fuel_type,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_cities": len(summary),
            "summary": summary,
            "cheapest": summary[0],
            "costliest": summary[-1]
        }

       def format_for_telegram(self, fuel_data: Dict, language: str = "hi") -> str:
        """Format fuel rates for Telegram"""
        city = fuel_data.get("city", "Delhi")
        date = fuel_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        rates = fuel_data.get("rates", {})

        if language == "hi":
            message = "⛽ *ईंधन के भाव* ⛽\n━━━━━━━━━━━━━━━\n📍 *" + city + "*\n📅 *" + date + "*\n\n"
            for fuel, rate in rates.items():
                name = FUEL_NAMES_HI.get(fuel, fuel.title())
                unit = "₹/kg" if fuel == "lpg" else "₹/litre"
                message += "🔹 *" + name + ":* ₹" + str(rate) + " " + unit + "\n"
            message += "\n📊 *स्रोत:* " + fuel_data.get('source', 'IOC') + "\n"
            message += "━━━━━━━━━━━━━━━\n⚡ *Singh Ji AI Ultra v7.0*"
        else:
            message = "⛽ *Fuel Prices* ⛽\n━━━━━━━━━━━━━━━\n📍 *" + city + "*\n📅 *" + date + "*\n\n"
            for fuel, rate in rates.items():
                unit = "₹/kg" if fuel == "lpg" else "₹/litre"
                message += "🔹 *" + fuel.title() + ":* ₹" + str(rate) + " " + unit + "\n"
            message += "\n📊 *Source:* " + fuel_data.get('source', 'IOC') + "\n"
            message += "━━━━━━━━━━━━━━━\n⚡ *Singh Ji AI Ultra v7.0*"

        return message
            message += "━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"
        else:
            message = f"⛽ *Fuel Prices* ⛽
━━━━━━━━━━━━━━━
📍 *{city}*
📅 *{date}*

"
            for fuel, rate in rates.items():
                unit = "₹/kg" if fuel == "lpg" else "₹/litre"
                message += f"🔹 *{fuel.title()}:* ₹{rate} {unit}
"
            message += f"
📊 *Source:* {fuel_data.get('source', 'IOC')}
"
            message += "━━━━━━━━━━━━━━━
⚡ *Singh Ji AI Ultra v7.0*"

        return message

    def format_comparison_telegram(self, comp_data: Dict, language: str = "hi") -> str:
        """Format comparison for Telegram"""
        fuel_type = comp_data.get("fuel_type", "petrol")
        fuel_name = FUEL_NAMES_HI.get(fuel_type, fuel_type.title())

        if language == "hi":
            message = f"🏙️ *{fuel_name} — शहरों में तुलना* 🏙️
📅 {comp_data.get('date')}

"
            for item in comp_data.get("comparison", []):
                message += f"📍 *{item['city']}* — ₹{item['rate']}
"
            cheapest = comp_data.get("cheapest")
            costliest = comp_data.get("costliest")
            if cheapest and costliest:
                message += f"
✅ सबसे सस्ता: {cheapest['city']} (₹{cheapest['rate']})
"
                message += f"❌ सबसे महंगा: {costliest['city']} (₹{costliest['rate']})
"
        else:
            message = f"🏙️ *{fuel_name} — City Comparison* 🏙️
📅 {comp_data.get('date')}

"
            for item in comp_data.get("comparison", []):
                message += f"📍 *{item['city']}* — ₹{item['rate']}
"
            cheapest = comp_data.get("cheapest")
            costliest = comp_data.get("costliest")
            if cheapest and costliest:
                message += f"
✅ Cheapest: {cheapest['city']} (₹{cheapest['rate']})
"
                message += f"❌ Costliest: {costliest['city']} (₹{costliest['rate']})
"

        message += "
⚡ *Singh Ji AI Ultra v7.0*"
        return message


# Singleton
fuel_handler = FuelHandler()

# Convenience functions
def get_rates(city: str = "Delhi", fuel_type: str = "all") -> Dict:
    return fuel_handler.get_city_rates(city, fuel_type)

def compare_cities(cities: List[str] = None, fuel_type: str = "petrol") -> Dict:
    return fuel_handler.compare_cities(cities, fuel_type)

def get_price_change(city: str = "Delhi", fuel_type: str = "petrol", days: int = 7) -> Dict:
    return fuel_handler.get_price_change(city, fuel_type, days)

def get_all_summary(fuel_type: str = "petrol") -> Dict:
    return fuel_handler.get_all_cities_summary(fuel_type)

def format_telegram(fuel_data: Dict, language: str = "hi") -> str:
    return fuel_handler.format_for_telegram(fuel_data, language)

def format_comparison_telegram(comp_data: Dict, language: str = "hi") -> str:
    return fuel_handler.format_comparison_telegram(comp_data, language)


# FastAPI handler for dynamic router
async def handler(request):
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)

        city = body.get("city") or params.get("city", "Delhi")
        fuel_type = body.get("fuel_type") or params.get("fuel_type", "all")
        action = body.get("action") or params.get("action", "get_rates")
        language = body.get("language") or params.get("language", "hi")
        days = int(body.get("days") or params.get("days", 7))

        if action == "get_rates":
            result = get_rates(city, fuel_type)
        elif action == "compare":
            cities = (body.get("cities") or params.get("cities", "")).split(",")
            cities = [c.strip() for c in cities if c.strip()] or None
            result = compare_cities(cities, fuel_type)
        elif action == "change":
            result = get_price_change(city, fuel_type, days)
        elif action == "all_summary":
            result = get_all_summary(fuel_type)
        elif action == "telegram":
            fuel_data = get_rates(city, fuel_type)
            result = {"status": "success", "message": format_telegram(fuel_data, language)}
        else:
            result = get_rates(city, fuel_type)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("🧪 Testing Fuel Handler...")
    result = get_rates("Delhi")
    print(f"Delhi Petrol: ₹{result['rates']['petrol']}")
    print(format_telegram(result, "hi"))
