"""
🏗️ Developer Portal API — FastAPI endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from .auth import AuthManager, DeveloperAuth, get_current_developer
from .models import Developer, MiniApp, Payment, AppReview
from .config import MiniProgramConfig
from .storage import storage
from .payment import payment
from .sandbox import sandbox

router = APIRouter(prefix=MiniProgramConfig.PORTAL_API_PREFIX)


# ============== 🔐 AUTH ENDPOINTS ==============

@router.post("/auth/register")
async def register_developer(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    company_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    db: Session = None  # Inject karna hoga main app se
):
    """👤 Developer register karo"""
    if not MiniProgramConfig.DEVELOPER_REGISTRATION_OPEN:
        raise HTTPException(status_code=403, detail="Registration temporarily closed!")
    
    return await DeveloperAuth.register(
        db, email, password, full_name, company_name, phone
    )


@router.post("/auth/login")
async def login_developer(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = None
):
    """🔑 Developer login karo"""
    return await DeveloperAuth.login(db, email, password)


@router.post("/auth/refresh")
async def refresh_token(token: str = Form(...)):
    """🔄 Token refresh karo"""
    return await DeveloperAuth.refresh_token(token)


@router.get("/auth/me")
async def get_profile(current: dict = Depends(get_current_developer), db: Session = None):
    """👤 Apna profile dekho"""
    developer = db.query(Developer).filter(Developer.id == current["developer_id"]).first()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer nahi mila!")
    return developer.to_dict()


# ============== 📱 APP MANAGEMENT ==============

@router.post("/apps/create")
async def create_app(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    source_code: Optional[str] = Form(None),
    manifest: Optional[str] = Form(None),
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """📱 Naya Mini-App banayo"""
    developer = db.query(Developer).filter(Developer.id == current["developer_id"]).first()
    
    # Check karo max apps limit
    if len(developer.apps) >= MiniProgramConfig.MAX_APPS_PER_DEVELOPER:
        raise HTTPException(status_code=400, detail=f"Max {MiniProgramConfig.MAX_APPS_PER_DEVELOPER} apps allowed!")
    
    import json
    app = MiniApp(
        developer_id=current["developer_id"],
        name=name,
        description=description,
        category=category,
        source_code=source_code,
        manifest=json.loads(manifest) if manifest else None
    )
    
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {
        "success": True,
        "message": "App created! 🎉",
        "app": app.to_dict()
    }


@router.get("/apps/list")
async def list_my_apps(
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """📋 Apni apps ki list"""
    apps = db.query(MiniApp).filter(
        MiniApp.developer_id == current["developer_id"]
    ).all()
    
    return {
        "apps": [app.to_dict() for app in apps],
        "total": len(apps)
    }


@router.get("/apps/{app_id}")
async def get_app(
    app_id: str,
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """📱 Ek app ki details"""
    app = db.query(MiniApp).filter(
        MiniApp.id == app_id,
        MiniApp.developer_id == current["developer_id"]
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="App nahi mila!")
    
    return app.to_dict(include_code=True)


@router.put("/apps/{app_id}")
async def update_app(
    app_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    source_code: Optional[str] = Form(None),
    manifest: Optional[str] = Form(None),
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """✏️ App update karo"""
    app = db.query(MiniApp).filter(
        MiniApp.id == app_id,
        MiniApp.developer_id == current["developer_id"]
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="App nahi mila!")
    
    if name:
        app.name = name
    if description:
        app.description = description
    if source_code:
        app.source_code = source_code
    if manifest:
        import json
        app.manifest = json.loads(manifest)
    
    db.commit()
    db.refresh(app)
    
    return {
        "success": True,
        "message": "App updated! ✅",
        "app": app.to_dict()
    }


@router.post("/apps/{app_id}/upload-icon")
async def upload_app_icon(
    app_id: str,
    file: UploadFile = File(...),
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """🖼️ App icon upload karo"""
    app = db.query(MiniApp).filter(
        MiniApp.id == app_id,
        MiniApp.developer_id == current["developer_id"]
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="App nahi mila!")
    
    contents = await file.read()
    
    # Supabase pe upload karo
    url = storage.upload_app_icon(app_id, contents)
    
    if url:
        app.icon_url = url
        db.commit()
        return {
            "success": True,
            "message": "Icon uploaded! 🎉",
            "url": url
        }
    
    raise HTTPException(status_code=500, detail="Upload failed!")


@router.delete("/apps/{app_id}")
async def delete_app(
    app_id: str,
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """🗑️ App delete karo"""
    app = db.query(MiniApp).filter(
        MiniApp.id == app_id,
        MiniApp.developer_id == current["developer_id"]
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="App nahi mila!")
    
    # Icon delete karo agar hai
    if app.icon_url:
        storage.delete_file(f"app-icons/{app_id}/icon.png")
    
    db.delete(app)
    db.commit()
    
    return {
        "success": True,
        "message": "App deleted! 🗑️"
    }


# ============== 🧪 SANDBOX ==============

@router.post("/sandbox/test")
async def test_code(
    code: str = Form(...),
    input_data: Optional[str] = Form(None),
    current: dict = Depends(get_current_developer)
):
    """🧪 Code test karo sandbox mein"""
    import json
    
    data = json.loads(input_data) if input_data else None
    result = sandbox.execute(code, data)
    
    return {
        "success": result["success"],
        "output": result.get("output"),
        "result": result.get("result"),
        "error": result.get("error"),
        "execution_time": result.get("execution_time"),
        "memory_used": result.get("memory_used")
    }


# ============== 💰 PAYMENT ==============

@router.post("/payments/create-order")
async def create_payment_order(
    amount: float = Form(...),
    payment_type: str = Form(...),
    description: Optional[str] = Form(None),
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """💰 Payment order banayo"""
    order = payment.create_order(
        amount=amount,
        notes={
            "developer_id": current["developer_id"],
            "payment_type": payment_type,
            "description": description
        }
    )
    
    if not order:
        raise HTTPException(status_code=500, detail="Order create failed!")
    
    # Database mein save karo
    pay = Payment(
        developer_id=current["developer_id"],
        razorpay_order_id=order["order_id"],
        amount=amount,
        payment_type=payment_type,
        description=description
    )
    db.add(pay)
    db.commit()
    
    return {
        "success": True,
        "order": order
    }


@router.post("/payments/verify")
async def verify_payment(
    order_id: str = Form(...),
    payment_id: str = Form(...),
    signature: str = Form(...),
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """✅ Payment verify karo"""
    is_valid = payment.verify_payment(order_id, payment_id, signature)
    
    if is_valid:
        # Database update karo
        pay = db.query(Payment).filter(
            Payment.razorpay_order_id == order_id,
            Payment.developer_id == current["developer_id"]
        ).first()
        
        if pay:
            pay.razorpay_payment_id = payment_id
            pay.status = "completed"
            pay.completed_at = datetime.utcnow()
            db.commit()
        
        return {
            "success": True,
            "message": "Payment verified! ✅"
        }
    
    raise HTTPException(status_code=400, detail="Payment verification failed!")


@router.get("/payments/history")
async def payment_history(
    current: dict = Depends(get_current_developer),
    db: Session = None
):
    """📜 Payment history dekho"""
    payments = db.query(Payment).filter(
        Payment.developer_id == current["developer_id"]
    ).order_by(Payment.created_at.desc()).all()
    
    return {
        "payments": [p.to_dict() for p in payments],
        "total": len(payments)
    }


# ============== 📊 PUBLIC ENDPOINTS (No Auth) ==============

@router.get("/public/apps")
async def list_public_apps(
    category: Optional[str] = None,
    db: Session = None
):
    """🌍 Public apps ki list"""
    query = db.query(MiniApp).filter(MiniApp.status == "published")
    
    if category:
        query = query.filter(MiniApp.category == category)
    
    apps = query.order_by(MiniApp.downloads.desc()).all()
    
    return {
        "apps": [app.to_dict() for app in apps],
        "total": len(apps)
    }


@router.get("/public/apps/{app_id}")
async def get_public_app(app_id: str, db: Session = None):
    """🌍 Public app details"""
    app = db.query(MiniApp).filter(
        MiniApp.id == app_id,
        MiniApp.status == "published"
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="App nahi mila!")
    
    # Download count badhao
    app.downloads += 1
    db.commit()
    
    return app.to_dict(include_code=True)
