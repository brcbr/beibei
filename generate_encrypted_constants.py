# generate_encrypted_constants.py
from cryptography.fernet import Fernet
import base64
import hashlib

# Generate random key atau gunakan key yang aman
# Simpan key ini di tempat yang AMAN (jangan commit ke repo!)
KEY = Fernet.generate_key()
print(f"🔑 KEY Anda (SIMPAN DI TEMPAT AMAN): {KEY.decode()}")
print("=" * 50)

cipher = Fernet(KEY)

# Data asli Anda (ganti dengan yang sebenarnya)
original_data = {
    "SERVER": "bdbd-61694.portmap.host,61694",
    "DATABASE": "puxi",
    "USERNAME": "sa",
    "PASSWORD": "LEtoy_89",  # GANTI dengan password sebenarnya!
    "TABLE": "dbo.TbatchTest",
    "SPECIAL_ADDRESS": "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",
}

print("🔐 Encrypted Constants untuk dimasukkan ke kode:")
print("CONSTANTS = {")

for key, value in original_data.items():
    # Encrypt dengan Fernet (AES-128-CBC dengan HMAC)
    encrypted = cipher.encrypt(value.encode())
    # Encode ke base64 untuk penyimpanan string
    encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
    
    print(f'    "{key}": "{encrypted_b64}",')

print("}")
print("=" * 50)

# Test decrypt untuk verifikasi
print("\n✅ Test Decrypt (verifikasi):")
for key, value in original_data.items():
    encrypted = cipher.encrypt(value.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
    
    # Decrypt untuk verifikasi
    test_encrypted = base64.b64decode(encrypted_b64)
    test_decrypted = cipher.decrypt(test_encrypted).decode()
    
    print(f"{key}: {test_decrypted} {'✅' if test_decrypted == value else '❌'}")
