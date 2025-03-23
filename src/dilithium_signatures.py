# Copyright (c) 2025 Ernesto Sola-Thomas
"""
Digital signature module using CRYSTALS-Dilithium for the PQFE system.
Implements post-quantum secure digital signature functions.
"""

from typing import Dict, Any, Tuple, Optional
import oqs
import hashlib

class DilithiumSignature:
    """Main class for Dilithium-based digital signature operations"""

    SUPPORTED_VARIANTS = {
        "Dilithium2": "Dilithium2",
        "Dilithium3": "Dilithium3",
        "Dilithium5": "Dilithium5"
    }
    
    def __init__(self, variant: str = "Dilithium3"):
        """
        Initialize DilithiumSignature with specified variant.
        
        Args:
            variant (str): Dilithium variant to use (Dilithium2, Dilithium3, or Dilithium5)
        """
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant. Choose from: {', '.join(self.SUPPORTED_VARIANTS.keys())}")
        self.variant = variant

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new public/private key pair for digital signatures.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        with oqs.Signature(self.variant) as sig:
            public_key = sig.generate_keypair()
            private_key = sig.export_secret_key()
        return public_key, private_key

    def sign_data(self, data: bytes, private_key: bytes) -> bytes:
        """
        Sign data using the private key.
        
        Args:
            data (bytes): Data to sign
            private_key (bytes): Private key for signing
            
        Returns:
            bytes: Digital signature
        """
        # First hash the data to have a fixed-length input
        data_hash = hashlib.sha3_384(data).digest()
        
        with oqs.Signature(self.variant, private_key) as sig:
            signature = sig.sign(data_hash)
        return signature

    def verify_signature(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a signature using the public key.
        
        Args:
            data (bytes): Data that was signed
            signature (bytes): Signature to verify
            public_key (bytes): Public key to use for verification
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # First hash the data to match what was signed
        data_hash = hashlib.sha3_384(data).digest()
        
        try:
            with oqs.Signature(self.variant) as sig:
                result = sig.verify(data_hash, signature, public_key)
            return result
        except Exception:
            # Any exception during verification means the signature is invalid
            return False

    def sign_file(self, file_path: str, private_key: bytes) -> bytes:
        """
        Generate a signature for a file.
        
        Args:
            file_path (str): Path to the file to sign
            private_key (bytes): Private key for signing
            
        Returns:
            bytes: Digital signature
        """
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Sign the file content
        return self.sign_data(file_content, private_key)

    def verify_file(self, file_path: str, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a file's signature.
        
        Args:
            file_path (str): Path to the file to verify
            signature (bytes): Signature to verify
            public_key (bytes): Public key to use for verification
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Verify the signature
        return self.verify_signature(file_content, signature, public_key)