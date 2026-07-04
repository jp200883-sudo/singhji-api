# modules/schedule/handler.py

import os
import logging
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'list').strip()
        else:
            body = await request.json()
            action = body.get('action', 'list').strip()
        
        # Schedule data
        schedules = [
            {"id": 1, "title": "Morning Water Supply", "time": "06:00 - 09:00", "days": "Daily", "type": "utility"},
            {"id": 2, "title": "Evening Power Cut", "time": "14:00 - 16:00", "days": "Mon, Wed, Fri", "type": "power"},
            {"id": 3, "title": "Garbage Collection", "time": "07:00 - 08:30", "days": "Tue, Thu, Sat", "type": "sanitation"},
            {"id": 4, "title": "Ration Shop Open", "time": "09:00 - 17:00", "days": "Mon-Sat", "type": "government"},
            {"id": 5, "title": "Bank Hours", "time": "10:00 - 16:00", "days": "Mon-Fri", "type": "banking"}
        ]
        
        if action == 'today':
            today = datetime.now().strftime('%A')
            today_schedules = [s for s in schedules if today in s['days'] or 'Daily' in s['days'] or 'Mon-Sat' in s['days']]
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {"today": today, "schedules": today_schedules}
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {"total": len(schedules), "schedules": schedules}
        })
        
    except Exception as e:
        logger.error(f"Schedule crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
