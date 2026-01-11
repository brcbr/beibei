#!/usr/bin/env python3
"""
Build script with automatic dependency installation
"""

import os
import sys
import shutil
import subprocess
import importlib
from datetime import datetime

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        'cryptography',  # For encryption
        'pyodbc',        # For database
        'pyarmor',       # For obfuscation  
        'pyinstaller',   # For compilation
    ]
    
    for dep in dependencies:
        try:
            importlib.import_module(dep.replace('-', '_'))
            print(f"✅ {dep} already installed")
        except ImportError:
            print(f"📦 Installing {dep}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep, '--quiet'], 
                             check=True, capture_output=True)
                print(f"✅ {dep} installed")
            except Exception as e:
                print(f"❌ Failed to install {dep}: {e}")
                if dep == 'cryptography':
                    print("⚠️ Cryptography is CRITICAL for encryption")
                    return False
    return True

def check_and_fix_xiebo_file():
    """Check and fix xiebo.py file"""
    print("🔍 Checking xiebo.py...")
    
    if not os.path.exists('xiebo.py'):
        print("❌ xiebo.py not found in current directory")
        return False
    
    with open('xiebo.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for cryptography import
    if 'from cryptography.fernet import Fernet' not in content:
        print("⚠️ Cryptography import not found in xiebo.py")
        
        # Find where to add import
        lines = content.split('\n')
        import_added = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Add after existing imports
                lines.insert(i + 1, 'from cryptography.fernet import Fernet')
                import_added = True
                break
        
        if not import_added:
            # Add at the beginning
            lines.insert(0, 'from cryptography.fernet import Fernet')
        
        content = '\n'.join(lines)
        
        # Write back
        with open('xiebo.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added cryptography import to xiebo.py")
    
    return True

def build_executable():
    """Build the executable"""
    print("="*60)
    print("🔧 BUILDING XIEBO EXECUTABLE")
    print("="*60)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Step 2: Check and fix xiebo.py
    if not check_and_fix_xiebo_file():
        return False
    
    # Step 3: Clean previous builds
    print("\n🧹 Cleaning...")
    for d in ['dist', 'build', 'obfuscated', '__pycache__']:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    
    # Step 4: Obfuscate (optional)
    print("\n🛡️ Obfuscating...")
    obfuscated_file = 'xiebo.py'  # Default to original
    
    try:
        # Try to obfuscate
        cmd = ['pyarmor', 'gen', '-O', 'obfuscated', 'xiebo.py']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find obfuscated file
            if os.path.exists('obfuscated'):
                for file in os.listdir('obfuscated'):
                    if file.endswith('.py'):
                        obfuscated_file = os.path.join('obfuscated', file)
                        print(f"✅ Using obfuscated file: {obfuscated_file}")
                        break
        else:
            print(f"⚠️ Obfuscation failed: {result.stderr[:100]}")
            print("📁 Using original file (not obfuscated)")
            
    except Exception as e:
        print(f"⚠️ Obfuscation error: {e}")
        print("📁 Using original file")
    
    # Step 5: Compile with PyInstaller
    print("\n🔨 Compiling...")
    
    # Critical hidden imports
    hidden_imports = [
        'cryptography',          # CRITICAL
        'cryptography.fernet',   # CRITICAL
        'pyodbc',
        'platform',
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
    ]
    
    # Build command
    cmd = ['pyinstaller', '--onefile', '--console', '--clean', '--name=xiebo_protected']
    
    # Add hidden imports
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # Add additional data if cryptography needs it
    cmd.extend(['--add-data', f'{sys.executable[:-10]}../lib/python*/site-packages/cryptography:./cryptography'])
    
    # Add the file to compile
    cmd.append(obfuscated_file)
    
    print(f"Running: {' '.join(cmd[:6])}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            print(f"❌ Compilation failed: {result.stderr[:300]}")
            
            # Try simpler command
            print("\n🔄 Trying simpler compilation...")
            simple_cmd = [
                'pyinstaller',
                '--onefile',
                '--console',
                '--clean',
                '--name=xiebo_protected',
                '--hidden-import=cryptography',
                '--hidden-import=pyodbc',
                obfuscated_file
            ]
            
            result = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"❌ Simple compilation also failed: {result.stderr[:300]}")
                return False
        
        print("✅ Compilation successful")
        
    except subprocess.TimeoutExpired:
        print("⚠️ Compilation timeout")
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        return False
    
    # Step 6: Verify and package
    print("\n📦 Creating final package...")
    
    exec_name = 'xiebo_protected'
    if os.name == 'nt':
        exec_name += '.exe'
    
    # Look for executable
    src_path = None
    possible_paths = [
        f'dist/{exec_name}',
        exec_name,
        f'build/{exec_name}/{exec_name}',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            src_path = path
            break
    
    if not src_path:
        # Search recursively
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'xiebo' in file.lower() and not file.endswith('.py'):
                    src_path = os.path.join(root, file)
                    exec_name = os.path.basename(src_path)
                    break
            if src_path:
                break
    
    if src_path and os.path.exists(src_path):
        # Create output directory
        os.makedirs('dist/protected', exist_ok=True)
        dst_path = f'dist/protected/{exec_name}'
        
        # Copy executable
        shutil.copy(src_path, dst_path)
        
        # Make executable on Unix
        if os.name != 'nt':
            os.chmod(dst_path, 0o755)
        
        print(f"✅ Executable: {dst_path}")
        print(f"📏 Size: {os.path.getsize(dst_path) / 1024 / 1024:.2f} MB")
        
        # Create launcher
        create_launcher(exec_name)
        
        # Test the executable
        print("\n🧪 Testing executable...")
        try:
            test_cmd = [dst_path, '--help']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Executable test PASSED")
            else:
                print(f"⚠️ Executable test warning: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"⚠️ Could not test executable: {e}")
        
        return True
    
    else:
        print(f"❌ Executable not found after compilation")
        print("📁 Checking for files...")
        
        if os.path.exists('dist'):
            print("Files in dist/:")
            for root, dirs, files in os.walk('dist'):
                for file in files:
                    print(f"  {os.path.join(root, file)}")
        
        return False

def create_launcher(exec_name):
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
        print(f"Error: Executable not found at {{exec_path}}")
        sys.exit(1)
    
    # Make executable on Unix
    if os.name != "nt":
        try:
            os.chmod(exec_path, 0o755)
        except:
            pass
    
    # Check for required environment variable
    if not os.environ.get("XIEBO_ENCRYPTION_KEY"):
        print("Warning: XIEBO_ENCRYPTION_KEY environment variable not set")
        print("  Set it with: export XIEBO_ENCRYPTION_KEY='your_key_here'")
        print("  Or create .env file in this directory")
        print("")
    
    # Run the executable with all arguments
    cmd = [exec_path] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running executable: {{e}}")
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

def main():
    """Main function"""
    print("="*60)
    print("XIEBO BUILD SYSTEM")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists('xiebo.py'):
        print("❌ ERROR: xiebo.py not found in current directory")
        print("💡 Make sure you're in the directory containing xiebo.py")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Build
    success = build_executable()
    
    if success:
        print("\n" + "="*60)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📁 Output directory: dist/protected/")
        print("🚀 To run: cd dist/protected && ./xiebo_protected --help")
        print("\n⚠️  IMPORTANT: Set encryption key before running:")
        print("   export XIEBO_ENCRYPTION_KEY='your_encryption_key_here'")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ BUILD FAILED")
        print("="*60)
        
        # Provide troubleshooting tips
        print("\n💡 TROUBLESHOOTING:")
        print("1. Install dependencies manually:")
        print("   pip install cryptography pyodbc pyarmor pyinstaller")
        print("\n2. Try manual compilation:")
        print("   pyinstaller --onefile --console \\")
        print("     --hidden-import=cryptography \\")
        print("     --hidden-import=pyodbc \\")
        print("     --name=xiebo_protected xiebo.py")
        print("\n3. Check Python version:")
        print(f"   Python: {sys.version}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
