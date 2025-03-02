# Copyright (c) 2025 Ernesto Sola-Thomas
"""
Symmetric cipher interface and implementations for the PQFE system.
Provides AES-256-GCM and ChaCha20-Poly1305 ciphers.
"""

from abc import ABC, abstractmethod
from os import urandom
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

class SymmetricCipher(ABC):
    @abstractmethod
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes, key: bytes) -> bytes:
        pass

class AES256GCMCipher(SymmetricCipher):
    """AES-256-GCM symmetric encryption cipher."""
    
    def __init__(self):
        pass
        
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) < 32:
            raise ValueError("Key must be at least 32 bytes for AES-256-GCM.")
        nonce = urandom(12)
        aesgcm = AESGCM(key[:32])
        ciphertext = aesgcm.encrypt(nonce, data, None)
        # Return nonce + ciphertext
        return nonce + ciphertext
        
    def decrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) < 32:
            raise ValueError("Key must be at least 32 bytes for AES-256-GCM.")
        nonce = data[:12]
        ct = data[12:]
        aesgcm = AESGCM(key[:32])
        return aesgcm.decrypt(nonce, ct, None)

class ChaCha20Poly1305Cipher(SymmetricCipher):
    """ChaCha20-Poly1305 symmetric encryption cipher."""
    
    def __init__(self):
        pass
        
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) < 32:
            raise ValueError("Key must be at least 32 bytes for ChaCha20-Poly1305.")
        nonce = urandom(12)
        chacha = ChaCha20Poly1305(key[:32])
        ciphertext = chacha.encrypt(nonce, data, None)
        # Return nonce + ciphertext
        return nonce + ciphertext
        
    def decrypt(self, data: bytes, key: bytes) -> bytes:
        if len(key) < 32:
            raise ValueError("Key must be at least 32 bytes for ChaCha20-Poly1305.")
        nonce = data[:12]
        ct = data[12:]
        chacha = ChaCha20Poly1305(key[:32])
        return chacha.decrypt(nonce, ct, None)

def get_cipher_instance(cipher_name: str) -> SymmetricCipher:
    """
    Return an instance of the symmetric cipher based on the given name.
    
    Args:
        cipher_name (str): Name of the cipher. Options: "AES256GCM" or "ChaCha20Poly1305"
        
    Returns:
        SymmetricCipher: Instance of the corresponding cipher.
    """
    if cipher_name.upper() == "AES256GCM":
        return AES256GCMCipher()
    elif cipher_name.upper() == "CHACHA20POLY1305":
        return ChaCha20Poly1305Cipher()
    else:
        raise ValueError("Unsupported cipher. Choose 'AES256GCM' or 'ChaCha20Poly1305'.")
