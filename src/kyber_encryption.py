# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Main class for Kyber-based encryption operations.
Implements core encryption and decryption functionality using liboqs.
"""

from typing import Tuple, Dict, Any, Optional
import oqs
from .file_ops import read_file, write_encrypted_file, read_encrypted_file
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

class KyberEncryption:
    """Main class for Kyber-based encryption operations"""
    
    SUPPORTED_VARIANTS = {
        "Kyber512": "Kyber512",
        "Kyber768": "Kyber768",
        "Kyber1024": "Kyber1024"
    }
    
    def __init__(self, variant: str = "Kyber512"):
        """
        Initialize KyberEncryption with specified variant.
        
        Args:
            variant (str): Kyber variant to use (Kyber512, Kyber768, or Kyber1024)
        """
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant. Choose from: {', '.join(self.SUPPORTED_VARIANTS.keys())}")
        self.variant = variant
        self.kem = None  # Will be initialized when needed

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new public/private key pair.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        with oqs.KeyEncapsulation(self.variant) as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()
        return public_key, private_key
    def encrypt_file(self, input_file: str, public_key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Encrypt a file using Kyber.
        
        Args:
            input_file (str): Path to the file to encrypt
            public_key (bytes, optional): Public key for encryption
            
        Returns:
            Dict containing encrypted_file_path, ciphertext, and shared_secret
        """
        if public_key is None:
            raise ValueError("Public key is required for encryption.")

        # Read the file content
        file_content = read_file(input_file)

        # Generate shared secret using Kyber
        with oqs.KeyEncapsulation(self.variant) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)

        # Use the shared secret to encrypt the file content
        
        # Derive a Fernet key from the shared secret
        fernet_key = urlsafe_b64encode(shared_secret[:32])
        f = Fernet(fernet_key)
        
        # Encrypt the actual file content
        encrypted_content = f.encrypt(file_content)

        # Write the encrypted content to a file
        encrypted_file_path = write_encrypted_file(
            input_file, 
            encrypted_content,
            ciphertext, 
            {'shared_secret': shared_secret.hex()}
        )

        return {
            'encrypted_file_path': encrypted_file_path,
            'ciphertext': ciphertext,
            'shared_secret': shared_secret
        }

    def decrypt_file(self, encrypted_file: str, private_key: bytes) -> bytes:
        """
        Decrypt a file using Kyber.
        
        Args:
            encrypted_file (str): Path to the encrypted file
            private_key (bytes): Private key for decryption
            
        Returns:
            bytes: Decrypted content
        """
        # Read the encrypted file content
        encrypted_content, ciphertext, metadata = read_encrypted_file(encrypted_file)

        # Decrypt the content
        with oqs.KeyEncapsulation(self.variant, private_key) as kem:
            shared_secret = kem.decap_secret(ciphertext)

        # Verify the shared secret
        if shared_secret.hex() != metadata['shared_secret']:
            raise ValueError("Shared secret does not match. Decryption failed.")

        return encrypted_content 