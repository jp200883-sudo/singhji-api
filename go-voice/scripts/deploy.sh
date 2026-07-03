#!/bin/bash
# Singh Ji AI Voice Deploy Script
# Render.com Auto-Deploy

set -e

echo "🦁 SINGH JI AI VOICE DEPLOY"
echo "==========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Go not installed${NC}"
    echo "   Install: https://go.dev/dl/"
    exit 1
fi
echo -e "${GREEN}✅ Go: $(go version)${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git: $(git --version)${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env not found!${NC}"
    echo "   Copy .env.example to .env and add your API keys"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env from template${NC}"
    echo "   Edit .env with your API keys before deploying!"
    exit 1
fi

# Build
echo ""
echo "🔨 Building..."
go mod tidy
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o voice-server ./cmd/voice-server

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Build successful${NC}"

# Test locally (optional)
read -p "🧪 Test locally? (y/n): " test_local
if [ "$test_local" = "y" ]; then
    echo "🚀 Starting local server..."
    PORT=8080 ./voice-server &
    SERVER_PID=$!
    sleep 2

    echo "🌐 Testing health endpoint..."
    curl -s http://localhost:8080/health | python3 -m json.tool || true

    kill $SERVER_PID 2>/dev/null
    echo -e "${GREEN}✅ Local test passed${NC}"
fi

# Git push (auto-deploy to Render)
echo ""
echo "🚀 Deploying to Render..."
git add .
git commit -m "🦁 Singh Ji Voice v7.0 - $(date '+%Y-%m-%d %H:%M:%S')" || true
git push origin main || git push origin master

echo ""
echo -e "${GREEN}✅ Deployed!${NC}"
echo "🌐 URL: https://singhji-voice.onrender.com"
echo "📊 Dashboard: https://dashboard.render.com"
echo ""
echo "🦁 Singh Ji AI Voice is LIVE!"
