# api/ai.py
"""
Singh Ji AI Ultra — Multi-Model AI Brain v9.0
Human-like responses, no emojis, no robotic tone.
Uses Groq + Gemini + Cerebras + HuggingFace, picks the BEST response.
"""

import os
import re
import time
import json
import base64
import tempfile
import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

from core.config import GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY, AVAILABLE_KEYS
from core.cache import _cache_key, _cache_get, _cache_set
from core.memory import _memory_save
from utils.helpers import _b64_too_big

router = APIRouter()
logger = logging.getLogger(__name__)

HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client


# ═══════════════════════════════════════════════════════════════
#  SYSTEM PROMPT — Bilkul Human, Bilkul Desi Dost
# ═══════════════════════════════════════════════════════════════

HUMAN_SYSTEM_PROMPT = """Tu ek asli Indian dost hai. Tu bilkul normal insaan ki tarah baat karta hai.

RULES — Inhe todne pe penalty:
1. KABHI bhi emoji mat use kar (na smiley, na symbol, na kuch)
2. KABHI bhi "main ek AI hoon" / "main aapki madad ke liye yahaan hoon" mat bol
3. Natural Hinglish mein baat kar — jaise WhatsApp pe koi real dost karta hai
4. Short aur to-the-point jawab de. Lambi speech mat de.
5. Agar koi gaali de ya gussa ho toh calmly handle kar, react mat kar jaise robot ho
6. Agar koi cheez pata nahi toh seedha bol "yaar ye nahi pata mujhe" ya "iska idea nahi hai"
7. Kabhi "dhanyavaad", "kripaya", "aapka swaagat hai" jaisa formal mat bol
8. Kabhi "main hamesha aapki seva mein taiyaar hoon" mat bol
9. Baat kar jaise tu koi 25 saal ka desi ladka hai jo tech jaanta hai
10. User ka naam agar pata ho toh use kar, nahi toh "bhai" ya "yaar" bol
11. Agar koi technical sawaal ho toh simple words mein samjha, lecture mat de
12. Kabhi bhi numbered list ya bullet points mat de — normal paragraph mein bol
13. Hinglish mein likh: Hindi words Devanagari mein, English words Roman mein — mix karke
14. Kabhi "---" ya "===" ya separator mat daal
15. Response 2-4 lines se zyada mat kar, chhota aur crisp rakho

EXAMPLES:
- User: "Kya haal hai?"
  Jawab: "Bas bhai chill hai. Tu bata kya chal raha hai?"

- User: "Mera server crash ho gaya"
  Jawab: "Arre yaar, kya error aa raha hai? Logs check kiye? Bata main dekhun."

- User: "AI kya hai?"
  Jawab: "Bhai AI matlab aisa computer jo seekh sakta hai. Jaise tu phone pe face unlock karta hai, woh bhi AI hi hai."

- User: "Tum kaam nahi kar rahe"
  Jawab: "Haan yaar thoda system slow chal raha hai. Dobara try kar, ab theek ho jayega."

- User: "Mujhe gussa aa raha hai"
  Jawab: "Chhod na yaar, gussa se kuch nahi hoga. Thoda paani pi, fresh ho jaa."""


# ═══════════════════════════════════════════════════════════════
#  RESPONSE JUDGE — Kaunsa jawab sabse human-like hai
# ═══════════════════════════════════════════════════════════════

@dataclass
class ScoredResponse:
    source: str
    text: str
    latency: float
    quality_score: float = 0.0
    human_score: float = 0.0


