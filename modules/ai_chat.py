# ... existing code upar ...

def get_ai_response(message: str, model: str = "llama3-70b-8192", 
                   system_prompt: Optional[str] = None,
                   history: Optional[list] = None) -> Dict:
    """Get AI response using Groq"""
    # ... pura code ...
    # ... pura code ...
    # ... pura code ...

# ============================================
# YAHAN SE NAYA CODE — END में add करो
# ============================================

def handler(request_data):
    """
    Singh Ji AI module router handler.
    """
    message = request_data.get("json", {}).get("message", "")
    if not message:
        message = request_data.get("args", {}).get("message", "Hello")
    
    result = get_ai_response(
        message=message,
        model=request_data.get("json", {}).get("model", "llama3-70b-8192"),
        system_prompt=request_data.get("json", {}).get("system_prompt", None)
    )
    
    return {
        "module": "ai_chat",
        "status": "success" if result.get("success") else "error",
        "data": result
    }
