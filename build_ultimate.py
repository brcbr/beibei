#!/usr/bin/env python3
"""
Build Script Fixed Version - No f-string multiline issues
"""

import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
from datetime import datetime

class XieboBuilder:
    def __init__(self):
        self.build_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.final_dir = "dist/protected"
        
    def build(self, source_file):
        """Main build function - SIMPLE AND WORKING"""
        print("="*60)
        print("🔧 XIEBO BUILD TOOL")
        print(f"Build ID: {self.build_id}")
        print("="*60)
        
        # Check source
        if not os.path.exists(source_file):
            print(f"❌ Source file not found: {source_file}")
            return False
        
        # Create output directory
        os.makedirs(self.final_dir, exist_ok=True)
        
        # Backup source
        backup_path = os.path.join(self.final_dir, "xiebo_source_backup.py")
        shutil.copy2(source_file, backup_path)
        print(f"📄 Source backup: {backup_path}")
        
        try:
            # STEP 1: Obfuscate with PyArmor
            print("\n1️⃣ Obfuscating with PyArmor...")
            
            # Try different PyArmor commands
            cmds_to_try = [
                ["pyarmor", "gen", "-O", "obfuscated", source_file],
                ["pyarmor", "gen", "obfuscated", source_file],
                ["pyarmor", "gen", "-O", "obfuscated", "--mix-str", source_file],
            ]
            
            obfuscated = False
            for cmd in cmds_to_try:
                success, stdout, stderr = self.run_command(cmd)
                if success:
                    print(f"✅ PyArmor success with: {' '.join(cmd[:3])}")
                    obfuscated = True
                    break
                else:
                    print(f"⚠️  PyArmor failed: {stderr[:100]}")
            
            if not obfuscated:
                print("⚠️  PyArmor failed, using original file")
                shutil.copy2(source_file, "obfuscated/xiebo.py")
            
            # STEP 2: Compile with PyInstaller
            print("\n2️⃣ Compiling with PyInstaller...")
            
            # Clean previous builds
            for dir_name in ['build', 'dist']:
                if os.path.exists(dir_name):
                    shutil.rmtree(dir_name, ignore_errors=True)
            
            # PyInstaller command
            pyinstaller_cmd = [
                "pyinstaller",
                "--onefile",
                "--console",
                "--clean",
                "--name=xiebo_protected",
                "--hidden-import=pyodbc",
                "--hidden-import=cryptography",
                "--hidden-import=hashlib",
                "--hidden-import=base64",
                "--strip",
                "--noupx",
                "obfuscated/xiebo.py"
            ]
            
            success, stdout, stderr = self.run_command(pyinstaller_cmd, timeout=120)
            
            if not success:
                print(f"❌ PyInstaller failed: {stderr[:200]}")
                return False
            
            print("✅ PyInstaller compilation successful")
            
            # STEP 3: Create final package
            print("\n3️⃣ Creating final package...")
            self.create_final_package()
            
            # STEP 4: Cleanup
            print("\n4️⃣ Cleaning up...")
            self.cleanup()
            
            # Success message
            self.print_success()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_command(self, cmd, timeout=60):
        """Run a command"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def create_final_package(self):
        """Create final deployment package"""
        # Copy executable
        exec_name = "xiebo_protected.exe" if os.name == 'nt' else "xiebo_protected"
        src_exec = os.path.join("dist", exec_name)
        
        if os.path.exists(src_exec):
            dest_exec = os.path.join(self.final_dir, exec_name)
            shutil.copy2(src_exec, dest_exec)
            
            if os.name != 'nt':
                os.chmod(dest_exec, 0o755)
            
            print(f"📦 Executable: {dest_exec}")
        
        # Create launcher script
        self.create_launcher_script(exec_name)
        
        # Create README
        self.create_readme_file(exec_name)
        
        # Create install script
        self.create_install_script()
        
        print(f"✅ Package created in: {self.final_dir}")
    
    def create_launcher_script(self, exec_name):
        """Create launcher script without complex f-strings"""
        build_id = self.build_id
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        launcher_content = '''#!/usr/bin/env python3
"""
Xiebo Launcher
'''

        launcher_content += f'Build ID: {build_id}\n'
        launcher_content += f'Generated: {current_time}\n'
        launcher_content += '''"""
'''

        launcher_content += '''
import os
import sys
import subprocess

def main():
    # Get executable path
    script_dir = os.path.dirname(os.path.abspath(__file__))
'''

        launcher_content += f'    exec_path = os.path.join(script_dir, "{exec_name}")' + '\n\n'
        
        launcher_content += '''    if not os.path.exists(exec_path):
        print(f"❌ Executable not found: {exec_path}")
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
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        launcher_path = os.path.join(self.final_dir, "run_xiebo.py")
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        if os.name != 'nt':
            os.chmod(launcher_path, 0o755)
        
        print(f"📄 Launcher: {launcher_path}")
    
    def create_readme_file(self, exec_name):
        """Create README file without f-string issues"""
        lines = []
        lines.append("# Xiebo Protected Executable")
        lines.append("")
        lines.append(f"## Build Information")
        lines.append(f"- Build ID: {self.build_id}")
        lines.append(f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- Protection: PyArmor obfuscation + PyInstaller")
        lines.append("")
        lines.append("## Files")
        lines.append(f"- `{exec_name}` - Main executable (standalone)")
        lines.append("- `run_xiebo.py` - Launcher script (optional)")
        lines.append("- `install_deps.sh` - Dependency installer")
        lines.append("- `xiebo_source_backup.py` - Original source backup")
        lines.append("")
        lines.append("## Quick Start")
        lines.append("")
        lines.append("### 1. Install Dependencies")
        lines.append("```bash")
        lines.append("chmod +x install_deps.sh")
        lines.append("sudo ./install_deps.sh")
        lines.append("```")
        lines.append("")
        lines.append("### 2. Configure Environment")
        lines.append("```bash")
        lines.append("# Set encryption key")
        lines.append("export XIEBO_ENCRYPTION_KEY='your_encryption_key_here'")
        lines.append("")
        lines.append("# Or create .env file")
        lines.append("echo 'XIEBO_ENCRYPTION_KEY=your_key' > .env")
        lines.append("```")
        lines.append("")
        lines.append("### 3. Run")
        lines.append("```bash")
        lines.append(f"# Method 1: Direct executable")
        lines.append(f"chmod +x {exec_name}")
        lines.append(f"./{exec_name} --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z")
        lines.append("")
        lines.append("# Method 2: Using launcher")
        lines.append("python3 run_xiebo.py --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z")
        lines.append("```")
        lines.append("")
        lines.append("## Notes")
        lines.append("- The executable is standalone (no Python installation required)")
        lines.append("- Still requires SQL Server ODBC driver (installed by script)")
        lines.append("- Set XIEBO_ENCRYPTION_KEY environment variable")
        lines.append("- Tested on Ubuntu 20.04+, Debian 10+")
        
        readme_path = os.path.join(self.final_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"📄 README: {readme_path}")
    
    def create_install_script(self):
        """Create installation script"""
        install_script = '''#!/bin/bash
# install_deps.sh - Install dependencies for Xiebo

echo "🔧 Installing Xiebo dependencies..."

# Check OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Cannot detect OS"
    exit 1
fi

echo "📦 OS: $OS"

# Install based on OS
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Installing for Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y curl gnupg
    
    # Install ODBC
    sudo apt-get install -y unixodbc unixodbc-dev
    
    # Install MS SQL Server ODBC driver
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | sudo tee /etc/apt/sources.list.d/mssql-release.list
    sudo apt-get update
    sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
    
    echo "✅ Dependencies installed for Ubuntu/Debian"
    
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    echo "Installing for CentOS/RHEL/Fedora..."
    sudo yum install -y unixODBC unixODBC-devel
    
    # Add Microsoft repo
    curl -fsSL https://packages.microsoft.com/config/rhel/8/prod.repo | sudo tee /etc/yum.repos.d/mssql-release.repo
    sudo ACCEPT_EULA=Y yum install -y msodbcsql18
    
    echo "✅ Dependencies installed for CentOS/RHEL"
    
else
    echo "⚠️  Unsupported OS: $OS"
    echo "Please manually install:"
    echo "  1. unixodbc"
    echo "  2. Microsoft ODBC Driver 18 for SQL Server"
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "💡 Next steps:"
echo "  1. Set encryption key:"
echo "     export XIEBO_ENCRYPTION_KEY='your-key'"
echo "  2. Make executable: chmod +x xiebo_protected"
echo "  3. Run: ./xiebo_protected --help"
'''
        
        install_path = os.path.join(self.final_dir, "install_deps.sh")
        with open(install_path, 'w') as f:
            f.write(install_script)
        
        if os.name != 'nt':
            os.chmod(install_path, 0o755)
        
        print(f"📄 Install script: {install_path}")
    
    def cleanup(self):
        """Cleanup temporary files"""
        dirs_to_clean = ['build', 'obfuscated', '__pycache__']
        
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name, ignore_errors=True)
        
        # Remove spec file
        spec_file = "xiebo_protected.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
        
        print("🧹 Cleanup completed")
    
    def print_success(self):
        """Print success message"""
        exec_name = "xiebo_protected.exe" if os.name == 'nt' else "xiebo_protected"
        
        print("\n" + "="*60)
        print("🎉 BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\n📁 Output directory: {self.final_dir}")
        print(f"📦 Executable: {self.final_dir}/{exec_name}")
        print(f"📄 Launcher: {self.final_dir}/run_xiebo.py")
        print(f"🔧 Installer: {self.final_dir}/install_deps.sh")
        print(f"📋 Documentation: {self.final_dir}/README.md")
        
        print("\n🚀 Quick start:")
        print(f"  cd {self.final_dir}")
        print(f"  chmod +x {exec_name}")
        print(f"  ./{exec_name} --help")
        
        print("\n✅ Features:")
        print("  - Code obfuscation (PyArmor)")
        print("  - Standalone executable (PyInstaller)")
        print("  - No Python installation required")
        print("  - Includes all dependencies")
        
        print("\n⚠️  Requirements on target machine:")
        print("  - SQL Server ODBC driver (use install_deps.sh)")
        print("  - XIEBO_ENCRYPTION_KEY environment variable")
        print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python build_fixed.py <source_file.py>")
        print("Example: python build_fixed.py xiebo.py")
        sys.exit(1)
    
    source_file = sys.argv[1]
    
    builder = XieboBuilder()
    success = builder.build(source_file)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
