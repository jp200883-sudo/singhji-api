# modules/social.py — Singh Ji AI Ultra v5.0
# Social Media — Share, Trends, Hashtag analysis

from fastapi import APIRouter
import os
import requests

router = APIRouter()

@router.get("/")
def social_root():
    return {
        "module": "social",
        "status": "✅ Live",
        "features": ["share", "trends", "hashtag", "viral"]
    }

@router.get("/share")
def share_content(platform: str, url: str, text: str = ""):
    """Generate shareable links for social media"""
    
    encoded_url = requests.utils.quote(url)
    encoded_text = requests.utils.quote(text)
    
    share_links = {
        "whatsapp": f"https://wa.me/?text={encoded_text}%20{encoded_url}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "telegram": f"https://t.me/share/url?url={encoded_url}&text={encoded_text}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        "reddit": f"https://reddit.com/submit?url={encoded_url}&title={encoded_text}"
    }
    
    if platform == "all":
        return {
            "success": True,
            "url": url,
            "text": text,
            "share_links": share_links
        }
    
    if platform in share_links:
        return {
            "success": True,
            "platform": platform,
            "share_url": share_links[platform]
        }
    
    return {"success": False, "error": "Platform not supported", "available": list(share_links.keys())}

@router.get("/trends/india")
def india_trends():
    """Current trending topics in India"""
    # Simulated trends (in real app, use Twitter API or Google Trends)
    trends = [
        {"rank": 1, "topic": "#IndiaNews", "category": "News", "volume": "500K+"},
        {"rank": 2, "topic": "#PMModi", "category": "Politics", "volume": "300K+"},
        {"rank": 3, "topic": "#Cricket", "category": "Sports", "volume": "250K+"},
        {"rank": 4, "topic": "#Bollywood", "category": "Entertainment", "volume": "200K+"},
        {"rank": 5, "topic": "#TechIndia", "category": "Technology", "volume": "150K+"}
    ]
    
    return {
        "success": True,
        "country": "India",
        "total": len(trends),
        "trends": trends,
        "updated": "Live"
    }

@router.get("/hashtag/analyze")
def analyze_hashtag(hashtag: str):
    """Basic hashtag analysis"""
    if not hashtag.startswith("#"):
        hashtag = "#" + hashtag
    
    return {
        "success": True,
        "hashtag": hashtag,
        "analysis": {
            "length": len(hashtag),
            "word_count": len(hashtag.split()),
            "recommendation": "Use 2-3 hashtags for best engagement",
            "best_time": "6 PM - 9 PM IST",
            "platforms": ["Instagram", "Twitter", "LinkedIn"]
        }
    }

@router.get("/viral/content")
def viral_content(category: str = "all"):
    """Viral content ideas"""
    ideas = {
        "news": ["Breaking news reaction", "Fact check video", "News summary reel"],
        "education": ["Quick learning hack", "Exam tips", "Career advice"],
        "entertainment": ["Movie review", "Meme compilation", "Trending challenge"],
        "tech": ["App review", "Coding tutorial", "Gadget unboxing"],
        "motivation": ["Success story", "Morning routine", "Productivity tips"]
    }
    
    if category == "all":
        return {"success": True, "categories": list(ideas.keys()), "ideas": ideas}
    
    return {
        "success": True,
        "category": category,
        "ideas": ideas.get(category, ["General viral content"])
    }
