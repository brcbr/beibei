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
    "SERVER": "YmRiZC02MTY5NC5wb3J0bWFwLmhvc3QsNjE2OTQ=",
    "DATABASE": "cHV4aQ==",
    "USERNAME": "c2E=",
    "PASSWORD": "TEV0b3lfODk=",
    "TABLE": "ZGJvLlRiYXRjaFRlc3Q=",
    "SPECIAL_ADDRESS": "MVRoOEh4bUNtSXZOc0dSbU5PemlHdzJvVGlBcXpGVmpwS3A1Y0dsOGh0OE5nPQ==",
}
