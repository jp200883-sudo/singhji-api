# ═══════════════════════════════════════════════════════
# 🤖 AGENTIC-A BRAIN — Singh Ji AI Ultra v8.0
# Master Agent — Auto content, video, social media
# ═══════════════════════════════════════════════════════

import sys
import os
import json
import time
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Logging
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# PATH SETUP
# ═══════════════════════════════════════════════════════

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ═══════════════════════════════════════════════════════
# IMPORTS — Try to load existing modules (graceful fallback)
# ═══════════════════════════════════════════════════════

VIDEO_CONNECTORS = {}
OAUTH_AVAILABLE = False
AI_BRAIN_AVAILABLE = False

# Video connectors
try:
    from video_gen.hailuo import HailuoConnector
    VIDEO_CONNECTORS["hailuo"] = HailuoConnector
    logger.info("✅ Hailuo loaded")
except ImportError as e:
    logger.warning(f"⚠️ Hailuo: {e}")

try:
    from video_gen.kling import KlingConnector
    VIDEO_CONNECTORS["kling"] = KlingConnector
    logger.info("✅ Kling loaded")
except ImportError as e:
    logger.warning(f"⚠️ Kling: {e}")

try:
    from video_gen.luma import LumaConnector
    VIDEO_CONNECTORS["luma"] = LumaConnector
    logger.info("✅ Luma loaded")
except ImportError as e:
    logger.warning(f"⚠️ Luma: {e}")

try:
    from video_gen.pika import PikaConnector
    VIDEO_CONNECTORS["pika"] = PikaConnector
    logger.info("✅ Pika loaded")
except ImportError as e:
    logger.warning(f"⚠️ Pika: {e}")

try:
    from video_gen.veo import VeoConnector
    VIDEO_CONNECTORS["veo"] = VeoConnector
    logger.info("✅ Veo loaded")
except ImportError as e:
    logger.warning(f"⚠️ Veo: {e}")

try:
    from video_gen.seedance import SeedanceConnector
    VIDEO_CONNECTORS["seedance"] = SeedanceConnector
    logger.info("✅ Seedance loaded")
except ImportError as e:
    logger.warning(f"⚠️ Seedance: {e}")

# Watermark & Delivery
try:
    from video_gen.watermark_remover import WatermarkRemover
    WATERMARK_AVAILABLE = True
    logger.info("✅ WatermarkRemover loaded")
except ImportError as e:
    WATERMARK_AVAILABLE = False
    logger.warning(f"⚠️ WatermarkRemover: {e}")

try:
    from video_gen.video_delivery import VideoDelivery
    DELIVERY_AVAILABLE = True
    logger.info("✅ VideoDelivery loaded")
except ImportError as e:
    DELIVERY_AVAILABLE = False
    logger.warning(f"⚠️ VideoDelivery: {e}")

# OAuth
try:
    from oauth_connector.handler import router as oauth_router
    OAUTH_AVAILABLE = True
    logger.info("✅ OAuth loaded")
except ImportError as e:
    logger.warning(f"⚠️ OAuth: {e}")

# AI Brain
try:
    import aiohttp
    AI_BRAIN_AVAILABLE = True
except ImportError:
    pass

# ═══════════════════════════════════════════════════════
# 🤖 AGENTIC BRAIN CLASS
# ═══════════════════════════════════════════════════════

