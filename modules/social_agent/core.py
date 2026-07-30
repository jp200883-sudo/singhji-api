"""
🦁 Singh Ji Social Agent v1.0
Fully Autonomous — Content Gen → Image Gen → Schedule → Post → Analytics
"""
import os
import json
import time
import asyncio
import random
import base64
import io
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

# ─── CONFIG ───
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

FACEBOOK_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")


async def _load_token_from_supabase(http: httpx.AsyncClient) -> Optional[str]:
    """पिछली बार refresh हुआ token Supabase से लोड करो (अगर env वाले से नया है)"""
    if not (SUPABASE_URL and SUPABASE_KEY):
        return None
    try:
        r = await http.get(
            f"{SUPABASE_URL}/rest/v1/api_tokens?key=eq.facebook_page_token&select=value",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        )
        rows = r.json()
        if rows:
            return rows[0]["value"]
    except Exception as e:
        logger.warning(f"[SOCIAL_AGENT] Supabase token load fail: {e}")
    return None


async def _save_token_to_supabase(http: httpx.AsyncClient, token: str, expires_at: str):
    """नया refreshed token Supabase में upsert करो"""
    if not (SUPABASE_URL and SUPABASE_KEY):
        return
    try:
        await http.post(
            f"{SUPABASE_URL}/rest/v1/api_tokens",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "resolution=merge-duplicates",
            },
            json={"key": "facebook_page_token", "value": token, "expires_at": expires_at},
        )
    except Exception as e:
        logger.warning(f"[SOCIAL_AGENT] Supabase token save fail: {e}")

# Free image gen — no API key needed
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1080&seed={seed}&nologo=true"

CONTENT_NICHES = [
    "agriculture_tips", "govt_schemes", "daily_motivation",
    "tech_news", "health_ayurveda", "financial_literacy",
    "farmers_rights", "weather_alerts", "success_stories"
]

POSTING_SCHEDULE = {
    "facebook": ["08:00", "12:30", "17:00", "20:00"],
    "instagram": ["09:00", "13:00", "18:30", "21:00"],
    "youtube": ["10:00", "16:00"]
}

