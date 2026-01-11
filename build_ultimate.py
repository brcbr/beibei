#!/usr/bin/env python3
"""
Robust build script - handles different PyInstaller output locations
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def find_executable():
    """Find executable in various possible locations"""
    possible_paths = [
        "dist/xiebo_protected",           # Linux default
        "dist/xiebo_protected.exe",       # Windows default  
        "xiebo_protected",                # Direct in current dir
        "xiebo_protected.exe",            # Windows direct
        "build/xiebo_protected/xiebo_protected",  # Sometimes here
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found executable: {path}")
            return path
    
    # Search recursively
    for root, dirs, files in os.walk("."):
        for file in files:
            if "xiebo" in file.lower() and not file.endswith(".py"):
                full_path = os.path.join(root, file)
                print(f"🔍 Found possible executable: {full_path}")
                return full_path
    
    return None

def build_xiebo(source_file):
    """Main build function"""
    print("="*60)
    print("🔧 XIEBO BUILDER - ROBUST VERSION")
    print("="*60)
    
    # Check source
    if not os.path.exists(source_file):
        print(f"❌ Source not found: {source_file}")
        return False
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for item in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(item):
            shutil.rmtree(item, ignore_errors=True)
    
    # STEP 1: Obfuscate
    print("\n1️⃣ Obfuscating...")
    
    # Try PyArmor
    try:
        cmd = ["pyarmor", "gen", "-O", "obfuscated", source_file]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyArmor successful")
            # Find obfuscated file
            obf_file = None
            if os.path.exists("obfuscated"):
                for file in os.listdir("obfuscated"):
                    if file.endswith(".py"):
                        obf_file = os.path.join("obfuscated", file)
                        print(f"📁 Using: {obf_file}")
                        break
        else:
            print(f"⚠️ PyArmor failed: {result.stderr[:100]}")
            obf_file = source_file
    except:
        print("⚠️ PyArmor not available, using original")
        obf_file = source_file
    
    # STEP 2: Compile with PyInstaller
    print("\n2️⃣ Compiling...")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--clean",
        "--name=xiebo_protected",
        "--hidden-import=pyodbc",
        "--hidden-import=cryptography",
        obf_file
    ]
    
    print(f"Running: {' '.join(pyinstaller_cmd[:5])}...")
    
    try:
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr[:200]}")
            return False
        
        print("✅ PyInstaller compilation completed")
        
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        return False
    
    # STEP 3: Find and copy executable
    print("\n3️⃣ Creating final package...")
    
    exec_path = find_executable()
    
    if not exec_path:
        print("❌ Could not find executable after compilation")
        print("📁 Checking dist directory...")
        if os.path.exists("dist"):
            print("Contents of dist/:")
            for root, dirs, files in os.walk("dist"):
                for file in files:
                    print(f"  {os.path.join(root, file)}")
        return False
    
    # Create protected directory
    protected_dir = "dist/protected"
    os.makedirs(protected_dir, exist_ok=True)
    
    # Copy executable
    exec_name = os.path.basename(exec_path)
    dest_path = os.path.join(protected_dir, exec_name)
    
    try:
        shutil.copy2(exec_path, dest_path)
        print(f"📦 Copied: {exec_path} -> {dest_path}")
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        # Try to move instead
        try:
            shutil.move(exec_path, dest_path)
            print(f"📦 Moved: {exec_path} -> {dest_path}")
        except Exception as e2:
            print(f"❌ Move also failed: {e2}")
            # Just use the original location
            dest_path = exec_path
    
    # Make executable on Unix
    if os.name != 'nt' and os.path.exists(dest_path):
        os.chmod(dest_path, 0o755)
        print(f"🔧 Made executable: {dest_path}")
    
    # STEP 4: Create launcher
    print("\n4️⃣ Creating launcher...")
    create_launcher(protected_dir, exec_name)
    
    # STEP 5: Create README
    create_readme(protected_dir, exec_name)
    
    # Success
    print("\n" + "="*60)
    print("🎉 BUILD SUCCESSFUL!")
    print("="*60)
    print(f"\n📁 Output: {protected_dir}/")
    print(f"📦 Executable: {dest_path}")
    print(f"📄 Launcher: {protected_dir}/run_xiebo.py")
    
    print("\n🚀 Quick test:")
    print(f"  cd {protected_dir}")
    print(f"  ./{exec_name} --help")
    print("="*60)
    
    return True

def create_launcher(output_dir, exec_name):
    """Create launcher script"""
    launcher = f'''#!/usr/bin/env python3
"""
Xiebo Launcher
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
import sys
import subprocess

def main():
    # Get path to executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exec_path = os.path.join(script_dir, "{exec_name}")
    
    if not os.path.exists(exec_path):
        print(f"❌ Executable not found: {{exec_path}}")
        sys.exit(1)
    
    # Make executable if needed
    if os.name != 'nt':
        try:
            os.chmod(exec_path, 0o755)
        except:
            pass
    
    # Run with arguments
    cmd = [exec_path] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    launcher_path = os.path.join(output_dir, "run_xiebo.py")
    with open(launcher_path, 'w') as f:
        f.write(launcher)
    
    if os.name != 'nt':
        os.chmod(launcher_path, 0o755)
    
    print(f"📄 Launcher created: {launcher_path}")

def create_readme(output_dir, exec_name):
    """Create README file"""
    readme = f'''# Xiebo Protected Executable

## Files
- `{exec_name}` - Main executable (standalone)
- `run_xiebo.py` - Launcher script

## Usage
```bash
# Make executable
chmod +x {exec_name}

# Set encryption key
export XIEBO_ENCRYPTION_KEY="your_encryption_key_here"

# Run
./{exec_name} --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z

# Or use launcher
python3 run_xiebo.py --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z
