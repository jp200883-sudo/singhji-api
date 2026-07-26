"""
Singh Ji AI — Scheme Swarm FastAPI Routes
Mount these in your main FastAPI app
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional
import logging
import json

from .eligibility import EligibilityEngine, UserProfile
from .db_helpers import (
    get_scheme_profile, save_scheme_profile, 
    get_user_applications, save_application,
    get_module_stats, update_application_status
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/modules/scheme_swarm", tags=["scheme_swarm"])

# Initialize eligibility engine
engine = EligibilityEngine()


# ═══════════════════════════════════════════════════════
# PROFILE ROUTES
# ═══════════════════════════════════════════════════════

@router.post("/save-profile")
async def save_profile(request: Request):
    """Save or update user profile for scheme matching"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        profile = data.get("profile", {})

        if not user_id or not profile:
            raise HTTPException(status_code=400, detail="user_id and profile required")

        success = await save_scheme_profile(user_id, profile)

        if success:
            return {
                "status": "success",
                "message": "Profile saved successfully",
                "user_id": user_id,
                "profile_summary": {
                    "age": profile.get("age"),
                    "income": profile.get("income"),
                    "state": profile.get("state"),
                    "occupation": profile.get("occupation"),
                    "caste": profile.get("caste")
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save profile route error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_profile(user_id: int):
    """Get user's scheme profile"""
    try:
        profile = await get_scheme_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "status": "success",
            "profile": profile
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# MATCHING ROUTES
# ═══════════════════════════════════════════════════════

@router.post("/match")
async def match_schemes(request: Request):
    """Find matching schemes for a user based on their profile"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        min_score = data.get("min_score", 40)
        limit = data.get("limit", 10)

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")

        # Get profile from DB
        profile_data = await get_scheme_profile(user_id)

        if not profile_data:
            return {
                "matches": [],
                "error": "Profile not found",
                "message": "Please create profile first using /scheme_profile"
            }

        # Build UserProfile object
        user_prof = UserProfile(
            age=profile_data.get("age", 25),
            gender=profile_data.get("gender", "male"),
            caste_category=profile_data.get("caste_category", "GENERAL"),
            annual_income=profile_data.get("annual_income", 0),
            state=profile_data.get("state", "Delhi"),
            occupation=profile_data.get("occupation", "unemployed"),
            education_level=profile_data.get("education_level"),
            bpl_status=profile_data.get("bpl_status", False),
            is_farmer=profile_data.get("is_farmer", False),
            land_area_acres=profile_data.get("land_area_acres", 0),
            is_student=profile_data.get("is_student", False),
            is_widow=profile_data.get("is_widow", False),
            is_disabled=profile_data.get("is_disabled", False),
            disability_percentage=profile_data.get("disability_percentage", 0),
            is_senior_citizen=profile_data.get("is_senior_citizen", False),
            family_members=profile_data.get("family_members", 1),
            children_count=profile_data.get("children_count", 0)
        )

        # Find matches
        matches = engine.find_all_matches(user_prof, min_score=min_score)

        # Format response
        formatted_matches = []
        for m in matches[:limit]:
            formatted_matches.append({
                "id": m.scheme_id,
                "name": m.scheme_name,
                "score": m.match_score,
                "benefits": m.benefits_summary,
                "documents": m.documents_needed,
                "deadline": str(m.deadline) if m.deadline else None,
                "url": m.application_url
            })

        return {
            "status": "success",
            "user_id": user_id,
            "total_matches": len(matches),
            "matches": formatted_matches,
            "profile_summary": {
                "age": user_prof.age,
                "income": user_prof.annual_income,
                "state": user_prof.state,
                "occupation": user_prof.occupation,
                "caste": user_prof.caste_category
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Match error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-check")
async def quick_check(request: Request):
    """Quick eligibility check without saving profile"""
    try:
        data = await request.json()

        user_prof = UserProfile(
            age=data.get("age", 25),
            gender=data.get("gender", "male"),
            caste_category=data.get("caste", "GENERAL").upper(),
            annual_income=data.get("income", 0),
            state=data.get("state", "Delhi"),
            occupation=data.get("occupation", "unemployed"),
            bpl_status=data.get("bpl_status", False),
            is_farmer=data.get("is_farmer", False),
            is_student=data.get("is_student", False),
            is_senior_citizen=data.get("age", 0) >= 60
        )

        matches = engine.find_all_matches(user_prof, min_score=30)

        return {
            "status": "success",
            "total_matches": len(matches),
            "matches": [
                {
                    "id": m.scheme_id,
                    "name": m.scheme_name,
                    "score": m.match_score,
                    "benefits": m.benefits_summary
                }
                for m in matches[:10]
            ]
        }

    except Exception as e:
        logger.error(f"Quick check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# SCHEME DETAIL ROUTES
# ═══════════════════════════════════════════════════════

@router.get("/scheme/{scheme_id}")
async def get_scheme_detail(scheme_id: str):
    """Get detailed information about a specific scheme"""
    try:
        scheme = next(
            (s for s in engine.schemes if s["scheme_code"] == scheme_id),
            None
        )

        if not scheme:
            raise HTTPException(status_code=404, detail=f"Scheme {scheme_id} not found")

        return {
            "status": "success",
            "scheme_code": scheme["scheme_code"],
            "name": scheme["name"],
            "name_hi": scheme.get("name_hi", ""),
            "description": scheme["description"],
            "description_hi": scheme.get("description_hi", ""),
            "level": scheme["level"],
            "ministry": scheme.get("ministry", ""),
            "category": scheme.get("category", ""),
            "subcategory": scheme.get("subcategory", ""),
            "benefits_summary": scheme.get("benefits", {}).get("benefit_summary", ""),
            "eligibility_rules": scheme.get("eligibility_rules", {}),
            "documents": scheme.get("documents_required", []),
            "url": scheme.get("application_url", ""),
            "offline_process": scheme.get("offline_process", ""),
            "deadline": str(scheme["deadline"]) if scheme.get("deadline") else None,
            "is_active": scheme.get("is_active", True),
            "launched_year": scheme.get("launched_year", 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get scheme error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemes")
async def list_all_schemes(
    category: Optional[str] = None,
    ministry: Optional[str] = None,
    active_only: bool = True
):
    """List all schemes with optional filtering"""
    try:
        schemes = engine.schemes

        if active_only:
            schemes = [s for s in schemes if s.get("is_active", True)]

        if category:
            schemes = [s for s in schemes if s.get("category", "").lower() == category.lower()]

        if ministry:
            schemes = [s for s in schemes if ministry.lower() in s.get("ministry", "").lower()]

        return {
            "status": "success",
            "total": len(schemes),
            "schemes": [
                {
                    "id": s["scheme_code"],
                    "name": s["name"],
                    "category": s.get("category", ""),
                    "ministry": s.get("ministry", ""),
                    "benefits": s.get("benefits", {}).get("benefit_summary", "")
                }
                for s in schemes
            ]
        }

    except Exception as e:
        logger.error(f"List schemes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# APPLICATION TRACKING ROUTES
# ═══════════════════════════════════════════════════════

@router.post("/apply")
async def track_application(request: Request):
    """Track a new scheme application"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        scheme_id = data.get("scheme_id")
        application_data = data.get("application_data", {})

        if not user_id or not scheme_id:
            raise HTTPException(status_code=400, detail="user_id and scheme_id required")

        success = await save_application(user_id, scheme_id, application_data)

        return {
            "status": "success" if success else "failed",
            "message": "Application tracked successfully" if success else "Failed to track"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apply error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/{user_id}")
async def get_applications(user_id: int):
    """Get all tracked applications for a user"""
    try:
        applications = await get_user_applications(user_id)

        return {
            "status": "success",
            "user_id": user_id,
            "total_applications": len(applications),
            "applications": applications
        }

    except Exception as e:
        logger.error(f"Get applications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-status")
async def update_status(request: Request):
    """Update application status"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        scheme_id = data.get("scheme_id")
        status = data.get("status")
        notes = data.get("notes", "")

        if not all([user_id, scheme_id, status]):
            raise HTTPException(status_code=400, detail="user_id, scheme_id, and status required")

        success = await update_application_status(user_id, scheme_id, status, notes)

        return {
            "status": "success" if success else "failed",
            "message": f"Status updated to {status}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# STATS & HEALTH
# ═══════════════════════════════════════════════════════

@router.get("/stats")
async def module_stats():
    """Get Scheme Swarm module statistics"""
    try:
        stats = await get_module_stats()

        return {
            "status": "success",
            "module": "scheme_swarm",
            "version": "1.0.0",
            "total_schemes": len(engine.schemes),
            **stats
        }

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for Scheme Swarm module"""
    return {
        "status": "healthy",
        "module": "scheme_swarm",
        "version": "1.0.0",
        "total_schemes_loaded": len(engine.schemes),
        "eligibility_engine": "active"
    }
