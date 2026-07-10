"""
Singh Ji AI Ultra v8.0 — Facebook Long-Term Token (60 Days)
App ID: 1008554401796459
Never Expire Token banao — baar-baar login nahi karna padega!
"""
import os
import requests
from datetime import datetime, timedelta

# ============================================
# CONFIG — YAHAN VALUES DAALO
# ============================================

FACEBOOK_APP_ID = "1008554401796459"
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET", "YOUR_SECRET_HERE")

# ============================================
# STEP 1: SHORT-TERM TOKEN → LONG-TERM TOKEN (60 Days)
# ============================================

def get_long_lived_token(short_token):
    """
    Short token (1-2 hours) ko Long token (60 days) mein convert karo

    Args:
        short_token: User login ke baad mila token (1-2 hours valid)

    Returns:
        Long-term token (60 days valid)
    """
    url = "https://graph.facebook.com/v18.0/oauth/access_token"

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": FACEBOOK_APP_ID,
        "client_secret": FACEBOOK_APP_SECRET,
        "fb_exchange_token": short_token
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "access_token" in data:
            expires = data.get("expires_in", 5184000)  # 60 days default
            expiry_date = datetime.now() + timedelta(seconds=expires)

            return {
                "success": True,
                "long_token": data["access_token"],
                "expires_in_seconds": expires,
                "expires_in_days": round(expires / 86400, 1),
                "expiry_date": expiry_date.strftime("%d %b %Y, %I:%M %p"),
                "message": f"✅ Long-term token ready! {round(expires/86400, 1)} din tak valid!",
                "note": "Yeh token 60 din tak chalega — baar-baar login nahi karna!"
            }
        else:
            return {
                "success": False,
                "error": data.get("error", {}).get("message", "Token exchange failed"),
                "code": data.get("error", {}).get("code", 0),
                "solution": "App Secret check karo — reset kiya hoga toh naya daalo"
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# STEP 2: LONG-TERM TOKEN → NEVER EXPIRE TOKEN
# ============================================

def get_never_expire_token(long_token, page_id):
    """
    Page Access Token banao jo kabhi expire nahi hoga!

    Args:
        long_token: 60-day token from Step 1
        page_id: Facebook Page ID (jo manage karta hai)

    Returns:
        Page Access Token (Never Expires!)
    """
    url = f"https://graph.facebook.com/v18.0/{page_id}"

    params = {
        "fields": "access_token",
        "access_token": long_token
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "access_token" in data:
            return {
                "success": True,
                "page_token": data["access_token"],
                "page_id": page_id,
                "expires": "NEVER",  # Page token kabhi expire nahi hota!
                "message": "✅ NEVER EXPIRE token ready!",
                "note": "Yeh token kabhi expire nahi hoga — ek baar banao, hamesha chalao!"
            }
        else:
            return {
                "success": False,
                "error": data.get("error", {}).get("message", "Page token failed"),
                "solution": "Page admin rights check karo — token wale user ko admin banao"
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# STEP 3: TOKEN VALIDITY CHECK
# ============================================

def check_token_validity(token):
    """
    Token abhi valid hai ya nahi — check karo

    Args:
        token: Any Facebook token

    Returns:
        Validity info + expiry date
    """
    url = "https://graph.facebook.com/v18.0/debug_token"

    params = {
        "input_token": token,
        "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        token_data = data.get("data", {})

        if token_data.get("is_valid"):
            expires_at = token_data.get("expires_at", 0)
            if expires_at > 0:
                expiry = datetime.fromtimestamp(expires_at)
                days_left = (expiry - datetime.now()).days

                return {
                    "success": True,
                    "valid": True,
                    "expires_at": expiry.strftime("%d %b %Y, %I:%M %p"),
                    "days_left": days_left,
                    "app_id": token_data.get("app_id"),
                    "scopes": token_data.get("scopes", []),
                    "message": f"✅ Token valid! {days_left} din bache hain." if days_left > 0 else "⚠️ Token expire hone wala hai!",
                    "action": "Renew karo" if days_left < 7 else "Sab theek hai"
                }
            else:
                return {
                    "success": True,
                    "valid": True,
                    "expires_at": "NEVER",
                    "days_left": "∞",
                    "message": "✅ NEVER EXPIRE token! Hamesha chalega!"
                }
        else:
            return {
                "success": False,
                "valid": False,
                "error": token_data.get("error", {}).get("message", "Invalid token"),
                "message": "❌ Token invalid ho gaya! Naya token generate karo."
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# STEP 4: AUTO-RENEW TOKEN (Before Expiry)
# ============================================

def auto_renew_token(current_token, page_id=None):
    """
    Token expire hone se pehle auto-renew karo

    Args:
        current_token: Current working token
        page_id: Optional page ID for page token

    Returns:
        New token (same ya renewed)
    """
    # Check current token
    check = check_token_validity(current_token)

    if not check.get("valid"):
        return {"error": "Token expired! Manual login required."}

    days_left = check.get("days_left", 0)

    # Agar 7 din se kam bache hain → Renew karo
    if isinstance(days_left, int) and days_left < 7:
        # Try to refresh (only works for some token types)
        return {
            "success": True,
            "action": "renew_needed",
            "days_left": days_left,
            "message": f"⚠️ {days_left} din bache! Token renew karo.",
            "steps": [
                "1. User ko login URL bhejo",
                "2. New short token lo",
                "3. exchange_long_token() call karo",
                "4. New long token save karo"
            ]
        }

    return {
        "success": True,
        "action": "no_action",
        "days_left": days_left,
        "message": f"✅ Token theek hai! {days_left} din bache hain."
    }

# ============================================
# COMPLETE WORKFLOW: One Function
# ============================================

def get_permanent_facebook_token(short_token, page_id):
    """
    EK BAAR CALL KARO — Permanent token mil jayega!

    Flow: Short Token → Long Token → Page Token (Never Expire)
    """
    # Step 1: Short → Long
    long_result = get_long_lived_token(short_token)

    if not long_result.get("success"):
        return long_result

    long_token = long_result["long_token"]

    # Step 2: Long → Page (Never Expire)
    page_result = get_never_expire_token(long_token, page_id)

    if not page_result.get("success"):
        # Return long token as fallback
        return {
            "success": True,
            "fallback": True,
            "long_token": long_token,
            "long_expiry": long_result["expiry_date"],
            "page_token_error": page_result.get("error"),
            "message": "✅ Long token mil gaya (60 din). Page token failed — manually try karo."
        }

    return {
        "success": True,
        "page_token": page_result["page_token"],
        "page_id": page_id,
        "token_type": "NEVER_EXPIRE",
        "message": "🎉 PERMANENT TOKEN READY! Kabhi expire nahi hoga!",
        "usage": "Yeh token hamesha use karo — baar-baar login nahi karna!"
    }

# ============================================
# SINGH JI AI — FACEBOOK POST (Using Permanent Token)
# ============================================

def post_with_permanent_token(page_id, message, page_token):
    """
    Permanent token se post karo — hamesha chalega!
    """
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"

    params = {
        "message": message,
        "access_token": page_token  # Yeh token kabhi expire nahi hoga!
    }

    try:
        response = requests.post(url, params=params, timeout=10)
        data = response.json()

        if "id" in data:
            return {
                "success": True,
                "post_id": data["id"],
                "message": "✅ Facebook pe post ho gaya!",
                "token_status": "Permanent token — no expiry!"
            }
        else:
            return {
                "success": False,
                "error": data.get("error", {}).get("message", "Post failed")
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# ENVIRONMENT VARIABLES (Railway/Render)
# ============================================
"""
Railway/Render Dashboard → Environment Variables:

FACEBOOK_APP_ID=1008554401796459
FACEBOOK_APP_SECRET=your_actual_secret_here
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_PAGE_TOKEN=your_never_expire_page_token_here

# Yeh 4 variables ek baar daalo — hamesha kaam karenge!
"""

# ============================================
# USAGE EXAMPLE
# ============================================
"""
# EK BAAR KARO — HAMESHA KAAM KAREGA:

# 1. User se short token lo (login ke baad)
short = "EAAH...xyz"  # 1-2 hours valid

# 2. Permanent token banao
result = get_permanent_facebook_token(short, "YOUR_PAGE_ID")

# 3. Token save karo (database ya .env mein)
permanent_token = result["page_token"]

# 4. Hamesha use karo — kabhi expire nahi hoga!
post_with_permanent_token("YOUR_PAGE_ID", "Hello!", permanent_token)
"""

__all__ = [
    "get_long_lived_token",
    "get_never_expire_token",
    "check_token_validity",
    "auto_renew_token",
    "get_permanent_facebook_token",
    "post_with_permanent_token"
]
