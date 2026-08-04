import time
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

# Core imports 
from core.config import config
from core.cache import cache_store
from core.rate_limit import rate_limit_middleware
from core.telegram import send_telegram_message

# सारे modules import (36)
from modules.weather.handler import router as weather_router
from modules.news.handler import router as news_router
from modules.mandi.handler import router as mandi_router

app = FastAPI(title="Singh Ji AI ULTRA", version="8.3")

# Rate limit middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    rate_limit_middleware(request)
    return await call_next(request)

# Root
@app.get("/")
async def root():
    return {"status": "ok", "version": "8.3", "modules": 36}

# सारे routers register
app.include_router(weather_router, prefix="/api/v1/weather")
app.include_router(news_router, prefix="/api/v1/news")
# ... बाकी सब

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
