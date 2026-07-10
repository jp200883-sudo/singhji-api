cat > miniprogram/developer.py << 'EOF'
"""🦁 Developer Portal & Analytics"""
from datetime import datetime

class DeveloperPortal:
    @classmethod
    def get_dashboard(cls, developer_id):
        from .auth import MiniAuth
        dev = MiniAuth.DEVELOPERS.get(developer_id)
        if not dev:
            return {"error": "Developer not found"}
        apps = []
        for app_id in dev.get("apps", []):
            app = MiniAuth.APPROVED_APPS.get(app_id, {})
            apps.append({"id": app_id, "name": app.get("name"), "status": app.get("status"),
                        "type": app.get("type"), "submitted_at": app.get("submitted_at")})
        return {"developer": {"id": dev["id"], "name": dev["name"], "email": dev["email"]},
                "apps": apps, "total_apps": len(apps),
                "active_apps": sum(1 for a in apps if a["status"] == "approved")}
    
    @classmethod
    def get_all_apps(cls, status=None):
        from .auth import MiniAuth
        return [{"id": aid, "name": a["name"], "developer_id": a["developer_id"],
                "status": a["status"], "type": a["type"]}
                for aid, a in MiniAuth.APPROVED_APPS.items()
                if not status or a["status"] == status]
EOF
