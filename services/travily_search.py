"""
Service: Tavily AI Search
Singh Ji AI Ultra v8.3
"""
import httpx
from core.config import TAVILY_API_KEY

TAVILY_URL = "https://api.tavily.com/search"


async def search(query: str, max_results: int = 5) -> list:
    """
    Tavily AI से असली सर्च नतीजे लाएँ।
    Return: [{"title": ..., "url": ..., "content": ...}, ...]
    """
    if not TAVILY_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                TAVILY_URL,
                json={
                    "api_key": TAVILY_API_KEY,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                },
            )
            data = resp.json()
            results = data.get("results", [])
            return [
                {
                    "title": r.get("title", "No title"),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:200],
                }
                for r in results[:max_results]
            ]
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []
async def search_tavily(query: str, max_results: int = 5) -> list:
    return await search(query, max_results)
