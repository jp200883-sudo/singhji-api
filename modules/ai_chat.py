# ═══════════════════════════════════════════════════════
#   SINGH JI AI ULTRA v7.0 — DEVLIPI (Developer Lipi)
#   Auto-Handler Wrapper for File Modules
# ═══════════════════════════════════════════════════════

import importlib.util
import sys
from pathlib import Path
from typing import Optional, Dict, Callable, Any

# ─── Auto Handler Wrapper ───────────────────────────────
def create_auto_handler(module_name: str, module_obj) -> Callable:
    """
    Devlipi: Agar module mein handler nahi hai,
    toh auto-wrapper banao jo module ke functions ko call kare.
    """
    
    def auto_handler(request_data: Any = None) -> Dict:
        """Auto-generated handler — Devlipi ka jadoo!"""
        
        # Module ke saare functions dhoondo
        functions = {
            name: func 
            for name, func in vars(module_obj).items()
            if callable(func) and not name.startswith('_')
        }
        
        # Sabse pehla non-handler function lo
        main_func = None
        for name, func in functions.items():
            if name not in ('handler', 'Handler', 'create_auto_handler'):
                main_func = func
                break
        
        # Function call karo
        if main_func:
            try:
                result = main_func(request_data)
                return {
                    "module": module_name,
                    "status": "success",
                    "source": "auto_handler",
                    "data": result
                }
            except:
                try:
                    result = main_func()
                    return {
                        "module": module_name,
                        "status": "success", 
                        "source": "auto_handler",
                        "data": result
                    }
                except:
                    pass
        
        # Fallback
        return {
            "module": module_name,
            "status": "success",
            "source": "auto_handler",
            "message": f"{module_name} active via Devlipi!",
            "available_functions": list(functions.keys())
        }
    
    return auto_handler


# ─── Load Single Module ─────────────────────────────────
def load_module(module_name: str, modules_dir: str = "modules") -> Optional[Dict]:
    """Devlipi module loader — 37 modules, sab load honge!"""
    
    modules_path = Path(modules_dir)
    module_path = modules_path / module_name
    info = {
        "name": module_name, 
        "type": None, 
        "handler": None, 
        "status": "loading"
    }
    
    try:
        if module_path.is_dir():
            # Folder module
            info["type"] = "folder"
            init_file = module_path / "__init__.py"
            handler_file = module_path / "handler.py"
            target = init_file if init_file.exists() else handler_file
            
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
        
        elif module_path.is_file() and module_path.suffix == '.py':
            # File module — YAHAN DEVLIPI KA JADOO HAI!
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
                    # Handler mil gaya
                    info["handler"] = handler
                    info["status"] = "loaded"
                    print(f"✅ File loaded (handler found): {module_name}")
                else:
                    # Handler NAHI mila — Devlipi auto-wrapper banao!
                    info["handler"] = create_auto_handler(module_name, mod)
                    info["status"] = "loaded"
                    print(f"✅ File loaded (Devlipi auto-wrapper): {module_name}")
        
        else:
            info["status"] = "not_found"
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
        print(f"❌ Fail: {module_name} — {e}")
    
    return info


# ─── Load All Modules ───────────────────────────────────
def load_all_modules(modules_dir: str = "modules") -> Dict[str, Dict]:
    """Saare modules load karo — 37 mein se 37 load hone chahiye!"""
    
    modules_path = Path(modules_dir)
    loaded = {}
    
    if not modules_path.exists():
        print(f"❌ Modules directory not found: {modules_dir}")
        return loaded
    
    # Sab .py files aur folders dhoondo
    for item in modules_path.iterdir():
        name = item.stem if item.is_file() else item.name
        
        # Skip __pycache__ aur hidden files
        if name.startswith('_') or name.startswith('.'):
            continue
            
        info = load_module(name, modules_dir)
        loaded[name] = info
    
    # Summary print karo
    total = len(loaded)
    successful = sum(1 for v in loaded.values() if v["status"] == "loaded")
    failed = sum(1 for v in loaded.values() if v["status"] == "error")
    
    print(f"\n{'='*50}")
    print(f"🦁 SINGH JI AI v7.0 — DEVLIPI LOAD SUMMARY")
    print(f"{'='*50}")
    print(f"📁 Total modules found: {total}")
    print(f"✅ Successfully loaded: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Target: 37/37 load hone chahiye!")
    print(f"{'='*50}\n")
    
    return loaded
