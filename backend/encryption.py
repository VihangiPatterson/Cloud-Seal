"""
AES-256 Encryption with Convergent Encryption
"""
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def generate_content_hash(file_content: bytes) -> str:
    """
    Generates SHA-256 hash of file content (for CID generation)
    """
    return hashlib.sha256(file_content).hexdigest()


def generate_convergent_key(file_content: bytes, tenant_id: str = "", tenant_secret: str = "") -> bytes:
    """
    Generates deterministic encryption key from file content
    Adds tenant-specific salt for privacy
    """
    # Add tenant-specific prefix for privacy
    combined = f"{tenant_id}:{tenant_secret}".encode() + file_content
    hash_digest = hashlib.sha256(combined).digest()
    return hash_digest[:32]  # AES-256 requires 32 bytes


def encrypt_file(file_content: bytes, key: bytes) -> bytes:
    """
    Encrypts file using AES-256 in CBC mode
    """
    # Generate random IV
    iv = os.urandom(16)
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad content to 16-byte blocks (PKCS7 padding)
    padding_length = 16 - (len(file_content) % 16)
    padded_content = file_content + bytes([padding_length] * padding_length)
    
    # Encrypt
    ciphertext = encryptor.update(padded_content) + encryptor.finalize()
    
    # Return IV + ciphertext (IV needed for decryption)
    return iv + ciphertext


def decrypt_file(encrypted_content: bytes, key: bytes) -> bytes:
    """
    Decrypts file using AES-256
    """
    # Extract IV from first 16 bytes
    iv = encrypted_content[:16]
    ciphertext = encrypted_content[16:]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    padding_length = padded_plaintext[-1]
    plaintext = padded_plaintext[:-padding_length]
    
    return plaintext


# Test function
if __name__ == "__main__":
    # Test encryption/decryption
    original = b"Hello, Cloud Seal!"
    key = generate_convergent_key(original, "tenant_A", "secret123")
    
    encrypted = encrypt_file(original, key)
    decrypted = decrypt_file(encrypted, key)
    
    print(f"Original: {original}")
    print(f"Key: {key.hex()[:32]}...")
    print(f"Encrypted length: {len(encrypted)} bytes")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")