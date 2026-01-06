"""
Cryptography Service for Secure Data Storage
Provides hashing, encryption, and key derivation utilities
"""

import hashlib
import hmac
import secrets
import base64
import json
from typing import Any, Optional, Tuple


# Salt for additional security (should be in env var in production)
_SALT = b"stonks_by_kg_2026"


def hash_sha256(data: str) -> str:
    """Generate SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def hash_with_salt(data: str, salt: str = None) -> Tuple[str, str]:
    """
    Hash data with a random salt
    Returns: (hash, salt) tuple
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{salt}:{data}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return hashed, salt


def verify_hash(data: str, expected_hash: str, salt: str) -> bool:
    """Verify data against stored hash and salt"""
    computed_hash, _ = hash_with_salt(data, salt)
    return hmac.compare_digest(computed_hash, expected_hash)


def derive_key(session_token: str, purpose: str = "encryption") -> bytes:
    """
    Derive an encryption key from session token using PBKDF2
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        session_token.encode(),
        _SALT + purpose.encode(),
        iterations=100000,
        dklen=32
    )


def simple_encrypt(data: str, key: bytes) -> str:
    """
    Simple XOR-based encryption for non-critical data
    For production, use Fernet from cryptography library
    """
    data_bytes = data.encode()
    key_extended = (key * ((len(data_bytes) // len(key)) + 1))[:len(data_bytes)]
    encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_extended))
    return base64.b64encode(encrypted).decode()


def simple_decrypt(encrypted_data: str, key: bytes) -> str:
    """Decrypt XOR-encrypted data"""
    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    key_extended = (key * ((len(encrypted_bytes) // len(key)) + 1))[:len(encrypted_bytes)]
    decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key_extended))
    return decrypted.decode()


def encrypt_dict(data: dict, session_token: str) -> str:
    """Encrypt a dictionary using session-derived key"""
    key = derive_key(session_token)
    json_str = json.dumps(data, default=str)
    return simple_encrypt(json_str, key)


def decrypt_dict(encrypted_data: str, session_token: str) -> Optional[dict]:
    """Decrypt an encrypted dictionary"""
    try:
        key = derive_key(session_token)
        json_str = simple_decrypt(encrypted_data, key)
        return json.loads(json_str)
    except Exception:
        return None


def generate_secure_id() -> str:
    """Generate a cryptographically secure random ID"""
    return secrets.token_urlsafe(32)


def hash_portfolio_data(holdings: list) -> str:
    """
    Create a checksum hash of portfolio holdings
    Used to detect if data has been tampered with
    """
    # Sort for consistent hashing
    sorted_data = sorted(holdings, key=lambda x: x.get('symbol', ''))
    data_str = json.dumps(sorted_data, sort_keys=True, default=str)
    return hash_sha256(data_str)


def mask_sensitive_value(value: Any, show_chars: int = 4) -> str:
    """Mask sensitive values for display (e.g., 1234.56 -> ****56)"""
    str_val = str(value)
    if len(str_val) <= show_chars:
        return "*" * len(str_val)
    return "*" * (len(str_val) - show_chars) + str_val[-show_chars:]
