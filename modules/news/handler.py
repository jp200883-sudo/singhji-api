#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - News Handler Module
Fetches latest news from multiple sources with Indian language support
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# API Keys from environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# News Sources Configuration
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

# Indian Languages Mapping
LANGUAGE_CODES = {
    "hi": "hindi",
    "en": "english", 
    "ta": "tamil",
    "te": "telugu",
    "bn": "bengali",
    "mr": "marathi",
    "gu": "gujarati",
    "kn": "kannada",
    "ml": "malayalam",
    "pa": "punjabi",
    "ur": "urdu",
    "or": "odia",
    "as": "assamese"
}

# Fallback news data for demo/offline mode
FALLBACK_NEWS = {
    "india": [
        {
            "title": "भारत में आज राष्ट्रीय खबरें",
            "description": "देश भर की महत्वपूर्ण खबरें और घटनाक्रम।",
            "source": "Singh Ji AI News",
            "publishedAt": datetime.now().isoformat(),
            "url": "#",
            "image": None
        }
    ],
    "sports": [
        {
            "title": "Team India की तैयारी जारी",
            "description": "भारतीय टीम अगले मैच की तैयारी में जुटी।",
            "source": "Singh Ji AI Sports",
            "publishedAt": datetime.now().isoformat(),
            "url": "#",
            "image": None
        }
    ]
}


