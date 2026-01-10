# crypto_strings.py
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class StringEncryptor:
    def __init__(self, master_key=None):
        if master_key is None:
            # Generate key from system fingerprint
            import platform
            import socket
            system_info = f"{platform.node()}{platform.processor()}{platform.system()}"
            salt = hashlib.sha256(system_info.encode()).digest()[:16]
            
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b"xiebo_master_key"))
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(master_key)
    
    def encrypt_string(self, text):
        encrypted = self.cipher.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_string(self, encrypted_text):
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        return self.cipher.decrypt(encrypted_bytes).decode()

# Pre-encrypted constants untuk dimasukkan ke kode utama
CONSTANTS = {
    "SERVER": "Z0FBQUFBQnBZdEJpQXB6UUZDWjhUSHFPb2lIeE11Q2g1bFNtS3JRNmF5WFQtUnRsLTVmU0RxSmt4LUk4LUU3dm40MlNtdy1KeEp2dU1QdmhLX2JCRUd4amg3aUo1WHd0WllCdGtqRy1PTWdlVmRadDVlQ0FNZFk9",
    "DATABASE": "Z0FBQUFBQnBZdEJpbWNna3h4SzZXUlpNSGNxZ0lVa3g3alZycngtazdZaDFlc3dzckpMbXFCVTlXb19CUXVqMmxCd01HRWt4MF9HRlhlRHRhOTgxUDdtU1ppaVVJV2x0cVE9PQ==",
    "USERNAME": "Z0FBQUFBQnBZdEJpVG9tc2RiUi1kY3hhbG80NjJMYVVtYjZBeG9Rc2RWTU8yU2hMbjVlNmtiR1JXeDVoSkREajFacFd0cjI5dUVUTmtpTmt3YUNZUlcwNjgzUEJWOThMaGc9PQ==",
    "PASSWORD": "Z0FBQUFBQnBZdEJpVUNGMmxRVnJRWGdwME10cGYtdFRqTEVqdDJmOUY0YlczQmhoT2ZBbG85azdIaV9zbEEwWGw0TkRaTHJrQTJXZTZjMEV0dGtGcWJxNUlVWmJIS21nU0E9PQ==",
    "TABLE": "Z0FBQUFBQnBZdEJpdWRYajVybnZCZXdOQWJHTlVkWlR6R2t6TzRaV1JXV1FJZF9MaHBUaHEzS2VNOEpIS2VaSl9TcGUxMTJEYXdxZjFqSmtwSW5wV1R2ampCOWROMkJ4T0E9PQ==",
    "SPECIAL_ADDRESS": "Z0FBQUFBQnBZdEJpVU5pRTVMSENQb2lwc2FnWjBlbkNldjdKeEhaQ01EcWdYZy1yc1pDU0ZOa3RTT1FBODVrZHNMNHBNbkNqS3F2Q1M2QWhBYTdlbWprN0NHX0pzU3BEcE5kdzNIY1lMOUcwMm5JSC1xVTh1VTNPeDVvTVprek9PcWNORFgtQ2ZuWE4=",
}
