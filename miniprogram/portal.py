"""
Singh Ji AI Ultra v8.0 — Mini-Program Portal API
Developer: Singh Ji
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Form, Depends, Request
from typing import Optional, Dict, Any
import json
import uuid
from datetime import datetime

from .auth import AuthManager, DeveloperAuth, get_current_developer
from .config import MiniProgramConfig
from .models import Developer, MiniApp, Payment, AppReview, SandboxLog
from .storage import storage
from .payment import payment
from .utils import generate_app_id, validate_app_code

router = APIRouter(prefix="/mini", tags=["Mini-Program"])


# ========== AUTH ROUTES ==========

@router.post("/auth/register", response_model=None)
async def register_developer(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    company_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None)
):
    """👤 Developer register karo"""
    if not MiniProgramConfig.DEVELOPER_REGISTRATION_OPEN:
        raise HTTPException(status_code=403, detail="Registration temporarily closed!")
    
    return await DeveloperAuth.register(
        email=email, 
        password=password, 
        name=full_name
    )


@router.post("/auth/login", response_model=None)
async def login_developer(
    email: str = Form(...),
    password: str = Form(...)
):
    """🔑 Developer login karo"""
    try:
        return await DeveloperAuth.login(email=email, password=password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/refresh", response_model=None)
async def refresh_token(token: str = Form(...)):
    """🔄 Token refresh karo"""
    return await DeveloperAuth.refresh_token(token=token)


# ========== APP MANAGEMENT ==========

@router.post("/apps/create", response_model=None)
async def create_app(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    token: str = Form(...)
):
    """📱 Naya Mini-App create karo"""
    developer = await get_current_developer(token)
    app_id = generate_app_id()
    
    app_data = {
        "id": app_id,
        "name": name,
        "description": description,
        "category": category,
        "developer_id": developer.get("id"),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    # Storage mein save karo
    await storage.save_app(app_id, app_data)
    
    return {
        "status": "success",
        "app_id": app_id,
        "message": "App created! Review ke liye bheja gaya."
    }


@router.get("/apps/list", response_model=None)
async def list_apps(token: str):
    """📋 Developer ke saare apps dikhao"""
    developer = await get_current_developer(token)
    apps = await storage.get_developer_apps(developer.get("id"))
    return {"apps": apps}


@router.get("/apps/{app_id}", response_model=None)
async def get_app(app_id: str, token: str):
    """🔍 Specific app details"""
    developer = await get_current_developer(token)
    app = await storage.get_app(app_id)
    
    if not app or app.get("developer_id") != developer.get("id"):
        raise HTTPException(status_code=404, detail="App not found!")
    
    return {"app": app}


# ========== SANDBOX ==========

@router.post("/sandbox/run", response_model=None)
async def run_sandbox(
    app_id: str = Form(...),
    code: str = Form(...),
    token: str = Form(...)
):
    """🏖️ Code sandbox mein run karo"""
    developer = await get_current_developer(token)
    
    # Security check
    if not validate_app_code(code):
        raise HTTPException(status_code=400, detail="Code mein restricted functions hain!")
    
    # Sandbox execution
    result = await SandboxLog.run_code(app_id, code)
    
    return {
        "status": "success",
        "output": result.get("output"),
        "execution_time": result.get("time"),
        "memory_used": result.get("memory")
    }


# ========== PAYMENT ==========

@router.post("/payment/create", response_model=None)
async def create_payment(
    amount: float = Form(...),
    currency: str = Form("INR"),
    app_id: Optional[str] = Form(None),
    token: str = Form(...)
):
    """💰 Payment order create karo"""
    developer = await get_current_developer(token)
    
    order = await payment.create_order(
        amount=amount,
        currency=currency,
        developer_id=developer.get("id"),
        app_id=app_id
    )
    
    return {
        "status": "success",
        "order_id": order.get("id"),
        "amount": amount,
        "currency": currency
    }


@router.get("/payment/status/{order_id}", response_model=None)
async def payment_status(order_id: str, token: str):
    """💳 Payment status check karo"""
    await get_current_developer(token)
    status = await payment.get_status(order_id)
    return {"order_id": order_id, "status": status}


# ========== REVIEWS ==========

@router.post("/reviews/submit", response_model=None)
async def submit_review(
    app_id: str = Form(...),
    rating: int = Form(...),
    comment: Optional[str] = Form(None),
    token: str = Form(...)
):
    """⭐ App review karo"""
    await get_current_developer(token)
    
    review = {
        "id": str(uuid.uuid4()),
        "app_id": app_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await storage.save_review(review)
    return {"status": "success", "review_id": review["id"]}


# ========== ANALYTICS ==========

@router.get("/analytics/{app_id}", response_model=None)
async def app_analytics(app_id: str, token: str):
    """📊 App analytics dikhao"""
    developer = await get_current_developer(token)
    app = await storage.get_app(app_id)
    
    if not app or app.get("developer_id") != developer.get("id"):
        raise HTTPException(status_code=404, detail="App not found!")
    
    analytics = await storage.get_analytics(app_id)
    return {"app_id": app_id, "analytics": analytics}


# ========== ADMIN ROUTES ==========

@router.get("/admin/pending-apps", response_model=None)
async def pending_apps(admin_token: str):
    """🔒 Admin — pending apps dikhao"""
    if not MiniProgramConfig.is_admin_ready():
        raise HTTPException(status_code=503, detail="Admin panel disabled — ADMIN_SECRET set nahi hai!")
    if admin_token != MiniProgramConfig.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied!")
    
    apps = await storage.get_pending_apps()
    return {"pending_apps": apps}


@router.post("/admin/approve/{app_id}", response_model=None)
async def approve_app(app_id: str, admin_token: str):
    """✅ Admin — app approve karo"""
    if not MiniProgramConfig.is_admin_ready():
        raise HTTPException(status_code=503, detail="Admin panel disabled — ADMIN_SECRET set nahi hai!")
    if admin_token != MiniProgramConfig.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied!")
    
    await storage.update_app_status(app_id, "approved")
    return {"status": "success", "app_id": app_id, "message": "App approved!"}


@router.post("/admin/reject/{app_id}", response_model=None)
async def reject_app(app_id: str, admin_token: str, reason: Optional[str] = Form(None)):
    """❌ Admin — app reject karo"""
    if not MiniProgramConfig.is_admin_ready():
        raise HTTPException(status_code=503, detail="Admin panel disabled — ADMIN_SECRET set nahi hai!")
    if admin_token != MiniProgramConfig.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access denied!")
    
    await storage.update_app_status(app_id, "rejected", reason)
    return {"status": "success", "app_id": app_id, "reason": reason}
