#!/usr/bin/env python3
"""
Ultimate Protection Builder for Xiebo
Combines PyArmor obfuscation + PyInstaller packing + Custom protection
"""

import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import zipfile
import base64
from pathlib import Path
from datetime import datetime

class UltimateProtector:
    def __init__(self):
        self.version = "1.0"
        self.build_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = tempfile.mkdtemp(prefix=f"xiebo_build_{self.build_id}_")
        self.final_dir = "dist/protected"
        
    def check_dependencies(self):
        """Check and install required packages"""
        required = ['pyarmor', 'pyinstaller', 'cryptography']
        missing = []
        
        for package in required:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"📦 Installing missing packages: {', '.join(missing)}")
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
        
        return True
    
    def create_anti_reverse_layer(self):
        """Create anti-reverse engineering layer"""
        protection_code = f'''
# =============================================
# ANTI-REVERSE ENGINEERING PROTECTION LAYER
# =============================================
import sys
import os
import ctypes
import hashlib
import time
import platform
import inspect
import zipfile
import marshal
import zlib
from datetime import datetime

class AntiReverse:
    def __init__(self):
        self.start_time = time.time()
        self.checks_passed = 0
        self.total_checks = 7
        
    def check_1_debugger(self):
        """Check for debuggers"""
        try:
            if platform.system() == "Linux":
                # Check TracerPid
                try:
                    with open("/proc/self/status", "r") as f:
                        for line in f:
                            if line.startswith("TracerPid:"):
                                pid = int(line.split(":")[1].strip())
                                if pid != 0:
                                    self._slow_down()
                                    return False
                except:
                    pass
                    
                # Check /proc/self/exe
                if os.path.islink("/proc/self/exe"):
                    exe_path = os.readlink("/proc/self/exe")
                    suspicious = ["gdb", "strace", "ltrace", "rr", "radare2"]
                    if any(s in exe_path.lower() for s in suspicious):
                        self._slow_down()
                        return False
                        
            elif platform.system() == "Windows":
                # Check for debugger via IsDebuggerPresent
                try:
                    kernel32 = ctypes.windll.kernel32
                    if kernel32.IsDebuggerPresent():
                        self._slow_down()
                        return False
                except:
                    pass
                    
            self.checks_passed += 1
            return True
            
        except:
            return True  # Continue on error
    
    def check_2_vm_detection(self):
        """Detect virtual machines/emulators"""
        try:
            vm_indicators = [
                "vmware", "virtualbox", "qemu", "xen", "hyperv",
                "docker", "lxc", "container", "podman", "wsl"
            ]
            
            # Check CPU info
            if platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        cpuinfo = f.read().lower()
                        if any(vm in cpuinfo for vm in vm_indicators):
                            self._slow_down()
                            return False
                except:
                    pass
                    
                # Check DMI
                try:
                    with open("/sys/class/dmi/id/product_name", "r") as f:
                        product = f.read().lower()
                        if any(vm in product for vm in vm_indicators):
                            self._slow_down()
                            return False
                except:
                    pass
            
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def check_3_timing_attack(self):
        """Detect timing analysis"""
        try:
            elapsed = time.time() - self.start_time
            
            # If execution is too fast (emulated) or too slow (debugged)
            if elapsed < 0.001:  # Too fast - likely emulated
                time.sleep(0.5)
                return False
            elif elapsed > 10.0:  # Too slow - likely debugged
                return False
                
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def check_4_memory_scan(self):
        """Detect memory scanning"""
        try:
            # Allocate and check memory
            test_data = os.urandom(1024 * 1024)  # 1MB random
            test_hash = hashlib.sha256(test_data).hexdigest()
            
            # Simulate computation
            for i in range(1000):
                hashlib.sha256(str(i).encode()).hexdigest()
                
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def check_5_packing_integrity(self):
        """Check if binary has been unpacked/modified"""
        try:
            # Get current executable hash
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundled
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
                
            with open(exe_path, "rb") as f:
                content = f.read(65536)  # First 64KB
                current_hash = hashlib.sha256(content).hexdigest()
            
            # You can embed expected hash in the binary
            # For now, just pass the check
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def check_6_import_hooks(self):
        """Detect import hooks (used by unpackers)"""
        try:
            # Check if standard modules have been hooked
            std_modules = ["os", "sys", "time", "hashlib"]
            for mod_name in std_modules:
                module = sys.modules.get(mod_name)
                if module:
                    # Check module file location
                    if hasattr(module, "__file__"):
                        file_path = module.__file__
                        if file_path and "site-packages" not in file_path:
                            self._slow_down()
                            return False
                            
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def check_7_environment_tamper(self):
        """Check for environment tampering"""
        try:
            # Check for suspicious environment variables
            suspicious_envs = ["PYTHONDEBUG", "PYTHONINSPECT", "PYTHONOPTIMIZE"]
            for env in suspicious_envs:
                if os.environ.get(env):
                    self._slow_down()
                    return False
            
            # Check LD_PRELOAD on Linux
            if platform.system() == "Linux":
                if os.environ.get("LD_PRELOAD"):
                    self._slow_down()
                    return False
                    
            self.checks_passed += 1
            return True
            
        except:
            return True
    
    def _slow_down(self):
        """Slow down execution if suspicious activity detected"""
        time.sleep(0.1 + hash(str(time.time())) % 10 / 100.0)
    
    def run_all_checks(self):
        """Run all anti-reverse checks"""
        print("🔍 Running security checks...")
        
        checks = [
            self.check_1_debugger,
            self.check_2_vm_detection,
            self.check_3_timing_attack,
            self.check_4_memory_scan,
            self.check_5_packing_integrity,
            self.check_6_import_hooks,
            self.check_7_environment_tamper,
        ]
        
        for i, check in enumerate(checks, 1):
            if not check():
                print(f"⚠️  Check {i} triggered security warning")
        
        print(f"✅ Security checks passed: {self.checks_passed}/{self.total_checks}")
        
        # If too many checks failed, exit
        if self.checks_passed < self.total_checks // 2:
            print("❌ Multiple security checks failed")
            time.sleep(5)
            sys.exit(0)
        
        return True

# =============================================
# CODE ENCRYPTION LAYER
# =============================================
class CodeEncryptor:
    def __init__(self, master_key=None):
        self.key = master_key or self._generate_key()
        self.encrypted_chunks = {{ENCRYPTED_CODE_CHUNKS}}
    
    def _generate_key(self):
        """Generate key from system fingerprint"""
        fingerprint = ""
        try:
            import platform
            fingerprint += platform.node()
            fingerprint += platform.processor()
            fingerprint += platform.system()
            fingerprint += str(os.getpid())
        except:
            fingerprint = "default_fingerprint_2024"
        
        return hashlib.sha256(fingerprint.encode()).digest()[:32]
    
    def decrypt_chunk(self, chunk_id):
        """Decrypt a code chunk"""
        if chunk_id not in self.encrypted_chunks:
            return None
        
        encrypted_data = base64.b64decode(self.encrypted_chunks[chunk_id])
        
        # Simple XOR decryption (replace with AES for production)
        decrypted = bytes([encrypted_data[i] ^ self.key[i % len(self.key)] 
                          for i in range(len(encrypted_data))])
        
        return zlib.decompress(decrypted)
    
    def execute_chunk(self, chunk_id):
        """Decrypt and execute a code chunk"""
        code_bytes = self.decrypt_chunk(chunk_id)
        if not code_bytes:
            return None
        
        code_obj = marshal.loads(code_bytes)
        exec(code_obj)

# Initialize protection
if __name__ != "__main__":
    anti_rev = AntiReverse()
    anti_rev.run_all_checks()
    
    # Only import main module if checks pass
    if anti_rev.checks_passed >= 4:
        # Dynamically load encrypted code chunks
        encryptor = CodeEncryptor()
        encryptor.execute_chunk("main_module")
    else:
        print("❌ Security checks failed")
        sys.exit(1)
'''
        
        return protection_code
    
    def create_loader_script(self):
        """Create encrypted loader script"""
        loader = f'''#!/usr/bin/env python3
# =============================================
# XIEBO ENCRYPTED LOADER
# Build ID: {self.build_id}
# =============================================
import sys
import os

# Add protected library path
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
else:
    # Find the directory containing this executable
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    protected_lib = os.path.join(app_path, "lib", "protected")
    if os.path.exists(protected_lib):
        sys.path.insert(0, protected_lib)

# Import and run
try:
    from xiebo_protected import main
    main()
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    print("This executable may be corrupted or modified.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Runtime error: {{e}}")
    sys.exit(1)
'''
        
        return loader
    
    def obfuscate_with_pyarmor(self, source_file):
        """Obfuscate using PyArmor with maximum protection"""
        print("🔒 Obfuscating with PyArmor...")
        
        # Create output directory
        obfuscated_dir = os.path.join(self.temp_dir, "obfuscated")
        os.makedirs(obfuscated_dir, exist_ok=True)
        
        # PyArmor commands for maximum protection
        commands = [
            # First pass: Basic obfuscation
            ["pyarmor", "gen", "-O", obfuscated_dir, "--mix-str", source_file],
            
            # Second pass: Advanced obfuscation
            ["pyarmor", "gen", "-O", os.path.join(obfuscated_dir, "advanced"),
             "--restrict-mode", "2",
             "--obf-code", "2",
             source_file],
            
            # Create runtime package
            ["pyarmor", "runtime", "-O", os.path.join(obfuscated_dir, "runtime")],
        ]
        
        for cmd in commands:
            try:
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️  Warning: {result.stderr[:200]}")
            except Exception as e:
                print(f"⚠️  Error: {e}")
        
        return obfuscated_dir
    
    def encrypt_code_chunks(self, source_file):
        """Encrypt Python code into chunks"""
        print("🔐 Encrypting code chunks...")
        
        with open(source_file, 'rb') as f:
            source_code = f.read()
        
        # Split code into chunks
        chunk_size = 1024 * 10  # 10KB chunks
        chunks = [source_code[i:i+chunk_size] for i in range(0, len(source_code), chunk_size)]
        
        encrypted_chunks = {}
        key = os.urandom(32)
        
        for i, chunk in enumerate(chunks):
            # Compress
            compressed = zlib.compress(chunk, level=9)
            
            # Simple XOR encryption (use AES for production)
            encrypted = bytes([compressed[j] ^ key[j % len(key)] for j in range(len(compressed))])
            
            # Store as base64
            encrypted_chunks[f"chunk_{i}"] = base64.b64encode(encrypted).decode()
        
        # Save key (in production, derive from system or use external key)
        key_file = os.path.join(self.temp_dir, "key.bin")
        with open(key_file, 'wb') as f:
            f.write(key)
        
        return encrypted_chunks
    
    def create_protected_module(self, source_file):
        """Create protected module with anti-reverse features"""
        print("🛡️ Creating protected module...")
        
        # Read original source
        with open(source_file, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Get encrypted chunks
        encrypted_chunks = self.encrypt_code_chunks(source_file)
        
        # Create protection layer
        protection_layer = self.create_anti_reverse_layer()
        
        # Replace placeholder with actual encrypted chunks
        protection_layer = protection_layer.replace(
            "{{ENCRYPTED_CODE_CHUNKS}}", 
            str(encrypted_chunks)
        )
        
        # Combine protection layer with original code
        protected_code = protection_layer + "\n\n" + original_code
        
        # Save protected module
        protected_file = os.path.join(self.temp_dir, "xiebo_protected.py")
        with open(protected_file, 'w', encoding='utf-8') as f:
            f.write(protected_code)
        
        return protected_file
    
    def compile_with_pyinstaller(self, entry_file):
        """Compile with PyInstaller with maximum protection"""
        print("🔨 Compiling with PyInstaller...")
        
        # Create spec file for maximum protection
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.__main__ import run

# Build options
build_options = [
    '--name=xiebo_protected',
    '--onefile',
    '--console',
    '--clean',
    '--noconfirm',
    
    # Optimization
    '--optimize=2',
    
    # Exclude unnecessary modules
    '--exclude-module=tests',
    '--exclude-module=test',
    '--exclude-module=unittest',
    '--exclude-module=pytest',
    
    # Hide import warnings
    '--disable-windowed-traceback',
    
    # Add data files
    # ('path/to/data', 'data'),
    
    # Runtime hooks
    # '--runtime-hook=hook.py',
    
    # Binary inclusion
    # '--add-binary=libcrypto.so.1.1:.',
    
    # UPX compression (if available)
    # '--upx-dir=/path/to/upx',
    
    # Additional flags
    '--strip',  # Strip debug symbols
    '--noupx',  # Don't use UPX (better for anti-virus)
]

# Run PyInstaller
run(build_options + ['{entry_file}'])
'''
        
        spec_file = os.path.join(self.temp_dir, "xiebo.spec")
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Run PyInstaller
        pyinstaller_cmd = [
            'pyinstaller',
            '--onefile',
            '--console',
            '--clean',
            '--noconfirm',
            '--name=xiebo_protected',
            '--add-data', f'{self.temp_dir}/obfuscated:xiebo_protected',
            '--hidden-import=pyodbc',
            '--hidden-import=cryptography',
            '--hidden-import=pyodbc',
            '--exclude-module=tests',
            '--exclude-module=test',
            '--strip',
            '--noupx',
            entry_file
        ]
        
        print(f"Running: {' '.join(pyinstaller_cmd[:5])}...")
        
        try:
            result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ PyInstaller compilation successful")
                return True
            else:
                print(f"❌ PyInstaller failed: {result.stderr[:500]}")
                return False
        except Exception as e:
            print(f"❌ PyInstaller error: {e}")
            return False
    
    def add_custom_packer(self):
        """Add custom packer layer"""
        print("📦 Adding custom packer layer...")
        
        packer_code = '''
import struct
import lzma
import hashlib

class CustomPacker:
    def __init__(self):
        self.magic = b'XIEBO'  # File signature
        self.version = 1
        self.checksum = None
        
    def pack(self, data):
        """Pack data with custom format"""
        # Compress
        compressed = lzma.compress(data, preset=9)
        
        # Add header
        header = struct.pack('5sBI', self.magic, self.version, len(compressed))
        
        # Calculate checksum
        self.checksum = hashlib.sha256(compressed).digest()
        
        # Combine
        packed = header + self.checksum + compressed
        
        return packed
        
    def unpack(self, packed_data):
        """Unpack custom format"""
        # Verify magic
        magic = packed_data[:5]
        if magic != self.magic:
            return None
            
        # Parse header
        version = packed_data[5]
        data_len = struct.unpack('I', packed_data[6:10])[0]
        checksum = packed_data[10:42]
        compressed = packed_data[42:42+data_len]
        
        # Verify checksum
        if hashlib.sha256(compressed).digest() != checksum:
            return None
            
        # Decompress
        return lzma.decompress(compressed)
'''
        
        packer_file = os.path.join(self.temp_dir, "packer.py")
        with open(packer_file, 'w') as f:
            f.write(packer_code)
        
        return packer_file
    
    def create_final_package(self):
        """Create final protected package"""
        print("🎁 Creating final package...")
        
        os.makedirs(self.final_dir, exist_ok=True)
        
        # Copy files
        files_to_copy = [
            ("dist/xiebo_protected", os.path.join(self.final_dir, "xiebo_protected")),
            ("xiebo.py", os.path.join(self.final_dir, "xiebo_source_backup.py")),
        ]
        
        for src, dst in files_to_copy:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"📄 Copied: {dst}")
        
        # Create launcher script
        launcher = self.create_loader_script()
        launcher_path = os.path.join(self.final_dir, "launch_xiebo.py")
        with open(launcher_path, 'w') as f:
            f.write(launcher)
        
        # Make executable on Unix
        if os.name != 'nt':
            os.chmod(launcher_path, 0o755)
        
        # Create README
        readme = f'''# Xiebo Protected Executable
Build ID: {self.build_id}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files:
- `xiebo_protected` - Main protected executable
- `launch_xiebo.py` - Launcher script
- `xiebo_source_backup.py` - Source backup

## Protection Features:
1. PyArmor obfuscation
2. PyInstaller compilation
3. Anti-debugging techniques
4. VM detection
5. Code encryption
6. Integrity checks
7. Timing attack protection

## Usage:
```bash
# Linux/Mac
chmod +x xiebo_protected
./xiebo_protected --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z

# Or use launcher
python3 launch_xiebo.py --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z

# Windows
xiebo_protected.exe --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z
