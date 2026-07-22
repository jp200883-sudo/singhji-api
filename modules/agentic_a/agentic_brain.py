# ═══════════════════════════════════════════════════════
# 🤖 AGENTIC-A BRAIN — Singh Ji AI Ultra v8.0
# Auto content generation, video, social media posting
# ═══════════════════════════════════════════════════════

import os
import sys
import json
import time
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Logging setup
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# PATH SETUP — Modules access
# ═══════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, '..')

# Add paths
for path in [MODULES_DIR, os.path.join(MODULES_DIR, 'video_gen'), 
             os.path.join(MODULES_DIR, 'oauth_connector')]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ═══════════════════════════════════════════════════════
# IMPORTS — Try to load existing modules
# ═══════════════════════════════════════════════════════

VIDEO_GEN_AVAILABLE = False
OAUTH_AVAILABLE = False
AI_BRAIN_AVAILABLE = False

# Try video generation modules
try:
    from video_gen.hailuo import generate_video as hailuo_gen
    from video_gen.kling import generate_video as kling_gen
    VIDEO_GEN_AVAILABLE = True
    logger.info("✅ Video gen modules loaded!")
except ImportError as e:
    logger.warning(f"⚠️ Video gen not available: {e}")

# Try OAuth/social media
try:
    from oauth_connector import post_to_platform
    OAUTH_AVAILABLE = True
    logger.info("✅ OAuth connector loaded!")
except ImportError as e:
    logger.warning(f"⚠️ OAuth not available: {e}")

# Try AI brain (Groq/Gemini)
try:
    # Try different AI backends
    import requests
    AI_BRAIN_AVAILABLE = True
    logger.info("✅ AI brain available!")
except ImportError:
    logger.warning("⚠️ AI brain not available")

# ═══════════════════════════════════════════════════════
# 🤖 AGENTIC BRAIN CLASS
# ═══════════════════════════════════════════════════════

