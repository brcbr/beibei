#!/usr/bin/env python3
"""
BUILD SCRIPT: FIXED FOR CRYPTOGRAPHY & URLLIB
"""

import os
import sys
import shutil
import subprocess
import site
from datetime import datetime

def fix_imports_in_xiebo():
    """Memastikan import platform ada di xiebo.py untuk mencegah error PyInstaller"""
    print("🔧 Fixing imports in xiebo.py...")
    if not os.path.exists('xiebo.py'):
        print("❌ Error: xiebo.py tidak ditemukan!")
        return False

    with open('xiebo.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    has_platform = any('import platform' in line for line in lines[:25])
    
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
    """Proses Build Utama"""
    print("="*60)
    print("🚀 STARTING BUILD PROCESS")
    print("="*60)
    
    # 0. Persiapan Path
    python_exe = sys.executable
    site_pkgs = site.getsitepackages()
    
    # 1. Fix Imports
    if not fix_imports_in_xiebo():
        return False
    
    # 2. Cleaning
    print("\n1️⃣ Cleaning old build files...")
    for d in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # 3. Obfuscate dengan PyArmor
    print("\n2️⃣ Obfuscating code...")
    obfuscated = False
    try:
        # Mencoba menjalankan pyarmor sebagai modul
        result = subprocess.run([python_exe, '-m', 'pyarmor.cli', 'gen', '-O', 'obfuscated', 'xiebo.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            obfuscated = True
            print("✅ PyArmor successful")
        else:
            # Fallback ke command langsung
            result = subprocess.run(['pyarmor', 'gen', '-O', 'obfuscated', 'xiebo.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                obfuscated = True
                print("✅ PyArmor successful (fallback)")
    except:
        pass

    if not obfuscated:
        print("⚠️ PyArmor failed/not found. Using original file.")
        os.makedirs('obfuscated', exist_ok=True)
        shutil.copy('xiebo.py', 'obfuscated/xiebo.py')

    # 4. Compile dengan PyInstaller
    print("\n3️⃣ Compiling with PyInstaller...")
    
    # Daftar hidden imports yang sangat spesifik untuk mengatasi ModuleNotFoundError
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
        'logging',
        'urllib',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'http.client',
        'email.message' # Kadang dibutuhkan oleh urllib
    ]
    
    cmd = [
        python_exe, '-m', 'PyInstaller',
        '--onefile',
        '--console',
        '--clean',
        '--name=xiebo_protected'
    ]
    
    # Menambahkan paths agar PyInstaller menemukan library yang terinstall
    for sp in site_pkgs:
        cmd.extend(['--paths', sp])
        
    # Menambahkan hidden imports
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])

    # Memaksa pengambilan seluruh sub-modul penting
    cmd.extend(['--collect-submodules', 'urllib'])
    cmd.extend(['--collect-submodules', 'cryptography'])
    
    # Target file yang sudah di-obfuscate
    cmd.append('obfuscated/xiebo.py')
    
    print(f"Executing: {' '.join(cmd[:10])}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ PyInstaller Error:\n{result.stderr}")
            return False
        print("✅ Compilation successful")
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return False

    # 5. Finalisasi
    print("\n4️⃣ Finalizing output...")
    exec_name = 'xiebo_protected' + ('.exe' if os.name == 'nt' else '')
    src_path = os.path.join('dist', exec_name)
    
    if os.path.exists(src_path):
        out_dir = 'dist/protected'
        os.makedirs(out_dir, exist_ok=True)
        dst_path = os.path.join(out_dir, exec_name)
        shutil.copy(src_path, dst_path)
        
        if os.name != 'nt':
            os.chmod(dst_path, 0o755)
            
        print(f"\n" + "="*60)
        print(f"🎉 SUCCESS!")
        print(f"📂 Lokasi File: {dst_path}")
        print("="*60)
        return True
    else:
        print("❌ Error: Executable tidak ditemukan di folder dist.")
        return False

if __name__ == "__main__":
    # Cek apakah modul utama tersedia sebelum build
    try:
        import cryptography
        import urllib.request
    except ImportError as e:
        print(f"❌ Error: Library {e.name} belum terinstall di Python ini.")
        print(f"Silakan jalankan: {sys.executable} -m pip install cryptography")
        sys.exit(1)

    success = build_xiebo()
    sys.exit(0 if success else 1)
