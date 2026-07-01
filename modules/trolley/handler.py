import os
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
            action = params.get('action', 'list').strip()
        else:
            body = await request.json()
            action = body.get('action', 'list').strip()
        
        products = [
            {"id": 1, "name": "Wheat Flour (5kg)", "price": 250, "category": "grocery"},
            {"id": 2, "name": "Rice Basmati (5kg)", "price": 450, "category": "grocery"},
            {"id": 3, "name": "Sugar (1kg)", "price": 45, "category": "grocery"},
            {"id": 4, "name": "Cooking Oil (1L)", "price": 120, "category": "grocery"},
            {"id": 5, "name": "Dal Toor (1kg)", "price": 140, "category": "grocery"},
            {"id": 6, "name": "Salt (1kg)", "price": 20, "category": "grocery"},
            {"id": 7, "name": "Onion (1kg)", "price": 35, "category": "vegetable"},
            {"id": 8, "name": "Potato (1kg)", "price": 30, "category": "vegetable"}
        ]
        
        if action == 'list':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "total": len(products),
                    "products": products,
                    "categories": list(set(p["category"] for p in products)),
                    "note": "E-commerce module — payment gateway on hold until 1000+ users"
                }
            })
        
        elif action == 'cart':
            return JSONResponse(content={
                "success": True,
                "error": None,
                "data": {
                    "message": "Cart system coming soon",
                    "status": "Pending payment gateway activation",
                    "note": "Razorpay ready but on hold"
                }
            })
        
        return JSONResponse(content={
            "success": True,
            "error": None,
            "data": {
                "actions": ["list", "cart"],
                "message": "Use ?action=list or ?action=cart"
            }
        })
        
    except Exception as e:
        logger.error(f"Trolley crash: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, "error": str(e), "data": None
        })
