!/bin/sh
set -e

echo "🦁 Singh Ji AI Ultra v8.0 Starting..."
echo "PORT env: $PORT"

# Use Railway's PORT or default to 8000
APP_PORT="${PORT:-8000}"
echo "Using port: $APP_PORT"

# Start uvicorn
exec uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"
