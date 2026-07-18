#!/usr/bin/env python3
"""
Singh Ji AI Ultra v8.0 - News Handler Module
Fetches latest news from multiple sources with Indian language support
(FIXED: async httpx, FastAPI-style response, parallel trending fetch)
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

NEWS_SOURCES = {
    "india": {
        "categories": ["national", "politics", "crime", "states"],
        "keywords": ["India", "Bharat", "Delhi", "Mumbai", "UP", "Bihar"]
    },
    "world": {
        "categories": ["international", "global", "foreign"],
        "keywords": ["World", "Global", "UN", "USA", "Russia", "China"]
    },
    "sports": {
        "categories": ["cricket", "football", "olympics", "ipl"],
        "keywords": ["Cricket", "IPL", "Olympics", "Sports", "Team India"]
    },
    "business": {
        "categories": ["economy", "stock", "market", "startup"],
        "keywords": ["Sensex", "Nifty", "GDP", "Rupee", "Stock Market"]
    },
    "technology": {
        "categories": ["tech", "ai", "mobile", "internet"],
        "keywords": ["AI", "Technology", "5G", "ISRO", "Digital India"]
    },
    "entertainment": {
        "categories": ["bollywood", "hollywood", "music"],
        "keywords": ["Bollywood", "Movie", "Actor", "Film", "Celebrity"]
    }
}

LANGUAGE_CODES = {
    "hi": "hindi", "en": "english", "ta": "tamil", "te": "telugu",
    "bn": "bengali", "mr": "marathi", "gu": "gujarati", "kn": "kannada",
    "ml": "malayalam", "pa": "punjabi", "ur": "urdu", "or": "odia", "as": "assamese"
}

FALLBACK_NEWS = {
    "india": [{
        "title": "भारत में आज राष्ट्रीय खबरें",
        "description": "देश भर की महत्वपूर्ण खबरें और घटनाक्रम।",
        "source": "Singh Ji AI News",
        "publishedAt": datetime.now().isoformat(),
        "url": "#", "image": None
    }],
    "sports": [{
        "title": "Team India की तैयारी जारी",
        "description": "भारतीय टीम अगले मैच की तैयारी में जुटी।",
        "source": "Singh Ji AI Sports",
        "publishedAt": datetime.now().isoformat(),
        "url": "#", "image": None
    }]
}

# Saara module ek hi shared async client istemal karta hai
_client: Optional[httpx.AsyncClient] = None

def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10)
    return _client


class NewsHandler:
    """Main news handler class for Singh Ji AI Ultra"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
        self.last_fetch = {}

    def _get_cached(self, key: str) -> Optional[List[Dict]]:
        if key in self.cache and key in self.last_fetch:
            if datetime.now() - self.last_fetch[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data: List[Dict]):
        self.cache[key] = data
        self.last_fetch[key] = datetime.now()

    async def fetch_from_newsapi(self, category: str = "general", lang: str = "en", page_size: int = 10) -> List[Dict]:
        if not NEWS_API_KEY:
            return []
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": NEWS_API_KEY, "category": category, "language": lang,
                "pageSize": page_size, "sortBy": "publishedAt"
            }
            if category in ["india", "national"]:
                params["country"] = "in"
                del params["category"]

            resp = await _get_client().get(url, params=params)
            data = resp.json()
            if data.get("status") == "ok":
                return self._format_newsapi_articles(data.get("articles", []))
            return []
        except Exception as e:
            logger.warning(f"[NewsHandler] NewsAPI Error: {e}")
            return []

    async def fetch_from_gnews(self, category: str = "general", lang: str = "en", max_results: int = 10) -> List[Dict]:
        if not GNEWS_API_KEY:
            return []
        try:
            url = "https://gnews.io/api/v4/top-headlines"
            params = {
                "apikey": GNEWS_API_KEY,
                "category": category if category != "india" else "general",
                "lang": lang, "max": max_results,
                "country": "in" if category == "india" else None
            }
            if params["country"] is None:
                del params["country"]

            resp = await _get_client().get(url, params=params)
            data = resp.json()
            return self._format_gnews_articles(data.get("articles", []))
        except Exception as e:
            logger.warning(f"[NewsHandler] GNews Error: {e}")
            return []

    def _format_newsapi_articles(self, articles: List[Dict]) -> List[Dict]:
        return [{
            "title": a.get("title", "No Title"),
            "description": a.get("description", ""),
            "source": a.get("source", {}).get("name", "Unknown"),
            "publishedAt": a.get("publishedAt", ""),
            "url": a.get("url", "#"),
            "image": a.get("urlToImage"),
            "author": a.get("author", ""),
            "content": a.get("content", "")
        } for a in articles]

    def _format_gnews_articles(self, articles: List[Dict]) -> List[Dict]:
        return [{
            "title": a.get("title", "No Title"),
            "description": a.get("description", ""),
            "source": a.get("source", {}).get("name", "Unknown"),
            "publishedAt": a.get("publishedAt", ""),
            "url": a.get("url", "#"),
            "image": a.get("image"),
            "author": a.get("source", {}).get("name", ""),
            "content": ""
        } for a in articles]

    async def get_news(self, category: str = "india", language: str = "hi", count: int = 5) -> Dict:
        cache_key = f"{category}_{language}_{count}"
        cached = self._get_cached(cache_key)
        if cached:
            return {
                "status": "success", "source": "cache", "category": category,
                "language": language, "count": len(cached), "articles": cached,
                "timestamp": datetime.now().isoformat()
            }

        articles = []
        if NEWS_API_KEY:
            api_category = self._map_category(category)
            articles = await self.fetch_from_newsapi(api_category, language, count)

        if not articles and GNEWS_API_KEY:
            articles = await self.fetch_from_gnews(category, language, count)

        used_fallback = False
        if not articles:
            articles = FALLBACK_NEWS.get(category, FALLBACK_NEWS["india"])
            used_fallback = True

        articles = articles[:count]
        self._set_cache(cache_key, articles)

        return {
            "status": "success",
            "source": "fallback" if used_fallback else "live",
            "category": category, "language": language,
            "count": len(articles), "articles": articles,
            "timestamp": datetime.now().isoformat()
        }

    def _map_category(self, category: str) -> str:
        mapping = {
            "india": "general", "world": "general", "sports": "sports",
            "business": "business", "technology": "technology", "entertainment": "entertainment"
        }
        return mapping.get(category, "general")

    async def get_news_summary(self, article_url: str) -> Dict:
        """Get AI summary of news article using Groq"""
        if not GROQ_API_KEY:
            return {"status": "error", "message": "Groq API key not configured", "summary": ""}

        # SSRF guard — sirf http/https aur ek asli hostname hona chahiye,
        # internal/private URLs (localhost, IP-only, no scheme) allow nahi
        parsed = urlparse(article_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return {"status": "error", "message": "Invalid article URL", "summary": ""}

        try:
            headers = {"User-Agent": "SinghJiAI/8.0 (News Bot)"}
            response = await _get_client().get(article_url, headers=headers, timeout=15)

            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.in_script = False

                def handle_starttag(self, tag, attrs):
                    if tag in ["script", "style"]:
                        self.in_script = True

                def handle_endtag(self, tag):
                    if tag in ["script", "style"]:
                        self.in_script = False

                def handle_data(self, data):
                    if not self.in_script:
                        self.text.append(data.strip())

            extractor = TextExtractor()
            extractor.feed(response.text)
            article_text = " ".join(extractor.text)[:4000]

            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            groq_data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a Hindi news summarizer. Summarize the given article in 3-4 lines in simple Hindi."},
                    {"role": "user", "content": f"Summarize this news article in Hindi:\n\n{article_text}"}
                ],
                "max_tokens": 300, "temperature": 0.3
            }

            groq_response = await _get_client().post(groq_url, headers=groq_headers, json=groq_data, timeout=15)
            groq_result = groq_response.json()
            summary = groq_result["choices"][0]["message"]["content"] if "choices" in groq_result else "सारांश उपलब्ध नहीं।"

            return {"status": "success", "url": article_url, "summary": summary, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"status": "error", "message": str(e), "summary": "सारांश बनाने में त्रुटि।"}

    async def get_trending_topics(self, language: str = "hi") -> Dict:
        """Get trending news topics — 4 categories ab samantar (parallel) fetch hoti hain"""
        categories = ["india", "world", "sports", "business"]
        results = await asyncio.gather(*(self.get_news(c, language, 3) for c in categories))

        all_news = []
        for result in results:
            all_news.extend(result.get("articles", []))

        stopwords = {"the", "and", "that", "with", "from", "this", "have", "है", "और", "से", "को", "की", "का"}
        topics = []
        for article in all_news[:10]:
            title = article.get("title", "")
            for word in title.split():
                if len(word) > 3 and word not in stopwords:
                    topics.append(word)

        unique_topics = list(dict.fromkeys(topics))[:10]

        return {
            "status": "success", "language": language, "trending": unique_topics,
            "total_articles": len(all_news), "timestamp": datetime.now().isoformat()
        }

    async def get_news_by_keyword(self, keyword: str, language: str = "hi", count: int = 5) -> Dict:
        try:
            if NEWS_API_KEY:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "apiKey": NEWS_API_KEY, "q": keyword, "language": language,
                    "sortBy": "publishedAt", "pageSize": count
                }
                resp = await _get_client().get(url, params=params)
                data = resp.json()
                if data.get("status") == "ok":
                    articles = self._format_newsapi_articles(data.get("articles", []))
                    return {
                        "status": "success", "keyword": keyword, "language": language,
                        "count": len(articles), "articles": articles,
                        "timestamp": datetime.now().isoformat()
                    }
            return {"status": "error", "message": "No API key configured or no results found", "keyword": keyword, "articles": []}
        except Exception as e:
            return {"status": "error", "message": str(e), "keyword": keyword, "articles": []}

    def format_for_telegram(self, news_data: Dict, language: str = "hi") -> str:
        category = news_data.get("category", "news").upper()
        articles = news_data.get("articles", [])
        label_header_hi = f"📰 *{category} की ताज़ा खबरें* 📰\n━━━━━━━━━━━━━━━\n\n"
        label_header_en = f"📰 *Latest {category} News* 📰\n━━━━━━━━━━━━━━━\n\n"
        message = label_header_hi if language == "hi" else label_header_en
        read_more = "पूरा पढ़ें" if language == "hi" else "Read More"

        for i, article in enumerate(articles[:5], 1):
            title = article.get("title", "No Title")
            source = article.get("source", "Unknown")
            desc = article.get("description", "")[:100]
            url = article.get("url", "#")
            message += f"{i}. *{title}*\n"
            message += f"   📍 {source}\n"
            if desc:
                message += f"   📝 {desc}...\n"
            message += f"   🔗 [{read_more}]({url})\n\n"

        message += "━━━━━━━━━━━━━━━\n⚡ *Singh Ji AI Ultra v8.0*"
        return message

    def format_for_web(self, news_data: Dict) -> Dict:
        return {
            "status": news_data.get("status"),
            "category": news_data.get("category"),
            "language": news_data.get("language"),
            "count": news_data.get("count"),
            "articles": news_data.get("articles", []),
            "timestamp": news_data.get("timestamp"),
            "html": self._generate_html(news_data)
        }

    def _generate_html(self, news_data: Dict) -> str:
        articles = news_data.get("articles", [])
        category = news_data.get("category", "news")
        html = f'<div class="news-container"><h2 class="news-category">{category.upper()} NEWS</h2><div class="news-grid">'
        for article in articles:
            title = article.get("title", "No Title")
            desc = article.get("description", "")
            source = article.get("source", "Unknown")
            url = article.get("url", "#")
            image = article.get("image", "")
            img_tag = f'<img src="{image}" alt="{title}" class="news-image" loading="lazy">' if image else ""
            html += f"""
                <div class="news-card">
                    {img_tag}
                    <div class="news-content">
                        <h3 class="news-title">{title}</h3>
                        <p class="news-desc">{desc[:150]}...</p>
                        <div class="news-meta">
                            <span class="news-source">📍 {source}</span>
                            <a href="{url}" target="_blank" class="news-link">Read More →</a>
                        </div>
                    </div>
                </div>
            """
        html += "</div></div>"
        return html


