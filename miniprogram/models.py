"""
Database Models — SQLAlchemy models for Mini-Program
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class Developer(Base):
    """👤 Developer Registration Model"""
    __tablename__ = "miniprogram_developers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    company_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    # Razorpay
    razorpay_customer_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relations
    apps = relationship("MiniApp", back_populates="developer", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="developer", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "company_name": self.company_name,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "app_count": len(self.apps) if self.apps else 0
        }


class MiniApp(Base):
    """📱 Mini-App Model"""
    __tablename__ = "miniprogram_apps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    developer_id = Column(String(36), ForeignKey("miniprogram_developers.id"), nullable=False)

    # App Info
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)

    # Code
    source_code = Column(Text, nullable=True)  # Python code
    manifest = Column(JSON, nullable=True)  # app.json config

    # Status
    status = Column(String(20), default="draft")  # draft, pending, approved, rejected, published, suspended
    version = Column(String(20), default="1.0.0")

    # Stats
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relations
    developer = relationship("Developer", back_populates="apps")
    reviews = relationship("AppReview", back_populates="app", cascade="all, delete-orphan")

    def to_dict(self, include_code=False):
        data = {
            "id": self.id,
            "developer_id": self.developer_id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "category": self.category,
            "status": self.status,
            "version": self.version,
            "downloads": self.downloads,
            "rating": self.rating,
            "review_count": self.review_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
        if include_code:
            data["source_code"] = self.source_code
            data["manifest"] = self.manifest
        return data


class Payment(Base):
    """💰 Payment Model"""
    __tablename__ = "miniprogram_payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    developer_id = Column(String(36), ForeignKey("miniprogram_developers.id"), nullable=False)

    # Payment Details
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")

    # Type: subscription, onetime, commission
    payment_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded

    # Metadata - SQLAlchemy mein 'metadata' reserved hai! 🚫
    description = Column(String(255), nullable=True)
    extra_data = Column(JSON, nullable=True)  # ✅ FIX: 'metadata' → 'extra_data'

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relations
    developer = relationship("Developer", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_type": self.payment_type,
            "status": self.status,
            "description": self.description,
            "extra_data": self.extra_data,  # ✅ FIX
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AppReview(Base):
    """⭐ App Review Model"""
    __tablename__ = "miniprogram_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    app_id = Column(String(36), ForeignKey("miniprogram_apps.id"), nullable=False)
    user_id = Column(String(36), nullable=False)

    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    app = relationship("MiniApp", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "app_id": self.app_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SandboxLog(Base):
    """🧪 Sandbox Execution Log"""
    __tablename__ = "miniprogram_sandbox_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    app_id = Column(String(36), nullable=False)

    # Execution
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Performance
    execution_time = Column(Float, nullable=True)  # seconds
    memory_used = Column(Float, nullable=True)  # MB

    # Status
    status = Column(String(20), default="running")  # running, success, error, timeout

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "app_id": self.app_id,
            "status": self.status,
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
