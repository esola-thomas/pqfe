# api.py
"""
API interface for the Post-Quantum File Encryption system.
Provides high-level functions for encryption, decryption, and key management.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .kyber_encryption import KyberEncryption
from . import key_management

class PQFE:
    """Main API interface for Post-Quantum File Encryption"""
    
    def __init__(
        self, 
        variant: str = "Kyber512", 
        key_directory: Optional[str] = None,
        cipher: str = "AES256GCM"
    ):
        """
        Initialize PQFE with specified Kyber variant, cipher, and key directory.
        
        Args:
            variant (str): Kyber variant to use
            key_directory (Optional[str]): Directory for key storage
            cipher (str): Symmetric cipher to use ("AES256GCM" or "ChaCha20Poly1305")
        """
        self.encryptor = KyberEncryption(variant=variant, cipher=cipher)
        self.key_directory = key_directory or str(Path.home() / ".pqfe" / "keys")
        
    def encrypt_file(
        self, 
        file_path: str, 
        public_key: Optional[bytes] = None,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        return_as_data: bool = False
    ) -> Dict[str, Any]:
        """
        Encrypt a file using Kyber.
        
        Args:
            file_path (str): Path to file to encrypt
            public_key (Optional[bytes]): Public key for encryption
            output_dir (Optional[str]): Directory to write the encrypted file
            output_filename (Optional[str]): Custom filename for the encrypted file
            return_as_data (bool): If True, return encrypted data in-memory instead of writing to disk
            
        Returns:
            Dict containing:
            - encrypted_file_path (str) or encrypted_data (bytes)
            - ciphertext (bytes)
            - shared_secret (bytes)
        """
        return self.encryptor.encrypt_file(
            file_path, 
            public_key, 
            output_dir, 
            output_filename, 
            return_as_data
        )
        
    def decrypt_file(
        self,
        encrypted_file: str,
        ciphertext: bytes,
        private_key: Optional[bytes] = None,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        return_as_data: bool = False
    ) -> Dict[str, Any]:
        """
        Decrypt a file using Kyber.
        
        Args:
            encrypted_file (str): Path to encrypted file
            ciphertext (bytes): The Kyber ciphertext from encryption
            private_key (Optional[bytes]): Private key for decryption
            output_dir (Optional[str]): Directory to write the decrypted file
            output_filename (Optional[str]): Custom filename for the decrypted file
            return_as_data (bool): If True, return decrypted data in-memory instead of writing to disk
            
        Returns:
            Dict containing:
            - decrypted_file_path (str) or decrypted_data (bytes)
        """
        if private_key is None:
            raise ValueError("Private key is required for decryption.")
        return self.encryptor.decrypt_file(
            encrypted_file, 
            private_key, 
            ciphertext, 
            output_dir, 
            output_filename, 
            return_as_data
        )
        
    def generate_keys(self) -> Tuple[bytes, bytes]:
        """
        Generate new keypair and save to the configured directory using key management module.
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        public_key, private_key = self.encryptor.generate_keypair()
        # Use key_management module to save keys
        key_management.save_keys(public_key, private_key, self.key_directory)
        return public_key, private_key
        
    def load_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load keys from configured directory.
        
        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: (public_key, private_key)
        """
        return key_management.load_keys(self.key_directory)
