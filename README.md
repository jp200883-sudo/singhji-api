# 🦁 Singh Ji AI Ultra v8.3 FINAL

AI-powered multi-module assistant API with voice, payments, social media automation and Hindi/Indic language support. Deployed on **Render** (also Railway-ready).

[![Deploy](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi)](https://fastapi.tiangolo.com)

---

## ✨ Features

- 🎙️ **Voice** — ASR (Whisper + Bhashini) & TTS (Piper / Edge / GTTS / Bhashini)
- 🤖 **AI Swarm** — 42+ modules, multi-LLM chain (OpenAI / Groq / Gemini)
- 💬 **Telegram Bot** — webhook-based, master scheduler with broadcasts
- 📱 **Mini Program Portal** — embedded client portal
- 🗄️ **Database** — Supabase (PostgreSQL) + in-memory cache & memory layer
- 💳 **Payments** — Stripe + Razorpay + agent payment app
- 📲 **Social Media Agent** — Facebook / YouTube / Instagram / Twitter automation
- 🛡️ **Rate Limiting** — global + strict tiers (60s retry on 429)
- 📹 **Video tools**, 🌱 plant ID, 🧠 scheduler, 📊 admin panel

---

## 🏗️ Architecture

```javascript
Telegram / Web / Mini Program
        │
        ▼
   FastAPI (main.py)  ── Rate Limit Middleware ── CORS
        │
        ├── /api/*      → ai, chat, tts, whisper, bhashini, plant
        ├── /api/admin  → admin panel
        ├── /api/payment → Stripe / Razorpay
        ├── /api/social → social agent
        ├── /api/video  → video tools
        ├── /api/agent  → agent payment app
        ├── /telegram   → Telegram webhook
        ├── /mini program portal
        └── go-voice/   → Go voice server (separate service)
        │
   Supabase (users, prefs)  +  Swarm  +  Master Scheduler
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/jp200883-sudo/singhji-api.git
cd singhji-api
pip install -r requirements.txt
cp .env.example .env   # ← fill your keys
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` for Swagger UI.

---

## 🔌 API Overview

| Endpoint | Description |
| --- | --- |
| `GET /` | Live status — modules, agents, APIs, scheduler, subscribers |
| `GET /health` | Health check |
| `GET /ping` | Liveness ping |
| `POST /api/chat` | AI chat (strict rate limit) |
| `POST /api/whisper/*` | Speech-to-text |
| `POST /api/bhashini/*` | Bhashini translation/TTS/ASR |
| `POST /api/tts` | Text-to-speech |
| `POST /api/plant/*` | Plant identification |
| `/modules/voice` | Voice module (strict rate limit) |
| `/api/ai/*` | AI utilities |
| `/api/admin/*` | Admin panel |
| `/api/payment/*` | Payments |
| `/api/social/*` | Social media agent |
| `/api/video/*` | Video tools |
| `/telegram/*` | Telegram webhook |
| `/api/agent` | Agent payment app |

> ⚡ Strict-rate-limit paths: `/api/chat`, `/api/whisper/`, `/api/bhashini/`, `/api/tts`, `/api/plant/`, `/modules/voice`

---

## 🔐 Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `TELEGRAM_TOKEN` | ✅ | Telegram bot token |
| `APP_URL` | ✅ | Public URL for webhook (https://your-app.onrender.com) |
| `ADMIN_USER_ID` | ✅ | Telegram admin user ID |
| `BHASHINI_USER_ID` | voice | Bhashini account ID |
| `BHASHINI_INFERENCE_API_KEY` | voice | Bhashini inference key |
| `OPENAI_API_KEY` | AI | OpenAI |
| `GROQ_API_KEY` | AI | Groq (fast inference) |
| `GEMINI_API_KEY` | AI | Google Gemini |
| `SUPABASE_URL` / `SUPABASE_KEY` | ✅ | Supabase project |
| `STRIPE_SECRET_KEY` | payments | Stripe |
| `RAZORPAY_KEY_ID/SECRET` | payments | Razorpay |
| `EXTRA_CORS_ORIGINS` | optional | Extra allowed origins, comma-separated |
| `PORT` | auto | Server port (default 8000) |

---

## 🚢 Deployment

### Render (recommended)

`render.yaml` included — connect repo and deploy. Use Docker for ffmpeg/playwright support.

### Railway

`railway.json` included.

### Docker

```bash
docker build -t singhji-api .
docker run -p 8000:8000 --env-file .env singhji-api
```

### Go Voice Server (separate service)

See [`go-voice/README.md`](go-voice/README.md) — deployed independently on Render.

---

## 📁 Structure

```javascript
├── main.py            # FastAPI app entry (v8.3 FINAL)
├── api/               # route modules (ai, admin, payment, video, social)
├── core/              # config, database, rate limit, swarm, scheduler,
│                      # telegram, cache, memory
├── modules/           # feature modules (social_agent, voice, ...)
├── services/ utils/   # shared logic
├── tg_bot/            # Telegram webhook handlers
├── go-voice/          # Go voice server (separate deploy)
├── miniprogram/       # mini program portal
├── templates/         # Jinja2 templates
└── render.yaml railway.json Dockerfile deploy.yml
```

---

## ⚠️ Notes

- Heavy deps (torch CPU, playwright) — use Docker deploy on Render
- Keep `.env` out of git (never commit real keys)
- `static/` folder is expected by `main.py` (auto-skipped if missing)

---

*Built with ❤️ by Singh Ji*
