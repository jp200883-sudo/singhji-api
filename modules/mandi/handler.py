# mandi/handler.py
import os
import json
import requests
import time
from typing import Dict, Any, List

# ========== CONFIG ==========
MANDI_API_KEY = os.getenv("MANDI_API_KEY")

# ========== MANDI MODULE ==========
class MandiModule:
    def __init__(self):
        self.api_key = MANDI_API_KEY
        # Agriwatch / data.gov.in style API
        self.base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    def get_mandi_rates(self, state: str = None, commodity: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get mandi rates from API or fallback to mock"""
        if not self.api_key:
            return self._mock_mandi(state, commodity, limit)
        
        try:
            # data.gov.in API format
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit
            }
            if state:
                params["filters[state]"] = state
            if commodity:
                params["filters[commodity]"] = commodity
            
            resp = requests.get(self.base_url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            records = []
            for record in data.get("records", []):
                records.append({
                    "state": record.get("state", "Unknown"),
                    "district": record.get("district", "Unknown"),
                    "market": record.get("market", "Unknown"),
                    "commodity": record.get("commodity", "Unknown"),
                    "variety": record.get("variety", "General"),
                    "min_price": record.get("min_price", "0"),
                    "max_price": record.get("max_price", "0"),
                    "modal_price": record.get("modal_price", "0"),
                    "date": record.get("arrival_date", time.strftime("%Y-%m-%d"))
                })
            
            return {
                "success": True,
                "source": "data.gov.in",
                "count": len(records),
                "records": records,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Mandi API failed: {str(e)}")
            return self._mock_mandi(state, commodity, limit)
    
    def get_commodity_list(self) -> List[str]:
        """List of supported commodities"""
        return [
            "Wheat", "Rice", "Maize", "Bajra", "Jowar",
            "Arhar (Tur)", "Moong", "Urad", "Masoor",
            "Groundnut", "Mustard", "Soyabean", "Sunflower",
            "Cotton", "Sugarcane", "Potato", "Onion", "Tomato"
        ]
    
    def get_state_list(self) -> List[str]:
        """List of states with mandi data"""
        return [
            "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh",
            "Rajasthan", "Gujarat", "Maharashtra", "Bihar",
            "West Bengal", "Karnataka", "Andhra Pradesh", "Telangana"
        ]
    
    def _mock_mandi(self, state: str = None, commodity: str = None, limit: int = 10) -> Dict[str, Any]:
        """Fallback mock mandi data"""
        mock_data = [
            {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana", "commodity": "Wheat", "variety": "PBW-343", "min_price": "2100", "max_price": "2300", "modal_price": "2200", "date": time.strftime("%Y-%m-%d")},
            {"state": "Haryana", "district": "Karnal", "market": "Karnal", "commodity": "Rice", "variety": "Basmati", "min_price": "3500", "max_price": "4000", "modal_price": "3750", "date": time.strftime("%Y-%m-%d")},
            {"state": "Uttar Pradesh", "district": "Agra", "market": "Agra", "commodity": "Potato", "variety": "Kufri Jyoti", "min_price": "800", "max_price": "1000", "modal_price": "900", "date": time.strftime("%Y-%m-%d")},
            {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore", "commodity": "Soyabean", "variety": "JS-335", "min_price": "4500", "max_price": "4800", "modal_price": "4650", "date": time.strftime("%Y-%m-%d")},
            {"state": "Rajasthan", "district": "Jaipur", "market": "Jaipur", "commodity": "Mustard", "variety": "Varuna", "min_price": "5200", "max_price": "5500", "modal_price": "5350", "date": time.strftime("%Y-%m-%d")},
            {"state": "Gujarat", "district": "Rajkot", "market": "Rajkot", "commodity": "Groundnut", "variety": "GJG-9", "min_price": "6000", "max_price": "6500", "modal_price": "6250", "date": time.strftime("%Y-%m-%d")},
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "min_price": "1200", "max_price": "1500", "modal_price": "1350", "date": time.strftime("%Y-%m-%d")},
            {"state": "Bihar", "district": "Patna", "market": "Patna", "commodity": "Maize", "variety": "HQPM-1", "min_price": "1800", "max_price": "2000", "modal_price": "1900", "date": time.strftime("%Y-%m-%d")},
            {"state": "Karnataka", "district": "Mandya", "market": "Mandya", "commodity": "Sugarcane", "variety": "CO-0238", "min_price": "3000", "max_price": "3200", "modal_price": "3100", "date": time.strftime("%Y-%m-%d")},
            {"state": "Andhra Pradesh", "district": "Guntur", "market": "Guntur", "commodity": "Cotton", "variety": "Bunny", "min_price": "7000", "max_price": "7500", "modal_price": "7250", "date": time.strftime("%Y-%m-%d")}
        ]
        
        # Filter
        filtered = mock_data
        if state:
            filtered = [r for r in filtered if r["state"].lower() == state.lower()]
        if commodity:
            filtered = [r for r in filtered if r["commodity"].lower() == commodity.lower()]
        
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "count": len(filtered[:limit]),
            "records": filtered[:limit],
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "mandi",
            "api_key_set": bool(self.api_key),
            "status": "✅ Ready" if self.api_key else "⚠️ Mock Mode"
        }


# ========== RENDER HANDLER ==========
def handler(request):
    if request.method == "GET":
        m = MandiModule()
        params = request.args if hasattr(request, 'args') else {}
        state = params.get("state")
        commodity = params.get("commodity")
        limit = int(params.get("limit", 10))
        
        result = m.get_mandi_rates(state, commodity, limit)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result, ensure_ascii=False)
        }
    
    elif request.method == "POST":
        try:
            body = json.loads(request.body) if hasattr(request, 'body') else request.json()
            state = body.get("state")
            commodity = body.get("commodity")
            limit = body.get("limit", 10)
            
            m = MandiModule()
            result = m.get_mandi_rates(state, commodity, limit)
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result, ensure_ascii=False)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    
    return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}


if __name__ == "__main__":
    m = MandiModule()
    print("🦁 SINGH JI AI ULTRA v7.0 — Mandi Module")
    print("Health:", m.health_check())
    print("\nAll Rates:")
    print(json.dumps(m.get_mandi_rates(), indent=2, ensure_ascii=False))
    print("\nWheat in Punjab:")
    print(json.dumps(m.get_mandi_rates(state="Punjab", commodity="Wheat"), indent=2, ensure_ascii=False))
