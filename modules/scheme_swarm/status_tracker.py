"""
Track application status across multiple scheme portals
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Optional, List

class StatusTracker:
    """Track scheme application status from various portals"""
    
    PORTAL_APIS = {
        "PM-KISAN": {
            "status_url": "https://pmkisan.gov.in/BeneficiaryStatus.aspx",
            "method": "POST",
            "params": {"BeneficiaryCode": "{application_id}"}
        },
        "PM-AWAS": {
            "status_url": "https://pmaymis.gov.in/open/check_aadhar_status.aspx",
            "method": "GET", 
            "params": {"aadhar": "{aadhaar}"}
        }
    }
    
    async def check_status(self, scheme_code: str, application_id: str, aadhaar: Optional[str] = None) -> Dict:
        """
        Check application status on a scheme portal
        Returns: {status, message, last_updated, next_step}
        """
        portal = self.PORTAL_APIS.get(scheme_code)
        if not portal:
            return {
                "status": "unknown",
                "message": "Auto-tracking not available for this scheme. Check manually.",
                "portal_url": f"https://www.google.com/search?q={scheme_code}+status+check"
            }
        
        url = portal["status_url"]
        method = portal["method"]
        
        # Build params
        params = {}
        for key, value in portal["params"].items():
            params[key] = value.replace("{application_id}", application_id).replace("{aadhaar}", aadhaar or "")
        
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, params=params, timeout=30) as response:
                        html = await response.text()
                else:
                    async with session.post(url, data=params, timeout=30) as response:
                        html = await response.text()
                
                # Parse response (simplified)
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract status (portal-specific parsing needed)
                status_text = soup.find("span", {"id": "lblStatus"})
                status = status_text.text if status_text else "Unable to parse"
                
                return {
                    "status": status.lower(),
                    "message": f"Current status: {status}",
                    "last_updated": "Just now",
                    "next_step": "Check again in 7 days" if "pending" in status.lower() else "Approved! Check your bank account."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Tracking failed: {str(e)}",
                "portal_url": url
            }
    
    async def batch_check(self, user_applications: List[Dict]) -> List[Dict]:
        """Check status for all user's applications"""
        tasks = []
        for app in user_applications:
            task = self.check_status(
                app["scheme_code"],
                app["application_id"],
                app.get("aadhaar")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            {"scheme": app["scheme_code"], "result": res} 
            for app, res in zip(user_applications, results)
        ]
