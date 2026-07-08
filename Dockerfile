# Railway 2026 - Updated & Tested
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Railway 2026: Dynamic PORT
EXPOSE $PORT

# Start command - Shell form for env vars
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
