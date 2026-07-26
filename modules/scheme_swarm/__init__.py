
"""
Scheme Swarm Module — Singh Ji AI v8.0
"""

from .eligibility import EligibilityEngine, UserProfile
from .form_filler import FormFiller
from .status_tracker import StatusTracker
from .notifications import SchemeNotifier

__all__ = [
    "EligibilityEngine",
    "UserProfile", 
    "FormFiller",
    "StatusTracker",
    "SchemeNotifier"
]

MODULE_INFO = {
    "name": "Scheme Swarm",
    "version": "1.0.0",
    "description": "Bharat Sarkar Schemes AI — Auto-matching, form filling, and tracking",
    "commands": [
        "/schemes — Find eligible schemes",
        "/scheme_profile — Update your profile", 
        "/scheme_status — Check application status",
        "/scheme_docs — Document checklist",
        "/scheme_remind — Set deadline reminders"
    ],
    "status": "active"
}
