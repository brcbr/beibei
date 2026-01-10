#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import time
import math
import re
import threading
import platform
import urllib.request
import ssl
import warnings
from datetime import datetime, timedelta
import ctypes
import hashlib
import inspect

# =============================================
# ANTI-DEBUGGING AND ANTI-TAMPERING MECHANISMS
# =============================================

class SecurityCheck:
    @staticmethod
    def check_integrity():
        """Check if code has been modified"""
        current_hash = hashlib.sha256(
            open(__file__, 'rb').read()
        ).hexdigest()
        
        # Hardcoded hash of original file
        expected_hash = "a1b2c3d4e5f67890"  # This should be updated after final build
        
        if current_hash != expected_hash:
            sys.exit(0)
    
    @staticmethod
    def anti_debug():
        """Detect debugging attempts"""
        try:
            # Linux: check TracerPid
            if sys.platform == "linux":
                with open('/proc/self/status', 'r') as f:
                    for line in f:
                        if line.startswith('TracerPid:'):
                            tracer_pid = int(line.split(':')[1].strip())
                            if tracer_pid != 0:
                                os._exit(0)
            
            # Check for common debuggers in process list
            debuggers = ['gdb', 'lldb', 'strace', 'ltrace', 'radare2', 'idaq']
            try:
                import psutil
                for proc in psutil.process_iter(['name']):
                    if any(debugger in proc.info['name'].lower() for debugger in debuggers):
                        os._exit(0)
            except:
                pass
                
        except:
            pass
    
    @staticmethod
    def check_runtime():
        """Check runtime environment"""
        # Prevent running in virtual machines/containers
        vm_indicators = ['qemu', 'virtualbox', 'vmware', 'docker', 'lxc']
        try:
            if sys.platform == "linux":
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    if any(indicator in cpuinfo for indicator in vm_indicators):
                        time.sleep(10)  # Slow down in VM
                
                # Check /proc/self/exe symlink
                if os.path.islink('/proc/self/exe'):
                    real_path = os.readlink('/proc/self/exe')
                    if 'snap' in real_path or 'flatpak' in real_path:
                        os._exit(0)
        except:
            pass

# =============================================
# ENCRYPTED CONFIGURATION (DYNAMIC DECRYPTION)
# =============================================

class ConfigManager:
    def __init__(self):
        self.master_key = self._generate_key()
    
    def _generate_key(self):
        """Generate key based on system fingerprint"""
        system_data = ""
        try:
            system_data += platform.node()
            system_data += platform.processor()
            system_data += platform.system()
            system_data += str(os.getuid())
        except:
            system_data = "default_fingerprint"
        
        # Create deterministic but unique key
        key = hashlib.sha256(system_data.encode()).digest()
        return base64.urlsafe_b64encode(key[:32])
    
    def decrypt_value(self, encrypted_b64):
        """Decrypt configuration values at runtime"""
        try:
            from cryptography.fernet import Fernet
            cipher = Fernet(self.master_key)
            encrypted = base64.b64decode(encrypted_b64)
            return cipher.decrypt(encrypted).decode()
        except:
            # Fallback values if decryption fails
            return "ERROR_DECRYPT_FAILED"

# Encrypted constants (will be decrypted at runtime)
_ENCRYPTED_CONFIG = {
    'SERVER': 'gAAAAABm...',  # Encrypted values
    'DATABASE': 'gAAAAABm...',
    'USERNAME': 'gAAAAABm...',
    'PASSWORD': 'gAAAAABm...',
    'TABLE': 'gAAAAABm...',
    'SPECIAL_ADDR': 'gAAAAABm...'
}

# =============================================
# CODE FLATTENING AND CONTROL FLOW OBFUSCATION
# =============================================

def execute_with_obfuscation(func, *args):
    """Execute function with obfuscated control flow"""
    # Split execution into multiple steps
    steps = [
        lambda: SecurityCheck.anti_debug(),
        lambda: SecurityCheck.check_runtime(),
        lambda: func(*args)
    ]
    
    # Execute in random order (deterministic but confusing)
    import random
    random.seed(12345)  # Fixed seed for determinism
    order = [0, 1, 2]
    random.shuffle(order)
    
    for idx in order:
        if idx == 2:
            return steps[idx]()
        else:
            steps[idx]()

# =============================================
# MAIN LOGIC (REWRITTEN WITH OBFUSCATION)
# =============================================

def _01_init():
    """Initialization with anti-tampering"""
    SecurityCheck.check_integrity()
    warnings.filterwarnings("ignore")
    
    # Decrypt configuration
    config = ConfigManager()
    global SERVER, DATABASE, USERNAME, PASSWORD, TABLE, SPECIAL_ADDRESS_NO_OUTPUT
    SERVER = config.decrypt_value(_ENCRYPTED_CONFIG['SERVER'])
    DATABASE = config.decrypt_value(_ENCRYPTED_CONFIG['DATABASE'])
    USERNAME = config.decrypt_value(_ENCRYPTED_CONFIG['USERNAME'])
    PASSWORD = config.decrypt_value(_ENCRYPTED_CONFIG['PASSWORD'])
    TABLE = config.decrypt_value(_ENCRYPTED_CONFIG['TABLE'])
    SPECIAL_ADDRESS_NO_OUTPUT = config.decrypt_value(_ENCRYPTED_CONFIG['SPECIAL_ADDR'])

def _02_download():
    """Download xiebo binary with verification"""
    # ... (encrypted version of check_and_download_xiebo)
    pass

def _03_db_connect():
    """Database connection with obfuscation"""
    # ... (encrypted version of connect_db)
    pass

# =============================================
# BUILD SCRIPT FINAL
# =============================================

def build_final():
    """Script untuk build final executable"""
    build_script = '''
#!/bin/bash
echo "🔨 Building protected executable..."

# Step 1: Obfuscate Python code
pyarmor gen --output build/obf --restrict 3 --advanced 3 \
    --mix-str 1 --obf-code 3 --obf-mod 2 --wrap-mode 1 \
    --enable-import-hook 1 --runtime-path @lib \
    xiebo_protected.py

# Step 2: Create self-extracting archive
cat > xiebo_final.sh << 'EOF'
#!/bin/bash
# Self-extracting encrypted Python application
MD5_EXPECTED="$(cat MD5SUM)"
MD5_ACTUAL="$(md5sum "$0" | cut -d' ' -f1)"

if [ "$MD5_ACTUAL" != "$MD5_EXPECTED" ]; then
    echo "❌ Integrity check failed!"
    exit 1
fi

# Extract and execute
ARCHIVE=$(awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' "$0")
tail -n+$ARCHIVE "$0" | tar -xz
cd build/obf
exec python3 ./xiebo_protected.py "$@"

__ARCHIVE_BELOW__
EOF

# Step 3: Package
cd build/obf && tar -czf ../app.tar.gz .
cat ../app.tar.gz >> ../xiebo_final.sh
chmod +x ../xiebo_final.sh

# Step 4: Generate checksum
md5sum ../xiebo_final.sh > MD5SUM

echo "✅ Build complete: build/xiebo_final.sh"
'''
    
    with open('build.sh', 'w') as f:
        f.write(build_script)
    
    os.chmod('build.sh', 0o755)
    print("✅ Created build.sh")

if __name__ == "__main__":
    # Execute with obfuscated control flow
    execute_with_obfuscation(_01_init)
    
    # Rest of main logic...
    # [Kode utama di sini dengan semua fungsi yang sudah dienkripsi string-nya]
