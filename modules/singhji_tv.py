# modules/singhji_tv.py — Singh Ji TV Module
# 📺 TV bina TV ke — Phone mein sab kuch!

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import os
import json
from typing import Optional, List

router = APIRouter(prefix="/api/tv", tags=["Singh Ji TV"])

# ===== CONFIG =====
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_BASE = "https://www.googleapis.com/youtube/v3"

# ===== CATEGORIES =====
TV_CATEGORIES = {
    "news": {
        "name": "📰 Live News",
        "channels": [
            {"name": "Aaj Tak", "id": "UCt4t-jeY85JegMlZ-E5UWtA"},
            {"name": "ABP News", "id": "UCRWFSbif-RFHHM6c9QkT6OQ"},
            {"name": "India TV", "id": "UCttspZesZIDEwwpVIgoZtWQ"},
            {"name": "NDTV India", "id": "UC9CYT9gSNLevX5ey2_6CK0Q"},
            {"name": "Zee News", "id": "UCIvaYmXn910QMdemBG3v1pQ"},
        ],
        "keywords": ["live news hindi", "breaking news", "samachar"]
    },
    "bhajan": {
        "name": "🙏 Bhajans & Aarti",
        "channels": [
            {"name": "T-Series Bhakti", "id": "UCaayLD9iED1fbsh_UkI0LJA"},
            {"name": "Bhakti TV", "id": "UC2A4Xz7-RbPNTnDpR1EiQBg"},
        ],
        "keywords": ["hanuman chalisa", "durga aarti", "krishna bhajan"]
    },
    "kisan": {
        "name": "🌾 Kisan TV",
        "channels": [
            {"name": "DD Kisan", "id": "UCnDfmcYLYhmOlgCiqC7DNCQ"},
            {"name": "Kisan Tak", "id": "UCnDfmcYLYhmOlgCiqC7DNCQ"},
        ],
        "keywords": ["kisan news", "farming tips hindi", "agriculture india"]
    },
    "education": {
        "name": "📚 Education",
        "channels": [
            {"name": "Khan Academy Hindi", "id": "UCZ3Z4Z3Z3Z3Z3Z3Z3Z3Z3Z3"},
            {"name": "Study IQ", "id": "UCrC8mOqJQpoB7NuIMKIS6rQ"},
        ],
        "keywords": ["ncert solutions", "upsc hindi", "ssc cgl"]
    },
    "entertainment": {
        "name": "🎬 Entertainment",
        "channels": [
            {"name": "T-Series", "id": "UCq-Fj5jknLsUf-MWSy4_brA"},
            {"name": "Zee Music", "id": "UCFFbwnve3yF62_tVXkTyHqg"},
        ],
        "keywords": ["new hindi songs", "bollywood trailer", "comedy"]
    },
    "sports": {
        "name": "🏏 Sports",
        "channels": [
            {"name": "Star Sports", "id": "UCpS0Hlw5fEBY8gV8i0k0X1Q"},
            {"name": "Sony Sports", "id": "UCqS0Hlw5fEBY8gV8i0k0X1Q"},
        ],
        "keywords": ["cricket live", "ipl highlights", "sports news"]
    },
    "health": {
        "name": "💊 Health & Yoga",
        "channels": [
            {"name": "Ramdev Yoga", "id": "UCXw5v3Q0iX9v2j1q8v3w4x5"},
            {"name": "Health TV", "id": "UCY5w5v3Q0iX9v2j1q8v3w4x5"},
        ],
        "keywords": ["yoga hindi", "health tips", "ayurveda"]
    },
    "movies": {
        "name": "🎬 Free Movies",
        "channels": [
            {"name": "Goldmines", "id": "UCyoXW_Dse7fURq30EWl_CUA"},
            {"name": "Pen Movies", "id": "UC3gNmTGu-TTbFPxmP5E3kJg"},
        ],
        "keywords": ["free hindi movie", "classic bollywood", "old movie"]
    }
}

# ===== DUMMY DATA (When API key not available) =====
DUMMY_VIDEOS = {
    "news": [
        {"title": "Breaking: Modi Ji ka naya scheme", "channel": "Aaj Tak", "videoId": "dummy1", "thumbnail": "https://via.placeholder.com/320x180?text=News+1"},
        {"title": "Weather alert: Barish aa rahi hai", "channel": "ABP", "videoId": "dummy2", "thumbnail": "https://via.placeholder.com/320x180?text=News+2"},
        {"title": "Kisan Andolan: Latest update", "channel": "India TV", "videoId": "dummy3", "thumbnail": "https://via.placeholder.com/320x180?text=News+3"},
    ],
    "bhajan": [
        {"title": "Hanuman Chalisa - Full", "channel": "T-Series", "videoId": "dummy4", "thumbnail": "https://via.placeholder.com/320x180?text=Bhajan+1"},
        {"title": "Durga Aarti - Jagdambe", "channel": "Bhakti TV", "videoId": "dummy5", "thumbnail": "https://via.placeholder.com/320x180?text=Bhajan+2"},
    ],
    "kisan": [
        {"title": "Kheti ka naya tarika - Organic", "channel": "DD Kisan", "videoId": "dummy6", "thumbnail": "https://via.placeholder.com/320x180?text=Kisan+1"},
        {"title": "Mandi rates - Aaj ka bhav", "channel": "Kisan Tak", "videoId": "dummy7", "thumbnail": "https://via.placeholder.com/320x180?text=Kisan+2"},
    ],
    "movies": [
        {"title": "Sholay - Full Movie HD", "channel": "Goldmines", "videoId": "dummy8", "thumbnail": "https://via.placeholder.com/320x180?text=Movie+1"},
        {"title": "Mughal-e-Azam - Classic", "channel": "Pen Movies", "videoId": "dummy9", "thumbnail": "https://via.placeholder.com/320x180?text=Movie+2"},
    ]
}

