
FROM python:3.11-slim

# वर्किंग डायरेक्टरी
WORKDIR /app

# सिस्टम डिपेंडेंसीज़
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python पैकेज इंस्टॉल
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# सारा कोड कॉपी
COPY . .

# पोर्ट एक्सपोज़
EXPOSE ${PORT:-8000}

# 🟢 सही CMD — शेल फॉर्म, $PORT एक्सपांड होगा
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
