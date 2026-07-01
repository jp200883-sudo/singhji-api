import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

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
        
        languages = {
            "hi": "हिन्दी",
            "en": "English",
            "bn": "বাংলা",
            "te": "తెలుగు",
            "mr": "मराठी",
            "ta": "தமிழ்",
            "ur": "اردو",
            "gu": "ગુજરાતી",
            "kn": "ಕನ್ನಡ",
            "ml": "മലയാളം",
            "pa": "ਪੰਜਾਬੀ",
            "or": "ଓଡ଼ିଆ",
            "as": "অসমীয়া",
            "ne": "नेपाली",
            "si": "සිංහල",
            "sd": "سنڌي",
            "sa": "संस्कृतम्",
            "kok": "कोंकणी",
            "mni": "ꯃꯤꯇꯩ ꯂꯣꯟ",
            "doi": "डोगरी",
            "bho": "भोजपुरी",
            "mai": "मैथिली",
            "sat": "ᱥᱟᱱᱛᱟᱲᱤ",
            "ks": "کٲشُر",
            "brx": "बड़ो",
            "lus": "Mizo"
        }
        
        if action == 'list':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "total": len(languages),
                    "languages": languages,
                    "default": "hi",
                    "note": "Bhashini API pending approval for translation"
                }
            })
        
        elif action == 'translate':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Translation service coming soon",
                    "available_languages": list(languages.keys()),
                    "status": "Bhashini approval pending"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["list", "translate"],
                "message": "Use ?action=list or ?action=translate"
            }
        })
        
    except Exception as e:
        logger.error(f"Language hub crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
