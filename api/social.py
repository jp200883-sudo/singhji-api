# api/social.py
from fastapi import APIRouter, Request
from core.config import FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID

router = APIRouter()
HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client

@router.get("/facebook/status")
async def facebook_status():
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}?access_token={FACEBOOK_ACCESS_TOKEN}&fields=id,name,followers_count"
        resp = await HTTP_CLIENT.get(url)
        data = resp.json()
        if resp.status_code == 200:
            return {"status": "connected", "page": {"id": data.get("id"), "name": data.get("name"), "followers": data.get("followers_count", 0)}}
        return {"error": data.get("error", {}).get("message", "Unknown")}
    except Exception as e:
        return {"error": str(e)}

@router.post("/facebook/post")
async def facebook_post(request: Request):
    if not FACEBOOK_ACCESS_TOKEN:
        return {"error": "FACEBOOK_ACCESS_TOKEN missing"}
    data = await request.json()
    try:
        url = f"https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/feed"
        payload = {"access_token": FACEBOOK_ACCESS_TOKEN, "message": data.get("message", "")}
        resp = await HTTP_CLIENT.post(url, data=payload)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
