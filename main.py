from fastapi import FastAPI, HTTPException, Request  # ← Request ADD किया!
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import random
from datetime import datetime

# SINGLE FastAPI app
app = FastAPI(
    title="Singh Ji AI — 300 Agent Swarm",
    version="8.0.0"
)

# CORS — ONCE only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (बाकी endpoints same)
# ============================================================
# 🦁 11 CLAWS — 300 AGENTS SWARM DATA
# ============================================================

SWARM_DATA = {
    "claw_groups": {
        # 1. 🌾 Agriculture (DONE)
        "claw_1_agriculture": {
            "name": "🌾 Agriculture Claw",
            "leader": "CropMaster Agent",
            "agents_list": [
                {"id": "AGR-001", "name": "Crop Advisor Agent", "role": "क्या बोएं, कब बोएं", "status": "active"},
                {"id": "AGR-002", "name": "Price Tracker Agent", "role": "Mandi भाव real-time", "status": "active"},
                {"id": "AGR-003", "name": "Weather Farm Agent", "role": "फसल weather alert", "status": "active"},
                {"id": "AGR-004", "name": "Soil Health Agent", "role": "मिट्टी analysis", "status": "active"},
                {"id": "AGR-005", "name": "Pest Control Agent", "role": "कीट नियंत्रण", "status": "active"},
                {"id": "AGR-006", "name": "Irrigation Agent", "role": "सिंचाई planner", "status": "active"},
                {"id": "AGR-007", "name": "Organic Farming Agent", "role": "जैविक खेती guide", "status": "active"},
                {"id": "AGR-008", "name": "Market Link Agent", "role": "Direct buyer connect", "status": "active"},
                {"id": "AGR-009", "name": "Seed Bank Agent", "role": "बीज भंडार", "status": "active"},
                {"id": "AGR-010", "name": "Govt Scheme Agent", "role": "सरकारी योजना info", "status": "active"},
                {"id": "AGR-011", "name": "Drone Spray Agent", "role": "ड्रोन spraying", "status": "active"},
                {"id": "AGR-012", "name": "Livestock Agent", "role": "पशुपालन guide", "status": "active"},
                {"id": "AGR-013", "name": "Dairy Agent", "role": "Dairy farming", "status": "active"},
                {"id": "AGR-014", "name": "Fishery Agent", "role": "मछली पालन", "status": "active"},
                {"id": "AGR-015", "name": "Horticulture Agent", "role": "बागवानी expert", "status": "active"},
                {"id": "AGR-016", "name": "Agri Loan Agent", "role": "कृषि loan", "status": "active"},
                {"id": "AGR-017", "name": "Cold Storage Agent", "role": "कोल्ड स्टोरेज", "status": "active"},
                {"id": "AGR-018", "name": "Export Agent", "role": "Export guide", "status": "active"},
                {"id": "AGR-019", "name": "Farm Insurance Agent", "role": "फसल बीमा", "status": "active"},
                {"id": "AGR-020", "name": "Krishi Kendra Agent", "role": "KVK info", "status": "active"},
                {"id": "AGR-021", "name": "Vermicompost Agent", "role": "वर्मीकंपोस्ट", "status": "active"},
                {"id": "AGR-022", "name": "Biofuel Agent", "role": "जैव ईंधन", "status": "active"},
                {"id": "AGR-023", "name": "Farm Labour Agent", "role": "मजदूर booking", "status": "active"},
                {"id": "AGR-024", "name": "Agri News Agent", "role": "कृषि समाचार", "status": "active"},
                {"id": "AGR-025", "name": "Smart Farm Agent", "role": "IoT farming", "status": "active"},
                {"id": "AGR-026", "name": "Greenhouse Agent", "role": "Greenhouse setup", "status": "active"},
                {"id": "AGR-027", "name": "Polyhouse Agent", "role": "पॉलीहाउस", "status": "active"},
                {"id": "AGR-028", "name": "Mushroom Agent", "role": "मशरूम farming", "status": "active"},
                {"id": "AGR-029", "name": "Beekeeping Agent", "role": "मधुमक्खी पालन", "status": "active"},
                {"id": "AGR-030", "name": "Sericulture Agent", "role": "रेशम कीट पालन", "status": "active"},
            ]
        },

        # 2. 🏥 Health (DONE)
        "claw_2_health": {
            "name": "🏥 Health Claw",
            "leader": "Dr. Singh Agent",
            "agents_list": [
                {"id": "HLT-001", "name": "Symptom Checker Agent", "role": "बीमारी पहचान", "status": "active"},
                {"id": "HLT-002", "name": "Doctor Finder Agent", "role": "नजदीकी doctor", "status": "active"},
                {"id": "HLT-003", "name": "Medicine Info Agent", "role": "दवाई जानकारी", "status": "active"},
                {"id": "HLT-004", "name": "Ayurveda Agent", "role": "आयुर्वेद", "status": "active"},
                {"id": "HLT-005", "name": "Homeopathy Agent", "role": "होम्योपैथी", "status": "active"},
                {"id": "HLT-006", "name": "Yoga Agent", "role": "योग guide", "status": "active"},
                {"id": "HLT-007", "name": "Diet Planner Agent", "role": "आहार योजना", "status": "active"},
                {"id": "HLT-008", "name": "Mental Health Agent", "role": "मानसिक स्वास्थ्य", "status": "active"},
                {"id": "HLT-009", "name": "Vaccination Agent", "role": "टीकाकरण", "status": "active"},
                {"id": "HLT-010", "name": "Blood Bank Agent", "role": "Blood bank", "status": "active"},
                {"id": "HLT-011", "name": "Ambulance Agent", "role": "108 Ambulance", "status": "active"},
                {"id": "HLT-012", "name": "Health Insurance Agent", "role": "Health insurance", "status": "active"},
                {"id": "HLT-013", "name": "Lab Test Agent", "role": "Lab test booking", "status": "active"},
                {"id": "HLT-014", "name": "Surgery Guide Agent", "role": "Surgery info", "status": "active"},
                {"id": "HLT-015", "name": "Pregnancy Care Agent", "role": "गर्भावस्था care", "status": "active"},
                {"id": "HLT-016", "name": "Child Care Agent", "role": "बच्चों की देखभाल", "status": "active"},
                {"id": "HLT-017", "name": "Elder Care Agent", "role": "बुजुर्ग care", "status": "active"},
                {"id": "HLT-018", "name": "Diabetes Agent", "role": "Diabetes management", "status": "active"},
                {"id": "HLT-019", "name": "BP Heart Agent", "role": "BP/Heart care", "status": "active"},
                {"id": "HLT-020", "name": "Cancer Support Agent", "role": "Cancer support", "status": "active"},
                {"id": "HLT-021", "name": "Eye Care Agent", "role": "आंखों की देखभाल", "status": "active"},
                {"id": "HLT-022", "name": "Dental Agent", "role": "दांतों की देखभाल", "status": "active"},
                {"id": "HLT-023", "name": "Skin Care Agent", "role": "Skin treatment", "status": "active"},
                {"id": "HLT-024", "name": "Physiotherapy Agent", "role": "फिजियोथेरेपी", "status": "active"},
                {"id": "HLT-025", "name": "First Aid Agent", "role": "प्राथमिक चिकित्सा", "status": "active"},
                {"id": "HLT-026", "name": "Emergency Agent", "role": "Emergency guide", "status": "active"},
                {"id": "HLT-027", "name": "Medical Tourism Agent", "role": "Medical tourism", "status": "active"},
                {"id": "HLT-028", "name": "Telemedicine Agent", "role": "Online consultation", "status": "active"},
                {"id": "HLT-029", "name": "Health Record Agent", "role": "Medical records", "status": "active"},
                {"id": "HLT-030", "name": "Fitness Tracker Agent", "role": "Fitness tracking", "status": "active"},
            ]
        },

        # 3. 💰 Finance (NEW)
        "claw_3_finance": {
            "name": "💰 Finance Claw",
            "leader": "Banker Singh Agent",
            "agents_list": [
                {"id": "FIN-001", "name": "Loan Advisor Agent", "role": "Loan guide", "status": "active"},
                {"id": "FIN-002", "name": "Investment Agent", "role": "निवेश सलाह", "status": "active"},
                {"id": "FIN-003", "name": "Tax Filing Agent", "role": "Tax return", "status": "active"},
                {"id": "FIN-004", "name": "UPI Payment Agent", "role": "UPI transactions", "status": "active"},
                {"id": "FIN-005", "name": "Stock Market Agent", "role": "Share market", "status": "active"},
                {"id": "FIN-006", "name": "Mutual Fund Agent", "role": "SIP/Mutual fund", "status": "active"},
                {"id": "FIN-007", "name": "Insurance Agent", "role": "Insurance plans", "status": "active"},
                {"id": "FIN-008", "name": "Gold Rate Agent", "role": "Gold/silver rate", "status": "active"},
                {"id": "FIN-009", "name": "Currency Agent", "role": "Forex rates", "status": "active"},
                {"id": "FIN-010", "name": "Crypto Agent", "role": "Cryptocurrency", "status": "active"},
                {"id": "FIN-011", "name": "Budget Planner Agent", "role": "बजट योजना", "status": "active"},
                {"id": "FIN-012", "name": "Credit Score Agent", "role": "CIBIL score", "status": "active"},
                {"id": "FIN-013", "name": "EMI Calculator Agent", "role": "EMI calculation", "status": "active"},
                {"id": "FIN-014", "name": "Retirement Agent", "role": "Pension planning", "status": "active"},
                {"id": "FIN-015", "name": "GST Agent", "role": "GST filing", "status": "active"},
                {"id": "FIN-016", "name": "Banking Agent", "role": "Bank services", "status": "active"},
                {"id": "FIN-017", "name": "Digital Wallet Agent", "role": "Wallet management", "status": "active"},
                {"id": "FIN-018", "name": "Microfinance Agent", "role": "Small loans", "status": "active"},
                {"id": "FIN-019", "name": "Crowdfunding Agent", "role": "Crowdfunding", "status": "active"},
                {"id": "FIN-020", "name": "Financial News Agent", "role": "Finance news", "status": "active"},
                {"id": "FIN-021", "name": "FD RD Agent", "role": "Fixed deposit", "status": "active"},
                {"id": "FIN-022", "name": "NPS Agent", "role": "National Pension", "status": "active"},
                {"id": "FIN-023", "name": "PPF Agent", "role": "PPF account", "status": "active"},
                {"id": "FIN-024", "name": "Sukanya Agent", "role": "Sukanya Samriddhi", "status": "active"},
                {"id": "FIN-025", "name": "PM Kisan Agent", "role": "PM Kisan scheme", "status": "active"},
                {"id": "FIN-026", "name": "Scholarship Agent", "role": "Scholarship info", "status": "active"},
                {"id": "FIN-027", "name": "Business Loan Agent", "role": "Business loan", "status": "active"},
                {"id": "FIN-028", "name": "Home Loan Agent", "role": "Housing loan", "status": "active"},
                {"id": "FIN-029", "name": "Vehicle Loan Agent", "role": "Car/bike loan", "status": "active"},
                {"id": "FIN-030", "name": "Personal Loan Agent", "role": "Personal loan", "status": "active"},
            ]
        },

        # 4. 🎓 Education (NEW)
        "claw_4_education": {
            "name": "🎓 Education Claw",
            "leader": "Guru Singh Agent",
            "agents_list": [
                {"id": "EDU-001", "name": "Career Guide Agent", "role": "Career counselling", "status": "active"},
                {"id": "EDU-002", "name": "Exam Prep Agent", "role": "Exam preparation", "status": "active"},
                {"id": "EDU-003", "name": "College Finder Agent", "role": "College search", "status": "active"},
                {"id": "EDU-004", "name": "Scholarship Agent", "role": "Scholarship hunt", "status": "active"},
                {"id": "EDU-005", "name": "Online Course Agent", "role": "Course recommendation", "status": "active"},
                {"id": "EDU-006", "name": "Language Agent", "role": "Language learning", "status": "active"},
                {"id": "EDU-007", "name": "Coding Agent", "role": "Programming teach", "status": "active"},
                {"id": "EDU-008", "name": "Math Tutor Agent", "role": "Mathematics", "status": "active"},
                {"id": "EDU-009", "name": "Science Agent", "role": "Science projects", "status": "active"},
                {"id": "EDU-010", "name": "History Agent", "role": "History lessons", "status": "active"},
                {"id": "EDU-011", "name": "Geography Agent", "role": "Geography guide", "status": "active"},
                {"id": "EDU-012", "name": "UPSC Agent", "role": "UPSC preparation", "status": "active"},
                {"id": "EDU-013", "name": "SSC Agent", "role": "SSC exam prep", "status": "active"},
                {"id": "EDU-014", "name": "Banking Exam Agent", "role": "Bank PO prep", "status": "active"},
                {"id": "EDU-015", "name": "Railway Exam Agent", "role": "RRB exam prep", "status": "active"},
                {"id": "EDU-016", "name": "NEET Agent", "role": "Medical entrance", "status": "active"},
                {"id": "EDU-017", "name": "JEE Agent", "role": "Engineering entrance", "status": "active"},
                {"id": "EDU-018", "name": "CAT Agent", "role": "MBA entrance", "status": "active"},
                {"id": "EDU-019", "name": "GATE Agent", "role": "GATE prep", "status": "active"},
                {"id": "EDU-020", "name": "IELTS Agent", "role": "IELTS coaching", "status": "active"},
                {"id": "EDU-021", "name": "GRE Agent", "role": "GRE prep", "status": "active"},
                {"id": "EDU-022", "name": "Study Abroad Agent", "role": "Foreign education", "status": "active"},
                {"id": "EDU-023", "name": "Vocational Agent", "role": "ITI/vocational", "status": "active"},
                {"id": "EDU-024", "name": "Skill India Agent", "role": "Skill development", "status": "active"},
                {"id": "EDU-025", "name": "Digital India Agent", "role": "Digital literacy", "status": "active"},
                {"id": "EDU-026", "name": "Homework Agent", "role": "Homework help", "status": "active"},
                {"id": "EDU-027", "name": "Project Agent", "role": "Project assistance", "status": "active"},
                {"id": "EDU-028", "name": "Research Agent", "role": "Research paper", "status": "active"},
                {"id": "EDU-029", "name": "Library Agent", "role": "Book finder", "status": "active"},
                {"id": "EDU-030", "name": "Competition Agent", "role": "Olympiad prep", "status": "active"},
            ]
        },

        # 5. 🛒 E-Commerce (NEW)
        "claw_5_ecommerce": {
            "name": "🛒 E-Commerce Claw",
            "leader": "ShopKing Agent",
            "agents_list": [
                {"id": "ECM-001", "name": "Price Compare Agent", "role": "Best price finder", "status": "active"},
                {"id": "ECM-002", "name": "Deal Hunter Agent", "role": "Best deals", "status": "active"},
                {"id": "ECM-003", "name": "Coupon Agent", "role": "Coupon codes", "status": "active"},
                {"id": "ECM-004", "name": "Cashback Agent", "role": "Cashback offers", "status": "active"},
                {"id": "ECM-005", "name": "Review Agent", "role": "Product reviews", "status": "active"},
                {"id": "ECM-006", "name": "Wishlist Agent", "role": "Price drop alert", "status": "active"},
                {"id": "ECM-007", "name": "Return Agent", "role": "Return policy", "status": "active"},
                {"id": "ECM-008", "name": "Delivery Agent", "role": "Delivery tracking", "status": "active"},
                {"id": "ECM-009", "name": "Seller Agent", "role": "Seller dashboard", "status": "active"},
                {"id": "ECM-010", "name": "Inventory Agent", "role": "Stock management", "status": "active"},
                {"id": "ECM-011", "name": "Payment Agent", "role": "Payment gateway", "status": "active"},
                {"id": "ECM-012", "name": "Fraud Detect Agent", "role": "Fraud protection", "status": "active"},
                {"id": "ECM-013", "name": "Subscription Agent", "role": "Subscription manage", "status": "active"},
                {"id": "ECM-014", "name": "Gift Card Agent", "role": "Gift cards", "status": "active"},
                {"id": "ECM-015", "name": "Auction Agent", "role": "Online bidding", "status": "active"},
                {"id": "ECM-016", "name": "Wholesale Agent", "role": "B2B wholesale", "status": "active"},
                {"id": "ECM-017", "name": "Dropship Agent", "role": "Dropshipping", "status": "active"},
                {"id": "ECM-018", "name": "Import Export Agent", "role": "Global trade", "status": "active"},
                {"id": "ECM-019", "name": "Local Market Agent", "role": "Nearby shops", "status": "active"},
                {"id": "ECM-020", "name": "Fashion Agent", "role": "Fashion trends", "status": "active"},
                {"id": "ECM-021", "name": "Electronics Agent", "role": "Gadget guide", "status": "active"},
                {"id": "ECM-022", "name": "Grocery Agent", "role": "Grocery delivery", "status": "active"},
                {"id": "ECM-023", "name": "Medicine Delivery Agent", "role": "Online pharmacy", "status": "active"},
                {"id": "ECM-024", "name": "Furniture Agent", "role": "Furniture shopping", "status": "active"},
                {"id": "ECM-025", "name": "Appliance Agent", "role": "Home appliances", "status": "active"},
                {"id": "ECM-026", "name": "Jewelry Agent", "role": "Jewelry shopping", "status": "active"},
                {"id": "ECM-027", "name": "Sports Agent", "role": "Sports gear", "status": "active"},
                {"id": "ECM-028", "name": "Books Agent", "role": "Book store", "status": "active"},
                {"id": "ECM-029", "name": "Toys Agent", "role": "Kids toys", "status": "active"},
                {"id": "ECM-030", "name": "Auto Parts Agent", "role": "Vehicle parts", "status": "active"},
            ]
        },

        # 6. 🚗 Transport (NEW)
        "claw_6_transport": {
            "name": "🚗 Transport Claw",
            "leader": "Chalak Singh Agent",
            "agents_list": [
                {"id": "TRN-001", "name": "Cab Booking Agent", "role": "Taxi/Ola/Uber", "status": "active"},
                {"id": "TRN-002", "name": "Train Ticket Agent", "role": "IRCTC booking", "status": "active"},
                {"id": "TRN-003", "name": "Bus Ticket Agent", "role": "Bus booking", "status": "active"},
                {"id": "TRN-004", "name": "Flight Agent", "role": "Air ticket", "status": "active"},
                {"id": "TRN-005", "name": "Metro Agent", "role": "Metro route", "status": "active"},
                {"id": "TRN-006", "name": "Auto Rickshaw Agent", "role": "Auto booking", "status": "active"},
                {"id": "TRN-007", "name": "Bike Taxi Agent", "role": "Rapido/Bike", "status": "active"},
                {"id": "TRN-008", "name": "EV Charging Agent", "role": "Charging station", "status": "active"},
                {"id": "TRN-009", "name": "Parking Agent", "role": "Parking finder", "status": "active"},
                {"id": "TRN-010", "name": "Toll Agent", "role": "FASTag/Recharge", "status": "active"},
                {"id": "TRN-011", "name": "Fuel Price Agent", "role": "Petrol/Diesel rate", "status": "active"},
                {"id": "TRN-012", "name": "Vehicle Reg Agent", "role": "RTO services", "status": "active"},
                {"id": "TRN-013", "name": "DL Agent", "role": "Driving license", "status": "active"},
                {"id": "TRN-014", "name": "Insurance Agent", "role": "Vehicle insurance", "status": "active"},
                {"id": "TRN-015", "name": "Breakdown Agent", "role": "Roadside help", "status": "active"},
                {"id": "TRN-016", "name": "Traffic Agent", "role": "Traffic updates", "status": "active"},
                {"id": "TRN-017", "name": "Route Planner Agent", "role": "Best route", "status": "active"},
                {"id": "TRN-018", "name": "Car Pool Agent", "role": "Carpooling", "status": "active"},
                {"id": "TRN-019", "name": "Bike Rental Agent", "role": "Bike on rent", "status": "active"},
                {"id": "TRN-020", "name": "Car Rental Agent", "role": "Car on rent", "status": "active"},
                {"id": "TRN-021", "name": "Logistics Agent", "role": "Goods transport", "status": "active"},
                {"id": "TRN-022", "name": "Courier Agent", "role": "Parcel tracking", "status": "active"},
                {"id": "TRN-023", "name": "Shipping Agent", "role": "Sea cargo", "status": "active"},
                {"id": "TRN-024", "name": "Warehouse Agent", "role": "Storage finder", "status": "active"},
                {"id": "TRN-025", "name": "Fleet Agent", "role": "Fleet management", "status": "active"},
                {"id": "TRN-026", "name": "GPS Tracker Agent", "role": "Live tracking", "status": "active"},
                {"id": "TRN-027", "name": "Taxi Driver Agent", "role": "Driver onboarding", "status": "active"},
                {"id": "TRN-028", "name": "School Bus Agent", "role": "School transport", "status": "active"},
                {"id": "TRN-029", "name": "Ambulance Agent", "role": "Medical transport", "status": "active"},
                {"id": "TRN-030", "name": "Helicopter Agent", "role": "Air ambulance", "status": "active"},
            ]
        },

        # 7. 🏠 Real Estate (NEW)
        "claw_7_realestate": {
            "name": "🏠 Real Estate Claw",
            "leader": "Makan Malik Agent",
            "agents_list": [
                {"id": "RSE-001", "name": "Buy House Agent", "role": "Property purchase", "status": "active"},
                {"id": "RSE-002", "name": "Rent House Agent", "role": "Rental search", "status": "active"},
                {"id": "RSE-003", "name": "Sell House Agent", "role": "Property listing", "status": "active"},
                {"id": "RSE-004", "name": "PG/Hostel Agent", "role": "PG finder", "status": "active"},
                {"id": "RSE-005", "name": "Commercial Agent", "role": "Office/Shop", "status": "active"},
                {"id": "RSE-006", "name": "Land Agent", "role": "Plot/Land", "status": "active"},
                {"id": "RSE-007", "name": "Vastu Agent", "role": "Vastu consultant", "status": "active"},
                {"id": "RSE-008", "name": "Interior Agent", "role": "Interior design", "status": "active"},
                {"id": "RSE-009", "name": "Construction Agent", "role": "Builder connect", "status": "active"},
                {"id": "RSE-010", "name": "Home Loan Agent", "role": "Housing finance", "status": "active"},
                {"id": "RSE-011", "name": "Property Valuation Agent", "role": "Rate calculator", "status": "active"},
                {"id": "RSE-012", "name": "Legal Agent", "role": "Property lawyer", "status": "active"},
                {"id": "RSE-013", "name": "RERA Agent", "role": "RERA compliance", "status": "active"},
                {"id": "RSE-014", "name": "NRI Agent", "role": "NRI investment", "status": "active"},
                {"id": "RSE-015", "name": "Smart City Agent", "role": "Smart home", "status": "active"},
                {"id": "RSE-016", "name": "Solar Home Agent", "role": "Solar panel", "status": "active"},
                {"id": "RSE-017", "name": "Green Building Agent", "role": "Eco-friendly", "status": "active"},
                {"id": "RSE-018", "name": "Co-working Agent", "role": "Shared office", "status": "active"},
                {"id": "RSE-019", "name": "Warehouse Agent", "role": "Godown/Storage", "status": "active"},
                {"id": "RSE-020", "name": "Farm House Agent", "role": "Agricultural land", "status": "active"},
                {"id": "RSE-021", "name": "Resort Agent", "role": "Holiday home", "status": "active"},
                {"id": "RSE-022", "name": "Heritage Agent", "role": "Heritage property", "status": "active"},
                {"id": "RSE-023", "name": "Parking Space Agent", "role": "Parking buy/rent", "status": "active"},
                {"id": "RSE-024", "name": "Property Tax Agent", "role": "Tax calculation", "status": "active"},
                {"id": "RSE-025", "name": "Mutation Agent", "role": "Name transfer", "status": "active"},
                {"id": "RSE-026", "name": "Registry Agent", "role": "Document registry", "status": "active"},
                {"id": "RSE-027", "name": "Broker Agent", "role": "Agent finder", "status": "active"},
                {"id": "RSE-028", "name": "Rent Agreement Agent", "role": "Agreement draft", "status": "active"},
                {"id": "RSE-029", "name": "Home Inspection Agent", "role": "Quality check", "status": "active"},
                {"id": "RSE-030", "name": "Property News Agent", "role": "Market updates", "status": "active"},
            ]
        },

        # 8. 🍔 Food (NEW)
        "claw_8_food": {
            "name": "🍔 Food Claw",
            "leader": "Chef Singh Agent",
            "agents_list": [
                {"id": "FOD-001", "name": "Restaurant Finder Agent", "role": "Nearby restaurant", "status": "active"},
                {"id": "FOD-002", "name": "Food Delivery Agent", "role": "Zomato/Swiggy", "status": "active"},
                {"id": "FOD-003", "name": "Recipe Agent", "role": "Recipe guide", "status": "active"},
                {"id": "FOD-004", "name": "Diet Plan Agent", "role": "Healthy diet", "status": "active"},
                {"id": "FOD-005", "name": "Grocery Agent", "role": "Grocery delivery", "status": "active"},
                {"id": "FOD-006", "name": "Organic Food Agent", "role": "Organic products", "status": "active"},
                {"id": "FOD-007", "name": "Street Food Agent", "role": "Local delicacies", "status": "active"},
                {"id": "FOD-008", "name": "Catering Agent", "role": "Event catering", "status": "active"},
                {"id": "FOD-009", "name": "Tiffin Service Agent", "role": "Daily tiffin", "status": "active"},
                {"id": "FOD-010", "name": "Bakery Agent", "role": "Cakes/bakery", "status": "active"},
                {"id": "FOD-011", "name": "Beverage Agent", "role": "Drinks/juices", "status": "active"},
                {"id": "FOD-012", "name": "Cloud Kitchen Agent", "role": "Virtual restaurant", "status": "active"},
                {"id": "FOD-013", "name": "Food Safety Agent", "role": "FSSAI guide", "status": "active"},
                {"id": "FOD-014", "name": "Nutrition Agent", "role": "Nutrition facts", "status": "active"},
                {"id": "FOD-015", "name": "Vegan Agent", "role": "Vegan options", "status": "active"},
                {"id": "FOD-016", "name": "Jain Food Agent", "role": "Jain cuisine", "status": "active"},
                {"id": "FOD-017", "name": "Halal Food Agent", "role": "Halal certified", "status": "active"},
                {"id": "FOD-018", "name": "Festival Food Agent", "role": "Special occasions", "status": "active"},
                {"id": "FOD-019", "name": "Regional Cuisine Agent", "role": "State specials", "status": "active"},
                {"id": "FOD-020", "name": "Food Review Agent", "role": "Ratings/reviews", "status": "active"},
                {"id": "FOD-021", "name": "Table Booking Agent", "role": "Restaurant reserve", "status": "active"},
                {"id": "FOD-022", "name": "Party Order Agent", "role": "Bulk order", "status": "active"},
                {"id": "FOD-023", "name": "Midnight Hunger Agent", "role": "Late night food", "status": "active"},
                {"id": "FOD-024", "name": "Healthy Snack Agent", "role": "Nutritious snacks", "status": "active"},
                {"id": "FOD-025", "name": "Baby Food Agent", "role": "Infant nutrition", "status": "active"},
                {"id": "FOD-026", "name": "Pet Food Agent", "role": "Animal food", "status": "active"},
                {"id": "FOD-027", "name": "Food Truck Agent", "role": "Mobile kitchen", "status": "active"},
                {"id": "FOD-028", "name": "Cooking Class Agent", "role": "Learn cooking", "status": "active"},
                {"id": "FOD-029", "name": "Meal Prep Agent", "role": "Weekly meal plan", "status": "active"},
                {"id": "FOD-030", "name": "Food Waste Agent", "role": "Zero waste", "status": "active"},
            ]
        },

        # 9. 💼 Jobs (NEW)
        "claw_9_jobs": {
            "name": "💼 Jobs Claw",
            "leader": "HR Singh Agent",
            "agents_list": [
                {"id": "JOB-001", "name": "Job Search Agent", "role": "Vacancy finder", "status": "active"},
                {"id": "JOB-002", "name": "Resume Builder Agent", "role": "CV maker", "status": "active"},
                {"id": "JOB-003", "name": "Interview Prep Agent", "role": "Mock interview", "status": "active"},
                {"id": "JOB-004", "name": "Salary Negotiate Agent", "role": "Package discuss", "status": "active"},
                {"id": "JOB-005", "name": "Freelance Agent", "role": "Freelance work", "status": "active"},
                {"id": "JOB-006", "name": "Internship Agent", "role": "Intern search", "status": "active"},
                {"id": "JOB-007", "name": "Govt Job Agent", "role": "Sarkari naukri", "status": "active"},
                {"id": "JOB-008", "name": "Private Job Agent", "role": "Corporate jobs", "status": "active"},
                {"id": "JOB-009", "name": "Startup Job Agent", "role": "Startup hiring", "status": "active"},
                {"id": "JOB-010", "name": "Remote Job Agent", "role": "Work from home", "status": "active"},
                {"id": "JOB-011", "name": "Part Time Agent", "role": "Side income", "status": "active"},
                {"id": "JOB-012", "name": "Skill Test Agent", "role": "Aptitude test", "status": "active"},
                {"id": "JOB-013", "name": "LinkedIn Agent", "role": "Profile optimize", "status": "active"},
                {"id": "JOB-014", "name": "Naukri Agent", "role": "Naukri.com", "status": "active"},
                {"id": "JOB-015", "name": "Indeed Agent", "role": "Indeed jobs", "status": "active"},
                {"id": "JOB-016", "name": "Glassdoor Agent", "role": "Company reviews", "status": "active"},
                {"id": "JOB-017", "name": "Referral Agent", "role": "Employee referral", "status": "active"},
                {"id": "JOB-018", "name": "Campus Placement Agent", "role": "College hiring", "status": "active"},
                {"id": "JOB-019", "name": "Walk-in Agent", "role": "Direct interview", "status": "active"},
                {"id": "JOB-020", "name": "Contract Job Agent", "role": "Temporary work", "status": "active"},
                {"id": "JOB-021", "name": "NGO Job Agent", "role": "Social work", "status": "active"},
                {"id": "JOB-022", "name": "Army Job Agent", "role": "Defence forces", "status": "active"},
                {"id": "JOB-023", "name": "Police Job Agent", "role": "Law enforcement", "status": "active"},
                {"id": "JOB-024", "name": "Teaching Job Agent", "role": "Teacher vacancy", "status": "active"},
                {"id": "JOB-025", "name": "Medical Job Agent", "role": "Hospital jobs", "status": "active"},
                {"id": "JOB-026", "name": "Engineering Job Agent", "role": "Tech jobs", "status": "active"},
                {"id": "JOB-027", "name": "Banking Job Agent", "role": "Bank PO/Clerk", "status": "active"},
                {"id": "JOB-028", "name": "Aviation Job Agent", "role": "Airline jobs", "status": "active"},
                {"id": "JOB-029", "name": "Hospitality Job Agent", "role": "Hotel jobs", "status": "active"},
                {"id": "JOB-030", "name": "Agriculture Job Agent", "role": "Farm jobs", "status": "active"},
            ]
        },

        # 10. 🌤️ Weather (NEW)
        "claw_10_weather": {
            "name": "🌤️ Weather Claw",
            "leader": "Mausam Agent",
            "agents_list": [
                {"id": "WTH-001", "name": "Current Weather Agent", "role": "Live weather", "status": "active"},
                {"id": "WTH-002", "name": "Forecast Agent", "role": "7-day forecast", "status": "active"},
                {"id": "WTH-003", "name": "Rain Alert Agent", "role": "Barish warning", "status": "active"},
                {"id": "WTH-004", "name": "Flood Alert Agent", "role": "Bhad warning", "status": "active"},
                {"id": "WTH-005", "name": "Cyclone Agent", "role": "Cyclone track", "status": "active"},
                {"id": "WTH-006", "name": "Earthquake Agent", "role": "Seismic alert", "status": "active"},
                {"id": "WTH-007", "name": "Tsunami Agent", "role": "Sea wave alert", "status": "active"},
                {"id": "WTH-008", "name": "Heat Wave Agent", "role": "Garmi warning", "status": "active"},
                {"id": "WTH-009", "name": "Cold Wave Agent", "role": "Thand warning", "status": "active"},
                {"id": "WTH-010", "name": "Fog Alert Agent", "role": "Kohra warning", "status": "active"},
                {"id": "WTH-011", "name": "Air Quality Agent", "role": "AQI index", "status": "active"},
                {"id": "WTH-012", "name": "UV Index Agent", "role": "Sun protection", "status": "active"},
                {"id": "WTH-013", "name": "Pollen Alert Agent", "role": "Allergy warning", "status": "active"},
                {"id": "WTH-014", "name": "Monsoon Agent", "role": "Rain forecast", "status": "active"},
                {"id": "WTH-015", "name": "Winter Agent", "role": "Cold season", "status": "active"},
                {"id": "WTH-016", "name": "Summer Agent", "role": "Hot season", "status": "active"},
                {"id": "WTH-017", "name": "Spring Agent", "role": "Flower season", "status": "active"},
                {"id": "WTH-018", "name": "Autumn Agent", "role": "Fall season", "status": "active"},
                {"id": "WTH-019", "name": "Drought Agent", "role": "Sukha warning", "status": "active"},
                {"id": "WTH-020", "name": "Lightning Agent", "role": "Bijli alert", "status": "active"},
                {"id": "WTH-021", "name": "Wind Speed Agent", "role": "Hawa speed", "status": "active"},
                {"id": "WTH-022", "name": "Humidity Agent", "role": "Nami level", "status": "active"},
                {"id": "WTH-023", "name": "Visibility Agent", "role": "Dikhne ki doori", "status": "active"},
                {"id": "WTH-024", "name": "Sunrise Sunset Agent", "role": "Suryoday/Suryast", "status": "active"},
                {"id": "WTH-025", "name": "Moon Phase Agent", "role": "Chand ki dasha", "status": "active"},
                {"id": "WTH-026", "name": "Tide Agent", "role": "Jowar/Bhawar", "status": "active"},
                {"id": "WTH-027", "name": "Snowfall Agent", "role": "Barfbari", "status": "active"},
                {"id": "WTH-028", "name": "Hailstorm Agent", "role": "Ole warning", "status": "active"},
                {"id": "WTH-029", "name": "Dust Storm Agent", "role": "Andhi alert", "status": "active"},
                {"id": "WTH-030", "name": "Climate Change Agent", "role": "Global warming", "status": "active"},
            ]
        },

        # 11. 🎬 Entertainment (NEW)
        "claw_11_entertainment": {
            "name": "🎬 Entertainment Claw",
            "leader": "Star Singh Agent",
            "agents_list": [
                {"id": "ENT-001", "name": "Movie Finder Agent", "role": "Film search", "status": "active"},
                {"id": "ENT-002", "name": "OTT Guide Agent", "role": "Netflix/Prime", "status": "active"},
                {"id": "ENT-003", "name": "Music Agent", "role": "Gaana/Spotify", "status": "active"},
                {"id": "ENT-004", "name": "Gaming Agent", "role": "Game recommendation", "status": "active"},
                {"id": "ENT-005", "name": "Book Reader Agent", "role": "E-book suggest", "status": "active"},
                {"id": "ENT-006", "name": "News Agent", "role": "Daily news", "status": "active"},
                {"id": "ENT-007", "name": "Sports Agent", "role": "Live scores", "status": "active"},
                {"id": "ENT-008", "name": "Cricket Agent", "role": "IPL/World Cup", "status": "active"},
                {"id": "ENT-009", "name": "Football Agent", "role": "FIFA/ISL", "status": "active"},
                {"id": "ENT-010", "name": "Kabaddi Agent", "role": "Pro Kabaddi", "status": "active"},
                {"id": "ENT-011", "name": "Wrestling Agent", "role": "WWE/Kushti", "status": "active"},
                {"id": "ENT-012", "name": "Comedy Agent", "role": "Hasi-mazaak", "status": "active"},
                {"id": "ENT-013", "name": "Astrology Agent", "role": "Rashifal", "status": "active"},
                {"id": "ENT-014", "name": "Horoscope Agent", "role": "Daily kundli", "status": "active"},
                {"id": "ENT-015", "name": "Meme Agent", "role": "Funny memes", "status": "active"},
                {"id": "ENT-016", "name": "Short Video Agent", "role": "Reels/Shorts", "status": "active"},
                {"id": "ENT-017", "name": "Podcast Agent", "role": "Audio shows", "status": "active"},
                {"id": "ENT-018", "name": "Radio Agent", "role": "FM stations", "status": "active"},
                {"id": "ENT-019", "name": "TV Guide Agent", "role": "Channel schedule", "status": "active"},
                {"id": "ENT-020", "name": "Event Ticket Agent", "role": "Concert/movie tix", "status": "active"},
                {"id": "ENT-021", "name": "Celebrity News Agent", "role": "Star gossip", "status": "active"},
                {"id": "ENT-022", "name": "Fan Club Agent", "role": "Fan community", "status": "active"},
                {"id": "ENT-023", "name": "Dance Agent", "role": "Dance tutorials", "status": "active"},
                {"id": "ENT-024", "name": "Singing Agent", "role": "Music lessons", "status": "active"},
                {"id": "ENT-025", "name": "Photography Agent", "role": "Photo tips", "status": "active"},
                {"id": "ENT-026", "name": "Art Gallery Agent", "role": "Painting/Art", "status": "active"},
                {"id": "ENT-027", "name": "Theatre Agent", "role": "Drama/plays", "status": "active"},
                {"id": "ENT-028", "name": "Standup Agent", "role": "Comedy shows", "status": "active"},
                {"id": "ENT-029", "name": "Reality Show Agent", "role": "TV reality", "status": "active"},
                {"id": "ENT-030", "name": "Festival Agent", "role": "Event calendar", "status": "active"},
            ]
        },
    }
}

