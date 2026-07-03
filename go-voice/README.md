# 🦁 SINGH JI AI VOICE SERVER v7.0

**Zero Cost Voice AI - 306+ Languages, ₹0 Budget**

Go = 10x Speed | Python = 60 Modules | Hybrid = Rocket 🚀

## ⚡ Features

- 🎙️ **STT**: Whisper (offline) → Vosk (offline) → Google STT (free)
- 🔊 **TTS**: Minimax (free+clone) → Edge TTS (no key) → Piper/Kokoro (offline)
- 🌐 **Translation**: IndicTrans2 (22 Indian) → SeamlessM4T (100+) → Google (free)
- 🧠 **AI Brain**: Groq (fast) → Gemini (smart) → Local LLM (offline)
- 🎭 **Voice Clone**: Coqui XTTS v2 → Fish Audio → Orpheus
- 🌐 **WebSocket**: 10,000+ concurrent streams
- 💾 **Storage**: Supabase (free tier)

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/singhji-ai/singhji-voice-go.git
cd singhji-voice-go

# 2. Install dependencies
go mod tidy

# 3. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run
PORT=8080 go run ./cmd/voice-server

# 5. Test
curl http://localhost:8080/health
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ws/voice` | WS | Real-time voice streaming |
| `/api/v1/tts` | POST | Text-to-Speech |
| `/api/v1/stt` | POST | Speech-to-Text |
| `/api/v1/translate` | POST | Translation |
| `/api/v1/ai-voice` | POST | AI Chat + Voice |
| `/api/v1/voice-clone` | POST | Voice Cloning |
| `/api/v1/history/:id` | GET | Voice History |

## 🔌 WebSocket Protocol

```json
// Client -> Server
{"type": "chat", "text": "Hello", "language": "hi", "voice": "default"}

// Server -> Client
{"type": "chat_response", "text": "Namaste!", "audio": "base64...", "latency_ms": 150}
```

## 🛠️ Deploy to Render

1. Push to GitHub
2. Connect repo in Render
3. Set environment variables
4. Deploy!

## 🦁 Singh Ji Guarantee

> "Go mein voice — 10x speed, 10,000+ concurrent, 306 languages, ₹0 cost!"
