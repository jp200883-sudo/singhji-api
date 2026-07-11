"""
🧪 Sandbox Environment — Safe code execution
"""
import ast
import sys
import resource
import signal
import multiprocessing
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional
from datetime import datetime

from .config import MiniProgramConfig
from .models import SandboxLog


class SandboxSecurity:
    """🔒 Security checks for code"""
    
    FORBIDDEN_KEYWORDS = [
        'import os', 'import sys', 'import subprocess', 
        'open(', '__import__', 'eval(', 'exec(',
        'compile(', 'input(', 'raw_input(',
        'file(', 'reload(', 'breakpoint(',
        'import socket', 'import urllib', 'import requests',
        'import ftplib', 'import smtplib', 'import telnetlib',
        'import webbrowser', 'import tkinter', 'import ctypes',
        'os.system', 'os.popen', 'os.spawn', 'os.exec',
        'subprocess.call', 'subprocess.Popen', 'subprocess.run',
        'shutil.rmtree', 'shutil.move', 'shutil.copy',
        'import sqlite3', 'import psycopg2', 'import pymongo',
        'import mysql', 'import sqlalchemy',
    ]
    
    FORBIDDEN_BUILTINS = [
        'open', 'exec', 'eval', 'compile', '__import__',
        'input', 'raw_input', 'reload', 'breakpoint',
        'exit', 'quit', 'help'
    ]
    
    @classmethod
    def check_code(cls, code: str) -> Dict[str, Any]:
        """Code scan karo — malicious hai kya?"""
        issues = []
        
        # Keyword check
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in code.lower():
                issues.append(f"🚫 Forbidden keyword found: {keyword}")
        
        # AST parse karo
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "safe": False,
                "issues": [f"Syntax Error: {str(e)}"]
            }
        
        # AST walk — dangerous nodes check karo
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in MiniProgramConfig.SANDBOX_ALLOWED_MODULES:
                        issues.append(f"🚫 Forbidden import: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module not in MiniProgramConfig.SANDBOX_ALLOWED_MODULES:
                    issues.append(f"🚫 Forbidden import from: {node.module}")
            
            elif isinstance(node, ast.Call):
                # Dangerous calls check karo
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.FORBIDDEN_BUILTINS:
                        issues.append(f"🚫 Forbidden builtin: {node.func.id}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues
        }


class ResourceLimiter:
    """⏱️ Resource limits set karo"""
    
    @staticmethod
    def set_limits():
        """CPU aur memory limit lagao"""
        # Memory limit
        memory_limit = MiniProgramConfig.SANDBOX_MEMORY_LIMIT * 1024 * 1024  # bytes
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # CPU time limit
        cpu_limit = MiniProgramConfig.SANDBOX_TIMEOUT
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit + 1))


class SandboxExecutor:
    """🧪 Safe Code Execution"""
    
    def __init__(self):
        self.security = SandboxSecurity()
    
    def execute(self, code: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Code safely execute karo
        Returns: execution result with output, errors, metrics
        """
        start_time = datetime.utcnow()
        
        # 🔒 Security check
        security_check = self.security.check_code(code)
        if not security_check["safe"]:
            return {
                "success": False,
                "error": "Security check failed!",
                "issues": security_check["issues"],
                "output": None,
                "execution_time": 0,
                "memory_used": 0
            }
        
        # 🧪 Execute in separate process
        manager = multiprocessing.Manager()
        result_dict = manager.dict()
        
        process = multiprocessing.Process(
            target=self._run_code,
            args=(code, input_data, result_dict)
        )
        
        process.start()
        process.join(timeout=MiniProgramConfig.SANDBOX_TIMEOUT)
        
        if process.is_alive():
            process.terminate()
            process.join()
            return {
                "success": False,
                "error": "⏱️ Execution timeout! Code 30 seconds se zyada chala.",
                "output": None,
                "execution_time": MiniProgramConfig.SANDBOX_TIMEOUT,
                "memory_used": 0
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = dict(result_dict)
        result["execution_time"] = round(execution_time, 3)
        
        return result
    
    def _run_code(self, code: str, input_data: Dict, result_dict):
        """Actual code run karo — child process mein"""
        try:
            # Resource limits lagao
            ResourceLimiter.set_limits()
            
            # Safe globals banayo
            safe_globals = {
                "__builtins__": {
                    name: getattr(__builtins__, name)
                    for name in dir(__builtins__)
                    if name not in SandboxSecurity.FORBIDDEN_BUILTINS
                }
            }
            
            # Allowed modules add karo
            for module_name in MiniProgramConfig.SANDBOX_ALLOWED_MODULES:
                try:
                    safe_globals[module_name] = __import__(module_name)
                except ImportError:
                    pass
            
            # Input data add karo
            if input_data:
                safe_globals["input_data"] = input_data
            
            # Output capture karo
            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, safe_globals)
            
            output = stdout_buffer.getvalue()
            error = stderr_buffer.getvalue()
            
            # Result extract karo (agar developer ne `result` variable set kiya)
            result_value = safe_globals.get("result", None)
            
            result_dict["success"] = True
            result_dict["output"] = output
            result_dict["result"] = result_value
            result_dict["error"] = error if error else None
            
        except Exception as e:
            result_dict["success"] = False
            result_dict["error"] = str(e)
            result_dict["output"] = None
            result_dict["result"] = None


# Global instance
sandbox = SandboxExecutor()
