# build_universal.py
import os
import sys
import shutil
import subprocess
import platform
from datetime import datetime

def detect_pyarmor_version():
    """Detect PyArmor version and capabilities"""
    try:
        result = subprocess.run(['pyarmor', '--version'], 
                              capture_output=True, text=True)
        version_str = result.stdout.strip()
        
        # Parse version number
        version_parts = version_str.split('.')
        if len(version_parts) >= 2:
            major = int(version_parts[0])
            minor = int(version_parts[1])
        else:
            major = 7  # Assume older version
        
        print(f"🔍 Detected PyArmor version: {version_str}")
        
        # Check available options
        print("\n📋 Checking available options...")
        help_result = subprocess.run(['pyarmor', 'gen', '--help'], 
                                   capture_output=True, text=True)
        help_text = help_result.stdout + help_result.stderr
        
        capabilities = {
            'version': version_str,
            'major': major,
            'has_pack': '--pack' in help_text,
            'has_mix_str': '--mix-str' in help_text,
            'has_restrict': '--restrict' in help_text,
            'has_restrict_mode': '--restrict-mode' in help_text,
            'max_obf_code': 2 if '3' not in help_text else 3,
            'has_obf_mod': '--obf-module' in help_text or '--obf-mod' in help_text,
            'has_wrap': '--no-wrap' in help_text,
            'has_enable': '--enable' in help_text
        }
        
        return capabilities
        
    except Exception as e:
        print(f"❌ Cannot detect PyArmor: {e}")
        return None

