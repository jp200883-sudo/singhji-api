"""
🛠️ Utility Functions
"""
import re
import uuid
from typing import Dict, Any


def generate_slug(name: str) -> str:
    """Name se URL-friendly slug banao"""
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:50]


def validate_email(email: str) -> bool:
    """Email validate karo"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Dict[str, Any]:
    """Password strength check karo"""
    issues = []
    
    if len(password) < 8:
        issues.append("Minimum 8 characters chahiye")
    if not re.search(r'[A-Z]', password):
        issues.append("Ek capital letter chahiye")
    if not re.search(r'[a-z]', password):
        issues.append("Ek small letter chahiye")
    if not re.search(r'\d', password):
        issues.append("Ek number chahiye")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Ek special character chahiye")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "strength": "strong" if len(issues) == 0 else "weak"
    }


def sanitize_filename(filename: str) -> str:
    """Filename clean karo"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', filename)


def format_bytes(size: int) -> str:
    """Bytes ko human-readable format mein karo"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
