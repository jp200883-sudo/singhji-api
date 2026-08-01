"""
📰 सिंह जी AI अल्ट्रा — न्यूज़ मॉड्यूल (एकीकृत, final)
Sources: NewsData.io → GNews → CurrentsAPI (parallel fetch, dedup, cache, Hindi filter)
यह main.py की चारों जगह डुप्लिकेट news code की जगह अब यही एक मॉड्यूल इस्तेमाल होता है।
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from collections import Counter

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger("singhji.news")
router = APIRouter(prefix="/api/news", tags=["📰 समाचार"])

# ─── CONFIG ───
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

CACHE_TTL = 180
REQUEST_TIMEOUT = 12.0

_news_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(query: str, category: str, country: str) -> str:
    return f"{query.lower().strip()}:{category}:{country}"


def _get_cached(key: str) -> Optional[Dict[str, Any]]:
    entry = _news_cache.get(key)
    if entry and (datetime.utcnow() - entry["ts"]).total_seconds() < CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: Dict[str, Any]) -> None:
    _news_cache[key] = {"data": data, "ts": datetime.utcnow()}


def _is_hindi_text(text: str, threshold: float = 0.3) -> bool:
    if not text:
        return False
    devanagari = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    letters = sum(1 for ch in text if ch.isalpha())
    return letters > 0 and (devanagari / letters) >= threshold


# ─── SOURCE 1: NEWSDATA.IO ───
async def _fetch_newsdata(query: str = "", category: str = "", country: str = "in") -> List[Dict[str, Any]]:
    if not NEWSDATA_API_KEY:
        return []
    try:
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
        return [
            {
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "url": r.get("link", ""),
                "source": r.get("source_id", "Unknown"),
                "published": r.get("pubDate", ""),
                "image": r.get("image_url", ""),
            }
            for r in results[:10]
        ]
    except Exception as e:
        logger.warning(f"[NEWS] NewsData fail: {e}")
        return []


# ─── SOURCE 2: GNEWS ───
async def _fetch_gnews(query: str = "", lang: str = "hi", country: str = "in") -> List[Dict[str, Any]]:
    if not GNEWS_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            if query:
                url = f"https://gnews.io/api/v4/search?apikey={GNEWS_API_KEY}&q={quote(query)}&lang={lang}&country={country}&max=10"
            else:
                url = f"https://gnews.io/api/v4/top-headlines?apikey={GNEWS_API_KEY}&country={country}&lang={lang}&max=10"
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
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        logger.warning(f"[NEWS] GNews fail: {e}")
        return []


# ─── SOURCE 3: CURRENTSAPI ───
async def _fetch_currents(query: str = "") -> List[Dict[str, Any]]:
    if not CURRENTS_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            if query:
                url = f"https://api.currentsapi.services/v1/search?apiKey={CURRENTS_API_KEY}&language=en&keywords={quote(query)}"
            else:
                url = f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}&language=en"
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
            }
            for n in data.get("news", [])
        ]
    except Exception as e:
        logger.warning(f"[NEWS] Currents fail: {e}")
        return []


# ─── SOURCE 4: TAVILY (WEB SEARCH — sabse bharosemand, jab dedicated news APIs fail/limit ho jayein) ───
_GENERIC_TITLE_PATTERNS = [
    "news in hindi", "breaking news", "live news", "superfast news",
    "news live", "top news", "latest news", "news today", "समाचार",
    "हिंदी न्यूज़", "हिन्दी समाचार", "ब्रेकिंग न्यूज़",
]


def _is_generic_title(title: str) -> bool:
    """Channel/homepage jaisi generic titles ko chhaanta hai (jaise 'India News In Hindi - ABP News')"""
    t = title.lower().strip()
    return any(p in t for p in _GENERIC_TITLE_PATTERNS) or len(t) < 15


async def _fetch_tavily(query: str = "") -> List[Dict[str, Any]]:
    if not TAVILY_API_KEY:
        return []
    try:
        today = datetime.utcnow().strftime("%d %B %Y")
        search_query = query if query else f"India specific news headlines {today}"
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": TAVILY_API_KEY,
                    "query": search_query,
                    "search_depth": "advanced",
                    "topic": "news",
                    "time_range": "day",
                    "max_results": 15,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        results = []
        for r in data.get("results", []):
            title = r.get("title", "")
            if not title or _is_generic_title(title):
                continue
            results.append({
                "title": title,
                "description": r.get("content", "")[:200],
                "url": r.get("url", ""),
                "source": "Tavily",
                "published": r.get("published_date", ""),
                "image": "",
            })
        return results
    except Exception as e:
        logger.warning(f"[NEWS] Tavily fail: {e}")
        return []


# ─── AI SUMMARY (GROQ) ───
async def _summarize_with_groq(news_items: List[Dict[str, Any]]) -> str:
    if not GROQ_API_KEY or len(news_items) < 3:
        return ""
    titles = " | ".join([n["title"] for n in news_items[:5]])
    prompt = f"इन हेडलाइंस को हिंदी में 3 बुलेट पॉइंट में summarize करो: {titles}"
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.5,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.warning(f"[NEWS] Groq summary fail: {e}")
        return ""


# ─── CORE: सबसे ऊपर वाली shared function — बाकी सब यही कॉल करेंगे ───
async def get_latest_news(query: str = "", category: str = "", country: str = "in",
                           num: int = 10, hindi_only: bool = False) -> Dict[str, Any]:
    cache_key = _cache_key(query, category, country)
    cached = _get_cached(cache_key)
    if cached:
        return {**cached, "cached": True}

    results = await asyncio.gather(
        _fetch_newsdata(query, category, country),
        _fetch_gnews(query, "hi", country),
        _fetch_currents(query),
        _fetch_tavily(query),
        return_exceptions=True,
    )

    all_news = []
    source_counts = {}
    for i, result in enumerate(results):
        name = ["NewsData", "GNews", "Currents", "Tavily"][i]
        if isinstance(result, list):
            all_news.extend(result)
            source_counts[name] = len(result)
        else:
            source_counts[name] = 0

    if hindi_only:
        all_news = [n for n in all_news if _is_hindi_text(n.get("title", ""))]

    seen_urls = set()
    unique_news = []
    for n in all_news:
        url = n.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(n)
    unique_news.sort(key=lambda x: x.get("published", ""), reverse=True)

    summary = await _summarize_with_groq(unique_news[:10])

    response_data = {
        "status": "success" if unique_news else "empty",
        "total_articles": len(unique_news),
        "source_counts": source_counts,
        "summary": summary,
        "articles": unique_news[:num],
        "timestamp": datetime.utcnow().isoformat(),
        "cached": False,
    }
    if unique_news:
        _set_cached(cache_key, response_data)
    return response_data


async def get_news_digest_text(count: int = 5, hindi_only: bool = True) -> str:
    """Telegram/Voice के लिए plain text digest — scheduler jobs और bot commands यही इस्तेमाल करें"""
    data = await get_latest_news(num=count, hindi_only=hindi_only)
    articles = data.get("articles", [])
    if not articles and hindi_only:
        # Hindi mein kuch nahi mila, English/mixed results se fallback (khaali se behtar)
        data = await get_latest_news(num=count, hindi_only=False)
        articles = data.get("articles", [])
    if not articles:
        return "अभी कोई खबर उपलब्ध नहीं है।"
    lines = []
    summary = data.get("summary", "")
    if summary:
        lines.append(summary.strip())
        lines.append("")
    for i, a in enumerate(articles[:count], 1):
        title = a.get("title", "बिना शीर्षक")
        lines.append(f"{i}. {title}")
    return "\n".join(lines)


# ─── ROUTES ───
@router.get("/latest")
async def news_latest(query: str = "", category: str = "", country: str = "in", num: int = 10):
    data = await get_latest_news(query=query, category=category, country=country, num=num)
    return JSONResponse({"success": True, "data": data})


@router.get("/search")
async def news_search(keywords: str = "भारत", num: int = 5, country: str = "in"):
    data = await get_latest_news(query=keywords, country=country, num=num)
    return JSONResponse({"success": True, "data": data})


@router.get("/trending")
async def trending_topics():
    data = await get_latest_news(num=20)
    words = []
    for a in data.get("articles", []):
        title = a.get("title", "").lower()
        words.extend([w for w in title.split() if len(w) > 4])
    trending = Counter(words).most_common(10)
    return JSONResponse({
        "trending_keywords": [{"word": w, "count": c} for w, c in trending],
        "timestamp": datetime.utcnow().isoformat(),
    })


@router.get("/")
async def news_root():
    return JSONResponse({
        "module": "📰 News",
        "version": "3.0-unified",
        "sources": ["NewsData.io", "GNews", "CurrentsAPI", "Tavily"],
        "features": ["multi-source", "cached", "hindi-filter", "ai-summary", "trending"],
        "cache_ttl_seconds": CACHE_TTL,
    })


# ─── legacy compat: modules/news/__init__.py इसे import करता है ───
async def handler(request):
    query = request.query_params.get("q", "") if hasattr(request, "query_params") else ""
    data = await get_latest_news(query=query)
    return JSONResponse({"success": True, "data": data})