class NewsHandler:
    """Main news handler class for Singh Ji AI Ultra"""

    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        self.last_fetch = {}

    def _get_cached(self, key: str) -> Optional[List[Dict]]:
        """Get cached news if valid"""
        if key in self.cache and key in self.last_fetch:
            if datetime.now() - self.last_fetch[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data: List[Dict]):
        """Cache news data"""
        self.cache[key] = data
        self.last_fetch[key] = datetime.now()

    def fetch_from_newsapi(self, category: str = "general", lang: str = "en", page_size: int = 10) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if not NEWS_API_KEY:
            return []

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "language": lang,
                "pageSize": page_size,
                "sortBy": "publishedAt"
            }

            # Add country for India news
            if category in ["india", "national"]:
                params["country"] = "in"
                del params["category"]

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "ok":
                return self._format_newsapi_articles(data.get("articles", []))
            return []
        except Exception as e:
            print(f"[NewsHandler] NewsAPI Error: {e}")
            return []

    def fetch_from_gnews(self, category: str = "general", lang: str = "en", max_results: int = 10) -> List[Dict]:
        """Fetch news from GNews API"""
        if not GNEWS_API_KEY:
            return []

        try:
            url = "https://gnews.io/api/v4/top-headlines"
            params = {
                "apikey": GNEWS_API_KEY,
                "category": category if category != "india" else "general",
                "lang": lang,
                "max": max_results,
                "country": "in" if category == "india" else None
            }

            if params["country"] is None:
                del params["country"]

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            return self._format_gnews_articles(data.get("articles", []))
        except Exception as e:
            print(f"[NewsHandler] GNews Error: {e}")
            return []

    def _format_newsapi_articles(self, articles: List[Dict]) -> List[Dict]:
        """Format NewsAPI articles to standard format"""
        formatted = []
        for article in articles:
            formatted.append({
                "title": article.get("title", "No Title"),
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", "#"),
                "image": article.get("urlToImage"),
                "author": article.get("author", ""),
                "content": article.get("content", "")
            })
        return formatted

    def _format_gnews_articles(self, articles: List[Dict]) -> List[Dict]:
        """Format GNews articles to standard format"""
        formatted = []
        for article in articles:
            formatted.append({
                "title": article.get("title", "No Title"),
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", "#"),
                "image": article.get("image"),
                "author": article.get("source", {}).get("name", ""),
                "content": ""
            })
        return formatted

    def get_news(self, category: str = "india", language: str = "hi", count: int = 5) -> Dict:
        """
        Get news headlines

        Args:
            category: india, world, sports, business, technology, entertainment
            language: hi, en, ta, te, bn, mr, gu, kn, ml, pa, ur
            count: Number of articles (1-20)

        Returns:
            Dict with news data and metadata
        """
        cache_key = f"{category}_{language}_{count}"
        cached = self._get_cached(cache_key)

        if cached:
            return {
                "status": "success",
                "source": "cache",
                "category": category,
                "language": language,
                "count": len(cached),
                "articles": cached,
                "timestamp": datetime.now().isoformat()
            }

        # Try multiple sources
        articles = []

        # Try NewsAPI first
        if NEWS_API_KEY:
            api_category = self._map_category(category)
            articles = self.fetch_from_newsapi(api_category, language, count)

        # Fallback to GNews
        if not articles and GNEWS_API_KEY:
            articles = self.fetch_from_gnews(category, language, count)

        # Final fallback
        if not articles:
            articles = FALLBACK_NEWS.get(category, FALLBACK_NEWS["india"])

        # Limit to requested count
        articles = articles[:count]

        # Cache the result
        self._set_cache(cache_key, articles)

        return {
            "status": "success",
            "source": "live" if articles != FALLBACK_NEWS.get(category) else "fallback",
            "category": category,
            "language": language,
            "count": len(articles),
            "articles": articles,
            "timestamp": datetime.now().isoformat()
        }

    def _map_category(self, category: str) -> str:
        """Map Singh Ji category to API category"""
        mapping = {
            "india": "general",
            "world": "general",
            "sports": "sports",
            "business": "business",
            "technology": "technology",
            "entertainment": "entertainment"
        }
        return mapping.get(category, "general")

    def get_news_summary(self, article_url: str) -> Dict:
        """Get AI summary of news article using Groq"""
        if not GROQ_API_KEY:
            return {
                "status": "error",
                "message": "Groq API key not configured",
                "summary": ""
            }

        try:
            # Fetch article content
            headers = {
                "User-Agent": "SinghJiAI/7.0 (News Bot)"
            }
            response = requests.get(article_url, headers=headers, timeout=15)

            # Extract text (simplified)
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
            article_text = " ".join(extractor.text)[:4000]  # Limit for API

            # Get summary from Groq
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            groq_data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a Hindi news summarizer. Summarize the given article in 3-4 lines in simple Hindi."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this news article in Hindi:\n\n{article_text}"
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }

            groq_response = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=15)
            groq_result = groq_response.json()

            summary = groq_result["choices"][0]["message"]["content"] if "choices" in groq_result else "सारांश उपलब्ध नहीं।"

            return {
                "status": "success",
                "url": article_url,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "summary": "सारांश बनाने में त्रुटि।"
            }

    def get_trending_topics(self, language: str = "hi") -> Dict:
        """Get trending news topics"""
        # Combine all categories and get top topics
        all_news = []
        for category in ["india", "world", "sports", "business"]:
            result = self.get_news(category, language, 3)
            all_news.extend(result.get("articles", []))

        # Extract keywords (simplified)
        topics = []
        for article in all_news[:10]:
            title = article.get("title", "")
            # Simple keyword extraction
            words = title.split()
            for word in words:
                if len(word) > 3 and word not in ["the", "and", "that", "with", "from", "this", "have", "है", "और", "से", "को", "की", "का"]:
                    topics.append(word)

        # Get unique topics
        unique_topics = list(set(topics))[:10]

        return {
            "status": "success",
            "language": language,
            "trending": unique_topics,
            "total_articles": len(all_news),
            "timestamp": datetime.now().isoformat()
        }

    def get_news_by_keyword(self, keyword: str, language: str = "hi", count: int = 5) -> Dict:
        """Search news by keyword"""
        try:
            if NEWS_API_KEY:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "apiKey": NEWS_API_KEY,
                    "q": keyword,
                    "language": language,
                    "sortBy": "publishedAt",
                    "pageSize": count
                }

                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if data.get("status") == "ok":
                    articles = self._format_newsapi_articles(data.get("articles", []))
                    return {
                        "status": "success",
                        "keyword": keyword,
                        "language": language,
                        "count": len(articles),
                        "articles": articles,
                        "timestamp": datetime.now().isoformat()
                    }

            return {
                "status": "error",
                "message": "No API key configured or no results found",
                "keyword": keyword,
                "articles": []
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "keyword": keyword,
                "articles": []
            }

    def format_for_telegram(self, news_data: Dict, language: str = "hi") -> str:
        """Format news for Telegram message"""
        category = news_data.get("category", "news").upper()
        articles = news_data.get("articles", [])

        if language == "hi":
            header = f"📰 *{category} की ताज़ा खबरें* 📰\n"
            header += f"━━━━━━━━━━━━━━━\n\n"

            message = header
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "No Title")
                source = article.get("source", "Unknown")
                desc = article.get("description", "")[:100]
                url = article.get("url", "#")

                message += f"{i}. *{title}*\n"
                message += f"   📍 {source}\n"
                if desc:
                    message += f"   📝 {desc}...\n"
                message += f"   🔗 [पूरा पढ़ें]({url})\n\n"

            message += f"━━━━━━━━━━━━━━━\n"
            message += f"⚡ *Singh Ji AI Ultra v7.0*"
        else:
            header = f"📰 *Latest {category} News* 📰\n"
            header += f"━━━━━━━━━━━━━━━\n\n"

            message = header
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "No Title")
                source = article.get("source", "Unknown")
                desc = article.get("description", "")[:100]
                url = article.get("url", "#")

                message += f"{i}. *{title}*\n"
                message += f"   📍 {source}\n"
                if desc:
                    message += f"   📝 {desc}...\n"
                message += f"   🔗 [Read More]({url})\n\n"

            message += f"━━━━━━━━━━━━━━━\n"
            message += f"⚡ *Singh Ji AI Ultra v7.0*"

        return message

    def format_for_web(self, news_data: Dict) -> Dict:
        """Format news for web frontend"""
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
        """Generate HTML for web display"""
        articles = news_data.get("articles", [])
        category = news_data.get("category", "news")

        html = f"""
        <div class="news-container">
            <h2 class="news-category">{category.upper()} NEWS</h2>
            <div class="news-grid">
        """

        for article in articles:
            title = article.get("title", "No Title")
            desc = article.get("description", "")
            source = article.get("source", "Unknown")
            url = article.get("url", "#")
            image = article.get("image", "")

            html += f"""
                <div class="news-card">
                    {f'<img src="{image}" alt="{title}" class="news-image" loading="lazy">' if image else ''}
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

        html += """
            </div>
        </div>
        """
        return html


# Singleton instance
news_handler = NewsHandler()

# Convenience functions for direct use
def get_news(category: str = "india", language: str = "hi", count: int = 5) -> Dict:
    """Get news headlines"""
    return news_handler.get_news(category, language, count)

def get_news_summary(article_url: str) -> Dict:
    """Get AI summary of article"""
    return news_handler.get_news_summary(article_url)

def get_trending_topics(language: str = "hi") -> Dict:
    """Get trending topics"""
    return news_handler.get_trending_topics(language)

def search_news(keyword: str, language: str = "hi", count: int = 5) -> Dict:
    """Search news by keyword"""
    return news_handler.get_news_by_keyword(keyword, language, count)

def format_telegram(news_data: Dict, language: str = "hi") -> str:
    """Format for Telegram"""
    return news_handler.format_for_telegram(news_data, language)

def format_web(news_data: Dict) -> Dict:
    """Format for web"""
    return news_handler.format_for_web(news_data)


if __name__ == "__main__":
    # Test
    print("🧪 Testing News Handler...")
    result = get_news("india", "hi", 3)
    print(f"Status: {result['status']}")
    print(f"Articles: {result['count']}")
    print(f"\nTelegram Format:")
    print(format_telegram(result, "hi"))