def obfuscate_universal():
    """Universal obfuscation that works with all PyArmor versions"""
    
    print("="*60)
    print("🔧 Universal Xiebo Code Protection Tool")
    print("="*60)
    
    # Detect PyArmor capabilities
    caps = detect_pyarmor_version()
    if not caps:
        print("❌ PyArmor not found or not working")
        print("Install with: pip install pyarmor")
        sys.exit(1)
    
    print(f"\n✅ PyArmor {caps['version']} detected")
    print(f"   Maximum obf-code level: {caps['max_obf_code']}")
    
    # Backup original
    original_file = "xiebo.py"
    if not os.path.exists(original_file):
        print(f"❌ Original file not found: {original_file}")
        sys.exit(1)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(original_file, f"{backup_dir}/xiebo_original_{timestamp}.py")
    print(f"✅ Backup created: {backup_dir}/xiebo_original_{timestamp}.py")
    
    # Clean previous builds
    for dir_name in ['dist', 'build', 'protected']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Create output directory
    os.makedirs('dist', exist_ok=True)
    
    # ============================================
    # OPTION 1: BASIC OBFUSCATION (Works with all versions)
    # ============================================
    print(f"\n{'='*40}")
    print("1️⃣ Basic Obfuscation")
    print(f"{'='*40}")
    
    basic_cmd = ['pyarmor', 'gen', '-O', 'dist/basic', original_file]
    
    # Add available options based on version
    if caps['max_obf_code'] >= 2:
        basic_cmd.extend(['--obf-code', '2'])
    elif caps['max_obf_code'] >= 1:
        basic_cmd.extend(['--obf-code', '1'])
    
    if caps['has_mix_str']:
        basic_cmd.append('--mix-str')
    
    if caps['has_restrict']:
        basic_cmd.extend(['--restrict', '2'])
    elif caps['has_restrict_mode']:
        basic_cmd.extend(['--restrict-mode', '2'])
    
    if caps['has_wrap']:
        basic_cmd.extend(['--no-wrap'])
    
    print(f"Command: {' '.join(basic_cmd)}")
    
    try:
        result = subprocess.run(basic_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Basic obfuscation successful")
            # Copy main file for easy access
            shutil.copy2('dist/basic/xiebo.py', 'xiebo_basic.py')
            print("📄 Basic version saved as: xiebo_basic.py")
        else:
            print(f"⚠️ Basic obfuscation warning: {result.stderr}")
            
            # Try simpler command
            print("\n🔄 Trying simpler command...")
            simple_cmd = ['pyarmor', 'gen', '-O', 'dist/basic_simple', original_file]
            subprocess.run(simple_cmd, check=False)
            
    except Exception as e:
        print(f"❌ Basic obfuscation failed: {e}")
    
    # ============================================
    # OPTION 2: WITH RUNTIME PACKAGE
    # ============================================
    print(f"\n{'='*40}")
    print("2️⃣ Obfuscation with Runtime Package")
    print(f"{'='*40}")
    
    runtime_cmd = ['pyarmor', 'gen', '-O', 'dist/runtime_pkg', original_file]
    
    # Use maximum available obfuscation
    if caps['max_obf_code'] >= 2:
        runtime_cmd.extend(['--obf-code', '2'])
    elif caps['max_obf_code'] >= 1:
        runtime_cmd.extend(['--obf-code', '1'])
    
    if caps['has_mix_str']:
        runtime_cmd.append('--mix-str')
    
    # Add enable options if available
    if caps['has_enable']:
        runtime_cmd.extend(['--enable', 'jit'])
    
    print(f"Command: {' '.join(runtime_cmd)}")
    
    try:
        result = subprocess.run(runtime_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Runtime package obfuscation successful")
    except Exception as e:
        print(f"❌ Runtime package obfuscation failed: {e}")
    
    # ============================================
    # OPTION 3: PACK TO EXECUTABLE (if available)
    # ============================================
    if caps['has_pack']:
        print(f"\n{'='*40}")
        print("3️⃣ Pack to Executable")
        print(f"{'='*40}")
        
        pack_cmd = [
            'pyarmor', 'gen',
            '-O', 'dist/packed',
            '--pack', 'xiebo_app',
            original_file
        ]
        
        print(f"Command: {' '.join(pack_cmd)}")
        
        try:
            result = subprocess.run(pack_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Packed executable created")
                
                # Find and make executable
                for root, dirs, files in os.walk('dist/packed'):
                    for file in files:
                        if file.startswith('xiebo_app'):
                            filepath = os.path.join(root, file)
                            if platform.system() != 'Windows':
                                os.chmod(filepath, 0o755)
                            print(f"📦 Packed file: {filepath}")
                            break
        except Exception as e:
            print(f"❌ Packing failed: {e}")
    
    # ============================================
    # OPTION 4: CUSTOM PROTECTION SCRIPT
    # ============================================
    print(f"\n{'='*40}")
    print("4️⃣ Custom Protection Script")
    print(f"{'='*40}")
    
    # Create a wrapper that adds extra protection
    wrapper_content = '''#!/usr/bin/env python3
"""
Protected Xiebo Launcher
Adds extra security layers before running obfuscated code
"""

import os
import sys
import hashlib
import time
import random

class SecurityLayer:
    @staticmethod
    def integrity_check():
        """Check file integrity"""
        current_file = os.path.abspath(__file__)
        try:
            with open(current_file, 'rb') as f:
                content = f.read()
            
            # Simple hash check
            file_hash = hashlib.sha256(content).hexdigest()
            
            # You can add your expected hash here
            expected_hash = ""  # Add your hash here
            
            if expected_hash and file_hash != expected_hash:
                print("❌ Integrity check failed")
                return False
                
        except Exception as e:
            print(f"⚠️ Integrity check warning: {e}")
        
        return True
    
    @staticmethod
    def anti_tamper():
        """Anti-tampering measures"""
        try:
            # Check file modification time
            current_file = os.path.abspath(__file__)
            mod_time = os.path.getmtime(current_file)
            current_time = time.time()
            
            # If file was modified recently (within 5 seconds), might be tampering
            if current_time - mod_time < 5:
                time.sleep(random.randint(5, 10))
                
        except:
            pass
    
    @staticmethod
    def run_protected():
        """Run the obfuscated code"""
        # Add obfuscated directory to path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        obfuscated_path = os.path.join(script_dir, 'dist', 'basic')
        
        if os.path.exists(obfuscated_path):
            sys.path.insert(0, obfuscated_path)
            try:
                from xiebo import main
                main()
            except ImportError as e:
                print(f"❌ Cannot import obfuscated module: {e}")
                print("Make sure to run the obfuscation first.")
                sys.exit(1)
        else:
            print("❌ Obfuscated files not found")
            print("Run: python build_universal.py first")
            sys.exit(1)

def main():
    print("🔒 Loading protected Xiebo...")
    
    # Run security checks
    SecurityLayer.anti_tamper()
    
    if not SecurityLayer.integrity_check():
        sys.exit(1)
    
    # Run the protected code
    SecurityLayer.run_protected()

if __name__ == "__main__":
    main()
'''
    
    with open('xiebo_protected.py', 'w') as f:
        f.write(wrapper_content)
    
    if platform.system() != 'Windows':
        os.chmod('xiebo_protected.py', 0o755)
    
    print("✅ Created protected launcher: xiebo_protected.py")
    
    # ============================================
    # CREATE SIMPLE BUILD SCRIPT
    # ============================================
    build_script = '''#!/bin/bash
# build.sh - Simple build script for Xiebo
echo "🔧 Building Xiebo with protection..."

# Clean previous builds
rm -rf dist/ build/ __pycache__/

# Run universal obfuscator
python3 build_universal.py

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output directories:"
echo "  dist/basic/           - Basic obfuscated version"
echo "  dist/runtime_pkg/     - With runtime package"
if [ -d "dist/packed" ]; then
    echo "  dist/packed/         - Packed executable"
fi
echo ""
echo "🚀 Quick run commands:"
echo "  python3 xiebo_protected.py          # Use protected launcher"
echo "  cd dist/basic && python3 xiebo.py   # Direct run"
echo ""
echo "📦 Distribution:"
echo "  To distribute, copy the entire 'dist/basic/' directory"
echo "  along with 'xiebo_protected.py'"
'''
    
    with open('build.sh', 'w') as f:
        f.write(build_script)
    
    if platform.system() != 'Windows':
        os.chmod('build.sh', 0o755)
    
    print("✅ Created build script: build.sh")
    
    # ============================================
    # FINAL SUMMARY
    # ============================================
    print(f"\n{'='*60}")
    print("🎉 PROTECTION PROCESS COMPLETED!")
    print(f"{'='*60}")
    
    print("\n📊 PyArmor Version: {}".format(caps['version']))
    print("📈 Obfuscation Level: {}".format("Basic" if caps['max_obf_code'] < 2 else "Advanced"))
    
    print("\n📁 Generated Files:")
    print("  • xiebo_protected.py  - Main launcher with security layers")
    print("  • build.sh            - Build automation script")
    print("  • dist/basic/         - Obfuscated Python files")
    
    if caps['has_pack'] and os.path.exists('dist/packed'):
        print("  • dist/packed/       - Packed executable")
    
    print("\n🚀 To run the protected version:")
    print("  python3 xiebo_protected.py --batch-db 0,1 49 1Pd8Vv...")
    
    print("\n🔧 To rebuild:")
    print("  chmod +x build.sh && ./build.sh")
    print("  OR")
    print("  python3 build_universal.py")
    
    print(f"\n{'='*60}")

def simple_obfuscation():
    """Simple one-step obfuscation for beginners"""
    print("🔧 Simple Obfuscation Method")
    print("="*40)
    
    # Try the most compatible command
    cmd = ['pyarmor', 'gen', '-O', 'protected', 'xiebo.py']
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Simple obfuscation successful!")
        print("📁 Output in: protected/ directory")
        print("🚀 Run with: cd protected && python xiebo.py")
        
        # Create a simple launcher
        launcher = '''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'protected'))
from xiebo import main
main()
'''
        
        with open('run_xiebo.py', 'w') as f:
            f.write(launcher)
        
        if platform.system() != 'Windows':
            os.chmod('run_xiebo.py', 0o755)
        
        print("✅ Created launcher: run_xiebo.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative method:")
        print("1. Manually obfuscate:")
        print("   pyarmor gen -O protected xiebo.py")
        print("2. Then run:")
        print("   cd protected && python xiebo.py")

if __name__ == "__main__":
    print("🔒 Xiebo Code Protection Toolkit")
    print("="*40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        simple_obfuscation()
    else:
        obfuscate_universal()
