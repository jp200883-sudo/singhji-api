# newsdata/handler.py
import os
import json
import requests
import time
from typing import Dict, Any, List

# ========== CONFIG ==========
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

# ========== NEWSDATA MODULE ==========
class NewsDataModule:
    def __init__(self):
        self.api_key = NEWSDATA_API_KEY
        self.base_url = "https://newsdata.io/api/1/news"
    
    def get_news(self, query: str = None, country: str = "in", category: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get news from NewsData.io or fallback to mock"""
        if not self.api_key:
            return self._mock_news(query, country, category, limit)
        
        try:
            params = {
                "apikey": self.api_key,
                "country": country,
                "language": "en,hi",
                "size": min(limit, 10)  # Free tier limit
            }
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            
            resp = requests.get(self.base_url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("status") != "success":
                return self._mock_news(query, country, category, limit)
            
            articles = []
            for article in data.get("results", []):
                articles.append({
                    "title": article.get("title", "No Title"),
                    "description": article.get("description", ""),
                    "link": article.get("link", ""),
                    "source": article.get("source_id", "Unknown"),
                    "pubDate": article.get("pubDate", ""),
                    "image": article.get("image_url", ""),
                    "category": article.get("category", ["general"])[0] if article.get("category") else "general"
                })
            
            return {
                "success": True,
                "source": "NewsData.io",
                "total": data.get("totalResults", 0),
                "articles": articles,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ NewsData API failed: {str(e)}")
            return self._mock_news(query, country, category, limit)
    
    def get_categories(self) -> List[str]:
        return ["business", "entertainment", "environment", "food", "health", "politics", "science", "sports", "technology", "top", "world"]
    
    def _mock_news(self, query: str = None, country: str = "in", category: str = None, limit: int = 10) -> Dict[str, Any]:
        """Fallback mock news"""
        mock_articles = [
            {"title": "PM Modi announces new scheme for farmers", "description": "Government launches Kisan Samridhi Yojana...", "link": "https://example.com/1", "source": "DD News", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "politics"},
            {"title": "ISRO successfully launches new satellite", "description": "PSLV-C56 carries advanced communication satellite...", "link": "https://example.com/2", "source": "ISRO", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "science"},
            {"title": "India wins cricket match against Australia", "description": "Virat Kohli scores century in thrilling victory...", "link": "https://example.com/3", "source": "BCCI", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "sports"},
            {"title": "New AI technology developed in Bangalore", "description": "IIT researchers create breakthrough AI model...", "link": "https://example.com/4", "source": "Tech India", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "technology"},
            {"title": "Monsoon arrives early in Kerala", "description": "IMD predicts above-normal rainfall this year...", "link": "https://example.com/5", "source": "IMD", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "environment"},
            {"title": "Stock market hits new high", "description": "Sensex crosses 80,000 mark for first time...", "link": "https://example.com/6", "source": "Economic Times", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "business"},
            {"title": "New health scheme for senior citizens", "description": "Ayushman Bharat expanded to cover elderly...", "link": "https://example.com/7", "source": "Health Ministry", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "health"},
            {"title": "Bollywood blockbuster breaks records", "description": "New movie earns 500 crore in first week...", "link": "https://example.com/8", "source": "Filmfare", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "entertainment"},
            {"title": "New education policy implemented", "description": "NEP 2020 rollout in all states by 2025...", "link": "https://example.com/9", "source": "Education Ministry", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "top"},
            {"title": "World leaders summit in Delhi", "description": "G20 follow-up meeting scheduled next month...", "link": "https://example.com/10", "source": "World News", "pubDate": time.strftime("%Y-%m-%d"), "image": "", "category": "world"}
        ]
        
        filtered = mock_articles
        if category:
            filtered = [a for a in filtered if a["category"] == category]
        if query:
            filtered = [a for a in filtered if query.lower() in a["title"].lower()]
        
        return {
            "success": True,
            "source": "Mock (API Failed)",
            "total": len(filtered[:limit]),
            "articles": filtered[:limit],
            "note": "Using mock data - API key missing or failed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "newsdata",
            "api_key_set": bool(self.api_key),
            "status": "✅ Ready" if self.api_key else "⚠️ Mock Mode"
        }


# ========== RENDER HANDLER ==========
def handler(request):
    if request.method == "GET":
        n = NewsDataModule()
        params = request.args if hasattr(request, 'args') else {}
        query = params.get("q")
        country = params.get("country", "in")
        category = params.get("category")
        limit = int(params.get("limit", 10))
        
        result = n.get_news(query, country, category, limit)
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
            result = NewsDataModule().get_news(
                body.get("q"),
                body.get("country", "in"),
                body.get("category"),
                body.get("limit", 10)
            )
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result, ensure_ascii=False)
            }
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    
    return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}


if __name__ == "__main__":
    n = NewsDataModule()
    print("🦁 SINGH JI AI ULTRA v7.0 — NewsData Module")
    print("Health:", n.health_check())
    print("\nTop News:")
    print(json.dumps(n.get_news(), indent=2, ensure_ascii=False))
    print("\nTech News:")
    print(json.dumps(n.get_news(category="technology"), indent=2, ensure_ascii=False))
