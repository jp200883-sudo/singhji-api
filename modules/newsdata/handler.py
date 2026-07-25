"""
═══════════════════════════════════════════════════════════════
  📰 सिंह जी AI अल्ट्रा v8.0 — न्यूज़ / समाचार मॉड्यूल
  फाइल: modules/news.py
  फीचर्स: CurrentsAPI → NewsData → GNews → Fallback,
          Async, Cache, TTS-ready, Supabase logging
  बदलाव (इस पैच में):
    - router prefix "/news" से "/api/news" किया गया, ताकि पुराने
      OpenAPI schema (/api/news/latest, /api/news/schedule/start)
      से टकराव न हो
    - "/api/news/latest" रूट जोड़ा गया (पुराने schema में मौजूद था,
      पर router में missing था — इसी वजह से 404 आ रहा था)
═══════════════════════════════════════════════════════════════
"""

import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger("singhji.news")

# ==== कॉन्फिगरेशन ====
NEWS_APIS = {
    "currents": {
        "url": "https://api.currentsapi.services/v1/search",
        "key_env": "CURRENTS_API_KEY",
        "priority": 1
    },
    "newsdata": {
        "url": "https://newsdata.io/api/1/news",
        "key_env": "NEWSDATA_API_KEY",
        "priority": 2
    },
    "gnews": {
        "url": "https://gnews.io/api/v4/search",
        "key_env": "GNEWS_API_KEY",
        "priority": 3
    }
}

DEFAULT_KEYWORDS = {
    "hi": "भारत",
    "en": "India",
    "ur": "پاکستان",
    "bn": "বাংলাদেশ"
}

POPULAR_TOPICS = [
    "technology", "sports", "business", "entertainment",
    "health", "science", "politics", "world"
]


@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    image: str
    published: str
    source: str
    category: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NewsResponse:
    keywords: str
    count: int
    source: str
    articles: List[Dict[str, Any]]
    tts: str
    timestamp: str
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keywords": self.keywords,
            "count": self.count,
            "source": self.source,
            "articles": self.articles,
            "tts": self.tts,
            "timestamp": self.timestamp,
            "cached": self.cached
        }


