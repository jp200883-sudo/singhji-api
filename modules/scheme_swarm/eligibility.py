"""
Singh Ji AI — Scheme Swarm Eligibility Engine
Matches user profile against all schemes using rule-based + AI scoring
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class UserProfile:
    age: int
    gender: str
    caste_category: str
    annual_income: float
    state: str
    occupation: str
    education_level: Optional[str] = None
    bpl_status: bool = False
    is_farmer: bool = False
    land_area_acres: float = 0.0
    is_student: bool = False
    is_widow: bool = False
    is_disabled: bool = False
    disability_percentage: int = 0
    is_senior_citizen: bool = False
    family_members: int = 1
    children_count: int = 0

@dataclass
class SchemeMatch:
    scheme_id: str
    scheme_name: str
    match_score: int  # 0-100
    match_reasons: List[str]
    benefits_summary: str
    application_url: Optional[str]
    documents_needed: List[str]
    deadline: Optional[date]


class EligibilityEngine:
    """Rule-based eligibility checker with AI-enhanced scoring"""
    
    def __init__(self, schemes_data_path: str = "modules/scheme_swarm/data/"):
        self.schemes = self._load_schemes(schemes_data_path)
        
    def _load_schemes(self, path: str) -> List[Dict]:
        """Load all central + state schemes from JSON"""
        schemes = []
        # Central schemes
        with open(f"{path}central_schemes.json", "r", encoding="utf-8") as f:
            schemes.extend(json.load(f))
        # State schemes (dynamic loading)
        import os
        state_dir = f"{path}state_schemes/"
        if os.path.exists(state_dir):
            for state_file in os.listdir(state_dir):
                if state_file.endswith(".json"):
                    with open(f"{state_dir}{state_file}", "r", encoding="utf-8") as f:
                        schemes.extend(json.load(f))
        return schemes
    
    def check_eligibility(self, profile: UserProfile, scheme: Dict) -> SchemeMatch:
        """
        Check if user is eligible for a scheme
        Returns match with score and reasons
        """
        rules = scheme.get("eligibility_rules", {})
        score = 0
        reasons = []
        max_score = 0
        
        # Age check
        if "age" in rules:
            max_score += 20
            age_rule = rules["age"]
            if age_rule.get("min", 0) <= profile.age <= age_rule.get("max", 150):
                score += 20
                reasons.append(f"✅ Age {profile.age} qualifies ({age_rule.get('min', 0)}-{age_rule.get('max', 150)})")
            else:
                reasons.append(f"❌ Age {profile.age} doesn't qualify ({age_rule.get('min', 0)}-{age_rule.get('max', 150)})")
        
        # Income check
        if "income" in rules:
            max_score += 25
            income_rule = rules["income"]
            if profile.annual_income <= income_rule.get("max", float('inf')):
                score += 25
                reasons.append(f"✅ Income ₹{profile.annual_income:,} within limit ₹{income_rule.get('max', 'No limit'):,}")
            else:
                reasons.append(f"❌ Income ₹{profile.annual_income:,} exceeds limit ₹{income_rule.get('max', 'No limit'):,}")
        
        # Caste check
        if "caste" in rules:
            max_score += 15
            allowed_castes = rules["caste"]
            if profile.caste_category.upper() in [c.upper() for c in allowed_castes]:
                score += 15
                reasons.append(f"✅ Caste {profile.caste_category} eligible")
            else:
                reasons.append(f"❌ Caste {profile.caste_category} not in {allowed_castes}")
        
        # Gender check
        if "gender" in rules:
            max_score += 10
            allowed_genders = rules["gender"]
            if profile.gender.lower() in [g.lower() for g in allowed_genders]:
                score += 10
                reasons.append(f"✅ Gender eligible")
            else:
                reasons.append(f"❌ Gender not eligible")
        
        # Occupation check
        if "occupation" in rules:
            max_score += 15
            allowed_occ = rules["occupation"]
            if profile.occupation.lower() in [o.lower() for o in allowed_occ]:
                score += 15
                reasons.append(f"✅ Occupation '{profile.occupation}' eligible")
            else:
                reasons.append(f"❌ Occupation '{profile.occupation}' not eligible")
        
        # Farmer check
        if "is_farmer" in rules and rules["is_farmer"]:
            max_score += 10
            if profile.is_farmer:
                score += 10
                reasons.append(f"✅ Farmer status confirmed")
            else:
                reasons.append(f"❌ Not a farmer")
        
        # Student check
        if "is_student" in rules and rules["is_student"]:
            max_score += 10
            if profile.is_student:
                score += 10
                reasons.append(f"✅ Student status confirmed")
            else:
                reasons.append(f"❌ Not a student")
        
        # BPL check
        if "bpl_status" in rules and rules["bpl_status"]:
            max_score += 10
            if profile.bpl_status:
                score += 10
                reasons.append(f"✅ BPL status confirmed")
            else:
                reasons.append(f"❌ Not BPL")
        
        # Land area check
        if "land_area" in rules and profile.is_farmer:
            max_score += 10
            land_rule = rules["land_area"]
            if land_rule.get("min", 0) <= profile.land_area_acres <= land_rule.get("max", float('inf')):
                score += 10
                reasons.append(f"✅ Land {profile.land_area_acres} acres qualifies")
            else:
                reasons.append(f"❌ Land {profile.land_area_acres} acres doesn't qualify")
        
        # State check
        if "states" in rules:
            max_score += 5
            allowed_states = rules["states"]
            if profile.state.lower() in [s.lower() for s in allowed_states]:
                score += 5
                reasons.append(f"✅ State {profile.state} eligible")
            else:
                reasons.append(f"❌ State {profile.state} not eligible")
        
        # Normalize score to 0-100
        normalized_score = int((score / max(max_score, 1)) * 100) if max_score > 0 else 0
        
        benefits = scheme.get("benefits", {})
        benefits_summary = self._format_benefits(benefits)
        
        return SchemeMatch(
            scheme_id=scheme["scheme_code"],
            scheme_name=scheme["name"],
            match_score=normalized_score,
            match_reasons=reasons,
            benefits_summary=benefits_summary,
            application_url=scheme.get("application_url"),
            documents_needed=scheme.get("documents_required", []),
            deadline=scheme.get("deadline")
        )
    
    def _format_benefits(self, benefits: Dict) -> str:
        """Format benefits into readable string"""
        parts = []
        if "amount" in benefits:
            parts.append(f"₹{benefits['amount']:,}")
        if "frequency" in benefits:
            parts.append(f"{benefits['frequency']}")
        if "type" in benefits:
            parts.append(f"({benefits['type']})")
        return " ".join(parts) if parts else "Benefits vary"
    
    def find_all_matches(self, profile: UserProfile, min_score: int = 50) -> List[SchemeMatch]:
        """Find all matching schemes for a user profile"""
        matches = []
        for scheme in self.schemes:
            match = self.check_eligibility(profile, scheme)
            if match.match_score >= min_score:
                matches.append(match)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches
    
    def get_top_matches(self, profile: UserProfile, top_n: int = 5) -> List[SchemeMatch]:
        """Get top N matching schemes"""
        matches = self.find_all_matches(profile, min_score=30)
        return matches[:top_n]


# ============ SAMPLE SCHEMES DATA (central_schemes.json snippet) ============

SAMPLE_CENTRAL_SCHEMES = [
    {
        "scheme_code": "PM-KISAN",
        "name": "PM-KISAN Samman Nidhi",
        "name_hi": "पीएम-किसान सम्मान निधि",
        "description": "Direct income support of ₹6000/year to farmer families",
        "level": "central",
        "ministry": "Agriculture",
        "category": "agriculture",
        "eligibility_rules": {
            "is_farmer": True,
            "age": {"min": 18, "max": 100},
            "income": {"max": 500000}
        },
        "benefits": {
            "amount": 6000,
            "frequency": "yearly",
            "type": "cash_transfer"
        },
        "application_url": "https://pmkisan.gov.in",
        "documents_required": ["Aadhaar", "Bank Passbook", "Land Records", "Income Certificate"],
        "deadline": None
    },
    {
        "scheme_code": "PM-SVANIDHI",
        "name": "PM Street Vendor's Atmanirbhar Nidhi",
        "name_hi": "पीएम स्वनिधि योजना",
        "description": "Working capital loan up to ₹10,000 for street vendors",
        "level": "central",
        "ministry": "Housing & Urban Affairs",
        "category": "employment",
        "eligibility_rules": {
            "occupation": ["street_vendor", "hawker"],
            "age": {"min": 18, "max": 65}
        },
        "benefits": {
            "amount": 10000,
            "frequency": "one_time",
            "type": "loan"
        },
        "application_url": "https://pmsvanidhi.mohua.gov.in",
        "documents_required": ["Aadhaar", "Vendor Certificate", "Bank Account"],
        "deadline": None
    },
    {
        "scheme_code": "PM-JAY",
        "name": "Ayushman Bharat PM-JAY",
        "name_hi": "आयुष्मान भारत प्रधानमंत्री जन आरोग्य योजना",
        "description": "Health insurance up to ₹5 lakh per family per year",
        "level": "central",
        "ministry": "Health",
        "category": "health",
        "eligibility_rules": {
            "bpl_status": True,
            "income": {"max": 500000}
        },
        "benefits": {
            "amount": 500000,
            "frequency": "yearly",
            "type": "health_insurance"
        },
        "application_url": "https://pmjay.gov.in",
        "documents_required": ["Aadhaar", "Ration Card", "Income Certificate", "Mobile Number"],
        "deadline": None
    },
    {
        "scheme_code": "PM-AWAS",
        "name": "Pradhan Mantri Awas Yojana",
        "name_hi": "प्रधानमंत्री आवास योजना",
        "description": "Housing for all — subsidy on home loans",
        "level": "central",
        "ministry": "Housing & Urban Affairs",
        "category": "housing",
        "eligibility_rules": {
            "income": {"max": 1800000},
            "age": {"min": 18, "max": 70}
        },
        "benefits": {
            "amount": 267000,
            "frequency": "one_time",
            "type": "subsidy"
        },
        "application_url": "https://pmaymis.gov.in",
        "documents_required": ["Aadhaar", "Income Proof", "Bank Statement", "Property Documents"],
        "deadline": None
    },
    {
        "scheme_code": "NPS-LITE",
        "name": "National Pension Scheme - Swavalamban",
        "name_hi": "राष्ट्रीय पेंशन योजना - स्वावलंबन",
        "description": "Pension scheme for unorganized sector workers",
        "level": "central",
        "ministry": "Finance",
        "category": "social_security",
        "eligibility_rules": {
            "age": {"min": 18, "max": 40},
            "income": {"max": 300000}
        },
        "benefits": {
            "amount": 3000,
            "frequency": "monthly_pension",
            "type": "pension"
        },
        "application_url": "https://npscra.nsdl.co.in",
        "documents_required": ["Aadhaar", "PAN", "Bank Account", "Photograph"],
        "deadline": None
    },
    {
        "scheme_code": "SCHOLARSHIP-POSTMATRIC",
        "name": "Post Matric Scholarship for SC/ST",
        "name_hi": "पोस्ट मैट्रिक छात्रवृत्ति योजना",
        "description": "Scholarship for SC/ST students pursuing higher education",
        "level": "central",
        "ministry": "Social Justice",
        "category": "education",
        "eligibility_rules": {
            "is_student": True,
            "caste": ["SC", "ST"],
            "income": {"max": 250000}
        },
        "benefits": {
            "amount": 50000,
            "frequency": "yearly",
            "type": "scholarship"
        },
        "application_url": "https://scholarships.gov.in",
        "documents_required": ["Aadhaar", "Caste Certificate", "Income Certificate", "Marksheet", "Bank Account", "Institute Certificate"],
        "deadline": "2026-10-31"
    },
    {
        "scheme_code": "PM-MUDRA",
        "name": "Pradhan Mantri MUDRA Yojana",
        "name_hi": "प्रधानमंत्री मुद्रा योजना",
        "description": "Loans up to ₹10 lakh for non-corporate small business",
        "level": "central",
        "ministry": "Finance",
        "category": "employment",
        "eligibility_rules": {
            "occupation": ["self_employed", "small_business", "entrepreneur"],
            "age": {"min": 18, "max": 65}
        },
        "benefits": {
            "amount": 1000000,
            "frequency": "one_time",
            "type": "loan"
        },
        "application_url": "https://mudra.org.in",
        "documents_required": ["Aadhaar", "PAN", "Business Proof", "Bank Statement", "Project Report"],
        "deadline": None
    },
    {
        "scheme_code": "PM-UJJWALA",
        "name": "PM Ujjwala Yojana",
        "name_hi": "प्रधानमंत्री उज्ज्वला योजना",
        "description": "Free LPG connection to BPL households",
        "level": "central",
        "ministry": "Petroleum",
        "category": "welfare",
        "eligibility_rules": {
            "bpl_status": True,
            "income": {"max": 200000}
        },
        "benefits": {
            "amount": 1600,
            "frequency": "one_time",
            "type": "subsidy"
        },
        "application_url": "https://pmuy.gov.in",
        "documents_required": ["Aadhaar", "BPL Card", "Ration Card", "Bank Account"],
        "deadline": None
    }
]
