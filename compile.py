#!/usr/bin/env python3
"""
Build script with fixed imports for PyInstaller
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def fix_imports_in_xiebo():
    """Fix imports in xiebo.py for PyInstaller"""
    print("🔧 Fixing imports for PyInstaller...")
    
    with open('xiebo.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pastikan platform di-import di bagian atas
    if 'import platform' not in content.split('\n', 20):
        # Cari baris import pertama
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                lines.insert(i, 'import platform')
                break
        
        content = '\n'.join(lines)
    
    # Tulis kembali
    with open('xiebo.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Imports fixed")

def build_xiebo():
    """Build Xiebo executable"""
    print("="*60)
    print("🔧 BUILDING XIEBO EXECUTABLE")
    print("="*60)
    
    # Step 0: Fix imports
    fix_imports_in_xiebo()
    
    # Step 1: Clean
    print("\n1️⃣ Cleaning...")
    for d in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # Step 2: Obfuscate
    print("\n2️⃣ Obfuscating...")
    obfuscated = False
    try:
        result = subprocess.run(['pyarmor', 'gen', '-O', 'obfuscated', 'xiebo.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            obfuscated = True
            print("✅ PyArmor successful")
        else:
            print(f"⚠️ PyArmor failed: {result.stderr[:100]}")
    except:
        print("⚠️ PyArmor not available")
    
    if not obfuscated:
        os.makedirs('obfuscated', exist_ok=True)
        shutil.copy('xiebo.py', 'obfuscated/xiebo.py')
        print("📁 Using original file")
    
    # Step 3: Compile with ALL necessary hidden imports
    print("\n3️⃣ Compiling...")
    
    # List semua module yang mungkin digunakan
    hidden_imports = [
        'platform',          # ← PASTIKAN INI ADA
        'pyodbc',
        'cryptography',
        'hashlib',
        'base64',
        'ssl',
        'datetime',
        'threading',
        'subprocess',
        're',
        'math',
        'warnings',
        'urllib.request',
        'urllib.error',
        'urllib.parse',
        'os',
        'sys',
        'time',
        'json',
        'logging',
    ]
    
    cmd = ['pyinstaller', '--onefile', '--console', '--clean', '--name=xiebo_protected']
    
    # Tambah semua hidden imports
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # Tambah file
    cmd.append('obfuscated/xiebo.py')
    
    print(f"Command: {' '.join(cmd[:8])}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr[:300]}")
            return False
        
        print("✅ Compilation successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 4: Verify and create output
    print("\n4️⃣ Creating output...")
    
    exec_name = 'xiebo_protected'
    if os.name == 'nt':
        exec_name += '.exe'
    
    src_path = f'dist/{exec_name}'
    
    if not os.path.exists(src_path):
        # Cari file executable
        for root, dirs, files in os.walk('dist'):
            for file in files:
                if 'xiebo' in file.lower():
                    src_path = os.path.join(root, file)
                    exec_name = file
                    break
    
    if os.path.exists(src_path):
        # Create protected directory
        os.makedirs('dist/protected', exist_ok=True)
        dst_path = f'dist/protected/{exec_name}'
        
        shutil.copy(src_path, dst_path)
        
        if os.name != 'nt':
            os.chmod(dst_path, 0o755)
        
        print(f"📦 Executable: {dst_path}")
        
        # Create launcher
        create_launcher(exec_name)
        
        # Success
        print("\n" + "="*60)
        print("🎉 BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\n📁 Output: dist/protected/")
        print(f"🚀 Run: ./dist/protected/{exec_name} --help")
        print("="*60)
        
        return True
    else:
        print(f"❌ Executable not found: {exec_name}")
        print("Files in dist/:")
        if os.path.exists('dist'):
            for root, dirs, files in os.walk('dist'):
                for file in files:
                    print(f"  {os.path.join(root, file)}")
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
    
    # Make executable on Unix
    if os.name != "nt":
        try:
            os.chmod(exec_path, 0o755)
        except:
            pass
    
    # Check environment variable
    if not os.environ.get("XIEBO_ENCRYPTION_KEY"):
        print("Warning: XIEBO_ENCRYPTION_KEY not set")
        print("Set with: export XIEBO_ENCRYPTION_KEY='your_key'")
    
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
    
    print(f"📄 Launcher: {launcher_path}")

if __name__ == "__main__":
    if not os.path.exists('xiebo.py'):
        print("❌ xiebo.py not found")
        sys.exit(1)
    
    success = build_xiebo()
    sys.exit(0 if success else 1)