class ResponseJudge:
    """Scores how human-like a response is. Higher = more human."""

    ROBOTIC_PATTERNS = [
        r"main ek\s+ai\b", r"main ek\s+artificial",
        r"language model", r"llm\b", r"ai model",
        r"dhanyavaad", r"kripaya", r"aapka swaagat",
        r"main aapki\s+madad", r"main aapki\s+sahayata",
        r"main hamesha", r"main yahaan\s+hoon",
        r"aapki seva mein", r"kya main aapki",
        r"as an ai", r"i am an ai", r"i don't have",
        r"i cannot", r"i'm unable to", r"i apologize",
        r"i'm sorry", r"i regret", r"i am unable",
        r"how can i help", r"how may i assist",
        r"is there anything else", r"feel free to ask",
    ]

    NATURAL_WORDS = [
        "bhai", "yaar", "dost", "samajh", "pata", "chhod",
        "dekh", "sach", "matlab", "bas", "theek", "hoga",
        "kar le", "chal", "ruk", "sun", "arre", "abe",
        "kya baat", "mast", "bindaas", "jhakaas", "bawaal",
        "haina", "na", "toh", "hi", "hai", "tha", "thi",
        "kya", "kaise", "kyun", "kab", "kahan", "kaun",
        "arey", "han", "nahi", "haan", "hmm", "acha",
        "thik", "sahi", "galat", "badiya", "bekar"
    ]

    @classmethod
    def score(cls, text: str, latency: float) -> float:
        score = 60.0  # Base score
        text_lower = text.lower()

        # Penalty for robotic phrases
        for pattern in cls.ROBOTIC_PATTERNS:
            if re.search(pattern, text_lower):
                score -= 15

        # Bonus for natural words
        for word in cls.NATURAL_WORDS:
            if word in text_lower:
                score += 4

        # Penalty for emojis / Unicode symbols
        emoji_count = sum(1 for ch in text if ord(ch) > 127 and not (0x0900 <= ord(ch) <= 0x097F))
        score -= emoji_count * 10

        # Penalty for ASCII smileys
        smiley_count = len(re.findall(r'[:;]-?[)(DdPpSsOo@#$%^&*]', text))
        score -= smiley_count * 15

        # Penalty for excessive punctuation
        if text.count('!') > 2 or text.count('?') > 3:
            score -= 10

        # Bonus for Hinglish (Devanagari + ASCII mix)
        dev_chars = len(re.findall(r'[\u0900-\u097F]', text))
        ascii_chars = len(re.findall(r'[a-zA-Z]', text))
        if dev_chars > 3 and ascii_chars > 3:
            score += 12  # Good Hinglish

        # Penalty for too short or too long
        words = text.split()
        if len(words) < 3:
            score -= 25
        elif len(words) > 80:
            score -= 15
        elif 10 <= len(words) <= 40:
            score += 8  # Sweet spot

        # Penalty for code blocks (unless asked)
        if "```" in text:
            score -= 10

        # Penalty for numbered lists / bullets
        if re.search(r'^(\d+[.\)]|[-•*])\s', text, re.MULTILINE):
            score -= 8

        # Penalty for high latency
        score -= latency * 1.5

        # Penalty for repetitive text
        if len(words) > 5:
            unique_ratio = len(set(w.lower() for w in words)) / len(words)
            if unique_ratio < 0.5:
                score -= 20

        return max(0, min(100, score))


# ═══════════════════════════════════════════════════════════════
#  RESPONSE CLEANER — Emoji, robotic text hatao
# ═══════════════════════════════════════════════════════════════

def clean_response(text: str) -> str:
    """Remove all robot-like stuff from response."""
    if not text:
        return "Haan bhai, kuch toh bola lekin samajh nahi aaya. Dobara bol."

    # Remove emojis and non-Devanagari Unicode symbols
    cleaned = []
    for ch in text:
        code = ord(ch)
        # Keep ASCII, Devanagari, basic punctuation, whitespace
        if code <= 127 or (0x0900 <= code <= 0x097F):
            cleaned.append(ch)
        elif ch in '.,!?;:'"()- \\n\t':
            cleaned.append(ch)
        # Skip everything else (emojis, symbols, etc.)
    text = ''.join(cleaned)

    # Remove ASCII smileys
    text = re.sub(r'[:;]-?[)(DdPpSsOo@#$%^&*]', '', text)

    # Remove robotic phrases
    robotic_replacements = [
        (r"(?i)main ek\s+ai\s+hoon?\.?", ""),
        (r"(?i)main ek\s+artificial\s+intelligence\s+hoon?\.?", ""),
        (r"(?i)main aapki\s+(madad|sahayata)\s+ke\s+liye\s+yahaan\s+hoon?\.?", ""),
        (r"(?i)main hamesha\s+aapki\s+(madad|sahayata)\s+ke\s+liye\s+taiyaar\s+hoon?\.?", ""),
        (r"(?i)aapka\s+swaagat\s+hai\.?", ""),
        (r"(?i)dhanyavaad\s*,?\s*", ""),
        (r"(?i)kripaya\s*,?\s*", ""),
        (r"(?i)main\s+yahaan\s+hoon\s*,?\s*", ""),
        (r"(?i)as\s+an\s+ai\s*,?\s*", ""),
        (r"(?i)i\s+am\s+an\s+ai\s*,?\s*", ""),
        (r"(?i)i\s+don't\s+have\s+personal\s+experiences\s*,?\s*", ""),
        (r"(?i)i\s+apologize\s*,?\s*", "arre koi baat nahi, "),
        (r"(?i)i\s+cannot\s*,?\s*", "main nahi kar sakta, "),
        (r"(?i)i'm\s+unable\s+to\s*,?\s*", "main nahi kar pa raha, "),
        (r"(?i)i\s+am\s+unable\s+to\s*,?\s*", "main nahi kar pa raha, "),
        (r"(?i)how\s+can\s+i\s+assist\s+you\s*\??", "bata kya chahiye?"),
        (r"(?i)how\s+may\s+i\s+help\s+you\s*\??", "bata kya kaam hai?"),
        (r"(?i)is\s+there\s+anything\s+else\s*\??", "aur kuch chahiye toh bata."),
        (r"(?i)feel\s+free\s+to\s+ask\s*,?\s*", ""),
    ]

    for pattern, replacement in robotic_replacements:
        text = re.sub(pattern, replacement, text)

    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^[=-]{3,}$', '', text, flags=re.MULTILINE)

    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()


