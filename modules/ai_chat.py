# ─── Load Single Module ─────────────────────────────────
def load_module(module_name: str, modules_dir: str = "modules") -> Optional[Dict]:
    modules_path = Path(modules_dir)
    module_path = modules_path / module_name
    info = {"name": module_name, "type": None, "handler": None, "status": "loading"}
    
    try:
        if module_path.is_dir():
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
                logger.info(f"✅ Folder loaded: {module_name}")
        
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
                    # Handler mil gaya — use karo
                    info["handler"] = handler
                    info["status"] = "loaded"
                    logger.info(f"✅ File loaded (handler found): {module_name}")
                else:
                    # Handler NAHI mila — auto wrapper banao
                    info["handler"] = create_auto_handler(module_name, mod)
                    info["status"] = "loaded"
                    logger.info(f"✅ File loaded (auto wrapper): {module_name}")
        
        else:
            info["status"] = "not_found"
            
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
        logger.error(f"❌ Fail: {module_name} — {e}")
    
    return info


# ─── Auto Handler Wrapper ────────────────────────────────
def create_auto_handler(module_name: str, module_obj):
    """
    Agar module mein handler function nahi hai,
    toh auto wrapper banao jo module ke functions ko call kare.
    """
    
    def auto_handler(request_data):
        """Auto-generated handler for module"""
        
        # Module ke saare functions dhoondo
        functions = {
            name: func for name, func in vars(module_obj).items()
            if callable(func) and not name.startswith('_')
        }
        
        # Sabse pehla function lo (jo handler nahi hai)
        main_func = None
        for name, func in functions.items():
            if name not in ('handler', 'Handler', 'create_auto_handler'):
                main_func = func
                break
        
        # Agar function mila, toh call karo
        if main_func:
            try:
                # Try with request_data
                result = main_func(request_data)
                return {
                    "module": module_name,
                    "status": "success",
                    "data": result
                }
            except:
                try:
                    # Try without args
                    result = main_func()
                    return {
                        "module": module_name,
                        "status": "success",
                        "data": result
                    }
                except:
                    pass
        
        # Fallback — simple response
        return {
            "module": module_name,
            "status": "success",
            "message": f"{module_name} module active!",
            "available_functions": list(functions.keys())
        }
    
    return auto_handler
    
