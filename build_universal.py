#!/usr/bin/env python3
# quick_protect.py - One file solution
import os, sys, subprocess

print("🔒 Quick Protection for Xiebo")

# Clean
for d in ['protected', 'dist']:
    if os.path.exists(d):
        import shutil
        shutil.rmtree(d)

# Try commands in order
commands = [
    ['pyarmor', 'gen', '-O', 'protected', '--obf-code', '2', '--mix-str', 'xiebo.py'],
    ['pyarmor', 'gen', '-O', 'protected', '--mix-str', 'xiebo.py'],
    ['pyarmor', 'gen', '-O', 'protected', 'xiebo.py'],
    ['pyarmor', 'gen', 'protected', 'xiebo.py']
]

for cmd in commands:
    print(f"Trying: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        print("✅ Success!")
        
        # Create runner
        with open('run.py', 'w') as f:
            f.write('''#!/usr/bin/env python3
import sys, os
sys.path.insert(0, 'protected')
from xiebo import main
main()
''')
        os.chmod('run.py', 0o755)
        
        print("\n📁 Output: protected/")
        print("🚀 Run: python3 run.py --batch-db 0,1 49 YOUR_ADDRESS")
        sys.exit(0)

print("❌ All methods failed. Try manually:")
print("pyarmor gen protected xiebo.py")
