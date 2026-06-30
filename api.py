# ─── Load Single Module (with Auto-Wrapper) ─────────────
def auto_wrap_handler(mod, module_name: str):
    """
    Agar module mein 'handler' ya 'Handler' nahi hai,
    to module ke andar koi bhi callable function dhoondh
    kar use auto-wrap kar dega.
    """
    # 1. Direct handler/Handler check
    handler = getattr(mod, 'handler', None) or getattr(mod, 'Handler', None)
    if handler:
        return handler

    # 2. Common alternate names try karo
    alt_names = ['process', 'run', 'main', 'execute', f'{module_name}_handler']
    for name in alt_names:
        fn = getattr(mod, name, None)
        if callable(fn):
            logger.info(f"🔧 Auto-wrapped '{name}' as handler for {module_name}")
            return fn

    # 3. Module mein defined koi bhi function dhoondo (built-in/imported chhodkar)
    candidates = [
        getattr(mod, attr) for attr in dir(mod)
        if callable(getattr(mod, attr, None))
        and not attr.startswith('_')
        and getattr(getattr(mod, attr), '__module__', '') == mod.__name__
    ]
    if candidates:
        fn = candidates[0]
        logger.info(f"🔧 Auto-wrapped first function '{fn.__name__}' for {module_name}")

        # Wrap so it always accepts req_data dict, even if original fn takes no args
        def wrapped(req_data, _fn=fn):
            import inspect
            sig = inspect.signature(_fn)
            if len(sig.parameters) == 0:
                return _fn()
            return _fn(req_data)
        return wrapped

    # 4. Kuch nahi mila — safe fallback handler
    logger.warning(f"⚠️ No callable found in {module_name}, using stub handler")
    def stub_handler(req_data):
        return {"status": "stub", "message": f"{module_name} mein koi handler function nahi mila"}
    return stub_handler


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
                info["handler"] = auto_wrap_handler(mod, module_name)
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
                info["handler"] = auto_wrap_handler(mod, module_name)
                info["status"] = "loaded"
                logger.info(f"✅ File loaded: {module_name}")

        else:
            info["status"] = "not_found"

    except Exception as e:
        # YEH SABSE IMPORTANT FIX HAI:
        # Pehle agar exec_module mein koi error aata tha (jaise missing import,
        # syntax error, ya dependency na milna) to poora module hi skip ho jata tha.
        # Ab hum exact error log karenge taaki pata chale 29 modules kyun fail ho rahe.
        info["status"] = "error"
        info["error"] = str(e)
        logger.error(f"❌ FAIL: {module_name} — {type(e).__name__}: {e}")

    return info
