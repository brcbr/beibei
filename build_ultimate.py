#!/usr/bin/env python3
"""
Build Script for PyArmor 9
Fixed for latest PyArmor version
"""

import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
from datetime import datetime

class PyArmor9Builder:
    def __init__(self):
        self.build_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = tempfile.mkdtemp(prefix=f"xiebo_build_{self.build_id}_")
        self.final_dir = "dist/protected"
        
    def get_pyarmor_version(self):
        """Get PyArmor version and check capabilities"""
        try:
            result = subprocess.run(['pyarmor', '--version'], 
                                  capture_output=True, text=True)
            version_output = result.stdout.strip()
            print(f"🔍 PyArmor Version: {version_output}")
            
            # Check help to see available options
            help_result = subprocess.run(['pyarmor', 'gen', '--help'], 
                                       capture_output=True, text=True)
            help_text = help_result.stdout + help_result.stderr
            
            # Detect features
            has_restrict_mode = '--restrict-mode' in help_text
            has_mix_str = '--mix-str' in help_text
            has_obf_code = '--obf-code' in help_text
            
            return {
                'version': version_output,
                'has_restrict_mode': has_restrict_mode,
                'has_mix_str': has_mix_str,
                'has_obf_code': has_obf_code,
                'help_text': help_text[:500]  # First 500 chars
            }
        except Exception as e:
            print(f"❌ Cannot get PyArmor version: {e}")
            return None
    
    def obfuscate_pyarmor9(self, source_file):
        """Obfuscate using PyArmor 9 compatible commands"""
        print("🔒 Obfuscating with PyArmor 9...")
        
        # Get PyArmor capabilities
        caps = self.get_pyarmor_version()
        if not caps:
            print("⚠️  Cannot detect PyArmor features, using simple mode")
            return self.obfuscate_simple(source_file)
        
        print(f"📊 Detected features: mix-str={caps['has_mix_str']}, "
              f"restrict-mode={caps['has_restrict_mode']}")
        
        obfuscated_dir = os.path.join(self.temp_dir, "obfuscated")
        os.makedirs(obfuscated_dir, exist_ok=True)
        
        # Try different command patterns for PyArmor 9
        command_patterns = [
            # Pattern 1: Modern PyArmor 9
            ['pyarmor', 'gen', '-O', obfuscated_dir, '--mix-str', source_file],
            
            # Pattern 2: With obf-code if available
            ['pyarmor', 'gen', '-O', obfuscated_dir, '--obf-code=2', source_file],
            
            # Pattern 3: Simple mode
            ['pyarmor', 'gen', '-O', obfuscated_dir, source_file],
            
            # Pattern 4: Old style (backward compatible)
            ['pyarmor', 'gen', obfuscated_dir, source_file],
        ]
        
        success = False
        for i, cmd in enumerate(command_patterns, 1):
            # Skip patterns based on detected capabilities
            if i == 1 and not caps['has_mix_str']:
                continue
            if i == 2 and not caps['has_obf_code']:
                continue
            
            print(f"\n🔄 Trying pattern {i}:")
            print(f"   Command: {' '.join(cmd[:5])}...")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Pattern {i} successful!")
                    success = True
                    
                    # Check if files were created
                    if os.path.exists(obfuscated_dir):
                        files = os.listdir(obfuscated_dir)
                        if files:
                            print(f"📁 Created {len(files)} files in {obfuscated_dir}")
                            break
                        else:
                            print(f"⚠️  No files created in {obfuscated_dir}")
                else:
                    print(f"❌ Pattern {i} failed: {result.stderr[:100]}")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️  Pattern {i} timeout")
            except Exception as e:
                print(f"⚠️  Pattern {i} error: {e}")
        
        if not success:
            print("❌ All PyArmor patterns failed, using original file")
            shutil.copy2(source_file, os.path.join(obfuscated_dir, "xiebo.py"))
        
        return obfuscated_dir
    
    def obfuscate_simple(self, source_file):
        """Simple obfuscation fallback"""
        print("🔒 Using simple obfuscation...")
        
        obfuscated_dir = os.path.join(self.temp_dir, "obfuscated")
        os.makedirs(obfuscated_dir, exist_ok=True)
        
        # Just copy the file
        shutil.copy2(source_file, os.path.join(obfuscated_dir, "xiebo.py"))
        
        # Add simple string obfuscation
        self.simple_string_obfuscation(os.path.join(obfuscated_dir, "xiebo.py"))
        
        return obfuscated_dir
    
    def simple_string_obfuscation(self, filepath):
        """Simple string obfuscation for fallback"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple encryption for sensitive strings
            import base64
            
            # Find and obfuscate database credentials
            patterns = [
                (r'SERVER\s*=\s*"([^"]+)"', 'SERVER'),
                (r'DATABASE\s*=\s*"([^"]+)"', 'DATABASE'),
                (r'USERNAME\s*=\s*"([^"]+)"', 'USERNAME'),
                (r'PASSWORD\s*=\s*"([^"]+)"', 'PASSWORD'),
            ]
            
            import re
            for pattern, varname in patterns:
                match = re.search(pattern, content)
                if match:
                    original = match.group(1)
                    # Simple base64 encoding
                    encoded = base64.b64encode(original.encode()).decode()
                    replacement = f'{varname} = base64.b64decode("{encoded}").decode()'
                    content = content.replace(match.group(0), replacement)
            
            # Add base64 import if not present
            if 'import base64' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        lines.insert(i, 'import base64')
                        break
                content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("✅ Applied simple string obfuscation")
            
        except Exception as e:
            print(f"⚠️  Simple obfuscation failed: {e}")
    
    def compile_with_pyinstaller(self, source_file):
        """Compile with PyInstaller"""
        print("🔨 Compiling with PyInstaller...")
        
        # Clean previous builds
        for dir_name in ['build', 'dist']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name, ignore_errors=True)
        
        # Create spec file for better control
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{source_file}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pyodbc', 'cryptography', 'hashlib', 'base64', 'ssl'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='xiebo_protected',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        spec_file = 'xiebo.spec'
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Build with spec file
        cmd = ['pyinstaller', '--clean', '--noconfirm', spec_file]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ PyInstaller compilation successful")
                
                # Check if executable was created
                exec_name = "xiebo_protected.exe" if os.name == 'nt' else "xiebo_protected"
                exec_path = os.path.join("dist", exec_name)
                
                if os.path.exists(exec_path):
                    print(f"📦 Executable created: {exec_path}")
                    return exec_path
                else:
                    print(f"⚠️  Executable not found at: {exec_path}")
                    # Check alternative location
                    for root, dirs, files in os.walk("dist"):
                        for file in files:
                            if "xiebo" in file.lower():
                                alt_path = os.path.join(root, file)
                                print(f"📦 Found alternative: {alt_path}")
                                return alt_path
            else:
                print(f"❌ PyInstaller failed: {result.stderr[:200]}")
                
                # Try direct command as fallback
                print("🔄 Trying direct PyInstaller command...")
                return self.compile_direct(source_file)
                
        except subprocess.TimeoutExpired:
            print("⚠️  PyInstaller timeout")
            return None
        except Exception as e:
            print(f"❌ PyInstaller error: {e}")
            return None
    
    def compile_direct(self, source_file):
        """Direct PyInstaller compilation"""
        print("🔨 Trying direct compilation...")
        
        cmd = [
            'pyinstaller',
            '--onefile',
            '--console',
            '--clean',
            '--name=xiebo_protected',
            '--hidden-import=pyodbc',
            '--hidden-import=cryptography',
            '--hidden-import=hashlib',
            '--hidden-import=base64',
            '--strip',
            '--noupx',
            source_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            
            exec_name = "xiebo_protected.exe" if os.name == 'nt' else "xiebo_protected"
            exec_path = os.path.join("dist", exec_name)
            
            if os.path.exists(exec_path):
                print(f"✅ Direct compilation successful: {exec_path}")
                return exec_path
            
        except Exception as e:
            print(f"❌ Direct compilation failed: {e}")
        
        return None
    
    def create_launcher(self, exec_path):
        """Create launcher script"""
        print("📄 Creating launcher...")
        
        if not exec_path or not os.path.exists(exec_path):
            print("⚠️  No executable found, skipping launcher")
            return None
        
        exec_name = os.path.basename(exec_path)
        
        launcher_content = f'''#!/usr/bin/env python3
"""
Xiebo Launcher
Build ID: {self.build_id}
"""

import os
import sys
import subprocess

def main():
    # Get executable path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exec_path = os.path.join(script_dir, "{exec_name}")
    
    if not os.path.exists(exec_path):
        print(f"❌ Executable not found: {{exec_path}}")
        sys.exit(1)
    
    # Make executable on Unix
    if os.name != 'nt':
        try:
            os.chmod(exec_path, 0o755)
        except:
            pass
    
    # Check for encryption key
    if not os.environ.get('XIEBO_ENCRYPTION_KEY'):
        print("⚠️  WARNING: XIEBO_ENCRYPTION_KEY environment variable not set")
        print("   Set it with: export XIEBO_ENCRYPTION_KEY='your-key'")
        print("   Or create .env file in the same directory")
    
    # Run the executable
    cmd = [exec_path] + sys.argv[1:]
    
    try:
        process = subprocess.run(cmd)
        sys.exit(process.returncode)
    except Exception as e:
        print(f"❌ Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        launcher_path = os.path.join(self.final_dir, "run_xiebo.py")
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        if os.name != 'nt':
            os.chmod(launcher_path, 0o755)
        
        print(f"✅ Launcher created: {launcher_path}")
        return launcher_path
    
    def create_deployment_package(self, exec_path):
        """Create final deployment package"""
        print("🎁 Creating deployment package...")
        
        os.makedirs(self.final_dir, exist_ok=True)
        
        # Copy executable
        if exec_path and os.path.exists(exec_path):
            dest_exec = os.path.join(self.final_dir, os.path.basename(exec_path))
            shutil.copy2(exec_path, dest_exec)
            
            if os.name != 'nt':
                os.chmod(dest_exec, 0o755)
            
            print(f"📦 Executable copied to: {dest_exec}")
        
        # Create launcher
        self.create_launcher(exec_path)
        
        # Create README
        self.create_readme()
        
        # Create install script
        self.create_install_script()
        
        # Create .env template
        self.create_env_template()
        
        print(f"\n✅ Package created in: {self.final_dir}")
        
        return True
    
    def create_readme(self):
        """Create README file"""
        readme_content = f'''# Xiebo Protected Executable

## Build Information
- Build ID: {self.build_id}
- Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Protection: PyArmor obfuscation + PyInstaller

## Files
- `xiebo_protected` - Main executable (standalone)
- `run_xiebo.py` - Launcher script (optional)
- `install_dependencies.sh` - Dependency installer
- `.env.template` - Environment template

## Quick Start

### 1. Install Dependencies
```bash
chmod +x install_dependencies.sh
sudo ./install_dependencies.sh
