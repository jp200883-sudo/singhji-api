"""
📰 SINGH JI AI — NEWS MODULE v2.0 (POLISHED)
Superior: Multi-source, Cached, Summarized, Trending, Indian Focus
Sources: NewsAPI, GNews, CurrentsAPI, Groq Summary
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/news", tags=["News"])

# ─── CONFIG ───
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

CACHE_TTL = 180  # 3 min for news
REQUEST_TIMEOUT = 12.0
MAX_RETRIES = 3

_news_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(source: str, query: str = "") -> str:
    return f"{source}:{query.lower().strip()}"


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    entry = _news_cache.get(key)
    if entry and (datetime.utcnow() - entry["ts"]).total_seconds() < CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: Dict[str, Any]) -> None:
    _news_cache[key] = {"data": data, "ts": datetime.utcnow()}


# ─── RETRY DECORATOR ───
def async_retry(max_retries: int = MAX_RETRIES, delay: float = 1.0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__}: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(delay * attempt)
            raise last_exc
        return wrapper
    return decorator

def _is_hindi_text(text: str, threshold: float = 0.3) -> bool:
    if not text:
        return False
    devanagari = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    letters = sum(1 for ch in text if ch.isalpha())
    return letters > 0 and (devanagari / letters) >= threshold
# ─── SOURCE 1: NEWSDATA.IO ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_newsdata(query: str = "", category: str = "", country: str = "in") -> List[Dict[str, Any]]:
    if not NEWSDATA_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
       url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country={country}&language=hi"
        if query:
            url += f"&q={quote(query)}"
        if category:
            url += f"&category={category}"

        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        results = [r for r in results if _is_hindi_text(r.get("title", ""))]
        return [
            {
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "url": r.get("link", ""),
                "source": r.get("source_id", "Unknown"),
                "published": r.get("pubDate", ""),
                "image": r.get("image_url", ""),
                "category": r.get("category", ["general"]),
            }
            for r in results[:10]
        ]


# ─── SOURCE 2: GNEWS ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_gnews(query: str = "", lang: str = "en", country: str = "in") -> List[Dict[str, Any]]:
    if not GNEWS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        url = f"https://gnews.io/api/v4/top-headlines?apikey={GNEWS_API_KEY}&country={country}&lang={lang}&max=10"
        if query:
            url = f"https://gnews.io/api/v4/search?apikey={GNEWS_API_KEY}&q={quote(query)}&lang={lang}&country={country}&max=10"

        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "published": a.get("publishedAt", ""),
                "image": a.get("image", ""),
                "category": ["general"],
            }
            for a in data.get("articles", [])
        ]


# ─── SOURCE 3: CURRENTSAPI ───
@async_retry(max_retries=2, delay=1.0)
async def _fetch_currents(query: str = "") -> List[Dict[str, Any]]:
    if not CURRENTS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        url = f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}&language=en"
        if query:
            url = f"https://api.currentsapi.services/v1/search?apiKey={CURRENTS_API_KEY}&language=en&keywords={quote(query)}"

        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        return [
            {
                "title": n.get("title", ""),
                "description": n.get("description", ""),
                "url": n.get("url", ""),
                "source": n.get("author", "Unknown"),
                "published": n.get("published", ""),
                "image": n.get("image", "") or n.get("image_url", ""),
                "category": n.get("category", ["general"]),
            }
            for n in data.get("news", [])
        ]


# ─── AI SUMMARY (GROQ) ───
@async_retry(max_retries=2, delay=1.0)
async def _summarize_with_groq(news_items: List[Dict[str, Any]]) -> str:
    if not GROQ_API_KEY or len(news_items) < 3:
        return ""

    titles = " | ".join([n["title"] for n in news_items[:5]])
    prompt = f"Summarize these news headlines in 3 bullet points in Hinglish (Hindi+English mix): {titles}"

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.5,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


# ─── ROUTES ───
@router.get("/latest")
async def latest_news(query: str = "", category: str = "", country: str = "in"):
    """
    📰 Latest news from multiple sources.

    Query params:
    - query: Search keyword
    - category: business, entertainment, health, science, sports, technology
    - country: in, us, gb, etc.
    """
    logger.info(f"📰 News request: q={query}, cat={category}, country={country}")

    cache_key = _cache_key("latest", f"{query}:{category}:{country}")
    cached = _get_cached(cache_key)
    if cached:
        return JSONResponse({"cached": True, "data": cached})

    # Fetch from all sources in parallel
    tasks = [
        _fetch_newsdata(query, category, country),
        _fetch_gnews(query, "en", country),
        _fetch_currents(query),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_news = []
    source_counts = {}
    for i, result in enumerate(results):
        source_name = ["NewsData", "GNews", "Currents"][i]
        if isinstance(result, list):
            all_news.extend(result)
            source_counts[source_name] = len(result)
        else:
            logger.warning(f"📰 {source_name} failed: {result}")
            source_counts[source_name] = 0

    if not all_news:
        raise HTTPException(status_code=503, detail="❌ Koi news source available nahi hai. Thodi der baad try karo.")

    # Deduplicate by URL
    seen_urls = set()
    unique_news = []
    for n in all_news:
        url = n.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(n)

    # Sort by published date (newest first)
    unique_news.sort(key=lambda x: x.get("published", ""), reverse=True)

    # AI summary
    summary = await _summarize_with_groq(unique_news[:10])

    response_data = {
        "status": "success",
        "module": "news",
        "version": "2.0-polished",
        "total_articles": len(unique_news),
        "source_counts": source_counts,
        "summary": summary,
        "articles": unique_news[:20],
        "timestamp": datetime.utcnow().isoformat(),
    }

    _set_cached(cache_key, response_data)
    return JSONResponse({"cached": False, "data": response_data})


@router.get("/trending")
async def trending_topics():
    """📈 Trending topics based on latest news aggregation."""
    cache_key = _cache_key("trending", "")
    cached = _get_cached(cache_key)
    if cached:
        return JSONResponse({"cached": True, "data": cached})

    # Fetch latest without query to get trending
    data = await latest_news()
    articles = data.body.get("data", {}).get("articles", [])

    # Extract keywords (simple frequency)
    from collections import Counter
    words = []
    for a in articles:
        title = a.get("title", "").lower()
        words.extend([w for w in title.split() if len(w) > 4])

    trending = Counter(words).most_common(10)

    result = {
        "trending_keywords": [{"word": w, "count": c} for w, c in trending],
        "timestamp": datetime.utcnow().isoformat(),
    }
    _set_cached(cache_key, result)
    return JSONResponse({"cached": False, "data": result})


@router.get("/")
async def news_root():
    """News module info."""
    return JSONResponse({
        "module": "📰 News",
        "version": "2.0-polished",
        "sources": ["NewsData.io", "GNews", "CurrentsAPI"],
        "features": ["multi-source", "cached", "retry", "ai-summary", "trending"],
        "cache_ttl_seconds": CACHE_TTL,
    })


# Legacy handler
async def handler(request: Request):
    query = request.query_params.get("q", "")
    category = request.query_params.get("category", "")
    return await latest_news(query=query, category=category)
