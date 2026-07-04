# 🦁 AI_CHAT

Phase 1 Module
# Singh Ji AI Ultra v7.0 - New Modules (4 July 2026)

## 📦 Modules Included

### 1. news_handler.py
- India/World news headlines
- 6 categories: india, world, sports, business, technology, entertainment
- 13 Indian languages support
- AI summary using Groq
- News search by keyword
- Telegram + Web formatting
- 5-minute cache system

### 2. horoscope_handler.py
- 12 Zodiac signs (Hindi + English)
- Daily/Weekly/Monthly predictions
- AI-powered via Groq (fallback auto-generate)
- Birth date to zodiac sign
- Compatibility checker
- Lucky number, color, time, direction
- Telegram + Web formatting
- 1-hour cache system

### 3. modules_routes.py
- Flask Blueprint for all routes
- REST API endpoints
- Telegram bot command handlers
- Health check endpoint

## 🔗 API Endpoints

### News
- GET /api/modules/news?category=india&language=hi&count=5
- POST /api/modules/news/summary {"url": "article_url"}
- GET /api/modules/news/search?q=keyword&language=hi
- GET /api/modules/news/telegram?category=india

### Horoscope
- GET /api/modules/horoscope?rashi=मेष&period=daily&language=hi
- GET /api/modules/horoscope/all?period=daily
- GET /api/modules/horoscope/by-date?day=15&month=8
- GET /api/modules/horoscope/compatibility?rashi1=मेष&rashi2=तुला
- GET /api/modules/horoscope/telegram?rashi=मेष

### Telegram Commands
- /news [category] [language]
- /sports
- /business
- /rashifal [rashi]
- /allrashifal
- /milan <rashi1> <rashi2>

## 📁 Installation

1. Copy files to singhji-api/handlers/ and singhji-api/routes/
2. Add to main.py:
   ```python
   from routes.modules_routes import modules_bp, handle_telegram_command
   app.register_blueprint(modules_bp)
   ```
3. Add environment variables:
   - NEWS_API_KEY (from newsapi.org)
   - GNEWS_API_KEY (from gnews.io)
   - GROQ_API_KEY (already set)

## 🎯 Part 1 Progress
- Modules: 2/10 done
- Files: 3/168 done
- Next: Gold Rate, Fuel Price, Train Status

Created: 4 July 2026
Singh Ji AI Ultra v7.0
