"""
Auto-form filling for common scheme portals
Uses Selenium/Playwright for browser automation
"""

import asyncio
from typing import Dict, List
from playwright.async_api import async_playwright

class FormFiller:
    """Automates form filling on scheme portals"""
    
    PORTAL_SELECTORS = {
        "pmkisan.gov.in": {
            "aadhaar": "#aadhaar_number",
            "name": "#farmer_name", 
            "bank_account": "#account_number",
            "ifsc": "#ifsc_code",
            "submit": "#btnSubmit"
        },
        "scholarships.gov.in": {
            "aadhaar": "#aadharId",
            "name": "#studentName",
            "caste": "#casteCategory",
            "income": "#familyIncome",
            "submit": "#finalSubmit"
        }
    }
    
    async def fill_form(self, portal_url: str, user_data: Dict, scheme_code: str):
        """
        Auto-fill form on a scheme portal
        Returns: success boolean, application_id, screenshot_path
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(portal_url)
                await page.wait_for_load_state("networkidle")
                
                # Get selectors for this portal
                domain = portal_url.replace("https://", "").replace("http://", "").split("/")[0]
                selectors = self.PORTAL_SELECTORS.get(domain, {})
                
                # Fill form fields
                for field, selector in selectors.items():
                    if field in user_data and field != "submit":
                        try:
                            await page.fill(selector, str(user_data[field]))
                            await asyncio.sleep(0.5)  # Human-like delay
                        except:
                            pass  # Field might not exist
                
                # Take screenshot before submit
                screenshot_path = f"/tmp/form_{scheme_code}_{user_data.get('aadhaar', 'unknown')}.png"
                await page.screenshot(path=screenshot_path)
                
                # Submit form (optional - can be manual)
                # await page.click(selectors.get("submit", ""))
                
                await browser.close()
                return True, None, screenshot_path
                
            except Exception as e:
                await browser.close()
                return False, str(e), None
    
    def generate_prefilled_pdf(self, scheme: Dict, user_data: Dict) -> str:
        """
        Generate a pre-filled PDF form for offline submission
        Returns PDF file path
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        pdf_path = f"/tmp/prefilled_{scheme['scheme_code']}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=A4)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, scheme["name"])
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"Application Date: {datetime.now().strftime('%d-%m-%Y')}")
        
        # Pre-filled fields
        y = 750
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "PRE-FILLED APPLICATION")
        y -= 30
        
        fields = [
            ("Full Name", user_data.get("name", "")),
            ("Aadhaar Number", user_data.get("aadhaar", "")),
            ("Date of Birth", user_data.get("dob", "")),
            ("Gender", user_data.get("gender", "")),
            ("Caste Category", user_data.get("caste_category", "")),
            ("Annual Income", f"₹{user_data.get('annual_income', 0):,}"),
            ("Bank Account", user_data.get("bank_account", "")),
            ("IFSC Code", user_data.get("ifsc", "")),
            ("Mobile Number", user_data.get("mobile", "")),
            ("Address", user_data.get("address", "")),
        ]
        
        for label, value in fields:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, f"{label}:")
            c.setFont("Helvetica", 10)
            c.drawString(200, y, str(value))
            y -= 25
        
        # Document checklist
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "DOCUMENTS TO ATTACH:")
        y -= 25
        
        for doc in scheme.get("documents_required", []):
            c.setFont("Helvetica", 10)
            c.drawString(70, y, f"☐ {doc}")
            y -= 20
        
        # Declaration
        y -= 30
        c.setFont("Helvetica", 9)
        c.drawString(50, y, "I hereby declare that all information provided is true to the best of my knowledge.")
        y -= 40
        c.drawString(50, y, "Signature: _______________________")
        c.drawString(350, y, "Date: _______________________")
        
        c.save()
        return pdf_path