class AgenticBrain:
    """
    🤖 Agentic-A Brain — Auto content generation & distribution
    """
    
    def __init__(self):
        self.name = "Agentic-A"
        self.version = "1.0.0"
        self.active = True
        self.tasks = []
        self.history = []
        
        # API Keys (from env)
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.together_key = os.getenv("TOGETHER_API_KEY", "")
        
        # Content templates
        self.templates = {
            "kisaan": {
                "topics": ["farming tips", "weather alert", "crop prices", "govt schemes"],
                "tone": "helpful, simple Hindi",
                "hashtags": ["#Kisaan", "#Farming", "#Agriculture", "#SinghJiAI"]
            },
            "student": {
                "topics": ["study tips", "exam prep", "career guide", "free courses"],
                "tone": "motivational, friendly",
                "hashtags": ["#Student", "#Education", "#Career", "#SinghJiAI"]
            },
            "business": {
                "topics": ["business tips", "market trends", "startup guide", "finance"],
                "tone": "professional, practical",
                "hashtags": ["#Business", "#Startup", "#Finance", "#SinghJiAI"]
            },
            "health": {
                "topics": ["health tips", "yoga", "home remedies", "mental health"],
                "tone": "caring, informative",
                "hashtags": ["#Health", "#Wellness", "#Yoga", "#SinghJiAI"]
            },
            "spiritual": {
                "topics": ["bhajan", "prayer", "motivation", "positive thoughts"],
                "tone": "peaceful, devotional",
                "hashtags": ["#Spiritual", "#Bhakti", "#PositiveVibes", "#SinghJiAI"]
            }
        }
        
        logger.info(f"🤖 {self.name} v{self.version} initialized!")
    
    # ═══════════════════════════════════════════════════════
    # CORE: Run Agentic Task
    # ═══════════════════════════════════════════════════════
    
    async def run(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        🤖 Main entry — Parse goal and execute
        """
        logger.info(f"🎯 Agentic task: {prompt}")
        
        # Detect category from prompt
        category = self._detect_category(prompt)
        
        # Generate content
        content = await self._generate_content(prompt, category)
        
        # Build result
        result = {
            "success": True,
            "goal": prompt,
            "category": category,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # Auto-actions based on intent
        if "video" in prompt.lower() or "वीडियो" in prompt:
            video_result = await self.generate_video(prompt)
            result["actions"].append({"type": "video", "result": video_result})
        
        if "post" in prompt.lower() or "post" in prompt.lower():
            post_result = await self.post_to_all(content[:500])
            result["actions"].append({"type": "post", "result": post_result})
        
        self.history.append(result)
        return result
    
    def _detect_category(self, prompt: str) -> str:
        """Detect content category from prompt"""
        prompt_lower = prompt.lower()
        
        keywords = {
            "kisaan": ["kisaan", "farmer", "farming", "crop", "agriculture", "खेती", "किसान"],
            "student": ["student", "study", "exam", "education", "career", "पढ़ाई", "छात्र"],
            "business": ["business", "startup", "money", "finance", "market", "व्यापार"],
            "health": ["health", "yoga", "fitness", "doctor", "wellness", "स्वास्थ्य"],
            "spiritual": ["bhajan", "prayer", "god", "spiritual", "motivation", "भजन", "प्रार्थना"]
        }
        
        for cat, words in keywords.items():
            if any(w in prompt_lower for w in words):
                return cat
        
        return "general"
    
    # ═══════════════════════════════════════════════════════
    # CONTENT GENERATION
    # ═══════════════════════════════════════════════════════
    
    async def _generate_content(self, prompt: str, category: str) -> str:
        """Generate AI content for the goal"""
        
        template = self.templates.get(category, self.templates["kisaan"])
        
        # Try AI brain first
        if self.groq_key:
            try:
                return await self._generate_with_groq(prompt, template)
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        if self.gemini_key:
            try:
                return await self._generate_with_gemini(prompt, template)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")
        
        # Fallback: Template-based generation
        return self._generate_template_content(prompt, category, template)
    
    async def _generate_with_groq(self, prompt: str, template: Dict) -> str:
        """Generate using Groq API"""
        import aiohttp
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        system_msg = f"You are Singh Ji AI. Create content in Hindi-English mix (HINGLISH). Tone: {template['tone']}. Include hashtags: {', '.join(template['hashtags'])}"
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    
    async def _generate_with_gemini(self, prompt: str, template: Dict) -> str:
        """Generate using Gemini API"""
        import aiohttp
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Create content in HINGLISH (Hindi + English mix). Topic: {prompt}. Tone: {template['tone']}. Include hashtags."
                }]
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
    
    def _generate_template_content(self, prompt: str, category: str, template: Dict) -> str:
        """Fallback template-based content"""
        topics = template["topics"]
        hashtags = " ".join(template["hashtags"])
        
        return f"""🌟 Singh Ji AI — {category.title()} Update!

{prompt}

💡 Tips:
• {random.choice(topics).title()} — Stay updated!
• Daily useful content for you
• Share with friends!

{hashtags}

Powered by 🤖 Singh Ji AI Ultra v8.0"""
    
    # ═══════════════════════════════════════════════════════
    # VIDEO GENERATION
    # ═══════════════════════════════════════════════════════
    
    async def generate_video(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        🎬 Generate video using available providers
        """
        logger.info(f"🎬 Video generation: {prompt}")
        
        if not VIDEO_GEN_AVAILABLE:
            return {
                "success": False,
                "error": "Video generation modules not available",
                "source": None
            }
        
        # Try providers in order
        providers = [
            ("hailuo", hailuo_gen),
            ("kling", kling_gen)
        ]
        
        for name, gen_func in providers:
            try:
                result = await gen_func(prompt, **kwargs)
                if result and result.get("success"):
                    return {
                        "success": True,
                        "source": name,
                        "url": result.get("url"),
                        "prompt": prompt
                    }
            except Exception as e:
                logger.warning(f"{name} failed: {e}")
                continue
        
        # Fallback: Return instructions
        return {
            "success": False,
            "error": "All video providers failed. Check video_gen modules.",
            "source": None
        }
    
    # ═══════════════════════════════════════════════════════
    # SOCIAL MEDIA POSTING
    # ═══════════════════════════════════════════════════════
    
    async def post_to_all(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        📱 Post to all connected social media platforms
        """
        logger.info(f"📱 Posting to all platforms: {message[:50]}...")
        
        platforms = ["twitter", "facebook", "instagram", "linkedin", "telegram_channel"]
        results = {}
        successful = 0
        
        for platform in platforms:
            try:
                if OAUTH_AVAILABLE:
                    result = await post_to_platform(platform, message)
                else:
                    # Mock post (no OAuth available)
                    result = {"success": True, "mock": True, "platform": platform}
                
                results[platform] = result
                if result.get("success"):
                    successful += 1
                    
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}
        
        return {
            "success": successful > 0,
            "successful": successful,
            "total": len(platforms),
            "results": results
        }
    
    async def post_to_platform(self, platform: str, message: str) -> Dict[str, Any]:
        """Post to specific platform"""
        try:
            if OAUTH_AVAILABLE:
                return await post_to_platform(platform, message)
            return {"success": False, "error": "OAuth not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════
    # SCHEDULED / BACKGROUND TASKS
    # ═══════════════════════════════════════════════════════
    
    async def schedule_content(self, category: str, time_str: str, **kwargs) -> Dict[str, Any]:
        """Schedule auto content generation"""
        task = {
            "id": f"task_{int(time.time())}",
            "category": category,
            "time": time_str,
            "status": "scheduled",
            "created": datetime.now().isoformat()
        }
        self.tasks.append(task)
        return task
    
    async def run_scheduled(self):
        """Run all scheduled tasks"""
        now = datetime.now().strftime("%H:%M")
        for task in self.tasks:
            if task["time"] == now and task["status"] == "scheduled":
                task["status"] = "running"
                content = await self._generate_content(
                    f"Auto {task['category']} content", 
                    task["category"]
                )
                await self.post_to_all(content)
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
    
    # ═══════════════════════════════════════════════════════
    # CALLBACK HANDLERS (For Telegram inline buttons)
    # ═══════════════════════════════════════════════════════
    
    async def handle_callback(self, callback_data: str) -> Dict[str, Any]:
        """Handle inline button callbacks"""
        
        if callback_data.startswith("agentic_"):
            category = callback_data.replace("agentic_", "")
            content = await self._generate_content(
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
    # STATS & INFO
    # ═══════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Agentic-A stats"""
        return {
            "name": self.name,
            "version": self.version,
            "active": self.active,
            "tasks_scheduled": len(self.tasks),
            "history_count": len(self.history),
            "video_gen": VIDEO_GEN_AVAILABLE,
            "oauth": OAUTH_AVAILABLE,
            "ai_brain": AI_BRAIN_AVAILABLE
        }


# ═══════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test run
    brain = AgenticBrain()
    print(f"🤖 {brain.name} v{brain.version} ready!")
    print(f"Stats: {json.dumps(brain.get_stats(), indent=2)}")
