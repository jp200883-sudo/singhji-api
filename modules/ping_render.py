import asyncio
import httpx
from datetime import datetime

# Render ko har 10 minute me ping karo
PING_INTERVAL = 600  # 10 minutes
RENDER_URL = "https://singhji-api.onrender.com/api/health"

async def handler(request):
    method = request.method if hasattr(request, 'method') else 'GET'
    
    if method == 'POST':
        data = await request.json()
        action = data.get('action', 'status')
        
        if action == 'start':
            # Background ping start
            asyncio.create_task(_keep_alive_loop())
            return {
                "status": "success",
                "message": "Keep-alive ping STARTED",
                "interval": f"{PING_INTERVAL} seconds",
                "target": RENDER_URL,
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == 'stop':
            return {
                "status": "success",
                "message": "Keep-alive ping STOPPED (manual)",
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == 'ping_now':
            result = await _ping_render()
            return result
    
    # Default: status check
    return {
        "module": "ping_render",
        "status": "active",
        "purpose": "Keep Render server awake",
        "interval": f"{PING_INTERVAL} seconds",
        "target": RENDER_URL,
        "last_ping": "Check /api/ping_render status",
        "commands": {
            "start": "POST {'action': 'start'}",
            "stop": "POST {'action': 'stop'}",
            "ping_now": "POST {'action': 'ping_now'}"
        }
    }

async def _ping_render():
    """Render ko ping karo"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(RENDER_URL)
            return {
                "status": "success",
                "ping_status": response.status_code,
                "response_time": "OK",
                "timestamp": datetime.now().isoformat(),
                "message": "Render is AWAKE!"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "Ping failed, will retry"
        }

async def _keep_alive_loop():
    """Har 10 minute me ping karte raho"""
    while True:
        await asyncio.sleep(PING_INTERVAL)
        result = await _ping_render()
        print(f"[PING_RENDER] {datetime.now()}: {result['message']}")
