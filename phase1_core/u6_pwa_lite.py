"""🦁 U6: PWA Lite — Installable App"""
class PWALite:
    async def handle(self, action, request):
        return {"module": "U6", "installable": True, "offline": True}
