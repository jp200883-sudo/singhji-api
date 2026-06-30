# ═══════════════════════════════════════════════════════
#   SINGH JI AI ULTRA v7.0 — AUTO-WRAPPER FIX
#   29 file modules → auto handler banega
# ═══════════════════════════════════════════════════════

import importlib.util
import sys
import inspect
from pathlib import Path
from typing import Optional, Dict, Callable, Any

# ─── Logger (tumhara existing logger use karo) ──────────
# import logging
# logger = logging.getLogger(__name__)


# ─── Auto Handler Wrapper ───────────────────────────────
def create_auto_handler(module_name: str, module_obj) -> Callable:
    """
    Agar module mein handler function nahi hai,
    toh auto wrapper banao jo module ke functions ko call kare.
    """
    
    def auto_handler(request_data: Any = None) -> Dict:
        """Auto-generated handler for module"""
        
        # Module ke saare functions dhoondo (private nahi)
        functions = {
            name: func 
            for name, func in vars(module_obj).items()
            if callable(func) and not name.startswith('_')
        }
        
        # Sabse pehla function lo (jo handler nahi hai)
        main_func = None
        main_name = None
        for name, func in functions.items():
            if name not in ('handler', 'Handler', 'create_auto_handler', 'auto_handler'):
                main_func = func
                main_name = name
                break
        
        # Agar function mila, toh call karo
        if main_func:
            try:
                # Pehle try with request_data
                sig = inspect.signature(main_func)
                if len(sig.parameters) > 0:
                    result = main_func(request_data)
                else:
                    result = main_func()
                return {
                    "module": module_name,
                    "status": "success",
                    "handler_type": "auto",
                    "function_called": main_name,
                    "data": result
                }
            except Exception as e:
                return {
                    "module": module_name,
                    "status": "error",
                    "handler_type": "auto",
                    "error": str(e),
                    "available_functions": list(functions.keys())
                }
        
        # Fallback — simple response
        return {
            "module": module_name,
            "status": "success",
            "handler_type": "auto",
            "message": f"{module_name} module active via auto-wrapper!",
            "available_functions": list(functions.keys())
        }
    
    return auto_handler


# ─── Load Single Module ─────────────────────────────────
def load_module(module_name: str, modules_dir: str = "modules") -> Optional[Dict]:
    """
    Module load karo — folder ho ya file, handler ho ya nahi!
    """
    modules_path = Path(modules_dir)
    module_path = modules_path / module_name
    info = {
        "name": module_name,
        "type": None,
        "handler": None,
        "status": "loading"
    }
    
    try:
        # ═══ FOLDER MODULE ═══
        if module_path.is_dir():
            info["type"] = "folder"
            init_file = module_path / "__init__.py"
            handler_file = module_path / "handler.py"
            target = init_file if init_file.exists() else handler_file
            
            if not target.exists():
                info["status"] = "not_found"
                info["error"] = "No __init__.py or handler.py found"
                return info
            
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(target)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                info["handler"] = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                info["status"] = "loaded"
                print(f"✅ Folder loaded: {module_name}")
        
        # ═══ FILE MODULE ═══
        elif module_path.is_file() and module_path.suffix == '.py':
            info["type"] = "file"
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_name}", str(module_path)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"modules.{module_name}"] = mod
                spec.loader.exec_module(mod)
                
                # Pehle check karo — handler function hai?
                handler = getattr(mod, 'handler', getattr(mod, 'Handler', None))
                
                if handler:
                    # ✅ Handler mil gaya
                    info["handler"] = handler
                    info["status"] = "loaded"
                    print(f"✅ File loaded (handler found): {module_name}")
                else:
                    # ❌ Handler NAHI mila — AUTO WRAPPER banao!
                    info["handler"] = create_auto_handler(module_name, mod)
                    info["status"] = "loaded"
                    print(f"✅ File loaded (auto-wrapper): {module_name}")
        
        else:
            info["status"] = "not_found"
            info["error"] = "Module not found or not a valid Python file"
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
        print(f"❌ Fail: {module_name} — {e}")
    
    return info
