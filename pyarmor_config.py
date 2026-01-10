# pyarmor_config.py
import os

config = {
    # Obfuscation mode: 0 (none), 1 (basic), 2 (normal), 3 (advanced)
    'obf_code': 2,
    
    # Obfuscate module names and function names
    'obf_mod': 1,
    
    # Mix up the constant strings
    'mix_str': 1,
    
    # Restrict mode: 1 (no restrict), 2 (allow same machine), 3 (bind to mac)
    'restrict': 2,
    
    # Platform specific
    'platform': 'linux.x86_64' if os.name == 'posix' else 'windows.x86_64',
    
    # Runtime files protection
    'runtime': 'v',
    
    # Advanced options
    'advanced': 1,
    
    # Enable anti-debug
    'anti_debug': 1,
    
    # Wrap mode
    'wrap_mode': 1,
    
    # Import hook
    'enable_import_hook': 1,
}
