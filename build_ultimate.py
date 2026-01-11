#!/usr/bin/env python3
"""
Build script that ALWAYS WORKS - No complex f-strings
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def run_cmd(cmd):
    """Run command and return success"""
    print(f"Running: {' '.join(cmd[:4])}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except:
        return False

def build():
    """Main build function - SIMPLE AND WORKING"""
    print("="*50)
    print("BUILDING XIEBO")
    print("="*50)
    
    # Clean
    for d in ['dist', 'build', 'obfuscated']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # Step 1: Obfuscate
    print("\n1. Obfuscating...")
    if run_cmd(['pyarmor', 'gen', '-O', 'obfuscated', 'xiebo.py']):
        print("✅ Obfuscation done")
    else:
        print("⚠️ Obfuscation failed, using original")
        os.makedirs('obfuscated', exist_ok=True)
        shutil.copy('xiebo.py', 'obfuscated/xiebo.py')
    
    # Step 2: Compile
    print("\n2. Compiling...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',
        '--clean',
        '--name=xiebo_protected',
        '--hidden-import=pyodbc',
        '--hidden-import=cryptography',
        'obfuscated/xiebo.py'
    ]
    
    if run_cmd(cmd):
        print("✅ Compilation done")
    else:
        print("❌ Compilation failed")
        return False
    
    # Step 3: Create output
    print("\n3. Creating output...")
    os.makedirs('dist/protected', exist_ok=True)
    
    # Find executable
    exec_name = 'xiebo_protected'
    if os.name == 'nt':
        exec_name += '.exe'
    
    src = f'dist/{exec_name}'
    
    if not os.path.exists(src):
        # Try to find it
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'xiebo' in file.lower() and not file.endswith('.py'):
                    src = os.path.join(root, file)
                    exec_name = file
                    break
    
    if os.path.exists(src):
        dst = f'dist/protected/{exec_name}'
        shutil.copy(src, dst)
        
        if os.name != 'nt':
            os.chmod(dst, 0o755)
        
        print(f"✅ Executable: {dst}")
    else:
        print("❌ Executable not found")
        return False
    
    # Step 4: Create simple files
    print("\n4. Creating support files...")
    
    # Create launcher
    launcher = '''#!/usr/bin/env python3
import os
import sys
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
exec_path = os.path.join(script_dir, "''' + exec_name + '''")

if not os.path.exists(exec_path):
    print("Executable not found:", exec_path)
    sys.exit(1)

if os.name != "nt":
    try:
        os.chmod(exec_path, 0o755)
    except:
        pass

cmd = [exec_path] + sys.argv[1:]
try:
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
except Exception as e:
    print("Error:", e)
    sys.exit(1)
'''
    
    with open('dist/protected/run_xiebo.py', 'w') as f:
        f.write(launcher)
    
    if os.name != 'nt':
        os.chmod('dist/protected/run_xiebo.py', 0o755)
    
    # Create README
    readme_lines = [
        "# Xiebo Protected Executable",
        "",
        "## Files",
        f"- `{exec_name}` - Main executable",
        "- `run_xiebo.py` - Launcher script",
        "",
        "## Usage",
        "```bash",
        f"# Set encryption key",
        "export XIEBO_ENCRYPTION_KEY='your_key_here'",
        "",
        f"# Run directly",
        f"./{exec_name} --batch-db 0,1 49 ADDRESS",
        "",
        "# Or use launcher",
        "python3 run_xiebo.py --batch-db 0,1 49 ADDRESS",
        "```",
        "",
        "## Requirements",
        "- SQL Server ODBC Driver",
        "- XIEBO_ENCRYPTION_KEY environment variable",
        "",
        f"Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    
    with open('dist/protected/README.md', 'w') as f:
        f.write('\n'.join(readme_lines))
    
    # Success
    print("\n" + "="*50)
    print("BUILD SUCCESSFUL!")
    print("="*50)
    print(f"\nOutput: dist/protected/")
    print(f"Executable: dist/protected/{exec_name}")
    print(f"Launcher: dist/protected/run_xiebo.py")
    print("\nTest: cd dist/protected && ./" + exec_name + " --help")
    print("="*50)
    
    return True

if __name__ == "__main__":
    # Check if xiebo.py exists
    if not os.path.exists('xiebo.py'):
        print("❌ xiebo.py not found in current directory")
        sys.exit(1)
    
    success = build()
    sys.exit(0 if success else 1)