class SinghJiSocialAgent:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http = http_client
        self.content_queue: List[Dict] = []
        self.posted_history: List[Dict] = []
        self.is_running = False
        self.fb_token = FACEBOOK_TOKEN  # runtime override — refresh होने पर यह अपडेट होगा
        self._bsky_session = None  # {accessJwt, did} — login होने पर cache होगा

    async def load_saved_facebook_token(self):
        """Startup पर पिछला refreshed token (अगर है) Supabase से लोड करो"""
        saved = await _load_token_from_supabase(self.http)
        if saved:
            self.fb_token = saved
            logger.info("[SOCIAL_AGENT] Facebook token Supabase से लोड हुआ")

    async def check_and_refresh_facebook_token(self):
        """
        Facebook long-lived token की expiry खुद चेक करता है।
        7 दिन से कम बचे हों तो खुद नया token ले लेता है और Supabase में सेव कर देता है।
        """
        if not self.fb_token:
            logger.warning("[SOCIAL_AGENT] कोई Facebook token नहीं है, refresh skip")
            return {"checked": False, "reason": "no_token"}

        try:
            # STEP 1: अभी वाले token की expiry पता करो
            debug = await self.http.get(
                "https://graph.facebook.com/debug_token",
                params={"input_token": self.fb_token, "access_token": self.fb_token},
            )
            data = debug.json().get("data", {})
            expires_at_ts = data.get("expires_at", 0)  # 0 का मतलब कभी expire नहीं होगा

            if expires_at_ts == 0:
                logger.info("[SOCIAL_AGENT] Facebook token कभी expire नहीं होगा (page token, non-expiring)")
                return {"checked": True, "expires": "never"}

            days_left = (expires_at_ts - time.time()) / 86400
            logger.info(f"[SOCIAL_AGENT] Facebook token में {days_left:.1f} दिन बचे हैं")

            if days_left > 7:
                return {"checked": True, "days_left": round(days_left, 1), "refreshed": False}

            # STEP 2: 7 दिन से कम बचे — नया long-lived token लो
            if not (FACEBOOK_APP_ID and FACEBOOK_APP_SECRET):
                logger.error("[SOCIAL_AGENT] ⚠️ Token expire होने वाला है पर FACEBOOK_APP_ID/SECRET सेट नहीं — auto-refresh नहीं हो सकता")
                return {"checked": True, "days_left": round(days_left, 1), "refreshed": False, "error": "no_app_credentials"}

            resp = await self.http.get(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": FACEBOOK_APP_ID,
                    "client_secret": FACEBOOK_APP_SECRET,
                    "fb_exchange_token": self.fb_token,
                },
            )
            new_data = resp.json()
            new_token = new_data.get("access_token")
            if not new_token:
                logger.error(f"[SOCIAL_AGENT] Token refresh fail: {new_data}")
                return {"checked": True, "refreshed": False, "error": str(new_data)}

            new_expires_days = new_data.get("expires_in", 5184000) / 86400  # default ~60 din
            new_expires_at = (datetime.now() + timedelta(days=new_expires_days)).isoformat()

            self.fb_token = new_token
            await _save_token_to_supabase(self.http, new_token, new_expires_at)
            logger.info(f"[SOCIAL_AGENT] ✅ Facebook token अपने-आप refresh हो गया, अब {new_expires_days:.0f} दिन और चलेगा")

            return {"checked": True, "refreshed": True, "new_expires_in_days": round(new_expires_days, 1)}

        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Token check/refresh fail: {e}")
            return {"checked": False, "error": str(e)}
        
    # ═══════════════════════════════════════
    # STEP 1: AI CONTENT GENERATION
    # ═══════════════════════════════════════
    
    async def _generate_content_groq(self, niche: str, lang: str = "hi") -> Dict:
        """Groq se post content generate karo"""
        if not GROQ_API_KEY:
            return None
            
        prompts = {
            "agriculture_tips": "Ek engaging Instagram/Facebook post likho kisaano ke liye. Hindi mein. 150 words max. Hashtags alag se. Emoji use karo.",
            "govt_schemes": "Ek sarkari yojna ke baare mein short post likho jo aam aadmi samajh sake. Hindi mein. 120 words. 5 hashtags.",
            "daily_motivation": "Motivational quote + 2 line message Hindi mein. Powerful. Short. 3 hashtags.",
            "tech_news": "Bharat mein nayi technology ke baare mein simple post. Hindi + English mix. 100 words. 4 hashtags.",
            "health_ayurveda": "Ayurvedic health tip in Hindi. Desi nuskha style. 100 words. Emoji. 4 hashtags.",
            "financial_literacy": "Paise bachane ya invest karne ka simple tip. Hindi mein. 120 words. 5 hashtags.",
            "farmers_rights": "Kisaan adhikaar ya MSP ke baare mein informative post. Hindi. 130 words.",
            "weather_alerts": "Mausam update + farming advice. Hindi. 80 words. Urgent tone.",
            "success_stories": "Ek chhote businessman/kisaan ki success story. Inspirational. Hindi. 150 words."
        }
        
        system_prompt = "Tu Singh Ji AI hai — Bharat ka apna AI. Social media expert. Short, viral, desi content likhta hai."
        user_prompt = prompts.get(niche, prompts["daily_motivation"])
        
        try:
            resp = await self.http.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{user_prompt}\n\nNiche: {niche}\nLanguage: {lang}"}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 400
                },
                timeout=30
            )
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            
            # Parse caption and hashtags
            lines = text.strip().split("\n")
            caption_lines = []
            hashtags = []
            
            for line in lines:
                if line.strip().startswith("#"):
                    hashtags.extend([h.strip() for h in line.split() if h.startswith("#")])
                else:
                    caption_lines.append(line)
            
            caption = "\n".join(caption_lines).strip()
            if not hashtags:
                hashtags = [f"#{niche}", "#SinghJiAI", "#Bharat", "#India", "#Trending"]
            
            return {
                "caption": caption,
                "hashtags": " ".join(hashtags[:8]),
                "niche": niche,
                "generated_at": datetime.now().isoformat(),
                "lang": lang
            }
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Content gen fail: {e}")
            return None

    async def _generate_content_gemini(self, niche: str, lang: str = "hi") -> Dict:
        """Gemini fallback"""
        if not GEMINI_API_KEY:
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Write a viral social media post about {niche} in Hindi. Include emojis. Separate hashtags at end. Max 150 words."
            resp = await self.http.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "caption": text[:500],
                "hashtags": f"#{niche} #SinghJiAI #Bharat #India",
                "niche": niche,
                "generated_at": datetime.now().isoformat(),
                "lang": lang
            }
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Gemini fail: {e}")
            return None

    async def generate_post_content(self, niche: str = None, lang: str = "hi") -> Dict:
        """Auto niche select + content generate"""
        if not niche:
            niche = random.choice(CONTENT_NICHES)
        
        result = await self._generate_content_groq(niche, lang)
        if not result:
            result = await self._generate_content_gemini(niche, lang)
        if not result:
            # Hard fallback
            result = {
                "caption": f"🦁 Singh Ji AI se judiye!\n\nAaj ka {niche.replace('_', ' ').title()} update. Stay connected! 🇮🇳",
                "hashtags": f"#{niche} #SinghJiAI #Bharat #India #DigitalIndia",
                "niche": niche,
                "generated_at": datetime.now().isoformat(),
                "lang": lang
            }
        return result

    # ═══════════════════════════════════════
    # STEP 2: AI IMAGE GENERATION
    # ═══════════════════════════════════════
    
    async def generate_image(self, niche: str, caption: str) -> Optional[bytes]:
        """Pollinations.ai se free image — no API key needed"""
        try:
            # Image prompt banao caption se
            image_prompt = f"{niche.replace('_', ' ')}, indian style, vibrant colors, professional social media post, high quality, 4k, {caption[:50]}"
            # Clean prompt for URL
            clean_prompt = image_prompt.replace(" ", "%20").replace(",", "%2C")[:300]
            seed = random.randint(1000, 999999)
            url = POLLINATIONS_IMAGE_URL.format(prompt=clean_prompt, seed=seed)
            
            resp = await self.http.get(url, timeout=60)
            if resp.status_code == 200:
                logger.info(f"[SOCIAL_AGENT] Image generated for {niche}")
                return resp.content
            else:
                logger.warning(f"[SOCIAL_AGENT] Image gen status {resp.status_code}")
                return None
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Image gen error: {e}")
            return None

    async def generate_image_hf(self, niche: str, caption: str) -> Optional[bytes]:
        """HuggingFace fallback"""
        if not HF_TOKEN:
            return None
        try:
            prompt = f"Social media post image about {niche}, indian theme, vibrant, professional"
            resp = await self.http.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": prompt},
                timeout=60
            )
            if resp.status_code == 200:
                return resp.content
            return None
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] HF image fail: {e}")
            return None

    # ═══════════════════════════════════════
    # STEP 3: PUBLISH TO PLATFORMS
    # ═══════════════════════════════════════
    
    async def post_to_facebook(self, caption: str, hashtags: str, image_bytes: bytes = None) -> Dict:
        """Facebook Page pe auto-post"""
        if not self.fb_token or not FACEBOOK_PAGE_ID:
            return {"error": "Facebook credentials missing"}
        
        full_text = f"{caption}\n\n{hashtags}"
        
        try:
            if image_bytes:
                # Photo post
                files = {"file": ("image.png", io.BytesIO(image_bytes), "image/png")}
                data = {
                    "access_token": self.fb_token,
                    "message": full_text,
                    "published": "true"
                }
                url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/photos"
                resp = await self.http.post(url, data=data, files=files, timeout=30)
            else:
                # Text-only post
                url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/feed"
                resp = await self.http.post(url, data={
                    "access_token": self.fb_token,
                    "message": full_text
                }, timeout=20)
            
            result = resp.json()
            if "id" in result:
                logger.info(f"[SOCIAL_AGENT] Facebook post success: {result['id']}")
                return {"success": True, "platform": "facebook", "post_id": result["id"]}
            else:
                logger.error(f"[SOCIAL_AGENT] Facebook fail: {result}")
                return {"error": result.get("error", {}).get("message", "Unknown"), "platform": "facebook"}
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Facebook exception: {e}")
            return {"error": str(e), "platform": "facebook"}

    async def post_to_instagram(self, caption: str, hashtags: str, image_bytes: bytes) -> Dict:
        """Instagram Business Account pe auto-post (Facebook से linked होना ज़रूरी)"""
        ig_token = INSTAGRAM_TOKEN or self.fb_token  # linked होने पर Page token ही चलता है
        if not ig_token or not INSTAGRAM_BUSINESS_ID:
            return {"error": "Instagram credentials missing — Facebook Page se link + INSTAGRAM_BUSINESS_ID chahiye"}
        
        if not image_bytes:
            return {"error": "Instagram needs image"}
        
        full_caption = f"{caption}\n\n{hashtags}"
        
        try:
            # Step 1: Upload image to container
            image_b64 = base64.b64encode(image_bytes).decode()
            
            # Actually IG needs image URL, not bytes directly. Use temporary upload or data URI
            # For now, we'll use Facebook as media host since IG Business requires public URL
            # Alternative: Upload to Supabase storage first if available
            
            # Simplified: Post via Facebook Creator Studio API flow
            # First upload media to FB, then publish to IG
            
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media"
            
            # Upload image to temp URL (using imgur or similar as temp host)
            # For production, use Supabase storage or S3
            # Here we'll try direct data approach
            
            # Actually let's use a simpler approach - upload to FB first
            fb_upload = await self.http.post(
                f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/photos",
                data={"access_token": self.fb_token, "published": "false", "message": "temp"},
                files={"file": ("temp.jpg", io.BytesIO(image_bytes), "image/jpeg")},
                timeout=30
            )
            fb_data = fb_upload.json()
            if "id" not in fb_data:
                return {"error": "FB media upload failed", "details": fb_data}
            
            media_fbid = fb_data["id"]
            
            # Get URL of uploaded image
            img_resp = await self.http.get(
                f"https://graph.facebook.com/v25.0/{media_fbid}?access_token={self.fb_token}&fields=images"
            )
            img_data = img_resp.json()
            image_url = img_data.get("images", [{}])[0].get("source", "")
            
            if not image_url:
                return {"error": "Could not get image URL"}
            
            # Step 2: Create IG container
            container_resp = await self.http.post(
                container_url,
                data={
                    "access_token": ig_token,
                    "image_url": image_url,
                    "caption": full_caption
                },
                timeout=20
            )
            container_data = container_resp.json()
            creation_id = container_data.get("id")
            
            if not creation_id:
                return {"error": "IG container creation failed", "details": container_data}
            
            # Step 3: Publish
            await asyncio.sleep(5)  # Wait for processing
            
            publish_resp = await self.http.post(
                f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media_publish",
                data={
                    "access_token": ig_token,
                    "creation_id": creation_id
                },
                timeout=20
            )
            pub_data = publish_resp.json()
            
            if "id" in pub_data:
                logger.info(f"[SOCIAL_AGENT] Instagram post success: {pub_data['id']}")
                return {"success": True, "platform": "instagram", "post_id": pub_data["id"]}
            else:
                return {"error": pub_data.get("error", {}).get("message", "Publish failed"), "platform": "instagram"}
                
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Instagram exception: {e}")
            return {"error": str(e), "platform": "instagram"}

    async def post_to_youtube_community(self, caption: str, hashtags: str) -> Dict:
        """YouTube Community tab post (text only for now)"""
        if not YOUTUBE_API_KEY:
            return {"error": "YouTube API key missing"}
        # YouTube Community posts require OAuth2, API key alone won't work
        # This is a placeholder - full implementation needs OAuth flow
        return {"status": "pending", "platform": "youtube", "note": "Requires OAuth2 setup"}

    async def _bsky_login(self) -> Optional[Dict]:
        """Bluesky App Password से session लो (cache करके रखो)"""
        if self._bsky_session:
            return self._bsky_session
        if not (BLUESKY_HANDLE and BLUESKY_APP_PASSWORD):
            return None
        try:
            resp = await self.http.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
                timeout=15,
            )
            data = resp.json()
            if "accessJwt" not in data:
                logger.error(f"[SOCIAL_AGENT] Bluesky login fail: {data}")
                return None
            self._bsky_session = data
            return data
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Bluesky login exception: {e}")
            return None

    async def post_to_bluesky(self, caption: str, hashtags: str, image_bytes: bytes = None) -> Dict:
        """Bluesky (AT Protocol) pe auto-post"""
        session = await self._bsky_login()
        if not session:
            return {"error": "Bluesky credentials missing/invalid", "platform": "bluesky"}

        full_text = f"{caption}\n\n{hashtags}"[:300]  # Bluesky 300-char limit
        headers = {"Authorization": f"Bearer {session['accessJwt']}"}
        embed = None

        try:
            if image_bytes:
                upload = await self.http.post(
                    "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                    headers={**headers, "Content-Type": "image/png"},
                    content=image_bytes,
                    timeout=30,
                )
                blob_data = upload.json()
                if "blob" in blob_data:
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [{"alt": caption[:100], "image": blob_data["blob"]}],
                    }

            record = {
                "$type": "app.bsky.feed.post",
                "text": full_text,
                "createdAt": datetime.utcnow().isoformat() + "Z",
            }
            if embed:
                record["embed"] = embed

            resp = await self.http.post(
                "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                headers=headers,
                json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
                timeout=20,
            )
            result = resp.json()
            if "uri" in result:
                logger.info(f"[SOCIAL_AGENT] Bluesky post success: {result['uri']}")
                return {"success": True, "platform": "bluesky", "post_id": result["uri"]}
            else:
                logger.error(f"[SOCIAL_AGENT] Bluesky post fail: {result}")
                return {"error": str(result), "platform": "bluesky"}
        except Exception as e:
            logger.error(f"[SOCIAL_AGENT] Bluesky exception: {e}")
            return {"error": str(e), "platform": "bluesky"}

    # ═══════════════════════════════════════
    # STEP 4: FULL AUTOPILOT PIPELINE
    # ═══════════════════════════════════════
    
    async def create_and_publish(self, platforms: List[str] = None, niche: str = None) -> Dict:
        """Full pipeline: Generate → Image → Post"""
        if platforms is None:
            platforms = ["facebook", "instagram", "bluesky"]
        
        logger.info(f"[SOCIAL_AGENT] Starting auto-post pipeline for {platforms}")
        
        # 1. Generate content
        content = await self.generate_post_content(niche)
        
        # 2. Generate image
        image = await self.generate_image(content["niche"], content["caption"])
        if not image:
            image = await self.generate_image_hf(content["niche"], content["caption"])
        
        results = []
        
        # 3. Post to each platform
        for platform in platforms:
            if platform == "facebook":
                res = await self.post_to_facebook(content["caption"], content["hashtags"], image)
            elif platform == "instagram":
                if image:
                    res = await self.post_to_instagram(content["caption"], content["hashtags"], image)
                else:
                    res = {"error": "No image for Instagram", "platform": "instagram"}
            elif platform == "youtube":
                res = await self.post_to_youtube_community(content["caption"], content["hashtags"])
            elif platform == "bluesky":
                res = await self.post_to_bluesky(content["caption"], content["hashtags"], image)
            else:
                res = {"error": f"Unknown platform: {platform}"}
            
            res["content_preview"] = content["caption"][:50]
            res["timestamp"] = datetime.now().isoformat()
            results.append(res)
            
            # Delay between posts to avoid rate limits
            await asyncio.sleep(3)
        
        # Save to history
        post_record = {
            "time": datetime.now().isoformat(),
            "niche": content["niche"],
            "caption": content["caption"],
            "hashtags": content["hashtags"],
            "platforms": platforms,
            "results": results,
            "image_generated": image is not None
        }
        self.posted_history.append(post_record)
        
        # Keep only last 100
        if len(self.posted_history) > 100:
            self.posted_history = self.posted_history[-100:]
        
        success_count = sum(1 for r in results if r.get("success"))
        logger.info(f"[SOCIAL_AGENT] Pipeline complete. Success: {success_count}/{len(platforms)}")
        
        return {
            "success": success_count > 0,
            "total": len(platforms),
            "success_count": success_count,
            "results": results,
            "content": content
        }

    async def schedule_daily_posts(self):
        """Har din ke liye 3-4 posts queue mein daalo"""
        today_niches = random.sample(CONTENT_NICHES, min(4, len(CONTENT_NICHES)))
        for niche in today_niches:
            content = await self.generate_post_content(niche)
            if content:
                self.content_queue.append({
                    "content": content,
                    "scheduled_for": None,  # Will be set by scheduler
                    "posted": False
                })
        logger.info(f"[SOCIAL_AGENT] {len(self.content_queue)} posts queued for today")

    def get_stats(self) -> Dict:
        return {
            "total_posts": len(self.posted_history),
            "queue_size": len(self.content_queue),
            "recent_posts": self.posted_history[-5:],
            "platforms_configured": {
                "facebook": bool(FACEBOOK_TOKEN and FACEBOOK_PAGE_ID),
                "instagram": bool(INSTAGRAM_TOKEN and INSTAGRAM_BUSINESS_ID),
                "youtube": bool(YOUTUBE_API_KEY),
                "bluesky": bool(BLUESKY_HANDLE and BLUESKY_APP_PASSWORD)
            }
        }

# Global instance
SOCIAL_AGENT = None

def init_social_agent(http_client):
    global SOCIAL_AGENT
    SOCIAL_AGENT = SinghJiSocialAgent(http_client)
    return SOCIAL_AGENT
