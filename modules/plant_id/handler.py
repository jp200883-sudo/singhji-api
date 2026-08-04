from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import requests
import time

router = APIRouter()

# ========== CONFIG ==========
PLANT_ID_API = os.getenv("PLANT_ID_API")
PLANT_ID_URL = os.getenv("PLANT_ID_URL", "https://api.plant.id/v2")

# ========== PYDANTIC MODELS ==========
class PlantIdentifyRequest(BaseModel):
    image: str
    action: Optional[str] = "identify"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PlantDiagnoseRequest(BaseModel):
    image: str

# ========== PLANT ID MODULE ==========
class PlantIDModule:
    def __init__(self):
        self.api_key = PLANT_ID_API
        self.base_url = PLANT_ID_URL.rstrip("/")
    
    def identify_plant(self, image_base64: str, latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        if not self.api_key:
            return self._mock_identify()
        
        try:
            params = {
                "api_key": self.api_key,
                "images": [image_base64],
                "modifiers": ["crops_fast", "similar_images"],
                "plant_language": "en",
                "plant_details": ["common_names", "url", "wiki_description", "taxonomy", "synonyms"]
            }
            
            if latitude and longitude:
                params["latitude"] = latitude
                params["longitude"] = longitude
            
            resp = requests.post(
                f"{self.base_url}/identify",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            
            suggestions = []
            for suggestion in data.get("suggestions", [])[:3]:
                plant = suggestion.get("plant_details", {})
                suggestions.append({
                    "name": suggestion.get("plant_name", "Unknown"),
                    "probability": round(suggestion.get("probability", 0) * 100, 2),
                    "common_names": plant.get("common_names", []),
                    "description": plant.get("wiki_description", {}).get("value", ""),
                    "wiki_url": plant.get("url", ""),
                    "taxonomy": plant.get("taxonomy", {}),
                    "similar_images": [img.get("url") for img in suggestion.get("similar_images", [])[:2]]
                })
            
            return {
                "success": True,
                "source": "Plant.id",
                "id": data.get("id"),
                "suggestions": suggestions,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Plant.id API failed: {str(e)}")
            return self._mock_identify()
    
    def diagnose_disease(self, image_base64: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._mock_diagnose()
        
        try:
            params = {
                "api_key": self.api_key,
                "images": [image_base64],
                "modifiers": ["crops_fast", "similar_images"],
                "disease_details": ["description", "treatment", "classification", "common_names", "cause"]
            }
            
            resp = requests.post(
                f"{self.base_url}/health_assessment",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            
            health = data.get("health_assessment", {})
            diseases = []
            for disease in health.get("diseases", [])[:3]:
                diseases.append({
                    "name": disease.get("name", "Unknown"),
                    "probability": round(disease.get("probability", 0) * 100, 2),
                    "description": disease.get("disease_details", {}).get("description", ""),
                    "treatment": disease.get("disease_details", {}).get("treatment", {}).get("biological", ["Consult agricultural expert"]),
                    "cause": disease.get("disease_details", {}).get("cause", "")
                })
            
            return {
                "success": True,
                "source": "Plant.id",
                "is_healthy": health.get("is_healthy", False),
                "health_probability": round(health.get("health_probability", 0) * 100, 2),
                "diseases": diseases,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Plant.id diagnose failed: {str(e)}")
            return self._mock_diagnose()
    
    def _mock_identify(self) -> Dict[str, Any]:
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "id": "mock-123",
            "suggestions": [
                {
                    "name": "Triticum aestivum",
                    "probability": 95.5,
                    "common_names": ["Wheat", "Gehun"],
                    "description": "Wheat is a grass widely cultivated for its seed, a cereal grain which is a worldwide staple food.",
                    "wiki_url": "https://en.wikipedia.org/wiki/Wheat",
                    "taxonomy": {"kingdom": "Plantae", "family": "Poaceae"},
                    "similar_images": []
                }
            ],
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _mock_diagnose(self) -> Dict[str, Any]:
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "is_healthy": False,
            "health_probability": 30.0,
            "diseases": [
                {
                    "name": "Leaf Rust",
                    "probability": 75.0,
                    "description": "A fungal disease causing orange-brown pustules on leaves.",
                    "treatment": ["Apply fungicide", "Remove infected leaves", "Improve air circulation"],
                    "cause": "Fungus Puccinia triticina"
                }
            ],
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "plant_id",
            "api_key_set": bool(self.api_key),
            "status": "✅ Ready" if self.api_key else "⚠️ Mock Mode"
        }

# ========== FASTAPI ENDPOINTS ==========
@router.get("/")
async def plant_id_root():
    p = PlantIDModule()
    return {
        "module": "plant_id",
        "status": "LIVE",
        "health": p.health_check()
    }

@router.get("/ping")
async def plant_id_ping():
    return {"status": "alive", "module": "plant_id"}

@router.post("/identify")
async def identify_plant(request: PlantIdentifyRequest):
    try:
        p = PlantIDModule()
        result = p.identify_plant(request.image, request.latitude, request.longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diagnose")
async def diagnose_plant(request: PlantDiagnoseRequest):
    try:
        p = PlantIDModule()
        result = p.diagnose_disease(request.image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
