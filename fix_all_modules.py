import os
import re

MODULES_DIR = "modules"

# Saare modules automatically detect karo
modules = [d for d in os.listdir(MODULES_DIR) 
           if os.path.isdir(os.path.join(MODULES_DIR, d)) 
           and not d.startswith('__') 
           and not d.endswith('.py')]

print(f"🦁 Found {len(modules)} modules")
print("="*50)

for module in modules:
    module_path = os.path.join(MODULES_DIR, module)
    handler_path = os.path.join(module_path, "handler.py")
    init_path = os.path.join(module_path, "__init__.py")
    
    # ========== __init__.py ==========
    with open(init_path, "w") as f:
        f.write("""from .handler import router

__all__ = ['router']
""")
    
    # ========== handler.py ==========
    # Check if handler exists
    if os.path.exists(handler_path):
        with open(handler_path, 'r') as f:
            content = f.read()
        
        # Agar already router hai toh skip
        if 'router = APIRouter()' in content:
            print(f"⏩ {module} already has router")
            continue
        
        # Agar handler hai but router nahi hai toh replace
        print(f"🔄 Fixing {module}...")
        
        # Extract any custom code if needed (optional)
        # Simple template
        new_content = f"""from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def {module}_handler():
    return {{"status": "ok", "module": "{module}"}}

# ========== CUSTOM HANDLERS (Add below) ==========
# @router.post("/action")
# async def action():
#     return {{"result": "done"}}
"""
    else:
        # Naya handler banao
        print(f"✅ Creating {module}...")
        new_content = f"""from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def {module}_handler():
    return {{"status": "ok", "module": "{module}"}}
"""
    
    with open(handler_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ {module} fixed")

print("="*50)
print("🎉 ALL MODULES FIXED!")
print("🔄 Now run: python main.py")
