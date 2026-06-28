# modules/mandi.py — Singh Ji AI Ultra
import os
import requests
from fastapi import APIRouter

router = APIRouter()

MANDI_KEY = os.getenv("MANDI_API_KEY")

@router.get("/rates")
def mandi_rates(state: str = "Uttar Pradesh", commodity: str = None):
    """Mandi bhav — real-time rates"""
    if not MANDI_KEY:
        # Mock data for demo
        return {
            "status": "mock",
            "state": state,
            "commodity": commodity or "All",
            "rates": [
                {"commodity": "Gehu (Wheat)", "price": "2200/quintal", "market": "Kanpur", "date": "28-06-2026"},
                {"commodity": "Chawal (Rice)", "price": "3500/quintal", "market": "Lucknow", "date": "28-06-2026"},
                {"commodity": "Aloo (Potato)", "price": "800/quintal", "market": "Agra", "date": "28-06-2026"}
            ]
        }
    
    # Real API call (adjust based on your Mandi API provider)
    try:
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={MANDI_KEY}&format=json&filters[state]={state}"
        if commodity:
            url += f"&filters[commodity]={commodity}"
        
        res = requests.get(url, timeout=10)
        data = res.json()
        
        rates = []
        for record in data.get("records", []):
            rates.append({
                "commodity": record.get("commodity", "Unknown"),
                "market": record.get("market", "Unknown"),
                "price": f"{record.get('min_price', 'N/A')}-{record.get('max_price', 'N/A')}",
                "date": record.get("arrival_date", "Today")
            })
        
        return {"status": "live", "state": state, "count": len(rates), "rates": rates}
    except Exception as e:
        return {"error": str(e), "fallback": "mock"}