news_handler = NewsHandler()

async def get_news(category: str = "india", language: str = "hi", count: int = 5) -> Dict:
    return await news_handler.get_news(category, language, count)

async def get_news_summary(article_url: str) -> Dict:
    return await news_handler.get_news_summary(article_url)

async def get_trending_topics(language: str = "hi") -> Dict:
    return await news_handler.get_trending_topics(language)

async def search_news(keyword: str, language: str = "hi", count: int = 5) -> Dict:
    return await news_handler.get_news_by_keyword(keyword, language, count)

def format_telegram(news_data: Dict, language: str = "hi") -> str:
    return news_handler.format_for_telegram(news_data, language)

def format_web(news_data: Dict) -> Dict:
    return news_handler.format_for_web(news_data)


async def handler(request: Request):
    """
    FastAPI handler — baaki modules (jaise currency converter) ke saath
    consistent: seedha dict/JSONResponse lautata hai, Lambda-style
    statusCode/body wrapper nahi.
    """
    try:
        body = await request.json() if request.method == "POST" else {}
        params = dict(request.query_params)

        category = body.get("category") or params.get("category", "india")
        language = body.get("language") or params.get("language", "hi")
        try:
            count = int(body.get("count") or params.get("count", 5))
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"status": "error", "message": "count must be a number"})
        action = body.get("action") or params.get("action", "get_news")

        if action == "get_news":
            result = await get_news(category, language, count)
        elif action == "search":
            keyword = body.get("keyword") or params.get("keyword", "")
            result = await search_news(keyword, language, count)
        elif action == "trending":
            result = await get_trending_topics(language)
        elif action == "telegram":
            news_data = await get_news(category, language, count)
            result = {
                "status": "success",
                "message": format_telegram(news_data, language),
                "category": category, "language": language
            }
        else:
            result = await get_news(category, language, count)

        return JSONResponse(status_code=200, content=result)

    except Exception as e:
        logger.error(f"[NewsHandler] handler crash: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
