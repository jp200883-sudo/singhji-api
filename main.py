"""
Singh Ji AI Ultra v8.0 — Main Application
Root Level Modules — All routes mounted
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================
# EXISTING IMPORTS
# ============================================
from api import router as api_router
from agent_swarm_system import router as swarm_router

# ============================================
# NEW MODULE IMPORTS (Root Level)
# ============================================
from auto_account import AutoAccountManager
from youtube_auto_upload import YouTubeAutoUploader
from instagram_auto_post import InstagramAutoPoster
from trend_analysis import TrendAnalyzer
from auto_monetize import AutoMonetizer
from facebook_long_token import (
    get_long_lived_token,
    get_never_expire_token,
    post_with_permanent_token,
    check_token_validity
)

# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(
    title="🦁 Singh Ji AI Ultra v8.0",
    description="60 Modules | 330 Agent Swarm | 26 Languages | India Super App",
    version="8.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# EXISTING ROUTERS
# ============================================
app.include_router(api_router, prefix="/api")
app.include_router(swarm_router, prefix="/api/swarm")

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health_check():
    return {
        "status": "🦁 Singh Ji AI Ultra v8.0 is LIVE!",
        "version": "8.0.0",
        "owner": "JP Singh Ji Kanpur",
        "modules": 60,
        "agents": 330,
        "kela_mode": "ON 🍌",
        "timestamp": "2026-07-10"
    }

# ============================================
# AUTO-ACCOUNT ROUTES
# ============================================
@app.post("/api/auto_account/create")
async def create_accounts():
    """Create all social media accounts automatically"""
    manager = AutoAccountManager()
    return manager.auto_create_all()

@app.get("/api/auto_account/status")
async def account_status():
    """Get all account status"""
    manager = AutoAccountManager()
    return manager.get_account_status()

# ============================================
# YOUTUBE AUTO-UPLOAD ROUTES
# ============================================
@app.post("/api/youtube/upload")
async def youtube_upload(data: dict):
    """Auto-upload video to YouTube"""
    uploader = YouTubeAutoUploader()
    return uploader.auto_upload_pipeline(
        video_url=data.get("video_url"),
        prompt=data.get("prompt"),
        platform_used=data.get("platform", "auto")
    )

@app.get("/api/youtube/status/{job_id}")
async def youtube_status(job_id: str):
    """Check upload status"""
    uploader = YouTubeAutoUploader()
    return uploader.check_upload_status(job_id)

# ============================================
# INSTAGRAM AUTO-POST ROUTES
# ============================================
@app.post("/api/instagram/post")
async def instagram_post(data: dict):
    """Auto-post to Instagram"""
    poster = InstagramAutoPoster()
    return poster.auto_post_pipeline(
        image_url=data.get("image_url"),
        video_url=data.get("video_url"),
        content_data=data.get("content_data")
    )

@app.post("/api/instagram/story")
async def instagram_story(data: dict):
    """Post Instagram story"""
    poster = InstagramAutoPoster()
    return poster.post_story(
        image_url=data.get("image_url"),
        stickers=data.get("stickers")
    )

# ============================================
# TREND ANALYSIS ROUTES
# ============================================
@app.get("/api/trends/analyze")
async def trends_analyze(category: str = "all", region: str = "IN"):
    """Analyze current trends"""
    analyzer = TrendAnalyzer()
    return analyzer.analyze_trends(category, region)

@app.get("/api/trends/plan")
async def trends_plan():
    """Get content plan from trends"""
    analyzer = TrendAnalyzer()
    return analyzer.get_content_plan()

@app.get("/api/trends/viral/{topic}")
async def viral_score(topic: str):
    """Get viral score for topic"""
    analyzer = TrendAnalyzer()
    return analyzer.get_viral_score(topic)

# ============================================
# AUTO-MONETIZE ROUTES
# ============================================
@app.get("/api/monetize/earnings")
async def monetize_earnings(period: str = "today"):
    """Get earnings report"""
    monetizer = AutoMonetizer()
    return monetizer.get_earnings_report(period)

@app.get("/api/monetize/dashboard")
async def monetize_dashboard():
    """Get full analytics dashboard"""
    monetizer = AutoMonetizer()
    return monetizer.get_analytics_dashboard()

@app.post("/api/monetize/setup/{platform}")
async def monetize_setup(platform: str, data: dict = None):
    """Setup monetization for platform"""
    monetizer = AutoMonetizer()
    return monetizer.setup_monetization(platform, data)

# ============================================
# FACEBOOK ROUTES
# ============================================
@app.get("/api/facebook/login_url")
async def facebook_login():
    """Get Facebook login URL"""
    from facebook_long_token import FACEBOOK_APP_ID, FACEBOOK_REDIRECT_URI, FACEBOOK_SCOPES
    scopes = ",".join(FACEBOOK_SCOPES)
    url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={FACEBOOK_APP_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&scope={scopes}&response_type=code"
    return {"success": True, "login_url": url}

@app.post("/api/facebook/exchange_token")
async def facebook_exchange(data: dict):
    """Exchange code for long-term token"""
    code = data.get("code")
    result = get_long_lived_token(code)
    return result

@app.post("/api/facebook/post")
async def facebook_post(data: dict):
    """Post to Facebook using permanent token"""
    return post_with_permanent_token(
        page_id=data.get("page_id"),
        message=data.get("message"),
        page_token=os.environ.get("FACEBOOK_PAGE_TOKEN")
    )

@app.get("/api/facebook/check_token")
async def facebook_check():
    """Check token validity"""
    token = os.environ.get("FACEBOOK_PAGE_TOKEN")
    return check_token_validity(token)

# ============================================
# ONE-CLICK LIFE — MASTER ENDPOINT
# ============================================
@app.post("/api/one_click/start")
async def one_click_start(data: dict):
    """
    ONE-CLICK LIFE: 
    Trend → Content → Upload → Monetize
    """
    # Step 1: Trend Analysis
    analyzer = TrendAnalyzer()
    trends = analyzer.analyze_trends()
    
    # Step 2: Get top trend
    top_trend = trends.get("top_trend", {}).get("topic", "AI Technology")
    
    # Step 3: Return plan
    return {
        "success": True,
        "message": "🎉 One-Click Life started!",
        "top_trend": top_trend,
        "steps": [
            "1. ✅ Trend detected: " + top_trend,
            "2. 🎨 Generate content (Image/Video)",
            "3. 📤 Auto-upload to YouTube/Instagram/Facebook",
            "4. 💰 Monetize and track earnings"
        ],
        "next_action": "Call /api/youtube/upload or /api/instagram/post"
    }

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
