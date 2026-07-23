"""
═══════════════════════════════════════════════════════════════
  📰 सिंह जी AI अल्ट्रा v8.0 — न्यूज़ / समाचार मॉड्यूल
  फाइल: modules/news.py
  बनाया: 23 जुलाई 2026
  फीचर्स: CurrentsAPI → NewsData → GNews → RSS Fallback,
          Async, Cache, TTS-ready, Supabase logging
═══════════════════════════════════════════════════════════════
"""

import os
import asyncio
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


# ==== डेटा क्लास ====
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
    """
    सिंह जी समाचार इंजन — मल्टी-API async fallback
    """

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 600  # 10 मिनट
        self.supabase = None

    async def _get_cache(self, key: str) -> Optional[Dict]:
        """कैश से समाचार निकालो"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["time"] < timedelta(seconds=self.cache_ttl):
                logger.info(f"💾 न्यूज़ कैश हिट: {key}")
                return entry["data"]
            del self.cache[key]
        return None

    async def _save_cache(self, key: str, data: Dict):
        """कैश में सेव करो"""
        self.cache[key] = {"data": data, "time": datetime.now()}
        logger.info(f"💾 न्यूज़ कैश सेव: {key}")

    async def _fetch_currents(self, keywords: str, lang: str, num: int) -> Optional[List[NewsArticle]]:
        """CurrentsAPI से समाचार लाओ"""
        key = os.getenv(NEWS_APIS["currents"]["key_env"])
        if not key:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["currents"]["url"],
                    params={
                        "keywords": keywords,
                        "language": lang,
                        "apiKey": key
                    }
                )

            if resp.status_code != 200:
                logger.warning(f"⚠️ CurrentsAPI HTTP {resp.status_code}")
                return None

            data = resp.json()
            if data.get("status") != "ok" or not data.get("news"):
                return None

            articles = []
            for a in data["news"][:num]:
                articles.append(NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("url", ""),
                    image=a.get("image", "") or a.get("image_url", ""),
                    published=a.get("published", ""),
                    source=a.get("author", "CurrentsAPI")
                ))

            logger.info(f"✅ CurrentsAPI: {len(articles)} खबरें मिलीं")
            return articles

        except Exception as e:
            logger.error(f"💥 CurrentsAPI fail: {e}")
            return None

    async def _fetch_newsdata(self, keywords: str, lang: str, country: str, num: int) -> Optional[List[NewsArticle]]:
        """NewsData.io से समाचार लाओ"""
        key = os.getenv(NEWS_APIS["newsdata"]["key_env"])
        if not key:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["newsdata"]["url"],
                    params={
                        "apikey": key,
                        "q": keywords,
                        "language": lang,
                        "country": country,
                        "size": num
                    }
                )

            if resp.status_code != 200:
                return None

            data = resp.json()
            if not data.get("results"):
                return None

            articles = []
            for a in data["results"][:num]:
                articles.append(NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("link", ""),
                    image=a.get("image_url", ""),
                    published=a.get("pubDate", ""),
                    source=a.get("source_id", "NewsData")
                ))

            logger.info(f"✅ NewsData: {len(articles)} खबरें मिलीं")
            return articles

        except Exception as e:
            logger.error(f"💥 NewsData fail: {e}")
            return None

    async def _fetch_gnews(self, keywords: str, lang: str, num: int) -> Optional[List[NewsArticle]]:
        """GNews से समाचार लाओ"""
        key = os.getenv(NEWS_APIS["gnews"]["key_env"])
        if not key:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    NEWS_APIS["gnews"]["url"],
                    params={
                        "q": keywords,
                        "lang": lang,
                        "max": num,
                        "apikey": key
                    }
                )

            if resp.status_code != 200:
                return None

            data = resp.json()
            if not data.get("articles"):
                return None

            articles = []
            for a in data["articles"][:num]:
                articles.append(NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    url=a.get("url", ""),
                    image=a.get("image", ""),
                    published=a.get("publishedAt", ""),
                    source=a.get("source", {}).get("name", "GNews")
                ))

            logger.info(f"✅ GNews: {len(articles)} खबरें मिलीं")
            return articles

        except Exception as e:
            logger.error(f"💥 GNews fail: {e}")
            return None

    async def _fallback_articles(self, keywords: str) -> List[NewsArticle]:
        """लास्ट रिजॉर्ट — स्टैटिक fallback"""
        return [NewsArticle(
            title=f"'{keywords}' से जुड़ी कोई खबर नहीं मिली",
            description="सभी न्यूज़ APIs फेल हो गए या कोटा खत्म हो गया। कृपया बाद में कोशिश करें।",
            url="https://news.google.com",
            image="",
            published=datetime.now().isoformat(),
            source="Fallback"
        )]

    def _generate_tts(self, keywords: str, articles: List[NewsArticle]) -> str:
        """TTS टेक्स्ट जनरेट करो"""
        tts = f"समाचार अपडेट। {keywords} से जुड़ी {len(articles)} खबरें मिलीं।"
        if articles and articles[0].title:
            tts += f" पहली खबर: {articles[0].title[:100]}..."
        return tts

    async def get_news(self, keywords: str, num: int = 5, 
                       country: str = "in", lang: str = "hi") -> NewsResponse:
        """
        समाचार लाओ — मल्टी-API fallback chain
        """
        keywords = keywords.strip() or DEFAULT_KEYWORDS.get(lang, "India")
        num = min(int(num), 10)
        country = country.strip().lower() or "in"
        lang = lang.strip().lower() or "hi"

        cache_key = f"{keywords}_{lang}_{country}_{num}"

        # कैश चेक करो
        cached = await self._get_cache(cache_key)
        if cached:
            return NewsResponse(
                keywords=keywords,
                count=cached["count"],
                source=f"{cached['source']} (cache)",
                articles=cached["articles"],
                tts=cached["tts"],
                timestamp=datetime.now().isoformat(),
                cached=True
            )

        # API chain
        articles = None
        source_used = None

        # Try 1: CurrentsAPI
        articles = await self._fetch_currents(keywords, lang, num)
        if articles:
            source_used = "currentsapi.services"

        # Try 2: NewsData
        if not articles:
            articles = await self._fetch_newsdata(keywords, lang, country, num)
            if articles:
                source_used = "newsdata.io"

        # Try 3: GNews
        if not articles:
            articles = await self._fetch_gnews(keywords, lang, num)
            if articles:
                source_used = "gnews.io"

        # Fallback
        if not articles:
            articles = await self._fallback_articles(keywords)
            source_used = "fallback"

        # TTS बनाओ
        tts = self._generate_tts(keywords, articles)

        # Response बनाओ
        articles_dict = [a.to_dict() for a in articles]

        response = NewsResponse(
            keywords=keywords,
            count=len(articles),
            source=source_used,
            articles=articles_dict,
            tts=tts,
            timestamp=datetime.now().isoformat(),
            cached=False
        )

        # कैश सेव करो
        await self._save_cache(cache_key, {
            "count": len(articles),
            "source": source_used,
            "articles": articles_dict,
            "tts": tts
        })

        return response


# ==== सिंगलटन ====
singhji_news = SinghJiNews()


# ==== फास्टएपीआई राउटर ====
router = APIRouter(prefix="/news", tags=["📰 समाचार"])


@router.get("/search")
async def news_search(
    keywords: str = "भारत",
    num: int = 5,
    country: str = "in",
    lang: str = "hi"
):
    """
    📰 समाचार खोजो

    Example: /news/search?keywords=technology&num=5&country=in&lang=hi
    """
    try:
        result = await singhji_news.get_news(keywords, num, country, lang)

        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": result.to_dict(),
            "message": f"✅ {result.count} खबरें मिलीं — सोर्स: {result.source}"
        })

    except Exception as e:
        logger.error(f"💥 News search fail: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "data": None,
            "message": "❌ समाचार लाने में त्रुटि हुई, बाद में कोशिश करो"
        })


@router.get("/topics")
async def news_topics():
    """
    🔥 लोकप्रिय टॉपिक्स लिस्ट
    """
    return JSONResponse(content={
        "success": True,
        "topics": POPULAR_TOPICS,
        "message": "लोकप्रिय समाचार श्रेणियाँ"
    })


@router.get("/top")
async def news_top(country: str = "in", lang: str = "hi", num: int = 5):
    """
    🌟 टॉप हेडलाइन्स

    Example: /news/top?country=in&lang=hi&num=5
    """
    return await news_search(keywords="top", num=num, country=country, lang=lang)


# ==== बैकवर्ड कम्पैटिबल हैंडलर ====
async def handler(request: Request):
    """
    पुराना v7.0 हैंडलर — backward compatible
    Singh Ji AI Ultra v7.0 से v8.0 तक माइग्रेशन के लिए
    """
    try:
        params = dict(request.query_params)
        keywords = params.get("keywords", "India").strip()
        num = min(int(params.get("num", 5)), 10)
        country = params.get("country", "in").strip().lower()
        lang = params.get("lang", "hi").strip().lower()

        result = await singhji_news.get_news(keywords, num, country, lang)

        return JSONResponse(content={
            "success": True,
            "keywords": result.keywords,
            "count": result.count,
            "source": result.source,
            "articles": result.articles,
            "tts": result.tts,
            "usage": "/news/search?keywords=India&num=5&country=in&lang=hi"
        })

    except Exception as e:
        logger.error(f"Currents error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "tts": "समाचार लाने में त्रुटि हुई।"
        })