class SinghJiNews:
    """सिंह जी समाचार इंजन — मल्टी-API async fallback"""

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 600  # 10 मिनट

    async def _get_cache(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["time"] < timedelta(seconds=self.cache_ttl):
                logger.info(f"💾 न्यूज़ कैश हिट: {key}")
                return entry["data"]
            del self.cache[key]
        return None

    async def _save_cache(self, key: str, data: Dict):
        self.cache[key] = {"data": data, "time": datetime.now()}

    async def _fetch_currents(self, keywords: str, lang: str, num: int) -> Optional[List[NewsArticle]]:
        key = os.getenv(NEWS_APIS["currents"]["key_env"])
        if not key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["currents"]["url"],
                    params={"keywords": keywords, "language": lang, "apiKey": key}
                )
            if resp.status_code != 200:
                logger.warning(f"⚠️ CurrentsAPI HTTP {resp.status_code}")
                return None
            data = resp.json()
            if data.get("status") != "ok" or not data.get("news"):
                return None
            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("url", ""),
                    image=a.get("image", "") or a.get("image_url", ""),
                    published=a.get("published", ""),
                    source=a.get("author", "CurrentsAPI")
                ) for a in data["news"][:num]
            ]
            logger.info(f"✅ CurrentsAPI: {len(articles)} खबरें मिलीं")
            return articles
        except Exception as e:
            logger.error(f"💥 CurrentsAPI fail: {e}")
            return None

    async def _fetch_newsdata(self, keywords: str, lang: str, country: str, num: int) -> Optional[List[NewsArticle]]:
        key = os.getenv(NEWS_APIS["newsdata"]["key_env"])
        if not key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["newsdata"]["url"],
                    params={"apikey": key, "q": keywords, "language": lang, "country": country, "size": num}
                )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data.get("results"):
                return None
            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("link", ""),
                    image=a.get("image_url", ""),
                    published=a.get("pubDate", ""),
                    source=a.get("source_id", "NewsData")
                ) for a in data["results"][:num]
            ]
            logger.info(f"✅ NewsData: {len(articles)} खबरें मिलीं")
            return articles
        except Exception as e:
            logger.error(f"💥 NewsData fail: {e}")
            return None

    async def _fetch_gnews(self, keywords: str, lang: str, num: int) -> Optional[List[NewsArticle]]:
        key = os.getenv(NEWS_APIS["gnews"]["key_env"])
        if not key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["gnews"]["url"],
                    params={"q": keywords, "lang": lang, "max": num, "apikey": key}
                )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data.get("articles"):
                return None
            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("url", ""),
                    image=a.get("image", ""),
                    published=a.get("publishedAt", ""),
                    source=a.get("source", {}).get("name", "GNews")
                ) for a in data["articles"][:num]
            ]
            logger.info(f"✅ GNews: {len(articles)} खबरें मिलीं")
            return articles
        except Exception as e:
            logger.error(f"💥 GNews fail: {e}")
            return None

    async def _fallback_articles(self, keywords: str) -> List[NewsArticle]:
        return [NewsArticle(
            title=f"'{keywords}' से जुड़ी कोई खबर नहीं मिली",
            description="सभी न्यूज़ APIs फेल हो गए या कोटा खत्म हो गया। कृपया बाद में कोशिश करें।",
            url="https://news.google.com",
            image="",
            published=datetime.now().isoformat(),
            source="Fallback"
        )]

    def _generate_tts(self, keywords: str, articles: List[NewsArticle]) -> str:
        tts = f"समाचार अपडेट। {keywords} से जुड़ी {len(articles)} खबरें मिलीं।"
        if articles and articles[0].title:
            tts += f" पहली खबर: {articles[0].title[:100]}..."
        return tts

    async def get_news(self, keywords: str, num: int = 5,
                        country: str = "in", lang: str = "hi") -> NewsResponse:
        keywords = keywords.strip() or DEFAULT_KEYWORDS.get(lang, "India")
        num = min(int(num), 10)
        country = (country or "in").strip().lower()
        lang = (lang or "hi").strip().lower()

        cache_key = f"{keywords}_{lang}_{country}_{num}"
        cached = await self._get_cache(cache_key)
        if cached:
            return NewsResponse(
                keywords=keywords, count=cached["count"],
                source=f"{cached['source']} (cache)", articles=cached["articles"],
                tts=cached["tts"], timestamp=datetime.now().isoformat(), cached=True
            )

        articles = await self._fetch_currents(keywords, lang, num)
        source_used = "currentsapi.services" if articles else None

        if not articles:
            articles = await self._fetch_newsdata(keywords, lang, country, num)
            source_used = "newsdata.io" if articles else None

        if not articles:
            articles = await self._fetch_gnews(keywords, lang, num)
            source_used = "gnews.io" if articles else None

        if not articles:
            articles = await self._fallback_articles(keywords)
            source_used = "fallback"

        tts = self._generate_tts(keywords, articles)
        articles_dict = [a.to_dict() for a in articles]

        response = NewsResponse(
            keywords=keywords, count=len(articles), source=source_used,
            articles=articles_dict, tts=tts, timestamp=datetime.now().isoformat(), cached=False
        )

        await self._save_cache(cache_key, {
            "count": len(articles), "source": source_used,
            "articles": articles_dict, "tts": tts
        })
        return response


# ==== सिंगलटन — scheduler और अन्य मॉड्यूल यहीं से import करेंगे ====
singhji_news = SinghJiNews()


# ==== फास्टएपीआई राउटर — prefix अब /api/news (पहले /news था) ====
router = APIRouter(prefix="/api/news", tags=["📰 समाचार"])


@router.get("/latest")
async def news_latest(source: str = "currents", num: int = 5, lang: str = "hi", country: str = "in"):
    """
    📰 पुराने OpenAPI schema (/api/news/latest) के साथ compatible रूट।
    `source` पैरामीटर सिर्फ़ लॉगिंग के लिए रखा है — असली fallback chain
    हमेशा currents → newsdata → gnews क्रम में ही चलती है।
    """
    result = await singhji_news.get_news(keywords="", num=num, country=country, lang=lang)
    return JSONResponse(content={
        "success": True,
        "data": result.to_dict(),
        "message": f"✅ {result.count} खबरें मिलीं — सोर्स: {result.source}"
    })


@router.get("/search")
async def news_search(keywords: str = "भारत", num: int = 5, country: str = "in", lang: str = "hi"):
    """📰 समाचार खोजो — Example: /api/news/search?keywords=technology&num=5"""
    try:
        result = await singhji_news.get_news(keywords, num, country, lang)
        return JSONResponse(content={
            "success": True, "error": None, "data": result.to_dict(),
            "message": f"✅ {result.count} खबरें मिलीं — सोर्स: {result.source}"
        })
    except Exception as e:
        logger.error(f"💥 News search fail: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None,
            "message": "❌ समाचार लाने में त्रुटि हुई, बाद में कोशिश करो"
        })


@router.get("/topics")
async def news_topics():
    """🔥 लोकप्रिय टॉपिक्स लिस्ट"""
    return JSONResponse(content={"success": True, "topics": POPULAR_TOPICS})


@router.get("/top")
async def news_top(country: str = "in", lang: str = "hi", num: int = 5):
    """🌟 टॉप हेडलाइन्स"""
    return await news_search(keywords="top", num=num, country=country, lang=lang)
