
"""🦁 Mini-Program Sandbox — 5s, 128MB"""
import resource, signal
from contextlib import redirect_stdout, redirect_stderr
import io

class SandboxRunner:
    MAX_TIME = 5
    MAX_MEM = 128 * 1024 * 1024
    
    @classmethod
    def run(cls, code, app_id, user_id, api_instance=None):
        restricted = {
            '__builtins__': {name: __builtins__[name] for name in dir(__builtins__) 
                           if name not in ['open', 'exec', 'eval', 'compile', '__import__', 'input', 'exit', 'quit', 'os', 'sys', 'subprocess', 'socket']},
            'json': __import__('json'), 'datetime': __import__('datetime'),
            'math': __import__('math'), 'random': __import__('random'),
            'api': api_instance
        }
        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            resource.setrlimit(resource.RLIMIT_AS, (cls.MAX_MEM, cls.MAX_MEM))
            signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError))
            signal.alarm(cls.MAX_TIME)
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(code, restricted)
            signal.alarm(0)
            return {"status": "success", "output": stdout.getvalue()[:1024*1024], "stderr": stderr.getvalue()}
        except TimeoutError:
            return {"status": "error", "error": "Timeout (5s exceeded)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
EOF