# ═══════════════════════════════════════════════════════════════
#  MULTI-MODEL AI BRAIN
# ═══════════════════════════════════════════════════════════════

class MultiAIBrain:
    """Calls multiple AI services and returns the best human-like response."""

    def __init__(self):
        self.timeout = 25  # seconds per call
        self.max_total_time = 18  # seconds total wait

    async def _call_groq(self, prompt: str, system: str) -> Optional[ScoredResponse]:
        """Call Groq API (Llama 3.3 70B)."""
        if not HTTP_CLIENT:
            logger.warning("HTTP_CLIENT not set for Groq")
            return None
        start = time.time()
        try:
            resp = await HTTP_CLIENT.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.75,
                    "max_tokens": 400,
                    "top_p": 0.92,
                    "frequency_penalty": 0.3,
                    "presence_penalty": 0.2
                },
                timeout=self.timeout
            )
            result = resp.json()
            if "choices" not in result:
                logger.warning(f"Groq error: {result}")
                return None
            text = result["choices"][0]["message"]["content"]
            text = clean_response(text)
            latency = time.time() - start
            human_score = ResponseJudge.score(text, latency)
            return ScoredResponse("groq", text, latency, human_score=human_score)
        except Exception as e:
            logger.warning(f"Groq failed: {e}")
            return None

    async def _call_gemini(self, prompt: str, system: str) -> Optional[ScoredResponse]:
        """Call Google Gemini 1.5 Flash."""
        if not HTTP_CLIENT:
            logger.warning("HTTP_CLIENT not set for Gemini")
            return None
        start = time.time()
        try:
            url = (f"https://generativelanguage.googleapis.com/v1beta/"
                   f"models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}")
            resp = await HTTP_CLIENT.post(
                url,
                json={
                    "contents": [{
                        "parts": [{
                            "text": f"{system}\n\nUser ne bola: {prompt}\n\n"
                                    f"Jawab do bilkul natural Hinglish mein. "
                                    f"Koi emoji mat daal. 2-4 lines mein jawab do."
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.75,
                        "maxOutputTokens": 400,
                        "topP": 0.92
                    }
                },
                timeout=self.timeout
            )
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = clean_response(text)
            latency = time.time() - start
            human_score = ResponseJudge.score(text, latency)
            return ScoredResponse("gemini", text, latency, human_score=human_score)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")
            return None

    async def _call_cerebras(self, prompt: str, system: str) -> Optional[ScoredResponse]:
        """Call Cerebras API."""
        if not HTTP_CLIENT or not CEREBRAS_API_KEY:
            return None
        start = time.time()
        try:
            resp = await HTTP_CLIENT.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.75,
                    "max_tokens": 400,
                    "top_p": 0.92
                },
                timeout=self.timeout
            )
            result = resp.json()
            if "choices" not in result:
                return None
            text = result["choices"][0]["message"]["content"]
            text = clean_response(text)
            latency = time.time() - start
            human_score = ResponseJudge.score(text, latency)
            return ScoredResponse("cerebras", text, latency, human_score=human_score)
        except Exception as e:
            logger.warning(f"Cerebras failed: {e}")
            return None

    async def _call_huggingface(self, prompt: str, system: str) -> Optional[ScoredResponse]:
        """Call Hugging Face Inference API (fallback)."""
        hf_key = os.getenv("HUGGINGFACE_API_KEY", "")
        if not HTTP_CLIENT or not hf_key:
            return None
        start = time.time()
        try:
            url = ("https://api-inference.huggingface.co/models/"
                   "mistralai/Mistral-7B-Instruct-v0.3")
            full_prompt = f"<s>[INST] {system}\n\nUser: {prompt} [/INST]"
            resp = await HTTP_CLIENT.post(
                url,
                headers={"Authorization": f"Bearer {hf_key}"},
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 400,
                        "temperature": 0.75,
                        "return_full_text": False,
                        "top_p": 0.92
                    }
                },
                timeout=self.timeout
            )
            result = resp.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", "")
                text = clean_response(text)
                latency = time.time() - start
                human_score = ResponseJudge.score(text, latency)
                return ScoredResponse("huggingface", text, latency, human_score=human_score)
            return None
        except Exception as e:
            logger.warning(f"HF failed: {e}")
            return None

    async def _call_local(self, prompt: str, system: str) -> Optional[ScoredResponse]:
        """Call local AI server if configured."""
        local_url = os.getenv("LOCAL_AI_URL", "")
        if not HTTP_CLIENT or not local_url:
            return None
        start = time.time()
        try:
            resp = await HTTP_CLIENT.post(
                local_url,
                json={
                    "prompt": f"{system}\n\nUser: {prompt}\n\nJawab:",
                    "max_tokens": 400,
                    "temperature": 0.75
                },
                timeout=self.timeout
            )
            result = resp.json()
            text = result.get("response", result.get("text", ""))
            text = clean_response(text)
            latency = time.time() - start
            human_score = ResponseJudge.score(text, latency)
            return ScoredResponse("local", text, latency, human_score=human_score)
        except Exception as e:
            logger.warning(f"Local AI failed: {e}")
            return None

    async def get_best_response(self, prompt: str, user_id: str = "anonymous") -> Dict:
        """
        Call ALL available AI models concurrently.
        Pick the response with highest human-likeness score.
        """
        if not HTTP_CLIENT:
            return {
                "status": "error",
                "response": "Bhai HTTP client set nahi hai. Server restart kar.",
                "source": "NO_HTTP_CLIENT"
            }

        # Build system prompt with user context
        system = HUMAN_SYSTEM_PROMPT

        # Prepare all API calls
        tasks = []
        sources = []

        if GROQ_API_KEY:
            tasks.append(self._call_groq(prompt, system))
            sources.append("groq")
        if GEMINI_API_KEY:
            tasks.append(self._call_gemini(prompt, system))
            sources.append("gemini")
        if CEREBRAS_API_KEY:
            tasks.append(self._call_cerebras(prompt, system))
            sources.append("cerebras")
        if os.getenv("HUGGINGFACE_API_KEY"):
            tasks.append(self._call_huggingface(prompt, system))
            sources.append("huggingface")
        if os.getenv("LOCAL_AI_URL"):
            tasks.append(self._call_local(prompt, system))
            sources.append("local")

        if not tasks:
            return {
                "status": "error",
                "response": "Bhai koi AI service available nahi hai. API keys check kar.",
                "source": "NONE"
            }

        # Run all calls concurrently, with overall timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.max_total_time
            )
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "response": "Bhai sab AI services slow hain. Thodi der baad try kar.",
                "source": "TIMEOUT"
            }

        # Filter valid responses
        valid_responses: List[ScoredResponse] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"{sources[i]} threw exception: {result}")
                continue
            if result is None or not result.text or not result.text.strip():
                continue
            valid_responses.append(result)

        if not valid_responses:
            return {
                "status": "error",
                "response": "Bhai sab AI services down hain. Thodi der baad try kar.",
                "source": "ALL_FAILED"
            }

        # Sort by human-likeness score (highest first)
        valid_responses.sort(key=lambda r: r.human_score, reverse=True)

        best = valid_responses[0]
        runners_up = valid_responses[1:3]  # Next 2 best

        # Log the competition
        logger.info("=== AI RESPONSE COMPETITION ===")
        for i, r in enumerate(valid_responses):
            marker = "[WIN]" if i == 0 else "[   ]"
            logger.info(f"{marker} [{r.source}] HumanScore={r.human_score:.1f} | "
                       f"Latency={r.latency:.2f}s | Len={len(r.text)} | "
                       f"Text: {r.text[:80]}...")

        # Save to memory
        try:
            await _memory_save(
                f"chat:{user_id}:{int(time.time())}",
                {
                    "prompt": prompt,
                    "response": best.text,
                    "winner": best.source,
                    "all_scores": {r.source: r.human_score for r in valid_responses},
                    "runners_up": [r.text for r in runners_up]
                }
            )
        except Exception as e:
            logger.warning(f"Memory save failed: {e}")

        return {
            "status": "success",
            "model": best.source,
            "response": best.text,
            "source": f"{best.source.upper()}_LIVE",
            "human_score": round(best.human_score, 1),
            "latency_sec": round(best.latency, 2),
            "all_sources": [r.source for r in valid_responses],
            "all_scores": {r.source: round(r.human_score, 1) for r in valid_responses}
        }


