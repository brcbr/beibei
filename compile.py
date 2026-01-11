#!/usr/bin/env python3
"""
BUILD SCRIPT UPGRADED: FIXED PYARMOR RUNTIME & BINARY DEPENDENCIES
"""

import os
import sys
import shutil
import subprocess
import site
import platform

def fix_imports_in_xiebo():
    """Memastikan import platform ada di xiebo.py"""
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
    print("="*60)
    print("🚀 STARTING ROBUST BUILD PROCESS")
    print("="*60)
    
    python_exe = sys.executable
    site_pkgs = site.getsitepackages()
    
    # 1. Cleaning
    print("\n1️⃣ Cleaning old build files...")
    for d in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # 2. Fix Source
    if not fix_imports_in_xiebo(): return False

    # 3. Obfuscate dengan PyArmor
    print("\n2️⃣ Obfuscating code...")
    obfuscated_dir = 'obfuscated'
    os.makedirs(obfuscated_dir, exist_ok=True)
    
    obfuscated = False
    try:
        # Command PyArmor Gen
        # Kita menggunakan output ke folder 'obfuscated'
        cmd_pyarmor = [python_exe, '-m', 'pyarmor.cli', 'gen', '-O', obfuscated_dir, 'xiebo.py']
        result = subprocess.run(cmd_pyarmor, capture_output=True, text=True)
        
        if result.returncode == 0:
            obfuscated = True
            print("✅ PyArmor successful")
        else:
            print(f"⚠️ PyArmor Module failed: {result.stderr}")
            # Fallback global command
            result = subprocess.run(['pyarmor', 'gen', '-O', obfuscated_dir, 'xiebo.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                obfuscated = True
                print("✅ PyArmor successful (fallback)")
    except Exception as e:
        print(f"⚠️ PyArmor Exception: {e}")

    if not obfuscated:
        print("⚠️ PyArmor failed. Using original file (NOT SECURE).")
        shutil.copy('xiebo.py', os.path.join(obfuscated_dir, 'xiebo.py'))

    # 4. Compile dengan PyInstaller
    print("\n3️⃣ Compiling with PyInstaller...")
    
    # --- KRUSIAL: Mencari Folder Runtime PyArmor ---
    # PyArmor menghasilkan folder seperti 'pyarmor_runtime_000000'
    pyarmor_runtime_path = None
    pyarmor_runtime_name = None
    
    if obfuscated:
        for item in os.listdir(obfuscated_dir):
            if item.startswith('pyarmor_runtime'):
                pyarmor_runtime_name = item
                pyarmor_runtime_path = os.path.join(obfuscated_dir, item)
                print(f"ℹ️  PyArmor Runtime found: {pyarmor_runtime_name}")
                break
    
    # Separator untuk --add-data (Windows pakai ';', Unix pakai ':')
    path_sep = ';' if platform.system() == 'Windows' else ':'

    cmd = [
        python_exe, '-m', 'PyInstaller',
        '--onefile',
        '--clean',
        '--name=xiebo_protected',
        # Hapus --console jika ingin GUI application tanpa terminal
        '--console', 
    ]

    # --- KRUSIAL: Menambahkan Runtime PyArmor ke dalam EXE ---
    if pyarmor_runtime_path:
        # Format: source_path : dest_path
        add_data_arg = f"{pyarmor_runtime_path}{path_sep}{pyarmor_runtime_name}"
        cmd.extend(['--add-data', add_data_arg])
        # Tambahkan hidden import untuk runtime tersebut
        cmd.extend(['--hidden-import', pyarmor_runtime_name])

    # Hidden Imports
    hidden_imports = [
        'platform', 'pyodbc', 'hashlib', 'base64', 'ssl', 'json', 
        'logging', 'urllib', 'http.client', 'email'
    ]
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])

    # --- KRUSIAL: Gunakan collect-all untuk library kompleks ---
    # collect-submodules kadang tidak membawa file .dll/.so
    cmd.extend(['--collect-all', 'cryptography'])
    cmd.extend(['--collect-all', 'urllib'])
    
    # Path tambahan
    for sp in site_pkgs:
        cmd.extend(['--paths', sp])
        
    # Target file
    cmd.append(os.path.join(obfuscated_dir, 'xiebo.py'))
    
    print(f"Executing PyInstaller...")
    # Uncomment baris ini untuk melihat command lengkap jika debug
    # print(" ".join(cmd)) 

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ PyInstaller Error:\n{result.stderr}")
            # Tampilkan output stdout juga untuk hint lebih lanjut
            print(f"--- Stdout ---\n{result.stdout}")
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
        print(f"📂 Lokasi File: {os.path.abspath(dst_path)}")
        print("="*60)
        print("💡 TIPS: Jika program langsung menutup, jalankan via CMD/Terminal")
        print("         untuk melihat pesan error yang muncul.")
        return True
    else:
        print("❌ Error: Executable tidak ditemukan.")
        return False

if __name__ == "__main__":
    success = build_xiebo()
    sys.exit(0 if success else 1)
