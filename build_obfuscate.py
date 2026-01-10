# build_obfuscate.py
import os
import shutil
import subprocess
import sys
from datetime import datetime

def obfuscate_code():
    print("🔒 Starting code obfuscation...")
    
    # Backup original
    if not os.path.exists("backup"):
        os.makedirs("backup")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2("xiebo.py", f"backup/xiebo_original_{timestamp}.py")
    
    # Generate license file for binding
    with open("license.lic", "w") as f:
        f.write("# PyArmor License File\n")
        f.write(f"# Generated: {timestamp}\n")
        f.write("# This file is required for running obfuscated code\n")
    
    # PyArmor commands
    commands = [
        # First pass: obfuscate main code
        f"pyarmor gen --output dist/obfuscated --restrict 2 --advanced 2 "
        f"--mix-str 1 --obf-code 2 --obf-mod 1 --wrap-mode 1 xiebo.py",
        
        # Second pass: pack into executable
        f"pyarmor gen --output dist/packed --pack "
        f"--obf-code 3 --advanced 3 --restrict 3 --enable-import-hook 1 xiebo.py"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return False
    
    # Create loader script
    create_loader()
    
    print("✅ Obfuscation complete!")
    print("📁 Output in: dist/obfuscated/ and dist/packed/")
    
    return True

def create_loader():
    """Create a loader script that decrypts and runs the obfuscated code"""
    loader_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import ctypes
import hashlib

# Anti-debugging techniques
def anti_debug():
    try:
        # Check for debugger via ptrace
        if sys.platform == 'linux':
            try:
                with open('/proc/self/status', 'r') as f:
                    for line in f:
                        if line.startswith('TracerPid:'):
                            tracer_pid = int(line.split(':')[1].strip())
                            if tracer_pid != 0:
                                os._exit(1)
            except:
                pass
        
        # Check execution time (debugging slows execution)
        start_time = time.time()
        # Do some complex calculation
        for _ in range(1000):
            hashlib.sha256(b"anti-debug").hexdigest()
        elapsed = time.time() - start_time
        
        if elapsed > 0.1:  # If too slow, likely being debugged
            os._exit(1)
    except:
        pass

# Environment check
def check_environment():
    required_vars = ['PATH', 'HOME', 'USER']
    for var in required_vars:
        if var not in os.environ:
            os._exit(1)
    
    # Check if running in virtual environment
    suspicious_processes = ['gdb', 'strace', 'ltrace', 'radare2', 'idaq']
    try:
        if sys.platform == 'linux':
            with open('/proc/self/status', 'r') as f:
                content = f.read().lower()
                for proc in suspicious_processes:
                    if proc in content:
                        os._exit(1)
    except:
        pass

# Decryption stub (placeholder for actual encrypted code)
class CodeProtector:
    def __init__(self):
        self.key = self.generate_key()
    
    def generate_key(self):
        # Generate key based on system characteristics
        system_info = ""
        try:
            system_info += os.uname().sysname
            system_info += os.uname().nodename
            system_info += os.uname().release
        except:
            system_info = "default_system"
        
        return hashlib.sha256(system_info.encode()).digest()
    
    def decrypt_and_execute(self):
        # This would contain the actual decryption logic
        # For now, it imports the obfuscated module
        
        # First run anti-debug checks
        anti_debug()
        check_environment()
        
        # Import the actual obfuscated code
        try:
            from obfuscated.xiebo import main
            main()
        except ImportError:
            # Fallback to packed version
            try:
                import pytransform
                sys.path.insert(0, 'dist/packed')
                from xiebo import main
                main()
            except ImportError as e:
                print(f"❌ Failed to load protected module: {e}")
                sys.exit(1)

if __name__ == "__main__":
    protector = CodeProtector()
    protector.decrypt_and_execute()
'''
    
    with open("loader.py", "w") as f:
        f.write(loader_content)
    
    os.chmod("loader.py", 0o755)
    print("✅ Created loader.py")

if __name__ == "__main__":
    obfuscate_code()
