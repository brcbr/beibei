#!/usr/bin/env python3
"""
Build script with fixed imports for PyInstaller & Cryptography Fix
"""

import os
import sys
import shutil
import subprocess
import site
import cryptography
from datetime import datetime

def fix_imports_in_xiebo():
    """Fix imports in xiebo.py for PyInstaller"""
    print("🔧 Fixing imports for PyInstaller...")
    
    if not os.path.exists('xiebo.py'):
        print("❌ Error: xiebo.py not found!")
        return False

    with open('xiebo.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pastikan platform di-import di bagian atas
    lines = content.split('\n')
    has_platform = any('import platform' in line for line in lines[:20])
    
    if not has_platform:
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                lines.insert(i, 'import platform')
                break
        content = '\n'.join(lines)
    
    with open('xiebo.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Imports fixed")
    return True

def build_xiebo():
    """Build Xiebo executable"""
    print("="*60)
    print("🔧 BUILDING XIEBO EXECUTABLE")
    print("="*60)
    
    # Step 0: Fix imports
    if not fix_imports_in_xiebo():
        return False
    
    # Step 1: Clean
    print("\n1️⃣ Cleaning...")
    for d in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # Step 2: Obfuscate
    print("\n2️⃣ Obfuscating...")
    obfuscated = False
    try:
        # Menjalankan pyarmor menggunakan python yang sedang aktif
        result = subprocess.run([sys.executable, '-m', 'pyarmor.cli', 'gen', '-O', 'obfuscated', 'xiebo.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            obfuscated = True
            print("✅ PyArmor successful")
        else:
            # Coba perintah alternatif jika versi pyarmor berbeda
            result = subprocess.run(['pyarmor', 'gen', '-O', 'obfuscated', 'xiebo.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                obfuscated = True
                print("✅ PyArmor successful (legacy command)")
            else:
                print(f"⚠️ PyArmor failed, proceeding with original file")
    except Exception as e:
        print(f"⚠️ PyArmor not available: {e}")
    
    if not obfuscated:
        os.makedirs('obfuscated', exist_ok=True)
        shutil.copy('xiebo.py', 'obfuscated/xiebo.py')
        print("📁 Using original file (non-obfuscated)")
    
    # Step 3: Compile
    print("\n3️⃣ Compiling with Cryptography support...")
    
    # Dapatkan path site-packages secara dinamis
    site_pkgs = site.getsitepackages()
    
    hidden_imports = [
        'platform',
        'pyodbc',
        'cryptography',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'cryptography.hazmat.primitives.ciphers.aead',
        'hashlib',
        'base64',
        'ssl',
        'json',
        'logging'
    ]
    
    # Gunakan sys.executable -m PyInstaller untuk menjamin environment yang sama
    cmd = [sys.executable, '-m', 'PyInstaller', '--onefile', '--console', '--clean', '--name=xiebo_protected']
    
    # Tambahkan path pencarian module
    for sp in site_pkgs:
        cmd.extend(['--paths', sp])
        
    # Tambah hidden imports
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # Target file
    cmd.append('obfuscated/xiebo.py')
    
    print(f"Running: PyInstaller on {sys.executable}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed:\n{result.stderr}")
            return False
        
        print("✅ Compilation successful")
        
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        return False
    
    # Step 4: Verify and create output
    print("\n4️⃣ Creating output...")
    
    exec_name = 'xiebo_protected'
    if os.name == 'nt':
        exec_name += '.exe'
    
    src_path = os.path.join('dist', exec_name)
    
    if os.path.exists(src_path):
        os.makedirs('dist/protected', exist_ok=True)
        dst_path = os.path.join('dist/protected', exec_name)
        
        shutil.copy(src_path, dst_path)
        
        if os.name != 'nt':
            os.chmod(dst_path, 0o755)
        
        print(f"📦 Executable: {dst_path}")
        create_launcher(exec_name)
        
        print("\n" + "="*60)
        print("🎉 BUILD SUCCESSFUL!")
        print("="*60)
        return True
    else:
        print(f"❌ Executable not found at {src_path}")
        return False

def create_launcher(exec_name):
    """Create simple launcher script"""
    launcher = f'''#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exec_path = os.path.join(script_dir, "{exec_name}")
    
    if not os.path.exists(exec_path):
        print("Error: Executable not found at", exec_path)
        sys.exit(1)
    
    if os.name != "nt":
        try:
            os.chmod(exec_path, 0o755)
        except:
            pass
    
    # Run
    cmd = [exec_path] + sys.argv[1:]
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    launcher_path = 'dist/protected/run_xiebo.py'
    with open(launcher_path, 'w') as f:
        f.write(launcher)
    if os.name != 'nt':
        os.chmod(launcher_path, 0o755)
    print(f"📄 Launcher created: {launcher_path}")

if __name__ == "__main__":
    # Verifikasi awal cryptography sebelum mulai
    try:
        import cryptography
        print(f"✅ Cryptography detected in build script (v{cryptography.__version__})")
    except ImportError:
        print("❌ Error: Cryptography must be installed to run this build script.")
        print("Run: pip install cryptography")
        sys.exit(1)

    success = build_xiebo()
    sys.exit(0 if success else 1)