# Singleton
_brain_instance = None

def get_brain() -> MultiAIBrain:
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = MultiAIBrain()
    return _brain_instance


# ═══════════════════════════════════════════════════════════════
#  STANDALONE HELPER — Direct use without class
# ═══════════════════════════════════════════════════════════════

async def ask(prompt: str, user_id: str = "anonymous") -> str:
    """Simple helper — just returns the best response text."""
    brain = get_brain()
    result = await brain.get_best_response(prompt, user_id)
    if result.get("status") == "success":
        return result.get("response", "")
    return result.get("response", "Bhai kuch gadbad ho gayi.")


# ═══════════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/api/chat")
async def ai_chat(request: Request):
    """Main chat endpoint — uses multi-model brain."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "response": "Bhai JSON body bhej."}
        )

    prompt = data.get("prompt", "").strip()
    model = data.get("model", "auto")
    user_id = data.get("user_id", "anonymous")

    if not prompt:
        return {"status": "error", "response": "Bhai kuch toh likh pehle."}

    # Check for personal/sensitive info
    personal_kw = ["password", "otp", "secret", "aadhar", "pan", "bank", "cvv", "pin", "upi"]
    is_personal = any(kw in prompt.lower() for kw in personal_kw)

    # Try cache first (only for non-personal)
    cache_key = None
    if not is_personal:
        cache_key = _cache_key("ai_chat", model, prompt[:120])
        try:
            cached = await _cache_get(cache_key)
            if cached:
                cached["source"] = "CACHE"
                cached["human_score"] = 99.0
                return cached
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")

    # Get best response from multi-model brain
    brain = get_brain()
    result = await brain.get_best_response(prompt, user_id)

    # Cache if successful and not personal
    if result.get("status") == "success" and not is_personal and cache_key:
        try:
            await _cache_set(cache_key, result, ttl=3600)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    return result


# ---- WHISPER ----
_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            logger.info(f"Loading Whisper ({model_size})...")
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("Whisper loaded")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")
            return None
    return _whisper_model

def _transcribe_sync(audio_bytes: bytes, suffix: str, language=None):
    model = _get_whisper_model()
    if model is None:
        return None
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, info = model.transcribe(tmp.name, language=language)
        transcript = " ".join(seg.text.strip() for seg in segments)
    return transcript, info.language, info.language_probability


@router.post("/api/whisper/transcribe")
async def whisper_transcribe(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    audio_b64 = data.get("audio_base64", "")
    language = data.get("language")
    if not audio_b64:
        return {"error": "audio_base64 required"}
    if _b64_too_big(audio_b64):
        return JSONResponse(status_code=413, content={"error": "Audio too large (max 10MB)"})
    try:
        audio_bytes = base64.b64decode(audio_b64)
        out = await run_in_threadpool(_transcribe_sync, audio_bytes, ".wav", language)
        if out is None:
            return {"error": "Whisper model not available"}
        transcript, detected_lang, lang_prob = out
        return {
            "status": "success",
            "transcript": transcript,
            "detected_language": detected_lang,
            "language_probability": round(lang_prob, 3),
            "source": "WHISPER_LOCAL"
        }
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return {"error": str(e)}


# ---- TTS ----
def _tts_sync(text: str, lang: str) -> bytes:
    from gtts import gTTS
    import io
    tts = gTTS(text=text, lang=lang, slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()


@router.post("/api/tts")
async def text_to_speech(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    text = data.get("text", "")
    lang = data.get("lang", "hi")
    if not text:
        return {"error": "text required"}
    try:
        audio_bytes = await run_in_threadpool(_tts_sync, text, lang)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"status": "success", "audio_base64": audio_b64, "lang": lang, "source": "GTTS_LIVE"}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {"error": str(e)}
