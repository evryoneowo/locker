import os
import base64
from hashlib import sha256
import hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# handlers.py must not call this directly. The encryption key should always be derived in real time by this module and never stored.
def get_key(master_password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if not salt: salt = os.urandom(16)

    password_bytes = master_password.encode()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    key = kdf.derive(password_bytes)
    return key, salt

# Encryption of services' passwords. This func can be called from handlers.py because it doesn't give secret data.
def encrypt_password(master_password: str, password: str) -> tuple[bytes, bytes, bytes]:
    key, salt = get_key(master_password)
    
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    encrypted = aesgcm.encrypt(nonce, password.encode(), None)

    return encrypted, salt, nonce

# Decryption of services' passwords.
def decrypt_password(master_password: str, salt: bytes, encrypted_password: bytes, nonce: bytes) -> str:
    key, _ = get_key(master_password, salt)

    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, encrypted_password, None)

    return decrypted.decode()

# Master password must be saved only in hashed form.
def hash_password(password: str, salt: bytes | None = None) -> tuple[str, bytes]:
    if not salt: salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = kdf.derive(password.encode())

    return base64.urlsafe_b64encode(key).decode(), salt

# Check master password.
def check_password(password: str, salt: bytes, hashed: str) -> bool:
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)

# Just converts bytes into string.
def bytestostr(item: bytes) -> str:
    return base64.b64encode(item).decode()