# ============================================================
# TRACKERS
# ============================================================

active_missions = {}
step_tracker = {"current": 0, "max": 4000}
@app.post("/api/memory/store")
async def store_memory(request: Request):
    data = await request.json()
    memory.add(data.get("message"), user_id=data.get("user_id"))
    return {"status": "stored"}

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    total_agents = sum(len(c["agents_list"]) for c in SWARM_DATA["claw_groups"].values())
    return {
        "system": "🦁 Singh Ji AI — 300+ Agent Swarm",
        "version": "v8.0",
        "agents": total_agents,
        "claws": len(SWARM_DATA["claw_groups"]),
        "max_steps": 4000,
        "status": "🔥 ACTIVE 🔥"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/swarm/stats")
async def swarm_stats():
    total_agents = sum(len(c["agents_list"]) for c in SWARM_DATA["claw_groups"].values())
    active_agents = sum(
        1 for c in SWARM_DATA["claw_groups"].values() 
        for a in c["agents_list"] 
        if a["status"] == "active"
    )
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_claws": len(SWARM_DATA["claw_groups"]),
        "max_steps": 4000,
        "steps_used": step_tracker["current"],
        "steps_remaining": 4000 - step_tracker["current"],
        "status": "active"
    }

@app.get("/swarm/claws")
async def list_claws():
    return {
        "claws": [
            {
                "id": claw_id,
                "name": claw["name"],
                "leader": claw["leader"],
                "agent_count": len(claw["agents_list"])
            }
            for claw_id, claw in SWARM_DATA["claw_groups"].items()
        ]
    }