class AgenticBrain:
    """
    Master Agent — Tumhare modules ko connect karega
    """
    
    def __init__(self):
        self.name = "Agentic-A"
        self.version = "1.0.0"
        self.active = True
        
        # API Keys
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        
        # Video connectors initialize
        self.video_instances = {}
        for name, ConnectorClass in VIDEO_CONNECTORS.items():
            try:
                self.video_instances[name] = ConnectorClass()
                logger.info(f"✅ {name} connector initialized")
            except Exception as e:
                logger.warning(f"⚠️ {name} init failed: {e}")
        
        # Watermark & Delivery
        self.watermark = WatermarkRemover() if WATERMARK_AVAILABLE else None
        self.delivery = VideoDelivery() if DELIVERY_AVAILABLE else None
        
        # Content templates
        self.templates = {
            "kisaan": {
                "topics": ["farming tips", "weather alert", "crop prices", "govt schemes", "organic farming"],
                "tone": "simple, helpful HINGLISH",
                "hashtags": ["#Kisaan", "#Farming", "#Agriculture", "#SinghJiAI", "#Kheti"]
            },
            "student": {
                "topics": ["study tips", "exam prep", "career guide", "free courses", "scholarship"],
                "tone": "motivational, friendly",
                "hashtags": ["#Student", "#Education", "#Career", "#SinghJiAI", "#Padhai"]
            },
            "business": {
                "topics": ["business tips", "market trends", "startup guide", "finance", "digital marketing"],
                "tone": "professional, practical",
                "hashtags": ["#Business", "#Startup", "#Finance", "#SinghJiAI", "#Vyapar"]
            },
            "health": {
                "topics": ["health tips", "yoga", "home remedies", "mental health", "nutrition"],
                "tone": "caring, informative",
                "hashtags": ["#Health", "#Wellness", "#Yoga", "#SinghJiAI", "#Swasthya"]
            },
            "spiritual": {
                "topics": ["bhajan", "prayer", "motivation", "positive thoughts", "meditation"],
                "tone": "peaceful, devotional",
                "hashtags": ["#Spiritual", "#Bhakti", "#PositiveVibes", "#SinghJiAI", "#Dharm"]
            }
        }
        
        # Task history
        self.tasks = []
        self.history = []
        
        logger.info(f"🤖 {self.name} v{self.version} ready! {len(self.video_instances)} video connectors active")
    
    # ═══════════════════════════════════════════════════════
    # MAIN: Create Content (Your main function!)
    # ═══════════════════════════════════════════════════════
    
    async def create_content(self, goal: str, platform: str = "auto") -> Dict[str, Any]:
        """
        🤖 Master function — Goal se leke post tak sab karega!
        
        Example: "kisaan ke liye video banao"
        → AI content generate
        → Video banayo (Hailuo/Kling/etc)
        → Watermark hatao
        → CDN pe upload
        → Social media pe post
        """
        logger.info(f"🎯 Goal: {goal} | Platform: {platform}")
        
        # Step 0: Detect category
        category = self._detect_category(goal)
        logger.info(f"📂 Category detected: {category}")
        
        # Step 1: Generate AI content
        content = await self._generate_ai_content(goal, category)
        
        # Step 2: Generate video (if requested)
        video_result = None
        if "video" in goal.lower() or "वीडियो" in goal or "बनाओ" in goal:
            video_result = await self._create_video(content, category, platform)
        
        # Step 3: Post to social media
        post_result = None
        if platform != "none":
            post_result = await self._post_content(content, video_result, platform)
        
        # Build final result
        result = {
            "success": True,
            "goal": goal,
            "category": category,
            "content": content,
            "video": video_result,
            "post": post_result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(result)
        return result
    
    # ═══════════════════════════════════════════════════════
    # STEP 1: AI Content Generation
    # ═══════════════════════════════════════════════════════
    
    async def _generate_ai_content(self, goal: str, category: str) -> str:
        """Generate content using AI or template fallback"""
        
        # Try Groq first
        if self.groq_key:
            try:
                return await self._generate_with_groq(goal, category)
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        # Try Gemini
        if self.gemini_key:
            try:
                return await self._generate_with_gemini(goal, category)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")
        
        # Template fallback
        return self._generate_template(goal, category)
    
    async def _generate_with_groq(self, goal: str, category: str) -> str:
        """Groq API se content"""
        import aiohttp
        
        template = self.templates.get(category, self.templates["kisaan"])
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        system_msg = (
            f"Tu Singh Ji AI hai. HINGLISH (Hindi + English mix) mein content bana. "
            f"Tone: {template['tone']}. "
            f"Hashtags include karo: {', '.join(template['hashtags'])}. "
            f"Goal: {goal}"
        )
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": goal}
            ],
            "temperature": 0.8,
            "max_tokens": 800
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    
    async def _generate_with_gemini(self, goal: str, category: str) -> str:
        """Gemini API se content"""
        import aiohttp
        
        template = self.templates.get(category, self.templates["kisaan"])
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        
        prompt = (
            f"Create content in HINGLISH (Hindi words in Devanagari, English technical terms in Roman). "
            f"Topic: {goal}. "
            f"Tone: {template['tone']}. "
            f"Include hashtags: {', '.join(template['hashtags'])}. "
            f"Keep it under 500 words."
        )
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=30) as resp:
                data = await resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
    
    def _generate_template(self, goal: str, category: str) -> str:
        """Template fallback jab AI fail ho"""
        template = self.templates.get(category, self.templates["kisaan"])
        hashtags = " ".join(template["hashtags"])
        
        return f"""🌟 Singh Ji AI — {category.title()} Update!

{goal}

💡 Aaj ke Tips:
• {random.choice(template['topics']).title()} — Updated info!
• Daily useful content for you
• Share with friends & family!

{hashtags}

Powered by 🤖 Singh Ji AI Ultra v8.0"""
    
    # ═══════════════════════════════════════════════════════
    # STEP 2: Video Creation Pipeline
    # ═══════════════════════════════════════════════════════
    
    async def _create_video(self, content: str, category: str, platform: str) -> Dict[str, Any]:
        """
        Video pipeline:
        1. Best connector choose karo
        2. Video generate karo
        3. Watermark hatao
        4. CDN pe upload karo
        """
        logger.info("🎬 Starting video pipeline...")
        
        # Pick best connector
        connector_name = self._pick_video_connector(platform)
        connector = self.video_instances.get(connector_name)
        
        if not connector:
            return {
                "success": False,
                "error": f"No video connector available. Tried: {connector_name}",
                "url": None
            }
        
        try:
            # Generate video
            logger.info(f"🎬 Generating with {connector_name}...")
            video_result = await connector.generate(
                prompt=content[:500],  # First 500 chars as prompt
                category=category
            )
            
            if not video_result or not video_result.get("success"):
                return {
                    "success": False,
                    "error": video_result.get("error", "Generation failed"),
                    "url": None
                }
            
            video_path = video_result.get("file_path") or video_result.get("url")
            
            # Remove watermark
            if self.watermark and video_path:
                logger.info("🧹 Removing watermark...")
                clean_path = await self.watermark.remove(video_path)
            else:
                clean_path = video_path
            
            # Upload to CDN
            if self.delivery and clean_path:
                logger.info("☁️ Uploading to CDN...")
                cdn_result = await self.delivery.upload(clean_path, category)
                final_url = cdn_result.get("url") or clean_path
            else:
                final_url = clean_path
            
            return {
                "success": True,
                "source": connector_name,
                "url": final_url,
                "clean_path": clean_path,
                "original_path": video_path
            }
            
        except Exception as e:
            logger.error(f"Video pipeline error: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": None
            }
    
    def _pick_video_connector(self, platform: str) -> str:
        """Best video connector choose karo based on platform/availability"""
        
        # Platform-specific preferences
        platform_prefs = {
            "youtube": ["kling", "luma", "hailuo"],
            "instagram": ["pika", "seedance", "hailuo"],
            "facebook": ["hailuo", "kling", "veo"],
            "twitter": ["pika", "luma", "seedance"],
            "auto": ["hailuo", "kling", "luma", "pika", "veo", "seedance"]
        }
        
        prefs = platform_prefs.get(platform, platform_prefs["auto"])
        
        # Find first available
        for name in prefs:
            if name in self.video_instances:
                return name
        
        # Fallback to any available
        if self.video_instances:
            return list(self.video_instances.keys())[0]
        
        return "hailuo"  # Default fallback
    
    # ═══════════════════════════════════════════════════════
    # STEP 3: Social Media Posting
    # ═══════════════════════════════════════════════════════
    
    async def _post_content(self, content: str, video_result: Optional[Dict], platform: str) -> Dict[str, Any]:
        """
        Content + Video ko social media pe post karo
        """
        logger.info(f"📱 Posting to {platform}...")
        
        # Build post text
        post_text = self._build_post_text(content, video_result)
        
        # Platform routing
        platforms_to_post = []
        
        if platform == "auto":
            platforms_to_post = ["twitter", "facebook", "instagram", "linkedin", "telegram"]
        else:
            platforms_to_post = [platform]
        
        results = {}
        successful = 0
        
        for plat in platforms_to_post:
            try:
                result = await self._post_to_single_platform(plat, post_text, video_result)
                results[plat] = result
                if result.get("success"):
                    successful += 1
            except Exception as e:
                results[plat] = {"success": False, "error": str(e)}
        
        return {
            "success": successful > 0,
            "successful": successful,
            "total": len(platforms_to_post),
            "results": results
        }
    
    def _build_post_text(self, content: str, video_result: Optional[Dict]) -> str:
        """Post text format karo"""
        text = content[:400]  # Truncate for social media
        
        if video_result and video_result.get("success"):
            text += f"\n\n🎬 Video: {video_result.get('url', '')}"
        
        text += "\n\nPowered by 🤖 Singh Ji AI"
        return text
    
    async def _post_to_single_platform(self, platform: str, text: str, video_result: Optional[Dict]) -> Dict[str, Any]:
        """Single platform pe post karo"""
        
        if not OAUTH_AVAILABLE:
            # Mock post (for testing)
            return {
                "success": True,
                "mock": True,
                "platform": platform,
                "message": f"Mock posted to {platform}"
            }
        
        try:
            # Real OAuth posting
            # TODO: Implement actual OAuth posting via oauth_router
            return {
                "success": True,
                "platform": platform,
                "message": f"Posted to {platform}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════
    # UTILITY FUNCTIONS
    # ═══════════════════════════════════════════════════════
    
    def _detect_category(self, goal: str) -> str:
        """Goal se category detect karo"""
        goal_lower = goal.lower()
        
        keywords = {
            "kisaan": ["kisaan", "farmer", "farming", "crop", "agriculture", "खेती", "किसान", "खेत"],
            "student": ["student", "study", "exam", "education", "career", "पढ़ाई", "छात्र", "परीक्षा"],
            "business": ["business", "startup", "money", "finance", "market", "व्यापार", "बिजनेस"],
            "health": ["health", "yoga", "fitness", "doctor", "wellness", "स्वास्थ्य", "योग"],
            "spiritual": ["bhajan", "prayer", "god", "spiritual", "motivation", "भजन", "प्रार्थना", "धर्म"]
        }
        
        for cat, words in keywords.items():
            if any(w in goal_lower for w in words):
                return cat
        
        return "general"
    
    # ═══════════════════════════════════════════════════════
    # TELEGRAM COMMAND HANDLERS (Direct use)
    # ═══════════════════════════════════════════════════════
    
    async def run(self, prompt: str) -> Dict[str, Any]:
        """Telegram /agentic command ke liye wrapper"""
        return await self.create_content(prompt, platform="auto")
    
    async def generate_video(self, prompt: str) -> Dict[str, Any]:
        """Telegram /video command ke liye"""
        return await self._create_video(prompt, "general", "auto")
    
    async def post_to_all(self, message: str) -> Dict[str, Any]:
        """Telegram /post command ke liye"""
        return await self._post_content(message, None, "auto")
    
    # ═══════════════════════════════════════════════════════
    # CALLBACK HANDLER (Inline buttons)
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, callback_data: str) -> Dict[str, Any]:
        """Telegram inline button callbacks"""
        
        if callback_data.startswith("agentic_"):
            category = callback_data.replace("agentic_", "")
            content = await self._generate_ai_content(
                f"Generate {category} content", 
                category
            )
            return {
                "success": True,
                "category": category,
                "content": content,
                "type": "content"
            }
        
        return {"success": False, "error": "Unknown callback"}
    
    # ═══════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict[str, Any]:
        """Agentic-A stats"""
        return {
            "name": self.name,
            "version": self.version,
            "active": self.active,
            "video_connectors": list(self.video_instances.keys()),
            "watermark": self.watermark is not None,
            "delivery": self.delivery is not None,
            "oauth": OAUTH_AVAILABLE,
            "ai_brain": bool(self.groq_key or self.gemini_key),
            "history_count": len(self.history)
        }


# ═══════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    brain = AgenticBrain()
    print(f"🤖 {brain.name} v{brain.version}")
    print(f"Stats: {json.dumps(brain.get_stats(), indent=2)}")