# ===== FETCH VIDEOS =====
def fetch_youtube_videos(category: str, max_results: int = 10):
    """Fetch videos from YouTube API or return dummy data"""
    
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "":
        # Return dummy data when no API key
        return {
            "source": "dummy",
            "message": "YouTube API key not configured - showing demo content",
            "videos": DUMMY_VIDEOS.get(category, DUMMY_VIDEOS["news"])[:max_results]
        }
    
    try:
        # Search YouTube
        cat_data = TV_CATEGORIES.get(category, TV_CATEGORIES["news"])
        keywords = cat_data["keywords"][0] if cat_data["keywords"] else "hindi news"
        
        url = f"{YOUTUBE_BASE}/search"
        params = {
            "part": "snippet",
            "q": keywords,
            "type": "video",
            "maxResults": max_results,
            "order": "relevance",
            "key": YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        videos = []
        for item in data.get("items", []):
            video = {
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "videoId": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"] if "high" in item["snippet"]["thumbnails"] else item["snippet"]["thumbnails"]["default"]["url"],
                "publishedAt": item["snippet"]["publishedAt"],
                "description": item["snippet"]["description"][:100] + "..."
            }
            videos.append(video)
        
        return {
            "source": "youtube",
            "category": category,
            "total": len(videos),
            "videos": videos
        }
        
    except Exception as e:
        return {
            "source": "error",
            "error": str(e),
            "videos": DUMMY_VIDEOS.get(category, DUMMY_VIDEOS["news"])[:max_results]
        }

# ===== API ENDPOINTS =====

@router.get("/")
async def tv_home():
    """Singh Ji TV Home"""
    return {
        "app": "📺 Singh Ji TV",
        "version": "1.0.0",
        "categories": list(TV_CATEGORIES.keys()),
        "total_categories": len(TV_CATEGORIES),
        "message": "TV bina TV ke — Phone mein sab kuch!",
        "endpoints": {
            "categories": "/api/tv/categories",
            "videos": "/api/tv/videos?category=news",
            "live": "/api/tv/live",
            "search": "/api/tv/search?q=modi"
        }
    }

@router.get("/categories")
async def tv_categories():
    """Get all TV categories"""
    return {
        "categories": [
            {
                "id": cat_id,
                "name": data["name"],
                "channels_count": len(data["channels"]),
                "channels": [c["name"] for c in data["channels"]]
            }
            for cat_id, data in TV_CATEGORIES.items()
        ]
    }

@router.get("/videos")
async def tv_videos(
    category: str = Query("news", description="Category: news, bhajan, kisan, education, entertainment, sports, health, movies"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get videos by category"""
    if category not in TV_CATEGORIES:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid category. Choose from: {list(TV_CATEGORIES.keys())}"}
        )
    
    result = fetch_youtube_videos(category, limit)
    return {
        "category": category,
        "category_name": TV_CATEGORIES[category]["name"],
        **result
    }

@router.get("/live")
async def tv_live():
    """Get live TV streams"""
    live_streams = {
        "news": [
            {"name": "Aaj Tak Live", "url": "https://www.youtube.com/embed/UCt4t-jeY85JegMlZ-E5UWtA?autoplay=1", "type": "youtube"},
            {"name": "ABP News Live", "url": "https://www.youtube.com/embed/UCRWFSbif-RFHHM6c9QkT6OQ?autoplay=1", "type": "youtube"},
        ],
        "bhajan": [
            {"name": "Hanuman Chalisa 24x7", "url": "https://www.youtube.com/embed/dummy_bhajan", "type": "youtube"},
        ]
    }
    return {
        "live_streams": live_streams,
        "message": "Live TV — bas internet chahiye!"
    }

@router.get("/search")
async def tv_search(q: str = Query(..., description="Search query"), limit: int = 10):
    """Search videos"""
    if not YOUTUBE_API_KEY:
        # Return dummy search results
        return {
            "query": q,
            "source": "dummy",
            "results": [
                {"title": f"{q} - Result 1", "channel": "Singh Ji TV", "videoId": "search1"},
                {"title": f"{q} - Result 2", "channel": "Singh Ji TV", "videoId": "search2"},
            ]
        }
    
    try:
        url = f"{YOUTUBE_BASE}/search"
        params = {
            "part": "snippet",
            "q": q + " hindi",
            "type": "video",
            "maxResults": limit,
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "videoId": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"] if "medium" in item["snippet"]["thumbnails"] else ""
            })
        
        return {"query": q, "total": len(results), "results": results}
        
    except Exception as e:
        return {"error": str(e), "query": q}

@router.get("/player/{video_id}")
async def tv_player(video_id: str):
    """Get video player URL"""
    return {
        "video_id": video_id,
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "download_url": None,
        "message": "Video player ready!"
    }

@router.get("/trending")
async def tv_trending():
    """Get trending videos"""
    trending = []
    for cat in ["news", "bhajan", "kisan", "entertainment"]:
        vids = fetch_youtube_videos(cat, 3)
        if "videos" in vids:
            trending.extend(vids["videos"][:2])
    
    return {
        "trending": trending[:10],
        "message": "Aaj kya trend kar raha hai!"
    }

# ===== EXPORT =====
if __name__ == "__main__":
    print("📺 Singh Ji TV Module")
    print("Categories:", list(TV_CATEGORIES.keys()))