@app.get("/swarm/claw/{claw_id}")
async def get_claw(claw_id: str):
    if claw_id not in SWARM_DATA["claw_groups"]:
        raise HTTPException(status_code=404, detail="Claw not found")
    return SWARM_DATA["claw_groups"][claw_id]

@app.get("/swarm/agents")
async def list_all_agents():
    all_agents = []
    for claw_id, claw in SWARM_DATA["claw_groups"].items():
        for agent in claw["agents_list"]:
            agent_copy = agent.copy()
            agent_copy["claw"] = claw["name"]
            all_agents.append(agent_copy)
    return {
        "total": len(all_agents),
        "agents": all_agents
    }

@app.get("/swarm/agent/{agent_id}")
async def get_agent(agent_id: str):
    for claw_id, claw in SWARM_DATA["claw_groups"].items():
        for agent in claw["agents_list"]:
            if agent["id"] == agent_id:
                result = agent.copy()
                result["claw"] = claw["name"]
                return result
    raise HTTPException(status_code=404, detail="Agent not found")

@app.get("/swarm/search")
async def search_agents(q: str):
    results = []
    q_lower = q.lower()
    for claw_id, claw in SWARM_DATA["claw_groups"].items():
        for agent in claw["agents_list"]:
            if (q_lower in agent["name"].lower() or 
                q_lower in agent["role"].lower() or
                q_lower in claw["name"].lower()):
                agent_copy = agent.copy()
                agent_copy["claw"] = claw["name"]
                results.append(agent_copy)
    return {
        "query": q,
        "count": len(results),
        "agents": results
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
